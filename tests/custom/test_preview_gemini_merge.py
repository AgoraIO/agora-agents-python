import pytest
from pydantic import ValidationError

from agora_agent.agentkit.preview import (
    GeminiLiveModels,
    OpenAIGPTLive,
    apply_preview_shape,
    required_preview_features,
)
from agora_agent.agentkit.vendors.mllm import GEMINI_MLLM_URL, GeminiLive


def test_gemini_live_models_use_production_routing():
    for vendor in (GeminiLive(api_key="test-key", model=GeminiLiveModels.LIVE_38), GeminiLive(api_key="test-key", model=GeminiLiveModels.LIVE_38_EXTENDED_THINKING)):
        properties = {"mllm": vendor.to_config()}
        assert required_preview_features(properties) == []
    assert required_preview_features({"mllm": OpenAIGPTLive(api_key="test-key").to_config()}) == []


def test_gemini_greeting_uses_production_wire_field():
    properties = {"mllm": GeminiLive(api_key="test-key", model=GeminiLiveModels.LIVE_38).to_config()}
    properties["mllm"]["greeting_message"] = "Hello"
    apply_preview_shape(properties)
    assert properties["mllm"]["greeting_message"] == "Hello"
    assert "greeting" not in properties["mllm"]


def test_gemini_production_class_supports_public_38_ids():
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
        assert config["url"] == GEMINI_MLLM_URL
        expected_thinking = thinking if model == GeminiLiveModels.LIVE_38_EXTENDED_THINKING else None
        assert config["params"].get("thinking_level") == expected_thinking
        assert required_preview_features({"mllm": config}) == []
        assert required_preview_features({"mllm": {"vendor": "gemini", "params": {"model": model}}}) == []


def test_gemini_mllm_rejects_blank_api_key():
    with pytest.raises(ValidationError, match="GeminiLive requires api_key"):
        GeminiLive(api_key="  ")


def test_unknown_gemini_model_keeps_production_greeting_without_nested_api_key():
    properties = {"mllm": GeminiLive(
        api_key="test-key", model="future-live-model", url="https://generativelanguage.googleapis.com"
    ).to_config()}
    properties["mllm"]["greeting_message"] = "Hello"
    apply_preview_shape(properties)
    assert properties["mllm"]["greeting_message"] == "Hello"
    assert "greeting" not in properties["mllm"]


def test_existing_gemini_models_preserve_additional_params():
    config = GeminiLive(
        api_key="test-key",
        model="gemini-live-2.5-flash",
        additional_params={"api_key": "legacy-nested-key", "thinking_level": "legacy-value"},
    ).to_config()

    assert config["url"] == ""
    assert config["params"]["api_key"] == "legacy-nested-key"
    assert config["params"]["thinking_level"] == "legacy-value"


def test_preview_gemini_imports_alias_production_objects():
    from agora_agent.agentkit.preview import GeminiLive as PreviewGeminiLive
    from agora_agent.agentkit.preview import GeminiLiveModels as PreviewGeminiLiveModels
    from agora_agent.agentkit.preview.vendors import build_gemini_preview_config

    assert PreviewGeminiLive is GeminiLive
    assert PreviewGeminiLiveModels is GeminiLiveModels
    vendor = PreviewGeminiLive(api_key="test-key", greeting_message="Hello")
    assert build_gemini_preview_config(vendor) == vendor.to_config()
    assert vendor.to_config()["greeting_message"] == "Hello"
