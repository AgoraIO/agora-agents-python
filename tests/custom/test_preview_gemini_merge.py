import pytest
from pydantic import ValidationError

from agora_agent.agentkit.preview import (
    GeminiLiveModels,
    OpenAIGPTLive,
    PreviewFeatures,
    apply_preview_shape,
    required_preview_features,
)
from agora_agent.agentkit.vendors.mllm import GeminiLive


def test_only_gemini_live_uses_a_preview_feature_gate():
    for vendor in (GeminiLive(api_key="test-key", model=GeminiLiveModels.LIVE_38), GeminiLive(api_key="test-key", model=GeminiLiveModels.LIVE_38_EXTENDED_THINKING)):
        properties = {"mllm": vendor.to_config()}
        assert required_preview_features(properties) == [PreviewFeatures.GEMINI_LIVE]
    assert required_preview_features({"mllm": OpenAIGPTLive(api_key="test-key").to_config()}) == []


def test_gemini_greeting_uses_preview_wire_field():
    properties = {"mllm": GeminiLive(api_key="test-key", model=GeminiLiveModels.LIVE_38).to_config()}
    properties["mllm"]["greeting_message"] = "Hello"
    apply_preview_shape(properties)
    assert properties["mllm"]["greeting"] == "Hello"
    assert "greeting_message" not in properties["mllm"]


def test_one_gemini_preview_class_supports_public_38_ids():
    assert GeminiLive(api_key="test-key", model="  ").to_config()["params"]["model"] == GeminiLiveModels.LIVE_38
    models = (
        (GeminiLiveModels.LIVE_38, "medium"),
        (GeminiLiveModels.LIVE_38_EXTENDED_THINKING, "medium"),
    )
    for model, thinking in models:
        config = GeminiLive(api_key="test-key", model=model, thinking_level=thinking,
                            additional_params={"thinking_level": "high", "api_key": "ignored-key"}).to_config()
        assert config["api_key"] == "test-key"
        assert "api_key" not in config["params"]
        assert config["params"]["model"] == model
        expected_thinking = thinking if model == GeminiLiveModels.LIVE_38_EXTENDED_THINKING else None
        assert config["params"].get("thinking_level") == expected_thinking
        assert required_preview_features({"mllm": config}) == [PreviewFeatures.GEMINI_LIVE]
        # Explicit IDs must route even in a hand-written config without the
        # SDK vendor's preview envelope.
        assert required_preview_features({"mllm": {"vendor": "gemini", "params": {"model": model}}}) == [
            PreviewFeatures.GEMINI_LIVE
        ]


def test_gemini_mllm_rejects_blank_api_key():
    with pytest.raises(ValidationError, match="GeminiLive requires api_key"):
        GeminiLive(api_key="  ")


def test_unknown_gemini_model_keeps_preview_greeting_without_nested_api_key():
    properties = {"mllm": GeminiLive(
        api_key="test-key", model="future-live-model", url="https://generativelanguage.googleapis.com"
    ).to_config()}
    properties["mllm"]["greeting_message"] = "Hello"
    apply_preview_shape(properties)
    assert properties["mllm"]["greeting"] == "Hello"
    assert "greeting_message" not in properties["mllm"]
