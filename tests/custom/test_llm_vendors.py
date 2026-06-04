import pytest

from agora_agent import AmazonBedrock, Anthropic, AzureOpenAI, CustomLLM, Dify, Gemini, Groq, OpenAI, VertexAILLM


def test_groq_serializes_as_openai_compatible() -> None:
    config = Groq(api_key="groq-key", model="llama-3.3-70b-versatile", base_url="https://api.groq.com/openai/v1/chat/completions").to_config()

    assert config["url"] == "https://api.groq.com/openai/v1/chat/completions"
    assert config["api_key"] == "groq-key"
    assert config["style"] == "openai"
    assert config["params"]["model"] == "llama-3.3-70b-versatile"


def test_custom_llm_marks_request_as_custom() -> None:
    config = CustomLLM(api_key="key", model="model", base_url="https://llm.example.com/chat").to_config()

    assert config["url"] == "https://llm.example.com/chat"
    assert config["api_key"] == "key"
    assert config["vendor"] == "custom"
    assert config["style"] == "openai"


def test_anthropic_serializes_required_claude_fields() -> None:
    config = Anthropic(
        api_key="anthropic-key",
        model="claude-3-5-sonnet-20241022",
        url="https://api.anthropic.com/v1/messages",
        headers={"anthropic-version": "2023-06-01"},
        max_tokens=1024,
    ).to_config()

    assert config["url"] == "https://api.anthropic.com/v1/messages"
    assert config["api_key"] == "anthropic-key"
    assert config["style"] == "anthropic"
    assert config["headers"]["anthropic-version"] == "2023-06-01"
    assert config["params"]["model"] == "claude-3-5-sonnet-20241022"
    assert config["params"]["max_tokens"] == 1024


def test_azure_openai_includes_required_model_param() -> None:
    config = AzureOpenAI(
        api_key="azure-key",
        endpoint="https://example.openai.azure.com",
        deployment_name="deployment",
        model="gpt-4o",
    ).to_config()

    assert config["api_key"] == "azure-key"
    assert config["vendor"] == "azure"
    assert config["style"] == "openai"
    assert config["params"]["model"] == "gpt-4o"


def test_vertex_ai_llm_includes_project_routing() -> None:
    config = VertexAILLM(
        api_key="vertex-token",
        model="gemini-2.0-flash",
        project_id="project",
        location="us-central1",
    ).to_config()

    assert config["api_key"] == "vertex-token"
    assert config["style"] == "gemini"
    assert config["params"]["model"] == "gemini-2.0-flash"
    assert config["params"]["project_id"] == "project"
    assert config["params"]["location"] == "us-central1"


def test_amazon_bedrock_serializes_as_bedrock_style() -> None:
    config = AmazonBedrock(
        access_key="aws-access",
        secret_key="aws-secret",
        region="us-east-1",
        model="anthropic.claude-3-5-sonnet-20241022-v2:0",
    ).to_config()

    assert config["access_key"] == "aws-access"
    assert config["secret_key"] == "aws-secret"
    assert config["region"] == "us-east-1"
    assert config["url"] == "https://bedrock-runtime.us-east-1.amazonaws.com/model/anthropic.claude-3-5-sonnet-20241022-v2:0/converse-stream"
    assert config["model"] == "anthropic.claude-3-5-sonnet-20241022-v2:0"
    assert config["style"] == "bedrock"


def test_dify_serializes_conversation_fields() -> None:
    config = Dify(
        api_key="dify-key",
        url="https://api.dify.ai/v1/chat-messages",
        model="default",
        user="user-1",
        conversation_id="conversation-1",
    ).to_config()

    assert config["api_key"] == "dify-key"
    assert config["style"] == "dify"
    assert config["params"]["model"] == "default"
    assert config["params"]["user"] == "user-1"
    assert config["params"]["conversation_id"] == "conversation-1"


def test_llm_vendors_reject_missing_required_models() -> None:
    with pytest.raises(Exception, match="model"):
        OpenAI(api_key="openai-key", base_url="https://api.openai.com/v1/chat/completions")

    with pytest.raises(Exception, match="model"):
        Anthropic(
            api_key="anthropic-key",
            url="https://api.anthropic.com/v1/messages",
            headers={"anthropic-version": "2023-06-01"},
            max_tokens=1024,
        )

    with pytest.raises(Exception, match="model"):
        Gemini(api_key="google-key")

    with pytest.raises(Exception, match="model"):
        Groq(api_key="groq-key", base_url="https://api.groq.com/openai/v1/chat/completions")

    with pytest.raises(Exception, match="model"):
        VertexAILLM(api_key="vertex-token", project_id="project", location="us-central1")

    with pytest.raises(Exception, match="model"):
        AmazonBedrock(access_key="aws-access", secret_key="aws-secret", region="us-east-1")


def test_openai_managed_mode_is_restricted_to_supported_models() -> None:
    assert OpenAI(model="gpt-5-mini").to_config()["params"]["model"] == "gpt-5-mini"

    with pytest.raises(Exception, match="api_key"):
        OpenAI(model="gpt-4o")

    with pytest.raises(Exception, match="does not allow vendor"):
        OpenAI(model="gpt-5-mini", vendor="custom")
