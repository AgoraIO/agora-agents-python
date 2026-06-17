import pytest

from agora_agent import AmazonTTS, CartesiaTTS, DeepgramTTS, ElevenLabsTTS, FishAudioTTS, GoogleTTS, HumeAITTS, MicrosoftTTS, MiniMaxTTS, MurfTTS, OpenAITTS, RimeTTS, SarvamTTS
from agora_agent.agents.types.start_agents_request_properties import StartAgentsRequestProperties
from agora_agent.core.jsonable_encoder import jsonable_encoder
from agora_agent.core.pydantic_utilities import parse_obj_as


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

    assert MiniMaxTTS(key="minimax-key", group_id="group", model="speech-02-turbo", voice_id="voice", url="wss://api-uw.minimax.io/ws/v1/t2a_v2").to_config()["params"] == {
        "model": "speech-02-turbo",
        "key": "minimax-key",
        "group_id": "group",
        "voice_setting": {"voice_id": "voice"},
        "url": "wss://api-uw.minimax.io/ws/v1/t2a_v2",
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

    with pytest.raises(Exception, match="MiniMaxTTS requires key unless using a supported Agora-managed model"):
        MiniMaxTTS(model="unsupported-model")


def test_tts_wire_serialization_applies_fern_aliases() -> None:
    """Verify alias-sensitive TTS params keep the exact provider wire keys."""
    _BASE = dict(channel="ch", token="tok", agent_rtc_uid="1", remote_rtc_uids=["100"])

    google_config = GoogleTTS(
        key="{}", voice_name="en-US-JennyNeural", language_code="en-US", sample_rate_hertz=24000
    ).to_config()
    assert "VoiceSelectionParams" in google_config["params"]
    google_wire = jsonable_encoder(parse_obj_as(StartAgentsRequestProperties, {**_BASE, "tts": google_config}))
    google_params = google_wire["tts"]["params"]
    assert "VoiceSelectionParams" in google_params, f"wire missing VoiceSelectionParams, got: {list(google_params)}"
    assert "voice_selection_params" not in google_params
    assert "AudioConfig" in google_params
    assert "audio_config" not in google_params

    rime_config = RimeTTS(key="rime-key", speaker="speaker", model_id="mist").to_config()
    assert "modelId" in rime_config["params"]
    rime_wire = jsonable_encoder(parse_obj_as(StartAgentsRequestProperties, {**_BASE, "tts": rime_config}))
    rime_params = rime_wire["tts"]["params"]
    assert "modelId" in rime_params, f"wire missing modelId, got: {list(rime_params)}"
    assert "model_id" not in rime_params

    murf_config = MurfTTS(key="murf-key", voice_id="Ariana").to_config()
    assert "voiceId" in murf_config["params"]
    murf_wire = jsonable_encoder(parse_obj_as(StartAgentsRequestProperties, {**_BASE, "tts": murf_config}))
    murf_params = murf_wire["tts"]["params"]
    assert "voiceId" in murf_params, f"wire missing voiceId, got: {list(murf_params)}"
    assert murf_params["voiceId"] == "Ariana"
