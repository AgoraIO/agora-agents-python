"""Basic REST auth stays separate from RTC transport token provisioning."""

import base64
import json

import httpx
import pytest
from test_convoai_token_services import decode_token

from agora_agent import Agent, Agora, Area, AsyncAgora, AsyncSavedAgent, OpenAI, OpenAITTS, SavedAgent
from agora_agent.core.public_auth import validate_public_headers
from agora_agent.v3 import V3Options

BASIC = "Basic " + base64.b64encode(b"customer:secret:with-colon").decode()


@pytest.mark.parametrize("cls", [Agora, AsyncAgora])
@pytest.mark.parametrize("credentials", [
    {"customer_id": "id"}, {"customer_secret": "secret"},
    {"customer_id": "", "customer_secret": "secret"},
    {"customer_id": "id", "customer_secret": " "},
    {"customer_id": "bad:id", "customer_secret": "secret"},
    {"customer_id": "id", "customer_secret": "secret", "auth_token": "token"},
])
def test_basic_credentials_are_complete_and_unambiguous(cls, credentials):
    with pytest.raises(ValueError) as error:
        cls(area=Area.US, app_id="a" * 32, **credentials)
    assert "secret" not in str(error.value).replace("customer_secret", "")


@pytest.mark.asyncio
@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.parametrize("with_certificate", [False, True])
async def test_basic_auth_on_low_level_and_agentkit_sessions(async_, with_certificate):
    requests = []

    def handler(request):
        requests.append(request)
        assert request.headers["Authorization"] == BASIC
        if request.url.path.endswith("/agents/saved"):
            return httpx.Response(200, json={"agent_id": "saved", "agent_name": "Support"}, headers={"ETag": '"1"'})
        return httpx.Response(200, json={"agent_id": "legacy", "agent_session_id": "session", "status": "RUNNING", "create_ts": 1})

    http = (httpx.AsyncClient if async_ else httpx.Client)(transport=httpx.MockTransport(handler))
    client = (AsyncAgora if async_ else Agora)(
        area=Area.US, app_id="a" * 32, app_certificate="b" * 32 if with_certificate else None,
        customer_id="customer", customer_secret="secret:with-colon", httpx_client=http,
    )
    assert client.auth_mode == "basic"
    for result in (client.agents.get("a" * 32, "legacy"), client.v3.sessions.list()):
        if async_:
            await result
    saved = await AsyncSavedAgent.get(client, "saved") if async_ else SavedAgent.get(client, "saved")
    agent = Agent(client).with_llm(OpenAI(model="gpt-5-mini")).with_tts(OpenAITTS(model="tts-1", voice="alloy"))
    ephemeral = agent.create_async_ephemeral_session if async_ else agent.create_ephemeral_session
    legacy = agent.create_async_session if async_ else agent.create_session
    for create in (saved.create_session, ephemeral, legacy):
        # Legacy RTC needs a supplied token without a certificate; Platform RTC
        # can leave provisioning to the server. REST auth remains Basic either way.
        options = {"token": "provided-rtc"} if create == legacy and not with_certificate else {}
        session = create(channel="room", agent_uid="123", remote_uids=["2"], **options)
        result = session.start()
        if async_:
            await result
        body = json.loads(requests[-1].content)
        rtc = body.get("transport", body.get("properties", {})).get("token")
        if with_certificate:
            assert decode_token(rtc)[2][9] == ({}, [])
        elif create != legacy:
            assert rtc is None
        else:
            assert rtc == "provided-rtc"
        for action in (session.get_info, session.stop):
            result = action()
            if async_:
                await result
    if async_:
        await http.aclose()
    else:
        http.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("async_", [False, True])
async def test_explicit_basic_header_override_reaches_both_resource_families(async_):
    requests = []
    http = (httpx.AsyncClient if async_ else httpx.Client)(transport=httpx.MockTransport(
        lambda request: requests.append(request) or httpx.Response(200, json={"agent_id": "legacy", "status": "RUNNING"})
    ))
    client = (AsyncAgora if async_ else Agora)(area=Area.US, app_id="project", auth_token="provided-token", httpx_client=http)
    options = {"additional_headers": {"authorization": BASIC}}
    for result in (client.agents.get("project", "legacy", request_options=options), client.v3.sessions.list(request_options=options)):
        if async_:
            await result
    assert len(requests) == 2 and all(request.headers["Authorization"] == BASIC for request in requests)
    if async_:
        await http.aclose()
    else:
        http.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.parametrize("name", ["Authorization", "authorization", "AUTHORIZATION"])
async def test_v3_basic_override_is_case_insensitive_with_app_credentials(async_, name):
    requests = []
    http = (httpx.AsyncClient if async_ else httpx.Client)(transport=httpx.MockTransport(
        lambda request: requests.append(request) or httpx.Response(200, json={"items": []})
    ))
    client = (AsyncAgora if async_ else Agora)(
        area=Area.US, app_id="a" * 32, app_certificate="b" * 32,
        v3=V3Options(headers={name: BASIC}), httpx_client=http,
    )
    result = client.v3.sessions.list()
    if async_:
        await result
    assert len(requests) == 1
    assert requests[0].headers.get_list("Authorization") == [BASIC]
    if async_:
        await http.aclose()
    else:
        http.close()


@pytest.mark.parametrize("value", ["Basic stale", "Basic Og==", "Basic aWQ6", "Basic OnNlY3JldA==", "Basic bm9jb2xvbg=="])
def test_invalid_basic_headers_are_rejected(value):
    with pytest.raises(ValueError):
        validate_public_headers({"Authorization": value})
