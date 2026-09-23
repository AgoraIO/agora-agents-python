"""Gemini TTS preview; reuses the gemini-live session gate."""

from typing import Any, Dict, Optional

from ..vendors.base import BaseTTS
from pydantic import ConfigDict, Field, field_validator


class GeminiTTSModels:
    """Gemini 3.8 Flash TTS preview model."""

    FLASH_38 = "gemini-3.8-flash-tts"


class GeminiTTS(BaseTTS):
    """Preview-only TTS; model names are sent verbatim for rollout flexibility."""

    model_config = ConfigDict(extra="forbid")
    api_key: str = Field(..., repr=False)
    model: str = GeminiTTSModels.FLASH_38
    voice: str = "Puck"
    style: Optional[str] = None

    @field_validator("api_key", "model", "voice")
    @classmethod
    def require_nonblank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("GeminiTTS requires a nonblank value")
        return value

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {"api_key": self.api_key, "model": self.model, "voice": self.voice}
        if self.style is not None:
            params["style"] = self.style
        return {"vendor": "gemini", "params": params}
