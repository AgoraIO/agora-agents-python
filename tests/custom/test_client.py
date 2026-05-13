from agora_agent.agentkit.agent import Agent, AdvancedFeatures, InterruptionConfig, MllmTurnDetectionConfig, TurnDetectionConfig
from agora_agent.agentkit.constants import TurnDetectionTypeValues
import asyncio
import warnings
from agora_agent.agentkit.agent_session import AgentSession, AsyncAgentSession
from agora_agent.agentkit.vendors import DeepgramTTS, HeyGenAvatar, MicrosoftTTS, OpenAI, OpenAIRealtime
from agora_agent.agent_management.types.agent_think_response import AgentThinkResponse
from typing import Any, Dict, List, Tuple


class _AgentManagementStub:
    def __init__(self) -> None:
        self.calls: List[Tuple[str, str, Dict[str, Any]]] = []

    def agent_think(self, appid, agent_id, **kwargs):  # noqa: ANN001
        self.calls.append((appid, agent_id, kwargs))
        return AgentThinkResponse(agent_id=agent_id, channel="room", start_ts=1)


class _ClientStub:
    auth_mode = "basic"

    def __init__(self) -> None:
        self.agents = object()
        self.agent_management = _AgentManagementStub()


class _AsyncAgentManagementStub:
    def __init__(self) -> None:
        self.calls: List[Tuple[str, str, Dict[str, Any]]] = []

    async def agent_think(self, appid, agent_id, **kwargs):  # noqa: ANN001
        self.calls.append((appid, agent_id, kwargs))
        return AgentThinkResponse(agent_id=agent_id, channel="room", start_ts=1)


class _AsyncClientStub:
    auth_mode = "basic"

    def __init__(self) -> None:
        self.agents = object()
        self.agent_management = _AsyncAgentManagementStub()


def test_agentkit_think_routes_to_agent_management() -> None:
    client = _ClientStub()
    session = AgentSession(
        client=client,
        agent=Agent(),
        app_id="appid",
        name="agent",
        channel="room",
        token="token",
        agent_uid="1",
        remote_uids=["2"],
    )
    session._status = "running"
    session._agent_id = "agent-1"

    response = session.think("Injected instruction", on_thinking_action="interrupt")
    assert response.agent_id == "agent-1"
    assert len(client.agent_management.calls) == 1
    appid, agent_id, kwargs = client.agent_management.calls[0]
    assert appid == "appid"
    assert agent_id == "agent-1"
    assert kwargs["text"] == "Injected instruction"
    assert kwargs["on_thinking_action"] == "interrupt"


def test_async_agentkit_think_routes_to_agent_management() -> None:
    async def _run() -> None:
        client = _AsyncClientStub()
        session = AsyncAgentSession(
            client=client,
            agent=Agent(),
            app_id="appid",
            name="agent",
            channel="room",
            token="token",
            agent_uid="1",
            remote_uids=["2"],
        )
        session._status = "running"
        session._agent_id = "agent-1"

        response = await session.think("Injected instruction", on_thinking_action="interrupt")
        assert response.agent_id == "agent-1"
        assert len(client.agent_management.calls) == 1
        appid, agent_id, kwargs = client.agent_management.calls[0]
        assert appid == "appid"
        assert agent_id == "agent-1"
        assert kwargs["text"] == "Injected instruction"
        assert kwargs["on_thinking_action"] == "interrupt"

    asyncio.run(_run())


def test_llm_vendor_headers_are_forwarded_to_properties() -> None:
    agent = Agent().with_llm(
        OpenAI(
            api_key="openai-key",
            model="gpt-4o-mini",
            headers={"X-Trace-Id": "trace-123"},
            output_modalities=["text", "audio"],
            greeting_configs={"mode": "single_first"},
            template_variables={"caller_name": "Ada"},
        )
    ).with_tts(MicrosoftTTS(key="tts-key", region="eastus", voice_name="en-US-JennyNeural"))

    props = agent.to_properties(
        channel="room",
        token="rtc-token",
        agent_uid="1",
        remote_uids=["2"],
    )

    assert props.llm is not None
    assert props.llm.headers == {"X-Trace-Id": "trace-123"}
    assert props.llm.output_modalities == ["text", "audio"]
    assert props.llm.greeting_configs is not None
    assert props.llm.greeting_configs.mode == "single_first"
    assert props.llm.template_variables == {"caller_name": "Ada"}


def test_with_turn_detection_forwards_config() -> None:
    turn_detection = TurnDetectionConfig(
        type=TurnDetectionTypeValues.AGORA_VAD,
        threshold=0.5,
    )

    props = Agent().with_turn_detection(turn_detection).to_properties(
        channel="room",
        token="rtc-token",
        agent_uid="1",
        remote_uids=["2"],
        skip_vendor_validation=True,
    )

    assert props.turn_detection == turn_detection


def test_with_interruption_forwards_config() -> None:
    interruption = InterruptionConfig(
        enable=False,
        disabled_config={"strategy": "ignore"},
    )

    props = Agent().with_interruption(interruption).to_properties(
        channel="room",
        token="rtc-token",
        agent_uid="1",
        remote_uids=["2"],
        skip_vendor_validation=True,
    )

    assert props.interruption == interruption


def test_mllm_turn_detection_is_forwarded_without_legacy_style() -> None:
    mllm_turn_detection = MllmTurnDetectionConfig(
        mode="server_vad",
        server_vad_config={"idle_timeout_ms": 5000},
    )
    props = Agent().with_mllm(
        OpenAIRealtime(api_key="openai-key", turn_detection=mllm_turn_detection)
    ).to_properties(
        channel="room",
        token="rtc-token",
        agent_uid="1",
        remote_uids=["2"],
    )

    assert props.mllm is not None
    assert props.mllm.vendor == "openai"
    assert props.mllm.style is None
    assert props.mllm.turn_detection == mllm_turn_detection


def test_with_mllm_sets_mllm_enable_without_legacy_flag() -> None:
    agent = Agent().with_mllm(OpenAIRealtime(api_key="openai-key"))

    props = agent.to_properties(
        channel="room",
        token="rtc-token",
        agent_uid="1",
        remote_uids=["2"],
    )

    assert props.mllm is not None
    assert props.mllm.enable is True
    assert props.advanced_features is None


def test_with_mllm_removes_deprecated_enable_mllm_from_existing_advanced_features() -> None:
    agent = Agent(
        advanced_features=AdvancedFeatures(enable_mllm=True, enable_rtm=True)
    ).with_mllm(OpenAIRealtime(api_key="openai-key"))

    props = agent.to_properties(
        channel="room",
        token="rtc-token",
        agent_uid="1",
        remote_uids=["2"],
    )

    assert props.mllm is not None
    assert props.mllm.enable is True
    assert props.advanced_features is not None
    assert props.advanced_features.enable_mllm is None
    assert props.advanced_features.enable_rtm is True


def test_with_mllm_drops_advanced_features_when_only_deprecated_enable_mllm_was_set() -> None:
    props = Agent(
        advanced_features=AdvancedFeatures(enable_mllm=True)
    ).with_mllm(OpenAIRealtime(api_key="openai-key")).to_properties(
        channel="room",
        token="rtc-token",
        agent_uid="1",
        remote_uids=["2"],
    )

    assert props.mllm is not None
    assert props.mllm.enable is True
    assert props.advanced_features is None


def test_with_tools_sets_enable_tools() -> None:
    props = Agent().with_tools().to_properties(
        channel="room",
        token="rtc-token",
        agent_uid="1",
        remote_uids=["2"],
        skip_vendor_validation=True,
    )

    assert props.advanced_features is not None
    assert props.advanced_features.enable_tools is True


def test_heygen_avatar_emits_deprecation_warning() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        HeyGenAvatar(api_key="heygen-key", quality="high", agora_uid="42")

    assert any("HeyGenAvatar is deprecated" in str(warning.message) for warning in caught)


def test_deepgram_tts_vendor_config() -> None:
    tts = DeepgramTTS(
        api_key="deepgram-key",
        model="aura-2-thalia-en",
        base_url="wss://api.deepgram.com/v1/speak",
        sample_rate=24000,
        params={"encoding": "linear16"},
    ).to_config()

    assert tts["vendor"] == "deepgram"
    assert tts["params"] == {
        "api_key": "deepgram-key",
        "model": "aura-2-thalia-en",
        "base_url": "wss://api.deepgram.com/v1/speak",
        "sample_rate": 24000,
        "encoding": "linear16",
    }
