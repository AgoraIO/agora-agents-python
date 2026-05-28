from agora_agent import AmazonBedrock, CustomLLM, Dify, Groq, VertexAILLM


def test_groq_serializes_as_openai_compatible() -> None:
    config = Groq(api_key="groq-key", model="llama-3.3-70b-versatile").to_config()

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


def test_amazon_bedrock_serializes_as_anthropic_style() -> None:
    config = AmazonBedrock(
        api_key="bedrock-key",
        url="https://bedrock.example.com/messages",
        model="anthropic.claude-3-5-sonnet-20241022-v2:0",
    ).to_config()

    assert config["api_key"] == "bedrock-key"
    assert config["style"] == "anthropic"
    assert config["params"]["model"] == "anthropic.claude-3-5-sonnet-20241022-v2:0"


def test_dify_serializes_conversation_fields() -> None:
    config = Dify(
        api_key="dify-key",
        url="https://api.dify.ai/v1/chat-messages",
        user="user-1",
        conversation_id="conversation-1",
    ).to_config()

    assert config["api_key"] == "dify-key"
    assert config["style"] == "dify"
    assert config["params"]["user"] == "user-1"
    assert config["params"]["conversation_id"] == "conversation-1"
