"""Preview provider vendor classes.

These follow the same shape as the GA vendor classes in ``vendors/`` — snake_case
constructor options in, snake_case wire config out — so they work with the
corresponding ``Agent`` builder method. Sessions that use a preview-only vendor
route to the preview endpoint automatically.
"""

import json
import warnings
from typing import Any, Dict, List, Optional
from urllib.parse import urlsplit, urlunsplit

from ..vendors.base import BaseMLLM, ensure_mcp_transport
from ..vendors.mllm import MllmTurnDetectionConfig
from ..vendors.stt import GeminiSTT, GeminiSTTModels
from pydantic import ConfigDict, Field
from typing_extensions import Literal

_OpenAIApiKey = Field(..., min_length=1, description="OpenAI API key")


class OpenAIGPTLive(BaseMLLM):
    """GPT Live v3 alpha configuration. Not for production traffic.

    Explicit options override params. Unset tuning options retain provider defaults.
    instructions is a compatibility alias for prompt; prompt takes precedence.
    """

    model_config = ConfigDict(extra="forbid")
    api_key: str = _OpenAIApiKey
    url: Optional[str] = None
    instructions: Optional[str] = None
    greeting: Optional[str] = None
    failure_message: Optional[str] = None
    input_modalities: Optional[List[str]] = None
    output_modalities: Optional[List[str]] = None
    messages: Optional[List[Dict[str, Any]]] = None
    mcp_servers: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="MCP servers exposed to GPT Live. Requires Agent.with_tools().",
    )
    params: Optional[Dict[str, Any]] = None
    # Legacy options retained to diagnose unsupported v2 configuration.
    input_audio_transcription: Optional[Dict[str, Any]] = None
    turn_detection: Optional[Any] = None
    model: Optional[str] = Field(default=None, description="Defaults to gpt-live-1-diamond-alpha.")
    voice: Optional[str] = Field(default=None, description="Output voice; provider default marin. Custom voice objects require PR #1522; use params after rollout.")
    prompt: Optional[str] = Field(default=None, description="Session instructions.")
    base_url: Optional[str] = Field(default=None, description="Host when url is omitted; default wss://api.openai.com.")
    path: Optional[str] = Field(default=None, description="WebSocket path; default /v1/live/sessions.")
    alpha_selector: Optional[str] = Field(default=None, description="OpenAI-Alpha selector. Defaults to the required GPT Live v3 contract.")
    headers: Optional[str] = Field(default=None, description="Extra provider request headers as a JSON string; protocol headers win.")
    output_idle_end_ms: Optional[int] = Field(default=None, description="Assistant silence boundary in ms; provider default 600. Zero disables inference.")
    input_idle_end_ms: Optional[int] = Field(default=None, description="Caller silence boundary in ms; provider default 1500.")
    output_silence_peak: Optional[int] = Field(default=None, description="Speech amplitude threshold on the 16-bit scale; provider default 50.")
    output_sample_rate: Optional[int] = Field(default=None, description="Graph PCM sample rate; provider default 24000.")
    output_buffer_ms: Optional[int] = Field(default=None, description="Initial audio cushion; provider default 0. Negative disables pacing.")
    input_batch_ms: Optional[int] = Field(default=None, description="Mic append batching in ms. Join default 0; extension class default 100.")
    tool_enabled: Optional[bool] = Field(default=None, description="Advertise graph tools; provider default false. Does not control delegate built-ins.")
    delegation: Optional[Literal["client", "responses"]] = Field(default=None, description="Tool delegation mode; provider default responses. Fixed for the session.")
    responses_model: Optional[str] = Field(default=None, description="Tool delegate model; provider default gpt-5.6-sol.")
    interrupt_on_user_turn: Optional[bool] = Field(default=None, description="Interrupt playback on caller speech; provider default false.")
    session_params: Optional[Dict[str, Any]] = Field(default=None, description="Unmodelled v3 session fields. Cannot override model, delegation, audio, instructions or input.")

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "model": "gpt-live-1-diamond-alpha",
            "alpha_selector": "quicksilver=v3",
            **(self.params or {}),
        }
        if self.instructions is not None:
            params["prompt"] = self.instructions
        for name in (
            "model",
            "voice",
            "prompt",
            "base_url",
            "path",
            "alpha_selector",
            "headers",
            "output_idle_end_ms",
            "input_idle_end_ms",
            "output_silence_peak",
            "output_sample_rate",
            "output_buffer_ms",
            "input_batch_ms",
            "tool_enabled",
            "delegation",
            "responses_model",
            "interrupt_on_user_turn",
            "session_params",
        ):
            value = getattr(self, name)
            if value is not None:
                params[name] = value
        if self.input_audio_transcription is not None or "input_audio_transcription" in params:
            raise ValueError("GPT Live v3 does not support input_audio_transcription")
        if self.turn_detection is not None or "turn_detection" in params:
            warnings.warn("GPT Live v3 ignores turn_detection; endpointing is internal", UserWarning, stacklevel=2)
            params.pop("turn_detection", None)
        if "delegation" in params and params["delegation"] not in ("client", "responses"):
            raise ValueError("GPT Live delegation must be client or responses")
        if "headers" in params:
            try:
                headers = json.loads(params["headers"])
            except (TypeError, ValueError) as exc:
                raise ValueError("GPT Live headers must be a JSON object string") from exc
            if not isinstance(headers, dict):
                raise ValueError("GPT Live headers must be a JSON object string")
        session = params.get("session_params", {})
        if not isinstance(session, dict):
            raise ValueError("GPT Live session_params must be an object")
        for name in ("model", "delegation", "audio", "instructions", "input"):
            if name in session:
                raise ValueError(f"GPT Live session_params cannot override {name}")
        url = self.url or (
            str(params.get("base_url", "wss://api.openai.com")).rstrip("/")
            + "/" + str(params.get("path", "/v1/live/sessions")).lstrip("/")
        )
        try:
            parsed = urlsplit(url)
            hostname = parsed.hostname
        except ValueError as exc:
            raise ValueError("GPT Live url must be a full ws:// or wss:// endpoint") from exc
        if parsed.scheme not in ("ws", "wss") or not hostname:
            raise ValueError("GPT Live url must be a full ws:// or wss:// endpoint")
        if parsed.hostname == "api.openai.com" and parsed.path == "/v1/live":
            url = urlunsplit(parsed._replace(path="/v1/live/sessions"))
        config: Dict[str, Any] = {
            "vendor": "openai_gpt_live", "api_key": self.api_key, "url": url, "params": params,
        }
        for name in ("failure_message", "input_modalities", "output_modalities", "messages"):
            value = getattr(self, name)
            if value is not None:
                config[name] = value
        if self.greeting is not None:
            config["greeting_message"] = self.greeting
        if self.mcp_servers is not None:
            config["mcp_servers"] = ensure_mcp_transport(self.mcp_servers)
        return config


__all__ = [
    "OpenAIGPTLive",
    "GEMINI_PREVIEW_MLLM_DEFAULTS",
    "GEMINI_PREVIEW_MLLM_URL",
    "GEMINI_THINKING_LEVELS",
    "GeminiCleverChatter",
    "GeminiPreviewMllmModels",
    "GeminiThinkingLevel",
    "GeminiWalkieTalkie",
    "GeminiSTTModels",
    "GeminiSTT",
]


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
