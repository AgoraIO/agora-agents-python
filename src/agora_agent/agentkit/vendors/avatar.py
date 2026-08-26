import warnings
from typing import Any, Dict, Optional

from .base import BaseAvatar
from pydantic import BaseModel, ConfigDict, Field, field_validator

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


class LiveAvatarAvatar(LiveAvatarAvatarOptions, BaseAvatar):
    @property
    def required_sample_rate(self) -> int:
        return LIVEAVATAR_SAMPLE_RATE

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "api_key": self.api_key,
            "quality": self.quality,
            "agora_uid": self.agora_uid,
        }

        if self.agora_token is not None:
            params["agora_token"] = self.agora_token
        if self.avatar_id is not None:
            params["avatar_id"] = self.avatar_id
        if self.disable_idle_timeout is not None:
            params["disable_idle_timeout"] = self.disable_idle_timeout
        if self.activity_idle_timeout is not None:
            params["activity_idle_timeout"] = self.activity_idle_timeout
        if self.additional_params is not None:
            params = {**self.additional_params, **params}

        enable = self.enable if self.enable is not None else True
        return {"enable": enable, "vendor": "liveavatar", "params": params}


class HeyGenAvatarOptions(BaseModel):
    """Deprecated: HeyGen has been renamed to LiveAvatar. Use LiveAvatarAvatar instead."""

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

    def model_post_init(self, __context: Any) -> None:
        # stacklevel=3: warn() <- model_post_init <- pydantic __init__ <- user code,
        # so the warning points at the user's construction site, not pydantic internals.
        warnings.warn(
            "HeyGenAvatar is deprecated; use LiveAvatarAvatar instead.",
            DeprecationWarning,
            stacklevel=3,
        )


class HeyGenAvatar(HeyGenAvatarOptions, BaseAvatar):
    """Deprecated: HeyGen has been renamed to LiveAvatar. Use LiveAvatarAvatar instead."""

    @property
    def required_sample_rate(self) -> int:
        return HEYGEN_SAMPLE_RATE

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "api_key": self.api_key,
            "quality": self.quality,
            "agora_uid": self.agora_uid,
        }

        if self.agora_token is not None:
            params["agora_token"] = self.agora_token
        if self.avatar_id is not None:
            params["avatar_id"] = self.avatar_id
        if self.disable_idle_timeout is not None:
            params["disable_idle_timeout"] = self.disable_idle_timeout
        if self.activity_idle_timeout is not None:
            params["activity_idle_timeout"] = self.activity_idle_timeout
        if self.additional_params is not None:
            params = {**self.additional_params, **params}

        enable = self.enable if self.enable is not None else True
        return {"enable": enable, "vendor": "heygen", "params": params}


class AkoolAvatarOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Akool API key")
    avatar_id: Optional[str] = Field(default=None, description="Avatar ID")
    enable: Optional[bool] = Field(default=None, description="Enable avatar (default: true)")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional vendor-specific parameters")


class AkoolAvatar(AkoolAvatarOptions, BaseAvatar):
    @property
    def required_sample_rate(self) -> int:
        return AKOOL_SAMPLE_RATE

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "api_key": self.api_key,
        }

        if self.avatar_id is not None:
            params["avatar_id"] = self.avatar_id
        if self.additional_params is not None:
            params = {**self.additional_params, **params}

        enable = self.enable if self.enable is not None else True
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


class GenericAvatar(GenericAvatarOptions, BaseAvatar):
    @property
    def required_sample_rate(self) -> int:
        return 0

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "api_key": self.api_key,
            "api_base_url": self.api_base_url,
            "avatar_id": self.avatar_id,
            "agora_uid": self.agora_uid,
        }

        if self.agora_appid is not None:
            params["agora_appid"] = self.agora_appid
        if self.agora_token is not None:
            params["agora_token"] = self.agora_token
        if self.agora_channel is not None:
            params["agora_channel"] = self.agora_channel
        if self.additional_params is not None:
            params = {**self.additional_params, **params}

        enable = self.enable if self.enable is not None else True
        return {"enable": enable, "vendor": "generic", "params": params}


class AnamAvatarOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Anam API key")
    avatar_id: str = Field(..., description="Anam avatar ID")
    enable: Optional[bool] = Field(default=None, description="Enable avatar (default: true)")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional vendor-specific parameters")


class AnamAvatar(AnamAvatarOptions, BaseAvatar):
    @property
    def required_sample_rate(self) -> int:
        return 0

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "api_key": self.api_key,
            "avatar_id": self.avatar_id,
        }

        if self.additional_params is not None:
            params = {**self.additional_params, **params}

        enable = self.enable if self.enable is not None else True
        return {"enable": enable, "vendor": "anam", "params": params}
