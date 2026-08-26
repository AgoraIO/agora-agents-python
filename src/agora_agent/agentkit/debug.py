"""Redaction for ``debug=True`` session logging.

The debug dump is routinely pasted into issues and chat threads, so it must
never carry a usable credential. Header redaction already exists in
``pool_client``; nothing redacted the request *body*, which is where vendor API
keys and RTC tokens live.
"""

from __future__ import annotations

import typing
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

#: Marker substituted for a redacted value.
REDACTED = "[REDACTED]"

#: Body fields whose values are credentials or account identifiers.
#:
#: Compared case-insensitively, and matched on both snake_case and camelCase
#: spellings so this keeps working if a caller hand-builds a config.
_SENSITIVE_BODY_KEYS = frozenset(
    {
        # Vendor credentials
        "api_key",
        "apikey",
        "key",
        "secret",
        "api_secret",
        "apisecret",
        "password",
        "access_key_id",
        "accesskeyid",
        "secret_access_key",
        "secretaccesskey",
        "adc_credentials_string",
        "adccredentialsstring",
        "credentials",
        "subscription_key",
        "subscriptionkey",
        # Agora credentials and account identifiers
        "token",
        "agora_token",
        "agoratoken",
        "authorization",
        "appid",
        "app_id",
        "agora_appid",
        "agoraappid",
        "app_certificate",
        "appcertificate",
        "customer_secret",
        "customersecret",
    }
)


def _is_sensitive_key(key: str) -> bool:
    return key.lower() in _SENSITIVE_BODY_KEYS


def _redact_query_keys(value: str) -> str:
    """Strip Gemini-style ``key=`` query values from URL strings."""
    parts = urlsplit(value)
    if not parts.scheme or not parts.query:
        return value
    pairs = []
    changed = False
    for key, item in parse_qsl(parts.query, keep_blank_values=True):
        if key.lower() == "key" and item:
            pairs.append((key, REDACTED))
            changed = True
        else:
            pairs.append((key, item))
    if not changed:
        return value
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(pairs), parts.fragment))


def redact_secrets(value: typing.Any) -> typing.Any:
    """Deep-copy ``value``, replacing credential fields with :data:`REDACTED`.

    Empty strings are left visible on purpose: ``""`` is the signature of an
    unset environment variable, and hiding it behind ``[REDACTED]`` would
    disguise the exact misconfiguration the debug output exists to surface.

    Never mutates the input — the request that goes on the wire is untouched.
    """
    if isinstance(value, dict):
        result: typing.Dict[typing.Any, typing.Any] = {}
        for key, item in value.items():
            if isinstance(key, str) and _is_sensitive_key(key) and isinstance(item, str) and item:
                result[key] = REDACTED
            elif isinstance(item, str):
                result[key] = _redact_query_keys(item)
            else:
                result[key] = redact_secrets(item)
        return result
    if isinstance(value, (list, tuple)):
        redacted = [redact_secrets(item) for item in value]
        return type(value)(redacted) if isinstance(value, tuple) else redacted
    return value


__all__ = ["REDACTED", "redact_secrets"]
