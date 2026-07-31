# isort: skip_file
"""China (CN) vendor classes for the Agora Conversational AI SDK.

Import CN vendors explicitly from this module so they stay separate from the global
top-level namespace::

    from agora_agent.cn import AliyunLLM, MiniMaxTTS, QwenOmni, TencentSTT

``MicrosoftSTT`` / ``MicrosoftTTS`` / ``MiniMaxTTS`` here are the CN variants; the
global variants of those names are available from the top-level package
(e.g. ``from agora_agent import MiniMaxTTS``).
"""

from .agentkit.vendors.cn import (
    AliyunLLM,
    BytedanceDuplexTTS,
    BytedanceLLM,
    BytedanceTTS,
    CosyVoiceTTS,
    DeepSeekLLM,
    FengmingSTT,
    MicrosoftSTT,
    MicrosoftTTS,
    MiniMaxTTS,
    QwenOmni,
    SenseTimeAvatar,
    SpatiusAvatar,
    StepFunTTS,
    TencentLLM,
    TencentSTT,
    TencentTTS,
    XfyunBigModelSTT,
    XfyunDialectSTT,
    XfyunSTT,
)

__all__ = [
    # STT
    "FengmingSTT",
    "MicrosoftSTT",
    "TencentSTT",
    "XfyunBigModelSTT",
    "XfyunDialectSTT",
    "XfyunSTT",
    # TTS
    "BytedanceDuplexTTS",
    "BytedanceTTS",
    "CosyVoiceTTS",
    "MicrosoftTTS",
    "MiniMaxTTS",
    "StepFunTTS",
    "TencentTTS",
    # LLM
    "AliyunLLM",
    "BytedanceLLM",
    "DeepSeekLLM",
    "TencentLLM",
    # MLLM
    "QwenOmni",
    # Avatar
    "SenseTimeAvatar",
    "SpatiusAvatar",
]
