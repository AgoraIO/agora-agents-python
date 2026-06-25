import pytest

from agora_agent import (
    AgentClient,
    Agent,
    Area,
    DeepgramSTT,
    GenericTTS,
    MiniMaxCNTTS,
    MiniMaxTTS,
    OpenAI,
    SpatiusAvatar,
    TencentSTT,
    XaiSTT,
    XaiTTS,
    XaiGrok,
)
from agora_agent.agentkit.vendors.region import (
    CN_ASR_VENDORS,
    CN_AVATAR_VENDORS,
    CN_TTS_VENDORS,
    GLOBAL_ASR_VENDORS,
    GLOBAL_AVATAR_VENDORS,
    GLOBAL_TTS_VENDORS,
)


def _client(area: Area) -> AgentClient:
    return AgentClient(area=area, app_id="0" * 32, app_certificate="1" * 32)


def test_agent_requires_client_at_construction() -> None:
    with pytest.raises(TypeError, match="client is required"):
        Agent()  # type: ignore[call-arg]


def test_cn_client_exposes_cn_vendor_catalog() -> None:
    client = _client(Area.CN)

    assert client.area_scope == "cn"
    assert Agent(client=client).__class__.__name__ == "CNAgent"


def test_global_client_exposes_global_vendor_catalog() -> None:
    client = _client(Area.US)

    assert client.area_scope == "global"
    assert Agent(client=client).__class__.__name__ == "GlobalAgent"


def test_regional_agent_builder_preserves_agent_kwargs() -> None:
    cn_agent = Agent(client=_client(Area.CN), turn_detection={"language": "zh-CN"})
    global_agent = Agent(client=_client(Area.US), turn_detection={"language": "en-US"})

    assert cn_agent.__class__.__name__ == "CNAgent"
    assert cn_agent.turn_detection == {"language": "zh-CN"}
    assert global_agent.__class__.__name__ == "GlobalAgent"
    assert global_agent.turn_detection == {"language": "en-US"}


def test_agent_constructor_auto_selects_area_aware_subclass() -> None:
    cn_agent = Agent(client=_client(Area.CN))
    global_agent = Agent(client=_client(Area.US))

    assert cn_agent.__class__.__name__ == "CNAgent"
    assert global_agent.__class__.__name__ == "GlobalAgent"


def test_cn_client_allows_global_only_vendor() -> None:
    client = _client(Area.CN)
    agent = Agent(client=client).with_stt(
        DeepgramSTT(api_key="dg-key", model="nova-2", language="en-US")
    )
    assert agent.__class__.__name__ == "CNAgent"
    assert agent.stt is not None
    assert agent.stt["vendor"] == "deepgram"


def test_global_client_allows_cn_only_vendor() -> None:
    client = _client(Area.US)
    tencent_stt = TencentSTT(
        key="sec", app_id="appid", secret="secret", engine_model_type="16k_zh", voice_id="voice"
    )
    agent = Agent(client=client).with_stt(tencent_stt)
    assert agent.__class__.__name__ == "GlobalAgent"
    assert agent.stt is not None
    assert agent.stt["vendor"] == "tencent"


def test_direct_import_vendors_work_with_bound_global_client() -> None:
    agent = (
        Agent(client=_client(Area.US))
        .with_stt(DeepgramSTT(model="nova-3", language="en-US"))
        .with_llm(OpenAI(model="gpt-4o-mini"))
        .with_tts(MiniMaxTTS(model="speech_2_6_turbo", voice_id="English_captivating_female1"))
    )

    assert agent.__class__.__name__ == "GlobalAgent"


def test_direct_import_cn_vendors_work_with_bound_cn_client() -> None:
    agent = (
        Agent(client=_client(Area.CN))
        .with_stt(TencentSTT(key="sec", app_id="appid", secret="secret", engine_model_type="16k_zh", voice_id="voice"))
        .with_tts(MiniMaxCNTTS(key="mm-key", model="speech-01-turbo", voice_id="female-shaonv"))
    )

    assert agent.__class__.__name__ == "CNAgent"


def test_spatius_avatar_is_classified_as_cn_vendor() -> None:
    assert "spatius" in CN_AVATAR_VENDORS
    assert "spatius" not in GLOBAL_AVATAR_VENDORS

    agent = Agent(client=_client(Area.CN)).with_avatar(
        SpatiusAvatar(
            spatius_api_key="spatius-key",
            spatius_app_id="spatius-app",
            spatius_avatar_id="spatius-avatar",
            agora_uid="2",
        )
    )
    assert agent.__class__.__name__ == "CNAgent"


def test_generic_tts_is_classified_as_shared_vendor() -> None:
    assert "generic" in CN_TTS_VENDORS
    assert "generic" in GLOBAL_TTS_VENDORS

    cn_agent = Agent(client=_client(Area.CN)).with_tts(
        GenericTTS(
            url="https://tts.example.com/v1/audio",
            headers={"Authorization": "Bearer token"},
            model="tts-model",
            voice="voice-1",
        )
    )
    global_agent = Agent(client=_client(Area.US)).with_tts(
        GenericTTS(
            url="https://tts.example.com/v1/audio",
            headers={"Authorization": "Bearer token"},
            model="tts-model",
            voice="voice-1",
        )
    )

    assert cn_agent.__class__.__name__ == "CNAgent"
    assert global_agent.__class__.__name__ == "GlobalAgent"
    assert cn_agent.tts is not None and cn_agent.tts["vendor"] == "generic"
    assert global_agent.tts is not None and global_agent.tts["vendor"] == "generic"


def test_xai_asr_and_tts_are_classified_as_global_vendors() -> None:
    assert "xai" not in CN_ASR_VENDORS
    assert "xai" in GLOBAL_ASR_VENDORS
    assert "xai" not in CN_TTS_VENDORS
    assert "xai" in GLOBAL_TTS_VENDORS

    global_agent = (
        Agent(client=_client(Area.US))
        .with_stt(XaiSTT(api_key="xai-stt-key"))
        .with_tts(
            XaiTTS(
                api_key="xai-tts-key",
                language="en-US",
            )
        )
    )

    assert global_agent.__class__.__name__ == "GlobalAgent"
    assert global_agent.stt is not None and global_agent.stt["vendor"] == "xai"
    assert global_agent.tts is not None and global_agent.tts["vendor"] == "xai"


def test_xai_grok_remains_mllm_vendor() -> None:
    agent = Agent(client=_client(Area.US)).with_mllm(XaiGrok(api_key="xai-key"))

    assert agent.__class__.__name__ == "GlobalAgent"
    assert agent.mllm is not None and agent.mllm["vendor"] == "xai"
