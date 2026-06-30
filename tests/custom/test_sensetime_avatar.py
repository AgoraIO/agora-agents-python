import pytest
from types import SimpleNamespace
from typing import Any, Dict, List

from agora_agent.agentkit import Agent, AgentSession, validate_avatar_config
from agora_agent.agentkit.avatar_types import is_sensetime_avatar
from agora_agent.agentkit.vendors.cn import SenseTimeAvatar
from test_helpers import test_client

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


def _scene_list() -> List[Dict[str, Any]]:
    return [{"digital_role": {"face_feature_id": "role-1"}}]


def test_sensetime_avatar_to_config_shape() -> None:
    config = SenseTimeAvatar(
        agora_token="avatar-token",
        agora_uid="2",
        appId="sensetime-app-id",
        app_key="sensetime-app-key",
        sceneList=_scene_list(),
    ).to_config()

    assert config == {
        "enable": True,
        "vendor": "sensetime",
        "params": {
            "agora_token": "avatar-token",
            "agora_uid": "2",
            "appId": "sensetime-app-id",
            "app_key": "sensetime-app-key",
            "sceneList": _scene_list(),
        },
    }
    assert is_sensetime_avatar(config)


def test_sensetime_avatar_to_config_omits_token_when_not_provided() -> None:
    config = SenseTimeAvatar(
        agora_uid="2",
        app_key="sensetime-app-key",
        sceneList=_scene_list(),
    ).to_config()

    assert "agora_token" not in config["params"]
    assert config["params"]["agora_uid"] == "2"


def test_sensetime_avatar_to_config_omits_scene_list_when_not_provided() -> None:
    config = SenseTimeAvatar(
        agora_uid="2",
        app_key="sensetime-app-key",
    ).to_config()

    assert "sceneList" not in config["params"]
    assert config["params"]["agora_uid"] == "2"


@pytest.mark.parametrize(
    ("params", "message"),
    [
        ({}, "SenseTime avatar requires app_key"),
        (
            {"app_key": "key", "sceneList": _scene_list()},
            "SenseTime avatar requires agora_uid",
        ),
    ],
)
def test_validate_avatar_config_rejects_incomplete_sensetime(
    params: dict, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        validate_avatar_config({"vendor": "sensetime", "params": params})


def test_validate_avatar_config_requires_agora_token_at_session_time() -> None:
    with pytest.raises(ValueError, match="SenseTime avatar requires agora_token"):
        validate_avatar_config(
            {
                "vendor": "sensetime",
                "params": {
                    "app_key": "key",
                    "sceneList": _scene_list(),
                    "agora_uid": "2",
                },
            },
            require_session_fields=True,
        )


def test_validate_avatar_config_allows_missing_scene_list() -> None:
    validate_avatar_config(
        {
            "vendor": "sensetime",
            "params": {
                "app_key": "key",
                "agora_uid": "2",
            },
        }
    )


def test_sensetime_avatar_session_validation_and_token_passthrough() -> None:
    agent = Agent(test_client()).with_avatar(
        SenseTimeAvatar(
            agora_token="avatar-token",
            agora_uid="2",
            app_key="sensetime-app-key",
            sceneList=_scene_list(),
        )
    )
    session = _session(agent)

    session._validate_avatar_config()  # noqa: SLF001

    properties = session._build_start_properties(  # noqa: SLF001
        {"app_id": APP_ID, "app_certificate": APP_CERTIFICATE},
        skip_vendor_validation_categories=set(),
        allow_missing_vendor_categories={"tts", "llm", "asr"},
    )

    assert properties["avatar"]["params"]["agora_token"] == "avatar-token"
    assert properties["avatar"]["params"]["sceneList"] == _scene_list()


def test_sensetime_avatar_enrichment_generates_token() -> None:
    agent = Agent(test_client()).with_avatar(
        SenseTimeAvatar(
            agora_uid="2",
            app_key="sensetime-app-key",
            sceneList=_scene_list(),
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


def test_sensetime_avatar_user_token_is_not_overwritten() -> None:
    agent = Agent(test_client()).with_avatar(
        SenseTimeAvatar(
            agora_uid="2",
            agora_token="user-token",
            app_key="sensetime-app-key",
            sceneList=_scene_list(),
        )
    )
    session = _session(agent)

    properties = session._build_start_properties(  # noqa: SLF001
        {"app_id": APP_ID, "app_certificate": APP_CERTIFICATE},
        skip_vendor_validation_categories=set(),
        allow_missing_vendor_categories={"tts", "llm", "asr"},
    )

    assert properties["avatar"]["params"]["agora_token"] == "user-token"


def test_sensetime_avatar_enrichment_without_scene_list() -> None:
    agent = Agent(test_client()).with_avatar(
        SenseTimeAvatar(
            agora_uid="2",
            app_key="sensetime-app-key",
        )
    )
    session = _session(agent)

    properties = session._build_start_properties(  # noqa: SLF001
        {"app_id": APP_ID, "app_certificate": APP_CERTIFICATE},
        skip_vendor_validation_categories=set(),
        allow_missing_vendor_categories={"tts", "llm", "asr"},
    )

    params = properties["avatar"]["params"]
    assert "sceneList" not in params
    assert params["agora_uid"] == "2"
    assert params["agora_token"]
