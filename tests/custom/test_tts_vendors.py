import json

import httpx
import pytest

from agora_agent import (
    Agent,
    Agora,
    AmazonTTS,
    Area,
    CartesiaTTS,
    CredentialMode,
    DeepgramSTT,
    DeepgramTTS,
    ElevenLabsTTS,
    FishAudioTTS,
    GoogleTTS,
    GradiumTTS,
    HumeAITTS,
    MicrosoftTTS,
    MiniMaxTTS,
    MistralTTS,
    MurfTTS,
    OpenAI,
    OpenAITTS,
    RimeTTS,
    SarvamTTS,
    TypecastTTS,
)


def test_tts_vendor_params_match_generated_core_shapes() -> None:
    assert MicrosoftTTS(key="ms-key", region="eastus", voice_name="en-US-JennyNeural").to_config()["params"] == {
        "key": "ms-key",
        "region": "eastus",
        "voice_name": "en-US-JennyNeural",
    }

    assert AmazonTTS(access_key="access", secret_key="secret", region="us-east-1", voice_id="Joanna", engine="neural").to_config()["params"] == {
        "aws_access_key_id": "access",
        "aws_secret_access_key": "secret",
        "region_name": "us-east-1",
        "voice": "Joanna",
        "engine": "neural",
    }

    assert GoogleTTS(key="{}", voice_name="en-US-JennyNeural", language_code="en-US", sample_rate_hertz=24000).to_config()["params"] == {
        "credentials": "{}",
        "VoiceSelectionParams": {"name": "en-US-JennyNeural", "language_code": "en-US"},
        "AudioConfig": {"sample_rate_hertz": 24000},
    }

    assert CartesiaTTS(api_key="cartesia-key", voice_id="voice", model_id="sonic-2", sample_rate=24000).to_config()["params"] == {
        "api_key": "cartesia-key",
        "model_id": "sonic-2",
        "voice": {"mode": "id", "id": "voice"},
        "output_format": {"container": "raw", "sample_rate": 24000},
    }

    assert RimeTTS(key="rime-key", speaker="speaker", model_id="mist").to_config()["params"] == {
        "api_key": "rime-key",
        "speaker": "speaker",
        "modelId": "mist",
    }

    assert FishAudioTTS(key="fish-key", reference_id="ref", backend="speech-1.5").to_config()["params"] == {
        "api_key": "fish-key",
        "reference_id": "ref",
        "backend": "speech-1.5",
    }

    assert ElevenLabsTTS(key="eleven-key", model_id="eleven_flash_v2_5", voice_id="voice", base_url="wss://api.elevenlabs.io/v1").to_config()["params"] == {
        "key": "eleven-key",
        "base_url": "wss://api.elevenlabs.io/v1",
        "model_id": "eleven_flash_v2_5",
        "voice_id": "voice",
    }

    assert DeepgramTTS(api_key="deepgram-key", model="aura-2-thalia-en", base_url="wss://api.deepgram.com/v1/speak", sample_rate=24000, additional_params={"encoding": "linear16"}).to_config()["params"] == {
        "api_key": "deepgram-key",
        "model": "aura-2-thalia-en",
        "base_url": "wss://api.deepgram.com/v1/speak",
        "sample_rate": 24000,
        "encoding": "linear16",
    }

    assert GradiumTTS(
        api_key="gradium-key",
        url="wss://api.gradium.ai/api/speech/tts",
        model_name="default",
        voice_id="voice",
        sample_rate=16000,
        additional_params={"api_key": "ignored-key", "custom_gain": 0.5},
    ).to_config()["params"] == {
        "api_key": "gradium-key",
        "url": "wss://api.gradium.ai/api/speech/tts",
        "model_name": "default",
        "voice_id": "voice",
        "sample_rate": 16000,
        "custom_gain": 0.5,
    }

    assert MistralTTS(
        api_key="mistral-key",
        model="voxtral-mini-tts-2603",
        voice="voice",
        additional_params={"api_key": "ignored-key", "speed": 1.1},
    ).to_config()["params"] == {
        "api_key": "mistral-key",
        "model": "voxtral-mini-tts-2603",
        "voice": "voice",
        "speed": 1.1,
    }

    assert OpenAITTS(api_key="openai-key", voice="coral", model="gpt-4o-mini-tts", base_url="https://api.openai.com/v1", instructions="speak clearly").to_config()["params"] == {
        "voice": "coral",
        "api_key": "openai-key",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini-tts",
        "instructions": "speak clearly",
    }

    assert OpenAITTS(voice="coral").to_config()["params"] == {
        "voice": "coral",
    }

    assert HumeAITTS(key="hume-key", voice_id="voice", provider="CUSTOM_VOICE").to_config()["params"] == {
        "key": "hume-key",
        "voice_id": "voice",
        "provider": "CUSTOM_VOICE",
    }

    assert MiniMaxTTS(key="minimax-key", group_id="group", model="speech-02-turbo", voice_id="voice").to_config()["params"] == {
        "model": "speech-02-turbo",
        "key": "minimax-key",
        "group_id": "group",
        "voice_setting": {"voice_id": "voice"},
    }

    assert MiniMaxTTS(
        key="minimax-key",
        group_id="group",
        model="speech-01-turbo",
        voice_id="female-shaonv",
        speed=1,
        vol=1,
        pitch=0,
        emotion="happy",
        latex_read=True,
        english_normalization=True,
        sample_rate=16000,
        pronunciation_dict={"tone": ["example/(ex1)(am2)(ple0)", "message/(mes1)(sage4)"]},
        language_boost="auto",
    ).to_config()["params"] == {
        "model": "speech-01-turbo",
        "key": "minimax-key",
        "group_id": "group",
        "voice_setting": {
            "voice_id": "female-shaonv",
            "speed": 1,
            "vol": 1,
            "pitch": 0,
            "emotion": "happy",
            "latex_read": True,
            "english_normalization": True,
        },
        "audio_setting": {"sample_rate": 16000},
        "pronunciation_dict": {"tone": ["example/(ex1)(am2)(ple0)", "message/(mes1)(sage4)"]},
        "language_boost": "auto",
    }

    assert SarvamTTS(key="sarvam-key", speaker="anushka", target_language_code="en-IN", sample_rate=24000).to_config()["params"] == {
        "api_subscription_key": "sarvam-key",
        "speaker": "anushka",
        "target_language_code": "en-IN",
        "sample_rate": 24000,
    }

    assert MurfTTS(
        key="murf-key",
        voice_id="Ariana",
        base_url="wss://murf.example/ws",
        locale="en-US",
        rate=0,
        pitch=0,
        model="FALCON",
        sample_rate=24000,
    ).to_config()["params"] == {
        "api_key": "murf-key",
        "base_url": "wss://murf.example/ws",
        "voiceId": "Ariana",
        "locale": "en-US",
        "rate": 0,
        "pitch": 0,
        "model": "FALCON",
        "sample_rate": 24000,
    }

    assert MurfTTS(key="murf-key").to_config()["params"] == {
        "api_key": "murf-key",
    }


def test_tts_managed_mode_validation_matches_core_shapes() -> None:
    with pytest.raises(Exception, match="OpenAITTS requires api_key"):
        OpenAITTS(voice="coral", model="tts-1-hd")

    with pytest.raises(Exception, match="MiniMaxTTS requires key unless using a supported Agora-managed model|MiniMaxTTS requires exactly one of voice_id or timber_weights"):
        MiniMaxTTS(model="unsupported-model")

    with pytest.raises(Exception, match="MiniMaxTTS requires exactly one of voice_id or timber_weights"):
        MiniMaxTTS(key="minimax-key", group_id="group", model="speech-01-turbo")

    with pytest.raises(Exception, match="MiniMaxTTS requires exactly one of voice_id or timber_weights"):
        MiniMaxTTS(
            key="minimax-key",
            group_id="group",
            model="speech-01-turbo",
            voice_id="voice",
            timber_weights=[{"voice_id": "voice-2", "weight": 1}],
        )


def test_new_global_tts_optional_fields_and_skip_patterns() -> None:
    assert GradiumTTS(api_key="gradium-key", skip_patterns=[1, 2]).to_config() == {
        "vendor": "gradium",
        "params": {"api_key": "gradium-key"},
        "skip_patterns": [1, 2],
    }
    assert MistralTTS(api_key="mistral-key", skip_patterns=[3]).to_config() == {
        "vendor": "mistral",
        "params": {"api_key": "mistral-key"},
        "skip_patterns": [3],
    }

    assert GradiumTTS(api_key="gradium-key", sample_rate=16000).resolved_sample_rate == 16000
    assert MistralTTS(api_key="mistral-key").resolved_sample_rate is None


@pytest.mark.parametrize("tts_class", [GradiumTTS, MistralTTS])
def test_new_global_tts_requires_api_key(tts_class) -> None:
    with pytest.raises(Exception, match="api_key"):
        tts_class()


def test_rime_tts_managed_credential_mode_params() -> None:
    config = RimeTTS(
        credential_mode=CredentialMode.MANAGED,
        base_url="wss://users.rime.ai/ws",
        model_id="mist",
    ).to_config()
    assert config == {
        "vendor": "rime",
        "credential_mode": "managed",
        "params": {
            "modelId": "mist",
            "base_url": "wss://users.rime.ai/ws",
        },
    }


@pytest.mark.parametrize("credential_mode", [None, CredentialMode.BYOK])
def test_rime_tts_byok_credential_mode_params(credential_mode) -> None:
    config = RimeTTS(
        credential_mode=credential_mode,
        key="rime-key",
        speaker="speaker",
        model_id="mist",
    ).to_config()
    expected = {
        "modelId": "mist",
        "api_key": "rime-key",
        "speaker": "speaker",
    }
    assert config["params"] == expected
    if credential_mode is None:
        assert "credential_mode" not in config
    else:
        assert config["credential_mode"] == credential_mode


@pytest.mark.parametrize(
    ("kwargs", "missing"),
    [
        ({"model_id": "mist"}, "base_url"),
        ({"base_url": "wss://users.rime.ai/ws"}, "model_id"),
        ({}, "base_url, model_id"),
    ],
)
def test_rime_tts_managed_mode_requires_base_url_and_model_id(kwargs: dict, missing: str) -> None:
    with pytest.raises(Exception, match=rf"RimeTTS requires {missing} for credential_mode='managed'"):
        RimeTTS(credential_mode=CredentialMode.MANAGED, **kwargs)


@pytest.mark.parametrize("credential_mode", [None, CredentialMode.BYOK])
@pytest.mark.parametrize(
    ("kwargs", "missing"),
    [
        ({"speaker": "speaker", "model_id": "mist"}, "key"),
        ({"key": "rime-key", "model_id": "mist"}, "speaker"),
        ({"key": "rime-key", "speaker": "speaker"}, "model_id"),
    ],
)
def test_rime_tts_byok_mode_requires_key_speaker_and_model_id(
    credential_mode,
    kwargs: dict,
    missing: str,
) -> None:
    with pytest.raises(Exception, match=rf"RimeTTS requires {missing}"):
        RimeTTS(credential_mode=credential_mode, **kwargs)


def test_rime_tts_rejects_unknown_credential_mode() -> None:
    with pytest.raises(Exception, match="credential_mode"):
        RimeTTS(credential_mode="unknown", base_url="wss://users.rime.ai/ws", model_id="mist")  # type: ignore[arg-type]


def _capture_start_request(tts) -> dict:
    requests = []

    def handle_request(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"agent_id": "agent-id"})

    with httpx.Client(transport=httpx.MockTransport(handle_request)) as httpx_client:
        client = Agora(
            area=Area.US,
            app_id="0" * 32,
            app_certificate="1" * 32,
            customer_id="customer-id",
            customer_secret="customer-secret",
            httpx_client=httpx_client,
        )
        agent = (
            Agent(client)
            .with_stt(DeepgramSTT(api_key="deepgram-key", model="nova-3", language="en"))
            .with_llm(
                OpenAI(
                    api_key="openai-key",
                    base_url="https://api.openai.com/v1/chat/completions",
                    model="gpt-4o-mini",
                )
            )
            .with_tts(tts)
        )
        agent_id = agent.create_session(
            channel="ch",
            token="tok",
            agent_uid="1",
            remote_uids=["100"],
            name="alias-test",
        ).start()

    assert agent_id == "agent-id"
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].url.path == f"/api/conversational-ai-agent/v2/projects/{'0' * 32}/join"
    return json.loads(requests[0].content)["properties"]["tts"]


@pytest.mark.parametrize(
    ("tts", "expected_tts"),
    [
        pytest.param(
            TypecastTTS(api_key="typecast-key", voice_id="typecast-voice", model="nova-3"),
            {
                "vendor": "typecast",
                "params": {
                    "api_key": "typecast-key",
                    "voice_id": "typecast-voice",
                    "model": "nova-3",
                },
            },
            id="typecast-keeps-voice-id",
        ),
        pytest.param(
            ElevenLabsTTS(
                key="eleven-key",
                model_id="eleven_flash_v2_5",
                voice_id="eleven-voice",
                base_url="wss://api.elevenlabs.io/v1",
            ),
            {
                "vendor": "elevenlabs",
                "params": {
                    "key": "eleven-key",
                    "base_url": "wss://api.elevenlabs.io/v1",
                    "model_id": "eleven_flash_v2_5",
                    "voice_id": "eleven-voice",
                },
            },
            id="elevenlabs-keeps-model-id-and-voice-id",
        ),
        pytest.param(
            CartesiaTTS(api_key="cartesia-key", voice_id="cartesia-voice", model_id="sonic-2"),
            {
                "vendor": "cartesia",
                "params": {
                    "api_key": "cartesia-key",
                    "model_id": "sonic-2",
                    "voice": {"mode": "id", "id": "cartesia-voice"},
                },
            },
            id="cartesia-keeps-model-id",
        ),
        pytest.param(
            GradiumTTS(
                api_key="gradium-key",
                model_name="default",
                voice_id="gradium-voice",
                sample_rate=16000,
                additional_params={"custom_gain": 0.5},
            ),
            {
                "vendor": "gradium",
                "params": {
                    "api_key": "gradium-key",
                    "model_name": "default",
                    "voice_id": "gradium-voice",
                    "sample_rate": 16000,
                    "custom_gain": 0.5,
                },
            },
            id="gradium-keeps-voice-id",
        ),
        pytest.param(
            GoogleTTS(
                key="{}",
                voice_name="en-US-JennyNeural",
                language_code="en-US",
                sample_rate_hertz=24000,
            ),
            {
                "vendor": "google",
                "params": {
                    "credentials": "{}",
                    "VoiceSelectionParams": {
                        "name": "en-US-JennyNeural",
                        "language_code": "en-US",
                    },
                    "AudioConfig": {"sample_rate_hertz": 24000},
                },
            },
            id="google-keeps-pascal-case-aliases",
        ),
        pytest.param(
            RimeTTS(key="rime-key", speaker="speaker", model_id="mist"),
            {
                "vendor": "rime",
                "params": {
                    "api_key": "rime-key",
                    "speaker": "speaker",
                    "modelId": "mist",
                },
            },
            id="rime-applies-model-id-alias",
        ),
        pytest.param(
            RimeTTS(
                credential_mode=CredentialMode.MANAGED,
                base_url="wss://users.rime.ai/ws",
                model_id="mist",
            ),
            {
                "vendor": "rime",
                "credential_mode": "managed",
                "params": {
                    "modelId": "mist",
                    "base_url": "wss://users.rime.ai/ws",
                },
            },
            id="managed-rime-applies-model-id-alias",
        ),
        pytest.param(
            MurfTTS(key="murf-key", voice_id="Ariana"),
            {
                "vendor": "murf",
                "params": {
                    "api_key": "murf-key",
                    "voiceId": "Ariana",
                },
            },
            id="murf-applies-voice-id-alias",
        ),
        pytest.param(
            MistralTTS(
                api_key="mistral-key",
                model="voxtral-mini-tts-2603",
                voice="voice",
                additional_params={"speed": 1.1},
            ),
            {
                "vendor": "mistral",
                "params": {
                    "api_key": "mistral-key",
                    "model": "voxtral-mini-tts-2603",
                    "voice": "voice",
                    "speed": 1.1,
                },
            },
            id="mistral-keeps-additional-params",
        ),
    ],
)
def test_tts_http_request_preserves_vendor_specific_wire_keys(tts, expected_tts: dict) -> None:
    assert _capture_start_request(tts) == expected_tts
