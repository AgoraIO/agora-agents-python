import warnings
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from ...agents.types.start_agents_request_properties_mllm_turn_detection import (
    StartAgentsRequestPropertiesMllmTurnDetection,
)
from .base import BaseMLLM

MllmTurnDetectionConfig = StartAgentsRequestPropertiesMllmTurnDetection


class OpenAIRealtimeOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="OpenAI API key")
    model: Optional[str] = Field(default=None, description="Model name (e.g., gpt-4o-realtime-preview)")
    url: Optional[str] = Field(default=None, description="WebSocket URL")
    greeting_message: Optional[str] = Field(default=None, description="Agent greeting message")
    input_modalities: Optional[List[str]] = Field(default=None, description="Input modalities")
    output_modalities: Optional[List[str]] = Field(default=None, description="Output modalities")
    messages: Optional[List[Dict[str, Any]]] = Field(default=None, description="Conversation messages")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Additional parameters")
    turn_detection: Optional[MllmTurnDetectionConfig] = Field(default=None, description="MLLM turn detection configuration")
    failure_message: Optional[str] = Field(default=None, description="Message played on failure")

class OpenAIRealtime(BaseMLLM):
    def __init__(self, **kwargs: Any):
        self.options = OpenAIRealtimeOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        config: Dict[str, Any] = {
            "vendor": "openai",
            "api_key": self.options.api_key,
        }

        if self.options.url is not None:
            config["url"] = self.options.url
        if self.options.model is not None:
            params = {"model": self.options.model}
            if self.options.params is not None:
                params.update(self.options.params)
            config["params"] = params
        elif self.options.params is not None:
            config["params"] = self.options.params
        if self.options.greeting_message is not None:
            config["greeting_message"] = self.options.greeting_message
        if self.options.input_modalities is not None:
            config["input_modalities"] = self.options.input_modalities
        if self.options.output_modalities is not None:
            config["output_modalities"] = self.options.output_modalities
        if self.options.messages is not None:
            config["messages"] = self.options.messages
        if self.options.failure_message is not None:
            config["failure_message"] = self.options.failure_message
        if self.options.turn_detection is not None:
            config["turn_detection"] = self.options.turn_detection

        return config


# xAI MLLM: use XaiGrok (product name, mllm.vendor "xai"). Do not use XaiRealtime—that name
# is deprecated and reserved naming for future XaiSTT / XaiTTS cascading vendors.


class XaiGrokOptions(BaseModel):
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


class XaiGrok(BaseMLLM):
    """xAI Grok MLLM vendor (`mllm.vendor`: ``xai``)."""

    def __init__(self, **kwargs: Any):
        self.options = XaiGrokOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.options.params or {})
        if self.options.voice is not None:
            params["voice"] = self.options.voice
        if self.options.language is not None:
            params["language"] = self.options.language
        if self.options.sample_rate is not None:
            params["sample_rate"] = self.options.sample_rate

        config: Dict[str, Any] = {
            "vendor": "xai",
            "api_key": self.options.api_key,
            "url": self.options.url,
            "params": params,
        }

        if self.options.greeting_message is not None:
            config["greeting_message"] = self.options.greeting_message
        if self.options.input_modalities is not None:
            config["input_modalities"] = self.options.input_modalities
        if self.options.output_modalities is not None:
            config["output_modalities"] = self.options.output_modalities
        if self.options.messages is not None:
            config["messages"] = self.options.messages
        if self.options.failure_message is not None:
            config["failure_message"] = self.options.failure_message
        if self.options.turn_detection is not None:
            config["turn_detection"] = self.options.turn_detection

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
    greeting_message: Optional[str] = Field(default=None, description="Agent greeting message")
    input_modalities: Optional[List[str]] = Field(default=None, description="Input modalities")
    output_modalities: Optional[List[str]] = Field(default=None, description="Output modalities")
    messages: Optional[List[Dict[str, Any]]] = Field(default=None, description="Conversation messages")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional parameters")
    turn_detection: Optional[MllmTurnDetectionConfig] = Field(default=None, description="MLLM turn detection configuration")
    failure_message: Optional[str] = Field(default=None, description="Message played on failure")

class VertexAI(BaseMLLM):
    def __init__(self, **kwargs: Any):
        self.options = VertexAIOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        # additional_params spread first so that explicit fields always win,
        # matching the TypeScript SDK.
        params: Dict[str, Any] = dict(self.options.additional_params or {})
        params["model"] = self.options.model
        params["project_id"] = self.options.project_id
        params["location"] = self.options.location
        params["adc_credentials_string"] = self.options.adc_credentials_string
        if self.options.instructions is not None:
            params["instructions"] = self.options.instructions
        if self.options.voice is not None:
            params["voice"] = self.options.voice

        config: Dict[str, Any] = {
            "vendor": "vertexai",
            "params": params,
        }

        if self.options.url is not None:
            config["url"] = self.options.url
        if self.options.greeting_message is not None:
            config["greeting_message"] = self.options.greeting_message
        if self.options.input_modalities is not None:
            config["input_modalities"] = self.options.input_modalities
        if self.options.output_modalities is not None:
            config["output_modalities"] = self.options.output_modalities
        if self.options.messages is not None:
            config["messages"] = self.options.messages
        if self.options.failure_message is not None:
            config["failure_message"] = self.options.failure_message
        if self.options.turn_detection is not None:
            config["turn_detection"] = self.options.turn_detection

        return config


class GeminiLiveOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Google API key")
    model: str = Field(..., description="Gemini Live model name")
    url: Optional[str] = Field(default=None, description="WebSocket URL")
    instructions: Optional[str] = Field(default=None, description="System instructions")
    voice: Optional[str] = Field(default=None, description="Voice name")
    greeting_message: Optional[str] = Field(default=None, description="Agent greeting message")
    input_modalities: Optional[List[str]] = Field(default=None, description="Input modalities")
    output_modalities: Optional[List[str]] = Field(default=None, description="Output modalities")
    messages: Optional[List[Dict[str, Any]]] = Field(default=None, description="Conversation messages")
    additional_params: Optional[Dict[str, Any]] = Field(default=None, description="Additional parameters")
    turn_detection: Optional[MllmTurnDetectionConfig] = Field(default=None, description="MLLM turn detection configuration")
    failure_message: Optional[str] = Field(default=None, description="Message played on failure")

class GeminiLive(BaseMLLM):
    def __init__(self, **kwargs: Any):
        self.options = GeminiLiveOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if self.options.additional_params is not None:
            params.update(self.options.additional_params)
        params["model"] = self.options.model
        if self.options.instructions is not None:
            params["instructions"] = self.options.instructions
        if self.options.voice is not None:
            params["voice"] = self.options.voice

        config: Dict[str, Any] = {
            "vendor": "gemini",
            "api_key": self.options.api_key,
            "params": params,
        }

        if self.options.url is not None:
            config["url"] = self.options.url
        if self.options.greeting_message is not None:
            config["greeting_message"] = self.options.greeting_message
        if self.options.input_modalities is not None:
            config["input_modalities"] = self.options.input_modalities
        if self.options.output_modalities is not None:
            config["output_modalities"] = self.options.output_modalities
        if self.options.messages is not None:
            config["messages"] = self.options.messages
        if self.options.failure_message is not None:
            config["failure_message"] = self.options.failure_message
        if self.options.turn_detection is not None:
            config["turn_detection"] = self.options.turn_detection

        return config
