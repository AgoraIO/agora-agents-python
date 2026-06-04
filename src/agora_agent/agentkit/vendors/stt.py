from typing import Any, Dict, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing_extensions import Literal

from .base import BaseSTT

TurnDetectionLanguage = Literal[
    "ar-EG",
    "ar-JO",
    "ar-SA",
    "ar-AE",
    "bn-IN",
    "zh-CN",
    "zh-HK",
    "zh-TW",
    "nl-NL",
    "en-IN",
    "en-US",
    "fil-PH",
    "fr-FR",
    "de-DE",
    "gu-IN",
    "he-IL",
    "hi-IN",
    "id-ID",
    "it-IT",
    "ja-JP",
    "kn-IN",
    "ko-KR",
    "ms-MY",
    "fa-IR",
    "pt-PT",
    "ru-RU",
    "es-ES",
    "ta-IN",
    "te-IN",
    "th-TH",
    "tr-TR",
    "vi-VN",
]

TURN_DETECTION_LANGUAGE_VALUES: Tuple[TurnDetectionLanguage, ...] = (
    "ar-EG",
    "ar-JO",
    "ar-SA",
    "ar-AE",
    "bn-IN",
    "zh-CN",
    "zh-HK",
    "zh-TW",
    "nl-NL",
    "en-IN",
    "en-US",
    "fil-PH",
    "fr-FR",
    "de-DE",
    "gu-IN",
    "he-IL",
    "hi-IN",
    "id-ID",
    "it-IT",
    "ja-JP",
    "kn-IN",
    "ko-KR",
    "ms-MY",
    "fa-IR",
    "pt-PT",
    "ru-RU",
    "es-ES",
    "ta-IN",
    "te-IN",
    "th-TH",
    "tr-TR",
    "vi-VN",
)
_TURN_DETECTION_LANGUAGES = set(TURN_DETECTION_LANGUAGE_VALUES)
_DEEPGRAM_MANAGED_MODELS = {"nova-2", "nova-3"}


def _turn_detection_language(language: Optional[str]) -> Optional[TurnDetectionLanguage]:
    if language in _TURN_DETECTION_LANGUAGES:
        return language  # type: ignore[return-value]
    return None


class SpeechmaticsSTTOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Speechmatics API key")
    language: str = Field(..., description="Language code (e.g., en, es, fr)")
    model: Optional[str] = Field(default=None, description="Model name")
    uri: Optional[str] = Field(default=None, description="Speechmatics streaming WebSocket URL")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)

class SpeechmaticsSTT(BaseSTT):
    def __init__(self, **kwargs: Any):
        self.options = SpeechmaticsSTTOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.options.additional_params or {})
        params.update({
            "api_key": self.options.api_key,
            "language": self.options.language,
        })
        if self.options.model is not None:
            params["model"] = self.options.model
        if self.options.uri is not None:
            params["uri"] = self.options.uri

        config: Dict[str, Any] = {
            "vendor": "speechmatics",
            "params": params,
        }
        turn_detection_language = _turn_detection_language(self.options.language)
        if turn_detection_language is not None:
            config["language"] = turn_detection_language
        return config


class DeepgramSTTOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: Optional[str] = Field(default=None, description="Deepgram API key")
    model: Optional[str] = Field(default=None, description="Model (e.g., nova-2, enhanced, base)")
    language: Optional[str] = Field(default=None, description="Language code (e.g., en-US)")
    smart_format: Optional[bool] = Field(default=None, description="Enable smart formatting")
    punctuation: Optional[bool] = Field(default=None, description="Enable punctuation")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)

    @model_validator(mode="after")
    def _validate_managed_model(self) -> "DeepgramSTTOptions":
        if self.api_key is None and (self.model is None or self.model.strip().lower() not in _DEEPGRAM_MANAGED_MODELS):
            raise ValueError("DeepgramSTT requires api_key unless using a supported Agora-managed model")
        return self

class DeepgramSTT(BaseSTT):
    def __init__(self, **kwargs: Any):
        self.options = DeepgramSTTOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.options.additional_params or {})

        if self.options.api_key is not None:
            params["key"] = self.options.api_key
        if self.options.model is not None:
            params["model"] = self.options.model
        if self.options.language is not None:
            params["language"] = self.options.language
        if self.options.smart_format is not None:
            params["smart_format"] = self.options.smart_format
        if self.options.punctuation is not None:
            params["punctuation"] = self.options.punctuation
        config: Dict[str, Any] = {
            "vendor": "deepgram",
            "params": params,
        }
        turn_detection_language = _turn_detection_language(self.options.language)
        if turn_detection_language is not None:
            config["language"] = turn_detection_language
        return config


class MicrosoftSTTOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(..., description="Azure subscription key")
    region: str = Field(..., description="Azure region (e.g., eastus)")
    language: str = Field(..., description="Language code (e.g., en-US)")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)

class MicrosoftSTT(BaseSTT):
    def __init__(self, **kwargs: Any):
        self.options = MicrosoftSTTOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.options.additional_params or {})
        params.update({
            "key": self.options.key,
            "region": self.options.region,
        })
        if self.options.language is not None:
            params["language"] = self.options.language

        config: Dict[str, Any] = {
            "vendor": "microsoft",
            "params": params,
        }
        turn_detection_language = _turn_detection_language(self.options.language)
        if turn_detection_language is not None:
            config["language"] = turn_detection_language
        return config


class OpenAISTTOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="OpenAI API key")
    model: Optional[str] = Field(default=None, description="Model (default: whisper-1)")
    language: Optional[str] = Field(default=None, description="Language code")
    prompt: Optional[str] = Field(default=None, description="Prompt that guides OpenAI transcription")
    input_audio_transcription: Optional[Dict[str, Any]] = Field(default=None, description="OpenAI transcription settings")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)

class OpenAISTT(BaseSTT):
    def __init__(self, **kwargs: Any):
        self.options = OpenAISTTOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.options.additional_params or {})
        params["api_key"] = self.options.api_key

        transcription = {"model": "whisper-1", **(self.options.input_audio_transcription or {})}
        if self.options.model is not None:
            transcription["model"] = self.options.model
        if self.options.prompt is not None:
            transcription["prompt"] = self.options.prompt
        if self.options.language is not None:
            transcription["language"] = self.options.language
        params["input_audio_transcription"] = transcription

        config: Dict[str, Any] = {
            "vendor": "openai",
            "params": params,
        }
        turn_detection_language = _turn_detection_language(self.options.language)
        if turn_detection_language is not None:
            config["language"] = turn_detection_language
        return config


class GoogleSTTOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: str = Field(..., description="Google Cloud project ID")
    location: str = Field(..., description="Google Cloud region")
    adc_credentials_string: str = Field(..., description="Google service account credentials JSON string")
    language: str = Field(..., description="Language code (e.g., en-US)")
    model: Optional[str] = Field(default=None, description="Recognition model")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)

class GoogleSTT(BaseSTT):
    def __init__(self, **kwargs: Any):
        self.options = GoogleSTTOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.options.additional_params or {})
        params.update({
            "project_id": self.options.project_id,
            "location": self.options.location,
            "adc_credentials_string": self.options.adc_credentials_string,
        })

        if self.options.language is not None:
            params["language"] = self.options.language
        if self.options.model is not None:
            params["model"] = self.options.model

        config: Dict[str, Any] = {
            "vendor": "google",
            "params": params,
        }
        turn_detection_language = _turn_detection_language(self.options.language)
        if turn_detection_language is not None:
            config["language"] = turn_detection_language
        return config


class AmazonSTTOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_key: str = Field(..., description="AWS Access Key ID")
    secret_key: str = Field(..., description="AWS Secret Access Key")
    region: str = Field(..., description="AWS region (e.g., us-east-1)")
    language: str = Field(..., description="Language code")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)

class AmazonSTT(BaseSTT):
    def __init__(self, **kwargs: Any):
        self.options = AmazonSTTOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.options.additional_params or {})
        params.update({
            "access_key_id": self.options.access_key,
            "secret_access_key": self.options.secret_key,
            "region": self.options.region,
        })
        if self.options.language is not None:
            params["language_code"] = self.options.language

        config: Dict[str, Any] = {
            "vendor": "amazon",
            "params": params,
        }
        turn_detection_language = _turn_detection_language(self.options.language)
        if turn_detection_language is not None:
            config["language"] = turn_detection_language
        return config


class AssemblyAISTTOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="AssemblyAI API key")
    language: str = Field(..., description="Language code")
    uri: Optional[str] = Field(default=None, description="AssemblyAI streaming WebSocket URL")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)

class AssemblyAISTT(BaseSTT):
    def __init__(self, **kwargs: Any):
        self.options = AssemblyAISTTOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.options.additional_params or {})
        params["api_key"] = self.options.api_key
        if self.options.language is not None:
            params["language"] = self.options.language
        if self.options.uri is not None:
            params["uri"] = self.options.uri

        config: Dict[str, Any] = {
            "vendor": "assemblyai",
            "params": params,
        }
        turn_detection_language = _turn_detection_language(self.options.language)
        if turn_detection_language is not None:
            config["language"] = turn_detection_language
        return config


class AresSTTOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    language: Optional[TurnDetectionLanguage] = Field(default=None, description="Language code")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)

class AresSTT(BaseSTT):
    def __init__(self, **kwargs: Any):
        self.options = AresSTTOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        config: Dict[str, Any] = {"vendor": "ares"}
        if self.options.language is not None:
            config["language"] = self.options.language
        if self.options.additional_params:
            config["params"] = self.options.additional_params
        return config


class SarvamSTTOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Sarvam API key")
    language: str = Field(..., description="Language code (e.g., en, hi, ta)")
    model: Optional[str] = Field(default=None, description="Model name")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)

class SarvamSTT(BaseSTT):
    def __init__(self, **kwargs: Any):
        self.options = SarvamSTTOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.options.additional_params or {})
        params.update({
            "api_key": self.options.api_key,
            "language": self.options.language,
        })
        if self.options.model is not None:
            params["model"] = self.options.model

        config: Dict[str, Any] = {
            "vendor": "sarvam",
            "params": params,
        }
        turn_detection_language = _turn_detection_language(self.options.language)
        if turn_detection_language is not None:
            config["language"] = turn_detection_language
        return config
