import pytest
from pydantic import ValidationError

from agora_agent.agentkit.preview import (
    GeminiMLLM,
    GeminiMLLMModels,
    OpenAIGPTLive,
    PreviewFeatures,
    apply_preview_shape,
    required_preview_features,
)


def test_gemini_and_gpt_live_use_their_own_feature_gates():
    for vendor in (GeminiMLLM(api_key="test-key", model=GeminiMLLMModels.WALKIE_TALKIE), GeminiMLLM(api_key="test-key", model=GeminiMLLMModels.CLEVER_CHATTER)):
        properties = {"mllm": vendor.to_config()}
        assert required_preview_features(properties) == [PreviewFeatures.GEMINI_LIVE]
    assert required_preview_features({"mllm": OpenAIGPTLive(api_key="test-key").to_config()}) == [
        PreviewFeatures.LIVE_MODELS
    ]


def test_gemini_greeting_uses_preview_wire_field():
    properties = {"mllm": GeminiMLLM(api_key="test-key", model=GeminiMLLMModels.WALKIE_TALKIE).to_config()}
    properties["mllm"]["greeting_message"] = "Hello"
    apply_preview_shape(properties)
    assert properties["mllm"]["greeting"] == "Hello"
    assert "greeting_message" not in properties["mllm"]


def test_one_gemini_preview_class_supports_codenames_and_38_ids():
    assert GeminiMLLM(api_key="test-key", model="  ").to_config()["params"]["model"] == GeminiMLLMModels.WALKIE_TALKIE
    models = (
        (GeminiMLLMModels.WALKIE_TALKIE, "medium"),
        (GeminiMLLMModels.CLEVER_CHATTER, "medium"),
        (GeminiMLLMModels.LIVE_38, "medium"),
        (GeminiMLLMModels.LIVE_38_EXTENDED_THINKING, "medium"),
    )
    for model, thinking in models:
        config = GeminiMLLM(api_key="test-key", model=model, thinking_level=thinking,
                            additional_params={"thinking_level": "high"}).to_config()
        assert config["params"]["model"] == model
        expected_thinking = thinking if model in (GeminiMLLMModels.CLEVER_CHATTER, GeminiMLLMModels.LIVE_38_EXTENDED_THINKING) else None
        assert config["params"].get("thinking_level") == expected_thinking
        assert required_preview_features({"mllm": config}) == [PreviewFeatures.GEMINI_LIVE]
        # Explicit IDs must route even in a hand-written config without the
        # SDK vendor's duplicate-key preview envelope.
        assert required_preview_features({"mllm": {"vendor": "gemini", "params": {"model": model}}}) == [
            PreviewFeatures.GEMINI_LIVE
        ]


def test_gemini_mllm_rejects_blank_api_key():
    with pytest.raises(ValidationError, match="GeminiMLLM requires api_key"):
        GeminiMLLM(api_key="  ")
