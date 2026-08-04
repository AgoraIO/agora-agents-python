from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import ConfigDict, Field, model_validator

from ...types.mllm_turn_detection import MllmTurnDetection
from .avatar import BaseAvatar
from .base import BaseLLM, BaseMLLM
from .llm import (
    _OPENAI_MANAGED_MODELS,
    LlmGreetingConfigs,
    _dump_optional_model,
    _ensure_mcp_transport,
)
from .stt import BaseSTT as _BaseSTTCompat
from .tts import BaseTTS as _BaseTTSCompat


class TencentSTT(_BaseSTTCompat):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(..., description="Tencent ASR secret key")
    app_id: str = Field(..., description="Tencent ASR app id")
    secret: str = Field(..., description="Tencent ASR secret")
    engine_model_type: str = Field(..., description="Tencent ASR engine model type")
    voice_id: str = Field(..., description="Tencent ASR voice id")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        params.update(
            {
                "key": self.key,
                "app_id": self.app_id,
                "secret": self.secret,
                "engine_model_type": self.engine_model_type,
                "voice_id": self.voice_id,
            }
        )
        return {"vendor": "tencent", "params": params}


class FengmingSTT(_BaseSTTCompat):
    model_config = ConfigDict(extra="forbid")

    keywords: Optional[List[str]] = Field(default=None, description="Hotwords that improve ASR accuracy")

    def to_config(self) -> Dict[str, Any]:
        config: Dict[str, Any] = {"vendor": "fengming"}
        if self.keywords is not None:
            config["params"] = {"keywords": self.keywords}
        return config


class XfyunSTT(_BaseSTTCompat):
    model_config = ConfigDict(extra="forbid")

    api_key: Optional[str] = Field(default=None, description="Xfyun ASR API key")
    app_id: Optional[str] = Field(default=None, description="Xfyun ASR app id")
    api_secret: Optional[str] = Field(default=None, description="Xfyun ASR API secret")
    language: Optional[str] = Field(default=None, description="Xfyun ASR language")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        if self.api_key is not None:
            params["api_key"] = self.api_key
        if self.app_id is not None:
            params["app_id"] = self.app_id
        if self.api_secret is not None:
            params["api_secret"] = self.api_secret
        if self.language is not None:
            params["language"] = self.language
        return {
            "vendor": "xfyun",
            "params": params,
        }


class XfyunBigModelSTT(_BaseSTTCompat):
    model_config = ConfigDict(extra="forbid")

    api_key: Optional[str] = Field(default=None, description="Xfyun BigModel ASR API key")
    app_id: Optional[str] = Field(default=None, description="Xfyun BigModel ASR app id")
    api_secret: Optional[str] = Field(default=None, description="Xfyun BigModel ASR API secret")
    language_name: Optional[str] = Field(default=None, description="Xfyun BigModel ASR language name")
    language: Optional[str] = Field(default=None, description="Xfyun BigModel ASR language")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        if self.api_key is not None:
            params["api_key"] = self.api_key
        if self.app_id is not None:
            params["app_id"] = self.app_id
        if self.api_secret is not None:
            params["api_secret"] = self.api_secret
        if self.language_name is not None:
            params["language_name"] = self.language_name
        if self.language is not None:
            params["language"] = self.language
        return {
            "vendor": "xfyun_bigmodel",
            "params": params,
        }


class XfyunDialectSTT(_BaseSTTCompat):
    model_config = ConfigDict(extra="forbid")

    app_id: Optional[str] = Field(default=None, description="Xfyun Dialect ASR app id")
    access_key_id: Optional[str] = Field(default=None, description="Xfyun Dialect ASR access key id")
    access_key_secret: Optional[str] = Field(default=None, description="Xfyun Dialect ASR access key secret")
    language: Optional[str] = Field(default=None, description="Xfyun Dialect ASR language")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        if self.app_id is not None:
            params["app_id"] = self.app_id
        if self.access_key_id is not None:
            params["access_key_id"] = self.access_key_id
        if self.access_key_secret is not None:
            params["access_key_secret"] = self.access_key_secret
        if self.language is not None:
            params["language"] = self.language
        return {
            "vendor": "xfyun_dialect",
            "params": params,
        }


class MicrosoftSTT(_BaseSTTCompat):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(..., description="Azure subscription key")
    region: str = Field(..., description="Azure region (e.g., eastus)")
    language: str = Field(..., description="Language code (e.g., zh-CN)")
    phrase_list: Optional[List[str]] = Field(default=None, description="Microsoft ASR phrase list")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        params.update({
            "key": self.key,
            "region": self.region,
            "language": self.language,
        })
        if self.phrase_list is not None:
            params["phrase_list"] = self.phrase_list
        return {
            "vendor": "microsoft",
            "params": params,
        }


class TencentTTS(_BaseTTSCompat):
    model_config = ConfigDict(extra="forbid")

    app_id: str = Field(..., description="Tencent TTS app id")
    secret_id: str = Field(..., description="Tencent TTS secret id")
    secret_key: str = Field(..., description="Tencent TTS secret key")
    voice_type: int = Field(..., description="Tencent TTS voice type")
    volume: Optional[int] = Field(default=None, description="Tencent TTS volume")
    speed: Optional[int] = Field(default=None, description="Tencent TTS speech speed")
    emotion_category: Optional[str] = Field(default=None, description="Tencent TTS emotion category")
    emotion_intensity: Optional[int] = Field(default=None, description="Tencent TTS emotion intensity")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional Tencent TTS params")
    skip_patterns: Optional[List[int]] = Field(default=None)

    @property
    def sample_rate(self) -> Optional[int]:
        audio_setting = (self.additional_params or {}).get("audio_setting")
        if isinstance(audio_setting, dict):
            sample_rate = audio_setting.get("sample_rate")
            if isinstance(sample_rate, int):
                return sample_rate
        return None

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        params.update(
            {
                "app_id": self.app_id,
                "secret_id": self.secret_id,
                "secret_key": self.secret_key,
                "voice_type": self.voice_type,
            }
        )
        if self.volume is not None:
            params["volume"] = self.volume
        if self.speed is not None:
            params["speed"] = self.speed
        if self.emotion_category is not None:
            params["emotion_category"] = self.emotion_category
        if self.emotion_intensity is not None:
            params["emotion_intensity"] = self.emotion_intensity

        result: Dict[str, Any] = {
            "vendor": "tencent",
            "params": params,
        }
        if self.skip_patterns is not None:
            result["skip_patterns"] = self.skip_patterns
        return result


class BytedanceTTS(_BaseTTSCompat):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(..., description="Bytedance TTS auth token")
    app_id: str = Field(..., description="Bytedance TTS app id")
    cluster: str = Field(..., description="Bytedance TTS cluster")
    voice_type: str = Field(..., description="Bytedance TTS voice type")
    speed_ratio: Optional[float] = Field(default=None, description="Bytedance TTS speed ratio")
    volume_ratio: Optional[float] = Field(default=None, description="Bytedance TTS volume ratio")
    pitch_ratio: Optional[float] = Field(default=None, description="Bytedance TTS pitch ratio")
    emotion: Optional[str] = Field(default=None, description="Bytedance TTS emotion")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional Bytedance TTS params")
    skip_patterns: Optional[List[int]] = Field(default=None)

    @property
    def sample_rate(self) -> Optional[int]:
        audio_setting = (self.additional_params or {}).get("audio_setting")
        if isinstance(audio_setting, dict):
            sample_rate = audio_setting.get("sample_rate")
            if isinstance(sample_rate, int):
                return sample_rate
        return None

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        params.update(
            {
                "token": self.token,
                "app_id": self.app_id,
                "cluster": self.cluster,
                "voice_type": self.voice_type,
            }
        )
        if self.speed_ratio is not None:
            params["speed_ratio"] = self.speed_ratio
        if self.volume_ratio is not None:
            params["volume_ratio"] = self.volume_ratio
        if self.pitch_ratio is not None:
            params["pitch_ratio"] = self.pitch_ratio
        if self.emotion is not None:
            params["emotion"] = self.emotion

        result: Dict[str, Any] = {
            "vendor": "bytedance",
            "params": params,
        }
        if self.skip_patterns is not None:
            result["skip_patterns"] = self.skip_patterns
        return result


class BytedanceDuplexTTS(_BaseTTSCompat):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(..., description="Bytedance Duplex TTS auth token")
    app_id: str = Field(..., description="Bytedance Duplex TTS app id")
    speaker: str = Field(..., description="Bytedance Duplex TTS speaker")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional Bytedance Duplex TTS params")
    skip_patterns: Optional[List[int]] = Field(default=None)

    @property
    def sample_rate(self) -> Optional[int]:
        audio_setting = (self.additional_params or {}).get("audio_setting")
        if isinstance(audio_setting, dict):
            sample_rate = audio_setting.get("sample_rate")
            if isinstance(sample_rate, int):
                return sample_rate
        return None

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        params.update(
            {
                "token": self.token,
                "app_id": self.app_id,
                "speaker": self.speaker,
            }
        )

        result: Dict[str, Any] = {
            "vendor": "bytedance_duplex",
            "params": params,
        }
        if self.skip_patterns is not None:
            result["skip_patterns"] = self.skip_patterns
        return result


class CosyVoiceTTS(_BaseTTSCompat):
    model_config = ConfigDict(extra="forbid")

    api_key: Optional[str] = Field(default=None, description="CosyVoice API key")
    model: Optional[str] = Field(default=None, description="CosyVoice model")
    sample_rate: Optional[int] = Field(default=None, description="Output sample rate in Hz")
    voice: Optional[str] = Field(default=None, description="CosyVoice voice")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="CosyVoice TTS params from REST doc")
    skip_patterns: Optional[List[int]] = Field(default=None)

    @property
    def resolved_sample_rate(self) -> Optional[int]:
        if self.sample_rate is not None:
            return self.sample_rate
        audio_setting = (self.additional_params or {}).get("audio_setting")
        if isinstance(audio_setting, dict):
            sample_rate = audio_setting.get("sample_rate")
            if isinstance(sample_rate, int):
                return sample_rate
        return None

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        if self.api_key is not None:
            params["api_key"] = self.api_key
        if self.model is not None:
            params["model"] = self.model
        if self.sample_rate is not None:
            params["sample_rate"] = self.sample_rate
        if self.voice is not None:
            params["voice"] = self.voice
        result: Dict[str, Any] = {
            "vendor": "cosyvoice",
            "params": params,
        }
        if self.skip_patterns is not None:
            result["skip_patterns"] = self.skip_patterns
        return result


class StepFunTTS(_BaseTTSCompat):
    model_config = ConfigDict(extra="forbid")

    api_key: Optional[str] = Field(default=None, description="StepFun TTS API key")
    model: Optional[str] = Field(default=None, description="StepFun TTS model")
    voice_id: Optional[str] = Field(default=None, description="StepFun TTS voice id")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="StepFun TTS params from REST doc")
    skip_patterns: Optional[List[int]] = Field(default=None)

    @property
    def sample_rate(self) -> Optional[int]:
        audio_setting = (self.additional_params or {}).get("audio_setting")
        if isinstance(audio_setting, dict):
            sample_rate = audio_setting.get("sample_rate")
            if isinstance(sample_rate, int):
                return sample_rate
        return None

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        if self.api_key is not None:
            params["api_key"] = self.api_key
        if self.model is not None:
            params["model"] = self.model
        if self.voice_id is not None:
            params["voice_id"] = self.voice_id
        result: Dict[str, Any] = {
            "vendor": "stepfun",
            "params": params,
        }
        if self.skip_patterns is not None:
            result["skip_patterns"] = self.skip_patterns
        return result


class MicrosoftTTS(_BaseTTSCompat):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(..., description="Azure subscription key")
    region: str = Field(..., description="Azure region (e.g., eastus)")
    voice_name: str = Field(..., description="Voice name")
    sample_rate: Optional[int] = Field(default=None, description="Sample rate in Hz")
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


class MiniMaxTTS(_BaseTTSCompat):
    model_config = ConfigDict(extra="forbid")

    key: Optional[str] = Field(default=None, description="MiniMax API key")
    model: str = Field(..., description="TTS model")
    voice_id: Optional[str] = Field(default=None, description="Voice style identifier")
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
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional MiniMax TTS params")
    skip_patterns: Optional[List[int]] = Field(default=None)

    @model_validator(mode="after")
    def _validate_params(self) -> "MiniMaxTTS":
        if self.voice_id is not None and self.timber_weights is not None:
            raise ValueError("MiniMaxTTS requires exactly one of voice_id or timber_weights")
        if self.voice_id is None and self.timber_weights is None:
            raise ValueError("MiniMaxTTS requires exactly one of voice_id or timber_weights")
        return self

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.additional_params or {})
        if self.key is not None:
            params["key"] = self.key
        params["model"] = self.model

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
        if self.skip_patterns is not None:
            result["skip_patterns"] = self.skip_patterns
        return result


class AliyunLLM(BaseLLM):
    model_config = ConfigDict(extra="forbid")

    api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    model: str = Field(..., description="Model name")
    base_url: Optional[str] = Field(default=None, description="Custom base URL")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    system_messages: Optional[List[Dict[str, Any]]] = Field(default=None)
    greeting_message: Optional[str] = Field(default=None)
    greeting_audio_url: Optional[str] = Field(default=None)
    failure_message: Optional[str] = Field(default=None)
    input_modalities: Optional[List[str]] = Field(default=None)
    params: Optional[Dict[str, Any]] = Field(default=None)
    headers: Optional[Dict[str, str]] = Field(default=None)
    output_modalities: Optional[List[str]] = Field(default=None)
    greeting_configs: Optional[LlmGreetingConfigs] = Field(default=None)
    template_variables: Optional[Dict[str, str]] = Field(default=None)
    vendor: Optional[str] = Field(default="aliyun")
    mcp_servers: Optional[List[Dict[str, Any]]] = Field(default=None)
    max_history: Optional[int] = Field(default=None, gt=0, description="Maximum number of conversation history messages to cache")

    @model_validator(mode="after")
    def _validate_byok_params(self) -> "AliyunLLM":
        if not self.model:
            raise ValueError("AliyunLLM requires model")
        if self.api_key is not None and self.base_url is None:
            raise ValueError("AliyunLLM requires base_url when api_key is set")
        if self.api_key is None and self.base_url is not None:
            raise ValueError("AliyunLLM base_url is only valid when api_key is set")
        if self.api_key is None and self.model.strip().lower() not in _OPENAI_MANAGED_MODELS:
            raise ValueError("AliyunLLM requires api_key unless using a supported Agora-managed model")
        if self.api_key is None and self.vendor is not None:
            raise ValueError("AliyunLLM Agora-managed mode does not allow vendor")
        return self

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {"model": self.model, **(self.params or {})}

        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens
        if self.temperature is not None:
            params["temperature"] = self.temperature
        if self.top_p is not None:
            params["top_p"] = self.top_p

        config: Dict[str, Any] = {
            "url": self.base_url or "https://api.openai.com/v1/chat/completions",
            "params": params,
            "style": "openai",
            "input_modalities": self.input_modalities or ["text"],
        }
        if self.api_key is not None:
            config["api_key"] = self.api_key
        if self.headers is not None:
            config["headers"] = self.headers

        if self.system_messages is not None:
            config["system_messages"] = self.system_messages
        if self.greeting_message is not None:
            config["greeting_message"] = self.greeting_message
        if self.greeting_audio_url is not None:
            config["greeting_audio_url"] = self.greeting_audio_url
        if self.failure_message is not None:
            config["failure_message"] = self.failure_message
        if self.output_modalities is not None:
            config["output_modalities"] = self.output_modalities
        if self.greeting_configs is not None:
            config["greeting_configs"] = _dump_optional_model(self.greeting_configs)
        if self.template_variables is not None:
            config["template_variables"] = self.template_variables
        if self.vendor is not None:
            config["vendor"] = self.vendor
        if self.mcp_servers is not None:
            config["mcp_servers"] = _ensure_mcp_transport(self.mcp_servers)
        if self.max_history is not None:
            config["max_history"] = self.max_history

        return config


class BytedanceLLM(BaseLLM):
    model_config = ConfigDict(extra="forbid")

    api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    model: str = Field(..., description="Model name")
    base_url: Optional[str] = Field(default=None, description="Custom base URL")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    system_messages: Optional[List[Dict[str, Any]]] = Field(default=None)
    greeting_message: Optional[str] = Field(default=None)
    greeting_audio_url: Optional[str] = Field(default=None)
    failure_message: Optional[str] = Field(default=None)
    input_modalities: Optional[List[str]] = Field(default=None)
    params: Optional[Dict[str, Any]] = Field(default=None)
    headers: Optional[Dict[str, str]] = Field(default=None)
    output_modalities: Optional[List[str]] = Field(default=None)
    greeting_configs: Optional[LlmGreetingConfigs] = Field(default=None)
    template_variables: Optional[Dict[str, str]] = Field(default=None)
    vendor: Optional[str] = Field(default="bytedance")
    mcp_servers: Optional[List[Dict[str, Any]]] = Field(default=None)
    max_history: Optional[int] = Field(default=None, gt=0, description="Maximum number of conversation history messages to cache")

    @model_validator(mode="after")
    def _validate_byok_params(self) -> "BytedanceLLM":
        if not self.model:
            raise ValueError("BytedanceLLM requires model")
        if self.api_key is not None and self.base_url is None:
            raise ValueError("BytedanceLLM requires base_url when api_key is set")
        if self.api_key is None and self.base_url is not None:
            raise ValueError("BytedanceLLM base_url is only valid when api_key is set")
        if self.api_key is None and self.model.strip().lower() not in _OPENAI_MANAGED_MODELS:
            raise ValueError("BytedanceLLM requires api_key unless using a supported Agora-managed model")
        if self.api_key is None and self.vendor is not None:
            raise ValueError("BytedanceLLM Agora-managed mode does not allow vendor")
        return self

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {"model": self.model, **(self.params or {})}

        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens
        if self.temperature is not None:
            params["temperature"] = self.temperature
        if self.top_p is not None:
            params["top_p"] = self.top_p

        config: Dict[str, Any] = {
            "url": self.base_url or "https://api.openai.com/v1/chat/completions",
            "params": params,
            "style": "openai",
            "input_modalities": self.input_modalities or ["text"],
        }
        if self.api_key is not None:
            config["api_key"] = self.api_key
        if self.headers is not None:
            config["headers"] = self.headers

        if self.system_messages is not None:
            config["system_messages"] = self.system_messages
        if self.greeting_message is not None:
            config["greeting_message"] = self.greeting_message
        if self.greeting_audio_url is not None:
            config["greeting_audio_url"] = self.greeting_audio_url
        if self.failure_message is not None:
            config["failure_message"] = self.failure_message
        if self.output_modalities is not None:
            config["output_modalities"] = self.output_modalities
        if self.greeting_configs is not None:
            config["greeting_configs"] = _dump_optional_model(self.greeting_configs)
        if self.template_variables is not None:
            config["template_variables"] = self.template_variables
        if self.vendor is not None:
            config["vendor"] = self.vendor
        if self.mcp_servers is not None:
            config["mcp_servers"] = _ensure_mcp_transport(self.mcp_servers)
        if self.max_history is not None:
            config["max_history"] = self.max_history

        return config


class DeepSeekLLM(BaseLLM):
    model_config = ConfigDict(extra="forbid")

    api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    model: str = Field(..., description="Model name")
    base_url: Optional[str] = Field(default=None, description="Custom base URL")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    system_messages: Optional[List[Dict[str, Any]]] = Field(default=None)
    greeting_message: Optional[str] = Field(default=None)
    greeting_audio_url: Optional[str] = Field(default=None)
    failure_message: Optional[str] = Field(default=None)
    input_modalities: Optional[List[str]] = Field(default=None)
    params: Optional[Dict[str, Any]] = Field(default=None)
    headers: Optional[Dict[str, str]] = Field(default=None)
    output_modalities: Optional[List[str]] = Field(default=None)
    greeting_configs: Optional[LlmGreetingConfigs] = Field(default=None)
    template_variables: Optional[Dict[str, str]] = Field(default=None)
    vendor: Optional[str] = Field(default="deepseek")
    mcp_servers: Optional[List[Dict[str, Any]]] = Field(default=None)
    max_history: Optional[int] = Field(default=None, gt=0, description="Maximum number of conversation history messages to cache")

    @model_validator(mode="after")
    def _validate_byok_params(self) -> "DeepSeekLLM":
        if not self.model:
            raise ValueError("DeepSeekLLM requires model")
        if self.api_key is not None and self.base_url is None:
            raise ValueError("DeepSeekLLM requires base_url when api_key is set")
        if self.api_key is None and self.base_url is not None:
            raise ValueError("DeepSeekLLM base_url is only valid when api_key is set")
        if self.api_key is None and self.model.strip().lower() not in _OPENAI_MANAGED_MODELS:
            raise ValueError("DeepSeekLLM requires api_key unless using a supported Agora-managed model")
        if self.api_key is None and self.vendor is not None:
            raise ValueError("DeepSeekLLM Agora-managed mode does not allow vendor")
        return self

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {"model": self.model, **(self.params or {})}

        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens
        if self.temperature is not None:
            params["temperature"] = self.temperature
        if self.top_p is not None:
            params["top_p"] = self.top_p

        config: Dict[str, Any] = {
            "url": self.base_url or "https://api.openai.com/v1/chat/completions",
            "params": params,
            "style": "openai",
            "input_modalities": self.input_modalities or ["text"],
        }
        if self.api_key is not None:
            config["api_key"] = self.api_key
        if self.headers is not None:
            config["headers"] = self.headers

        if self.system_messages is not None:
            config["system_messages"] = self.system_messages
        if self.greeting_message is not None:
            config["greeting_message"] = self.greeting_message
        if self.greeting_audio_url is not None:
            config["greeting_audio_url"] = self.greeting_audio_url
        if self.failure_message is not None:
            config["failure_message"] = self.failure_message
        if self.output_modalities is not None:
            config["output_modalities"] = self.output_modalities
        if self.greeting_configs is not None:
            config["greeting_configs"] = _dump_optional_model(self.greeting_configs)
        if self.template_variables is not None:
            config["template_variables"] = self.template_variables
        if self.vendor is not None:
            config["vendor"] = self.vendor
        if self.mcp_servers is not None:
            config["mcp_servers"] = _ensure_mcp_transport(self.mcp_servers)
        if self.max_history is not None:
            config["max_history"] = self.max_history

        return config


class TencentLLM(BaseLLM):
    model_config = ConfigDict(extra="forbid")

    api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    model: str = Field(..., description="Model name")
    base_url: Optional[str] = Field(default=None, description="Custom base URL")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    system_messages: Optional[List[Dict[str, Any]]] = Field(default=None)
    greeting_message: Optional[str] = Field(default=None)
    greeting_audio_url: Optional[str] = Field(default=None)
    failure_message: Optional[str] = Field(default=None)
    input_modalities: Optional[List[str]] = Field(default=None)
    params: Optional[Dict[str, Any]] = Field(default=None)
    headers: Optional[Dict[str, str]] = Field(default=None)
    output_modalities: Optional[List[str]] = Field(default=None)
    greeting_configs: Optional[LlmGreetingConfigs] = Field(default=None)
    template_variables: Optional[Dict[str, str]] = Field(default=None)
    vendor: Optional[str] = Field(default="tencent")
    mcp_servers: Optional[List[Dict[str, Any]]] = Field(default=None)
    max_history: Optional[int] = Field(default=None, gt=0, description="Maximum number of conversation history messages to cache")

    @model_validator(mode="after")
    def _validate_byok_params(self) -> "TencentLLM":
        if not self.model:
            raise ValueError("TencentLLM requires model")
        if self.api_key is not None and self.base_url is None:
            raise ValueError("TencentLLM requires base_url when api_key is set")
        if self.api_key is None and self.base_url is not None:
            raise ValueError("TencentLLM base_url is only valid when api_key is set")
        if self.api_key is None and self.model.strip().lower() not in _OPENAI_MANAGED_MODELS:
            raise ValueError("TencentLLM requires api_key unless using a supported Agora-managed model")
        if self.api_key is None and self.vendor is not None:
            raise ValueError("TencentLLM Agora-managed mode does not allow vendor")
        return self

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {"model": self.model, **(self.params or {})}

        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens
        if self.temperature is not None:
            params["temperature"] = self.temperature
        if self.top_p is not None:
            params["top_p"] = self.top_p

        config: Dict[str, Any] = {
            "url": self.base_url or "https://api.openai.com/v1/chat/completions",
            "params": params,
            "style": "openai",
            "input_modalities": self.input_modalities or ["text"],
        }
        if self.api_key is not None:
            config["api_key"] = self.api_key
        if self.headers is not None:
            config["headers"] = self.headers

        if self.system_messages is not None:
            config["system_messages"] = self.system_messages
        if self.greeting_message is not None:
            config["greeting_message"] = self.greeting_message
        if self.greeting_audio_url is not None:
            config["greeting_audio_url"] = self.greeting_audio_url
        if self.failure_message is not None:
            config["failure_message"] = self.failure_message
        if self.output_modalities is not None:
            config["output_modalities"] = self.output_modalities
        if self.greeting_configs is not None:
            config["greeting_configs"] = _dump_optional_model(self.greeting_configs)
        if self.template_variables is not None:
            config["template_variables"] = self.template_variables
        if self.vendor is not None:
            config["vendor"] = self.vendor
        if self.mcp_servers is not None:
            config["mcp_servers"] = _ensure_mcp_transport(self.mcp_servers)
        if self.max_history is not None:
            config["max_history"] = self.max_history

        return config


class QwenOmni(BaseMLLM):
    """Alibaba Cloud Qwen Omni Realtime MLLM vendor (`mllm.vendor`: ``qwen_omni``)."""

    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Alibaba Cloud Model Studio API key")
    url: str = Field(..., description="Qwen Omni Realtime WebSocket URL")
    model: Optional[str] = Field(default=None, description="Qwen Omni Realtime model name")
    voice: Optional[str] = Field(default=None, description="Voice identifier")
    instructions: Optional[str] = Field(default=None, description="System instructions")
    input_audio_transcription: Optional[Dict[str, Any]] = Field(
        default=None, description="Audio transcription settings"
    )
    greeting_message: Optional[str] = Field(default=None, description="Agent greeting message")
    input_modalities: Optional[List[str]] = Field(default=None, description="Input modalities")
    output_modalities: Optional[List[str]] = Field(default=None, description="Output modalities")
    messages: Optional[List[Dict[str, Any]]] = Field(default=None, description="Conversation messages")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Additional Qwen Omni parameters")
    turn_detection: Optional[MllmTurnDetection] = Field(default=None, description="MLLM turn detection configuration")
    failure_message: Optional[str] = Field(default=None, description="Message played on failure")

    def to_config(self) -> Dict[str, Any]:
        inner_params: Dict[str, Any] = dict(self.params or {})
        if self.model is not None:
            inner_params["model"] = self.model
        if self.voice is not None:
            inner_params["voice"] = self.voice
        if self.instructions is not None:
            inner_params["instructions"] = self.instructions
        if self.input_audio_transcription is not None:
            inner_params["input_audio_transcription"] = self.input_audio_transcription

        config: Dict[str, Any] = {
            "vendor": "qwen_omni",
            "api_key": self.api_key,
            "url": self.url,
        }
        if inner_params:
            config["params"] = inner_params
        if self.greeting_message is not None:
            config["greeting_message"] = self.greeting_message
        if self.input_modalities is not None:
            config["input_modalities"] = self.input_modalities
        if self.output_modalities is not None:
            config["output_modalities"] = self.output_modalities
        if self.messages is not None:
            config["messages"] = self.messages
        if self.failure_message is not None:
            config["failure_message"] = self.failure_message
        if self.turn_detection is not None:
            config["turn_detection"] = self.turn_detection
        return config


class SenseTimeAvatar(BaseAvatar):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    agora_token: Optional[str] = Field(default=None, description="RTC token for avatar publisher; generated by AgentSession when omitted")
    agora_uid: str = Field(..., description="Avatar RTC publisher uid")
    app_id: Optional[str] = Field(default=None, alias="appId", description="SenseTime app id")
    app_key: str = Field(..., description="SenseTime app key")
    scene_list: Optional[List[Dict[str, Any]]] = Field(default=None, alias="sceneList", description="SenseTime scene list")
    enable: Optional[bool] = Field(default=None)
    additional_params: Optional[Dict[str, Any]] = Field(default=None)

    @property
    def required_sample_rate(self) -> int:
        return 0

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "agora_uid": self.agora_uid,
            "app_key": self.app_key,
        }
        if self.agora_token is not None:
            params["agora_token"] = self.agora_token
        if self.app_id is not None:
            params["appId"] = self.app_id
        if self.scene_list is not None:
            params["sceneList"] = self.scene_list
        if self.additional_params is not None:
            params = {**self.additional_params, **params}

        enable = self.enable if self.enable is not None else True
        return {"enable": enable, "vendor": "sensetime", "params": params}


class SpatiusAvatar(BaseAvatar):
    model_config = ConfigDict(extra="forbid")

    spatius_api_key: str = Field(..., description="Spatius API key")
    spatius_app_id: str = Field(..., description="Spatius application ID")
    spatius_avatar_id: str = Field(..., description="Spatius avatar ID")
    agora_uid: str = Field(..., description="Agora UID used by the avatar service")
    agora_token: Optional[str] = Field(default=None, description="RTC token for avatar publisher; generated by AgentSession when omitted")
    region: Optional[str] = Field(default=None, description="Spatius service region, for example cn-beijing")
    sample_rate: Optional[int] = Field(default=None, description="Audio sample rate in Hz")
    session_expire_minutes: Optional[int] = Field(default=None, description="Spatius session validity duration in minutes")
    enable: Optional[bool] = Field(default=None)
    additional_params: Optional[Dict[str, Any]] = Field(default=None)

    @property
    def required_sample_rate(self) -> int:
        return self.sample_rate or 0

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "spatius_api_key": self.spatius_api_key,
            "spatius_app_id": self.spatius_app_id,
            "spatius_avatar_id": self.spatius_avatar_id,
            "agora_uid": self.agora_uid,
        }
        if self.agora_token is not None:
            params["agora_token"] = self.agora_token
        if self.region is not None:
            params["region"] = self.region
        if self.sample_rate is not None:
            params["sample_rate"] = self.sample_rate
        if self.session_expire_minutes is not None:
            params["session_expire_minutes"] = self.session_expire_minutes
        if self.additional_params is not None:
            params = {**self.additional_params, **params}

        enable = self.enable if self.enable is not None else True
        return {"enable": enable, "vendor": "spatius", "params": params}
