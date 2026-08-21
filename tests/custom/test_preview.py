"""Preview endpoint tests.

Wire-shape expectations are copied from the TypeScript suite so the three SDKs
stay byte-identical on the wire.
"""

import json

import httpx
import pytest

from agora_agent import Area
from agora_agent.agentkit import Agent
from agora_agent.agentkit.debug import REDACTED, redact_secrets
from agora_agent.agentkit.preview import (
    PREVIEW_API_BASE_URL,
    AgoraPreview,
    AsyncAgoraPreview,
    GeminiCleverChatter,
    GeminiWalkieTalkie,
    apply_preview_shape,
    required_preview_features,
)
from agora_agent.pool_client import Agora

API_KEY = "test-google-api-key"
APP_ID = "test-app-id-0123456789abcdefghij"
APP_CERTIFICATE = "test-app-certificate-01234567890"


def _preview_client(transport=None, **kwargs):
    httpx_client = httpx.Client(transport=transport) if transport is not None else None
    return AgoraPreview(
        area=Area.US,
        app_id=APP_ID,
        app_certificate=APP_CERTIFICATE,
        httpx_client=httpx_client,
        **kwargs,
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


def test_walkie_talkie_serialises_to_documented_mllm_shape():
    config = GeminiWalkieTalkie(api_key=API_KEY).to_config()

    assert config == {
        "vendor": "gemini",
        "api_key": API_KEY,
        "url": "https://generativelanguage.googleapis.com",
        "params": {
            "api_key": API_KEY,
            "model": "walkie-talkie",
            "voice": "Puck",
        },
    }


def test_clever_chatter_includes_thinking_level():
    config = GeminiCleverChatter(api_key=API_KEY, voice="Puck", thinking_level="medium").to_config()

    assert config == {
        "vendor": "gemini",
        "api_key": API_KEY,
        "url": "https://generativelanguage.googleapis.com",
        "params": {
            "api_key": API_KEY,
            "model": "clever-chatter",
            "voice": "Puck",
            "thinking_level": "medium",
        },
    }


def test_walkie_talkie_rejects_thinking_level():
    # thinking_level is structurally exclusive to clever-chatter.
    with pytest.raises(Exception):
        GeminiWalkieTalkie(api_key=API_KEY, thinking_level="low")


def test_preview_mllm_carries_instructions_and_transcription_flags():
    config = GeminiWalkieTalkie(
        api_key=API_KEY,
        instructions="You are Ada.",
        transcribe_agent=True,
        transcribe_user=True,
    ).to_config()

    assert config["params"]["instructions"] == "You are Ada."
    assert config["params"]["transcribe_agent"] is True
    assert config["params"]["transcribe_user"] is True


def test_sends_greeting_never_greeting_message():
    # The preview Gemini models read `greeting`. `greeting_message` is what the
    # production providers use.
    with_greeting = GeminiWalkieTalkie(api_key=API_KEY, greeting="Hi there.").to_config()
    assert with_greeting["greeting"] == "Hi there."
    assert "greeting_message" not in with_greeting

    without_greeting = GeminiWalkieTalkie(api_key=API_KEY).to_config()
    assert "greeting" not in without_greeting
    assert "greeting_message" not in without_greeting


# --- Routing ----------------------------------------------------------------


def test_reports_the_preview_base_url():
    client = _preview_client()

    assert client.get_current_url() == PREVIEW_API_BASE_URL
    assert client._client_wrapper.get_base_url() == PREVIEW_API_BASE_URL


def test_does_not_participate_in_regional_failover():
    client = _preview_client()

    client.next_region()
    client.select_best_domain()

    assert client.get_current_url() == PREVIEW_API_BASE_URL


def test_accepts_a_base_url_override():
    client = _preview_client(base_url="https://staging.example.com/preview/api/conversational-ai-agent")

    assert client.get_current_url() == "https://staging.example.com/preview/api/conversational-ai-agent"


def test_honours_a_custom_feature_list():
    client = _preview_client(features=["gemini-live", "another-preview"])

    assert client._client_wrapper.get_headers()["agora-feature"] == "gemini-live,another-preview"


def test_sends_requests_to_the_preview_endpoint_with_the_gate_header():
    recorder = _Recorder()
    client = _preview_client(transport=recorder)

    (
        Agent(client=client)
        .with_mllm(GeminiCleverChatter(api_key=API_KEY, thinking_level="high"))
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


def test_keeps_the_gate_header_on_every_request():
    # A request that loses the header is routed to the production environment,
    # where the preview providers do not exist — so each verb must carry it.
    recorder = _Recorder()
    client = _preview_client(transport=recorder)

    session = (
        Agent(client=client)
        .with_mllm(GeminiWalkieTalkie(api_key=API_KEY))
        .create_session(channel="preview-channel", agent_uid="1", remote_uids=["100"])
    )
    session.start()
    session.interrupt()
    session.stop()
    client.stop_agent("agent-2")

    assert len(recorder.requests) >= 4
    for request in recorder.requests:
        assert request.headers.get("agora-feature") == "gemini-live", request.url


def test_caller_headers_cannot_drop_the_gate():
    recorder = _Recorder()
    client = _preview_client(transport=recorder, headers={"agora-feature": "", "x-custom": "kept"})

    (
        Agent(client=client)
        .with_mllm(GeminiWalkieTalkie(api_key=API_KEY))
        .create_session(channel="preview-channel", agent_uid="1", remote_uids=["100"])
        .start()
    )

    request = recorder.requests[0]
    assert request.headers["agora-feature"] == "gemini-live"
    assert request.headers["x-custom"] == "kept"


def test_async_client_pins_the_preview_host_and_gate():
    client = AsyncAgoraPreview(area=Area.US, app_id=APP_ID, app_certificate=APP_CERTIFICATE)

    assert client.get_current_url() == PREVIEW_API_BASE_URL
    assert client._client_wrapper.get_headers()["agora-feature"] == "gemini-live"


# --- Preview support guard --------------------------------------------------


def test_required_preview_features_flags_preview_mllm_models():
    assert required_preview_features({"mllm": {"vendor": "gemini", "params": {"model": "walkie-talkie"}}}) == [
        "gemini-live"
    ]


@pytest.mark.parametrize(
    "model",
    ["walkie-talkie", "clever-chatter", "gemini-3.5-live", "gemini-3.5-live-thinking"],
)
def test_required_preview_features_recognises_both_sides_of_the_rename(model):
    # Google is renaming the codenames; the guard has to keep working through
    # the rollout whichever spelling a caller sends.
    assert required_preview_features({"mllm": {"vendor": "gemini", "params": {"model": model}}}) == ["gemini-live"]


def test_required_preview_features_leaves_ga_gemini_live_alone():
    ga = {"mllm": {"vendor": "gemini", "params": {"model": "gemini-live-2.5-flash-preview-native-audio-09-2025"}}}

    assert required_preview_features(ga) == []


def test_start_rejects_preview_providers_on_the_production_client():
    client = Agora(area=Area.US, app_id=APP_ID, app_certificate=APP_CERTIFICATE)
    session = (
        Agent(client=client)
        .with_mllm(GeminiWalkieTalkie(api_key=API_KEY))
        .create_session(channel="preview-channel", agent_uid="1", remote_uids=["100"])
    )

    with pytest.raises(ValueError, match="require the preview endpoint"):
        session.start()


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


def test_redact_secrets_leaves_empty_values_visible():
    # "" is the signature of an unset env var and must stay diagnosable.
    assert redact_secrets({"params": {"api_key": ""}}) == {"params": {"api_key": ""}}


def test_redact_secrets_does_not_mutate_input():
    original = {"properties": {"asr": {"params": {"api_key": API_KEY}}}}
    redact_secrets(original)

    assert original["properties"]["asr"]["params"]["api_key"] == API_KEY


def test_debug_output_never_prints_a_live_credential(capsys):
    recorder = _Recorder()
    client = _preview_client(transport=recorder)

    (
        Agent(client=client)
        .with_mllm(GeminiWalkieTalkie(api_key=API_KEY))
        .create_session(channel="c", agent_uid="1", remote_uids=["100"], debug=True)
        .start()
    )

    output = capsys.readouterr().out
    assert API_KEY not in output
    assert "gemini" in output  # non-secret config stays readable

    # The request itself still carries the real key.
    sent = json.loads(recorder.requests[0].content)
    assert sent["properties"]["mllm"]["params"]["api_key"] == API_KEY


def test_preview_mllm_sends_language_codes_never_singular_language():
    # `mllm.params.language` belongs to xAI Grok in the Agora schema, and the
    # production Gemini Live provider sends no language field at all. The
    # preview MLLMs take the plural array.
    with_codes = GeminiWalkieTalkie(api_key=API_KEY, language_codes=["en-US"]).to_config()
    assert with_codes["params"]["language_codes"] == ["en-US"]
    assert "language" not in with_codes["params"]

    with_multiple = GeminiCleverChatter(api_key=API_KEY, language_codes=["en-US", "es-ES"]).to_config()
    assert with_multiple["params"]["language_codes"] == ["en-US", "es-ES"]


def test_preview_mllm_omits_language_codes_when_unset():
    config = GeminiWalkieTalkie(api_key=API_KEY).to_config()

    assert "language_codes" not in config["params"]
    assert "language" not in config["params"]


def test_preview_mllm_rejects_the_singular_language_argument():
    # extra="forbid", so a stale `language=` fails loudly rather than silently
    # writing into xAI's field.
    with pytest.raises(Exception):
        GeminiWalkieTalkie(api_key=API_KEY, language="en-US")


# --- Preview wire-shape translation -----------------------------------------


def _preview_mllm(**extra):
    config = {"vendor": "gemini", "params": {"model": "walkie-talkie"}}
    config.update(extra)
    return {"mllm": config}


def test_agent_level_greeting_is_retargeted_to_greeting():
    # Agent.to_properties writes agent-level greetings to greeting_message, the
    # production spelling. Without this step the preview model never greets.
    properties = _preview_mllm(greeting_message="AGENT")

    apply_preview_shape(properties)

    assert properties["mllm"]["greeting"] == "AGENT"
    assert "greeting_message" not in properties["mllm"]


def test_hand_written_greeting_message_migrates_onto_greeting():
    # Lets an existing MLLM config keep working after only swapping the model.
    properties = _preview_mllm(greeting_message="EXISTING")

    apply_preview_shape(properties)

    assert properties["mllm"]["greeting"] == "EXISTING"
    assert "greeting_message" not in properties["mllm"]


def test_vendor_greeting_wins_over_agent_level():
    properties = _preview_mllm(greeting="VENDOR", greeting_message="AGENT")

    apply_preview_shape(properties)

    assert properties["mllm"]["greeting"] == "VENDOR"
    assert "greeting_message" not in properties["mllm"]


def test_failure_message_is_left_alone():
    # failure_message is an Agora engine feature, not a Gemini one.
    properties = _preview_mllm(failure_message="One moment.")

    apply_preview_shape(properties)

    assert properties["mllm"]["failure_message"] == "One moment."


def test_production_mllm_is_left_untouched():
    properties = {
        "mllm": {
            "vendor": "gemini",
            "greeting_message": "PROD",
            "params": {"model": "gemini-2.0-flash-live-001"},
        }
    }

    apply_preview_shape(properties)

    assert properties["mllm"]["greeting_message"] == "PROD"
    assert "greeting" not in properties["mllm"]


def test_apply_preview_shape_is_a_no_op_without_mllm():
    properties = {"asr": {"vendor": "gemini"}}

    apply_preview_shape(properties)

    assert properties == {"asr": {"vendor": "gemini"}}


def test_started_request_carries_greeting_not_greeting_message():
    # End-to-end: proves apply_preview_shape is wired into start().
    recorder = _Recorder()
    client = _preview_client(transport=recorder)
    session = (
        Agent(client=client, greeting="AGENT")
        .with_mllm(GeminiWalkieTalkie(api_key=API_KEY))
        .create_session(channel="c", agent_uid="1", remote_uids=["100"])
    )
    session.start()

    mllm = json.loads(recorder.requests[0].content)["properties"]["mllm"]
    assert mllm["greeting"] == "AGENT"
    assert "greeting_message" not in mllm


def test_unrecognised_model_on_a_preview_vendor_still_gets_the_greeting_rename():
    # Overriding ``model`` is the documented escape hatch for a Google rename
    # that lands ahead of an SDK release, so a name this SDK has never seen is
    # reachable by following its own advice. Matching on the model name alone
    # made that case fail silently: no rename, and an agent-level greeting would
    # land in a field these models ignore.
    recorder = _Recorder()
    session = (
        Agent(client=_preview_client(transport=recorder), greeting="AGENT")
        .with_mllm(GeminiWalkieTalkie(api_key=API_KEY, model="gemini-4.0-live-unreleased"))
        .create_session(channel="c", agent_uid="1", remote_uids=["100"])
    )
    session.start()

    mllm = json.loads(recorder.requests[0].content)["properties"]["mllm"]
    assert mllm["greeting"] == "AGENT"
    assert "greeting_message" not in mllm


def test_unrecognised_model_on_a_preview_vendor_still_requires_the_preview_endpoint():
    properties = {
        "mllm": GeminiWalkieTalkie(api_key=API_KEY, model="gemini-4.0-live-unreleased").to_config(),
    }

    assert required_preview_features(properties) == ["gemini-live"]


def test_envelope_check_does_not_catch_a_production_gemini_live_config():
    # GeminiLive leaves params.api_key unset and does not point url at the
    # Gemini Developer API host, so widening detection must not retarget
    # greeting_message for a GA caller.
    properties = {
        "mllm": {
            "vendor": "gemini",
            "api_key": "prod-key",
            "url": "wss://generativelanguage.googleapis.com/ws",
            "greeting_message": "PROD",
            "params": {"model": "gemini-2.0-flash-live-001"},
        }
    }

    apply_preview_shape(properties)

    assert properties["mllm"]["greeting_message"] == "PROD"
    assert "greeting" not in properties["mllm"]
    assert required_preview_features(properties) == []


@pytest.mark.parametrize("cls", [GeminiWalkieTalkie, GeminiCleverChatter])
def test_rejects_an_empty_api_key(cls):
    # Field(...) alone makes the key required but still accepts "", which would
    # reach the provider as a blank credential. The TypeScript and Go vendors
    # both refuse it at construction, so this one does too.
    with pytest.raises(Exception):
        cls(api_key="")
