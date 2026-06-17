"""
test_request_body.py — Integration-level tests for request body shape.

Covers:
  Scenario 1  — BYOK pipeline (full properties shape)
  Scenario 2  — Preset-backed pipeline (managed vendors, field-stripping)
  Scenario 3  — LLM config fields win over agent-level convenience fields
  Scenario 4  — VertexAILLM URL construction
  Scenario 5  — OpenAISTT params (5a model, 5b prompt, 5c language, 5d defaults)
  Scenario 6  — Mixed preset + BYOK (6a ASR preset + BYOK LLM/TTS, 6b TTS preset + BYOK LLM/ASR)
  Scenario 7  — Pipeline ID (7b shape with BYOK LLM, 7c empty properties)
  Scenario 8  — MLLM mode (8a start call, 8b/8c agent-level greeting wins/vendor wins)
  BYOK vendor coverage matrix (all STT, LLM, TTS vendors)
  Preset coverage matrix (all inferred presets)
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from agora_agent import (
    Agent,
    AmazonBedrock,
    AmazonSTT,
    AmazonTTS,
    Anthropic,
    AresSTT,
    AssemblyAISTT,
    AzureOpenAI,
    CartesiaTTS,
    CustomLLM,
    DeepgramSTT,
    DeepgramTTS,
    Dify,
    ElevenLabsTTS,
    FishAudioTTS,
    Gemini,
    GeminiLive,
    GoogleSTT,
    GoogleTTS,
    Groq,
    HumeAITTS,
    MicrosoftSTT,
    MicrosoftTTS,
    MiniMaxTTS,
    MurfTTS,
    OpenAI,
    OpenAIRealtime,
    OpenAISTT,
    OpenAITTS,
    RimeTTS,
    SarvamSTT,
    SarvamTTS,
    SpeechmaticsSTT,
    VertexAI,
    VertexAILLM,
    XaiGrok,
)
from agora_agent.agentkit import AgentSession
from agora_agent.agentkit.presets import resolve_session_presets


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

APP_ID = "0" * 32
APP_CERTIFICATE = "1" * 32


def dump(value):
    if hasattr(value, "model_dump"):
        return value.model_dump(exclude_none=True)
    if hasattr(value, "dict"):
        return value.dict(exclude_none=True)
    return value


def dump_wire(value):
    if hasattr(value, "dict"):
        return value.dict(by_alias=True)
    return dump(value)


# ---------------------------------------------------------------------------
# Pattern 1: FakeAgentsClient — captures the full start() call
# ---------------------------------------------------------------------------


class StartResponse:
    agent_id = "agent-id"


class FakeAgentsClient:
    def __init__(self):
        self.calls = []

    def start(self, appid, **kwargs):
        self.calls.append({"appid": appid, **kwargs})
        return StartResponse()


class FakeAsyncAgentsClient:
    def __init__(self):
        self.calls = []

    async def start(self, appid, **kwargs):
        self.calls.append({"appid": appid, **kwargs})
        return StartResponse()


class FakeClient:
    app_id = "appid"
    app_certificate = None

    def __init__(self, agents):
        self.agents = agents


def start_session(agent, **session_kwargs):
    """Start agent session via FakeAgentsClient and return the captured call dict."""
    agents = FakeAgentsClient()
    client = FakeClient(agents)
    agent.create_session(
        client=client,
        channel="channel",
        token="test-token",
        agent_uid="1",
        remote_uids=["100"],
        **session_kwargs,
    ).start()
    return agents.calls[0]


async def start_async_session(agent, **session_kwargs):
    """Start async agent session via FakeAsyncAgentsClient and return the captured call dict."""
    agents = FakeAsyncAgentsClient()
    client = FakeClient(agents)
    await agent.create_async_session(
        client=client,
        channel="channel",
        token="test-token",
        agent_uid="1",
        remote_uids=["100"],
        **session_kwargs,
    ).start()
    return agents.calls[0]


def full_agent_with_tts(tts):
    return (
        Agent(name="support")
        .with_stt(DeepgramSTT(api_key="dg-key", model="nova-2", language="en"))
        .with_llm(
            OpenAI(
                api_key="openai-key",
                base_url="https://api.openai.com/v1/chat/completions",
                model="gpt-4o",
            )
        )
        .with_tts(tts)
    )


def invalid_google_tts_properties():
    return {
        "channel": "channel",
        "token": "test-token",
        "agent_rtc_uid": "1",
        "remote_rtc_uids": ["100"],
        "tts": {
            "vendor": "google",
            "params": {
                "credentials": "{}",
            },
        },
    }


# ---------------------------------------------------------------------------
# Pattern 2: _build_start_properties — properties-only shape
# ---------------------------------------------------------------------------


class _Agents:
    def start(self, app_id, name, properties, preset=None, pipeline_id=None, request_options=None):
        return SimpleNamespace(agent_id="agent-1")


class _Client:
    auth_mode = "basic"
    app_id = APP_ID
    app_certificate = APP_CERTIFICATE

    def __init__(self):
        self.agents = _Agents()
        self.agent_management = object()


def build_properties(agent, allow_missing=None):
    session = AgentSession(
        client=_Client(),
        agent=agent,
        app_id=APP_ID,
        app_certificate=APP_CERTIFICATE,
        name="test",
        channel="channel",
        agent_uid="1",
        remote_uids=["100"],
    )
    return session._build_start_properties(  # noqa: SLF001
        {"app_id": APP_ID, "app_certificate": APP_CERTIFICATE},
        skip_vendor_validation_categories=set(),
        allow_missing_vendor_categories=allow_missing or set(),
    )


def test_request_properties_validation_raises_without_preset_or_pipeline() -> None:
    with pytest.raises(Exception):
        AgentSession._request_properties_for_start(  # noqa: SLF001
            invalid_google_tts_properties(),
            resolved_preset=None,
            pipeline_id=None,
        )


def test_request_properties_validation_fallback_allows_preset_partial_config() -> None:
    properties = invalid_google_tts_properties()

    request_properties = AgentSession._request_properties_for_start(  # noqa: SLF001
        properties,
        resolved_preset="openai_tts_1",
        pipeline_id=None,
    )

    assert request_properties is properties


def test_request_properties_validation_fallback_is_limited_to_preset_category() -> None:
    with pytest.raises(Exception):
        AgentSession._request_properties_for_start(  # noqa: SLF001
            invalid_google_tts_properties(),
            resolved_preset="openai_gpt_4o_mini",
            pipeline_id=None,
        )


def test_request_properties_validation_fallback_allows_pipeline_partial_config() -> None:
    properties = invalid_google_tts_properties()

    request_properties = AgentSession._request_properties_for_start(  # noqa: SLF001
        properties,
        resolved_preset=None,
        pipeline_id="pipeline-id",
    )

    assert request_properties is properties


# ===========================================================================
# Scenario 1 — BYOK pipeline (full properties shape)
# ===========================================================================


def test_byok_pipeline_full_properties_shape() -> None:
    """OpenAI BYOK LLM + Deepgram BYOK STT + ElevenLabs TTS produces expected properties."""
    agent = (
        Agent(name="support")
        .with_stt(DeepgramSTT(api_key="dg-key", model="nova-2", language="en"))
        .with_llm(
            OpenAI(
                api_key="openai-key",
                base_url="https://api.openai.com/v1/chat/completions",
                model="gpt-4o",
            )
        )
        .with_tts(
            ElevenLabsTTS(
                key="el-key",
                model_id="eleven_flash_v2_5",
                voice_id="voice123",
                base_url="wss://api.elevenlabs.io/v1",
            )
        )
    )

    props = build_properties(agent)

    # RTC routing
    assert props["channel"] == "channel"
    assert props["agent_rtc_uid"] == "1"
    assert props["remote_rtc_uids"] == ["100"]

    # ASR
    asr = props["asr"]
    assert asr["vendor"] == "deepgram"
    assert asr["params"]["key"] == "dg-key"
    assert asr["params"]["model"] == "nova-2"
    assert asr["params"]["language"] == "en"

    # LLM
    llm = props["llm"]
    assert llm["api_key"] == "openai-key"
    assert llm["style"] == "openai"
    assert llm["params"]["model"] == "gpt-4o"

    # TTS
    tts = props["tts"]
    assert tts["vendor"] == "elevenlabs"
    assert tts["params"]["key"] == "el-key"
    assert tts["params"]["model_id"] == "eleven_flash_v2_5"
    assert tts["params"]["voice_id"] == "voice123"


# ===========================================================================
# Scenario 2 — Preset-backed pipeline (full start request, field stripping)
# ===========================================================================


def test_managed_llm_and_tts_produce_preset_and_strip_fields() -> None:
    """Managed OpenAI LLM + MiniMax TTS generate preset string and strip BYOK fields."""
    agent = (
        Agent(name="support")
        .with_llm(OpenAI(model="gpt-4o-mini"))
        .with_tts(MiniMaxTTS(model="speech_2_8_turbo", voice_id="English_captivating_female1"))
    )

    call = start_session(agent)
    assert "openai_gpt_4o_mini" in (call["preset"] or "")
    assert "minimax_speech_2_8_turbo" in (call["preset"] or "")

    properties = dump(call["properties"])
    # api_key and url stripped for managed LLM
    assert "api_key" not in properties.get("llm", {})
    # vendor retained for TTS
    assert properties["tts"]["vendor"] == "minimax"
    # BYOK key stripped for managed TTS
    assert "key" not in properties["tts"].get("params", {})


# ===========================================================================
# Scenario 3 — LLM config wins over agent-level fields
# ===========================================================================


def test_llm_config_greeting_wins_over_agent_level_greeting() -> None:
    """When OpenAI vendor sets greeting_message it overrides agent.with_greeting()."""
    agent = (
        Agent(name="support")
        .with_llm(
            OpenAI(
                api_key="openai-key",
                base_url="https://api.openai.com/v1/chat/completions",
                model="gpt-4o",
                greeting_message="vendor greeting",
            )
        )
        .with_greeting("agent greeting")
    )

    props = build_properties(agent, allow_missing={"asr", "tts"})
    assert props["llm"]["greeting_message"] == "vendor greeting"


# ===========================================================================
# Scenario 4 — VertexAILLM URL construction
# ===========================================================================


def test_vertex_ai_llm_constructs_correct_url_and_params() -> None:
    """VertexAILLM auto-constructs the aiplatform URL; project_id/location are URL-encoded, not in params."""
    agent = Agent(name="support").with_llm(
        VertexAILLM(
            api_key="vertex-token",
            model="gemini-2.0-flash",
            project_id="my-project",
            location="us-central1",
        )
    )

    props = build_properties(agent, allow_missing={"asr", "tts"})
    llm = props["llm"]

    expected_url_fragment = "us-central1-aiplatform.googleapis.com"
    assert expected_url_fragment in llm["url"]
    assert "my-project" in llm["url"]
    assert llm["style"] == "gemini"
    assert llm["params"]["model"] == "gemini-2.0-flash"
    assert "project_id" not in llm["params"]
    assert "location" not in llm["params"]


# ===========================================================================
# Scenario 5 — OpenAISTT params
# ===========================================================================


def test_openai_stt_5a_model_param_is_sent() -> None:
    """5a: OpenAISTT model appears inside input_audio_transcription.model."""
    agent = Agent(name="support").with_stt(
        OpenAISTT(
            api_key="oai-key",
            model="gpt-4o-mini-transcribe",
            prompt="transcribe clearly",
            language="en",
        )
    )

    props = build_properties(agent, allow_missing={"llm", "tts"})
    transcription = props["asr"]["params"]["input_audio_transcription"]
    assert transcription["model"] == "gpt-4o-mini-transcribe"


def test_openai_stt_5b_prompt_param_is_sent() -> None:
    """5b: OpenAISTT prompt appears inside input_audio_transcription.prompt."""
    agent = Agent(name="support").with_stt(
        OpenAISTT(
            api_key="oai-key",
            model="gpt-4o-mini-transcribe",
            prompt="use proper nouns",
            language="en",
        )
    )

    props = build_properties(agent, allow_missing={"llm", "tts"})
    transcription = props["asr"]["params"]["input_audio_transcription"]
    assert transcription["prompt"] == "use proper nouns"


def test_openai_stt_5c_language_param_is_sent() -> None:
    """5c: OpenAISTT language appears inside input_audio_transcription.language."""
    agent = Agent(name="support").with_stt(
        OpenAISTT(
            api_key="oai-key",
            model="gpt-4o-mini-transcribe",
            prompt="some prompt",
            language="fr",
        )
    )

    props = build_properties(agent, allow_missing={"llm", "tts"})
    transcription = props["asr"]["params"]["input_audio_transcription"]
    assert transcription["language"] == "fr"


def test_openai_stt_5d_api_key_is_top_level_in_params() -> None:
    """5d: OpenAISTT api_key is a top-level key inside asr.params (not inside input_audio_transcription)."""
    agent = Agent(name="support").with_stt(
        OpenAISTT(
            api_key="oai-key",
            model="gpt-4o-mini-transcribe",
            prompt="some prompt",
            language="en",
        )
    )

    props = build_properties(agent, allow_missing={"llm", "tts"})
    asr_params = props["asr"]["params"]
    assert asr_params["api_key"] == "oai-key"
    assert "api_key" not in asr_params.get("input_audio_transcription", {})


# ===========================================================================
# Scenario 6 — Mixed preset + BYOK
# ===========================================================================


def test_6a_asr_preset_with_byok_llm_and_tts() -> None:
    """6a: Managed Deepgram ASR preset + BYOK LLM + BYOK TTS."""
    agent = (
        Agent(name="support")
        .with_stt(DeepgramSTT(model="nova-3", language="en-US"))
        .with_llm(
            OpenAI(
                api_key="openai-key",
                base_url="https://api.openai.com/v1/chat/completions",
                model="gpt-4o",
            )
        )
        .with_tts(
            ElevenLabsTTS(
                key="el-key",
                model_id="eleven_flash_v2_5",
                voice_id="voice123",
                base_url="wss://api.elevenlabs.io/v1",
            )
        )
    )

    call = start_session(agent)
    preset = call.get("preset") or ""
    assert "deepgram_nova_3" in preset
    # No LLM or TTS preset inferred
    assert "openai_gpt" not in preset
    assert "openai_tts" not in preset

    properties = dump(call["properties"])
    assert properties["llm"]["api_key"] == "openai-key"
    assert properties["tts"]["vendor"] == "elevenlabs"


def test_6b_tts_preset_with_byok_llm_and_asr() -> None:
    """6b: Managed OpenAITTS preset + BYOK LLM + BYOK Deepgram ASR."""
    agent = (
        Agent(name="support")
        .with_stt(DeepgramSTT(api_key="dg-key", model="nova-2", language="en-US"))
        .with_llm(
            OpenAI(
                api_key="openai-key",
                base_url="https://api.openai.com/v1/chat/completions",
                model="gpt-4o",
            )
        )
        .with_tts(OpenAITTS(voice="alloy"))
    )

    call = start_session(agent)
    preset = call.get("preset") or ""
    assert "openai_tts_1" in preset
    assert "deepgram_nova_2" not in preset  # BYOK key present — no ASR preset inferred

    properties = dump(call["properties"])
    # BYOK ASR: key and model both retained (nothing stripped for BYOK path)
    assert properties["asr"]["params"]["key"] == "dg-key"
    assert properties["asr"]["params"]["model"] == "nova-2"
    # BYOK LLM key retained
    assert properties["llm"]["api_key"] == "openai-key"
    # TTS api_key stripped (managed)
    assert "api_key" not in properties["tts"].get("params", {})


# ===========================================================================
# Scenario 7 — Pipeline ID
# ===========================================================================


def test_7b_pipeline_id_with_byok_llm_override() -> None:
    """7b: pipeline_id present, single LLM override, ASR/TTS absent from properties."""
    agent = Agent(name="support", pipeline_id="studio-pipeline").with_llm(
        OpenAI(
            api_key="openai-key",
            base_url="https://api.openai.com/v1/chat/completions",
            model="gpt-4o",
        )
    )

    call = start_session(agent)
    assert call["pipeline_id"] == "studio-pipeline"
    properties = dump(call["properties"])
    assert properties["llm"]["api_key"] == "openai-key"
    assert "asr" not in properties
    assert "tts" not in properties


def test_7c_pipeline_id_empty_properties_no_vendors() -> None:
    """7c: pipeline_id alone — no vendor keys in properties."""
    agent = Agent(name="support", pipeline_id="studio-pipeline")

    call = start_session(agent)
    assert call["pipeline_id"] == "studio-pipeline"
    properties = dump(call["properties"])
    assert "asr" not in properties
    assert "llm" not in properties
    assert "tts" not in properties


def test_7d_pipeline_id_with_byok_tts_only() -> None:
    """7d: pipeline_id present, TTS-only BYOK override — ASR and LLM absent from properties."""
    agent = Agent(name="support", pipeline_id="studio-pipeline").with_tts(
        ElevenLabsTTS(
            key="el-key",
            model_id="eleven_flash_v2_5",
            voice_id="some-voice",
            base_url="wss://api.elevenlabs.io/v1",
        )
    )

    call = start_session(agent)
    assert call["pipeline_id"] == "studio-pipeline"
    properties = dump(call["properties"])
    assert "asr" not in properties
    assert "llm" not in properties
    assert properties["tts"]["vendor"] == "elevenlabs"
    assert properties["tts"]["params"]["key"] == "el-key"


def test_7e_pipeline_id_with_byok_asr_and_tts() -> None:
    """7e: pipeline_id present, ASR+TTS BYOK overrides — LLM absent from properties."""
    agent = (
        Agent(name="support", pipeline_id="studio-pipeline")
        .with_stt(DeepgramSTT(api_key="dg-key", language="en"))
        .with_tts(
            ElevenLabsTTS(
                key="el-key",
                model_id="eleven_flash_v2_5",
                voice_id="some-voice",
                base_url="wss://api.elevenlabs.io/v1",
            )
        )
    )

    call = start_session(agent)
    assert call["pipeline_id"] == "studio-pipeline"
    properties = dump(call["properties"])
    assert "llm" not in properties
    assert properties["asr"]["vendor"] == "deepgram"
    assert properties["tts"]["vendor"] == "elevenlabs"


# ===========================================================================
# Scenario 8 — MLLM mode
# ===========================================================================


def test_8a_mllm_start_call_has_correct_top_level_vendor() -> None:
    """8a: OpenAIRealtime MLLM session – start call contains mllm with vendor=openai."""
    agent = Agent(name="support").with_mllm(
        OpenAIRealtime(api_key="realtime-key", model="gpt-4o-realtime-preview", voice="coral")
    )

    call = start_session(agent)
    properties = dump(call["properties"])
    assert "mllm" in properties
    mllm = properties["mllm"]
    assert mllm["vendor"] == "openai"
    assert mllm["api_key"] == "realtime-key"
    assert mllm["params"]["model"] == "gpt-4o-realtime-preview"
    assert mllm["params"]["voice"] == "coral"


def test_8b_agent_greeting_fills_mllm_when_vendor_omits_it() -> None:
    """8b: agent.with_greeting() fills mllm.greeting_message when vendor does not set it."""
    agent = (
        Agent(name="support")
        .with_mllm(OpenAIRealtime(api_key="realtime-key"))
        .with_greeting("hello from agent")
    )

    props = build_properties(agent)
    assert props["mllm"]["greeting_message"] == "hello from agent"


def test_8c_vendor_greeting_wins_over_agent_level_greeting_in_mllm() -> None:
    """8c: Vendor-level greeting_message wins over agent.with_greeting() in MLLM mode."""
    agent = (
        Agent(name="support")
        .with_mllm(
            OpenAIRealtime(
                api_key="realtime-key",
                greeting_message="vendor greeting",
            )
        )
        .with_greeting("agent greeting")
    )

    props = build_properties(agent)
    assert props["mllm"]["greeting_message"] == "vendor greeting"


# ===========================================================================
# BYOK Vendor Coverage Matrix — STT vendors
# ===========================================================================


def test_byok_deepgram_stt_params() -> None:
    agent = Agent(name="t").with_stt(
        DeepgramSTT(api_key="dg-key", model="nova-2", language="en")
    )
    props = build_properties(agent, allow_missing={"llm", "tts"})
    assert props["asr"]["vendor"] == "deepgram"
    assert props["asr"]["params"]["key"] == "dg-key"
    assert props["asr"]["params"]["model"] == "nova-2"
    assert props["asr"]["params"]["language"] == "en"


def test_byok_microsoft_stt_params() -> None:
    agent = Agent(name="t").with_stt(
        MicrosoftSTT(key="ms-key", region="eastus", language="en-US")
    )
    props = build_properties(agent, allow_missing={"llm", "tts"})
    assert props["asr"]["vendor"] == "microsoft"
    assert props["asr"]["params"]["key"] == "ms-key"
    assert props["asr"]["params"]["region"] == "eastus"
    assert props["asr"]["params"]["language"] == "en-US"


def test_byok_google_stt_params() -> None:
    agent = Agent(name="t").with_stt(
        GoogleSTT(
            project_id="my-project",
            location="global",
            adc_credentials_string="{}",
            language="en-US",
            model="long",
        )
    )
    props = build_properties(agent, allow_missing={"llm", "tts"})
    assert props["asr"]["vendor"] == "google"
    p = props["asr"]["params"]
    assert p["project_id"] == "my-project"
    assert p["location"] == "global"
    assert p["language"] == "en-US"
    assert p["model"] == "long"


def test_byok_amazon_stt_params() -> None:
    agent = Agent(name="t").with_stt(
        AmazonSTT(access_key="ak", secret_key="sk", region="us-east-1", language="en-US")
    )
    props = build_properties(agent, allow_missing={"llm", "tts"})
    assert props["asr"]["vendor"] == "amazon"
    p = props["asr"]["params"]
    assert p["access_key_id"] == "ak"
    assert p["secret_access_key"] == "sk"
    assert p["region"] == "us-east-1"
    assert p["language_code"] == "en-US"


def test_byok_assemblyai_stt_params() -> None:
    agent = Agent(name="t").with_stt(
        AssemblyAISTT(api_key="assembly-key", language="en-US")
    )
    props = build_properties(agent, allow_missing={"llm", "tts"})
    assert props["asr"]["vendor"] == "assemblyai"
    assert props["asr"]["params"]["api_key"] == "assembly-key"
    assert props["asr"]["params"]["language"] == "en-US"


def test_byok_ares_stt_no_params() -> None:
    agent = Agent(name="t").with_stt(AresSTT())
    props = build_properties(agent, allow_missing={"llm", "tts"})
    assert props["asr"]["vendor"] == "ares"
    assert "params" not in props["asr"]


def test_byok_speechmatics_stt_params() -> None:
    agent = Agent(name="t").with_stt(
        SpeechmaticsSTT(api_key="sm-key", language="en")
    )
    props = build_properties(agent, allow_missing={"llm", "tts"})
    assert props["asr"]["vendor"] == "speechmatics"
    assert props["asr"]["params"]["api_key"] == "sm-key"
    assert props["asr"]["params"]["language"] == "en"


def test_byok_sarvam_stt_params() -> None:
    agent = Agent(name="t").with_stt(
        SarvamSTT(api_key="sarvam-key", language="en-IN")
    )
    props = build_properties(agent, allow_missing={"llm", "tts"})
    assert props["asr"]["vendor"] == "sarvam"
    assert props["asr"]["params"]["api_key"] == "sarvam-key"
    assert props["asr"]["params"]["language"] == "en-IN"


# ---------------------------------------------------------------------------
# BYOK Vendor Coverage Matrix — LLM vendors
# ---------------------------------------------------------------------------


def test_byok_openai_llm_params() -> None:
    agent = Agent(name="t").with_llm(
        OpenAI(
            api_key="openai-key",
            base_url="https://api.openai.com/v1/chat/completions",
            model="gpt-4o",
        )
    )
    props = build_properties(agent, allow_missing={"asr", "tts"})
    assert props["llm"]["api_key"] == "openai-key"
    assert props["llm"]["style"] == "openai"
    assert props["llm"]["params"]["model"] == "gpt-4o"


def test_byok_azure_openai_llm_params() -> None:
    agent = Agent(name="t").with_llm(
        AzureOpenAI(
            api_key="azure-key",
            endpoint="https://example.openai.azure.com",
            deployment_name="my-deployment",
            model="gpt-4o",
        )
    )
    props = build_properties(agent, allow_missing={"asr", "tts"})
    assert props["llm"]["api_key"] == "azure-key"
    assert props["llm"]["style"] == "openai"
    assert props["llm"]["params"]["model"] == "gpt-4o"


def test_byok_anthropic_llm_params() -> None:
    agent = Agent(name="t").with_llm(
        Anthropic(
            api_key="anthropic-key",
            model="claude-3-5-sonnet-20241022",
            url="https://api.anthropic.com/v1/messages",
            headers={"anthropic-version": "2023-06-01"},
            max_tokens=1024,
        )
    )
    props = build_properties(agent, allow_missing={"asr", "tts"})
    assert props["llm"]["api_key"] == "anthropic-key"
    assert props["llm"]["style"] == "anthropic"
    assert props["llm"]["headers"]["anthropic-version"] == "2023-06-01"
    assert props["llm"]["params"]["max_tokens"] == 1024


def test_byok_gemini_llm_params() -> None:
    agent = Agent(name="t").with_llm(
        Gemini(api_key="gemini-key", model="gemini-2.0-flash")
    )
    props = build_properties(agent, allow_missing={"asr", "tts"})
    assert props["llm"]["api_key"] == "gemini-key"
    assert props["llm"]["style"] == "gemini"
    assert props["llm"]["params"]["model"] == "gemini-2.0-flash"


def test_byok_groq_llm_params() -> None:
    agent = Agent(name="t").with_llm(
        Groq(
            api_key="groq-key",
            model="llama-3.3-70b-versatile",
            base_url="https://api.groq.com/openai/v1/chat/completions",
        )
    )
    props = build_properties(agent, allow_missing={"asr", "tts"})
    assert props["llm"]["api_key"] == "groq-key"
    assert props["llm"]["style"] == "openai"
    assert props["llm"]["params"]["model"] == "llama-3.3-70b-versatile"


def test_byok_custom_llm_params() -> None:
    agent = Agent(name="t").with_llm(
        CustomLLM(
            api_key="custom-key",
            model="my-model",
            base_url="https://llm.example.com/chat",
        )
    )
    props = build_properties(agent, allow_missing={"asr", "tts"})
    assert props["llm"]["api_key"] == "custom-key"
    assert props["llm"]["vendor"] == "custom"
    assert props["llm"]["style"] == "openai"


def test_byok_amazon_bedrock_llm_params() -> None:
    agent = Agent(name="t").with_llm(
        AmazonBedrock(
            access_key="aws-access",
            secret_key="aws-secret",
            region="us-east-1",
            model="anthropic.claude-3-5-sonnet-20241022-v2:0",
        )
    )
    props = build_properties(agent, allow_missing={"asr", "tts"})
    assert props["llm"]["style"] == "bedrock"
    assert props["llm"]["access_key"] == "aws-access"
    assert "us-east-1" in props["llm"]["url"]


def test_byok_dify_llm_params() -> None:
    agent = Agent(name="t").with_llm(
        Dify(
            api_key="dify-key",
            url="https://api.dify.ai/v1/chat-messages",
            model="default",
        )
    )
    props = build_properties(agent, allow_missing={"asr", "tts"})
    assert props["llm"]["api_key"] == "dify-key"
    assert props["llm"]["style"] == "dify"
    assert props["llm"]["params"]["model"] == "default"


# ---------------------------------------------------------------------------
# BYOK Vendor Coverage Matrix — TTS vendors
# ---------------------------------------------------------------------------


def test_byok_elevenlabs_tts_params() -> None:
    agent = Agent(name="t").with_tts(
        ElevenLabsTTS(
            key="el-key",
            model_id="eleven_flash_v2_5",
            voice_id="voice",
            base_url="wss://api.elevenlabs.io/v1",
        )
    )
    props = build_properties(agent, allow_missing={"asr", "llm"})
    assert props["tts"]["vendor"] == "elevenlabs"
    assert props["tts"]["params"]["key"] == "el-key"
    assert props["tts"]["params"]["model_id"] == "eleven_flash_v2_5"
    assert props["tts"]["params"]["voice_id"] == "voice"


def test_byok_microsoft_tts_params() -> None:
    agent = Agent(name="t").with_tts(
        MicrosoftTTS(key="ms-key", region="eastus", voice_name="en-US-JennyNeural")
    )
    props = build_properties(agent, allow_missing={"asr", "llm"})
    assert props["tts"]["vendor"] == "microsoft"
    assert props["tts"]["params"]["key"] == "ms-key"
    assert props["tts"]["params"]["region"] == "eastus"
    assert props["tts"]["params"]["voice_name"] == "en-US-JennyNeural"


def test_byok_openai_tts_params() -> None:
    agent = Agent(name="t").with_tts(
        OpenAITTS(
            api_key="oai-tts-key",
            voice="alloy",
            model="tts-1-hd",
            base_url="https://api.openai.com/v1",
        )
    )
    props = build_properties(agent, allow_missing={"asr", "llm"})
    assert props["tts"]["vendor"] == "openai"
    assert props["tts"]["params"]["api_key"] == "oai-tts-key"
    assert props["tts"]["params"]["model"] == "tts-1-hd"
    assert props["tts"]["params"]["voice"] == "alloy"


def test_byok_cartesia_tts_params() -> None:
    agent = Agent(name="t").with_tts(
        CartesiaTTS(api_key="cartesia-key", voice_id="voice", model_id="sonic-2", sample_rate=24000)
    )
    props = build_properties(agent, allow_missing={"asr", "llm"})
    assert props["tts"]["vendor"] == "cartesia"
    p = props["tts"]["params"]
    assert p["api_key"] == "cartesia-key"
    assert p["voice"] == {"mode": "id", "id": "voice"}


def test_byok_google_tts_params() -> None:
    config = GoogleTTS(key="{}", voice_name="en-US-JennyNeural", language_code="en-US", sample_rate_hertz=24000).to_config()
    assert config["vendor"] == "google"
    p = config["params"]
    assert p["credentials"] == "{}"
    assert p["VoiceSelectionParams"]["name"] == "en-US-JennyNeural"
    assert p["VoiceSelectionParams"]["language_code"] == "en-US"


def test_byok_amazon_tts_params() -> None:
    agent = Agent(name="t").with_tts(
        AmazonTTS(access_key="access", secret_key="secret", region="us-east-1", voice_id="Joanna", engine="neural")
    )
    props = build_properties(agent, allow_missing={"asr", "llm"})
    assert props["tts"]["vendor"] == "amazon"
    p = props["tts"]["params"]
    assert p["aws_access_key_id"] == "access"
    assert p["aws_secret_access_key"] == "secret"
    assert p["voice"] == "Joanna"


def test_byok_deepgram_tts_params() -> None:
    agent = Agent(name="t").with_tts(
        DeepgramTTS(api_key="dg-tts-key", model="aura-2-thalia-en", base_url="wss://api.deepgram.com/v1/speak", sample_rate=24000)
    )
    props = build_properties(agent, allow_missing={"asr", "llm"})
    assert props["tts"]["vendor"] == "deepgram"
    assert props["tts"]["params"]["api_key"] == "dg-tts-key"
    assert props["tts"]["params"]["model"] == "aura-2-thalia-en"


def test_byok_humeai_tts_params() -> None:
    agent = Agent(name="t").with_tts(
        HumeAITTS(key="hume-key", voice_id="voice", provider="CUSTOM_VOICE")
    )
    props = build_properties(agent, allow_missing={"asr", "llm"})
    assert props["tts"]["vendor"] == "humeai"
    assert props["tts"]["params"]["key"] == "hume-key"
    assert props["tts"]["params"]["voice_id"] == "voice"


def test_byok_rime_tts_params() -> None:
    config = RimeTTS(key="rime-key", speaker="speaker", model_id="mist").to_config()
    assert config["vendor"] == "rime"
    assert config["params"]["api_key"] == "rime-key"
    assert config["params"]["speaker"] == "speaker"
    assert config["params"]["modelId"] == "mist"


def test_byok_fishaudio_tts_params() -> None:
    agent = Agent(name="t").with_tts(
        FishAudioTTS(key="fish-key", reference_id="ref", backend="speech-1.5")
    )
    props = build_properties(agent, allow_missing={"asr", "llm"})
    assert props["tts"]["vendor"] == "fishaudio"
    assert props["tts"]["params"]["api_key"] == "fish-key"
    assert props["tts"]["params"]["reference_id"] == "ref"


def test_byok_minimax_byok_tts_params() -> None:
    agent = Agent(name="t").with_tts(
        MiniMaxTTS(
            key="mm-key",
            group_id="group",
            model="speech-02-turbo",
            voice_id="voice",
            url="wss://api-uw.minimax.io/ws/v1/t2a_v2",
        )
    )
    props = build_properties(agent, allow_missing={"asr", "llm"})
    assert props["tts"]["vendor"] == "minimax"
    assert props["tts"]["params"]["key"] == "mm-key"


def test_byok_sarvam_tts_params() -> None:
    agent = Agent(name="t").with_tts(
        SarvamTTS(key="sarvam-key", speaker="anushka", target_language_code="en-IN", sample_rate=24000)
    )
    props = build_properties(agent, allow_missing={"asr", "llm"})
    assert props["tts"]["vendor"] == "sarvam"
    assert props["tts"]["params"]["api_subscription_key"] == "sarvam-key"
    assert props["tts"]["params"]["speaker"] == "anushka"


def test_byok_murf_tts_params() -> None:
    agent = Agent(name="t").with_tts(MurfTTS(key="murf-key", voice_id="Ariana"))
    props = build_properties(agent, allow_missing={"asr", "llm"})
    assert props["tts"]["vendor"] == "murf"
    assert props["tts"]["params"]["api_key"] == "murf-key"
    assert props["tts"]["params"]["voiceId"] == "Ariana"


def test_start_session_google_tts_preserves_wire_aliases() -> None:
    agent = full_agent_with_tts(
        GoogleTTS(
            key="{}",
            voice_name="en-US-JennyNeural",
            language_code="en-US",
            sample_rate_hertz=24000,
        )
    )

    call = start_session(agent)
    properties = dump_wire(call["properties"])
    params = properties["tts"]["params"]

    assert params["VoiceSelectionParams"]["name"] == "en-US-JennyNeural"
    assert params["VoiceSelectionParams"]["language_code"] == "en-US"
    assert params["AudioConfig"]["sample_rate_hertz"] == 24000
    assert "voice_selection_params" not in params
    assert "audio_config" not in params


def test_start_session_rime_tts_preserves_wire_aliases() -> None:
    agent = full_agent_with_tts(RimeTTS(key="rime-key", speaker="speaker", model_id="mist"))

    call = start_session(agent)
    properties = dump_wire(call["properties"])
    params = properties["tts"]["params"]

    assert params["modelId"] == "mist"
    assert "model_id" not in params


def test_start_session_murf_tts_preserves_wire_aliases() -> None:
    agent = full_agent_with_tts(MurfTTS(key="murf-key", voice_id="Ariana"))

    call = start_session(agent)
    properties = dump_wire(call["properties"])
    params = properties["tts"]["params"]

    assert params["voiceId"] == "Ariana"
    assert "voice_id" not in params


@pytest.mark.asyncio
async def test_async_start_session_google_tts_preserves_wire_aliases() -> None:
    agent = full_agent_with_tts(
        GoogleTTS(
            key="{}",
            voice_name="en-US-JennyNeural",
            language_code="en-US",
            sample_rate_hertz=24000,
        )
    )

    call = await start_async_session(agent)
    properties = dump_wire(call["properties"])
    params = properties["tts"]["params"]

    assert params["VoiceSelectionParams"]["name"] == "en-US-JennyNeural"
    assert params["VoiceSelectionParams"]["language_code"] == "en-US"
    assert params["AudioConfig"]["sample_rate_hertz"] == 24000
    assert "voice_selection_params" not in params
    assert "audio_config" not in params


def test_start_session_managed_minimax_tts_keeps_partial_preset_config() -> None:
    agent = (
        Agent(name="support")
        .with_llm(OpenAI(model="gpt-4o-mini"))
        .with_tts(MiniMaxTTS(model="speech_2_8_turbo", voice_id="English_captivating_female1"))
    )

    call = start_session(agent)
    properties = dump_wire(call["properties"])

    assert "minimax_speech_2_8_turbo" in (call["preset"] or "")
    assert properties["tts"]["vendor"] == "minimax"
    assert properties["tts"]["params"] == {
        "voice_setting": {"voice_id": "English_captivating_female1"},
    }


# ---------------------------------------------------------------------------
# BYOK Vendor Coverage Matrix — MLLM vendors
# ---------------------------------------------------------------------------


def test_byok_openai_realtime_mllm_params() -> None:
    agent = Agent(name="t").with_mllm(
        OpenAIRealtime(api_key="realtime-key", model="gpt-4o-realtime-preview", voice="coral")
    )
    props = build_properties(agent)
    assert props["mllm"]["vendor"] == "openai"
    assert props["mllm"]["api_key"] == "realtime-key"
    assert props["mllm"]["params"]["model"] == "gpt-4o-realtime-preview"
    assert props["mllm"]["params"]["voice"] == "coral"


def test_byok_gemini_live_mllm_params() -> None:
    agent = Agent(name="t").with_mllm(
        GeminiLive(api_key="gemini-key", model="gemini-live-2.5-flash")
    )
    props = build_properties(agent)
    assert props["mllm"]["vendor"] == "gemini"
    assert props["mllm"]["api_key"] == "gemini-key"
    assert props["mllm"]["params"]["model"] == "gemini-live-2.5-flash"


def test_byok_vertex_ai_mllm_params() -> None:
    agent = Agent(name="t").with_mllm(
        VertexAI(
            project_id="my-project",
            location="us-central1",
            adc_credentials_string="{}",
            model="gemini-live-2.5-flash",
        )
    )
    props = build_properties(agent)
    assert props["mllm"]["vendor"] == "vertexai"
    assert props["mllm"]["project_id"] == "my-project"
    assert props["mllm"]["location"] == "us-central1"
    assert props["mllm"]["adc_credentials_string"] == "{}"
    assert props["mllm"]["params"]["model"] == "gemini-live-2.5-flash"


def test_byok_xai_grok_mllm_params() -> None:
    agent = Agent(name="t").with_mllm(XaiGrok(api_key="xai-key"))
    props = build_properties(agent)
    assert props["mllm"]["vendor"] == "xai"
    assert props["mllm"]["api_key"] == "xai-key"


# ===========================================================================
# Preset Coverage Matrix
# ===========================================================================


def test_preset_deepgram_nova_2_inferred() -> None:
    tts = MiniMaxTTS(model="speech_2_8_turbo", voice_id="voice")
    preset, properties = resolve_session_presets(None, {"asr": DeepgramSTT(model="nova-2", language="en").to_config(), "tts": tts.to_config()})
    assert preset is not None and "deepgram_nova_2" in preset


def test_preset_deepgram_nova_3_inferred() -> None:
    tts = MiniMaxTTS(model="speech_2_8_turbo", voice_id="voice")
    preset, properties = resolve_session_presets(None, {"asr": DeepgramSTT(model="nova-3", language="en").to_config(), "tts": tts.to_config()})
    assert preset is not None and "deepgram_nova_3" in preset


def test_preset_openai_gpt_4o_mini_inferred() -> None:
    tts = MiniMaxTTS(model="speech_2_8_turbo", voice_id="voice")
    preset, properties = resolve_session_presets(None, {"llm": OpenAI(model="gpt-4o-mini").to_config(), "tts": tts.to_config()})
    assert preset is not None and "openai_gpt_4o_mini" in preset


def test_preset_openai_tts_1_inferred() -> None:
    preset, properties = resolve_session_presets(None, {"tts": OpenAITTS(voice="alloy").to_config()})
    assert preset == "openai_tts_1"
    assert properties["tts"]["vendor"] == "openai"


def test_preset_minimax_speech_2_8_turbo_inferred() -> None:
    preset, properties = resolve_session_presets(None, {"tts": MiniMaxTTS(model="speech_2_8_turbo", voice_id="voice").to_config()})
    assert preset == "minimax_speech_2_8_turbo"


def test_preset_minimax_speech_2_6_turbo_inferred() -> None:
    preset, properties = resolve_session_presets(None, {"tts": MiniMaxTTS(model="speech-2.6-turbo", voice_id="voice").to_config()})
    assert preset == "minimax_speech_2_6_turbo"


def test_explicit_minimax_preset_strips_internal_hint() -> None:
    """Explicit MiniMax TTS preset must not leak _minimax_preset_model to the wire."""
    # When the caller supplies the preset explicitly, inference is skipped but the
    # internal _minimax_preset_model hint set by MiniMaxTTS.to_config() must still
    # be removed before the POST body is sent.
    tts_config = MiniMaxTTS(model="speech_2_8_turbo", voice_id="voice").to_config()
    assert "_minimax_preset_model" in tts_config  # confirm the hint is set pre-strip

    _, properties = resolve_session_presets("minimax_speech_2_8_turbo", {"tts": tts_config})
    assert "_minimax_preset_model" not in properties["tts"]
