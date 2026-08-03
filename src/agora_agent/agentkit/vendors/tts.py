from typing import Any, Dict, List, Literal, Optional
from urllib.parse import urlsplit

from pydantic import ConfigDict, Field, field_validator, model_validator

from .base import BaseTTS, CartesiaSampleRate, ElevenLabsSampleRate, GoogleTTSSampleRate, MicrosoftSampleRate
from ..constants import CredentialMode
from ..presets import MiniMaxPresetModels, OpenAITtsPresetModels


class ElevenLabsTTS(BaseTTS):
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

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "key": self.key,
            "base_url": self.base_url,
            "model_id": self.model_id,
            "voice_id": self.voice_id,
        }

        if self.sample_rate is not None:
            params["sample_rate"] = self.sample_rate
        if self.optimize_streaming_latency is not None:
            params["optimize_streaming_latency"] = self.optimize_streaming_latency
        if self.stability is not None:
            params["stability"] = self.stability
        if self.similarity_boost is not None:
            params["similarity_boost"] = self.similarity_boost
        if self.style is not None:
            params["style"] = self.style
        if self.use_speaker_boost is not None:
            params["use_speaker_boost"] = self.use_speaker_boost

        result: Dict[str, Any] = {"vendor": "elevenlabs", "params": params}
        if self.skip_patterns is not None:
            result["skip_patterns"] = self.skip_patterns
        return result


class MicrosoftTTS(BaseTTS):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(..., description="Azure subscription key")
    region: str = Field(..., description="Azure region (e.g., eastus)")
    voice_name: str = Field(..., description="Voice name")
    sample_rate: Optional[MicrosoftSampleRate] = Field(default=None, description="Sample rate in Hz")
    speed: Optional[float] = Field(default=None, description="Speaking rate multiplier")
    volume: Optional[float] = Field(default=None, description="Audio volume")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional Microsoft TTS params")
    skip_patterns: Optional[List[int]] = Field(default=None)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        params.update({
                "key": self.key,
                "region": self.region,
                "voice_name": self.voice_name,
        })

        if self.sample_rate is not None:
            params["sample_rate"] = self.sample_rate
        if self.speed is not None:
            params["speed"] = self.speed
        if self.volume is not None:
            params["volume"] = self.volume

        result: Dict[str, Any] = {"vendor": "microsoft", "params": params}
        if self.skip_patterns is not None:
            result["skip_patterns"] = self.skip_patterns
        return result


class OpenAITTS(BaseTTS):
    model_config = ConfigDict(extra="forbid")

    api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    voice: str = Field(..., description="Voice name (alloy, echo, fable, onyx, nova, shimmer)")
    model: Optional[str] = Field(default=None, description="Model name (tts-1, tts-1-hd)")
    base_url: Optional[str] = Field(default=None, description="Endpoint URL")
    instructions: Optional[str] = Field(default=None, description="Custom voice instructions")
    speed: Optional[float] = Field(default=None, description="Speech speed multiplier")
    skip_patterns: Optional[List[int]] = Field(default=None)

    @model_validator(mode="after")
    def _validate_byok_params(self) -> "OpenAITTS":
        if self.api_key is not None:
            missing = [
                name
                for name, value in (
                    ("model", self.model),
                    ("base_url", self.base_url),
                )
                if not value
            ]
            if missing:
                raise ValueError(f"OpenAITTS requires {', '.join(missing)} when api_key is set")
        else:
            if self.model is not None and self.model.strip().lower() not in OpenAITtsPresetModels:
                raise ValueError("OpenAITTS requires api_key unless using the Agora-managed tts-1 model")
            if self.base_url is not None:
                raise ValueError("OpenAITTS base_url is only valid when api_key is set")
        return self

    @property
    def sample_rate(self) -> Optional[int]:
        return 24000

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "voice": self.voice,
        }
        if self.api_key is not None:
            params["api_key"] = self.api_key
            params["base_url"] = self.base_url
            params["model"] = self.model
        elif self.model is not None:
            params["model"] = self.model

        if self.instructions is not None:
            params["instructions"] = self.instructions
        if self.speed is not None:
            params["speed"] = self.speed

        result: Dict[str, Any] = {"vendor": "openai", "params": params}
        if self.skip_patterns is not None:
            result["skip_patterns"] = self.skip_patterns
        return result


class CartesiaTTS(BaseTTS):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Cartesia API key")
    voice_id: str = Field(..., description="Voice ID")
    model_id: str = Field(..., description="Model ID")
    base_url: Optional[str] = Field(default=None, description="WebSocket URL")
    language: Optional[str] = Field(default=None, description="Target language")
    sample_rate: Optional[CartesiaSampleRate] = Field(default=None, description="Sample rate in Hz")
    skip_patterns: Optional[List[int]] = Field(default=None)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "api_key": self.api_key,
            "model_id": self.model_id,
            "voice": {"mode": "id", "id": self.voice_id},
        }

        if self.base_url is not None:
            params["base_url"] = self.base_url
        if self.sample_rate is not None:
            params["output_format"] = {"container": "raw", "sample_rate": self.sample_rate}
        if self.language is not None:
            params["language"] = self.language

        result: Dict[str, Any] = {"vendor": "cartesia", "params": params}
        if self.skip_patterns is not None:
            result["skip_patterns"] = self.skip_patterns
        return result


class GoogleTTS(BaseTTS):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(..., description="Google Cloud service account credentials JSON string")
    voice_name: str = Field(..., description="Voice name")
    language_code: Optional[str] = Field(default=None, description="Language code (e.g., en-US)")
    sample_rate_hertz: Optional[GoogleTTSSampleRate] = Field(default=None, description="Sample rate in Hz")
    skip_patterns: Optional[List[int]] = Field(default=None)

    @property
    def sample_rate(self) -> Optional[int]:
        return self.sample_rate_hertz

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "credentials": self.key,
            "VoiceSelectionParams": {"name": self.voice_name},
        }

        if self.language_code is not None:
            params["VoiceSelectionParams"]["language_code"] = self.language_code
        if self.sample_rate_hertz is not None:
            params["AudioConfig"] = {"sample_rate_hertz": self.sample_rate_hertz}

        result: Dict[str, Any] = {"vendor": "google", "params": params}
        if self.skip_patterns is not None:
            result["skip_patterns"] = self.skip_patterns
        return result


class AmazonTTS(BaseTTS):
    model_config = ConfigDict(extra="forbid")

    access_key: str = Field(..., description="AWS access key")
    secret_key: str = Field(..., description="AWS secret key")
    region: str = Field(..., description="AWS region (e.g., us-east-1)")
    voice_id: str = Field(..., description="Amazon Polly voice ID")
    engine: str = Field(..., description="Amazon Polly engine type")
    skip_patterns: Optional[List[int]] = Field(default=None)

    @property
    def sample_rate(self) -> Optional[int]:
        return None

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "aws_access_key_id": self.access_key,
            "aws_secret_access_key": self.secret_key,
            "region_name": self.region,
            "voice": self.voice_id,
            "engine": self.engine,
        }

        result: Dict[str, Any] = {"vendor": "amazon", "params": params}
        if self.skip_patterns is not None:
            result["skip_patterns"] = self.skip_patterns
        return result


class DeepgramTTS(BaseTTS):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Deepgram API key")
    model: str = Field(..., description="Deepgram TTS model (e.g., 'aura-2-thalia-en')")
    base_url: Optional[str] = Field(default=None, description="WebSocket endpoint")
    sample_rate: Optional[int] = Field(default=None, description="Sample rate in Hz")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional Deepgram TTS parameters")
    skip_patterns: Optional[List[int]] = Field(default=None)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        params.update({
                "api_key": self.api_key,
                "model": self.model,
        })

        if self.base_url is not None:
            params["base_url"] = self.base_url
        if self.sample_rate is not None:
            params["sample_rate"] = self.sample_rate
        result: Dict[str, Any] = {"vendor": "deepgram", "params": params}
        if self.skip_patterns is not None:
            result["skip_patterns"] = self.skip_patterns
        return result


class GradiumTTS(BaseTTS):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Gradium API key")
    url: Optional[str] = Field(default=None, description="WebSocket endpoint for streaming TTS output")
    model_name: Optional[str] = Field(default=None, description="Gradium TTS model name")
    voice_id: Optional[str] = Field(default=None, description="Gradium voice identifier")
    sample_rate: Optional[int] = Field(default=None, description="Audio sample rate in Hz")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional Gradium TTS parameters")
    skip_patterns: Optional[List[int]] = Field(default=None)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        params["api_key"] = self.api_key
        if self.url is not None:
            params["url"] = self.url
        if self.model_name is not None:
            params["model_name"] = self.model_name
        if self.voice_id is not None:
            params["voice_id"] = self.voice_id
        if self.sample_rate is not None:
            params["sample_rate"] = self.sample_rate

        result: Dict[str, Any] = {"vendor": "gradium", "params": params}
        if self.skip_patterns is not None:
            result["skip_patterns"] = self.skip_patterns
        return result


class HumeAITTS(BaseTTS):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(..., description="Hume AI API key")
    config_id: Optional[str] = Field(default=None, description="Configuration ID")
    voice_id: str = Field(..., description="Hume AI voice ID")
    base_url: Optional[str] = Field(default=None, description="Base URL")
    provider: str = Field(..., description="Voice provider type")
    speed: Optional[float] = Field(default=None, description="Playback speed")
    trailing_silence: Optional[float] = Field(default=None, description="Trailing silence in seconds")
    skip_patterns: Optional[List[int]] = Field(default=None)

    @property
    def sample_rate(self) -> Optional[int]:
        return None

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "key": self.key,
            "voice_id": self.voice_id,
            "provider": self.provider,
        }

        if self.config_id is not None:
            params["config_id"] = self.config_id
        if self.base_url is not None:
            params["base_url"] = self.base_url
        if self.speed is not None:
            params["speed"] = self.speed
        if self.trailing_silence is not None:
            params["trailing_silence"] = self.trailing_silence

        result: Dict[str, Any] = {"vendor": "humeai", "params": params}
        if self.skip_patterns is not None:
            result["skip_patterns"] = self.skip_patterns
        return result


class RimeTTS(BaseTTS):
    model_config = ConfigDict(extra="forbid")

    key: Optional[str] = Field(default=None, description="Rime API key")
    speaker: Optional[str] = Field(default=None, description="Speaker ID")
    model_id: Optional[str] = Field(default=None, description="Model ID")
    base_url: Optional[str] = Field(default=None, description="WebSocket URL")
    credential_mode: Optional[Literal["managed", "byok"]] = Field(default=None, description="Credential mode")
    skip_patterns: Optional[List[int]] = Field(default=None)

    @model_validator(mode="after")
    def _validate_credential_mode(self) -> "RimeTTS":
        required: Dict[str, Optional[str]]
        if self.credential_mode == CredentialMode.MANAGED:
            required = {"base_url": self.base_url, "model_id": self.model_id}
            mode = "credential_mode='managed'"
        else:
            required = {"key": self.key, "speaker": self.speaker, "model_id": self.model_id}
            mode = "credential_mode='byok' or when credential_mode is omitted"

        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ValueError(f"RimeTTS requires {', '.join(missing)} for {mode}")
        return self

    @property
    def sample_rate(self) -> Optional[int]:
        return None

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {"modelId": self.model_id}
        if self.key is not None:
            params["api_key"] = self.key
        if self.speaker is not None:
            params["speaker"] = self.speaker
        if self.base_url is not None:
            params["base_url"] = self.base_url

        result: Dict[str, Any] = {"vendor": "rime", "params": params}
        if self.credential_mode is not None:
            result["credential_mode"] = self.credential_mode
        if self.skip_patterns is not None:
            result["skip_patterns"] = self.skip_patterns
        return result


class FishAudioTTS(BaseTTS):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(..., description="Fish Audio API key")
    reference_id: str = Field(..., description="Reference ID")
    backend: str = Field(..., description="Backend")
    skip_patterns: Optional[List[int]] = Field(default=None)

    @property
    def sample_rate(self) -> Optional[int]:
        return None

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "api_key": self.key,
            "reference_id": self.reference_id,
            "backend": self.backend,
        }

        result: Dict[str, Any] = {"vendor": "fishaudio", "params": params}
        if self.skip_patterns is not None:
            result["skip_patterns"] = self.skip_patterns
        return result


class MiniMaxTTS(BaseTTS):
    model_config = ConfigDict(extra="forbid")

    key: Optional[str] = Field(default=None, description="MiniMax API key")
    group_id: Optional[str] = Field(default=None, description="MiniMax group identifier")
    model: str = Field(..., description="TTS model (e.g., 'speech-02-turbo')")
    voice_id: Optional[str] = Field(default=None, description="Voice style identifier (e.g., 'English_captivating_female1')")
    speed: Optional[float] = Field(default=None, description="Speaking speed")
    vol: Optional[float] = Field(default=None, description="Volume gain")
    pitch: Optional[float] = Field(default=None, description="Pitch adjustment")
    emotion: Optional[str] = Field(default=None, description="Emotion style")
    latex_read: Optional[bool] = Field(default=None, description="Whether to read LaTeX expressions")
    english_normalization: Optional[bool] = Field(default=None, description="Whether to normalize English text")
    timber_weights: Optional[List[Dict[str, Any]]] = Field(default=None, description="Alternative timbre mix config")
    sample_rate: Optional[int] = Field(default=None, description="Output sample rate in Hz")
    pronunciation_dict: Optional[Dict[str, Any]] = Field(default=None, description="Pronunciation replacement dictionary")
    language_boost: Optional[str] = Field(default=None, description="Language boost strategy")
    url: Optional[str] = Field(default=None, description="Optional WebSocket endpoint override")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional MiniMax TTS params")
    skip_patterns: Optional[List[int]] = Field(default=None)

    @model_validator(mode="after")
    def _validate_byok_params(self) -> "MiniMaxTTS":
        if self.voice_id is not None and self.timber_weights is not None:
            raise ValueError("MiniMaxTTS requires exactly one of voice_id or timber_weights")
        if self.key is not None:
            missing = [
                name
                for name, value in (
                    ("group_id", self.group_id),
                    ("voice_id or timber_weights", self.voice_id if self.voice_id is not None else self.timber_weights),
                )
                if value is None
            ]
            if missing and not (len(missing) == 1 and missing[0] == "voice_id or timber_weights"):
                raise ValueError(f"MiniMaxTTS requires {', '.join(missing)} when key is set")
            if self.voice_id is None and self.timber_weights is None:
                raise ValueError("MiniMaxTTS requires exactly one of voice_id or timber_weights")
        else:
            if self.voice_id is None and self.timber_weights is None:
                raise ValueError("MiniMaxTTS requires exactly one of voice_id or timber_weights")
            if self.model.strip().lower() not in MiniMaxPresetModels:
                raise ValueError("MiniMaxTTS requires key unless using a supported Agora-managed model")
        return self

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        if self.key is not None:
            params["key"] = self.key
            params["group_id"] = self.group_id
            params["model"] = self.model
            if self.url is not None:
                params["url"] = self.url
        voice_setting: Dict[str, Any] = {}
        if self.voice_id is not None:
            voice_setting["voice_id"] = self.voice_id
        if self.speed is not None:
            voice_setting["speed"] = self.speed
        if self.vol is not None:
            voice_setting["vol"] = self.vol
        if self.pitch is not None:
            voice_setting["pitch"] = self.pitch
        if self.emotion is not None:
            voice_setting["emotion"] = self.emotion
        if self.latex_read is not None:
            voice_setting["latex_read"] = self.latex_read
        if self.english_normalization is not None:
            voice_setting["english_normalization"] = self.english_normalization
        if voice_setting:
            params["voice_setting"] = voice_setting
        if self.timber_weights is not None:
            params["timber_weights"] = self.timber_weights
        if self.sample_rate is not None:
            params["audio_setting"] = {"sample_rate": self.sample_rate}
        if self.pronunciation_dict is not None:
            params["pronunciation_dict"] = self.pronunciation_dict
        if self.language_boost is not None:
            params["language_boost"] = self.language_boost

        result: Dict[str, Any] = {"vendor": "minimax", "params": params}
        if self.key is None:
            # Preset path: model not in params; stored as top-level hint for preset
            # inference. Stripped by strip_inferred_preset_fields before the POST body.
            result["_minimax_preset_model"] = self.model
        if self.skip_patterns is not None:
            result["skip_patterns"] = self.skip_patterns
        return result


class MistralTTS(BaseTTS):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Mistral API key")
    model: Optional[str] = Field(default=None, description="Mistral TTS model name")
    voice: Optional[str] = Field(default=None, description="Mistral voice identifier")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional Mistral TTS parameters")
    skip_patterns: Optional[List[int]] = Field(default=None)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        params["api_key"] = self.api_key
        if self.model is not None:
            params["model"] = self.model
        if self.voice is not None:
            params["voice"] = self.voice

        result: Dict[str, Any] = {"vendor": "mistral", "params": params}
        if self.skip_patterns is not None:
            result["skip_patterns"] = self.skip_patterns
        return result


class TypecastTTS(BaseTTS):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Typecast API key")
    voice_id: str = Field(..., description="Typecast voice identifier")
    model: str = Field(..., description="Typecast TTS model name")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional Typecast TTS parameters")
    skip_patterns: Optional[List[int]] = Field(default=None)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        params.update(
            {
                "api_key": self.api_key,
                "voice_id": self.voice_id,
                "model": self.model,
            }
        )

        result: Dict[str, Any] = {"vendor": "typecast", "params": params}
        if self.skip_patterns is not None:
            result["skip_patterns"] = self.skip_patterns
        return result


class SarvamTTS(BaseTTS):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(..., description="Sarvam API subscription key")
    speaker: str = Field(..., description="Speaker/voice ID (e.g., 'anushka', 'abhilash', 'karun', 'hitesh', 'manisha', 'vidya', 'arya')")
    target_language_code: str = Field(..., description="Target language code (e.g., 'en-IN', 'hi-IN', 'ta-IN')")
    pitch: Optional[float] = Field(default=None, description="Pitch adjustment")
    pace: Optional[float] = Field(default=None, description="Speed of speech")
    loudness: Optional[float] = Field(default=None, description="Volume level")
    sample_rate: Optional[int] = Field(default=None, description="Audio sample rate in Hz")
    skip_patterns: Optional[List[int]] = Field(default=None)

    @property
    def resolved_sample_rate(self) -> Optional[int]:
        return None

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "api_subscription_key": self.key,
            "speaker": self.speaker,
            "target_language_code": self.target_language_code,
        }
        if self.pitch is not None:
            params["pitch"] = self.pitch
        if self.pace is not None:
            params["pace"] = self.pace
        if self.loudness is not None:
            params["loudness"] = self.loudness
        if self.sample_rate is not None:
            params["sample_rate"] = self.sample_rate

        result: Dict[str, Any] = {"vendor": "sarvam", "params": params}
        if self.skip_patterns is not None:
            result["skip_patterns"] = self.skip_patterns
        return result


class MurfTTS(BaseTTS):
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

    @property
    def resolved_sample_rate(self) -> Optional[int]:
        return None

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {"api_key": self.key}

        if self.base_url is not None:
            params["base_url"] = self.base_url
        if self.voice_id is not None:
            params["voiceId"] = self.voice_id
        if self.locale is not None:
            params["locale"] = self.locale
        if self.rate is not None:
            params["rate"] = self.rate
        if self.pitch is not None:
            params["pitch"] = self.pitch
        if self.model is not None:
            params["model"] = self.model
        if self.sample_rate is not None:
            params["sample_rate"] = self.sample_rate

        result: Dict[str, Any] = {"vendor": "murf", "params": params}
        if self.skip_patterns is not None:
            result["skip_patterns"] = self.skip_patterns
        return result


class GenericTTS(BaseTTS):
    model_config = ConfigDict(extra="forbid")

    url: str = Field(..., description="HTTP(S) endpoint of the generic TTS service")
    headers: Optional[Dict[str, str]] = Field(default=None, description="Custom request headers")
    model: Optional[str] = Field(default=None, description="TTS model name")
    voice: Optional[str] = Field(default=None, description="Voice name")
    api_key: Optional[str] = Field(default=None, description="API key for the generic TTS service")
    speed: Optional[float] = Field(default=None, description="Speech rate")
    sample_rate: Optional[int] = Field(default=None, description="Output audio sample rate in Hz")
    response_format: Optional[str] = Field(default=None, description="Output audio format")
    instruction: Optional[str] = Field(default=None, description="Additional voice style control instruction")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional generic TTS params")
    skip_patterns: Optional[List[int]] = Field(default=None)

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        parsed = urlsplit(value)
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
            raise ValueError("GenericTTS url must be a valid HTTP(S) endpoint")
        return value

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        if self.api_key is not None:
            params["api_key"] = self.api_key
        if self.model is not None:
            params["model"] = self.model
        if self.voice is not None:
            params["voice"] = self.voice
        if self.speed is not None:
            params["speed"] = self.speed
        if self.sample_rate is not None:
            params["sample_rate"] = self.sample_rate
        if self.response_format is not None:
            params["response_format"] = self.response_format
        if self.instruction is not None:
            params["instruction"] = self.instruction

        result: Dict[str, Any] = {
            "vendor": "generic_http",
            "url": self.url,
            "params": params,
        }
        if self.headers is not None:
            result["headers"] = self.headers
        if self.skip_patterns is not None:
            result["skip_patterns"] = self.skip_patterns
        return result


class XaiTTS(BaseTTS):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="xAI API key")
    language: str = Field(..., description="BCP-47 language code for speech synthesis")
    voice_id: Optional[str] = Field(default=None, description="xAI voice identifier")
    sample_rate: Optional[int] = Field(default=None, description="Audio sample rate in Hz")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional xAI TTS params")
    skip_patterns: Optional[List[int]] = Field(default=None)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        params["api_key"] = self.api_key
        params["language"] = self.language
        if self.voice_id is not None:
            params["voice_id"] = self.voice_id
        if self.sample_rate is not None:
            params["sample_rate"] = self.sample_rate

        result: Dict[str, Any] = {"vendor": "xai", "params": params}
        if self.skip_patterns is not None:
            result["skip_patterns"] = self.skip_patterns
        return result
