"""Preview provider vendor classes.

These follow the same shape as the GA vendor classes in ``vendors/`` — snake_case
constructor options in, snake_case wire config out — so they drop into
``agent.with_stt()`` unchanged. Sessions that use them route to the preview
endpoint automatically.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..vendors.base import BaseSTT
from pydantic import ConfigDict, Field

#: Rejects ``api_key=""``. ``Field(...)`` alone makes the key required but still
#: accepts the empty string, which would reach the provider as a blank
#: credential; the TypeScript and Go vendors both refuse it at construction.
_ApiKey = Field(..., min_length=1, description="Google API key")


class GeminiSTTModels:
    """Gemini preview transcription models."""

    TRANSCRIBE_35_LIVE = "gemini-3.5-transcribe-live"


class GeminiSTT(BaseSTT):
    """Gemini 3.5 Transcribe ASR vendor (preview).

    Example::

        agent = Agent(client=client).with_stt(
            GeminiSTT(api_key=..., language_codes=["en-US"])
        )
    """

    model_config = ConfigDict(extra="forbid")

    api_key: str = _ApiKey
    model: Optional[str] = Field(
        default=None,
        description="Model name. Defaults to `gemini-3.5-transcribe-live`.",
    )
    language_codes: Optional[List[str]] = Field(
        default=None,
        description=(
            "Languages the model should transcribe, sent as `params.language_codes`. "
            "Omitted from the request when unset, which is how the provider sets "
            "auto-detect — the SDK does not pin a language the caller never asked for. "
            "Pass one code to commit to a language, several to let the model choose "
            "between them, or an explicit empty list to request auto-detect outright. "
            "This is the only language setting on this vendor. The top-level "
            "`asr.language` is supplied by `Agent` from turn detection, as it is for "
            "every STT vendor."
        ),
    )
    custom_vocabulary: Optional[List[str]] = Field(
        default=None,
        description=(
            "Words and phrases to bias recognition toward — product names, jargon, "
            "proper nouns the model would otherwise mis-hear."
        ),
    )
    sample_rate: Optional[int] = Field(
        default=None,
        description="Audio sample rate in Hz. Defaults to 16000.",
    )
    word_timestamp: Optional[bool] = Field(
        default=None,
        description=(
            "Emit per-word timestamps in transcription results. Omitted unless explicitly set; "
            "cannot be `true` when `custom_vocabulary` is set."
        ),
    )
    additional_params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional vendor-specific parameters.",
    )

    def to_config(self) -> Dict[str, Any]:
        model = self.model if self.model is not None else GeminiSTTModels.TRANSCRIBE_35_LIVE
        sample_rate = self.sample_rate if self.sample_rate is not None else 16000

        # additional_params first so that explicit fields always win.
        params: Dict[str, Any] = dict(self.additional_params or {})
        params["api_key"] = self.api_key
        params["model"] = model
        params["sample_rate"] = sample_rate
        # Omitted unless the caller asked for it: no language_codes is how the
        # provider spells auto-detect, and seeding it from ``language`` would pin
        # every request to a language the caller never chose.
        if self.language_codes is not None:
            params["language_codes"] = list(self.language_codes)
        if self.custom_vocabulary is not None:
            params["custom_vocabulary"] = list(self.custom_vocabulary)
        if self.word_timestamp is not None:
            params["word_timestamp"] = self.word_timestamp
        if "custom_vocabulary" in params and params.get("word_timestamp") is True:
            raise ValueError("custom_vocabulary cannot be used with word_timestamp=true")

        # No top-level `language`: `Agent` sets it from turn detection,
        # the same as every other STT vendor.
        return {"vendor": "gemini", "params": params}


__all__ = [
    "GeminiSTTModels",
    "GeminiSTT",
]
