import pytest
from pydantic import ValidationError

from agora_agent.agentkit import LlmGreetingConfigs
from agora_agent.agentkit.vendors import GenericAvatar, OpenAI, OpenAIRealtime, XaiGrok


def test_xai_grok_serializes_v27_shape_without_style():
    config = XaiGrok(
        api_key="xai-key",
        voice="eve",
        language="en",
        sample_rate=24000,
        output_modalities=["audio", "text"],
        params={"temperature": 0.2},
    ).to_config()

    assert config["vendor"] == "xai"
    assert config["url"] == "wss://api.x.ai/v1/realtime"
    assert config["api_key"] == "xai-key"
    assert config["params"] == {
        "temperature": 0.2,
        "voice": "eve",
        "language": "en",
        "sample_rate": 24000,
    }
    assert config["output_modalities"] == ["audio", "text"]
    assert "style" not in config


def test_xai_grok_emits_params_even_when_empty():
    assert XaiGrok(api_key="xai-key").to_config()["params"] == {}



def test_mllm_rejects_fields_not_in_core_contract():
    with pytest.raises(ValidationError):
        OpenAIRealtime(api_key="openai-key", predefined_tools=["_publish_message"])

    with pytest.raises(ValidationError):
        XaiGrok(api_key="xai-key", max_history=10)


def test_generic_avatar_omits_session_enriched_fields_when_unset():
    config = GenericAvatar(
        api_key="avatar-key",
        api_base_url="https://avatar.example.com",
        avatar_id="avatar-1",
        agora_uid="2",
    ).to_config()

    assert config == {
        "enable": True,
        "vendor": "generic",
        "params": {
            "api_key": "avatar-key",
            "api_base_url": "https://avatar.example.com",
            "avatar_id": "avatar-1",
            "agora_uid": "2",
        },
    }


def test_vertex_ai_explicit_fields_override_additional_params():
    from agora_agent.agentkit.vendors import VertexAI

    config = VertexAI(
        model="explicit-model",
        project_id="explicit-project",
        location="explicit-region",
        adc_credentials_string="{}",
        additional_params={
            "model": "should-be-overridden",
            "project_id": "should-be-overridden",
            "location": "should-be-overridden",
            "adc_credentials_string": "should-be-overridden",
            "extra_key": "kept",
        },
    ).to_config()

    assert config["vendor"] == "vertexai"
    # routing fields are top-level, not inside params
    assert config["project_id"] == "explicit-project"
    assert config["location"] == "explicit-region"
    assert config["adc_credentials_string"] == "{}"
    # model and extra_key live inside params
    assert config["params"]["model"] == "explicit-model"
    assert config["params"]["extra_key"] == "kept"


def test_gemini_live_explicit_fields_override_additional_params():
    from agora_agent.agentkit.vendors import GeminiLive

    config = GeminiLive(
        api_key="key",
        model="explicit-model",
        additional_params={
            "model": "should-be-overridden",
            "extra_key": "kept",
        },
    ).to_config()

    assert config["params"]["model"] == "explicit-model"
    assert config["params"]["extra_key"] == "kept"


def test_llm_greeting_configs_interruptable_serializes():
    config = OpenAI(
        api_key="openai-key",
        model="gpt-4o",
        base_url="https://api.openai.com/v1/chat/completions",
        greeting_configs={"mode": "single_first", "interruptable": False},
    ).to_config()

    assert config["greeting_configs"]["mode"] == "single_first"
    assert config["greeting_configs"]["interruptable"] is False
