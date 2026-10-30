"""Verify signed service grants, not just the Token007 prefix."""

import base64
import hashlib
import hmac
import io
import json
import struct
import sys
import types
import zlib

import httpx
import pytest

from agora_agent import Agent, Agora, Area, AsyncAgora, AsyncSavedAgent, OpenAI, SavedAgent
from agora_agent.agentkit.token import generate_convo_ai_token


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


# Generated independently with AgoraIO/Tools Python AccessToken/ServiceConvoAI
# at b75635c32d30cedd25fd1199926fd55219533688, issue_ts=1700000000,
# salt=12345, app_id="a"*32, certificate="b"*32, channel="test-channel".
# RTC privilege TTL and RTM token TTL are set independently, preserving our API.
@pytest.mark.parametrize("uid,ttl,privilege_ttl,reference", [
    (0, 86400, 0, "007eJxTYFCdnfjV67P/1LMzPn285TnF14dxMvs/AfPe6iev2ic49D1TYEgkABg+Bqc2BDIyWBowMDAzMDKwADGIzwQmmcEkC5jkYShJLS7RTc5IzMtLzWFkMGACKoUoBnI4GRgYAA2GKgI="),
    (123, 3600, 600, "007eJxTYNh04Jz1NrvO8pwz+r/uFBls3vqg/+4akbWpZVqKXFsf/xNRYEgkABg+BqcK8DEwWBowMDAzMDKwAHEEEwMDE5hkBpMsYJKHoSS1uEQ3OSMxLy81h5nB0MiYCaiYkQGkHczlZGBgAAAqayeD"),
])
def test_matches_official_signed_fixture_even_with_legacy_builder_installed(monkeypatch, uid, ttl, privilege_ttl, reference):
    monkeypatch.setattr("agora_agent.agentkit.token.time.time", lambda: 1700000000)
    monkeypatch.setattr("agora_agent.agentkit.token.secrets.SystemRandom", lambda: types.SimpleNamespace(randint=lambda *_: 12345))
    legacy = types.SimpleNamespace(buildTokenWithRtm=lambda *_: pytest.fail("legacy RTC+RTM builder used"))
    monkeypatch.setitem(sys.modules, "agora_token_builder", types.SimpleNamespace(RtcTokenBuilder=legacy))
    token = generate_convo_ai_token("a" * 32, "b" * 32, "test-channel", uid, ttl, privilege_ttl)
    assert zlib.decompress(base64.b64decode(token[3:])) == zlib.decompress(base64.b64decode(reference[3:]))
    app_id, expiry, services = decode_token(token)
    assert app_id == "a" * 32 and expiry == ttl
    assert services == {
        1: ({key: privilege_ttl or ttl for key in (1, 2, 3, 4)}, ["test-channel", str(uid)]),
        2: ({1: ttl}, [str(uid)]),
        9: ({}, []),
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.parametrize("saved", [False, True])
async def test_platform_session_routes_receive_convoai_authorization(async_, saved):
    requests = []

    def handler(request):
        requests.append(request)
        token = request.headers["Authorization"][len("agora token="):]
        assert decode_token(token)[2][9] == ({}, [])
        if request.url.path.endswith("/agents/saved"):
            return httpx.Response(200, json={"agent_id": "saved", "agent_name": "support"}, headers={"ETag": '"1"'})
        return httpx.Response(200, json={"agent_session_id": "s", "status": "RUNNING", "create_ts": 1})

    transport = httpx.MockTransport(handler)
    http = httpx.AsyncClient(transport=transport) if async_ else httpx.Client(transport=transport)
    client = (AsyncAgora if async_ else Agora)(area=Area.US, app_id="a" * 32, app_certificate="b" * 32, httpx_client=http)
    owner = Agent(client).with_llm(OpenAI(model="gpt-5-mini"))
    if saved:
        owner = await AsyncSavedAgent.get(client, "saved") if async_ else SavedAgent.get(client, "saved")
        create = owner.create_session
    else:
        create = owner.create_async_ephemeral_session if async_ else owner.create_ephemeral_session
    session = create(channel="room", agent_uid="123", remote_uids=["2"])
    result = session.start()
    if async_:
        await result
    start = requests[-1]
    rtc_token = json.loads(start.content)["transport"]["token"]
    assert decode_token(rtc_token)[2][1][1] == ["room", "123"]
    for action in (session.get_info, session.stop, client.v3.sessions.list):
        result = action()
        if async_:
            await result
    assert len(requests) == (5 if saved else 4)
    if async_:
        await http.aclose()
    else:
        http.close()
