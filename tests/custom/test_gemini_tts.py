import json

import httpx
import pytest

from agora_agent import Agent, Agora, Area, AsyncAgora, Gemini, GeminiSTT, GeminiTTS, GeminiTTSModels
from agora_agent.agentkit.preview import PREVIEW_API_BASE_URL, required_preview_features

MODELS = [GeminiTTSModels.FLASH_38]


def make_agent(client, model):
    return (
        Agent(client=client)
        .with_stt(GeminiSTT(api_key="test-key"))
        .with_llm(Gemini(api_key="test-key", model="gemini-3.6-flash"))
        .with_tts(GeminiTTS(api_key="test-key", model=model, voice="Puck", style="warm and reassuring"))
    )


def transport(requests):
    def handle(request):
        requests.append(request)
        return httpx.Response(200, json={"agent_id": "agent-1", "data": {"list": []}})

    return httpx.MockTransport(handle)


def assert_requests(requests, model):
    assert len(requests) == 4
    assert json.loads(requests[0].content)["properties"]["tts"] == {
        "vendor": "gemini",
        "params": {"api_key": "test-key", "model": model, "voice": "Puck", "style": "warm and reassuring"},
    }
    for request in requests:
        assert str(request.url).startswith(PREVIEW_API_BASE_URL)
        assert request.headers["agora-feature"] == "gemini-live"
        assert request.headers["x-custom"] == "kept"


@pytest.mark.parametrize("model", MODELS)
def test_sync_lifecycle(model):
    requests = []
    with httpx.Client(transport=transport(requests)) as http_client:
        client = Agora(
            area=Area.US,
            app_id="0" * 32,
            app_certificate="1" * 32,
            httpx_client=http_client,
            headers={"agora-feature": "", "x-custom": "kept"},
        )
        production_url = client.get_current_url()
        session = make_agent(client, model).create_session(channel="test", agent_uid="1", remote_uids=["100"])
        session.start()
        session.say("hello")
        session.interrupt()
        session.stop()
        assert_requests(requests, model)
        assert client.get_current_url() == production_url
        assert client._client_wrapper.get_custom_headers()["agora-feature"] == ""


@pytest.mark.asyncio
@pytest.mark.parametrize("model", MODELS)
async def test_async_lifecycle(model):
    requests = []
    async with httpx.AsyncClient(transport=transport(requests)) as http_client:
        client = AsyncAgora(
            area=Area.US,
            app_id="0" * 32,
            app_certificate="1" * 32,
            httpx_client=http_client,
            headers={"agora-feature": "", "x-custom": "kept"},
        )
        session = make_agent(client, model).create_async_session(channel="test", agent_uid="1", remote_uids=["100"])
        await session.start()
        await session.say("hello")
        await session.interrupt()
        await session.stop()
        assert_requests(requests, model)


def test_defaults_and_raw_detection():
    assert GeminiTTS(api_key="test-key").to_config() == {
        "vendor": "gemini",
        "params": {"api_key": "test-key", "model": "gemini-3.8-flash-tts", "voice": "Puck"},
    }
    assert required_preview_features({"tts": {"vendor": "gemini", "params": {"model": "future-model"}}}) == [
        "gemini-live"
    ]
    assert set(required_preview_features({"tts": {"vendor": "gemini"}, "mllm": {"vendor": "openai_gpt_live"}})) == {
        "gemini-live",
    }
    assert required_preview_features({"asr": {"vendor": "gemini"}, "tts": {"vendor": "google"}}) == []


@pytest.mark.parametrize("field", ["api_key", "model", "voice"])
def test_rejects_blank_fields(field):
    with pytest.raises(ValueError):
        GeminiTTS(**{**{"api_key": "test-key"}, field: "  "})


@pytest.mark.parametrize("header", ["agora-feature", "Agora-Feature", "AGORA-FEATURE"])
def test_preview_gate_survives_raw_per_call_headers(header):
    requests = []
    with httpx.Client(transport=transport(requests)) as http_client:
        client = Agora(
            area=Area.US,
            app_id="0" * 32,
            app_certificate="1" * 32,
            httpx_client=http_client,
            headers={header: "caller-value"},
        )
        session = make_agent(client, MODELS[0]).create_session(channel="test", agent_uid="1", remote_uids=["100"])
        session.start()
        headers = {header: "", "x-custom": "preserved"}
        session.raw.get("0" * 32, "agent-1", request_options={"additional_headers": headers})
        for req in requests:
            assert req.headers.get_list("agora-feature") == ["gemini-live"]
        assert requests[-1].headers["x-custom"] == "preserved"
        assert headers[header] == ""
        assert client._client_wrapper.get_custom_headers()[header] == "caller-value"
        client.agents.get("0" * 32, "agent-1")
        assert not str(requests[-1].url).startswith(PREVIEW_API_BASE_URL)
        assert requests[-1].headers["agora-feature"] == "caller-value"


@pytest.mark.asyncio
async def test_async_preview_gate_survives_raw_per_call_headers():
    requests = []
    async with httpx.AsyncClient(transport=transport(requests)) as http_client:
        client = AsyncAgora(
            area=Area.US,
            app_id="0" * 32,
            app_certificate="1" * 32,
            httpx_client=http_client,
            headers={"Agora-Feature": "caller-value"},
        )
        session = make_agent(client, MODELS[0]).create_async_session(channel="test", agent_uid="1", remote_uids=["100"])
        await session.start()
        await session.raw.get("0" * 32, "agent-1", request_options={"additional_headers": {"AGORA-FEATURE": ""}})
        for req in requests:
            assert req.headers.get_list("agora-feature") == ["gemini-live"]
        await client.agents.get("0" * 32, "agent-1")
        assert not str(requests[-1].url).startswith(PREVIEW_API_BASE_URL)
        assert requests[-1].headers["agora-feature"] == "caller-value"
