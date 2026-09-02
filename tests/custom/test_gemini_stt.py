import json
from typing import List

import httpx
import pytest
from pydantic import ValidationError

import agora_agent
from agora_agent import Agent, Agora, Area, Gemini, GeminiSTT, GoogleTTS
from agora_agent.agentkit.vendors.catalog import GLOBAL_VENDOR_NAMESPACE
from agora_agent.agentkit.vendors.namespaces import GlobalSTTVendors
from agora_agent.agentkit.vendors.region import GLOBAL_ASR_VENDORS

API_KEY = "test-google-api-key"
MODEL = "gemini-3.7-transcribe-live"
APP_ID = "0" * 32
APP_CERTIFICATE = "1" * 32


class _Recorder(httpx.MockTransport):
    def __init__(self) -> None:
        self.requests: List[httpx.Request] = []
        super().__init__(self._handle)

    def _handle(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return httpx.Response(200, json={"agent_id": "agent-1"})


def _gemini_stt(**kwargs) -> GeminiSTT:
    options = {
        "api_key": API_KEY,
        "model": MODEL,
        "language": "en-US",
        "word_timestamp": True,
    }
    options.update(kwargs)
    return GeminiSTT(**options)


def _complete_agent(client: Agora) -> Agent:
    return (
        Agent(client=client)
        .with_stt(_gemini_stt())
        .with_llm(Gemini(api_key=API_KEY, model="gemini-2.0-flash"))
        .with_tts(
            GoogleTTS(
                key=API_KEY,
                voice_name="en-US-Chirp3-HD-Charon",
                language_code="en-US",
            )
        )
    )


def test_gemini_stt_serializes_fern_schema() -> None:
    assert _gemini_stt().to_config() == {
        "vendor": "gemini",
        "params": {
            "api_key": API_KEY,
            "model": MODEL,
            "language": "en-US",
            "word_timestamp": True,
        },
    }


def test_gemini_stt_serializes_optional_sample_rate() -> None:
    config = _gemini_stt(
        sample_rate=24000,
        additional_params={"provider_option": "kept", "model": "overridden"},
    ).to_config()

    assert config["params"] == {
        "provider_option": "kept",
        "api_key": API_KEY,
        "model": MODEL,
        "language": "en-US",
        "word_timestamp": True,
        "sample_rate": 24000,
    }


@pytest.mark.parametrize("field", ["api_key", "model"])
def test_gemini_stt_requires_fern_fields(field: str) -> None:
    options = {
        "api_key": API_KEY,
        "model": MODEL,
        "language": "en-US",
        "word_timestamp": True,
    }
    del options[field]

    with pytest.raises(ValidationError):
        GeminiSTT(**options)


def test_gemini_stt_omits_optional_fields_when_unset() -> None:
    config = GeminiSTT(api_key=API_KEY, model=MODEL).to_config()

    assert config == {
        "vendor": "gemini",
        "params": {
            "api_key": API_KEY,
            "model": MODEL,
        },
    }


def test_gemini_stt_preserves_explicit_false_word_timestamp() -> None:
    config = GeminiSTT(
        api_key=API_KEY,
        model=MODEL,
        word_timestamp=False,
    ).to_config()

    assert config["params"]["word_timestamp"] is False


def test_gemini_stt_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        _gemini_stt(unknown_option=True)


def test_gemini_stt_is_available_from_standard_vendor_surfaces() -> None:
    assert agora_agent.GeminiSTT is GeminiSTT
    assert "GeminiSTT" in agora_agent.__all__
    assert "gemini" in GLOBAL_ASR_VENDORS
    assert GLOBAL_VENDOR_NAMESPACE.asr["gemini"] is GeminiSTT
    assert GlobalSTTVendors.gemini is GeminiSTT


def test_gemini_stt_uses_production_endpoint_and_fern_request_model() -> None:
    recorder = _Recorder()
    client = Agora(
        area=Area.US,
        app_id=APP_ID,
        app_certificate=APP_CERTIFICATE,
        httpx_client=httpx.Client(transport=recorder),
    )

    _complete_agent(client).create_session(
        channel="gemini-channel",
        agent_uid="1",
        remote_uids=["100"],
    ).start()

    request = recorder.requests[0]
    body = json.loads(request.content)
    assert str(request.url).startswith(client.get_current_url())
    assert body["properties"]["asr"] == {
        "vendor": "gemini",
        "language": "en-US",
        "params": {
            "api_key": API_KEY,
            "model": MODEL,
            "language": "en-US",
            "word_timestamp": True,
        },
    }
