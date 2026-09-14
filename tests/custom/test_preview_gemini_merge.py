from agora_agent.agentkit.preview import (
    GeminiCleverChatter,
    GeminiWalkieTalkie,
    PreviewFeatures,
    OpenAIGPTLive,
    apply_preview_shape,
    required_preview_features,
)


def test_gemini_and_gpt_live_use_their_own_feature_gates():
    for vendor in (GeminiWalkieTalkie(api_key="test-key"), GeminiCleverChatter(api_key="test-key")):
        properties = {"mllm": vendor.to_config()}
        assert required_preview_features(properties) == [PreviewFeatures.GEMINI_LIVE]
    assert required_preview_features({"mllm": OpenAIGPTLive(api_key="test-key").to_config()}) == [
        PreviewFeatures.LIVE_MODELS
    ]


def test_gemini_greeting_uses_preview_wire_field():
    properties = {"mllm": GeminiWalkieTalkie(api_key="test-key").to_config()}
    properties["mllm"]["greeting_message"] = "Hello"
    apply_preview_shape(properties)
    assert properties["mllm"]["greeting"] == "Hello"
    assert "greeting_message" not in properties["mllm"]
