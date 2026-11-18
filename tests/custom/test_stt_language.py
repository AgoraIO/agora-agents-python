import pytest

from agora_agent import (
    Agent,
    Area,
    AmazonSTT,
    AssemblyAISTT,
    DeepgramSTT,
    ElevenLabsTTS,
    GoogleSTT,
    MicrosoftSTT,
    OpenAI,
    OpenAISTT,
    RtzrSTT,
    SarvamSTT,
    SpeechmaticsSTT,
    TurnDetectionConfig,
)
from test_helpers import test_client


def dump(value):
    if hasattr(value, "model_dump"):
        return value.model_dump(exclude_none=True)
    return value.dict(exclude_none=True)


def base_agent() -> Agent:
    return (
        Agent(test_client())
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
        Agent(test_client(), turn_detection=TurnDetectionConfig(language="fr-FR"))
        .with_llm(OpenAI(api_key="llm-key", model="gpt-4o-mini", base_url="https://api.openai.com/v1/chat/completions"))
        .with_tts(ElevenLabsTTS(key="tts-key", voice_id="voice", model_id="eleven_flash_v2_5", base_url="wss://api.elevenlabs.io/v1"))
        .with_stt(SpeechmaticsSTT(api_key="stt-key", language="en"))
    )

    assert props["turn_detection"]["language"] == "fr-FR"
    assert props["asr"]["language"] == "fr-FR"
    assert props["asr"]["params"]["language"] == "en"


def test_invalid_turn_detection_language_is_rejected() -> None:
    with pytest.raises(ValueError, match="Invalid turn_detection.language: xx"):
        properties(Agent(test_client(), turn_detection=TurnDetectionConfig(language="xx")))  # type: ignore[arg-type]


def test_default_turn_detection_language_is_sent_without_stt() -> None:
    props = properties(base_agent())

    assert props["asr"] == {"vendor": "ares", "language": "en-US"}
    assert props["turn_detection"] == {"language": "en-US"}


def test_default_stt_vendor_depends_on_client_area_when_stt_is_omitted() -> None:
    global_props = properties(base_agent())
    cn_props = properties(
        Agent(test_client(area=Area.CN))
        .with_llm(OpenAI(api_key="llm-key", model="gpt-4o-mini", base_url="https://api.openai.com/v1/chat/completions"))
        .with_tts(ElevenLabsTTS(key="tts-key", voice_id="voice", model_id="eleven_flash_v2_5", base_url="wss://api.elevenlabs.io/v1"))
    )

    assert global_props["asr"] == {"vendor": "ares", "language": "en-US"}
    assert cn_props["asr"] == {"vendor": "fengming", "language": "en-US"}


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
        "api_key": "dg-key",
        "language": "en",
    }

    # api_key uses the generated Deepgram ASR field name; keyterm passes through unchanged
    assert DeepgramSTT(api_key="dg-key", model="nova-3", language="en", keyterm="term").to_config()["params"] == {
        "api_key": "dg-key",
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

    assemblyai_config = AssemblyAISTT(api_key="assembly-key", language="en-US", ws_url="wss://example.test/ws").to_config()
    assert "language" not in assemblyai_config
    assert assemblyai_config["params"] == {
        "api_key": "assembly-key",
        "language": "en-US",
        "ws_url": "wss://example.test/ws",
    }

    assert MicrosoftSTT(key="ms-key", region="eastus", language="en-US").to_config()["params"] == {
        "key": "ms-key",
        "region": "eastus",
        "language": "en-US",
    }

    assert SpeechmaticsSTT(api_key="sm-key", language="en").to_config()["params"] == {
        "key": "sm-key",
        "language": "en",
    }

    assert SarvamSTT(api_key="sarvam-key", language="en-IN").to_config()["params"] == {
        "api_key": "sarvam-key",
        "language": "en-IN",
    }


def test_rtzr_stt_serializes_generated_params() -> None:
    assert RtzrSTT(
        client_id="client-id",
        client_secret="client-secret",
        api_base="https://rtzr.example.com",
        model_name="general",
        language="ko",
        sample_rate=16000,
        encoding="pcm_s16le",
        use_itn=True,
        use_disfluency_filter=False,
        use_profanity_filter=True,
        use_punctuation=True,
        keywords=["Agora"],
    ).to_config() == {
        "vendor": "rtzr",
        "params": {
            "client_id": "client-id",
            "client_secret": "client-secret",
            "api_base": "https://rtzr.example.com",
            "model_name": "general",
            "language": "ko",
            "sample_rate": 16000,
            "encoding": "pcm_s16le",
            "use_itn": True,
            "use_disfluency_filter": False,
            "use_profanity_filter": True,
            "use_punctuation": True,
            "keywords": ["Agora"],
        },
    }


def test_rtzr_stt_reaches_generated_request_properties() -> None:
    props = properties(
        base_agent().with_stt(RtzrSTT(client_id="client-id", client_secret="client-secret", language="ko"))
    )

    assert props["asr"] == {
        "vendor": "rtzr",
        "language": "en-US",
        "params": {
            "client_id": "client-id",
            "client_secret": "client-secret",
            "language": "ko",
        },
    }


def test_assemblyai_params_stay_nested_and_asr_language_comes_from_turn_detection() -> None:
    props = properties(
        Agent(test_client(), turn_detection=TurnDetectionConfig(language="fr-FR"))
        .with_llm(OpenAI(api_key="llm-key", model="gpt-4o-mini", base_url="https://api.openai.com/v1/chat/completions"))
        .with_tts(ElevenLabsTTS(key="tts-key", voice_id="voice", model_id="eleven_flash_v2_5", base_url="wss://api.elevenlabs.io/v1"))
        .with_stt(AssemblyAISTT(api_key="assembly-key", language="en-US", ws_url="wss://example.test/ws"))
    )

    assert props["asr"] == {
        "vendor": "assemblyai",
        "language": "fr-FR",
        "params": {
            "api_key": "assembly-key",
            "language": "en-US",
            "ws_url": "wss://example.test/ws",
        },
    }
    assert props["turn_detection"] == {"language": "fr-FR"}


def test_turn_detection_language_list_joins_into_asr_language_and_falls_back_to_vad() -> None:
    props = properties(base_agent().with_turn_detection({"language": ["en-US", "es-ES", "en-US"]}))

    assert props["asr"]["vendor"] == "ares"
    assert props["asr"]["language"] == "en-US,es-ES"
    assert props["turn_detection"]["language"] == "en-US,es-ES"
    assert props["turn_detection"]["config"]["end_of_speech"]["mode"] == "vad"


def test_turn_detection_language_list_keeps_caller_vad_config() -> None:
    props = properties(
        base_agent().with_turn_detection(
            {
                "language": ["en-US", "hi-IN"],
                "config": {
                    "speech_threshold": 0.5,
                    "end_of_speech": {"mode": "vad", "vad_config": {"silence_duration_ms": 640}},
                },
            }
        )
    )

    assert props["asr"]["language"] == "en-US,hi-IN"
    assert props["turn_detection"]["config"]["speech_threshold"] == 0.5
    assert props["turn_detection"]["config"]["end_of_speech"] == {
        "mode": "vad",
        "vad_config": {"silence_duration_ms": 640},
    }


def test_turn_detection_language_list_works_with_pydantic_model() -> None:
    config = TurnDetectionConfig(language=["en-US", "fr-FR"])  # type: ignore[call-arg]
    props = properties(base_agent().with_turn_detection(config))

    assert props["asr"]["language"] == "en-US,fr-FR"
    assert props["turn_detection"]["config"]["end_of_speech"]["mode"] == "vad"


def test_turn_detection_one_item_list_behaves_like_single_language() -> None:
    props = properties(base_agent().with_turn_detection({"language": ["ja-JP"]}))

    assert props["asr"]["language"] == "ja-JP"
    assert "config" not in props["turn_detection"]


def test_semantic_end_of_speech_allows_one_english_or_chinese_language() -> None:
    props = properties(
        base_agent().with_turn_detection({"language": "zh-CN", "config": {"end_of_speech": {"mode": "semantic"}}})
    )

    assert props["asr"]["language"] == "zh-CN"
    assert props["turn_detection"]["config"]["end_of_speech"]["mode"] == "semantic"


@pytest.mark.parametrize(
    "turn_detection, message",
    [
        (
            {"language": ["en-US", "zh-CN"], "config": {"end_of_speech": {"mode": "semantic"}}},
            "cannot be a list",
        ),
        ({"language": "fr-FR", "config": {"end_of_speech": {"mode": "semantic"}}}, "only English and Chinese"),
        ({"language": []}, "must not be an empty list"),
        ({"language": ["en-US", "xx-XX"]}, "Invalid turn_detection.language: xx-XX"),
    ],
)
def test_turn_detection_language_errors(turn_detection: dict, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        properties(base_agent().with_turn_detection(turn_detection))  # type: ignore[arg-type]


def test_mllm_turn_detection_language_list_is_joined() -> None:
    from agora_agent import OpenAIRealtime

    agent = Agent(test_client(), turn_detection={"language": ["en-US", "es-ES"]}).with_mllm(
        OpenAIRealtime(api_key="key", model="gpt-4o-realtime-preview")
    )
    props = properties(agent)

    assert props["turn_detection"]["language"] == "en-US,es-ES"
