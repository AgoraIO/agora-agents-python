"""Preview endpoint tests.

Wire-shape expectations are copied from the TypeScript suite so the three SDKs
stay byte-identical on the wire.
"""

import json

import httpx
import pytest

from agora_agent import Agora, Area, AsyncAgora
from agora_agent.agentkit import Agent
from agora_agent.agentkit.debug import REDACTED, redact_secrets
from agora_agent.agentkit.preview import (
    PREVIEW_API_BASE_URL,
    GeminiSTT,
    required_preview_features,
)
from agora_agent.agentkit.vendors import Gemini, GoogleTTS

API_KEY = "test-google-api-key"
APP_ID = "test-app-id-0123456789abcdefghij"
APP_CERTIFICATE = "test-app-certificate-01234567890"


def _client(transport=None, **kwargs):
    httpx_client = httpx.Client(transport=transport) if transport is not None else None
    return Agora(
        area=Area.US,
        app_id=APP_ID,
        app_certificate=APP_CERTIFICATE,
        httpx_client=httpx_client,
        **kwargs,
    )


def _with_preview_asr(agent):
    """Complete an agent with the preview ASR plus Gemini LLM and Google TTS.

    The preview ASR only reaches its provider through the preview endpoint, so
    this is what the routing and gating tests need to have configured.
    """
    return (
        agent.with_stt(GeminiSTT(api_key=API_KEY, language_codes=["en-US"]))
        .with_llm(Gemini(api_key=API_KEY, model="gemini-2.0-flash"))
        .with_tts(
            GoogleTTS(
                key=API_KEY,
                voice_name="en-US-Chirp3-HD-Charon",
                language_code="en-US",
            )
        )
    )


class _Recorder(httpx.MockTransport):
    """Captures every outgoing request and answers with a generic success body."""

    def __init__(self):
        self.requests = []
        super().__init__(self._handle)

    def _handle(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return httpx.Response(200, json={"agent_id": "agent-1", "data": {"list": []}})


# --- Vendor wire shapes -----------------------------------------------------


def test_gemini_transcribe_serialises_to_documented_asr_shape():
    config = GeminiSTT(api_key=API_KEY, language_codes=["en-US"]).to_config()

    assert config == {
        "vendor": "gemini",
        "params": {
            "api_key": API_KEY,
            "model": "gemini-3.5-transcribe-live",
            "sample_rate": 16000,
            "language_codes": ["en-US"],
        },
    }


def test_gemini_transcribe_allows_overrides():
    config = GeminiSTT(
        api_key=API_KEY,
        model="not-a-real-model",
        sample_rate=24000,
        word_timestamp=False,
        additional_params={"hotwords": ["Agora"]},
    ).to_config()

    assert config == {
        "vendor": "gemini",
        "params": {
            "hotwords": ["Agora"],
            "api_key": API_KEY,
            "model": "not-a-real-model",
            "sample_rate": 24000,
            "word_timestamp": False,
        },
    }


def test_emits_no_top_level_language_of_its_own():
    # Every STT vendor leaves asr.language to the Agent, which derives it from
    # the turn detection language. A vendor-level copy would be a no-op the
    # builder overwrites, so this one does not offer the option at all.
    config = GeminiSTT(api_key=API_KEY).to_config()

    assert "language" not in config
    assert "language" not in config["params"]
    # Nor does it invent language_codes — absent means auto-detect.
    assert "language_codes" not in config["params"]


def test_language_is_not_an_accepted_option():
    # extra="forbid", so a stale `language=` argument fails loudly rather than
    # being silently dropped.
    with pytest.raises(Exception):
        GeminiSTT(api_key=API_KEY, language="en-US")


def test_language_codes_is_sent_verbatim_when_supplied():
    single = GeminiSTT(api_key=API_KEY, language_codes=["es-ES"]).to_config()
    assert single["params"]["language_codes"] == ["es-ES"]

    multiple = GeminiSTT(api_key=API_KEY, language_codes=["en-US", "es-ES"]).to_config()
    assert multiple["params"]["language_codes"] == ["en-US", "es-ES"]


def test_explicit_empty_language_codes_still_reaches_the_wire():
    # `[]` is the caller spelling auto-detect outright; both that and omitting
    # the field mean the same thing to the provider.
    config = GeminiSTT(api_key=API_KEY, language_codes=[]).to_config()

    assert config["params"]["language_codes"] == []


def test_custom_vocabulary_is_sent_only_when_supplied():
    with_vocab = GeminiSTT(api_key=API_KEY, custom_vocabulary=["Agora", "Kubernetes"]).to_config()
    assert with_vocab["params"]["custom_vocabulary"] == ["Agora", "Kubernetes"]
    assert "word_timestamp" not in with_vocab["params"]

    without_vocab = GeminiSTT(api_key=API_KEY).to_config()
    assert "custom_vocabulary" not in without_vocab["params"]


def test_word_timestamp_is_sent_only_when_explicitly_supplied():
    without_timestamp = GeminiSTT(api_key=API_KEY).to_config()
    assert "word_timestamp" not in without_timestamp["params"]

    with_timestamp = GeminiSTT(api_key=API_KEY, word_timestamp=True).to_config()
    assert with_timestamp["params"]["word_timestamp"] is True


def test_custom_vocabulary_rejects_enabled_word_timestamps():
    incompatible_options = [
        {"custom_vocabulary": ["Agora"], "word_timestamp": True},
        {"custom_vocabulary": [], "word_timestamp": True},
        {
            "additional_params": {
                "custom_vocabulary": ["Agora"],
                "word_timestamp": True,
            }
        },
    ]

    for options in incompatible_options:
        with pytest.raises(
            ValueError,
            match="custom_vocabulary cannot be used with word_timestamp=true",
        ):
            GeminiSTT(api_key=API_KEY, **options).to_config()


def test_custom_vocabulary_allows_explicitly_disabled_word_timestamps():
    config = GeminiSTT(
        api_key=API_KEY,
        custom_vocabulary=["Agora"],
        word_timestamp=False,
    ).to_config()

    assert config["params"]["custom_vocabulary"] == ["Agora"]
    assert config["params"]["word_timestamp"] is False


# --- Routing ----------------------------------------------------------------


def test_sends_requests_to_the_preview_endpoint_with_the_gate_header():
    recorder = _Recorder()
    client = _client(transport=recorder)
    production_url = client.get_current_url()

    (
        _with_preview_asr(Agent(client=client))
        .create_session(channel="preview-channel", agent_uid="1", remote_uids=["100"])
        .start()
    )

    request = recorder.requests[0]
    assert str(request.url) == f"{PREVIEW_API_BASE_URL}/v2/projects/{APP_ID}/join"
    assert request.headers["agora-feature"] == "gemini-live"
    # Exactly one header may carry the preview value — the gateway accepts other
    # spellings that are not part of the public contract, and none may ship here.
    carriers = [name for name, value in request.headers.items() if "gemini-live" in value]
    assert carriers == ["agora-feature"]
    assert client.get_current_url() == production_url
    assert client._client_wrapper.get_base_url() == production_url
    assert "agora-feature" not in client._client_wrapper.get_headers()


def test_ga_session_stays_on_production_endpoint():
    recorder = _Recorder()
    client = _client(transport=recorder)
    production_url = client.get_current_url()

    Agent(client=client).create_session(
        channel="ga-channel",
        agent_uid="1",
        remote_uids=["100"],
        pipeline_id="pipeline-id",
    ).start()

    assert str(recorder.requests[0].url).startswith(production_url)
    assert "agora-feature" not in recorder.requests[0].headers


def test_keeps_the_gate_header_on_every_request():
    # A request that loses the header is routed to the production environment,
    # where the preview providers do not exist — so each verb must carry it.
    recorder = _Recorder()
    client = _client(transport=recorder)

    session = _with_preview_asr(Agent(client=client)).create_session(
        channel="preview-channel", agent_uid="1", remote_uids=["100"]
    )
    session.start()
    session.say("hello")
    session.interrupt()
    session.stop()

    assert len(recorder.requests) >= 4
    for request in recorder.requests:
        assert request.headers.get("agora-feature") == "gemini-live", request.url
        assert str(request.url).startswith(PREVIEW_API_BASE_URL)


def test_stop_agent_remains_production_only():
    recorder = _Recorder()
    client = _client(transport=recorder)
    production_url = client.get_current_url()

    client.stop_agent("agent-2")

    request = recorder.requests[0]
    assert str(request.url).startswith(production_url)
    assert "agora-feature" not in request.headers


def test_caller_headers_cannot_drop_the_gate():
    recorder = _Recorder()
    client = _client(transport=recorder, headers={"agora-feature": "", "x-custom": "kept"})

    (
        _with_preview_asr(Agent(client=client))
        .create_session(channel="preview-channel", agent_uid="1", remote_uids=["100"])
        .start()
    )

    request = recorder.requests[0]
    assert request.headers["agora-feature"] == "gemini-live"
    assert request.headers["x-custom"] == "kept"


@pytest.mark.asyncio
async def test_async_session_pins_the_preview_host_and_gate():
    recorder = _Recorder()
    client = AsyncAgora(
        area=Area.US,
        app_id=APP_ID,
        app_certificate=APP_CERTIFICATE,
        httpx_client=httpx.AsyncClient(transport=recorder),
    )
    session = _with_preview_asr(Agent(client=client)).create_async_session(
        channel="preview-channel", agent_uid="1", remote_uids=["100"]
    )

    await session.start()
    await session.say("hello")
    await session.interrupt()
    await session.stop()

    assert len(recorder.requests) == 4
    assert all(str(request.url).startswith(PREVIEW_API_BASE_URL) for request in recorder.requests)
    assert all(request.headers["agora-feature"] == "gemini-live" for request in recorder.requests)
    assert "agora-feature" not in client._client_wrapper.get_headers()


# --- Preview support guard --------------------------------------------------


def test_required_preview_features_flags_the_gemini_asr_vendor():
    assert required_preview_features({"asr": {"vendor": "gemini"}}) == ["gemini-live"]


def test_required_preview_features_leaves_a_ga_pipeline_alone():
    assert required_preview_features({"asr": {"vendor": "microsoft"}}) == []


# --- Debug redaction --------------------------------------------------------


def test_redact_secrets_walks_nested_structures():
    redacted = redact_secrets(
        {
            "appid": "81190c52971d4004b7244bdcd93e2f34",
            "properties": {
                "token": "007eJxTYKhsrH10",
                "asr": {"vendor": "gemini", "params": {"api_key": API_KEY, "model": "m"}},
                "mcp_servers": [{"name": "a", "headers": {"authorization": "Bearer x"}}],
            },
        }
    )

    assert redacted == {
        "appid": REDACTED,
        "properties": {
            "token": REDACTED,
            "asr": {"vendor": "gemini", "params": {"api_key": REDACTED, "model": "m"}},
            "mcp_servers": [{"name": "a", "headers": {"authorization": REDACTED}}],
        },
    }


def test_redact_secrets_covers_gemini_url_and_google_tts_credentials():
    redacted = redact_secrets(
        {
            "llm": {
                "url": (
                    "https://generativelanguage.googleapis.com/v1beta/models/"
                    f"gemini-2.0-flash:streamGenerateContent?alt=sse&key={API_KEY}"
                ),
            },
            "tts": {"params": {"credentials": API_KEY}},
        }
    )

    assert API_KEY not in json.dumps(redacted)


def test_redact_secrets_leaves_empty_values_visible():
    # "" is the signature of an unset env var and must stay diagnosable.
    assert redact_secrets({"params": {"api_key": ""}}) == {"params": {"api_key": ""}}


def test_redact_secrets_does_not_mutate_input():
    original = {"properties": {"asr": {"params": {"api_key": API_KEY}}}}
    redact_secrets(original)

    assert original["properties"]["asr"]["params"]["api_key"] == API_KEY


def test_debug_output_never_prints_a_live_credential(capsys):
    recorder = _Recorder()
    client = _client(transport=recorder)

    (
        Agent(client=client)
        .with_stt(GeminiSTT(api_key=API_KEY))
        .with_llm(Gemini(api_key=API_KEY, model="gemini-2.0-flash"))
        .with_tts(
            GoogleTTS(
                key=API_KEY,
                voice_name="en-US-Chirp3-HD-Charon",
                language_code="en-US",
            )
        )
        .create_session(channel="c", agent_uid="1", remote_uids=["100"], debug=True)
        .start()
    )

    output = capsys.readouterr().out
    assert API_KEY not in output
    assert "gemini" in output  # non-secret config stays readable

    # The request itself still carries the real key.
    sent = json.loads(recorder.requests[0].content)
    assert sent["properties"]["asr"]["params"]["api_key"] == API_KEY


# --- Vendor construction ----------------------------------------------------


def test_rejects_an_empty_api_key():
    # Field(...) alone makes the key required but still accepts "", which would
    # reach the provider as a blank credential. The TypeScript and Go vendors
    # both refuse it at construction, so this one does too.
    with pytest.raises(Exception):
        GeminiSTT(api_key="")
