import pytest

from agora_agent import Agent, DeepgramSTT, MiniMaxTTS, OpenAI, OpenAITTS
from agora_agent.agentkit.presets import resolve_session_presets


class StartResponse:
    agent_id = "agent-id"


class FakeAgentsClient:
    def __init__(self):
        self.calls = []

    def start(self, appid, **kwargs):
        self.calls.append({"appid": appid, **kwargs})
        return StartResponse()


class FakeAsyncAgentsClient:
    def __init__(self):
        self.calls = []

    async def start(self, appid, **kwargs):
        self.calls.append({"appid": appid, **kwargs})
        return StartResponse()


class FakeClient:
    app_id = "appid"
    app_certificate = None

    def __init__(self, agents):
        self.agents = agents


def test_infers_minimax_tts_preset_for_managed_model() -> None:
    tts = MiniMaxTTS(model="speech_2_8_turbo", voice_id="English_captivating_female1")
    preset, properties = resolve_session_presets(None, {"tts": tts.to_config()})

    assert preset == "minimax_speech_2_8_turbo"
    assert properties["tts"]["vendor"] == "minimax"
    assert properties["tts"]["params"] == {"voice_setting": {"voice_id": "English_captivating_female1"}}


def test_infers_hyphenated_minimax_tts_preset_model() -> None:
    tts = MiniMaxTTS(model="speech-2.6-turbo", voice_id="English_captivating_female1")
    preset, properties = resolve_session_presets(None, {"tts": tts.to_config()})

    assert preset == "minimax_speech_2_6_turbo"
    assert properties["tts"]["vendor"] == "minimax"
    assert properties["tts"]["params"] == {"voice_setting": {"voice_id": "English_captivating_female1"}}


def test_infers_openai_tts_preset_when_model_omitted() -> None:
    tts = OpenAITTS(voice="alloy")
    preset, properties = resolve_session_presets(None, {"tts": tts.to_config()})

    assert preset == "openai_tts_1"
    assert properties["tts"]["vendor"] == "openai"
    assert properties["tts"]["params"] == {"voice": "alloy"}


def dump(value):
    if hasattr(value, "model_dump"):
        return value.model_dump(exclude_none=True)
    if hasattr(value, "dict"):
        return value.dict(exclude_none=True)
    return value


def test_session_start_infers_presets_for_managed_tts_and_llm() -> None:
    agent = (
        Agent(name="support")
        .with_llm(OpenAI(model="gpt-4o-mini"))
        .with_tts(MiniMaxTTS(model="speech_2_8_turbo", voice_id="English_captivating_female1"))
    )

    agents = FakeAgentsClient()
    client = FakeClient(agents)
    agent.create_session(
        client=client,
        channel="channel",
        token="token",
        agent_uid="1",
        remote_uids=["2"],
    ).start()

    assert len(agents.calls) == 1
    call = agents.calls[0]
    assert call["preset"] == "openai_gpt_4o_mini,minimax_speech_2_8_turbo"

    properties = dump(call["properties"])
    assert properties["tts"]["vendor"] == "minimax"
    assert properties["tts"]["params"] == {"voice_setting": {"voice_id": "English_captivating_female1"}}


@pytest.mark.asyncio
async def test_async_session_start_infers_presets_for_managed_tts_and_llm() -> None:
    agent = (
        Agent(name="support")
        .with_llm(OpenAI(model="gpt-4o-mini"))
        .with_tts(OpenAITTS(voice="alloy"))
    )

    agents = FakeAsyncAgentsClient()
    client = FakeClient(agents)
    await agent.create_async_session(
        client=client,
        channel="channel",
        token="token",
        agent_uid="1",
        remote_uids=["2"],
    ).start()

    assert len(agents.calls) == 1
    call = agents.calls[0]
    assert call["preset"] == "openai_gpt_4o_mini,openai_tts_1"

    properties = dump(call["properties"])
    assert properties["tts"]["vendor"] == "openai"
    assert properties["tts"]["params"] == {"voice": "alloy"}


def test_session_start_infers_managed_asr_without_skipping_llm_or_tts_validation() -> None:
    agent = (
        Agent(name="support")
        .with_stt(DeepgramSTT(model="nova-3", language="en-US"))
        .with_llm(OpenAI(model="gpt-4o-mini"))
        .with_tts(OpenAITTS(voice="alloy"))
    )

    agents = FakeAgentsClient()
    client = FakeClient(agents)
    agent.create_session(
        client=client,
        channel="channel",
        token="token",
        agent_uid="1",
        remote_uids=["2"],
    ).start()

    assert len(agents.calls) == 1
    call = agents.calls[0]
    assert call["preset"] == "deepgram_nova_3,openai_gpt_4o_mini,openai_tts_1"

    properties = dump(call["properties"])
    assert properties["asr"]["vendor"] == "deepgram"
    assert properties["asr"]["params"] == {"language": "en-US"}
    assert properties["llm"]["style"] == "openai"
    assert properties["tts"]["vendor"] == "openai"


def test_explicit_asr_preset_still_requires_tts_and_llm() -> None:
    agent = Agent(name="support")

    agents = FakeAgentsClient()
    client = FakeClient(agents)

    with pytest.raises(ValueError, match="TTS configuration is required"):
        agent.create_session(
            client=client,
            channel="channel",
            token="token",
            agent_uid="1",
            remote_uids=["2"],
            preset="deepgram_nova_3",
        ).start()

    assert agents.calls == []


def test_managed_llm_inference_still_requires_tts() -> None:
    agent = Agent(name="support").with_llm(OpenAI(model="gpt-4o-mini"))

    agents = FakeAgentsClient()
    client = FakeClient(agents)

    with pytest.raises(ValueError, match="TTS configuration is required"):
        agent.create_session(
            client=client,
            channel="channel",
            token="token",
            agent_uid="1",
            remote_uids=["2"],
        ).start()

    assert agents.calls == []


def test_explicit_llm_preset_still_requires_tts() -> None:
    agent = Agent(name="support")

    agents = FakeAgentsClient()
    client = FakeClient(agents)

    with pytest.raises(ValueError, match="TTS configuration is required"):
        agent.create_session(
            client=client,
            channel="channel",
            token="token",
            agent_uid="1",
            remote_uids=["2"],
            preset="openai_gpt_4o_mini",
        ).start()

    assert agents.calls == []


def test_managed_tts_inference_still_requires_llm() -> None:
    agent = Agent(name="support").with_tts(
        MiniMaxTTS(model="speech_2_8_turbo", voice_id="English_captivating_female1")
    )

    agents = FakeAgentsClient()
    client = FakeClient(agents)

    with pytest.raises(ValueError, match="LLM configuration is required"):
        agent.create_session(
            client=client,
            channel="channel",
            token="token",
            agent_uid="1",
            remote_uids=["2"],
        ).start()

    assert agents.calls == []


def test_explicit_tts_preset_still_requires_llm() -> None:
    agent = Agent(name="support")

    agents = FakeAgentsClient()
    client = FakeClient(agents)

    with pytest.raises(ValueError, match="LLM configuration is required"):
        agent.create_session(
            client=client,
            channel="channel",
            token="token",
            agent_uid="1",
            remote_uids=["2"],
            preset="openai_tts_1",
        ).start()

    assert agents.calls == []


def test_minimax_speech_02_turbo_requires_byok() -> None:
    with pytest.raises(ValueError, match="MiniMaxTTS requires key unless using a supported Agora-managed model"):
        MiniMaxTTS(model="speech-02-turbo", voice_id="English_captivating_female1")
