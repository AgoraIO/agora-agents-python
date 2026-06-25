from __future__ import annotations

import typing
import typing_extensions

from ...core.domain import Area

AreaScope = typing_extensions.Literal["cn", "global"]

CN_AREAS = {Area.CN}

CN_ASR_VENDORS: typing.Tuple[str, ...] = (
    "fengming",
    "tencent",
    "microsoft",
    "xfyun",
    "xfyun_bigmodel",
    "xfyun_dialect",
)
GLOBAL_ASR_VENDORS: typing.Tuple[str, ...] = (
    "ares",
    "deepgram",
    "microsoft",
    "openai",
    "google",
    "amazon",
    "assemblyai",
    "speechmatics",
    "sarvam",
    "xai",
)

CN_TTS_VENDORS: typing.Tuple[str, ...] = (
    "minimax",
    "tencent",
    "bytedance",
    "microsoft",
    "cosyvoice",
    "bytedance_duplex",
    "stepfun",
    "generic",
)
GLOBAL_TTS_VENDORS: typing.Tuple[str, ...] = (
    "microsoft",
    "elevenlabs",
    "minimax",
    "murf",
    "cartesia",
    "openai",
    "humeai",
    "rime",
    "fishaudio",
    "google",
    "amazon",
    "sarvam",
    "generic",
    "xai",
    "deepgram",
)

CN_LLM_VENDORS: typing.Tuple[str, ...] = (
    "aliyun",
    "bytedance",
    "deepseek",
    "tencent",
)
GLOBAL_LLM_VENDORS: typing.Tuple[str, ...] = (
    "openai",
    "azure",
    "anthropic",
    "gemini",
    "groq",
    "vertexai",
    "bedrock",
    "dify",
    "custom",
)

CN_AVATAR_VENDORS: typing.Tuple[str, ...] = ("sensetime", "spatius")
GLOBAL_AVATAR_VENDORS: typing.Tuple[str, ...] = (
    "akool",
    "liveavatar",
    "anam",
    "generic",
    "heygen",
)


def area_to_scope(area: Area) -> AreaScope:
    return "cn" if area in CN_AREAS else "global"


def allowed_vendors_for_scope(scope: AreaScope) -> typing.Dict[str, typing.Tuple[str, ...]]:
    if scope == "cn":
        return {
            "asr": CN_ASR_VENDORS,
            "tts": CN_TTS_VENDORS,
            "llm": CN_LLM_VENDORS,
            "avatar": CN_AVATAR_VENDORS,
        }
    return {
        "asr": GLOBAL_ASR_VENDORS,
        "tts": GLOBAL_TTS_VENDORS,
        "llm": GLOBAL_LLM_VENDORS,
        "avatar": GLOBAL_AVATAR_VENDORS,
    }
