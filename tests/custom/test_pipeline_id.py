import pytest

from agora_agent import Agent, OpenAI, OpenAITTS


def dump(value):
    if hasattr(value, "model_dump"):
        return value.model_dump(exclude_none=True)
    if hasattr(value, "dict"):
        return value.dict(exclude_none=True)
    return value


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


def start_agent(agent, **overrides):
    agents = FakeAgentsClient()
    client = FakeClient(agents)
    options = {
        "channel": "channel",
        "token": "token",
        "agent_uid": "1",
        "remote_uids": ["100"],
        **overrides,
    }

    agent_id = agent.create_session(client, **options).start()

    assert agent_id == "agent-id"
    assert len(agents.calls) == 1
    return agents.calls[0]


def test_agent_pipeline_id_sends_top_level_pipeline_id() -> None:
    call = start_agent(Agent(name="support", pipeline_id="studio-pipeline-id"))

    assert call["appid"] == "appid"
    assert call["name"] == "support"
    assert call["pipeline_id"] == "studio-pipeline-id"
    properties = dump(call["properties"])
    assert properties["channel"] == "channel"
    assert properties["token"] == "token"
    assert properties["agent_rtc_uid"] == "1"
    assert properties["remote_rtc_uids"] == ["100"]


def test_session_pipeline_id_overrides_agent_pipeline_id() -> None:
    call = start_agent(
        Agent(name="support", pipeline_id="agent-pipeline"),
        pipeline_id="session-pipeline",
    )

    assert call["pipeline_id"] == "session-pipeline"


def test_agent_pipeline_id_skips_missing_vendor_validation() -> None:
    call = start_agent(Agent(name="support", pipeline_id="studio-pipeline-id"))

    assert call["pipeline_id"] == "studio-pipeline-id"
    properties = dump(call["properties"])
    assert "asr" not in properties
    assert "llm" not in properties
    assert "tts" not in properties


def test_pipeline_id_allows_single_llm_override_without_tts_or_asr() -> None:
    agent = Agent(name="support", pipeline_id="studio-pipeline-id").with_llm(
        OpenAI(
            api_key="openai-key",
            base_url="https://api.openai.com/v1/chat/completions",
            model="gpt-4o",
        )
    )

    call = start_agent(agent)

    assert call["pipeline_id"] == "studio-pipeline-id"
    properties = dump(call["properties"])
    assert "asr" not in properties
    assert "tts" not in properties
    assert properties["llm"]["api_key"] == "openai-key"
    assert properties["llm"]["params"]["model"] == "gpt-4o"


def test_pipeline_id_allows_multiple_overrides_without_asr() -> None:
    agent = (
        Agent(name="support", pipeline_id="studio-pipeline-id")
        .with_llm(
            OpenAI(
                api_key="openai-key",
                base_url="https://api.openai.com/v1/chat/completions",
                model="gpt-4o",
            )
        )
        .with_tts(
            OpenAITTS(
                api_key="tts-key",
                base_url="https://api.openai.com/v1/audio/speech",
                model="tts-1-hd",
                voice="alloy",
            )
        )
    )

    call = start_agent(agent)

    assert call["pipeline_id"] == "studio-pipeline-id"
    properties = dump(call["properties"])
    assert "asr" not in properties
    assert properties["llm"]["api_key"] == "openai-key"
    assert properties["tts"]["vendor"] == "openai"
    assert properties["tts"]["params"]["api_key"] == "tts-key"


def test_skip_vendor_validation_boolean_is_deprecated() -> None:
    with pytest.warns(DeprecationWarning, match="skip_vendor_validation is deprecated"):
        properties = Agent(name="support").to_properties(
            channel="channel",
            token="token",
            agent_uid="1",
            remote_uids=["100"],
            skip_vendor_validation=True,
        )

    payload = dump(properties)
    assert "asr" not in payload
    assert "llm" not in payload
    assert "tts" not in payload


def test_pipeline_id_is_not_sent_inside_properties() -> None:
    call = start_agent(Agent(name="support", pipeline_id="studio-pipeline-id"))

    assert call["pipeline_id"] == "studio-pipeline-id"
    assert "pipeline_id" not in dump(call["properties"])


def test_pipeline_id_survives_builder_clone() -> None:
    agent = Agent(name="support", pipeline_id="studio-pipeline-id").with_tools(True)

    assert agent.pipeline_id == "studio-pipeline-id"
    call = start_agent(agent)

    assert call["pipeline_id"] == "studio-pipeline-id"
    assert dump(call["properties"])["advanced_features"] == {"enable_tools": True}


@pytest.mark.asyncio
async def test_async_session_uses_agent_pipeline_id() -> None:
    agents = FakeAsyncAgentsClient()
    client = FakeClient(agents)
    agent = Agent(name="support", pipeline_id="studio-pipeline-id")

    agent_id = await agent.create_async_session(
        client,
        channel="channel",
        token="token",
        agent_uid="1",
        remote_uids=["100"],
    ).start()

    assert agent_id == "agent-id"
    assert agents.calls[0]["pipeline_id"] == "studio-pipeline-id"
    assert "pipeline_id" not in dump(agents.calls[0]["properties"])
