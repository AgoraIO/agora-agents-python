import base64
import hashlib
import hmac
import random
import struct
import time
import typing
import zlib

DEFAULT_EXPIRY_SECONDS = 86400
MAX_EXPIRY_SECONDS = 86400

ROLE_PUBLISHER = 1
ROLE_SUBSCRIBER = 2


def _validate_expires_in(seconds: float) -> int:
    """Validate an ``expires_in`` value in seconds.

    - Raises :class:`ValueError` if ``seconds <= 0``.
    - Warns and caps at :data:`MAX_EXPIRY_SECONDS` if ``seconds > MAX_EXPIRY_SECONDS``.
    """
    import warnings

    if seconds <= 0:
        raise ValueError("expires_in must be between 1 and 86400 seconds (24h)")
    if seconds > MAX_EXPIRY_SECONDS:
        warnings.warn("agora-agent-sdk: expires_in capped at 24h (Agora max)", stacklevel=3)
        return MAX_EXPIRY_SECONDS
    return int(seconds)


def expires_in_hours(hours: float) -> int:
    """Convert hours to seconds for use as ``expires_in``.

    Parameters
    ----------
    hours : float
        Number of hours. Must be > 0 and result must not exceed 24 hours (86400 s).

    Returns
    -------
    int
        Equivalent seconds, capped at :data:`MAX_EXPIRY_SECONDS`.

    Raises
    ------
    ValueError
        If ``hours <= 0``.
    """
    return _validate_expires_in(hours * 3600)


def expires_in_minutes(minutes: float) -> int:
    """Convert minutes to seconds for use as ``expires_in``.

    Parameters
    ----------
    minutes : float
        Number of minutes. Must be > 0 and result must not exceed 24 hours (86400 s).

    Returns
    -------
    int
        Equivalent seconds, capped at :data:`MAX_EXPIRY_SECONDS`.

    Raises
    ------
    ValueError
        If ``minutes <= 0``.
    """
    return _validate_expires_in(minutes * 60)


class GenerateTokenOptions(typing.TypedDict, total=False):
    app_id: str
    app_certificate: str
    channel: str
    uid: int
    role: int
    expiry_seconds: int


class GenerateConvoAITokenOptions(typing.TypedDict, total=False):
    app_id: str
    app_certificate: str
    channel_name: str
    uid: int
    token_expire: int
    privilege_expire: int


# ---------------------------------------------------------------------------
# AccessToken2 implementation (mirrors Agora's official python3 source)
# https://github.com/AgoraIO/Tools/tree/master/DynamicKey/AgoraDynamicKey/python3
# ---------------------------------------------------------------------------

def _pack_uint16(v: int) -> bytes:
    return struct.pack("<H", v)


def _pack_uint32(v: int) -> bytes:
    return struct.pack("<I", v)


def _pack_string(s: bytes) -> bytes:
    return _pack_uint16(len(s)) + s


def _pack_map_uint32(m: typing.Dict[int, int]) -> bytes:
    result = _pack_uint16(len(m))
    for k in sorted(m.keys()):
        result += _pack_uint16(k) + _pack_uint32(m[k])
    return result


def _build_access_token2(
    app_id: str,
    app_certificate: str,
    expire: int,
    services: typing.List[typing.Tuple[int, bytes]],
) -> str:
    """Build an AccessToken2 string with the given services.

    Parameters
    ----------
    app_id : str
        Agora App ID (32-char hex string).
    app_certificate : str
        Agora App Certificate (32-char hex string).
    expire : int
        Seconds from now until the token expires.
    services : list of (service_type, packed_service_bytes)
        Pre-packed service payloads.

    Returns
    -------
    str
        The AccessToken2 string prefixed with "007".
    """
    issue_ts = int(time.time())
    salt = random.randint(1, 99999999)

    app_id_bytes = app_id.encode("utf-8")
    app_cert_bytes = app_certificate.encode("utf-8")

    # signing key = HMAC(HMAC(app_cert, issue_ts_packed), salt_packed)
    signing = hmac.new(_pack_uint32(issue_ts), app_cert_bytes, hashlib.sha256).digest()
    signing = hmac.new(_pack_uint32(salt), signing, hashlib.sha256).digest()

    signing_info = (
        _pack_string(app_id_bytes)
        + _pack_uint32(issue_ts)
        + _pack_uint32(expire)
        + _pack_uint32(salt)
        + _pack_uint16(len(services))
    )
    for _, svc_bytes in services:
        signing_info += svc_bytes

    signature = hmac.new(signing, signing_info, hashlib.sha256).digest()
    compressed = zlib.compress(_pack_string(signature) + signing_info)
    return "007" + base64.b64encode(compressed).decode("utf-8")


def _pack_service_rtc(channel_name: str, account: str, privileges: typing.Dict[int, int]) -> bytes:
    """Pack an RTC service payload (type=1)."""
    channel_bytes = channel_name.encode("utf-8")
    account_bytes = account.encode("utf-8") if account else b""
    return (
        _pack_uint16(1)  # ServiceRtc.kServiceType
        + _pack_map_uint32(privileges)
        + _pack_string(channel_bytes)
        + _pack_string(account_bytes)
    )


def _pack_service_rtm(user_id: str, privileges: typing.Dict[int, int]) -> bytes:
    """Pack an RTM service payload (type=2)."""
    user_id_bytes = user_id.encode("utf-8")
    return (
        _pack_uint16(2)  # ServiceRtm.kServiceType
        + _pack_map_uint32(privileges)
        + _pack_string(user_id_bytes)
    )


def generate_rtc_token(
    app_id: str,
    app_certificate: str,
    channel: str,
    uid: int,
    role: int = ROLE_PUBLISHER,
    expiry_seconds: int = DEFAULT_EXPIRY_SECONDS,
) -> str:
    """Build a short-lived RTC token (AccessToken2).

    Parameters
    ----------
    app_id : str
        Agora App ID.
    app_certificate : str
        Agora App Certificate.
    channel : str
        Channel name.
    uid : int
        User ID (0 = any UID).
    role : int
        RTC role (ROLE_PUBLISHER or ROLE_SUBSCRIBER).
    expiry_seconds : int
        Token expiry in seconds (default 86400).

    Returns
    -------
    str
        The generated RTC token.
    """
    try:
        from agora_token_builder import RtcTokenBuilder  # type: ignore[import-not-found]

        privilege_expire_ts = int(time.time()) + expiry_seconds
        return RtcTokenBuilder.buildTokenWithUid(
            app_id,
            app_certificate,
            channel,
            uid,
            role,
            privilege_expire_ts,
        )
    except ImportError:
        account = "" if uid == 0 else str(uid)
        privileges: typing.Dict[int, int] = {1: expiry_seconds}  # kPrivilegeJoinChannel
        if role == ROLE_PUBLISHER:
            privileges[2] = expiry_seconds  # kPrivilegePublishAudioStream
            privileges[3] = expiry_seconds  # kPrivilegePublishVideoStream
            privileges[4] = expiry_seconds  # kPrivilegePublishDataStream
        svc = _pack_service_rtc(channel, account, privileges)
        return _build_access_token2(app_id, app_certificate, expiry_seconds, [(1, svc)])


def generate_convo_ai_token(
    app_id: str,
    app_certificate: str,
    channel_name: str,
    uid: int,
    token_expire: int = DEFAULT_EXPIRY_SECONDS,
    privilege_expire: int = 0,
) -> str:
    """Build a combined RTC + RTM token for ConvoAI REST API authentication.

    The resulting token is used as: ``Authorization: agora token=<token>``

    Mirrors ``RtcTokenBuilder.build_token_with_rtm`` from the official Agora
    python3 token builder:
    https://github.com/AgoraIO/Tools/tree/master/DynamicKey/AgoraDynamicKey/python3

    Parameters
    ----------
    app_id : str
        Agora App ID.
    app_certificate : str
        Agora App Certificate.
    channel_name : str
        The channel the agent will join (must match the start request).
    uid : int
        Numeric ConvoAI participant UID. Use the RTC UID for a user, agent, or avatar.
    token_expire : int
        Seconds until the token expires (default 86400).
    privilege_expire : int
        Seconds until privileges expire; 0 means same as token_expire (default 0).

    Returns
    -------
    str
        The AccessToken2 string for use in the Authorization header.
    """
    try:
        from agora_token_builder import RtcTokenBuilder  # type: ignore[import-not-found]

        return RtcTokenBuilder.buildTokenWithRtm(
            app_id,
            app_certificate,
            channel_name,
            _uid_to_account(uid),
            ROLE_PUBLISHER,
            token_expire,
            privilege_expire,
        )
    except (ImportError, AttributeError):
        pass

    priv_expire = privilege_expire if privilege_expire != 0 else token_expire
    account = _uid_to_account(uid)

    rtc_privileges: typing.Dict[int, int] = {
        1: priv_expire,  # kPrivilegeJoinChannel
        2: priv_expire,  # kPrivilegePublishAudioStream
        3: priv_expire,  # kPrivilegePublishVideoStream
        4: priv_expire,  # kPrivilegePublishDataStream
    }
    rtc_svc = _pack_service_rtc(channel_name, account, rtc_privileges)

    rtm_privileges: typing.Dict[int, int] = {
        1: token_expire,  # kPrivilegeLogin
    }
    rtm_svc = _pack_service_rtm(account, rtm_privileges)

    return _build_access_token2(
        app_id,
        app_certificate,
        token_expire,
        [(1, rtc_svc), (2, rtm_svc)],
    )


def _uid_to_account(uid: int) -> str:
    if not isinstance(uid, int) or isinstance(uid, bool):
        raise TypeError("uid must be an int")
    return str(uid)


def _parse_numeric_uid(uid: str, label: str) -> int:
    if not uid.isdigit():
        raise ValueError(f"{label} must be a numeric RTC UID when auto-generating a ConvoAI token")
    return int(uid)
