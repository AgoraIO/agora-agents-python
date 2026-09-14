"""Tests for provider-agnostic preview routing infrastructure."""

from typing import Dict, List

import httpx
import pytest
from pydantic import ConfigDict

from agora_agent import Agent, Agora, Area, AsyncAgora, Gemini, GoogleTTS
from agora_agent.agentkit.preview import (
    PREVIEW_API_BASE_URL,
    PREVIEW_FEATURE_HEADER,
    create_preview_session_clients,
    required_preview_features,
)
from agora_agent.agentkit.preview import client as preview_client
from agora_agent.agentkit.vendors import BaseSTT

API_KEY = "test-google-api-key"
APP_ID = "0" * 32
APP_CERTIFICATE = "1" * 32
TEST_FEATURE = "future-asr"
TEST_VENDOR = "future_preview"


class _PreviewSTT(BaseSTT):
    model_config = ConfigDict(extra="forbid")

    def to_config(self) -> Dict[str, object]:
        return {
            "vendor": TEST_VENDOR,
            "params": {"preview_option": True, "optional": None},
        }


class _Recorder(httpx.MockTransport):
    def __init__(self) -> None:
        self.requests: List[httpx.Request] = []
        super().__init__(self._handle)

    def _handle(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return httpx.Response(200, json={"agent_id": "agent-1"})


@pytest.fixture
def registered_preview_asr(monkeypatch):
    monkeypatch.setitem(preview_client._PREVIEW_FEATURES_BY_CATEGORY["asr"], TEST_VENDOR, TEST_FEATURE)


def _complete_preview_agent(client) -> Agent:
    return (
        Agent(client=client)
        .with_stt(_PreviewSTT())
        .with_llm(Gemini(api_key=API_KEY, model="gemini-2.0-flash"))
        .with_tts(
            GoogleTTS(
                key=API_KEY,
                voice_name="en-US-Chirp3-HD-Charon",
                language_code="en-US",
            )
        )
    )


def test_gemini_is_not_registered_for_preview_routing() -> None:
    assert required_preview_features({"asr": {"vendor": "gemini"}}) == []


def test_registered_provider_routes_session_to_preview(registered_preview_asr) -> None:
    recorder = _Recorder()
    client = Agora(
        area=Area.US,
        app_id=APP_ID,
        app_certificate=APP_CERTIFICATE,
        headers={PREVIEW_FEATURE_HEADER: "caller-value", "x-custom": "kept"},
        httpx_client=httpx.Client(transport=recorder),
    )
    production_url = client.get_current_url()

    _complete_preview_agent(client).create_session(
        channel="preview-channel",
        agent_uid="1",
        remote_uids=["100"],
    ).start()

    request = recorder.requests[0]
    assert str(request.url).startswith(PREVIEW_API_BASE_URL)
    assert request.headers[PREVIEW_FEATURE_HEADER] == TEST_FEATURE
    assert request.headers["x-custom"] == "kept"
    assert client.get_current_url() == production_url
    assert client._client_wrapper.get_base_url() == production_url
    custom_headers = client._client_wrapper.get_custom_headers()
    assert custom_headers is not None
    assert custom_headers[PREVIEW_FEATURE_HEADER] == "caller-value"
    assert b'"preview_option":true' in request.content
    assert b'"optional"' not in request.content


@pytest.mark.asyncio
async def test_registered_provider_routes_async_session_to_preview(registered_preview_asr) -> None:
    recorder = _Recorder()
    client = AsyncAgora(
        area=Area.US,
        app_id=APP_ID,
        app_certificate=APP_CERTIFICATE,
        httpx_client=httpx.AsyncClient(transport=recorder),
    )

    session = _complete_preview_agent(client).create_async_session(
        channel="preview-channel",
        agent_uid="1",
        remote_uids=["100"],
    )
    await session.start()

    request = recorder.requests[0]
    assert str(request.url).startswith(PREVIEW_API_BASE_URL)
    assert request.headers[PREVIEW_FEATURE_HEADER] == TEST_FEATURE


def test_preview_client_factory_supports_sync_and_async_clients() -> None:
    sync_client = Agora(
        area=Area.US,
        app_id=APP_ID,
        app_certificate=APP_CERTIFICATE,
        httpx_client=httpx.Client(transport=_Recorder()),
    )
    async_client = AsyncAgora(
        area=Area.US,
        app_id=APP_ID,
        app_certificate=APP_CERTIFICATE,
        httpx_client=httpx.AsyncClient(transport=_Recorder()),
    )

    sync_agents, sync_management = create_preview_session_clients(sync_client, [TEST_FEATURE])
    async_agents, async_management = create_preview_session_clients(async_client, [TEST_FEATURE])

    for generated_client in (sync_agents, sync_management, async_agents, async_management):
        wrapper = generated_client._raw_client._client_wrapper
        assert wrapper.get_base_url() == PREVIEW_API_BASE_URL
        assert wrapper.get_custom_headers()[PREVIEW_FEATURE_HEADER] == TEST_FEATURE
