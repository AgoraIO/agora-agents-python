from typing import Any, Dict, List, Optional

from pydantic import ConfigDict, Field

from ...types.mllm_turn_detection import MllmTurnDetection
from .base import BaseMLLM

MllmTurnDetectionConfig = MllmTurnDetection


class OpenAIRealtime(BaseMLLM):
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

        return config


# xAI MLLM: use XaiGrok (product name, mllm.vendor "xai"). Do not use XaiRealtime—that name
# is deprecated and reserved naming for future XaiSTT / XaiTTS cascading vendors.


class XaiGrok(BaseMLLM):
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

        return config


class VertexAI(BaseMLLM):
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

        return config


class GeminiLive(BaseMLLM):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Google API key")
    model: str = Field(..., description="Gemini Live model name")
    url: Optional[str] = Field(default=None, description="WebSocket URL")
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

    def to_config(self) -> Dict[str, Any]:
        inner_params: Dict[str, Any] = {}
        if self.additional_params is not None:
            inner_params.update(self.additional_params)
        inner_params["model"] = self.model
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
            "vendor": "gemini",
            "api_key": self.api_key,
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

        return config
