import pytest

from agora_agent import (
    AgentClient,
    Agent,
    Area,
    DeepgramSTT,
    MiniMaxCNTTS,
    MiniMaxTTS,
    OpenAI,
    TencentSTT,
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
    stt = agent.stt
    assert stt is not None
    assert stt["vendor"] == "deepgram"


def test_global_client_allows_cn_only_vendor() -> None:
    client = _client(Area.US)
    tencent_stt = TencentSTT(
        key="sec", app_id="appid", secret="secret", engine_model_type="16k_zh", voice_id="voice"
    )
    agent = Agent(client=client).with_stt(tencent_stt)
    assert agent.__class__.__name__ == "GlobalAgent"
    stt = agent.stt
    assert stt is not None
    assert stt["vendor"] == "tencent"


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
