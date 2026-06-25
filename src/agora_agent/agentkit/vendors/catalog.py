from __future__ import annotations

import typing

from . import cn as cn_vendors
from . import region
from .avatar import AkoolAvatar, AnamAvatar, GenericAvatar, HeyGenAvatar, LiveAvatarAvatar
from .llm import (
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
from .stt import (
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
from .tts import (
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
    GenericTTS,
    RimeTTS,
    SarvamTTS,
    XaiTTS,
)


class VendorNamespace:
    def __init__(
        self,
        *,
        asr: typing.Mapping[str, typing.Any],
        llm: typing.Mapping[str, typing.Any],
        tts: typing.Mapping[str, typing.Any],
        avatar: typing.Mapping[str, typing.Any],
    ) -> None:
        self.asr = dict(asr)
        self.llm = dict(llm)
        self.tts = dict(tts)
        self.avatar = dict(avatar)


GLOBAL_VENDOR_NAMESPACE = VendorNamespace(
    asr={
        "ares": AresSTT,
        "deepgram": DeepgramSTT,
        "microsoft": MicrosoftSTT,
        "openai": OpenAISTT,
        "google": GoogleSTT,
        "amazon": AmazonSTT,
        "assemblyai": AssemblyAISTT,
        "speechmatics": SpeechmaticsSTT,
        "sarvam": SarvamSTT,
        "xai": XaiSTT,
    },
    llm={
        "openai": OpenAI,
        "azure": AzureOpenAI,
        "anthropic": Anthropic,
        "gemini": Gemini,
        "groq": Groq,
        "vertexai": VertexAILLM,
        "bedrock": AmazonBedrock,
        "dify": Dify,
        "custom": CustomLLM,
    },
    tts={
        "microsoft": MicrosoftTTS,
        "elevenlabs": ElevenLabsTTS,
        "minimax": MiniMaxTTS,
        "murf": MurfTTS,
        "cartesia": CartesiaTTS,
        "openai": OpenAITTS,
        "humeai": HumeAITTS,
        "rime": RimeTTS,
        "fishaudio": FishAudioTTS,
        "google": GoogleTTS,
        "amazon": AmazonTTS,
        "sarvam": SarvamTTS,
        "generic": GenericTTS,
        "xai": XaiTTS,
        "deepgram": DeepgramTTS,
    },
    avatar={
        "akool": AkoolAvatar,
        "liveavatar": LiveAvatarAvatar,
        "anam": AnamAvatar,
        "generic": GenericAvatar,
        "heygen": HeyGenAvatar,
    },
)

CN_VENDOR_NAMESPACE = VendorNamespace(
    asr={
        "fengming": cn_vendors.FengmingSTT,
        "tencent": cn_vendors.TencentSTT,
        "microsoft": cn_vendors.MicrosoftSTT,
        "xfyun": cn_vendors.XfyunSTT,
        "xfyun_bigmodel": cn_vendors.XfyunBigModelSTT,
        "xfyun_dialect": cn_vendors.XfyunDialectSTT,
    },
    llm={
        "aliyun": cn_vendors.AliyunLLM,
        "bytedance": cn_vendors.BytedanceLLM,
        "deepseek": cn_vendors.DeepSeekLLM,
        "tencent": cn_vendors.TencentLLM,
    },
    tts={
        "minimax": cn_vendors.MiniMaxTTS,
        "tencent": cn_vendors.TencentTTS,
        "bytedance": cn_vendors.BytedanceTTS,
        "microsoft": cn_vendors.MicrosoftTTS,
        "cosyvoice": cn_vendors.CosyVoiceTTS,
        "bytedance_duplex": cn_vendors.BytedanceDuplexTTS,
        "stepfun": cn_vendors.StepFunTTS,
        "generic": GenericTTS,
    },
    avatar={
        "sensetime": cn_vendors.SenseTimeAvatar,
        "spatius": cn_vendors.SpatiusAvatar,
    },
)


class RegionVendorCatalog:
    cn = CN_VENDOR_NAMESPACE
    global_ = GLOBAL_VENDOR_NAMESPACE

    def __init__(self, scope: region.AreaScope) -> None:
        self._scope = scope

    @property
    def active(self) -> VendorNamespace:
        return CN_VENDOR_NAMESPACE if self._scope == "cn" else GLOBAL_VENDOR_NAMESPACE
