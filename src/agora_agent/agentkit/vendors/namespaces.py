from __future__ import annotations

from . import cn as cn_vendors
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


class GlobalSTTVendors:
    ares = AresSTT
    deepgram = DeepgramSTT
    microsoft = MicrosoftSTT
    openai = OpenAISTT
    google = GoogleSTT
    amazon = AmazonSTT
    assemblyai = AssemblyAISTT
    speechmatics = SpeechmaticsSTT
    sarvam = SarvamSTT
    xai = XaiSTT


class CNSTTVendors:
    fengming = cn_vendors.FengmingSTT
    tencent = cn_vendors.TencentSTT
    microsoft = cn_vendors.MicrosoftSTT
    xfyun = cn_vendors.XfyunSTT
    xfyun_bigmodel = cn_vendors.XfyunBigModelSTT
    xfyun_dialect = cn_vendors.XfyunDialectSTT


class GlobalLLMVendors:
    openai = OpenAI
    azure = AzureOpenAI
    anthropic = Anthropic
    gemini = Gemini
    groq = Groq
    vertexai = VertexAILLM
    bedrock = AmazonBedrock
    dify = Dify
    custom = CustomLLM


class CNLLMVendors:
    aliyun = cn_vendors.AliyunLLM
    bytedance = cn_vendors.BytedanceLLM
    deepseek = cn_vendors.DeepSeekLLM
    tencent = cn_vendors.TencentLLM


class GlobalTTSVendors:
    microsoft = MicrosoftTTS
    elevenlabs = ElevenLabsTTS
    minimax = MiniMaxTTS
    murf = MurfTTS
    cartesia = CartesiaTTS
    openai = OpenAITTS
    humeai = HumeAITTS
    rime = RimeTTS
    fishaudio = FishAudioTTS
    google = GoogleTTS
    amazon = AmazonTTS
    sarvam = SarvamTTS
    generic = GenericTTS
    xai = XaiTTS
    deepgram = DeepgramTTS


class CNTTSVendors:
    minimax = cn_vendors.MiniMaxTTS
    tencent = cn_vendors.TencentTTS
    bytedance = cn_vendors.BytedanceTTS
    microsoft = cn_vendors.MicrosoftTTS
    cosyvoice = cn_vendors.CosyVoiceTTS
    bytedance_duplex = cn_vendors.BytedanceDuplexTTS
    stepfun = cn_vendors.StepFunTTS
    generic = GenericTTS


class GlobalAvatarVendors:
    akool = AkoolAvatar
    liveavatar = LiveAvatarAvatar
    anam = AnamAvatar
    generic = GenericAvatar
    heygen = HeyGenAvatar


class CNAvatarVendors:
    sensetime = cn_vendors.SenseTimeAvatar
    spatius = cn_vendors.SpatiusAvatar


class GlobalVendors:
    stt: GlobalSTTVendors
    llm: GlobalLLMVendors
    tts: GlobalTTSVendors
    avatar: GlobalAvatarVendors

    def __init__(self) -> None:
        self.stt = GlobalSTTVendors()
        self.llm = GlobalLLMVendors()
        self.tts = GlobalTTSVendors()
        self.avatar = GlobalAvatarVendors()


class CNVendors:
    stt: CNSTTVendors
    llm: CNLLMVendors
    tts: CNTTSVendors
    avatar: CNAvatarVendors

    def __init__(self) -> None:
        self.stt = CNSTTVendors()
        self.llm = CNLLMVendors()
        self.tts = CNTTSVendors()
        self.avatar = CNAvatarVendors()
