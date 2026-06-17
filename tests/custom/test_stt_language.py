import pytest

from agora_agent import (
    Agent,
    AmazonSTT,
    AssemblyAISTT,
    DeepgramSTT,
    ElevenLabsTTS,
    GoogleSTT,
    MicrosoftSTT,
    OpenAI,
    OpenAISTT,
    SarvamSTT,
    SpeechmaticsSTT,
    TurnDetectionConfig,
)


def dump(value):
    if hasattr(value, "model_dump"):
        return value.model_dump(exclude_none=True)
    return value.dict(exclude_none=True)


def base_agent() -> Agent:
    return (
        Agent()
        .with_llm(OpenAI(api_key="llm-key", model="gpt-4o-mini", base_url="https://api.openai.com/v1/chat/completions"))
        .with_tts(ElevenLabsTTS(key="tts-key", voice_id="voice", model_id="eleven_flash_v2_5", base_url="wss://api.elevenlabs.io/v1"))
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


def test_bcp47_stt_language_stays_in_asr_params_and_defaults_turn_detection() -> None:
    props = properties(base_agent().with_stt(SpeechmaticsSTT(api_key="stt-key", language="en")))

    assert props["asr"]["vendor"] == "speechmatics"
    assert props["asr"]["language"] == "en-US"
    assert props["turn_detection"]["language"] == "en-US"
    assert props["asr"]["params"]["language"] == "en"


def test_provider_language_does_not_set_turn_detection_language() -> None:
    props = properties(base_agent().with_stt(SpeechmaticsSTT(api_key="stt-key", language="en")))

    assert props["asr"]["vendor"] == "speechmatics"
    assert props["asr"]["language"] == "en-US"
    assert props["turn_detection"]["language"] == "en-US"
    assert props["asr"]["params"]["language"] == "en"


def test_turn_detection_language_can_differ_from_provider_language() -> None:
    props = properties(
        Agent(turn_detection=TurnDetectionConfig(language="fr-FR"))
        .with_llm(OpenAI(api_key="llm-key", model="gpt-4o-mini", base_url="https://api.openai.com/v1/chat/completions"))
        .with_tts(ElevenLabsTTS(key="tts-key", voice_id="voice", model_id="eleven_flash_v2_5", base_url="wss://api.elevenlabs.io/v1"))
        .with_stt(SpeechmaticsSTT(api_key="stt-key", language="en"))
    )

    assert props["turn_detection"]["language"] == "fr-FR"
    assert props["asr"]["language"] == "fr-FR"
    assert props["asr"]["params"]["language"] == "en"


def test_invalid_turn_detection_language_is_rejected() -> None:
    with pytest.raises(ValueError, match="Invalid turn_detection.language: xx"):
        properties(Agent(turn_detection=TurnDetectionConfig(language="xx")))  # type: ignore[arg-type]


def test_default_turn_detection_language_is_sent_without_stt() -> None:
    props = properties(base_agent())

    assert props["asr"] == {"vendor": "ares", "language": "en-US"}
    assert props["turn_detection"] == {"language": "en-US"}


def test_stt_vendor_params_match_documented_shapes() -> None:
    deepgram_managed = DeepgramSTT(model="nova-3", language="en-US").to_config()
    assert "language" not in deepgram_managed
    assert deepgram_managed["params"] == {
        "model": "nova-3",
        "language": "en-US",
    }

    with pytest.raises(Exception, match="api_key"):
        DeepgramSTT(model="enhanced")

    assert DeepgramSTT(api_key="dg-key", language="en").to_config()["params"] == {
        "key": "dg-key",
        "language": "en",
    }

    # api_key → wire key "key"; keyterm passes through unchanged
    assert DeepgramSTT(api_key="dg-key", model="nova-3", language="en", keyterm="term").to_config()["params"] == {
        "key": "dg-key",
        "model": "nova-3",
        "language": "en",
        "keyterm": "term",
    }

    assert OpenAISTT(
        api_key="openai-key",
        model="gpt-4o-mini-transcribe",
        language="en",
        prompt="Transcribe English speech",
    ).to_config()["params"] == {
        "api_key": "openai-key",
        "input_audio_transcription": {
            "model": "gpt-4o-mini-transcribe",
            "language": "en",
            "prompt": "Transcribe English speech",
        },
    }

    with pytest.raises(ValueError, match="prompt is required"):
        OpenAISTT(api_key="openai-key", language="en").to_config()

    with pytest.raises(ValueError, match="language is required"):
        OpenAISTT(api_key="openai-key", prompt="Transcribe speech").to_config()

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

    assemblyai_config = AssemblyAISTT(api_key="assembly-key", language="en-US", uri="wss://example.test/ws").to_config()
    assert "language" not in assemblyai_config
    assert assemblyai_config["params"] == {
        "api_key": "assembly-key",
        "language": "en-US",
        "uri": "wss://example.test/ws",
    }

    assert MicrosoftSTT(key="ms-key", region="eastus", language="en-US").to_config()["params"] == {
        "key": "ms-key",
        "region": "eastus",
        "language": "en-US",
    }

    assert SpeechmaticsSTT(api_key="sm-key", language="en").to_config()["params"] == {
        "api_key": "sm-key",
        "language": "en",
    }

    assert SarvamSTT(api_key="sarvam-key", language="en-IN").to_config()["params"] == {
        "api_key": "sarvam-key",
        "language": "en-IN",
    }


def test_assemblyai_params_stay_nested_and_asr_language_comes_from_turn_detection() -> None:
    props = properties(
        Agent(turn_detection=TurnDetectionConfig(language="fr-FR"))
        .with_llm(OpenAI(api_key="llm-key", model="gpt-4o-mini", base_url="https://api.openai.com/v1/chat/completions"))
        .with_tts(ElevenLabsTTS(key="tts-key", voice_id="voice", model_id="eleven_flash_v2_5", base_url="wss://api.elevenlabs.io/v1"))
        .with_stt(AssemblyAISTT(api_key="assembly-key", language="en-US", uri="wss://example.test/ws"))
    )

    assert props["asr"] == {
        "vendor": "assemblyai",
        "language": "fr-FR",
        "params": {
            "api_key": "assembly-key",
            "language": "en-US",
            "uri": "wss://example.test/ws",
        },
    }
    assert props["turn_detection"] == {"language": "fr-FR"}
