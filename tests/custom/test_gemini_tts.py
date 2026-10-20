import json
from typing import get_args

import httpx
import pytest

from agora_agent import Agent, Agora, Area, AsyncAgora, Gemini, GeminiSTT, GeminiTTS, GeminiTTSModels
from agora_agent.agentkit.preview import PREVIEW_API_BASE_URL, required_preview_features
from agora_agent.agentkit.preview import GeminiTTS as PreviewGeminiTTS
from agora_agent.agentkit.preview.gemini_tts import GeminiTTS as LegacyGeminiTTS
from agora_agent.agentkit.regional_agent import GlobalTTS
from agora_agent.agentkit.vendors import GeminiTTS as VendorGeminiTTS
from agora_agent.agentkit.vendors.base import BaseSTT, BaseTTS
from agora_agent.agentkit.vendors.catalog import GLOBAL_VENDOR_NAMESPACE
from agora_agent.agentkit.vendors.namespaces import GlobalTTSVendors
from agora_agent.agentkit.vendors.region import CN_TTS_VENDORS, GLOBAL_TTS_VENDORS
from agora_agent.agentkit.vendors.tts import GeminiTTS as ProductionGeminiTTS
from agora_agent.types.tts import Tts_Gemini

MODELS = [GeminiTTSModels.FLASH_38, "future-tts-model"]


def make_agent(client, model, tts_type=GeminiTTS):
    return (
        Agent(client=client)
        .with_stt(GeminiSTT(api_key="test-key"))
        .with_llm(Gemini(api_key="test-key", model="gemini-3.6-flash"))
        .with_tts(tts_type(api_key="test-key", model=model, voice="Puck", style="warm and reassuring"))
    )


def transport(requests):
    def handle(request):
        requests.append(request)
        return httpx.Response(200, json={"agent_id": "agent-1", "data": {"list": []}})

    return httpx.MockTransport(handle)


def assert_requests(requests, model, production_url):
    assert len(requests) == 9
    assert json.loads(requests[0].content)["properties"]["tts"] == {
        "vendor": "gemini",
        "params": {"api_key": "test-key", "model": model, "voice": "Puck", "style": "warm and reassuring"},
    }
    for request in requests:
        assert str(request.url).startswith(production_url + "/")
        assert "agora-feature" not in request.headers
        assert request.headers["x-custom"] == "kept"


@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("area", [Area.US, Area.EU, Area.AP])
@pytest.mark.parametrize(
    "tts_type", [GeminiTTS, PreviewGeminiTTS, LegacyGeminiTTS], ids=["root", "preview", "legacy-module"]
)
def test_sync_lifecycle(model, area, tts_type):
    requests = []
    with httpx.Client(transport=transport(requests)) as http_client:
        client = Agora(
            area=area,
            app_id="0" * 32,
            app_certificate="1" * 32,
            httpx_client=http_client,
            headers={"x-custom": "kept"},
        )
        production_url = client.get_current_url()
        session = make_agent(client, model, tts_type).create_session(channel="test", agent_uid="1", remote_uids=["100"])
        session.start()
        session.say("hello")
        session.interrupt()
        session.think("think")
        session.update({})
        session.get_history()
        session.get_info()
        session.get_turns()
        session.stop()
        assert_requests(requests, model, production_url)
        assert client.get_current_url() == production_url
        client.agents.get("0" * 32, "agent-1")
        assert str(requests[-1].url).startswith(production_url + "/")
        assert "agora-feature" not in requests[-1].headers


@pytest.mark.asyncio
@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("area", [Area.US, Area.EU, Area.AP])
@pytest.mark.parametrize(
    "tts_type", [GeminiTTS, PreviewGeminiTTS, LegacyGeminiTTS], ids=["root", "preview", "legacy-module"]
)
async def test_async_lifecycle(model, area, tts_type):
    requests = []
    async with httpx.AsyncClient(transport=transport(requests)) as http_client:
        client = AsyncAgora(
            area=area,
            app_id="0" * 32,
            app_certificate="1" * 32,
            httpx_client=http_client,
            headers={"x-custom": "kept"},
        )
        production_url = client.get_current_url()
        session = make_agent(client, model, tts_type).create_async_session(
            channel="test", agent_uid="1", remote_uids=["100"]
        )
        await session.start()
        await session.say("hello")
        await session.interrupt()
        await session.think("think")
        await session.update({})
        await session.get_history()
        await session.get_info()
        await session.get_turns()
        await session.stop()
        assert_requests(requests, model, production_url)
        assert client.get_current_url() == production_url
        await client.agents.get("0" * 32, "agent-1")
        assert str(requests[-1].url).startswith(production_url + "/")
        assert "agora-feature" not in requests[-1].headers


def test_defaults_and_raw_detection():
    assert GeminiTTS(api_key="test-key").to_config() == {
        "vendor": "gemini",
        "params": {"api_key": "test-key", "model": "gemini-3.8-flash-tts", "voice": "Puck"},
    }
    assert required_preview_features({"tts": {"vendor": "gemini", "params": {"model": "future-model"}}}) == []
    assert required_preview_features({"tts": {"vendor": "gemini"}, "mllm": {"vendor": "openai_gpt_live"}}) == []
    assert required_preview_features({"asr": {"vendor": "gemini"}, "tts": {"vendor": "google"}}) == []


def test_additional_params_are_merged_before_named_options():
    additional_params = {"temperature": 0.7, "style": "overridden", "voice": "overridden"}
    config = GeminiTTS(
        api_key="test-key", style="warm", additional_params=additional_params, skip_patterns=[1]
    ).to_config()
    assert config["params"] == {
        "temperature": 0.7,
        "api_key": "test-key",
        "model": "gemini-3.8-flash-tts",
        "voice": "Puck",
        "style": "warm",
    }
    assert config["skip_patterns"] == [1]
    assert additional_params == {"temperature": 0.7, "style": "overridden", "voice": "overridden"}
    generated = Tts_Gemini.model_validate(config)
    assert generated.params.style == "warm"
    assert generated.params.temperature == 0.7


@pytest.mark.parametrize("field", ["api_key", "model", "voice"])
def test_rejects_blank_fields(field):
    with pytest.raises(ValueError):
        GeminiTTS(**{**{"api_key": "test-key"}, field: "  "})


def test_production_raw_calls_preserve_per_call_headers():
    requests = []
    with httpx.Client(transport=transport(requests)) as http_client:
        client = Agora(
            area=Area.US,
            app_id="0" * 32,
            app_certificate="1" * 32,
            httpx_client=http_client,
            headers={"x-custom": "caller-value"},
        )
        session = make_agent(client, MODELS[0]).create_session(channel="test", agent_uid="1", remote_uids=["100"])
        session.start()
        headers = {"x-request": "preserved"}
        session.raw.get("0" * 32, "agent-1", request_options={"additional_headers": headers})
        for req in requests:
            assert "agora-feature" not in req.headers
            assert str(req.url).startswith(client.get_current_url() + "/")
        assert requests[-1].headers["x-request"] == "preserved"
        assert headers == {"x-request": "preserved"}
        client.agents.get("0" * 32, "agent-1")
        assert not str(requests[-1].url).startswith(PREVIEW_API_BASE_URL)
        assert requests[-1].headers["x-custom"] == "caller-value"


@pytest.mark.asyncio
async def test_async_production_raw_calls_preserve_per_call_headers():
    requests = []
    async with httpx.AsyncClient(transport=transport(requests)) as http_client:
        client = AsyncAgora(
            area=Area.US,
            app_id="0" * 32,
            app_certificate="1" * 32,
            httpx_client=http_client,
            headers={"x-custom": "caller-value"},
        )
        session = make_agent(client, MODELS[0]).create_async_session(channel="test", agent_uid="1", remote_uids=["100"])
        await session.start()
        await session.raw.get("0" * 32, "agent-1", request_options={"additional_headers": {"x-request": "preserved"}})
        for req in requests:
            assert "agora-feature" not in req.headers
            assert str(req.url).startswith(client.get_current_url() + "/")
        assert requests[-1].headers["x-request"] == "preserved"
        await client.agents.get("0" * 32, "agent-1")
        assert not str(requests[-1].url).startswith(PREVIEW_API_BASE_URL)
        assert requests[-1].headers["x-custom"] == "caller-value"


def test_preview_imports_alias_production_and_register_in_global_catalog():
    from agora_agent.agentkit.preview import GeminiTTSModels as PreviewModels
    from agora_agent.agentkit.preview.gemini_tts import GeminiTTSModels as LegacyModels

    assert GeminiTTS is VendorGeminiTTS is ProductionGeminiTTS is PreviewGeminiTTS is LegacyGeminiTTS
    assert GeminiTTSModels is PreviewModels is LegacyModels
    assert GLOBAL_VENDOR_NAMESPACE.tts["gemini"] is GeminiTTS
    assert GlobalTTSVendors.gemini is GeminiTTS
    assert GeminiTTS in get_args(GlobalTTS)
    assert "gemini" in GLOBAL_TTS_VENDORS
    assert "gemini" not in CN_TTS_VENDORS


def test_raw_config_starts_on_production_and_drops_none():
    config = {
        "vendor": "gemini",
        "params": {"api_key": "test-key", "model": "future-tts-model", "voice": "Puck", "style": None},
    }

    class RawGeminiTTS(BaseTTS):
        def to_config(self):
            return config

    requests = []
    with httpx.Client(transport=transport(requests)) as http_client:
        client = Agora(area=Area.EU, app_id="0" * 32, app_certificate="1" * 32, httpx_client=http_client)
        session = make_agent(client, MODELS[0]).with_tts(RawGeminiTTS()).create_session(
            channel="raw", agent_uid="1", remote_uids=["100"]
        )
        session.start()
        session.stop()
        assert json.loads(requests[0].content)["properties"]["tts"] == {
            "vendor": "gemini",
            "params": {"api_key": "test-key", "model": "future-tts-model", "voice": "Puck"},
        }
        assert config["params"]["style"] is None
        for request in requests:
            assert str(request.url).startswith(client.get_current_url() + "/")
            assert "agora-feature" not in request.headers


def test_gemini_tts_schema_compatibility_still_validates_other_fields():
    class InvalidASR(BaseSTT):
        def to_config(self):
            return {"vendor": "gemini", "params": {"api_key": "test-key"}}

    requests = []
    with httpx.Client(transport=transport(requests)) as http_client:
        client = Agora(area=Area.US, app_id="0" * 32, app_certificate="1" * 32, httpx_client=http_client)
        session = make_agent(client, MODELS[0]).with_stt(InvalidASR()).create_session(
            channel="invalid", agent_uid="1", remote_uids=["100"]
        )
        with pytest.raises(ValueError):
            session.start()
        assert requests == []


def test_gemini_tts_can_share_a_session_with_a_registered_preview_provider(monkeypatch):
    from agora_agent.agentkit.preview import client as preview_client

    monkeypatch.setitem(preview_client._PREVIEW_FEATURES_BY_CATEGORY["asr"], "future_asr", "future-asr")

    class PreviewASR(BaseSTT):
        def to_config(self):
            return {"vendor": "future_asr", "params": {"model": "future-model"}}

    requests = []
    with httpx.Client(transport=transport(requests)) as http_client:
        client = Agora(area=Area.US, app_id="0" * 32, app_certificate="1" * 32, httpx_client=http_client)
        session = make_agent(client, MODELS[0]).with_stt(PreviewASR()).create_session(
            channel="mixed", agent_uid="1", remote_uids=["100"]
        )
        session.start()
        session.stop()
        assert json.loads(requests[0].content)["properties"]["tts"]["vendor"] == "gemini"
        for request in requests:
            assert str(request.url).startswith(PREVIEW_API_BASE_URL)
            assert request.headers["agora-feature"] == "future-asr"
