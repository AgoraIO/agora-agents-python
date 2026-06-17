from __future__ import annotations

import typing
from .agent import Agent
from .vendors.base import BaseAvatar, BaseLLM, BaseSTT, BaseTTS
from .vendors.cn import (
    AliyunLLM,
    BytedanceDuplexTTS,
    BytedanceLLM,
    BytedanceTTS,
    CosyVoiceTTS,
    DeepSeekLLM,
    FengmingSTT,
    MiniMaxTTS as MiniMaxCNTTS,
    MicrosoftSTT as MicrosoftCNSTT,
    MicrosoftTTS as MicrosoftCNTTS,
    SenseTimeAvatar,
    StepFunTTS,
    TencentLLM,
    TencentSTT,
    TencentTTS,
    XfyunBigModelSTT,
    XfyunDialectSTT,
    XfyunSTT,
)
from .vendors.stt import (
    AmazonSTT,
    AresSTT,
    AssemblyAISTT,
    DeepgramSTT,
    GoogleSTT,
    MicrosoftSTT,
    OpenAISTT,
    SarvamSTT,
    SpeechmaticsSTT,
)
from .vendors.llm import (
    AmazonBedrock,
    Anthropic,
    AzureOpenAI,
    CustomLLM,
    Dify,
    Gemini,
    Groq,
    OpenAI,
    VertexAILLM,
)
from .vendors.tts import (
    AmazonTTS,
    CartesiaTTS,
    DeepgramTTS,
    ElevenLabsTTS,
    FishAudioTTS,
    GoogleTTS,
    HumeAITTS,
    MicrosoftTTS,
    MiniMaxTTS,
    MurfTTS,
    OpenAITTS,
    RimeTTS,
    SarvamTTS,
)
from .vendors.avatar import AkoolAvatar, AnamAvatar, GenericAvatar, HeyGenAvatar, LiveAvatarAvatar

CNSTT = typing.Union[TencentSTT, FengmingSTT, MicrosoftCNSTT, XfyunSTT, XfyunBigModelSTT, XfyunDialectSTT]
CNTTS = typing.Union[MiniMaxCNTTS, TencentTTS, BytedanceTTS, MicrosoftCNTTS, CosyVoiceTTS, BytedanceDuplexTTS, StepFunTTS]
CNLLM = typing.Union[AliyunLLM, BytedanceLLM, DeepSeekLLM, TencentLLM]
CNAvatar = SenseTimeAvatar

GlobalSTT = typing.Union[
    AresSTT,
    DeepgramSTT,
    MicrosoftSTT,
    OpenAISTT,
    GoogleSTT,
    AmazonSTT,
    AssemblyAISTT,
    SpeechmaticsSTT,
    SarvamSTT,
]
GlobalTTS = typing.Union[
    MicrosoftTTS,
    ElevenLabsTTS,
    MiniMaxTTS,
    MurfTTS,
    CartesiaTTS,
    OpenAITTS,
    HumeAITTS,
    RimeTTS,
    FishAudioTTS,
    GoogleTTS,
    AmazonTTS,
    SarvamTTS,
    DeepgramTTS,
]
GlobalLLM = typing.Union[
    OpenAI,
    AzureOpenAI,
    Anthropic,
    Gemini,
    Groq,
    VertexAILLM,
    AmazonBedrock,
    Dify,
    CustomLLM,
]
GlobalAvatar = typing.Union[AkoolAvatar, LiveAvatarAvatar, AnamAvatar, GenericAvatar, HeyGenAvatar]


class CNAgent(Agent):
    def with_stt(self, vendor: CNSTT) -> "CNAgent":  # type: ignore[override]
        return typing.cast("CNAgent", super().with_stt(typing.cast(BaseSTT, vendor)))

    def with_llm(self, vendor: CNLLM) -> "CNAgent":  # type: ignore[override]
        return typing.cast("CNAgent", super().with_llm(typing.cast(BaseLLM, vendor)))

    def with_tts(self, vendor: CNTTS) -> "CNAgent":  # type: ignore[override]
        return typing.cast("CNAgent", super().with_tts(typing.cast(BaseTTS, vendor)))

    def with_avatar(self, vendor: CNAvatar) -> "CNAgent":  # type: ignore[override]
        return typing.cast("CNAgent", super().with_avatar(typing.cast(BaseAvatar, vendor)))


class GlobalAgent(Agent):
    def with_stt(self, vendor: GlobalSTT) -> "GlobalAgent":  # type: ignore[override]
        return typing.cast("GlobalAgent", super().with_stt(typing.cast(BaseSTT, vendor)))

    def with_llm(self, vendor: GlobalLLM) -> "GlobalAgent":  # type: ignore[override]
        return typing.cast("GlobalAgent", super().with_llm(typing.cast(BaseLLM, vendor)))

    def with_tts(self, vendor: GlobalTTS) -> "GlobalAgent":  # type: ignore[override]
        return typing.cast("GlobalAgent", super().with_tts(typing.cast(BaseTTS, vendor)))

    def with_avatar(self, vendor: GlobalAvatar) -> "GlobalAgent":  # type: ignore[override]
        return typing.cast("GlobalAgent", super().with_avatar(typing.cast(BaseAvatar, vendor)))


RegionalAgent = typing.Union[CNAgent, GlobalAgent]
