import json
from typing import Any, Tuple

import pytest
from pydantic import ValidationError

import agora_agent
import agora_agent.agentkit as agentkit
from agora_agent.agentkit import vendors
from agora_agent.agentkit.avatar_types import is_avatar_token_managed, validate_avatar_config
from agora_agent.agentkit.vendors.avatar import GenericAvatar, LemonSlice, Protoface, Tavus

INVALID_SELECTOR_VALUES: Tuple[Any, ...] = ("", "  ", None, 3, False, [], {})


@pytest.mark.parametrize("name", ["Tavus", "Protoface", "LemonSlice"])
def test_branded_avatar_exports_are_provider_wrappers(name: str) -> None:
    for module in (agora_agent, agentkit, vendors):
        assert getattr(module, name) is getattr(vendors, name)
        assert issubclass(getattr(module, name), GenericAvatar)
        assert name in module.__all__
        assert name in dir(module)


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
        additional_params={"custom": {"value": 1}, "api_key": "ignored", **({"agent_id": "agent"} if avatar_type is LemonSlice else {})},
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
            **({"agent_id": "agent"} if avatar_type is LemonSlice else {}),
        },
    }
    assert avatar.required_sample_rate == 0
    assert is_avatar_token_managed(config)
    validate_avatar_config(config, require_session_fields=True)


@pytest.mark.parametrize("avatar_type,url", [
    (Tavus, "https://tavusapi.com/v2/conversations/agora"),
    (Protoface, "https://api.protoface.com/v1/agora"),
    (LemonSlice, "https://lemonslice.com/api/liveai/agora"),
])
def test_defaults_required_fields_and_generic_requirement(avatar_type, url):
    options = dict(api_key="key", agora_uid="2")
    if avatar_type is LemonSlice:
        options["agent_id"] = "agent"
    else:
        options["avatar_id"] = "avatar"
    avatar = avatar_type(**options)
    assert avatar.to_config()["params"]["api_base_url"] == url
    if avatar_type is LemonSlice:
        assert avatar.avatar_id == "lemonslice"
    for key in ("api_key", "agora_uid") + (() if avatar_type is LemonSlice else ("avatar_id",)):
        with pytest.raises(ValidationError):
            avatar_type(**{k: v for k, v in options.items() if k != key})
    with pytest.raises(ValidationError):
        avatar_type(**options, unsupported=True)
    with pytest.raises(ValidationError):
        GenericAvatar(api_key="key", agora_uid="2", avatar_id="avatar")


@pytest.mark.parametrize("selector", ["agent_id", "agent_image_url", "agent_image_base64"])
@pytest.mark.parametrize("ratio", [None, "2x3", "9x16", "1x1"])
def test_lemonslice_selectors_ratios_and_nonmutation(selector, ratio):
    additional = {selector: "old", "custom": {"value": 1}}
    options = dict(api_key="key", agora_uid="2", additional_params=additional, **{selector: "new"})
    if ratio is not None:
        options["aspect_ratio"] = ratio
    avatar = LemonSlice(**options)
    params = avatar.to_config()["params"]
    assert params[selector] == "new"
    assert additional == {selector: "old", "custom": {"value": 1}}
    assert avatar.additional_params == additional
    assert params.get("aspect_ratio") == ratio
    assert ("aspect_ratio" in params) == (ratio is not None)
    assert LemonSlice(api_key="key", agora_uid="2", additional_params=additional).to_config()["params"][selector] == "old"


@pytest.mark.parametrize("additional", [
    {}, {"agent_id": "a", "agent_image_url": "url"},
    *[{key: value} for key in ("agent_id", "agent_image_url", "agent_image_base64")
      for value in INVALID_SELECTOR_VALUES],
    {"agent_id": "a", "agent_image_url": " "},
    {"agent_id": "a", "aspect_ratio": "16x9"},
    {"agent_id": "a", "aspect_ratio": None},
])
def test_lemonslice_rejects_invalid_effective_params(additional):
    with pytest.raises(ValidationError):
        LemonSlice(api_key="key", agora_uid="2", additional_params=additional)


def test_typed_overrides_validate_effective_values():
    avatar = LemonSlice(api_key="key", agora_uid="2", agent_id="valid", aspect_ratio="1x1",
                       additional_params={"agent_id": 3, "aspect_ratio": "invalid"})
    assert avatar.to_config()["params"]["aspect_ratio"] == "1x1"
    with pytest.raises(ValidationError):
        LemonSlice(api_key="key", agora_uid="2", agent_id="valid", additional_params={"agent_image_url": "other"})
    with pytest.raises(ValidationError):
        LemonSlice(api_key="key", agora_uid="2", agent_id="valid", aspect_ratio="invalid")
