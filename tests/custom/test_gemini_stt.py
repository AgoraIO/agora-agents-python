import json
from typing import List

import httpx
import pytest
from pydantic import ValidationError

import agora_agent
from agora_agent import Agent, Agora, Area, Gemini, GeminiSTT, GeminiSTTModels, GoogleTTS
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
        "language_hints": ["en-US", "es-ES"],
        "custom_vocabulary": ["Agora"],
        "word_timestamp": False,
    }
    options.update(kwargs)
    return GeminiSTT(**options)


def _complete_agent(client: Agora) -> Agent:
    return (
        Agent(client=client)
        .with_stt(_gemini_stt(mode="VERBATIM", diarization=True))
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
            "sample_rate": 16000,
            "language": "en-US",
            "language_hints": ["en-US", "es-ES"],
            "custom_vocabulary": ["Agora"],
            "word_timestamp": False,
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
        "sample_rate": 24000,
        "language": "en-US",
        "language_hints": ["en-US", "es-ES"],
        "custom_vocabulary": ["Agora"],
        "word_timestamp": False,
    }


@pytest.mark.parametrize("options", [{}, {"api_key": ""}])
def test_gemini_stt_requires_non_empty_api_key(options) -> None:
    with pytest.raises(ValidationError):
        GeminiSTT(**options)


def test_gemini_stt_preserves_preview_defaults() -> None:
    config = GeminiSTT(api_key=API_KEY, model=None, sample_rate=None).to_config()

    assert config == {
        "vendor": "gemini",
        "params": {
            "api_key": API_KEY,
            "model": GeminiSTTModels.TRANSCRIBE_35_LIVE,
            "sample_rate": 16000,
        },
    }


def test_gemini_stt_preserves_explicit_false_word_timestamp() -> None:
    config = GeminiSTT(
        api_key=API_KEY,
        model=MODEL,
        word_timestamp=False,
    ).to_config()

    assert config["params"]["word_timestamp"] is False


@pytest.mark.parametrize(
    ("field", "wire_key"),
    [
        ("language_hints", "language_hints"),
        ("custom_vocabulary", "custom_vocabulary"),
    ],
)
def test_gemini_stt_preserves_optional_list_semantics(field: str, wire_key: str) -> None:
    omitted = GeminiSTT(api_key=API_KEY).to_config()
    explicit_empty = GeminiSTT(api_key=API_KEY, **{field: []}).to_config()

    assert wire_key not in omitted["params"]
    assert explicit_empty["params"][wire_key] == []


def test_gemini_stt_maps_preview_parameters_to_production_extension() -> None:
    config = GeminiSTT(
        api_key=API_KEY,
        language_hints=["en-US", "es-ES"],
        custom_vocabulary=["Agora", "ConvoAI"],
    ).to_config()

    assert config["params"]["language_hints"] == ["en-US", "es-ES"]
    assert config["params"]["custom_vocabulary"] == ["Agora", "ConvoAI"]


def test_gemini_stt_deprecates_language_codes() -> None:
    with pytest.warns(DeprecationWarning, match="use language_hints instead"):
        config = GeminiSTT(api_key=API_KEY, language_codes=["en-US", "es-ES"]).to_config()

    assert config["params"]["language_hints"] == ["en-US", "es-ES"]


def test_gemini_stt_language_hints_take_priority_over_language_codes() -> None:
    with pytest.warns(DeprecationWarning, match="use language_hints instead"):
        config = GeminiSTT(
            api_key=API_KEY,
            language_codes=["en-US"],
            language_hints=[],
        ).to_config()

    assert config["params"]["language_hints"] == []


@pytest.mark.parametrize(
    ("options", "message"),
    [
        (
            {"custom_vocabulary": ["Agora"], "word_timestamp": True},
            "custom_vocabulary cannot be used with word_timestamp=true",
        ),
        (
            {"mode": "SMART", "word_timestamp": True},
            "GeminiSTT mode=SMART cannot be used with word_timestamp=true",
        ),
        (
            {"mode": "SMART", "diarization": True},
            "GeminiSTT mode=SMART cannot be used with diarization=true",
        ),
    ],
)
def test_gemini_stt_rejects_invalid_parameter_combinations(options, message) -> None:
    with pytest.raises(ValidationError, match=message):
        GeminiSTT(api_key=API_KEY, **options)


@pytest.mark.parametrize(
    "options",
    [
        {"mode": "SMART", "custom_vocabulary": ["Agora"]},
        {"mode": "VERBATIM", "word_timestamp": True, "diarization": True},
        {"mode": None, "word_timestamp": True, "diarization": True},
        {"mode": "", "word_timestamp": True, "diarization": True},
        {"custom_vocabulary": [], "word_timestamp": True},
    ],
)
def test_gemini_stt_accepts_valid_parameter_combinations(options) -> None:
    GeminiSTT(api_key=API_KEY, **options)


@pytest.mark.parametrize("mode", ["INVALID", "smart", 0, False])
def test_gemini_stt_rejects_invalid_mode_at_construction(mode) -> None:
    with pytest.raises(ValidationError, match="GeminiSTT mode must be SMART or VERBATIM"):
        GeminiSTT(api_key=API_KEY, mode=mode)


def test_gemini_stt_omits_empty_mode_and_nil_diarization() -> None:
    config = GeminiSTT(api_key=API_KEY, mode="", diarization=None).to_config()

    assert "mode" not in config["params"]
    assert "diarization" not in config["params"]


def test_gemini_stt_does_not_validate_additional_params() -> None:
    config = GeminiSTT(
        api_key=API_KEY,
        additional_params={
            "custom_vocabulary": ["Agora"],
            "word_timestamp": True,
            "mode": "SMART",
            "diarization": True,
        },
    ).to_config()

    assert config["params"]["custom_vocabulary"] == ["Agora"]
    assert config["params"]["word_timestamp"] is True
    assert config["params"]["mode"] == "SMART"
    assert config["params"]["diarization"] is True


def test_gemini_stt_explicit_fields_override_additional_params() -> None:
    config = GeminiSTT(
        api_key=API_KEY,
        model=MODEL,
        sample_rate=24000,
        language="en-US",
        language_hints=["en-US"],
        custom_vocabulary=["Agora"],
        word_timestamp=False,
        mode="SMART",
        diarization=False,
        additional_params={
            "api_key": "wrong-key",
            "model": "wrong-model",
            "sample_rate": 8000,
            "language": "fr-FR",
            "language_hints": ["fr-FR"],
            "custom_vocabulary": ["wrong"],
            "word_timestamp": True,
            "mode": "VERBATIM",
            "diarization": True,
            "provider_option": "kept",
        },
    ).to_config()

    assert config["params"] == {
        "api_key": API_KEY,
        "model": MODEL,
        "sample_rate": 24000,
        "language": "en-US",
        "language_hints": ["en-US"],
        "custom_vocabulary": ["Agora"],
        "word_timestamp": False,
        "mode": "SMART",
        "diarization": False,
        "provider_option": "kept",
    }


def test_gemini_stt_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        _gemini_stt(unknown_option=True)


def test_gemini_stt_is_available_from_standard_vendor_surfaces() -> None:
    assert agora_agent.GeminiSTT is GeminiSTT
    assert agora_agent.GeminiSTTModels is GeminiSTTModels
    assert "GeminiSTT" in agora_agent.__all__
    assert "GeminiSTTModels" in agora_agent.__all__
    assert "gemini" in GLOBAL_ASR_VENDORS
    assert GLOBAL_VENDOR_NAMESPACE.asr["gemini"] is GeminiSTT
    assert GlobalSTTVendors.gemini is GeminiSTT


def test_gemini_stt_preserves_preview_import_paths_and_constructor_usage() -> None:
    from agora_agent.agentkit.preview import GeminiSTT as PreviewGeminiSTT
    from agora_agent.agentkit.preview import GeminiSTTModels as PreviewGeminiSTTModels
    from agora_agent.agentkit.preview.vendors import GeminiSTT as PreviewVendorGeminiSTT

    assert PreviewGeminiSTT is GeminiSTT
    assert PreviewVendorGeminiSTT is GeminiSTT
    assert PreviewGeminiSTTModels is GeminiSTTModels
    with pytest.warns(DeprecationWarning, match="use language_hints instead"):
        config = PreviewGeminiSTT(
            api_key=API_KEY,
            model=None,
            language_codes=["en-US"],
            custom_vocabulary=["Agora"],
            sample_rate=None,
            word_timestamp=False,
            additional_params={"provider_option": "kept"},
        ).to_config()
    assert config == {
        "vendor": "gemini",
        "params": {
            "provider_option": "kept",
            "api_key": API_KEY,
            "model": GeminiSTTModels.TRANSCRIBE_35_LIVE,
            "sample_rate": 16000,
            "language_hints": ["en-US"],
            "custom_vocabulary": ["Agora"],
            "word_timestamp": False,
        },
    }


def test_retired_preview_helpers_remain_importable_without_preview_routing() -> None:
    from agora_agent.agentkit.preview import PreviewFeatures, required_preview_features

    assert PreviewFeatures.GEMINI_LIVE == "gemini-live"
    assert required_preview_features({"asr": {"vendor": "gemini"}}) == []


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
            "sample_rate": 16000,
            "language": "en-US",
            "language_hints": ["en-US", "es-ES"],
            "custom_vocabulary": ["Agora"],
            "word_timestamp": False,
            "mode": "VERBATIM",
            "diarization": True,
        },
    }
