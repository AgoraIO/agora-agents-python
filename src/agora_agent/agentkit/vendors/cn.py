from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .avatar import BaseAvatar
from .llm import OpenAI
from .stt import BaseSTT as _BaseSTTCompat
from .tts import BaseTTS as _BaseTTSCompat


class TencentSTTOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(..., description="Tencent ASR secret key")
    app_id: str = Field(..., description="Tencent ASR app id")
    secret: str = Field(..., description="Tencent ASR secret")
    engine_model_type: str = Field(..., description="Tencent ASR engine model type")
    voice_id: str = Field(..., description="Tencent ASR voice id")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)


class TencentSTT(_BaseSTTCompat):
    def __init__(self, **kwargs: Any):
        self.options = TencentSTTOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.options.additional_params or {})
        params.update(
            {
                "key": self.options.key,
                "app_id": self.options.app_id,
                "secret": self.options.secret,
                "engine_model_type": self.options.engine_model_type,
                "voice_id": self.options.voice_id,
            }
        )
        return {"vendor": "tencent", "params": params}


class FengmingSTT(_BaseSTTCompat):
    def __init__(self, **kwargs: Any):
        if kwargs:
            unexpected = ", ".join(sorted(kwargs))
            raise TypeError(f"FengmingSTT does not accept parameters: {unexpected}")

    def to_config(self) -> Dict[str, Any]:
        return {"vendor": "fengming"}


class XfyunSTTOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: Optional[str] = Field(default=None, description="Xfyun ASR API key")
    app_id: Optional[str] = Field(default=None, description="Xfyun ASR app id")
    api_secret: Optional[str] = Field(default=None, description="Xfyun ASR API secret")
    language: Optional[str] = Field(default=None, description="Xfyun ASR language")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)


class XfyunSTT(_BaseSTTCompat):
    def __init__(self, **kwargs: Any):
        self.options = XfyunSTTOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.options.additional_params or {})
        if self.options.api_key is not None:
            params["api_key"] = self.options.api_key
        if self.options.app_id is not None:
            params["app_id"] = self.options.app_id
        if self.options.api_secret is not None:
            params["api_secret"] = self.options.api_secret
        if self.options.language is not None:
            params["language"] = self.options.language
        return {
            "vendor": "xfyun",
            "params": params,
        }


class XfyunBigModelSTTOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: Optional[str] = Field(default=None, description="Xfyun BigModel ASR API key")
    app_id: Optional[str] = Field(default=None, description="Xfyun BigModel ASR app id")
    api_secret: Optional[str] = Field(default=None, description="Xfyun BigModel ASR API secret")
    language_name: Optional[str] = Field(default=None, description="Xfyun BigModel ASR language name")
    language: Optional[str] = Field(default=None, description="Xfyun BigModel ASR language")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)


class XfyunBigModelSTT(_BaseSTTCompat):
    def __init__(self, **kwargs: Any):
        self.options = XfyunBigModelSTTOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.options.additional_params or {})
        if self.options.api_key is not None:
            params["api_key"] = self.options.api_key
        if self.options.app_id is not None:
            params["app_id"] = self.options.app_id
        if self.options.api_secret is not None:
            params["api_secret"] = self.options.api_secret
        if self.options.language_name is not None:
            params["language_name"] = self.options.language_name
        if self.options.language is not None:
            params["language"] = self.options.language
        return {
            "vendor": "xfyun_bigmodel",
            "params": params,
        }


class XfyunDialectSTTOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app_id: Optional[str] = Field(default=None, description="Xfyun Dialect ASR app id")
    access_key_id: Optional[str] = Field(default=None, description="Xfyun Dialect ASR access key id")
    access_key_secret: Optional[str] = Field(default=None, description="Xfyun Dialect ASR access key secret")
    language: Optional[str] = Field(default=None, description="Xfyun Dialect ASR language")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)


class XfyunDialectSTT(_BaseSTTCompat):
    def __init__(self, **kwargs: Any):
        self.options = XfyunDialectSTTOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.options.additional_params or {})
        if self.options.app_id is not None:
            params["app_id"] = self.options.app_id
        if self.options.access_key_id is not None:
            params["access_key_id"] = self.options.access_key_id
        if self.options.access_key_secret is not None:
            params["access_key_secret"] = self.options.access_key_secret
        if self.options.language is not None:
            params["language"] = self.options.language
        return {
            "vendor": "xfyun_dialect",
            "params": params,
        }


class MicrosoftSTTOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(..., description="Azure subscription key")
    region: str = Field(..., description="Azure region (e.g., eastus)")
    language: str = Field(..., description="Language code (e.g., zh-CN)")
    phrase_list: Optional[List[str]] = Field(default=None, description="Microsoft ASR phrase list")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)


class MicrosoftSTT(_BaseSTTCompat):
    def __init__(self, **kwargs: Any):
        self.options = MicrosoftSTTOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.options.additional_params or {})
        params.update({
            "key": self.options.key,
            "region": self.options.region,
            "language": self.options.language,
        })
        if self.options.phrase_list is not None:
            params["phrase_list"] = self.options.phrase_list
        return {
            "vendor": "microsoft",
            "params": params,
        }


class TencentTTSOptions(BaseModel):
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


class TencentTTS(_BaseTTSCompat):
    def __init__(self, **kwargs: Any):
        self.options = TencentTTSOptions(**kwargs)

    @property
    def sample_rate(self) -> Optional[int]:
        audio_setting = (self.options.additional_params or {}).get("audio_setting")
        if isinstance(audio_setting, dict):
            sample_rate = audio_setting.get("sample_rate")
            if isinstance(sample_rate, int):
                return sample_rate
        return None

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.options.additional_params or {})
        params.update(
            {
                "app_id": self.options.app_id,
                "secret_id": self.options.secret_id,
                "secret_key": self.options.secret_key,
                "voice_type": self.options.voice_type,
            }
        )
        if self.options.volume is not None:
            params["volume"] = self.options.volume
        if self.options.speed is not None:
            params["speed"] = self.options.speed
        if self.options.emotion_category is not None:
            params["emotion_category"] = self.options.emotion_category
        if self.options.emotion_intensity is not None:
            params["emotion_intensity"] = self.options.emotion_intensity

        result: Dict[str, Any] = {
            "vendor": "tencent",
            "params": params,
        }
        if self.options.skip_patterns is not None:
            result["skip_patterns"] = self.options.skip_patterns
        return result


class BytedanceTTSOptions(BaseModel):
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


class BytedanceTTS(_BaseTTSCompat):
    def __init__(self, **kwargs: Any):
        self.options = BytedanceTTSOptions(**kwargs)

    @property
    def sample_rate(self) -> Optional[int]:
        audio_setting = (self.options.additional_params or {}).get("audio_setting")
        if isinstance(audio_setting, dict):
            sample_rate = audio_setting.get("sample_rate")
            if isinstance(sample_rate, int):
                return sample_rate
        return None

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.options.additional_params or {})
        params.update(
            {
                "token": self.options.token,
                "app_id": self.options.app_id,
                "cluster": self.options.cluster,
                "voice_type": self.options.voice_type,
            }
        )
        if self.options.speed_ratio is not None:
            params["speed_ratio"] = self.options.speed_ratio
        if self.options.volume_ratio is not None:
            params["volume_ratio"] = self.options.volume_ratio
        if self.options.pitch_ratio is not None:
            params["pitch_ratio"] = self.options.pitch_ratio
        if self.options.emotion is not None:
            params["emotion"] = self.options.emotion

        result: Dict[str, Any] = {
            "vendor": "bytedance",
            "params": params,
        }
        if self.options.skip_patterns is not None:
            result["skip_patterns"] = self.options.skip_patterns
        return result


class BytedanceDuplexTTSOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(..., description="Bytedance Duplex TTS auth token")
    app_id: str = Field(..., description="Bytedance Duplex TTS app id")
    speaker: str = Field(..., description="Bytedance Duplex TTS speaker")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional Bytedance Duplex TTS params")
    skip_patterns: Optional[List[int]] = Field(default=None)


class BytedanceDuplexTTS(_BaseTTSCompat):
    def __init__(self, **kwargs: Any):
        self.options = BytedanceDuplexTTSOptions(**kwargs)

    @property
    def sample_rate(self) -> Optional[int]:
        audio_setting = (self.options.additional_params or {}).get("audio_setting")
        if isinstance(audio_setting, dict):
            sample_rate = audio_setting.get("sample_rate")
            if isinstance(sample_rate, int):
                return sample_rate
        return None

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.options.additional_params or {})
        params.update(
            {
                "token": self.options.token,
                "app_id": self.options.app_id,
                "speaker": self.options.speaker,
            }
        )

        result: Dict[str, Any] = {
            "vendor": "bytedance_duplex",
            "params": params,
        }
        if self.options.skip_patterns is not None:
            result["skip_patterns"] = self.options.skip_patterns
        return result


class CosyVoiceTTSOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: Optional[str] = Field(default=None, description="CosyVoice API key")
    model: Optional[str] = Field(default=None, description="CosyVoice model")
    sample_rate: Optional[int] = Field(default=None, description="Output sample rate in Hz")
    voice: Optional[str] = Field(default=None, description="CosyVoice voice")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="CosyVoice TTS params from REST doc")
    skip_patterns: Optional[List[int]] = Field(default=None)


class CosyVoiceTTS(_BaseTTSCompat):
    def __init__(self, **kwargs: Any):
        self.options = CosyVoiceTTSOptions(**kwargs)

    @property
    def sample_rate(self) -> Optional[int]:
        if self.options.sample_rate is not None:
            return self.options.sample_rate
        audio_setting = (self.options.additional_params or {}).get("audio_setting")
        if isinstance(audio_setting, dict):
            sample_rate = audio_setting.get("sample_rate")
            if isinstance(sample_rate, int):
                return sample_rate
        return None

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.options.additional_params or {})
        if self.options.api_key is not None:
            params["api_key"] = self.options.api_key
        if self.options.model is not None:
            params["model"] = self.options.model
        if self.options.sample_rate is not None:
            params["sample_rate"] = self.options.sample_rate
        if self.options.voice is not None:
            params["voice"] = self.options.voice
        result: Dict[str, Any] = {
            "vendor": "cosyvoice",
            "params": params,
        }
        if self.options.skip_patterns is not None:
            result["skip_patterns"] = self.options.skip_patterns
        return result


class StepFunTTSOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: Optional[str] = Field(default=None, description="StepFun TTS API key")
    model: Optional[str] = Field(default=None, description="StepFun TTS model")
    voice_id: Optional[str] = Field(default=None, description="StepFun TTS voice id")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="StepFun TTS params from REST doc")
    skip_patterns: Optional[List[int]] = Field(default=None)


class StepFunTTS(_BaseTTSCompat):
    def __init__(self, **kwargs: Any):
        self.options = StepFunTTSOptions(**kwargs)

    @property
    def sample_rate(self) -> Optional[int]:
        audio_setting = (self.options.additional_params or {}).get("audio_setting")
        if isinstance(audio_setting, dict):
            sample_rate = audio_setting.get("sample_rate")
            if isinstance(sample_rate, int):
                return sample_rate
        return None

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.options.additional_params or {})
        if self.options.api_key is not None:
            params["api_key"] = self.options.api_key
        if self.options.model is not None:
            params["model"] = self.options.model
        if self.options.voice_id is not None:
            params["voice_id"] = self.options.voice_id
        result: Dict[str, Any] = {
            "vendor": "stepfun",
            "params": params,
        }
        if self.options.skip_patterns is not None:
            result["skip_patterns"] = self.options.skip_patterns
        return result


class MicrosoftTTSOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(..., description="Azure subscription key")
    region: str = Field(..., description="Azure region (e.g., eastus)")
    voice_name: str = Field(..., description="Voice name")
    sample_rate: Optional[int] = Field(default=None, description="Sample rate in Hz")
    speed: Optional[float] = Field(default=None, description="Speaking rate multiplier")
    volume: Optional[float] = Field(default=None, description="Audio volume")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional Microsoft TTS params")
    skip_patterns: Optional[List[int]] = Field(default=None)


class MicrosoftTTS(_BaseTTSCompat):
    def __init__(self, **kwargs: Any):
        self.options = MicrosoftTTSOptions(**kwargs)

    @property
    def sample_rate(self) -> Optional[int]:
        return self.options.sample_rate

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.options.additional_params or {})
        params.update({
            "key": self.options.key,
            "region": self.options.region,
            "voice_name": self.options.voice_name,
        })
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


class MiniMaxTTSOptions(BaseModel):
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
    def _validate_params(self) -> "MiniMaxTTSOptions":
        if self.voice_id is not None and self.timber_weights is not None:
            raise ValueError("MiniMaxTTS requires exactly one of voice_id or timber_weights")
        if self.voice_id is None and self.timber_weights is None:
            raise ValueError("MiniMaxTTS requires exactly one of voice_id or timber_weights")
        return self


class MiniMaxTTS(_BaseTTSCompat):
    def __init__(self, **kwargs: Any):
        self.options = MiniMaxTTSOptions(**kwargs)

    @property
    def sample_rate(self) -> Optional[int]:
        return self.options.sample_rate

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.options.additional_params or {})
        if self.options.key is not None:
            params["key"] = self.options.key
        params["model"] = self.options.model

        voice_setting: Dict[str, Any] = {}
        if self.options.voice_id is not None:
            voice_setting["voice_id"] = self.options.voice_id
        if self.options.speed is not None:
            voice_setting["speed"] = self.options.speed
        if self.options.vol is not None:
            voice_setting["vol"] = self.options.vol
        if self.options.pitch is not None:
            voice_setting["pitch"] = self.options.pitch
        if self.options.emotion is not None:
            voice_setting["emotion"] = self.options.emotion
        if self.options.latex_read is not None:
            voice_setting["latex_read"] = self.options.latex_read
        if self.options.english_normalization is not None:
            voice_setting["english_normalization"] = self.options.english_normalization
        if voice_setting:
            params["voice_setting"] = voice_setting
        if self.options.timber_weights is not None:
            params["timber_weights"] = self.options.timber_weights
        if self.options.sample_rate is not None:
            params["audio_setting"] = {"sample_rate": self.options.sample_rate}
        if self.options.pronunciation_dict is not None:
            params["pronunciation_dict"] = self.options.pronunciation_dict
        if self.options.language_boost is not None:
            params["language_boost"] = self.options.language_boost

        result: Dict[str, Any] = {"vendor": "minimax", "params": params}
        if self.options.skip_patterns is not None:
            result["skip_patterns"] = self.options.skip_patterns
        return result


class AliyunLLM(OpenAI):
    def __init__(self, **kwargs: Any):
        kwargs["vendor"] = "aliyun"
        super().__init__(**kwargs)


class BytedanceLLM(OpenAI):
    def __init__(self, **kwargs: Any):
        kwargs["vendor"] = "bytedance"
        super().__init__(**kwargs)


class DeepSeekLLM(OpenAI):
    def __init__(self, **kwargs: Any):
        kwargs["vendor"] = "deepseek"
        super().__init__(**kwargs)


class TencentLLM(OpenAI):
    def __init__(self, **kwargs: Any):
        kwargs["vendor"] = "tencent"
        super().__init__(**kwargs)


class SenseTimeAvatarOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agora_token: Optional[str] = Field(default=None, description="RTC token for avatar publisher; generated by AgentSession when omitted")
    agora_uid: str = Field(..., description="Avatar RTC publisher uid")
    app_id: Optional[str] = Field(default=None, alias="appId", description="SenseTime app id")
    app_key: str = Field(..., description="SenseTime app key")
    scene_list: Optional[List[Dict[str, Any]]] = Field(default=None, alias="sceneList", description="SenseTime scene list")
    enable: Optional[bool] = Field(default=None)
    additional_params: Optional[Dict[str, Any]] = Field(default=None)


class SenseTimeAvatar(BaseAvatar):
    def __init__(self, **kwargs: Any):
        self.options = SenseTimeAvatarOptions(**kwargs)

    @property
    def required_sample_rate(self) -> int:
        return 0

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "agora_uid": self.options.agora_uid,
            "app_key": self.options.app_key,
        }
        if self.options.agora_token is not None:
            params["agora_token"] = self.options.agora_token
        if self.options.app_id is not None:
            params["appId"] = self.options.app_id
        if self.options.scene_list is not None:
            params["sceneList"] = self.options.scene_list
        if self.options.additional_params is not None:
            params = {**self.options.additional_params, **params}

        enable = self.options.enable if self.options.enable is not None else True
        return {"enable": enable, "vendor": "sensetime", "params": params}


class SpatiusAvatarOptions(BaseModel):
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


class SpatiusAvatar(BaseAvatar):
    def __init__(self, **kwargs: Any):
        self.options = SpatiusAvatarOptions(**kwargs)

    @property
    def required_sample_rate(self) -> int:
        return self.options.sample_rate or 0

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "spatius_api_key": self.options.spatius_api_key,
            "spatius_app_id": self.options.spatius_app_id,
            "spatius_avatar_id": self.options.spatius_avatar_id,
            "agora_uid": self.options.agora_uid,
        }
        if self.options.agora_token is not None:
            params["agora_token"] = self.options.agora_token
        if self.options.region is not None:
            params["region"] = self.options.region
        if self.options.sample_rate is not None:
            params["sample_rate"] = self.options.sample_rate
        if self.options.session_expire_minutes is not None:
            params["session_expire_minutes"] = self.options.session_expire_minutes
        if self.options.additional_params is not None:
            params = {**self.options.additional_params, **params}

        enable = self.options.enable if self.options.enable is not None else True
        return {"enable": enable, "vendor": "spatius", "params": params}
