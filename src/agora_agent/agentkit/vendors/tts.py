from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .base import BaseTTS, CartesiaSampleRate, ElevenLabsSampleRate, GoogleTTSSampleRate, MicrosoftSampleRate
from ..presets import MiniMaxPresetModels, OpenAITtsPresetModels

class ElevenLabsTTSOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(..., description="ElevenLabs API key")
    model_id: str = Field(..., description="Model ID (e.g., eleven_flash_v2_5)")
    voice_id: str = Field(..., description="Voice ID")
    base_url: str = Field(..., description="WebSocket base URL")
    sample_rate: Optional[ElevenLabsSampleRate] = Field(default=None, description="Sample rate in Hz")
    skip_patterns: Optional[List[int]] = Field(default=None)
    optimize_streaming_latency: Optional[int] = Field(default=None, ge=0, le=4)
    stability: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    similarity_boost: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    style: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    use_speaker_boost: Optional[bool] = Field(default=None)

class ElevenLabsTTS(BaseTTS):
    def __init__(self, **kwargs: Any):
        self.options = ElevenLabsTTSOptions(**kwargs)

    @property
    def sample_rate(self) -> Optional[int]:
        return self.options.sample_rate

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "key": self.options.key,
            "base_url": self.options.base_url,
            "model_id": self.options.model_id,
            "voice_id": self.options.voice_id,
        }

        if self.options.sample_rate is not None:
            params["sample_rate"] = self.options.sample_rate
        if self.options.optimize_streaming_latency is not None:
            params["optimize_streaming_latency"] = self.options.optimize_streaming_latency
        if self.options.stability is not None:
            params["stability"] = self.options.stability
        if self.options.similarity_boost is not None:
            params["similarity_boost"] = self.options.similarity_boost
        if self.options.style is not None:
            params["style"] = self.options.style
        if self.options.use_speaker_boost is not None:
            params["use_speaker_boost"] = self.options.use_speaker_boost

        result: Dict[str, Any] = {"vendor": "elevenlabs", "params": params}
        if self.options.skip_patterns is not None:
            result["skip_patterns"] = self.options.skip_patterns
        return result


class MicrosoftTTSOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(..., description="Azure subscription key")
    region: str = Field(..., description="Azure region (e.g., eastus)")
    voice_name: str = Field(..., description="Voice name")
    sample_rate: Optional[MicrosoftSampleRate] = Field(default=None, description="Sample rate in Hz")
    speed: Optional[float] = Field(default=None, description="Speaking rate multiplier")
    volume: Optional[float] = Field(default=None, description="Audio volume")
    skip_patterns: Optional[List[int]] = Field(default=None)

class MicrosoftTTS(BaseTTS):
    def __init__(self, **kwargs: Any):
        self.options = MicrosoftTTSOptions(**kwargs)

    @property
    def sample_rate(self) -> Optional[int]:
        return self.options.sample_rate

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "key": self.options.key,
            "region": self.options.region,
            "voice_name": self.options.voice_name,
        }

        if self.options.sample_rate is not None:
            params["sample_rate"] = self.options.sample_rate
        if self.options.speed is not None:
            params["speed"] = self.options.speed
        if self.options.volume is not None:
            params["volume"] = self.options.volume

        result: Dict[str, Any] = {"vendor": "microsoft", "params": params}
        if self.options.skip_patterns is not None:
            result["skip_patterns"] = self.options.skip_patterns
        return result


class OpenAITTSOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    voice: str = Field(..., description="Voice name (alloy, echo, fable, onyx, nova, shimmer)")
    model: Optional[str] = Field(default=None, description="Model name (tts-1, tts-1-hd)")
    base_url: Optional[str] = Field(default=None, description="Endpoint URL")
    instructions: Optional[str] = Field(default=None, description="Custom voice instructions")
    speed: Optional[float] = Field(default=None, description="Speech speed multiplier")
    skip_patterns: Optional[List[int]] = Field(default=None)

    @model_validator(mode="after")
    def _validate_byok_params(self) -> "OpenAITTSOptions":
        if self.api_key is not None:
            missing = [
                name
                for name, value in (
                    ("model", self.model),
                    ("base_url", self.base_url),
                )
                if value is None
            ]
            if missing:
                raise ValueError(f"OpenAITTS requires {', '.join(missing)} when api_key is set")
        else:
            if self.model is not None and self.model.strip().lower() not in OpenAITtsPresetModels:
                raise ValueError("OpenAITTS requires api_key unless using the Agora-managed tts-1 model")
            if self.base_url is not None:
                raise ValueError("OpenAITTS base_url is only valid when api_key is set")
        return self

class OpenAITTS(BaseTTS):
    def __init__(self, **kwargs: Any):
        self.options = OpenAITTSOptions(**kwargs)

    @property
    def sample_rate(self) -> Optional[int]:
        return 24000

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "voice": self.options.voice,
        }
        if self.options.api_key is not None:
            params["api_key"] = self.options.api_key
            params["base_url"] = self.options.base_url
            params["model"] = self.options.model
        elif self.options.model is not None:
            params["model"] = self.options.model

        if self.options.instructions is not None:
            params["instructions"] = self.options.instructions
        if self.options.speed is not None:
            params["speed"] = self.options.speed

        result: Dict[str, Any] = {"vendor": "openai", "params": params}
        if self.options.skip_patterns is not None:
            result["skip_patterns"] = self.options.skip_patterns
        return result


class CartesiaTTSOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Cartesia API key")
    voice_id: str = Field(..., description="Voice ID")
    model_id: str = Field(..., description="Model ID")
    base_url: Optional[str] = Field(default=None, description="WebSocket URL")
    language: Optional[str] = Field(default=None, description="Target language")
    sample_rate: Optional[CartesiaSampleRate] = Field(default=None, description="Sample rate in Hz")
    skip_patterns: Optional[List[int]] = Field(default=None)

class CartesiaTTS(BaseTTS):
    def __init__(self, **kwargs: Any):
        self.options = CartesiaTTSOptions(**kwargs)

    @property
    def sample_rate(self) -> Optional[int]:
        return self.options.sample_rate

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "api_key": self.options.api_key,
            "model_id": self.options.model_id,
            "voice": {"mode": "id", "id": self.options.voice_id},
        }

        if self.options.base_url is not None:
            params["base_url"] = self.options.base_url
        if self.options.sample_rate is not None:
            params["output_format"] = {"container": "raw", "sample_rate": self.options.sample_rate}
        if self.options.language is not None:
            params["language"] = self.options.language

        result: Dict[str, Any] = {"vendor": "cartesia", "params": params}
        if self.options.skip_patterns is not None:
            result["skip_patterns"] = self.options.skip_patterns
        return result


class GoogleTTSOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(..., description="Google Cloud service account credentials JSON string")
    voice_name: str = Field(..., description="Voice name")
    language_code: Optional[str] = Field(default=None, description="Language code (e.g., en-US)")
    sample_rate_hertz: Optional[GoogleTTSSampleRate] = Field(default=None, description="Sample rate in Hz")
    skip_patterns: Optional[List[int]] = Field(default=None)

class GoogleTTS(BaseTTS):
    def __init__(self, **kwargs: Any):
        self.options = GoogleTTSOptions(**kwargs)

    @property
    def sample_rate(self) -> Optional[int]:
        return self.options.sample_rate_hertz

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "credentials": self.options.key,
            "VoiceSelectionParams": {"name": self.options.voice_name},
        }

        if self.options.language_code is not None:
            params["VoiceSelectionParams"]["language_code"] = self.options.language_code
        if self.options.sample_rate_hertz is not None:
            params["AudioConfig"] = {"sample_rate_hertz": self.options.sample_rate_hertz}

        result: Dict[str, Any] = {"vendor": "google", "params": params}
        if self.options.skip_patterns is not None:
            result["skip_patterns"] = self.options.skip_patterns
        return result


class AmazonTTSOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_key: str = Field(..., description="AWS access key")
    secret_key: str = Field(..., description="AWS secret key")
    region: str = Field(..., description="AWS region (e.g., us-east-1)")
    voice_id: str = Field(..., description="Amazon Polly voice ID")
    engine: str = Field(..., description="Amazon Polly engine type")
    skip_patterns: Optional[List[int]] = Field(default=None)

class AmazonTTS(BaseTTS):
    def __init__(self, **kwargs: Any):
        self.options = AmazonTTSOptions(**kwargs)

    @property
    def sample_rate(self) -> Optional[int]:
        return None

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "aws_access_key_id": self.options.access_key,
            "aws_secret_access_key": self.options.secret_key,
            "region_name": self.options.region,
            "voice": self.options.voice_id,
            "engine": self.options.engine,
        }

        result: Dict[str, Any] = {"vendor": "amazon", "params": params}
        if self.options.skip_patterns is not None:
            result["skip_patterns"] = self.options.skip_patterns
        return result


class DeepgramTTSOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Deepgram API key")
    model: str = Field(..., description="Deepgram TTS model (e.g., 'aura-2-thalia-en')")
    base_url: Optional[str] = Field(default=None, description="WebSocket endpoint")
    sample_rate: Optional[int] = Field(default=None, description="Sample rate in Hz")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional Deepgram TTS parameters")
    skip_patterns: Optional[List[int]] = Field(default=None)

class DeepgramTTS(BaseTTS):
    def __init__(self, **kwargs: Any):
        self.options = DeepgramTTSOptions(**kwargs)

    @property
    def sample_rate(self) -> Optional[int]:
        return self.options.sample_rate

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.options.additional_params or {})
        params.update({
            "api_key": self.options.api_key,
            "model": self.options.model,
        })

        if self.options.base_url is not None:
            params["base_url"] = self.options.base_url
        if self.options.sample_rate is not None:
            params["sample_rate"] = self.options.sample_rate
        result: Dict[str, Any] = {"vendor": "deepgram", "params": params}
        if self.options.skip_patterns is not None:
            result["skip_patterns"] = self.options.skip_patterns
        return result


class HumeAITTSOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(..., description="Hume AI API key")
    config_id: Optional[str] = Field(default=None, description="Configuration ID")
    voice_id: str = Field(..., description="Hume AI voice ID")
    base_url: Optional[str] = Field(default=None, description="Base URL")
    provider: str = Field(..., description="Voice provider type")
    speed: Optional[float] = Field(default=None, description="Playback speed")
    trailing_silence: Optional[float] = Field(default=None, description="Trailing silence in seconds")
    skip_patterns: Optional[List[int]] = Field(default=None)

class HumeAITTS(BaseTTS):
    def __init__(self, **kwargs: Any):
        self.options = HumeAITTSOptions(**kwargs)

    @property
    def sample_rate(self) -> Optional[int]:
        return None

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "key": self.options.key,
            "voice_id": self.options.voice_id,
            "provider": self.options.provider,
        }

        if self.options.config_id is not None:
            params["config_id"] = self.options.config_id
        if self.options.base_url is not None:
            params["base_url"] = self.options.base_url
        if self.options.speed is not None:
            params["speed"] = self.options.speed
        if self.options.trailing_silence is not None:
            params["trailing_silence"] = self.options.trailing_silence

        result: Dict[str, Any] = {"vendor": "humeai", "params": params}
        if self.options.skip_patterns is not None:
            result["skip_patterns"] = self.options.skip_patterns
        return result


class RimeTTSOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(..., description="Rime API key")
    speaker: str = Field(..., description="Speaker ID")
    model_id: str = Field(..., description="Model ID")
    base_url: Optional[str] = Field(default=None, description="WebSocket URL")
    skip_patterns: Optional[List[int]] = Field(default=None)

class RimeTTS(BaseTTS):
    def __init__(self, **kwargs: Any):
        self.options = RimeTTSOptions(**kwargs)

    @property
    def sample_rate(self) -> Optional[int]:
        return None

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "api_key": self.options.key,
            "speaker": self.options.speaker,
            "modelId": self.options.model_id,
        }
        if self.options.base_url is not None:
            params["base_url"] = self.options.base_url

        result: Dict[str, Any] = {"vendor": "rime", "params": params}
        if self.options.skip_patterns is not None:
            result["skip_patterns"] = self.options.skip_patterns
        return result


class FishAudioTTSOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(..., description="Fish Audio API key")
    reference_id: str = Field(..., description="Reference ID")
    backend: str = Field(..., description="Backend")
    skip_patterns: Optional[List[int]] = Field(default=None)

class FishAudioTTS(BaseTTS):
    def __init__(self, **kwargs: Any):
        self.options = FishAudioTTSOptions(**kwargs)

    @property
    def sample_rate(self) -> Optional[int]:
        return None

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "api_key": self.options.key,
            "reference_id": self.options.reference_id,
            "backend": self.options.backend,
        }

        result: Dict[str, Any] = {"vendor": "fishaudio", "params": params}
        if self.options.skip_patterns is not None:
            result["skip_patterns"] = self.options.skip_patterns
        return result


class MiniMaxTTSOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: Optional[str] = Field(default=None, description="MiniMax API key")
    group_id: Optional[str] = Field(default=None, description="MiniMax group identifier")
    model: str = Field(..., description="TTS model (e.g., 'speech-02-turbo')")
    voice_id: Optional[str] = Field(default=None, description="Voice style identifier (e.g., 'English_captivating_female1')")
    url: Optional[str] = Field(default=None, description="WebSocket endpoint (e.g., 'wss://api-uw.minimax.io/ws/v1/t2a_v2')")
    skip_patterns: Optional[List[int]] = Field(default=None)

    @model_validator(mode="after")
    def _validate_byok_params(self) -> "MiniMaxTTSOptions":
        if self.key is not None:
            missing = [
                name
                for name, value in (
                    ("group_id", self.group_id),
                    ("voice_id", self.voice_id),
                    ("url", self.url),
                )
                if value is None
            ]
            if missing:
                raise ValueError(f"MiniMaxTTS requires {', '.join(missing)} when key is set")
        elif self.model.strip().lower() not in MiniMaxPresetModels:
            raise ValueError("MiniMaxTTS requires key unless using a supported Agora-managed model")
        return self

class MiniMaxTTS(BaseTTS):
    def __init__(self, **kwargs: Any):
        self.options = MiniMaxTTSOptions(**kwargs)

    @property
    def sample_rate(self) -> Optional[int]:
        return None

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {"model": self.options.model}
        if self.options.key is not None:
            params["key"] = self.options.key
        if self.options.group_id is not None:
            params["group_id"] = self.options.group_id
        if self.options.voice_id is not None:
            params["voice_setting"] = {"voice_id": self.options.voice_id}
        if self.options.url is not None:
            params["url"] = self.options.url

        result: Dict[str, Any] = {"vendor": "minimax", "params": params}
        if self.options.skip_patterns is not None:
            result["skip_patterns"] = self.options.skip_patterns
        return result


class SarvamTTSOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(..., description="Sarvam API subscription key")
    speaker: str = Field(..., description="Speaker/voice ID (e.g., 'anushka', 'abhilash', 'karun', 'hitesh', 'manisha', 'vidya', 'arya')")
    target_language_code: str = Field(..., description="Target language code (e.g., 'en-IN', 'hi-IN', 'ta-IN')")
    pitch: Optional[float] = Field(default=None, description="Pitch adjustment")
    pace: Optional[float] = Field(default=None, description="Speed of speech")
    loudness: Optional[float] = Field(default=None, description="Volume level")
    sample_rate: Optional[int] = Field(default=None, description="Audio sample rate in Hz")
    skip_patterns: Optional[List[int]] = Field(default=None)

class SarvamTTS(BaseTTS):
    def __init__(self, **kwargs: Any):
        self.options = SarvamTTSOptions(**kwargs)

    @property
    def sample_rate(self) -> Optional[int]:
        return None

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "api_subscription_key": self.options.key,
            "speaker": self.options.speaker,
            "target_language_code": self.options.target_language_code,
        }
        if self.options.pitch is not None:
            params["pitch"] = self.options.pitch
        if self.options.pace is not None:
            params["pace"] = self.options.pace
        if self.options.loudness is not None:
            params["loudness"] = self.options.loudness
        if self.options.sample_rate is not None:
            params["sample_rate"] = self.options.sample_rate

        result: Dict[str, Any] = {"vendor": "sarvam", "params": params}
        if self.options.skip_patterns is not None:
            result["skip_patterns"] = self.options.skip_patterns
        return result


class MurfTTSOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(..., description="Murf API key")
    voice_id: Optional[str] = Field(default=None, description="Voice ID (e.g., 'Ariana', 'Natalie', 'Ken')")
    base_url: Optional[str] = Field(default=None, description="WebSocket endpoint")
    locale: Optional[str] = Field(default=None, description="Voice locale")
    rate: Optional[float] = Field(default=None, description="Speech rate")
    pitch: Optional[float] = Field(default=None, description="Pitch adjustment")
    model: Optional[str] = Field(default=None, description="TTS model")
    sample_rate: Optional[int] = Field(default=None, description="Audio sample rate")
    skip_patterns: Optional[List[int]] = Field(default=None)

class MurfTTS(BaseTTS):
    def __init__(self, **kwargs: Any):
        self.options = MurfTTSOptions(**kwargs)

    @property
    def sample_rate(self) -> Optional[int]:
        return None

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {"api_key": self.options.key}

        if self.options.base_url is not None:
            params["base_url"] = self.options.base_url
        if self.options.voice_id is not None:
            params["voiceId"] = self.options.voice_id
        if self.options.locale is not None:
            params["locale"] = self.options.locale
        if self.options.rate is not None:
            params["rate"] = self.options.rate
        if self.options.pitch is not None:
            params["pitch"] = self.options.pitch
        if self.options.model is not None:
            params["model"] = self.options.model
        if self.options.sample_rate is not None:
            params["sample_rate"] = self.options.sample_rate

        result: Dict[str, Any] = {"vendor": "murf", "params": params}
        if self.options.skip_patterns is not None:
            result["skip_patterns"] = self.options.skip_patterns
        return result
