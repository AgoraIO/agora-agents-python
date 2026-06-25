import warnings
import typing


def is_heygen_avatar(config: typing.Dict[str, typing.Any]) -> bool:
    return config.get("vendor") == "heygen"


def is_live_avatar_avatar(config: typing.Dict[str, typing.Any]) -> bool:
    return config.get("vendor") == "liveavatar"


def is_akool_avatar(config: typing.Dict[str, typing.Any]) -> bool:
    return config.get("vendor") == "akool"


def is_anam_avatar(config: typing.Dict[str, typing.Any]) -> bool:
    return config.get("vendor") == "anam"


def is_generic_avatar(config: typing.Dict[str, typing.Any]) -> bool:
    return config.get("vendor") == "generic"


def is_sensetime_avatar(config: typing.Dict[str, typing.Any]) -> bool:
    return config.get("vendor") == "sensetime"


def is_spatius_avatar(config: typing.Dict[str, typing.Any]) -> bool:
    return config.get("vendor") == "spatius"


def is_avatar_token_managed(config: typing.Dict[str, typing.Any]) -> bool:
    """Return True when AgentKit manages the avatar RTC publisher identity."""
    return (
        is_heygen_avatar(config)
        or is_live_avatar_avatar(config)
        or is_generic_avatar(config)
        or is_sensetime_avatar(config)
        or is_spatius_avatar(config)
    )


def is_rtc_avatar(config: typing.Dict[str, typing.Any]) -> bool:
    """Deprecated: use :func:`is_avatar_token_managed` for vendor gating."""
    warnings.warn(
        "is_rtc_avatar is deprecated; use is_avatar_token_managed for vendor gating "
        "and keep agora_uid checks in session enrichment.",
        DeprecationWarning,
        stacklevel=2,
    )
    params = config.get("params", {})
    return (
        isinstance(params, dict)
        and bool(params.get("agora_uid"))
        and is_avatar_token_managed(config)
    )


def validate_avatar_config(
    config: typing.Dict[str, typing.Any],
    require_session_fields: bool = False,
) -> None:
    """Validates avatar configuration at runtime.

    Parameters
    ----------
    config : dict
        The avatar configuration dictionary.

    Raises
    ------
    ValueError
        If the configuration is invalid.
    """
    if is_heygen_avatar(config) or is_live_avatar_avatar(config):
        label = "HeyGen" if is_heygen_avatar(config) else "LiveAvatar"
        params = config.get("params", {})
        if not params.get("api_key"):
            raise ValueError(f"{label} avatar requires api_key")
        if not params.get("quality"):
            raise ValueError(f"{label} avatar requires quality (low, medium, or high)")
        if not params.get("agora_uid"):
            raise ValueError(f"{label} avatar requires agora_uid")
        valid_qualities = ("low", "medium", "high")
        if params.get("quality") not in valid_qualities:
            raise ValueError(
                f"Invalid quality for {label}: {params.get('quality')}. "
                f"Must be one of: {', '.join(valid_qualities)}"
            )
        if require_session_fields and not params.get("agora_token"):
            raise ValueError(
                f"{label} avatar requires agora_token after session enrichment"
            )
    elif is_akool_avatar(config):
        params = config.get("params", {})
        if not params.get("api_key"):
            raise ValueError("Akool avatar requires api_key")
    elif is_anam_avatar(config):
        params = config.get("params", {})
        if not params.get("api_key"):
            raise ValueError("Anam avatar requires api_key")
    elif is_generic_avatar(config):
        params = config.get("params", {})
        if not params.get("api_key"):
            raise ValueError("Generic avatar requires api_key")
        if not params.get("api_base_url"):
            raise ValueError("Generic avatar requires api_base_url")
        if not params.get("avatar_id"):
            raise ValueError("Generic avatar requires avatar_id")
        if not params.get("agora_uid"):
            raise ValueError("Generic avatar requires agora_uid")
        if require_session_fields:
            if not params.get("agora_token"):
                raise ValueError(
                    "Generic avatar requires agora_token after session enrichment"
                )
            if not params.get("agora_appid"):
                raise ValueError(
                    "Generic avatar requires agora_appid after session enrichment"
                )
            if not params.get("agora_channel"):
                raise ValueError(
                    "Generic avatar requires agora_channel after session enrichment"
                )
    elif is_sensetime_avatar(config):
        params = config.get("params", {})
        if not params.get("app_key"):
            raise ValueError("SenseTime avatar requires app_key")
        scene_list = params.get("sceneList")
        if not scene_list:
            raise ValueError("SenseTime avatar requires sceneList")
        if not params.get("agora_uid"):
            raise ValueError("SenseTime avatar requires agora_uid")
        if require_session_fields and not params.get("agora_token"):
            raise ValueError("SenseTime avatar requires agora_token")
    elif is_spatius_avatar(config):
        params = config.get("params", {})
        if not params.get("spatius_api_key"):
            raise ValueError("Spatius avatar requires spatius_api_key")
        if not params.get("spatius_app_id"):
            raise ValueError("Spatius avatar requires spatius_app_id")
        if not params.get("spatius_avatar_id"):
            raise ValueError("Spatius avatar requires spatius_avatar_id")
        if not params.get("agora_uid"):
            raise ValueError("Spatius avatar requires agora_uid")
        if require_session_fields and not params.get("agora_token"):
            raise ValueError("Spatius avatar requires agora_token")


def validate_tts_sample_rate(
    avatar_config: typing.Dict[str, typing.Any],
    tts_sample_rate: int,
) -> None:
    """Validates that TTS sample rate is compatible with the avatar vendor.

    Different avatar vendors have specific sample rate requirements:
    - HeyGen/LiveAvatar: ONLY supports 24,000 Hz
    - Akool: ONLY supports 16,000 Hz

    Parameters
    ----------
    avatar_config : dict
        The avatar configuration dictionary.
    tts_sample_rate : int
        The sample rate from your TTS configuration (in Hz).

    Raises
    ------
    ValueError
        If TTS sample rate is incompatible with the avatar vendor.
    """
    if is_heygen_avatar(avatar_config) or is_live_avatar_avatar(avatar_config):
        if tts_sample_rate != 24000:
            label = "HeyGen" if is_heygen_avatar(avatar_config) else "LiveAvatar"
            raise ValueError(
                f"{label} avatars ONLY support 24,000 Hz sample rate. "
                f"Your TTS is configured with {tts_sample_rate} Hz. "
                f"Please update your TTS configuration to use 24kHz sample rate. "
                f"See: https://docs.agora.io/en/conversational-ai/models/avatar/overview"
            )
    elif is_akool_avatar(avatar_config):
        if tts_sample_rate != 16000:
            raise ValueError(
                f"Akool avatars ONLY support 16,000 Hz sample rate. "
                f"Your TTS is configured with {tts_sample_rate} Hz. "
                f"Please update your TTS configuration to use 16kHz sample rate. "
                f"See: https://docs.agora.io/en/conversational-ai/models/avatar/akool"
            )
    elif is_spatius_avatar(avatar_config):
        expected_sample_rate = avatar_config.get("params", {}).get("sample_rate")
        if isinstance(expected_sample_rate, int) and tts_sample_rate != expected_sample_rate:
            raise ValueError(
                f"Spatius avatar is configured with sample_rate {expected_sample_rate} Hz, "
                f"but TTS is configured with {tts_sample_rate} Hz. "
                f"Please align the TTS sample_rate with the avatar sample_rate."
            )
