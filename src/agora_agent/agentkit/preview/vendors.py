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
    model: Optional[str] = Field(default=None, description="Defaults to gpt-live-1.")
    voice: Optional[str] = Field(default=None, description="Output voice; provider default marin. Custom voice objects require PR #1522; use params after rollout.")
    prompt: Optional[str] = Field(default=None, description="Session instructions.")
    base_url: Optional[str] = Field(default=None, description="Host when url is omitted; default wss://api.openai.com.")
    path: Optional[str] = Field(default=None, description="WebSocket path; default /v1/live/sessions.")
    alpha_selector: Optional[str] = Field(default=None, description="Optional OpenAI-Alpha selector for preview contracts; omitted by default.")
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
            "model": "gpt-live-1",
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
    "GeminiSTTModels",
    "GeminiSTT",
]
