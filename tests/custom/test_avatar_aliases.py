import inspect
import json

import pytest
from pydantic import ValidationError

import agora_agent
import agora_agent.agentkit as agentkit
from agora_agent.agentkit import vendors
from agora_agent.agentkit.avatar_types import is_avatar_token_managed, validate_avatar_config
from agora_agent.agentkit.vendors.avatar import GenericAvatar, LemonSlice, Protoface, Tavus


@pytest.mark.parametrize("name", ["Tavus", "Protoface", "LemonSlice"])
def test_branded_avatar_exports_are_true_aliases(name: str) -> None:
    for module in (agora_agent, agentkit, vendors):
        assert getattr(module, name) is GenericAvatar
        assert name in module.__all__
        assert name in dir(module)
    assert inspect.signature(getattr(vendors, name)) == inspect.signature(GenericAvatar)


@pytest.mark.parametrize("avatar_type", [Tavus, Protoface, LemonSlice])
@pytest.mark.parametrize("enable", [None, False])
def test_branded_avatar_serializes_generic_configuration(avatar_type, enable) -> None:
    avatar = avatar_type(
        api_key="key",
        api_base_url="https://avatar.example.com",
        avatar_id="avatar-1",
        agora_uid="2",
        agora_appid="app",
        agora_channel="room",
        agora_token="token",
        enable=enable,
        additional_params={"custom": {"value": 1}, "api_key": "ignored"},
    )
    config = json.loads(json.dumps(avatar.to_config()))
    assert config == {
        "enable": enable if enable is not None else True,
        "vendor": "generic",
        "params": {
            "api_key": "key",
            "api_base_url": "https://avatar.example.com",
            "avatar_id": "avatar-1",
            "agora_uid": "2",
            "agora_appid": "app",
            "agora_channel": "room",
            "agora_token": "token",
            "custom": {"value": 1},
        },
    }
    assert avatar.required_sample_rate == 0
    assert is_avatar_token_managed(config)
    validate_avatar_config(config, require_session_fields=True)


@pytest.mark.parametrize("avatar_type", [Tavus, Protoface, LemonSlice])
def test_branded_avatar_preserves_required_and_optional_fields(avatar_type) -> None:
    required = dict(api_key="key", api_base_url="https://avatar.example.com", avatar_id="avatar-1", agora_uid="2")
    assert avatar_type(**required).to_config() == {"enable": True, "vendor": "generic", "params": required}
    for missing in required:
        with pytest.raises(ValidationError):
            avatar_type(**{key: value for key, value in required.items() if key != missing})
    with pytest.raises(ValidationError):
        avatar_type(**required, unsupported=True)
