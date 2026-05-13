from agora_agent.agentkit.presets import resolve_session_presets


def test_minimax_preset_strips_group_id_and_url_when_no_key() -> None:
    """When no key is provided, preset is inferred and credential fields are stripped."""
    properties = {
        "tts": {
            "vendor": "minimax",
            "params": {
                "group_id": "my-group",
                "model": "speech-2.6-turbo",
                "url": "wss://api-uw.minimax.io/ws/v1/t2a_v2",
                "voice_setting": {"voice_id": "English_captivating_female1"},
            },
        }
    }
    preset, resolved = resolve_session_presets(None, properties)
    assert preset == "minimax_speech_2_6_turbo"
    params = resolved["tts"]["params"]
    assert "group_id" not in params
    assert "url" not in params
    assert "model" not in params
    assert params["voice_setting"]["voice_id"] == "English_captivating_female1"


def test_minimax_preset_strips_group_id_and_url_for_28_turbo() -> None:
    properties = {
        "tts": {
            "vendor": "minimax",
            "params": {
                "group_id": "org-123",
                "model": "speech-2.8-turbo",
                "url": "wss://api.minimax.io/ws/v1/t2a_v2",
                "voice_setting": {"voice_id": "some-voice"},
            },
        }
    }
    preset, resolved = resolve_session_presets(None, properties)
    assert preset == "minimax_speech_2_8_turbo"
    params = resolved["tts"]["params"]
    assert "group_id" not in params
    assert "url" not in params
    assert "model" not in params


def test_minimax_preset_strips_group_id_and_url_with_underscore_model_name() -> None:
    properties = {
        "tts": {
            "vendor": "minimax",
            "params": {
                "group_id": "my-group",
                "model": "speech_2_6_turbo",
                "url": "wss://api-uw.minimax.io/ws/v1/t2a_v2",
            },
        }
    }
    preset, resolved = resolve_session_presets(None, properties)
    assert preset == "minimax_speech_2_6_turbo"
    params = resolved["tts"].get("params") or {}
    assert "group_id" not in params
    assert "url" not in params
    assert "model" not in params


def test_minimax_preset_not_inferred_when_key_present() -> None:
    """When user provides their own key, preset is NOT inferred and nothing is stripped."""
    properties = {
        "tts": {
            "vendor": "minimax",
            "params": {
                "key": "user-secret",
                "group_id": "my-group",
                "model": "speech-2.6-turbo",
            },
        }
    }
    preset, resolved = resolve_session_presets(None, properties)
    assert preset is None
    params = resolved["tts"]["params"]
    assert params.get("key") == "user-secret"
    assert params.get("group_id") == "my-group"


def test_minimax_preset_not_inferred_when_explicit_preset_given() -> None:
    """When an explicit tts preset is provided, tts inference is skipped."""
    properties = {
        "tts": {
            "vendor": "minimax",
            "params": {
                "group_id": "my-group",
                "model": "speech-2.6-turbo",
            },
        }
    }
    preset, resolved = resolve_session_presets("minimax_speech_2_6_turbo", properties)
    assert preset == "minimax_speech_2_6_turbo"
    # Explicit preset: tts inference is skipped, params are NOT stripped
    params = resolved["tts"]["params"]
    assert params.get("group_id") == "my-group"


def test_deepgram_preset_strips_model_and_api_key() -> None:
    properties = {
        "asr": {
            "vendor": "deepgram",
            "params": {
                "model": "nova-3",
                "language": "en-US",
            },
        }
    }
    preset, resolved = resolve_session_presets(None, properties)
    assert preset == "deepgram_nova_3"
    params = resolved["asr"]["params"]
    assert "model" not in params
    assert "api_key" not in params
    assert params.get("language") == "en-US"


def test_openai_llm_preset_strips_model_api_key_and_default_url() -> None:
    properties = {
        "llm": {
            "vendor": "openai",
            "url": "https://api.openai.com/v1/chat/completions",
            "params": {
                "model": "gpt-4o-mini",
            },
        }
    }
    preset, resolved = resolve_session_presets(None, properties)
    assert preset == "openai_gpt_4o_mini"
    llm = resolved["llm"]
    assert "api_key" not in llm
    assert "url" not in llm
    assert "model" not in (llm.get("params") or {})
