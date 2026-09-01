import warnings
from typing import Any, Dict, List, Optional

from .base import BaseSTT
from pydantic import BaseModel, ConfigDict, Field, model_validator

_DEEPGRAM_MANAGED_MODELS = {"nova-2", "nova-3"}


class SpeechmaticsSTTOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: Optional[str] = Field(default=None, description="Speechmatics API key")
    api_key: Optional[str] = Field(
        default=None,
        description="Deprecated alias for key; normalized to the REST API key field",
        deprecated="Use key instead.",
    )
    language: str = Field(..., description="Language code (e.g., en, es, fr)")
    model: Optional[str] = Field(default=None, description="Model name")
    uri: Optional[str] = Field(default=None, description="Speechmatics streaming WebSocket URL")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)

    @model_validator(mode="before")
    @classmethod
    def _warn_deprecated_api_key(cls, values: Any) -> Any:
        if isinstance(values, dict) and "api_key" in values:
            warnings.warn(
                "SpeechmaticsSTT.api_key is deprecated; use key instead.",
                DeprecationWarning,
                stacklevel=2,
            )
        return values

    @model_validator(mode="after")
    def _validate_key(self) -> "SpeechmaticsSTTOptions":
        if self.key is None and self.__dict__.get("api_key") is None:
            raise ValueError("SpeechmaticsSTT requires key")
        return self

class SpeechmaticsSTT(SpeechmaticsSTTOptions, BaseSTT):
    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        params.pop("api_key", None)
        params.update({
            "key": self.key if self.key is not None else self.__dict__.get("api_key"),
            "language": self.language,
        })
        if self.model is not None:
            params["model"] = self.model
        if self.uri is not None:
            params["uri"] = self.uri

        config: Dict[str, Any] = {
            "vendor": "speechmatics",
            "params": params,
        }
        return config


class DeepgramSTTOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: Optional[str] = Field(default=None, description="Deepgram API key")
    model: Optional[str] = Field(default=None, description="Model (e.g., nova-2, enhanced, base)")
    language: Optional[str] = Field(default=None, description="Language code (e.g., en-US)")
    keyterm: Optional[str] = Field(default=None, description="Boost specialized terms and brands for Deepgram")
    smart_format: Optional[bool] = Field(default=None, description="Enable smart formatting")
    punctuation: Optional[bool] = Field(default=None, description="Enable punctuation")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)

    @model_validator(mode="after")
    def _validate_managed_model(self) -> "DeepgramSTTOptions":
        if self.api_key is None and (self.model is None or self.model.strip().lower() not in _DEEPGRAM_MANAGED_MODELS):
            raise ValueError("DeepgramSTT requires api_key unless using a supported Agora-managed model")
        return self


class DeepgramSTT(DeepgramSTTOptions, BaseSTT):
    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})

        if self.api_key is not None:
            params["key"] = self.api_key
        if self.model is not None:
            params["model"] = self.model
        if self.language is not None:
            params["language"] = self.language
        if self.smart_format is not None:
            params["smart_format"] = self.smart_format
        if self.punctuation is not None:
            params["punctuation"] = self.punctuation
        if self.keyterm is not None:
            params["keyterm"] = self.keyterm
        config: Dict[str, Any] = {
            "vendor": "deepgram",
            "params": params,
        }
        return config


class MicrosoftSTTOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(..., description="Azure subscription key")
    region: str = Field(..., description="Azure region (e.g., eastus)")
    language: str = Field(..., description="Language code (e.g., en-US)")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)


class MicrosoftSTT(MicrosoftSTTOptions, BaseSTT):
    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        params.update({
            "key": self.key,
            "region": self.region,
        })
        if self.language is not None:
            params["language"] = self.language

        config: Dict[str, Any] = {
            "vendor": "microsoft",
            "params": params,
        }
        return config


class OpenAISTTOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="OpenAI API key")
    model: Optional[str] = Field(default=None, description="Model (default: whisper-1)")
    language: Optional[str] = Field(default=None, description="Language code")
    prompt: Optional[str] = Field(default=None, description="Prompt that guides OpenAI transcription")
    input_audio_transcription: Optional[Dict[str, Any]] = Field(default=None, description="OpenAI transcription settings")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)


class OpenAISTT(OpenAISTTOptions, BaseSTT):
    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        params["api_key"] = self.api_key

        transcription: Dict[str, Any] = {"model": "gpt-4o-mini-transcribe"}
        transcription.update(self.input_audio_transcription or {})
        if self.model is not None:
            transcription["model"] = self.model
        if self.prompt is not None:
            transcription["prompt"] = self.prompt
        if self.language is not None:
            transcription["language"] = self.language
        if not transcription.get("model"):
            raise ValueError("OpenAISTT: input_audio_transcription.model is required")
        if not transcription.get("prompt"):
            raise ValueError("OpenAISTT: input_audio_transcription.prompt is required")
        if not transcription.get("language"):
            raise ValueError("OpenAISTT: input_audio_transcription.language is required")
        params["input_audio_transcription"] = transcription

        config: Dict[str, Any] = {
            "vendor": "openai",
            "params": params,
        }
        return config


class GoogleSTTOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: str = Field(..., description="Google Cloud project ID")
    location: str = Field(..., description="Google Cloud region")
    adc_credentials_string: str = Field(..., description="Google service account credentials JSON string")
    language: str = Field(..., description="Language code (e.g., en-US)")
    model: Optional[str] = Field(default=None, description="Recognition model")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)


class GoogleSTT(GoogleSTTOptions, BaseSTT):
    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        params.update({
            "project_id": self.project_id,
            "location": self.location,
            "adc_credentials_string": self.adc_credentials_string,
        })

        if self.language is not None:
            params["language"] = self.language
        if self.model is not None:
            params["model"] = self.model

        config: Dict[str, Any] = {
            "vendor": "google",
            "params": params,
        }
        return config


class GeminiSTTOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Google Gemini API key")
    model: str = Field(..., description="Google Gemini transcription model")
    language: Optional[str] = Field(default=None, description="Language code for speech recognition")
    word_timestamp: Optional[bool] = Field(
        default=None,
        description="Include word-level timestamps in transcription results",
    )
    sample_rate: Optional[int] = Field(default=None, description="Audio sample rate in Hz")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)


class GeminiSTT(GeminiSTTOptions, BaseSTT):
    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        params.update(
            {
                "api_key": self.api_key,
                "model": self.model,
            }
        )
        if self.sample_rate is not None:
            params["sample_rate"] = self.sample_rate
        if self.language is not None:
            params["language"] = self.language
        if self.word_timestamp is not None:
            params["word_timestamp"] = self.word_timestamp

        return {
            "vendor": "gemini",
            "params": params,
        }


class AmazonSTTOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_key: str = Field(..., description="AWS Access Key ID")
    secret_key: str = Field(..., description="AWS Secret Access Key")
    region: str = Field(..., description="AWS region (e.g., us-east-1)")
    language: str = Field(..., description="Language code")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)


class AmazonSTT(AmazonSTTOptions, BaseSTT):
    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        params.update({
            "access_key_id": self.access_key,
            "secret_access_key": self.secret_key,
            "region": self.region,
        })
        if self.language is not None:
            params["language_code"] = self.language

        config: Dict[str, Any] = {
            "vendor": "amazon",
            "params": params,
        }
        return config


class AssemblyAISTTOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="AssemblyAI API key")
    language: str = Field(..., description="Language code")
    ws_url: Optional[str] = Field(default=None, description="AssemblyAI streaming WebSocket URL")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)


class AssemblyAISTT(AssemblyAISTTOptions, BaseSTT):
    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        params["api_key"] = self.api_key
        if self.language is not None:
            params["language"] = self.language
        if self.ws_url is not None:
            params["ws_url"] = self.ws_url

        config: Dict[str, Any] = {
            "vendor": "assemblyai",
            "params": params,
        }
        return config


class AresSTTOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    keywords: Optional[List[str]] = Field(default=None, description="Hotwords that improve ASR accuracy")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)


class AresSTT(AresSTTOptions, BaseSTT):
    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        config: Dict[str, Any] = {"vendor": "ares"}
        if self.keywords is not None:
            config["keywords"] = self.keywords
        if params:
            config["params"] = params
        return config


class SarvamSTTOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Sarvam API key")
    language: str = Field(..., description="Language code (e.g., en, hi, ta)")
    model: Optional[str] = Field(default=None, description="Model name")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)


class SarvamSTT(SarvamSTTOptions, BaseSTT):
    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        params.update({
            "api_key": self.api_key,
            "language": self.language,
        })
        if self.model is not None:
            params["model"] = self.model

        config: Dict[str, Any] = {
            "vendor": "sarvam",
            "params": params,
        }
        return config


class XaiSTTOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="xAI API key")
    base_url: Optional[str] = Field(default=None, description="WebSocket endpoint URL for the xAI streaming STT API")
    sample_rate: Optional[int] = Field(default=None, description="Audio sample rate in Hz")
    language: Optional[str] = Field(default=None, description="Language code for speech recognition")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)


class XaiSTT(XaiSTTOptions, BaseSTT):
    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        params["api_key"] = self.api_key
        if self.base_url is not None:
            params["base_url"] = self.base_url
        if self.sample_rate is not None:
            params["sample_rate"] = self.sample_rate
        if self.language is not None:
            params["language"] = self.language

        config: Dict[str, Any] = {
            "vendor": "xai",
            "params": params,
        }
        return config
