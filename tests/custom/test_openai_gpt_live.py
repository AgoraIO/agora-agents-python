from agora_agent import Agent, OpenAIGptLive, OpenAIRealtime
from agora_agent.agentkit.vendors.catalog import GLOBAL_VENDOR_NAMESPACE
from agora_agent.agentkit.vendors.region import GLOBAL_MLLM_VENDORS

from test_helpers import test_client


def test_openai_gpt_live_is_distinct_global_mllm_vendor() -> None:
    config = OpenAIGptLive(api_key="openai-key").to_config()

    assert config["vendor"] == "openai_gpt_live"
    assert config["url"] == "wss://api.openai.com/v1/live"
    assert "openai_gpt_live" in GLOBAL_MLLM_VENDORS
    assert GLOBAL_VENDOR_NAMESPACE.mllm["openai_gpt_live"] is OpenAIGptLive
    assert OpenAIRealtime(api_key="openai-key").to_config()["vendor"] == "openai"


def test_openai_gpt_live_serializes_greeting_message() -> None:
    config = OpenAIGptLive(api_key="openai-key", greeting_message="Welcome to GPT Live").to_config()

    assert config["greeting_message"] == "Welcome to GPT Live"
    assert "greeting" not in config


def test_agent_level_greeting_uses_openai_gpt_live_greeting_message_field() -> None:
    properties = Agent(test_client()).with_mllm(
        OpenAIGptLive(api_key="openai-key")
    ).with_greeting("Welcome to GPT Live")

    mllm = properties.to_properties(
        channel="test-channel",
        agent_uid="1",
        remote_uids=[],
        token="token",
        skip_vendor_validation=True,
    ).mllm
    assert mllm is not None
    assert mllm.greeting_message == "Welcome to GPT Live"
