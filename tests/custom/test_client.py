from agora_agent.agentkit.agent import Agent
from agora_agent.agentkit.agent_session import AgentSession


class _AgentManagementStub:
    def __init__(self) -> None:
        self.calls = []

    def agent_think(self, appid, agent_id, **kwargs):  # noqa: ANN001
        self.calls.append((appid, agent_id, kwargs))
        return {"agent_id": agent_id, "channel": "room", "start_ts": 1}


class _ClientStub:
    auth_mode = "basic"

    def __init__(self) -> None:
        self.agents = object()
        self.agent_management = _AgentManagementStub()


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
    assert response["agent_id"] == "agent-1"
    assert len(client.agent_management.calls) == 1
    appid, agent_id, kwargs = client.agent_management.calls[0]
    assert appid == "appid"
    assert agent_id == "agent-1"
    assert kwargs["text"] == "Injected instruction"
    assert kwargs["on_thinking_action"] == "interrupt"
