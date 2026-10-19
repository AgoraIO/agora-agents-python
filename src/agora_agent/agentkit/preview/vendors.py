"""Compatibility aliases for preview-era provider imports."""

from ..vendors.mllm import (
    GEMINI_MLLM_DEFAULT_MODEL,
    GEMINI_MLLM_URL,
    GEMINI_THINKING_LEVELS,
    GeminiLive,
    GeminiLiveModels,
    GeminiThinkingLevel,
    OpenAIGPTLive,
)
from ..vendors.stt import GeminiSTT, GeminiSTTModels

# Deprecated name retained for callers that imported the preview endpoint URL.
GEMINI_PREVIEW_MLLM_URL = GEMINI_MLLM_URL


def build_gemini_preview_config(vendor: GeminiLive):
    """Deprecated compatibility wrapper for the production serializer."""
    return vendor.to_config()


__all__ = [
    "OpenAIGPTLive",
    "GEMINI_MLLM_DEFAULT_MODEL",
    "GEMINI_PREVIEW_MLLM_URL",
    "GEMINI_THINKING_LEVELS",
    "GeminiLiveModels",
    "build_gemini_preview_config",
    "GeminiThinkingLevel",
    "GeminiLive",
    "GeminiSTTModels",
    "GeminiSTT",
]
