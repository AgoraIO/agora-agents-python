"""Compatibility aliases for preview-era provider imports."""

from typing import Any, Dict

from ..vendors.mllm import OpenAIGPTLive
from ..vendors.stt import GeminiSTT, GeminiSTTModels
from typing_extensions import Literal

__all__ = [
    "OpenAIGPTLive",
    "GEMINI_MLLM_DEFAULT_MODEL",
    "GEMINI_PREVIEW_MLLM_URL",
    "GEMINI_THINKING_LEVELS",
    "GeminiLiveModels",
    "build_gemini_preview_config",
    "GeminiThinkingLevel",
    "GeminiSTTModels",
    "GeminiSTT",
]


class GeminiLiveModels:
    """Preview MLLM model names.

    The ``models/`` prefix is part of each model ID.
    """

    LIVE_38 = "models/gemini-3.8-live"
    LIVE_38_EXTENDED_THINKING = "models/gemini-3.8-live-extended-thinking"


#: The model name the Gemini MLLM sends by default.
#:
#: Low-latency Gemini voice is the default.
GEMINI_MLLM_DEFAULT_MODEL = GeminiLiveModels.LIVE_38


GEMINI_THINKING_LEVELS = ("low", "medium", "high")

GeminiThinkingLevel = Literal["low", "medium", "high"]

#: The preview MLLM talks to the Gemini Developer API rather than a WebSocket host.
GEMINI_PREVIEW_MLLM_URL = "https://generativelanguage.googleapis.com"


def build_gemini_preview_config(self: Any) -> Dict[str, Any]:
    """Serialize GeminiLive options for the Gemini 3.8 preview gateway."""
    model = (self.model or "").strip() or GEMINI_MLLM_DEFAULT_MODEL
    voice = self.voice if self.voice is not None else "Puck"
    url = self.url if self.url is not None else GEMINI_PREVIEW_MLLM_URL

    params: Dict[str, Any] = dict(self.additional_params or {})
    params.pop("api_key", None)
    params["model"] = model
    params["voice"] = voice
    if model == GeminiLiveModels.LIVE_38_EXTENDED_THINKING:
        if self.thinking_level is not None:
            params["thinking_level"] = self.thinking_level
    else:
        params.pop("thinking_level", None)
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
    if self.greeting_message is not None:
        config["greeting"] = self.greeting_message
    if self.failure_message is not None:
        config["failure_message"] = self.failure_message
    if self.input_modalities is not None:
        config["input_modalities"] = self.input_modalities
    if self.output_modalities is not None:
        config["output_modalities"] = self.output_modalities
    if self.turn_detection is not None:
        config["turn_detection"] = self.turn_detection

    return config
