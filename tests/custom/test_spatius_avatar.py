import pytest
from types import SimpleNamespace

from agora_agent.agentkit import Agent, AgentSession, validate_avatar_config
from agora_agent.agentkit.avatar_types import is_spatius_avatar
from agora_agent.agentkit.vendors import SpatiusAvatar
from test_helpers import test_client as _test_client

APP_ID = "0" * 32
APP_CERTIFICATE = "1" * 32


class _Client:
    auth_mode = "basic"
    app_id = APP_ID
    app_certificate = APP_CERTIFICATE

    def __init__(self):
        self.agents = SimpleNamespace(
            start=lambda *args, **kwargs: SimpleNamespace(agent_id="agent-1")
        )
        self.agent_management = object()


def _session(agent):
    return AgentSession(
        client=_Client(),
        agent=agent,
        app_id=APP_ID,
        app_certificate=APP_CERTIFICATE,
        name="test",
        channel="room",
        agent_uid="1",
        remote_uids=["100"],
    )


def test_spatius_avatar_to_config_shape() -> None:
    config = SpatiusAvatar(
        spatius_api_key="spatius-key",
        spatius_app_id="spatius-app",
        spatius_avatar_id="spatius-avatar",
        agora_uid="2",
        agora_token="avatar-token",
        sample_rate=24000,
    ).to_config()

    assert config == {
        "enable": True,
        "vendor": "spatius",
        "params": {
            "spatius_api_key": "spatius-key",
            "spatius_app_id": "spatius-app",
            "spatius_avatar_id": "spatius-avatar",
            "agora_uid": "2",
            "agora_token": "avatar-token",
            "sample_rate": 24000,
        },
    }
    assert is_spatius_avatar(config)


@pytest.mark.parametrize(
    ("params", "message"),
    [
        ({}, "Spatius avatar requires spatius_api_key"),
        (
            {"spatius_api_key": "key"},
            "Spatius avatar requires spatius_app_id",
        ),
        (
            {"spatius_api_key": "key", "spatius_app_id": "app"},
            "Spatius avatar requires spatius_avatar_id",
        ),
        (
            {
                "spatius_api_key": "key",
                "spatius_app_id": "app",
                "spatius_avatar_id": "avatar",
            },
            "Spatius avatar requires agora_uid",
        ),
    ],
)
def test_validate_avatar_config_rejects_incomplete_spatius(
    params: dict, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        validate_avatar_config({"vendor": "spatius", "params": params})


def test_validate_avatar_config_requires_agora_token_at_session_time() -> None:
    with pytest.raises(ValueError, match="Spatius avatar requires agora_token"):
        validate_avatar_config(
            {
                "vendor": "spatius",
                "params": {
                    "spatius_api_key": "key",
                    "spatius_app_id": "app",
                    "spatius_avatar_id": "avatar",
                    "agora_uid": "2",
                },
            },
            require_session_fields=True,
        )


def test_spatius_avatar_enrichment_generates_token() -> None:
    agent = Agent(_test_client()).with_avatar(
        SpatiusAvatar(
            spatius_api_key="spatius-key",
            spatius_app_id="spatius-app",
            spatius_avatar_id="spatius-avatar",
            agora_uid="2",
            sample_rate=24000,
        )
    )
    session = _session(agent)

    properties = session._build_start_properties(  # noqa: SLF001
        {"app_id": APP_ID, "app_certificate": APP_CERTIFICATE},
        skip_vendor_validation_categories=set(),
        allow_missing_vendor_categories={"tts", "llm", "asr"},
    )

    params = properties["avatar"]["params"]
    assert params["agora_token"]
    assert params["agora_token"] != properties["token"]
    assert params["agora_uid"] == "2"
