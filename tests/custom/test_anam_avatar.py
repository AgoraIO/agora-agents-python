import pytest

from agora_agent.agentkit import validate_avatar_config
from agora_agent.agentkit.avatar_types import is_anam_avatar
from agora_agent.agentkit.vendors import AnamAvatar


def test_anam_avatar_to_config_shape() -> None:
    config = AnamAvatar(
        api_key="anam-key",
        avatar_id="anam-avatar",
    ).to_config()

    assert config == {
        "enable": True,
        "vendor": "anam",
        "params": {
            "api_key": "anam-key",
            "avatar_id": "anam-avatar",
        },
    }
    assert is_anam_avatar(config)


def test_anam_avatar_serializes_portrait_options_and_overrides_additional_params() -> None:
    config = AnamAvatar(
        api_key="anam-key",
        avatar_id="anam-avatar",
        avatar_model="cara_mk4",
        video_width=720,
        video_height=1280,
        additional_params={
            "avatar_model": "overridden-model",
            "video_width": 1,
            "video_height": 2,
        },
    ).to_config()

    assert config["params"] == {
        "api_key": "anam-key",
        "avatar_id": "anam-avatar",
        "avatar_model": "cara_mk4",
        "video_width": 720,
        "video_height": 1280,
    }


@pytest.mark.parametrize("kwargs", [{"video_width": 720}, {"video_height": 1280}])
def test_anam_avatar_requires_video_dimensions_as_pair(kwargs: dict) -> None:
    with pytest.raises(ValueError, match="Anam avatar requires video_width and video_height together"):
        AnamAvatar(api_key="anam-key", avatar_id="anam-avatar", **kwargs)


@pytest.mark.parametrize(
    ("params", "message"),
    [
        ({}, "Anam avatar requires api_key"),
        ({"api_key": "key"}, "Anam avatar requires avatar_id"),
        (
            {"api_key": "key", "avatar_id": "avatar", "video_width": 720},
            "Anam avatar requires video_width and video_height together",
        ),
        (
            {"api_key": "key", "avatar_id": "avatar", "video_height": 1280},
            "Anam avatar requires video_width and video_height together",
        ),
    ],
)
def test_validate_avatar_config_rejects_incomplete_anam(
    params: dict, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        validate_avatar_config({"vendor": "anam", "params": params})
