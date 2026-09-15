from test_helpers import test_client

from agora_agent import (
    AdvancedFeatures,
    Agent,
    LlmToolConfig,
    LlmToolFunctionConfig,
    LlmToolFunctionParametersConfig,
    LlmToolServerConfig,
    McpServerConfig,
    OpenAI,
    OpenAIGPTLive,
    OpenAIRealtime,
)
from agora_agent.agentkit.vendors.cn import AliyunLLM, BytedanceLLM, DeepSeekLLM, QwenOmni, TencentLLM


def _tool() -> dict:
    return {
        "type": "function",
        "function": {
            "name": "lookup_order",
            "parameters": {"type": "object", "properties": {}},
        },
        "server": {"method": "GET", "url": "https://example.com/orders"},
    }


def _typed_tool() -> LlmToolConfig:
    return LlmToolConfig(
        function=LlmToolFunctionConfig(
            name="lookup_order",
            parameters=LlmToolFunctionParametersConfig(properties={}),
        ),
        server=LlmToolServerConfig(method="GET", url="https://example.com/orders"),
    )


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


def test_global_and_cn_llms_accept_exported_typed_tools() -> None:
    expected = [_tool()]

    global_config = OpenAI(
        api_key="openai-key",
        base_url="https://api.openai.com/v1/chat/completions",
        model="gpt-4o-mini",
        tools=[_typed_tool()],
    ).to_config()
    cn_config = AliyunLLM(
        api_key="aliyun-key",
        base_url="https://example.com/v1/chat/completions",
        model="qwen-plus",
        tools=[_typed_tool()],
    ).to_config()

    assert global_config["tools"] == expected
    assert cn_config["tools"] == expected


def test_with_tools_preserves_other_advanced_features() -> None:
    agent = Agent(
        test_client(), advanced_features=AdvancedFeatures(enable_sal=True)
    ).with_tools()

    assert agent.advanced_features is not None
    assert agent.advanced_features.enable_sal is True
    assert agent.advanced_features.enable_tools is True


def test_typed_mcp_server_is_supported_by_llm() -> None:
    server = McpServerConfig(
        name="orders1",
        endpoint="https://example.com/mcp",
        headers={"Authorization": "Bearer token"},
        allowed_tools=["lookup_order"],
        timeout_ms=2500,
    )

    config = OpenAI(model="gpt-4o-mini", mcp_servers=[server]).to_config()

    assert config["mcp_servers"] == [
        {
            "name": "orders1",
            "endpoint": "https://example.com/mcp",
            "transport": "streamable_http",
            "headers": {"Authorization": "Bearer token"},
            "allowed_tools": ["lookup_order"],
            "timeout_ms": 2500,
        }
    ]


def test_mllm_supports_typed_tools_and_mcp_servers() -> None:
    config = OpenAIRealtime(
        api_key="openai-key",
        tools=[_typed_tool()],
        mcp_servers=[McpServerConfig(name="orders1", endpoint="https://example.com/mcp")],
    ).to_config()

    assert config["tools"][0]["function"]["name"] == "lookup_order"
    assert config["mcp_servers"] == [
        {
            "name": "orders1",
            "endpoint": "https://example.com/mcp",
            "transport": "streamable_http",
        }
    ]
    assert "tools" not in config.get("params", {})
    assert "mcp_servers" not in config.get("params", {})


def test_preview_mllm_supports_typed_tools() -> None:
    config = OpenAIGPTLive(api_key="openai-key", tools=[_typed_tool()]).to_config()

    assert config["tools"][0]["function"]["name"] == "lookup_order"
    assert "tools" not in config["params"]


def test_all_cn_llms_and_qwen_support_typed_tools_and_mcp_servers() -> None:
    server = McpServerConfig(name="orders1", endpoint="https://example.com/mcp")
    llm_configs = [
        vendor(
            api_key="cn-key",
            base_url="https://cn-llm.example.com/v1/chat/completions",
            model="cn-model",
            tools=[_typed_tool()],
            mcp_servers=[server],
        ).to_config()
        for vendor in (AliyunLLM, BytedanceLLM, DeepSeekLLM, TencentLLM)
    ]
    qwen_config = QwenOmni(
        api_key="aliyun-key",
        url="wss://dashscope.example.com/realtime",
        model="qwen-omni-turbo-realtime",
        tools=[_typed_tool()],
        mcp_servers=[server],
    ).to_config()

    for config in (*llm_configs, qwen_config):
        assert config["tools"][0]["function"]["name"] == "lookup_order"
        assert config["mcp_servers"] == [
            {
                "name": "orders1",
                "endpoint": "https://example.com/mcp",
                "transport": "streamable_http",
            }
        ]
        assert "tools" not in config["params"]
        assert "mcp_servers" not in config["params"]

    assert [config["vendor"] for config in llm_configs] == [
        "aliyun",
        "bytedance",
        "deepseek",
        "tencent",
    ]
    assert qwen_config["vendor"] == "qwen_omni"
