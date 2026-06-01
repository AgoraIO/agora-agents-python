from agora_agent import (
    Agent,
    AmazonSTT,
    AssemblyAISTT,
    DeepgramSTT,
    ElevenLabsTTS,
    GoogleSTT,
    OpenAI,
    OpenAISTT,
    SpeechmaticsSTT,
)


def dump(value):
    if hasattr(value, "model_dump"):
        return value.model_dump(exclude_none=True)
    return value.dict(exclude_none=True)


def base_agent() -> Agent:
    return (
        Agent()
        .with_llm(OpenAI(api_key="llm-key", model="gpt-4o-mini"))
        .with_tts(ElevenLabsTTS(key="tts-key", voice_id="voice", model_id="eleven_flash_v2_5"))
    )


def properties(agent: Agent) -> dict:
    return dump(
        agent.to_properties(
            channel="channel",
            token="token",
            agent_uid="1001",
            remote_uids=["1002"],
        )
    )


def test_bcp47_stt_language_sets_asr_language_and_provider_param() -> None:
    props = properties(base_agent().with_stt(SpeechmaticsSTT(api_key="stt-key", language="en-US")))

    assert props["asr"]["vendor"] == "speechmatics"
    assert props["asr"]["language"] == "en-US"
    assert props["asr"]["params"]["language"] == "en-US"


def test_provider_language_defaults_interaction_language_when_not_supported_by_ares() -> None:
    props = properties(base_agent().with_stt(SpeechmaticsSTT(api_key="stt-key", language="en")))

    assert props["asr"]["vendor"] == "speechmatics"
    assert props["asr"]["language"] == "en-US"
    assert props["asr"]["params"]["language"] == "en"
    assert "turn_detection" not in props


def test_explicit_interaction_language_can_differ_from_provider_language() -> None:
    props = properties(
        base_agent()
        .with_interaction_language("fr-FR")
        .with_stt(SpeechmaticsSTT(api_key="stt-key", language="en"))
    )

    assert props["asr"]["language"] == "fr-FR"
    assert props["asr"]["params"]["language"] == "en"


def test_default_interaction_language_is_sent_without_stt() -> None:
    props = properties(base_agent())

    assert props["asr"] == {"language": "en-US"}


def test_stt_vendor_params_match_documented_shapes() -> None:
    assert DeepgramSTT(api_key="dg-key", language="en").to_config()["params"] == {
        "key": "dg-key",
        "language": "en",
    }

    assert OpenAISTT(api_key="openai-key", model="gpt-4o-mini-transcribe", language="en").to_config()["params"] == {
        "api_key": "openai-key",
        "input_audio_transcription": {
            "model": "gpt-4o-mini-transcribe",
            "language": "en",
        },
    }

    assert GoogleSTT(
        project_id="project",
        location="global",
        adc_credentials_string="{}",
        language="en-US",
        model="long",
    ).to_config()["params"] == {
        "project_id": "project",
        "location": "global",
        "adc_credentials_string": "{}",
        "language": "en-US",
        "model": "long",
    }

    assert AmazonSTT(access_key="access", secret_key="secret", region="us-east-1", language="en-US").to_config()["params"] == {
        "access_key_id": "access",
        "secret_access_key": "secret",
        "region": "us-east-1",
        "language_code": "en-US",
    }

    assert AssemblyAISTT(api_key="assembly-key", language="en-US", uri="wss://example.test/ws").to_config()["params"] == {
        "api_key": "assembly-key",
        "language": "en-US",
        "uri": "wss://example.test/ws",
    }
