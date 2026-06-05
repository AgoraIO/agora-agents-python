from agora_agent.agentkit import (
    Agent,
    AvatarConfig,
    AvatarVendor,
    LlmConfig,
    LlmStyle,
    MllmConfig,
    MllmVendor,
    SttConfig,
    SttVendor,
    TtsConfig,
)
import pytest

from agora_agent.agentkit.vendors import (
    AkoolAvatar,
    ElevenLabsTTS,
    LiveAvatarAvatar,
    OpenAI,
    OpenAIRealtime,
)


def _parameter(config, key):
    parameters = config["parameters"]
    if isinstance(parameters, dict):
        return parameters[key]
    return getattr(parameters, key)


class _CopyOnlyModel:
    def __init__(self, **values):
        self.values = values

    def copy(self, update=None):
        return _CopyOnlyModel(**{**self.values, **(update or {})})


def test_generated_core_aliases_are_public():
    assert LlmConfig is not None
    assert LlmStyle is not None
    assert SttConfig is not None
    assert SttVendor is not None
    assert TtsConfig is not None
    assert MllmConfig is not None
    assert MllmVendor is not None
    assert AvatarConfig is not None
    assert AvatarVendor is not None


def test_model_copy_helper_supports_pydantic_v1_copy_api():
    copied = Agent._copy_model_update(_CopyOnlyModel(enable_rtm=True), {"data_channel": "rtm"})  # noqa: SLF001

    assert copied.values == {"enable_rtm": True, "data_channel": "rtm"}


def test_with_audio_scenario_sets_session_parameter():
    agent = Agent(name="test").with_audio_scenario("chorus")

    assert _parameter(agent.config, "audio_scenario") == "chorus"


def test_with_audio_scenario_preserves_existing_parameters():
    agent = Agent(name="test", parameters={"enable_metrics": True}).with_audio_scenario(
        "chorus"
    )

    assert _parameter(agent.config, "enable_metrics") is True
    assert _parameter(agent.config, "audio_scenario") == "chorus"


def test_enable_rtm_defaults_data_channel_to_rtm():
    properties = Agent(name="test", advanced_features={"enable_rtm": True}).to_properties(
        channel="room",
        agent_uid="1",
        remote_uids=["100"],
        token="token",
        skip_vendor_validation=True,
    )

    assert properties.parameters.data_channel == "rtm"


def test_enable_rtm_preserves_explicit_data_channel():
    properties = Agent(
        name="test",
        advanced_features={"enable_rtm": True},
        parameters={"data_channel": "datastream"},
    ).to_properties(
        channel="room",
        agent_uid="1",
        remote_uids=["100"],
        token="token",
        skip_vendor_validation=True,
    )

    assert properties.parameters.data_channel == "datastream"


def test_vendor_config_takes_priority_over_agent_level_convenience_fields():
    agent = (
        Agent(name="test")
        .with_llm(
            OpenAI(
                model="gpt-4o-mini",
                greeting_message="vendor greeting",
                failure_message="vendor failure",
                max_history=1,
            )
        )
        .with_tts(ElevenLabsTTS(key="tts-key", model_id="model", voice_id="voice", base_url="wss://api.elevenlabs.io/v1"))
        .with_greeting("agent greeting")
        .with_failure_message("agent failure")
        .with_max_history(2)
    )

    properties = agent.to_properties(
        channel="room",
        agent_uid="1",
        remote_uids=["100"],
        token="token",
    )

    assert properties.llm.greeting_message == "vendor greeting"
    assert properties.llm.failure_message == "vendor failure"
    assert properties.llm.max_history == 1


def test_avatar_sample_rate_validation_works_when_tts_added_after_avatar():
    agent = Agent(name="test").with_avatar(
        LiveAvatarAvatar(api_key="avatar-key", quality="medium", agora_uid="2")
    )

    with pytest.raises(ValueError, match="24000"):
        agent.with_tts(
            ElevenLabsTTS(key="tts-key", model_id="model", voice_id="voice", base_url="wss://api.elevenlabs.io/v1", sample_rate=16000)
        )


def test_avatar_sample_rate_validation_uses_wrapper_sample_rate():
    agent = (
        Agent(name="test")
        .with_avatar(AkoolAvatar(api_key="avatar-key"))
        .with_tts(
            ElevenLabsTTS(key="tts-key", model_id="model", voice_id="voice", base_url="wss://api.elevenlabs.io/v1", sample_rate=16000)
        )
    )

    assert agent.tts_sample_rate == 16000


def test_with_mllm_removes_deprecated_advanced_features_enable_mllm():
    properties = (
        Agent(
            name="test",
            advanced_features={"enable_mllm": True, "enable_rtm": True},
            greeting="hello from agent",
            failure_message="try again",
            max_history=5,
        )
        .with_mllm(OpenAIRealtime(api_key="openai-key"))
        .to_properties(
            channel="room",
            agent_uid="1",
            remote_uids=["100"],
            token="rtc-token",
        )
    )

    assert properties.mllm is not None
    assert properties.mllm.enable is True
    assert properties.mllm.greeting_message == "hello from agent"
    assert properties.mllm.failure_message == "try again"
    mllm_dump = properties.mllm.model_dump(exclude_none=True)
    assert "max_history" not in mllm_dump
    assert properties.advanced_features is not None
    af_dump = properties.advanced_features.model_dump(exclude_none=True)
    assert "enable_mllm" not in af_dump
    assert af_dump.get("enable_rtm") is True


def test_to_properties_rejects_mllm_with_enabled_avatar():
    agent = (
        Agent(name="test")
        .with_mllm(OpenAIRealtime(api_key="mllm-key"))
        .with_avatar(
            LiveAvatarAvatar(
                api_key="avatar-key",
                quality="medium",
                agora_uid="2",
                agora_token="avatar-token",
            )
        )
    )

    with pytest.raises(ValueError, match="cascading"):
        agent.to_properties(
            channel="room",
            agent_uid="1",
            remote_uids=["100"],
            token="rtc-token",
        )


def test_to_properties_mllm_with_avatar_fires_before_token_generation():
    """The guard must fire before the token-generation step so callers get a
    clear, actionable error even when app_id/app_certificate are empty.
    """
    agent = (
        Agent(name="test")
        .with_mllm(OpenAIRealtime(api_key="mllm-key"))
        .with_avatar(
            LiveAvatarAvatar(
                api_key="avatar-key",
                quality="medium",
                agora_uid="2",
                agora_token="avatar-token",
            )
        )
    )

    with pytest.raises(ValueError, match="cascading"):
        agent.to_properties(
            channel="room",
            agent_uid="1",
            remote_uids=["100"],
            app_id="",
            app_certificate="",
        )


def test_to_properties_rejects_mllm_with_default_enabled_avatar():
    """Avatar with no `enable` field should be treated as enabled."""
    agent = Agent(name="test").with_mllm(OpenAIRealtime(api_key="mllm-key"))
    agent._avatar = {  # noqa: SLF001
        "vendor": "liveavatar",
        "params": {
            "api_key": "avatar-key",
            "quality": "high",
            "agora_uid": "200",
            "agora_token": "avatar-token",
        },
    }

    with pytest.raises(ValueError, match="cascading"):
        agent.to_properties(
            channel="room",
            agent_uid="1",
            remote_uids=["100"],
            token="rtc-token",
        )


def test_to_properties_allows_mllm_with_disabled_avatar_and_no_tts():
    properties = (
        Agent(name="test")
        .with_mllm(OpenAIRealtime(api_key="mllm-key"))
        .with_avatar(
            LiveAvatarAvatar(
                api_key="avatar-key",
                quality="medium",
                agora_uid="2",
                agora_token="avatar-token",
                enable=False,
            )
        )
        .to_properties(
            channel="room",
            agent_uid="1",
            remote_uids=["100"],
            token="rtc-token",
        )
    )

    assert properties.mllm is not None and properties.mllm.enable is True
    assert properties.tts is None
    assert properties.llm is None
    assert properties.asr is None
    assert properties.avatar is not None and properties.avatar.enable is False


def test_to_properties_mllm_without_tts_or_llm_succeeds():
    properties = (
        Agent(name="test")
        .with_mllm(OpenAIRealtime(api_key="mllm-key"))
        .to_properties(
            channel="room",
            agent_uid="1",
            remote_uids=["100"],
            token="rtc-token",
        )
    )

    assert properties.mllm is not None and properties.mllm.enable is True
    assert properties.tts is None
    assert properties.llm is None
    assert properties.asr is None
    assert properties.avatar is None
