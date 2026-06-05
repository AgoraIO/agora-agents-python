from types import SimpleNamespace

import pytest

from agora_agent.agentkit import Agent, AgentSession
from agora_agent.agentkit.vendors import (
    ElevenLabsTTS,
    GenericAvatar,
    LiveAvatarAvatar,
    OpenAI,
    OpenAIRealtime,
)
from agora_agent.agents.types.get_turns_agents_response import GetTurnsAgentsResponse


APP_ID = "0" * 32
APP_CERTIFICATE = "1" * 32


class _Agents:
    def __init__(self):
        self.calls = []
        self.start_calls = []

    def start(self, app_id, name, properties, preset=None, pipeline_id=None, request_options=None):
        self.start_calls.append((app_id, name, properties, preset, pipeline_id, request_options))
        return SimpleNamespace(agent_id="agent-1")

    def get_turns(self, app_id, agent_id, page_index=None, page_size=None, request_options=None):
        self.calls.append((app_id, agent_id, page_index, page_size, request_options))
        is_last_page = page_index != 1
        return GetTurnsAgentsResponse(
            agent_id=agent_id,
            channel="room",
            total_turn_count=2,
            pagination={
                "page_index": page_index or 1,
                "total_pages": 2,
                "is_last_page": is_last_page,
            },
            turns=[{"turn_id": float(page_index or 1)}],
        )


class _Client:
    auth_mode = "basic"
    app_id = APP_ID
    app_certificate = APP_CERTIFICATE

    def __init__(self):
        self.agents = _Agents()
        self.agent_management = object()


def _session(agent, warn=None):
    return AgentSession(
        client=_Client(),
        agent=agent,
        app_id=APP_ID,
        app_certificate=APP_CERTIFICATE,
        name="test",
        channel="room",
        agent_uid="1",
        remote_uids=["100"],
        warn=warn,
    )


def test_generic_avatar_enrichment_adds_session_context_and_token():
    agent = Agent(name="test").with_avatar(
        GenericAvatar(
            api_key="avatar-key",
            api_base_url="https://avatar.example.com",
            avatar_id="avatar-1",
            agora_uid="2",
        )
    )
    session = _session(agent)

    properties = session._build_start_properties(  # noqa: SLF001
        {"app_id": APP_ID, "app_certificate": APP_CERTIFICATE},
        skip_vendor_validation_categories=set(),
        allow_missing_vendor_categories={"tts", "llm", "asr"},
    )

    params = properties["avatar"]["params"]
    assert params["agora_appid"] == APP_ID
    assert params["agora_channel"] == "room"
    assert params["agora_token"]
    assert params["agora_token"] != properties["token"]


def test_generic_avatar_empty_session_fields_are_filled():
    agent = Agent(name="test").with_avatar(
        GenericAvatar(
            api_key="avatar-key",
            api_base_url="https://avatar.example.com",
            avatar_id="avatar-1",
            agora_uid="2",
            agora_appid="",
            agora_channel="",
            agora_token="",
        )
    )
    session = _session(agent)

    properties = session._build_start_properties(  # noqa: SLF001
        {"app_id": APP_ID, "app_certificate": APP_CERTIFICATE},
        skip_vendor_validation_categories=set(),
        allow_missing_vendor_categories={"tts", "llm", "asr"},
    )

    params = properties["avatar"]["params"]
    assert params["agora_appid"] == APP_ID
    assert params["agora_channel"] == "room"
    assert params["agora_token"]


def test_avatar_uid_matching_agent_uid_warns():
    warnings = []
    agent = Agent(name="test").with_avatar(
        GenericAvatar(
            api_key="avatar-key",
            api_base_url="https://avatar.example.com",
            avatar_id="avatar-1",
            agora_uid="1",
        )
    )
    session = _session(agent, warn=warnings.append)

    session._build_start_properties(  # noqa: SLF001
        {"app_id": APP_ID, "app_certificate": APP_CERTIFICATE},
        skip_vendor_validation_categories=set(),
        allow_missing_vendor_categories={"tts", "llm", "asr"},
    )

    assert any("matches agent_rtc_uid" in warning for warning in warnings)


def test_vendor_config_takes_priority_over_agent_level_convenience_fields():
    agent = (
        Agent(name="test")
        .with_llm(
            OpenAI(
                model="gpt-4o-mini",
                greeting_message="vendor greeting",
                failure_message="vendor failure",
                max_history=1,
            )
        )
        .with_tts(ElevenLabsTTS(key="tts-key", model_id="model", voice_id="voice", base_url="wss://api.elevenlabs.io/v1"))
        .with_greeting("agent greeting")
        .with_failure_message("agent failure")
        .with_max_history(2)
    )
    session = _session(agent)

    properties = session._build_start_properties(  # noqa: SLF001
        {"app_id": APP_ID, "app_certificate": APP_CERTIFICATE},
        skip_vendor_validation_categories=set(),
        allow_missing_vendor_categories=set(),
    )

    assert properties["llm"]["greeting_message"] == "vendor greeting"
    assert properties["llm"]["failure_message"] == "vendor failure"
    assert properties["llm"]["max_history"] == 1


def test_session_start_properties_applies_mllm_agent_level_defaults():
    agent = (
        Agent(name="test")
        .with_mllm(OpenAIRealtime(api_key="mllm-key"))
        .with_greeting("agent greeting")
        .with_failure_message("agent failure")
        .with_max_history(2)
    )
    session = _session(agent)

    properties = session._build_start_properties(  # noqa: SLF001
        {"app_id": APP_ID, "app_certificate": APP_CERTIFICATE},
        skip_vendor_validation_categories=set(),
        allow_missing_vendor_categories=set(),
    )

    assert properties["mllm"]["greeting_message"] == "agent greeting"
    assert properties["mllm"]["failure_message"] == "agent failure"
    assert "max_history" not in properties["mllm"]


def test_session_start_properties_preserves_mllm_vendor_defaults():
    agent = (
        Agent(name="test")
        .with_mllm(
            OpenAIRealtime(
                api_key="mllm-key",
                greeting_message="vendor greeting",
                failure_message="vendor failure",
            )
        )
        .with_greeting("agent greeting")
        .with_failure_message("agent failure")
        .with_max_history(2)
    )
    session = _session(agent)

    properties = session._build_start_properties(  # noqa: SLF001
        {"app_id": APP_ID, "app_certificate": APP_CERTIFICATE},
        skip_vendor_validation_categories=set(),
        allow_missing_vendor_categories=set(),
    )

    assert properties["mllm"]["greeting_message"] == "vendor greeting"
    assert properties["mllm"]["failure_message"] == "vendor failure"
    assert "max_history" not in properties["mllm"]


def test_session_start_allows_mllm_without_tts():
    agent = Agent(name="test").with_mllm(OpenAIRealtime(api_key="mllm-key"))
    session = _session(agent)

    assert session.start() == "agent-1"


def test_session_start_rejects_mllm_with_enabled_avatar():
    agent = (
        Agent(name="test")
        .with_mllm(OpenAIRealtime(api_key="mllm-key"))
        .with_avatar(
            LiveAvatarAvatar(
                api_key="avatar-key",
                quality="medium",
                agora_uid="2",
                agora_token="avatar-token",
            )
        )
    )
    session = _session(agent)

    with pytest.raises(ValueError, match="cascading"):
        session.start()
    assert session._client.agents.start_calls == []  # noqa: SLF001


def test_session_start_allows_mllm_with_disabled_avatar():
    agent = (
        Agent(name="test")
        .with_mllm(OpenAIRealtime(api_key="mllm-key"))
        .with_avatar(
            LiveAvatarAvatar(
                api_key="avatar-key",
                quality="medium",
                agora_uid="2",
                agora_token="avatar-token",
                enable=False,
            )
        )
    )
    session = _session(agent)

    assert session.start() == "agent-1"


def test_avatar_sample_rate_validation_uses_serialized_vendor_keys():
    warnings = []
    agent = (
        Agent(name="test")
        .with_avatar(LiveAvatarAvatar(api_key="avatar-key", quality="medium", agora_uid="2"))
        .with_tts(ElevenLabsTTS(key="tts-key", model_id="eleven_flash_v2_5", voice_id="voice", base_url="wss://api.elevenlabs.io/v1", sample_rate=24000))
    )
    session = _session(agent, warn=warnings.append)

    session._validate_avatar_config()  # noqa: SLF001

    assert warnings == []


def test_avatar_user_token_is_not_overwritten():
    agent = Agent(name="test").with_avatar(
        LiveAvatarAvatar(
            api_key="live-key",
            quality="medium",
            agora_uid="2",
            agora_token="user-token",
        )
    )
    session = _session(agent)

    properties = session._build_start_properties(  # noqa: SLF001
        {"app_id": APP_ID, "app_certificate": APP_CERTIFICATE},
        skip_vendor_validation_categories=set(),
        allow_missing_vendor_categories={"tts", "llm", "asr"},
    )

    assert properties["avatar"]["params"]["agora_token"] == "user-token"


def test_get_turns_forwards_pagination_args():
    session = _session(Agent(name="test"))
    session._agent_id = "agent-id"  # noqa: SLF001

    session.get_turns(page_index=3, page_size=25)

    assert session._client.agents.calls[-1][:4] == (APP_ID, "agent-id", 3, 25)  # noqa: SLF001


def test_get_all_turns_aggregates_pages():
    session = _session(Agent(name="test"))
    session._agent_id = "agent-id"  # noqa: SLF001

    response = session.get_all_turns(page_size=1)

    assert [turn.turn_id for turn in response.turns] == [1.0, 2.0]
    assert response.pagination.page_index == 2


def test_get_all_turns_raises_when_pagination_does_not_advance():
    class _StuckAgents:
        def __init__(self):
            self.calls = 0

        def get_turns(self, app_id, agent_id, page_index=None, page_size=None, request_options=None):
            self.calls += 1
            return GetTurnsAgentsResponse(
                agent_id=agent_id,
                channel="room",
                total_turn_count=2,
                pagination={"page_index": 1, "is_last_page": False},
                turns=[{"turn_id": 1.0}],
            )

    class _StuckClient:
        auth_mode = "basic"
        app_id = APP_ID
        app_certificate = APP_CERTIFICATE

        def __init__(self):
            self.agents = _StuckAgents()
            self.agent_management = object()

    session = AgentSession(
        client=_StuckClient(),
        agent=Agent(name="test"),
        app_id=APP_ID,
        app_certificate=APP_CERTIFICATE,
        name="test",
        channel="room",
        agent_uid="1",
        remote_uids=["100"],
    )
    session._agent_id = "agent-id"  # noqa: SLF001

    with pytest.raises(RuntimeError, match="did not advance"):
        session.get_all_turns(page_size=1)


def test_get_all_turns_raises_when_pagination_metadata_missing():
    class _NoMetaAgents:
        def get_turns(self, app_id, agent_id, page_index=None, page_size=None, request_options=None):
            return GetTurnsAgentsResponse(
                agent_id=agent_id,
                channel="room",
                total_turn_count=1,
                pagination={"is_last_page": False},
                turns=[{"turn_id": 1.0}],
            )

    class _NoMetaClient:
        auth_mode = "basic"
        app_id = APP_ID
        app_certificate = APP_CERTIFICATE

        def __init__(self):
            self.agents = _NoMetaAgents()
            self.agent_management = object()

    session = AgentSession(
        client=_NoMetaClient(),
        agent=Agent(name="test"),
        app_id=APP_ID,
        app_certificate=APP_CERTIFICATE,
        name="test",
        channel="room",
        agent_uid="1",
        remote_uids=["100"],
    )
    session._agent_id = "agent-id"  # noqa: SLF001

    with pytest.raises(RuntimeError, match="cannot continue"):
        session.get_all_turns(page_size=1)
