from __future__ import annotations

import typing
from .agent import Agent
from .vendors.base import BaseAvatar, BaseLLM, BaseMLLM, BaseSTT, BaseTTS
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
    XaiSTT,
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
from .vendors.mllm import AzureOpenAIRealtime, GeminiLive, OpenAIRealtime, VertexAI, XaiGrok
from .vendors.tts import (
    AmazonTTS,
    CartesiaTTS,
    DeepgramTTS,
    ElevenLabsTTS,
    FishAudioTTS,
    GoogleTTS,
    GradiumTTS,
    HumeAITTS,
    MicrosoftTTS,
    MiniMaxTTS,
    MistralTTS,
    MurfTTS,
    OpenAITTS,
    GenericTTS,
    RimeTTS,
    SarvamTTS,
    TypecastTTS,
    XaiTTS,
)
from .vendors.avatar import AkoolAvatar, AnamAvatar, GenericAvatar, HeyGenAvatar, LiveAvatarAvatar

CNSTT = typing.Union[TencentSTT, FengmingSTT, MicrosoftCNSTT, XfyunSTT, XfyunBigModelSTT, XfyunDialectSTT]
CNTTS = typing.Union[MiniMaxCNTTS, TencentTTS, BytedanceTTS, MicrosoftCNTTS, CosyVoiceTTS, BytedanceDuplexTTS, StepFunTTS, GenericTTS]
CNLLM = typing.Union[AliyunLLM, BytedanceLLM, DeepSeekLLM, TencentLLM]
CNMLLM = QwenOmni
CNAvatar = typing.Union[SenseTimeAvatar, SpatiusAvatar]

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
    XaiSTT,
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
    GenericTTS,
    XaiTTS,
    DeepgramTTS,
    GradiumTTS,
    MistralTTS,
    TypecastTTS,
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
GlobalMLLM = typing.Union[OpenAIRealtime, AzureOpenAIRealtime, GeminiLive, VertexAI, XaiGrok]
GlobalAvatar = typing.Union[AkoolAvatar, LiveAvatarAvatar, AnamAvatar, GenericAvatar, HeyGenAvatar]


class CNAgent(Agent):
    def with_stt(self, vendor: BaseSTT) -> "CNAgent":
        return typing.cast("CNAgent", super().with_stt(vendor))

    def with_llm(self, vendor: BaseLLM) -> "CNAgent":
        return typing.cast("CNAgent", super().with_llm(vendor))

    def with_tts(self, vendor: BaseTTS) -> "CNAgent":
        return typing.cast("CNAgent", super().with_tts(vendor))

    def with_mllm(self, vendor: BaseMLLM) -> "CNAgent":
        return typing.cast("CNAgent", super().with_mllm(vendor))

    def with_avatar(self, vendor: BaseAvatar) -> "CNAgent":
        return typing.cast("CNAgent", super().with_avatar(vendor))


class GlobalAgent(Agent):
    def with_stt(self, vendor: BaseSTT) -> "GlobalAgent":
        return typing.cast("GlobalAgent", super().with_stt(vendor))

    def with_llm(self, vendor: BaseLLM) -> "GlobalAgent":
        return typing.cast("GlobalAgent", super().with_llm(vendor))

    def with_tts(self, vendor: BaseTTS) -> "GlobalAgent":
        return typing.cast("GlobalAgent", super().with_tts(vendor))

    def with_mllm(self, vendor: BaseMLLM) -> "GlobalAgent":
        return typing.cast("GlobalAgent", super().with_mllm(vendor))

    def with_avatar(self, vendor: BaseAvatar) -> "GlobalAgent":
        return typing.cast("GlobalAgent", super().with_avatar(vendor))


RegionalAgent = typing.Union[CNAgent, GlobalAgent]
