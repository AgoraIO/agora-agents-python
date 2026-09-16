import json
import warnings
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlsplit, urlunsplit

from ...types.llm_tool import LlmTool
from ...types.mllm_turn_detection import MllmTurnDetection
from .base import BaseMLLM, McpServerInput, dump_config_models, ensure_mcp_transport
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing_extensions import Literal

MllmTurnDetectionConfig = MllmTurnDetection
MllmToolInput = Union[Dict[str, Any], LlmTool]


class GeminiLiveModels:
    """Supported Gemini Live model names."""

    LIVE_38 = "models/gemini-3.8-live"
    LIVE_38_EXTENDED_THINKING = "models/gemini-3.8-live-extended-thinking"


GEMINI_MLLM_DEFAULT_MODEL = GeminiLiveModels.LIVE_38
GEMINI_THINKING_LEVELS = ("low", "medium", "high")
GeminiThinkingLevel = Literal["low", "medium", "high"]
GEMINI_MLLM_URL = "https://generativelanguage.googleapis.com"


class OpenAIGPTLive(BaseMLLM):
    """OpenAI GPT Live v3 MLLM configuration."""

    model_config = ConfigDict(extra="forbid")
    api_key: str = Field(..., min_length=1, description="OpenAI API key")
    url: Optional[str] = None
    instructions: Optional[str] = None
    greeting: Optional[str] = None
    failure_message: Optional[str] = None
    input_modalities: Optional[List[str]] = None
    output_modalities: Optional[List[str]] = None
    messages: Optional[List[Dict[str, Any]]] = None
    mcp_servers: Optional[List[McpServerInput]] = None
    tools: Optional[List[MllmToolInput]] = None
    params: Optional[Dict[str, Any]] = None
    input_audio_transcription: Optional[Dict[str, Any]] = None
    turn_detection: Optional[Any] = None
    model: Optional[str] = Field(default=None, description="Defaults to gpt-live-1.")
    voice: Optional[str] = None
    prompt: Optional[str] = None
    base_url: Optional[str] = None
    path: Optional[str] = None
    alpha_selector: Optional[str] = None
    headers: Optional[str] = None
    output_idle_end_ms: Optional[int] = None
    input_idle_end_ms: Optional[int] = None
    output_silence_peak: Optional[int] = None
    output_sample_rate: Optional[int] = None
    output_buffer_ms: Optional[int] = None
    input_batch_ms: Optional[int] = None
    tool_enabled: Optional[bool] = None
    delegation: Optional[Literal["client", "responses"]] = None
    responses_model: Optional[str] = None
    interrupt_on_user_turn: Optional[bool] = None
    session_params: Optional[Dict[str, Any]] = None

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {"model": "gpt-live-1", **(self.params or {})}
        if self.instructions is not None:
            params["prompt"] = self.instructions
        for name in (
            "model", "voice", "prompt", "base_url", "path", "alpha_selector", "headers",
            "output_idle_end_ms", "input_idle_end_ms", "output_silence_peak", "output_sample_rate",
            "output_buffer_ms", "input_batch_ms", "tool_enabled", "delegation", "responses_model",
            "interrupt_on_user_turn", "session_params",
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
        url = self.url or (str(params.get("base_url", "wss://api.openai.com")).rstrip("/") + "/" + str(params.get("path", "/v1/live/sessions")).lstrip("/"))
        try:
            parsed = urlsplit(url)
            hostname = parsed.hostname
        except ValueError as exc:
            raise ValueError("GPT Live url must be a full ws:// or wss:// endpoint") from exc
        if parsed.scheme not in ("ws", "wss") or not hostname:
            raise ValueError("GPT Live url must be a full ws:// or wss:// endpoint")
        if parsed.hostname == "api.openai.com" and parsed.path == "/v1/live":
            url = urlunsplit(parsed._replace(path="/v1/live/sessions"))
        config: Dict[str, Any] = {"vendor": "openai_gpt_live", "api_key": self.api_key, "url": url, "params": params}
        for name in ("failure_message", "input_modalities", "output_modalities", "messages"):
            value = getattr(self, name)
            if value is not None:
                config[name] = value
        if self.greeting is not None:
            config["greeting_message"] = self.greeting
        _add_tool_configs(config, self.mcp_servers, self.tools)
        return config


def _add_tool_configs(
    config: Dict[str, Any],
    mcp_servers: Optional[List[McpServerInput]],
    tools: Optional[List[MllmToolInput]],
) -> None:
    if mcp_servers is not None:
        config["mcp_servers"] = ensure_mcp_transport(mcp_servers)
    if tools is not None:
        config["tools"] = dump_config_models(tools)


class OpenAIRealtimeOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="OpenAI API key")
    model: Optional[str] = Field(default=None, description="Model name (e.g., gpt-4o-realtime-preview)")
    voice: Optional[str] = Field(default=None, description="Voice identifier")
    instructions: Optional[str] = Field(default=None, description="System instructions")
    input_audio_transcription: Optional[Dict[str, Any]] = Field(default=None, description="Audio transcription settings")
    url: str = Field(
        default="wss://api.openai.com/v1/realtime",
        description="OpenAI Realtime WebSocket URL",
    )
    greeting_message: Optional[str] = Field(default=None, description="Agent greeting message")
    input_modalities: Optional[List[str]] = Field(default=None, description="Input modalities")
    output_modalities: Optional[List[str]] = Field(default=None, description="Output modalities")
    messages: Optional[List[Dict[str, Any]]] = Field(default=None, description="Conversation messages")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Additional parameters")
    turn_detection: Optional[MllmTurnDetectionConfig] = Field(default=None, description="MLLM turn detection configuration")
    failure_message: Optional[str] = Field(default=None, description="Message played on failure")
    mcp_servers: Optional[List[McpServerInput]] = Field(default=None)
    tools: Optional[List[MllmToolInput]] = Field(default=None)


class OpenAIRealtime(OpenAIRealtimeOptions, BaseMLLM):
    def to_config(self) -> Dict[str, Any]:
        config: Dict[str, Any] = {
            "vendor": "openai",
            "api_key": self.api_key,
            "url": self.url,
        }

        if (
            self.model is not None
            or self.params is not None
            or self.voice is not None
            or self.instructions is not None
            or self.input_audio_transcription is not None
        ):
            inner_params: Dict[str, Any] = {}
            if self.model is not None:
                inner_params["model"] = self.model
            if self.params is not None:
                inner_params.update(self.params)
            if self.voice is not None:
                inner_params["voice"] = self.voice
            if self.instructions is not None:
                inner_params["instructions"] = self.instructions
            if self.input_audio_transcription is not None:
                inner_params["input_audio_transcription"] = self.input_audio_transcription
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
        _add_tool_configs(config, self.mcp_servers, self.tools)

        return config


class AzureOpenAIRealtimeOptions(BaseModel):
    """Azure OpenAI Realtime MLLM vendor (`mllm.vendor`: ``azure``)."""

    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Azure OpenAI API key")
    url: str = Field(..., description="Azure OpenAI Realtime WebSocket URL")
    model: Optional[str] = Field(default=None, description="Azure OpenAI Realtime model or deployment name")
    voice: Optional[str] = Field(default=None, description="Voice identifier")
    instructions: Optional[str] = Field(default=None, description="System instructions")
    input_audio_transcription: Optional[Dict[str, Any]] = Field(
        default=None, description="Audio transcription settings"
    )
    max_history: Optional[int] = Field(
        default=None, gt=0, description="Number of conversation history messages to cache"
    )
    greeting_message: Optional[str] = Field(default=None, description="Agent greeting message")
    output_modalities: Optional[List[str]] = Field(default=None, description="Output modalities")
    messages: Optional[List[Dict[str, Any]]] = Field(default=None, description="Conversation messages")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Additional Azure OpenAI parameters")
    turn_detection: MllmTurnDetectionConfig = Field(..., description="MLLM turn detection configuration")
    failure_message: Optional[str] = Field(default=None, description="Message played on failure")
    mcp_servers: Optional[List[McpServerInput]] = Field(default=None)
    tools: Optional[List[MllmToolInput]] = Field(default=None)


class AzureOpenAIRealtime(AzureOpenAIRealtimeOptions, BaseMLLM):
    """Azure OpenAI Realtime MLLM vendor (`mllm.vendor`: ``azure``)."""

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
            "vendor": "azure",
            "api_key": self.api_key,
            "url": self.url,
        }
        if inner_params:
            config["params"] = inner_params
        if self.max_history is not None:
            config["max_history"] = self.max_history
        if self.greeting_message is not None:
            config["greeting_message"] = self.greeting_message
        if self.output_modalities is not None:
            config["output_modalities"] = self.output_modalities
        if self.messages is not None:
            config["messages"] = self.messages
        if self.failure_message is not None:
            config["failure_message"] = self.failure_message
        config["turn_detection"] = self.turn_detection
        _add_tool_configs(config, self.mcp_servers, self.tools)
        return config


# xAI MLLM: use XaiGrok (product name, mllm.vendor "xai"). Do not use XaiRealtime—that name
# is deprecated and reserved naming for future XaiSTT / XaiTTS cascading vendors.


class XaiGrokOptions(BaseModel):
    """xAI Grok MLLM vendor (`mllm.vendor`: ``xai``)."""

    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="xAI API key")
    url: str = Field(default="wss://api.x.ai/v1/realtime", description="xAI Realtime WebSocket URL")
    voice: Optional[str] = Field(default=None, description="Voice identifier (e.g., eve or rex)")
    language: Optional[str] = Field(default=None, description="Language code (e.g., en)")
    sample_rate: Optional[int] = Field(default=None, description="Audio sample rate in Hz")
    greeting_message: Optional[str] = Field(default=None, description="Agent greeting message")
    input_modalities: Optional[List[str]] = Field(default=None, description="Input modalities")
    output_modalities: Optional[List[str]] = Field(default=None, description="Output modalities")
    messages: Optional[List[Dict[str, Any]]] = Field(default=None, description="Conversation messages")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Additional xAI parameters")
    turn_detection: Optional[MllmTurnDetectionConfig] = Field(default=None, description="MLLM turn detection configuration")
    failure_message: Optional[str] = Field(default=None, description="Message played on failure")
    mcp_servers: Optional[List[McpServerInput]] = Field(default=None)
    tools: Optional[List[MllmToolInput]] = Field(default=None)


class XaiGrok(XaiGrokOptions, BaseMLLM):
    """xAI Grok MLLM vendor (`mllm.vendor`: ``xai``)."""

    def to_config(self) -> Dict[str, Any]:
        inner_params: Dict[str, Any] = dict(self.params or {})
        if self.voice is not None:
            inner_params["voice"] = self.voice
        if self.language is not None:
            inner_params["language"] = self.language
        if self.sample_rate is not None:
            inner_params["sample_rate"] = self.sample_rate

        config: Dict[str, Any] = {
            "vendor": "xai",
            "api_key": self.api_key,
            "url": self.url,
            "params": inner_params,
        }

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
        _add_tool_configs(config, self.mcp_servers, self.tools)

        return config


class VertexAIOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str = Field(..., description="Model name")
    url: Optional[str] = Field(default=None, description="WebSocket URL")
    project_id: str = Field(..., description="Google Cloud project ID")
    location: str = Field(..., description="Google Cloud location/region")
    adc_credentials_string: str = Field(..., description="Application Default Credentials JSON string")
    instructions: Optional[str] = Field(default=None, description="System instructions")
    voice: Optional[str] = Field(default=None, description="Voice name (e.g., Aoede, Charon)")
    affective_dialog: Optional[bool] = Field(default=None, description="Enable affective dialog")
    proactive_audio: Optional[bool] = Field(default=None, description="Enable proactive audio")
    transcribe_agent: Optional[bool] = Field(default=None, description="Transcribe agent speech")
    transcribe_user: Optional[bool] = Field(default=None, description="Transcribe user speech")
    http_options: Optional[Dict[str, Any]] = Field(default=None, description="HTTP options")
    greeting_message: Optional[str] = Field(default=None, description="Agent greeting message")
    input_modalities: Optional[List[str]] = Field(default=None, description="Input modalities")
    output_modalities: Optional[List[str]] = Field(default=None, description="Output modalities")
    messages: Optional[List[Dict[str, Any]]] = Field(default=None, description="Conversation messages")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional parameters")
    turn_detection: Optional[MllmTurnDetectionConfig] = Field(default=None, description="MLLM turn detection configuration")
    failure_message: Optional[str] = Field(default=None, description="Message played on failure")
    mcp_servers: Optional[List[McpServerInput]] = Field(default=None)
    tools: Optional[List[MllmToolInput]] = Field(default=None)


class VertexAI(VertexAIOptions, BaseMLLM):
    def to_config(self) -> Dict[str, Any]:
        # additional_params spread first so that explicit fields always win,
        # matching the TypeScript SDK.
        inner_params: Dict[str, Any] = dict(self.additional_params or {})
        inner_params["model"] = self.model
        inner_params["project_id"] = self.project_id
        inner_params["location"] = self.location
        inner_params["adc_credentials_string"] = self.adc_credentials_string
        if self.instructions is not None:
            inner_params["instructions"] = self.instructions
        if self.voice is not None:
            inner_params["voice"] = self.voice
        if self.affective_dialog is not None:
            inner_params["affective_dialog"] = self.affective_dialog
        if self.proactive_audio is not None:
            inner_params["proactive_audio"] = self.proactive_audio
        if self.transcribe_agent is not None:
            inner_params["transcribe_agent"] = self.transcribe_agent
        if self.transcribe_user is not None:
            inner_params["transcribe_user"] = self.transcribe_user
        if self.http_options is not None:
            inner_params["http_options"] = self.http_options

        config: Dict[str, Any] = {
            "vendor": "vertexai",
            "url": self.url if self.url is not None else "",
            "params": inner_params,
        }
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
        _add_tool_configs(config, self.mcp_servers, self.tools)

        return config


class GeminiLiveOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Google API key")
    model: str = Field(default="models/gemini-3.8-live", description="Gemini Live model name")
    thinking_level: Optional[GeminiThinkingLevel] = Field(
        default=None, description="Reasoning budget for the 3.8 extended-thinking model"
    )
    language_codes: Optional[List[str]] = Field(default=None, description="Languages for Gemini 3.8")
    url: Optional[str] = Field(default=None, description="Endpoint override; Gemini 3.8 defaults to the Developer API host")
    instructions: Optional[str] = Field(default=None, description="System instructions")
    voice: Optional[str] = Field(default=None, description="Voice name")
    affective_dialog: Optional[bool] = Field(default=None, description="Enable affective dialog")
    proactive_audio: Optional[bool] = Field(default=None, description="Enable proactive audio")
    transcribe_agent: Optional[bool] = Field(default=None, description="Transcribe agent speech")
    transcribe_user: Optional[bool] = Field(default=None, description="Transcribe user speech")
    http_options: Optional[Dict[str, Any]] = Field(default=None, description="HTTP options")
    greeting_message: Optional[str] = Field(default=None, description="Agent greeting message")
    input_modalities: Optional[List[str]] = Field(default=None, description="Input modalities")
    output_modalities: Optional[List[str]] = Field(default=None, description="Output modalities")
    messages: Optional[List[Dict[str, Any]]] = Field(default=None, description="Conversation messages")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional parameters")
    turn_detection: Optional[MllmTurnDetectionConfig] = Field(default=None, description="MLLM turn detection configuration")
    failure_message: Optional[str] = Field(default=None, description="Message played on failure")
    mcp_servers: Optional[List[McpServerInput]] = Field(default=None)
    tools: Optional[List[MllmToolInput]] = Field(default=None)

    @field_validator("api_key")
    @classmethod
    def _validate_api_key(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("GeminiLive requires api_key")
        return value


class GeminiLive(GeminiLiveOptions, BaseMLLM):
    def to_config(self) -> Dict[str, Any]:
        selected_model = self.model.strip() or GEMINI_MLLM_DEFAULT_MODEL
        inner_params: Dict[str, Any] = dict(self.additional_params or {})
        inner_params["model"] = selected_model
        if selected_model in (GeminiLiveModels.LIVE_38, GeminiLiveModels.LIVE_38_EXTENDED_THINKING):
            inner_params.pop("api_key", None)
            inner_params["voice"] = self.voice if self.voice is not None else "Puck"
            if self.language_codes is not None:
                inner_params["language_codes"] = list(self.language_codes)
            if selected_model == GeminiLiveModels.LIVE_38_EXTENDED_THINKING:
                if self.thinking_level is not None:
                    inner_params["thinking_level"] = self.thinking_level
            else:
                inner_params.pop("thinking_level", None)
        if self.instructions is not None:
            inner_params["instructions"] = self.instructions
        if self.voice is not None and selected_model not in (
            GeminiLiveModels.LIVE_38,
            GeminiLiveModels.LIVE_38_EXTENDED_THINKING,
        ):
            inner_params["voice"] = self.voice
        if self.affective_dialog is not None:
            inner_params["affective_dialog"] = self.affective_dialog
        if self.proactive_audio is not None:
            inner_params["proactive_audio"] = self.proactive_audio
        if self.transcribe_agent is not None:
            inner_params["transcribe_agent"] = self.transcribe_agent
        if self.transcribe_user is not None:
            inner_params["transcribe_user"] = self.transcribe_user
        if self.http_options is not None:
            inner_params["http_options"] = self.http_options

        config: Dict[str, Any] = {
            "vendor": "gemini",
            "api_key": self.api_key,
            "url": self.url if self.url is not None else (
                GEMINI_MLLM_URL
                if selected_model in (GeminiLiveModels.LIVE_38, GeminiLiveModels.LIVE_38_EXTENDED_THINKING)
                else ""
            ),
            "params": inner_params,
        }
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
        _add_tool_configs(config, self.mcp_servers, self.tools)

        return config
