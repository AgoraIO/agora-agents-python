import warnings
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .base import BaseAvatar

LIVEAVATAR_SAMPLE_RATE = 24000
HEYGEN_SAMPLE_RATE = LIVEAVATAR_SAMPLE_RATE
AKOOL_SAMPLE_RATE = 16000


class LiveAvatarAvatarOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="LiveAvatar API key")
    quality: str = Field(..., description="Avatar quality: low, medium, or high")
    agora_uid: str = Field(..., description="Agora UID for the avatar stream")
    agora_token: Optional[str] = Field(default=None, description="RTC token for avatar authentication")
    avatar_id: Optional[str] = Field(default=None, description="Avatar ID")
    enable: Optional[bool] = Field(default=None, description="Enable avatar (default: true)")
    disable_idle_timeout: Optional[bool] = Field(default=None, description="Whether to disable idle timeout")
    activity_idle_timeout: Optional[int] = Field(default=None, description="Idle timeout in seconds")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional vendor-specific parameters")

    @field_validator("quality")
    @classmethod
    def validate_quality(cls, v: str) -> str:
        valid = ("low", "medium", "high")
        if v not in valid:
            raise ValueError(f"Invalid quality '{v}'. Must be one of: {', '.join(valid)}")
        return v


class LiveAvatarAvatar(BaseAvatar):
    def __init__(self, **kwargs: Any):
        self.options = LiveAvatarAvatarOptions(**kwargs)

    @property
    def required_sample_rate(self) -> int:
        return LIVEAVATAR_SAMPLE_RATE

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "api_key": self.options.api_key,
            "quality": self.options.quality,
            "agora_uid": self.options.agora_uid,
        }

        if self.options.agora_token is not None:
            params["agora_token"] = self.options.agora_token
        if self.options.avatar_id is not None:
            params["avatar_id"] = self.options.avatar_id
        if self.options.disable_idle_timeout is not None:
            params["disable_idle_timeout"] = self.options.disable_idle_timeout
        if self.options.activity_idle_timeout is not None:
            params["activity_idle_timeout"] = self.options.activity_idle_timeout
        if self.options.additional_params is not None:
            params = {**self.options.additional_params, **params}

        enable = self.options.enable if self.options.enable is not None else True
        return {"enable": enable, "vendor": "liveavatar", "params": params}


class HeyGenAvatarOptions(LiveAvatarAvatarOptions):
    """Deprecated: use :class:`LiveAvatarAvatarOptions` instead."""


class HeyGenAvatar(BaseAvatar):
    """Deprecated: HeyGen has been renamed to LiveAvatar. Use LiveAvatarAvatar instead."""

    def __init__(self, **kwargs: Any):
        warnings.warn(
            "HeyGenAvatar is deprecated; use LiveAvatarAvatar instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.options = HeyGenAvatarOptions(**kwargs)

    @property
    def required_sample_rate(self) -> int:
        return HEYGEN_SAMPLE_RATE

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "api_key": self.options.api_key,
            "quality": self.options.quality,
            "agora_uid": self.options.agora_uid,
        }

        if self.options.agora_token is not None:
            params["agora_token"] = self.options.agora_token
        if self.options.avatar_id is not None:
            params["avatar_id"] = self.options.avatar_id
        if self.options.disable_idle_timeout is not None:
            params["disable_idle_timeout"] = self.options.disable_idle_timeout
        if self.options.activity_idle_timeout is not None:
            params["activity_idle_timeout"] = self.options.activity_idle_timeout
        if self.options.additional_params is not None:
            params = {**self.options.additional_params, **params}

        enable = self.options.enable if self.options.enable is not None else True
        return {"enable": enable, "vendor": "heygen", "params": params}


class AkoolAvatarOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Akool API key")
    avatar_id: Optional[str] = Field(default=None, description="Avatar ID")
    enable: Optional[bool] = Field(default=None, description="Enable avatar (default: true)")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional vendor-specific parameters")


class AkoolAvatar(BaseAvatar):
    def __init__(self, **kwargs: Any):
        self.options = AkoolAvatarOptions(**kwargs)

    @property
    def required_sample_rate(self) -> int:
        return AKOOL_SAMPLE_RATE

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "api_key": self.options.api_key,
        }

        if self.options.avatar_id is not None:
            params["avatar_id"] = self.options.avatar_id
        if self.options.additional_params is not None:
            params = {**self.options.additional_params, **params}

        enable = self.options.enable if self.options.enable is not None else True
        return {"enable": enable, "vendor": "akool", "params": params}


class GenericAvatarOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Generic avatar provider API key")
    api_base_url: str = Field(..., description="Avatar provider API base URL")
    avatar_id: str = Field(..., description="Avatar ID")
    agora_uid: str = Field(..., description="Agora UID for the avatar video stream")
    agora_appid: Optional[str] = Field(default=None, description="Agora App ID; filled by AgentSession when omitted")
    agora_token: Optional[str] = Field(default=None, description="RTC token; generated by AgentSession when omitted")
    agora_channel: Optional[str] = Field(default=None, description="Agora channel; filled by AgentSession when omitted")
    enable: Optional[bool] = Field(default=None, description="Enable avatar (default: true)")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional vendor-specific parameters")


class GenericAvatar(BaseAvatar):
    def __init__(self, **kwargs: Any):
        self.options = GenericAvatarOptions(**kwargs)

    @property
    def required_sample_rate(self) -> int:
        return 0

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "api_key": self.options.api_key,
            "api_base_url": self.options.api_base_url,
            "avatar_id": self.options.avatar_id,
            "agora_uid": self.options.agora_uid,
        }

        if self.options.agora_appid is not None:
            params["agora_appid"] = self.options.agora_appid
        if self.options.agora_token is not None:
            params["agora_token"] = self.options.agora_token
        if self.options.agora_channel is not None:
            params["agora_channel"] = self.options.agora_channel
        if self.options.additional_params is not None:
            params = {**self.options.additional_params, **params}

        enable = self.options.enable if self.options.enable is not None else True
        return {"enable": enable, "vendor": "generic", "params": params}


class AnamAvatarOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Anam API key")
    persona_id: Optional[str] = Field(default=None, description="Anam persona ID")
    enable: Optional[bool] = Field(default=None, description="Enable avatar (default: true)")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional vendor-specific parameters")


class AnamAvatar(BaseAvatar):
    def __init__(self, **kwargs: Any):
        self.options = AnamAvatarOptions(**kwargs)

    @property
    def required_sample_rate(self) -> int:
        return 0

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "api_key": self.options.api_key,
        }

        if self.options.persona_id is not None:
            params["persona_id"] = self.options.persona_id
        if self.options.additional_params is not None:
            params = {**self.options.additional_params, **params}

        enable = self.options.enable if self.options.enable is not None else True
        return {"enable": enable, "vendor": "anam", "params": params}
