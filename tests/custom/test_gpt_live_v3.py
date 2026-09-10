import pytest

from agora_agent import OpenAIGPTLive


def test_alpha_selector_defaults_to_v3_and_mcp_transport_is_normalized():
    servers = [{"name": "lookup", "endpoint": "https://tools.example/mcp"}]
    config = OpenAIGPTLive(api_key="test", mcp_servers=servers).to_config()

    assert config["params"] == {
        "model": "gpt-live-1-diamond-alpha",
        "alpha_selector": "quicksilver=v3",
    }
    assert config["mcp_servers"] == [{**servers[0], "transport": "streamable_http"}]
    assert "transport" not in servers[0]


def test_v3_options_preserve_zero_false_and_explicit_precedence():
    original = {"model": "other", "prompt": "other", "output_idle_end_ms": 900}
    config = OpenAIGPTLive(
        api_key="test", model="gpt-live-1-diamond-alpha", voice="cedar",
        instructions="alias", prompt="Be brief", output_idle_end_ms=0,
        input_idle_end_ms=1500, output_silence_peak=0, output_sample_rate=24000,
        output_buffer_ms=-1, input_batch_ms=0, tool_enabled=False,
        delegation="client", responses_model="delegate",
        alpha_selector="custom=v4",
        interrupt_on_user_turn=False, headers='{"X-Test":"yes"}',
        session_params={"context_management": {"type": "compaction"}}, params=original,
    ).to_config()
    params = config["params"]
    assert params == {
        "model": "gpt-live-1-diamond-alpha", "voice": "cedar", "prompt": "Be brief",
        "output_idle_end_ms": 0,
        "input_idle_end_ms": 1500, "output_silence_peak": 0, "output_sample_rate": 24000,
        "output_buffer_ms": -1, "input_batch_ms": 0, "tool_enabled": False,
        "delegation": "client", "responses_model": "delegate",
        "alpha_selector": "custom=v4",
        "interrupt_on_user_turn": False, "headers": '{"X-Test":"yes"}',
        "session_params": {"context_management": {"type": "compaction"}},
    }
    assert original == {"model": "other", "prompt": "other", "output_idle_end_ms": 900}


@pytest.mark.parametrize("options, expected", [
    ({}, "wss://api.openai.com/v1/live/sessions"),
    ({"base_url": "wss://proxy.test/", "path": "custom"}, "wss://proxy.test/custom"),
    ({"url": "wss://proxy.test/v1/live?x=1", "base_url": "wss://unused.test"}, "wss://proxy.test/v1/live?x=1"),
    ({"url": "wss://api.openai.com/v1/live?x=1"}, "wss://api.openai.com/v1/live/sessions?x=1"),
])
def test_endpoint_precedence(options, expected):
    assert OpenAIGPTLive(api_key="test", **options).to_config()["url"] == expected


@pytest.mark.parametrize("field", ["model", "delegation", "audio", "instructions", "input"])
def test_session_escape_hatch_cannot_override_modelled_fields(field):
    with pytest.raises(ValueError, match="cannot override"):
        OpenAIGPTLive(api_key="test", params={"session_params": {field: {}}}).to_config()


def test_unsupported_turn_detection_warns_and_is_removed():
    with pytest.warns(UserWarning, match="ignores turn_detection"):
        config = OpenAIGPTLive(api_key="test", params={"turn_detection": {}}).to_config()
    assert "turn_detection" not in config and "turn_detection" not in config["params"]


def test_legacy_instructions_alias_and_pending_fields():
    config = OpenAIGPTLive(api_key="test", instructions="Be brief", params={
        "voice": {"id": "voice_123"}, "context_management": {"type": "compaction"},
    }).to_config()
    assert config["params"]["prompt"] == "Be brief"
    assert "instructions" not in config["params"]
    assert config["params"]["voice"] == {"id": "voice_123"}


@pytest.mark.parametrize("params", [
    {"delegation": "invalid"},
    {"session_params": None},
    {"input_audio_transcription": {}},
    {"headers": "not-json"},
    {"headers": "[]"},
])
def test_invalid_v3_config_is_rejected(params):
    with pytest.raises(ValueError):
        OpenAIGPTLive(api_key="test", params=params).to_config()


def test_json_headers_are_redacted_without_mutating_config():
    from agora_agent.agentkit.debug import REDACTED, redact_secrets

    config = OpenAIGPTLive(api_key="test", headers='{"Authorization":"private-value"}').to_config()
    assert redact_secrets(config)["params"]["headers"] == REDACTED
    assert config["params"]["headers"] == '{"Authorization":"private-value"}'


@pytest.mark.parametrize("url", ["https://api.openai.com/v1/live/sessions", "/v1/live/sessions", "wss:///missing-host"])
def test_invalid_websocket_endpoint_is_rejected(url):
    with pytest.raises(ValueError, match="full ws"):
        OpenAIGPTLive(api_key="test", url=url).to_config()
