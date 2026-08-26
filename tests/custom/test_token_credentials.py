"""Credential validation in the token builders.

Agora requires the App ID and App Certificate to be exactly 32 characters. The
Python signing path HMACs whatever it is given, so without a check a truncated
or whitespace-padded value produces a well-formed token that the gateway
rejects with an auth error naming neither field.
"""

import pytest

from agora_agent.agentkit.token import generate_convo_ai_token, generate_rtc_token

VALID_APP_ID = "0123456789abcdef0123456789abcdef"
VALID_CERTIFICATE = "fedcba9876543210fedcba9876543210"


def test_builds_a_token_when_both_credentials_are_the_right_length():
    token = generate_convo_ai_token(
        app_id=VALID_APP_ID,
        app_certificate=VALID_CERTIFICATE,
        channel_name="demo",
        uid=333,
    )

    assert token.startswith("007")


@pytest.mark.parametrize(
    "app_id,app_certificate,expected",
    [
        (VALID_APP_ID, VALID_CERTIFICATE[:31], "app_certificate is 31 characters"),
        (VALID_APP_ID, VALID_CERTIFICATE + "\n", "app_certificate is 33 characters"),
        ("short-app-id", VALID_CERTIFICATE, "app_id is 12 characters"),
    ],
)
def test_rejects_malformed_credentials(app_id, app_certificate, expected):
    with pytest.raises(ValueError, match=expected):
        generate_convo_ai_token(
            app_id=app_id, app_certificate=app_certificate, channel_name="demo", uid=333
        )


def test_names_both_fields_when_both_are_wrong():
    with pytest.raises(ValueError, match="app_id is 5 characters and app_certificate is 10 characters"):
        generate_convo_ai_token(
            app_id="short", app_certificate="also-short", channel_name="demo", uid=333
        )


def test_never_puts_the_credential_values_in_the_message():
    secret = "super-secret-but-wrong-length"
    with pytest.raises(ValueError) as excinfo:
        generate_convo_ai_token(
            app_id=VALID_APP_ID, app_certificate=secret, channel_name="demo", uid=333
        )

    assert secret not in str(excinfo.value)


def test_guards_the_rtc_builder_too():
    with pytest.raises(ValueError, match="app_certificate is 9 characters"):
        generate_rtc_token(
            app_id=VALID_APP_ID, app_certificate="too-short", channel="demo", uid=333
        )
