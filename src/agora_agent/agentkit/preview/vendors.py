"""Preview-only vendor classes.

Wire shapes here match the preview gateway contract exactly and are not served
by the production environment. See ``preview/client.py`` for the routing and the
``agora-feature`` gate.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from ..vendors.base import BaseMLLM
from ..vendors.mllm import MllmTurnDetectionConfig
from pydantic import ConfigDict, Field

#: Rejects ``api_key=""``. ``Field(...)`` alone makes the key required but still
#: accepts the empty string, which would reach the provider as a blank
#: credential; the TypeScript and Go vendors both refuse it at construction.
_ApiKey = Field(..., min_length=1, description="Google API key")


class GeminiPreviewMllmModels:
    """Preview MLLM model names.

    Google is renaming these from codenames to conventional model IDs
    (``walkie-talkie`` -> ``gemini-3.5-live``, ``clever-chatter`` ->
    ``gemini-3.5-live-thinking``). Both spellings are listed because both are
    accepted during the rollout; see :data:`GEMINI_PREVIEW_MLLM_DEFAULTS` for
    which one the vendor classes send.
    """

    #: Codename for the low-latency model. Currently the default.
    WALKIE_TALKIE = "walkie-talkie"
    #: Codename for the reasoning model. Currently the default.
    CLEVER_CHATTER = "clever-chatter"
    #: Post-rename name for :class:`GeminiWalkieTalkie`.
    LIVE_35 = "gemini-3.5-live"
    #: Post-rename name for :class:`GeminiCleverChatter`.
    LIVE_35_THINKING = "gemini-3.5-live-thinking"


#: The model name each preview MLLM class sends by default.
#:
#: Still the codenames: as of 2026-08-19 the renamed IDs are propagating through
#: Google's fleet and are not live everywhere, while the codenames work. When
#: Google confirms the rename has landed, point these two entries at ``LIVE_35``
#: / ``LIVE_35_THINKING`` — that is the whole cutover. Callers who need the new
#: names sooner can pass ``model=`` per instance.
GEMINI_PREVIEW_MLLM_DEFAULTS = {
    "walkie_talkie": GeminiPreviewMllmModels.WALKIE_TALKIE,
    "clever_chatter": GeminiPreviewMllmModels.CLEVER_CHATTER,
}


GEMINI_THINKING_LEVELS = ("low", "medium", "high")

GeminiThinkingLevel = Literal["low", "medium", "high"]

#: The preview MLLM talks to the Gemini Developer API rather than a WebSocket host.
GEMINI_PREVIEW_MLLM_URL = "https://generativelanguage.googleapis.com"


class _GeminiPreviewMLLM(BaseMLLM):
    """Shared envelope for the preview Gemini MLLMs.

    Differs from the production ``GeminiLive`` in two ways the preview
    gateway requires: ``params.api_key`` is repeated inside ``params``, and
    ``url`` defaults to the Gemini Developer API host rather than a WebSocket
    endpoint.
    """

    model_config = ConfigDict(extra="forbid")

    api_key: str = _ApiKey
    model: Optional[str] = Field(default=None, description="Override the preview model name")
    voice: Optional[str] = Field(default=None, description="Voice name (e.g., Puck)")
    language_codes: Optional[List[str]] = Field(
        default=None,
        description=(
            "Languages the model should work in, sent as params.language_codes. "
            "The preview MLLMs take the plural array, not the singular `language` "
            "(which belongs to xAI Grok). Omitted from the request when unset."
        ),
    )
    url: Optional[str] = Field(default=None, description="Gemini API host")
    instructions: Optional[str] = Field(default=None, description="System instructions")
    transcribe_agent: Optional[bool] = Field(default=None, description="Transcribe agent speech")
    transcribe_user: Optional[bool] = Field(default=None, description="Transcribe user speech")
    affective_dialog: Optional[bool] = Field(default=None, description="Enable affective dialog")
    proactive_audio: Optional[bool] = Field(default=None, description="Enable proactive audio")
    http_options: Optional[Dict[str, Any]] = Field(default=None, description="HTTP options")
    greeting: Optional[str] = Field(
        default=None,
        description=(
            "Agent greeting, serialized to `greeting`. The preview Gemini models "
            "read this spelling, not the `greeting_message` the production "
            "providers use."
        ),
    )
    failure_message: Optional[str] = Field(default=None, description="Message played on failure")
    input_modalities: Optional[List[str]] = Field(default=None, description="Input modalities")
    output_modalities: Optional[List[str]] = Field(default=None, description="Output modalities")
    messages: Optional[List[Dict[str, Any]]] = Field(default=None, description="Conversation messages")
    additional_params: Optional[Dict[str, Any]] = Field(default=None)
    turn_detection: Optional[MllmTurnDetectionConfig] = Field(default=None)

    #: Set by each concrete subclass.
    _default_model: str = ""

    def _model_params(self) -> Dict[str, Any]:
        """Model-specific params merged after ``voice``."""
        return {}

    def to_config(self) -> Dict[str, Any]:
        model = self.model if self.model is not None else self._default_model
        voice = self.voice if self.voice is not None else "Puck"
        url = self.url if self.url is not None else GEMINI_PREVIEW_MLLM_URL

        params: Dict[str, Any] = dict(self.additional_params or {})
        params["api_key"] = self.api_key
        params["model"] = model
        params["voice"] = voice
        params.update(self._model_params())
        # Plural array, and omitted when unset. The singular ``params.language``
        # belongs to xAI Grok in the Agora schema, and the production Gemini Live
        # provider sends no language field at all.
        if self.language_codes is not None:
            params["language_codes"] = list(self.language_codes)

        if self.instructions is not None:
            params["instructions"] = self.instructions
        if self.transcribe_agent is not None:
            params["transcribe_agent"] = self.transcribe_agent
        if self.transcribe_user is not None:
            params["transcribe_user"] = self.transcribe_user
        if self.affective_dialog is not None:
            params["affective_dialog"] = self.affective_dialog
        if self.proactive_audio is not None:
            params["proactive_audio"] = self.proactive_audio
        if self.http_options is not None:
            params["http_options"] = self.http_options

        config: Dict[str, Any] = {
            "vendor": "gemini",
            "api_key": self.api_key,
            "url": url,
            "params": params,
        }
        if self.messages is not None:
            config["messages"] = self.messages
        # ``greeting``, not ``greeting_message``: the preview Gemini models read
        # this spelling. See the preview-endpoint guide.
        if self.greeting is not None:
            config["greeting"] = self.greeting
        if self.failure_message is not None:
            config["failure_message"] = self.failure_message
        if self.input_modalities is not None:
            config["input_modalities"] = self.input_modalities
        if self.output_modalities is not None:
            config["output_modalities"] = self.output_modalities
        if self.turn_detection is not None:
            config["turn_detection"] = self.turn_detection

        return config


class GeminiWalkieTalkie(_GeminiPreviewMLLM):
    """Gemini walkie-talkie MLLM (preview)."""

    _default_model: str = GEMINI_PREVIEW_MLLM_DEFAULTS["walkie_talkie"]


class GeminiCleverChatter(_GeminiPreviewMLLM):
    """Gemini clever-chatter MLLM (preview).

    ``thinking_level`` is exclusive to this model — it is a separate class
    rather than a flag on the walkie-talkie so the distinction is structural.
    """

    thinking_level: Optional[GeminiThinkingLevel] = Field(
        default=None, description="Reasoning budget: low, medium, or high"
    )

    _default_model: str = GEMINI_PREVIEW_MLLM_DEFAULTS["clever_chatter"]

    def _model_params(self) -> Dict[str, Any]:
        return {} if self.thinking_level is None else {"thinking_level": self.thinking_level}


__all__ = [
    "GEMINI_PREVIEW_MLLM_DEFAULTS",
    "GEMINI_PREVIEW_MLLM_URL",
    "GEMINI_THINKING_LEVELS",
    "GeminiCleverChatter",
    "GeminiPreviewMllmModels",
    "GeminiThinkingLevel",
    "GeminiWalkieTalkie",
]
