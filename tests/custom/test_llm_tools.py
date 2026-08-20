from agora_agent import AdvancedFeatures, Agent, OpenAI
from agora_agent.agentkit.vendors.cn import AliyunLLM

from test_helpers import test_client


def _tool() -> dict:
    return {
        "type": "function",
        "function": {
            "name": "lookup_order",
            "parameters": {"type": "object", "properties": {}},
        },
        "server": {"method": "GET", "url": "https://example.com/orders"},
    }


def test_global_llm_tools_use_dict_shape_and_require_explicit_enablement() -> None:
    tool = _tool()
    vendor = OpenAI(
        api_key="openai-key",
        base_url="https://api.openai.com/v1/chat/completions",
        model="gpt-4o-mini",
        tools=[tool],
    )

    assert vendor.to_config()["tools"] == [tool]
    agent = Agent(test_client()).with_llm(vendor)
    assert agent.advanced_features is None
    enabled_agent = agent.with_tools()
    assert enabled_agent.advanced_features is not None
    assert enabled_agent.advanced_features.enable_tools is True
    disabled_agent = agent.with_tools(False)
    assert disabled_agent.advanced_features is not None
    assert disabled_agent.advanced_features.enable_tools is False


def test_cn_llm_uses_the_same_tools_shape_as_global_llm() -> None:
    tool = _tool()
    config = AliyunLLM(
        api_key="aliyun-key",
        base_url="https://example.com/v1/chat/completions",
        model="qwen-plus",
        tools=[tool],
    ).to_config()

    assert config["tools"] == [tool]


def test_with_tools_preserves_other_advanced_features() -> None:
    agent = Agent(
        test_client(), advanced_features=AdvancedFeatures(enable_sal=True)
    ).with_tools()

    assert agent.advanced_features is not None
    assert agent.advanced_features.enable_sal is True
    assert agent.advanced_features.enable_tools is True
