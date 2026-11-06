"""generate_client_token: RTC + RTM only, with no ConvoAI service."""
import base64
import hashlib
import hmac
import io
import struct
import zlib

import pytest

from agora_agent import generate_client_token as root_generate_client_token
from agora_agent.agentkit.token import generate_client_token


def decode_token(token):
    assert token.startswith("007")
    raw = zlib.decompress(base64.b64decode(token[3:]))
    stream = io.BytesIO(raw)

    def integer(fmt):
        return struct.unpack(fmt, stream.read(struct.calcsize(fmt)))[0]

    def string():
        return stream.read(integer("<H"))

    signature = string()
    signed = raw[stream.tell():]
    app_id = string().decode()
    issue, expiry, salt = (integer("<I") for _ in range(3))
    key = hmac.new(struct.pack("<I", issue), b"b" * 32, hashlib.sha256).digest()
    key = hmac.new(struct.pack("<I", salt), key, hashlib.sha256).digest()
    assert hmac.compare_digest(signature, hmac.new(key, signed, hashlib.sha256).digest())
    services = {}
    for _ in range(integer("<H")):
        service = integer("<H")
        privileges = {}
        for _ in range(integer("<H")):
            privilege = integer("<H")
            privileges[privilege] = integer("<I")
        payload = []
        for _ in range({1: 2, 2: 1, 9: 0}[service]):
            payload.append(string().decode())
        assert service not in services
        services[service] = (privileges, payload)
    assert not stream.read()
    return app_id, expiry, services



@pytest.mark.parametrize("uid,account,privilege_ttl", [(42, "42", 0), ("user-a", "user-a", 120)])
def test_client_token_grants_rtc_and_rtm_without_convo_ai(uid, account, privilege_ttl):
    token = generate_client_token("a" * 32, "b" * 32, "room", uid, 600, privilege_ttl)
    app_id, expiry, services = decode_token(token)
    assert app_id == "a" * 32 and expiry == 600
    assert services == {
        1: ({key: privilege_ttl or 600 for key in (1, 2, 3, 4)}, ["room", account]),
        2: ({1: 600}, [account]),
    }


@pytest.mark.parametrize("uid", [0, "0", "", "000"])
def test_client_token_rejects_uid_that_cannot_be_rtm_user_id(uid):
    with pytest.raises(ValueError, match="nonzero and nonempty"):
        generate_client_token("a" * 32, "b" * 32, "room", uid)


def test_client_token_names_malformed_credential():
    with pytest.raises(ValueError, match="app_id is 33 characters"):
        generate_client_token("a" * 33, "b" * 32, "room", 1)


def test_client_token_is_exported_from_the_package_root():
    assert root_generate_client_token is generate_client_token
