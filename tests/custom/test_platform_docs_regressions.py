"""Regression cases reported by the Platform docs team."""
import copy
import json
import subprocess
import sys

import httpx
import pytest
from test_v3_preview import make_client

from agora_agent import (
    Agent,
    AmazonBedrock,
    AresSTT,
    AsyncSavedAgent,
    AzureOpenAI,
    DeepgramSTT,
    Gemini,
    OpenAI,
    SavedAgent,
    secret_ref,
)
from agora_agent.agentkit.session_backend import prepare_start_body
from agora_agent.agentkit.v3 import build_body, module
from agora_agent.agentkit.vendors.stt import AssemblyAISTT, SpeechmaticsSTT


def test_managed_openai_and_provider_languages_and_keywords():
    client = make_client(lambda _: pytest.fail("no HTTP"))
    agent = Agent(client).with_llm(OpenAI(model="gpt-5.6-luna")).with_stt(AresSTT(keywords=["Agora"]))
    body = build_body(agent)
    assert body["pipeline"]["llm"]["vendor"] == "openai"
    assert body["pipeline"]["llm"]["credential"] == {"mode": "managed"}
    assert body["pipeline"]["asr"]["params"]["keywords"] == ["Agora"]
    assert body["pipeline"]["asr"]["language"] == "en-US"
    stt = DeepgramSTT(api_key=secret_ref("prod", "key"), model="nova-3", language="fr")
    asr = build_body(agent.with_stt(stt))["pipeline"]["asr"]
    assert asr["language"] == "fr" and "language" not in asr.get("params", {})


@pytest.mark.parametrize("vendor,expected", [
    (AssemblyAISTT(api_key="key", language="en", ws_url="wss://assembly.example"), "wss://assembly.example"),
    (SpeechmaticsSTT(key="key", language="en", uri="wss://speech.example"), "wss://speech.example"),
])
def test_asr_custom_endpoints(vendor, expected):
    errors = []
    result = module(vendor.to_config(), "asr", errors)
    assert not errors
    assert result["url"] == expected
    assert "ws_url" not in result.get("params", {}) and "uri" not in result.get("params", {})


@pytest.mark.parametrize("vendor", [None, "custom"])
@pytest.mark.parametrize("url", [None, "https://gemini.example/custom?alt=sse"])
def test_gemini_credentials_are_not_embedded_in_platform_url(url, vendor):
    key = secret_ref("models", "gemini")
    agent = Agent(make_client(lambda _: pytest.fail("no HTTP"))).with_llm(Gemini(model="gemini-flash", api_key=key, url=url, vendor=vendor))
    before = copy.deepcopy(agent.config)
    llm = build_body(agent)["pipeline"]["llm"]
    assert llm["vendor"] == (vendor or "gemini")
    assert llm["credential"] == {"mode": "byok", "fields": {"api_key": key}}
    assert "key=" not in llm["url"] and "$secrets" not in llm["url"]
    assert before == agent.config


def test_bedrock_api_key_and_azure_resource_name():
    config = AmazonBedrock(api_key=secret_ref("models", "bedrock"), model="model", region="us-east-1")
    llm = module(config.to_config(), "llm", [])
    assert llm["vendor"] == "amazon" and llm["credential"]["fields"] == {"api_key": "$secrets.models.bedrock"}
    with pytest.raises(ValueError):
        AmazonBedrock(api_key="key", access_key="a", secret_key="b", model="model", region="us-east-1")
    azure = AzureOpenAI(api_key="key", resource_name="resource", model="gpt", deployment_name="deploy")
    assert azure.to_config()["url"].startswith("https://resource.openai.azure.com/openai/deployments/deploy/")


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_explicit_ephemeral_and_calls(async_):
    requests = []
    def handler(request):
        requests.append(request)
        if request.method == "GET":
            return httpx.Response(200, json={"agent_id": "saved", "agent_name": "support"}, headers={"ETag": '"1"'})
        return httpx.Response(200, json={"agent_session_id": "s", "status": "RUNNING", "create_ts": 1})
    client = make_client(handler, async_)
    agent = Agent(client).with_llm(OpenAI(model="gpt-5.6-luna"))
    create = agent.create_async_ephemeral_session if async_ else agent.create_ephemeral_session
    session = create(channel="room", agent_uid="1", remote_uids=["2"], idle_timeout=30)
    result = session.start()
    if async_:
        await result
    assert requests[-1].url.path.endswith("/sessions/ephemeral")
    assert json.loads(requests[-1].content)["lifecycle"] == {"idle_timeout_ms": 30000}
    for saved in (False, True):
        owner = agent
        if saved:
            owner = await AsyncSavedAgent.get(client, "saved") if async_ else SavedAgent.get(client, "saved")
        call = owner.call if saved or not async_ else owner.call_async
        session = call(from_number="12345678-1234-1234-1234-123456789abc", to="+12025550123", call_policy={"max_ring_duration_ms": 30000})
        result = session.start()
        if async_:
            await result
        body = json.loads(requests[-1].content)
        assert body["transport"] == {"type": "telephony", "from": "12345678-1234-1234-1234-123456789abc", "to": "+12025550123", "call_policy": {"max_ring_duration_ms": 30000}}
        assert ("agent_id" in body) == saved
    with pytest.raises(ValueError, match="RTC"):
        (agent.call_async if async_ else agent.call)(from_number="n", to="+12025550123", channel="room")


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_assign_full_policy_and_empty_clear(async_):
    requests = []
    def handler(request):
        requests.append(request)
        return httpx.Response(200, json={"agent_id": "saved", "agent_name": "support", "number_id": "n", "number": "+12025550123"}, headers={"ETag": '"1"'})
    client = make_client(handler, async_)
    saved = await AsyncSavedAgent.get(client, "saved") if async_ else SavedAgent.get(client, "saved")
    for policy in ({"end_call": {"on_user_request": True}}, {}):
        result = saved.assign_number("n", call_policy=policy)
        if async_:
            await result
        assert json.loads(requests[-1].content)["inbound"]["call_policy"] == policy


def test_rtc_token_generated_once_and_explicit_tokens_preserved(monkeypatch):
    signed = []
    monkeypatch.setattr("agora_agent.agentkit.token.generate_convo_ai_token", lambda **kw: signed.append(kw) or "rtc-generated")
    client = make_client(lambda _: pytest.fail("no HTTP"))
    client.app_certificate = "certificate"
    agent = Agent(client).with_llm(OpenAI(model="gpt-5.6-luna"))
    session = agent.create_ephemeral_session(channel="room", agent_uid="1", remote_uids=["2"], idempotency_key="retry")
    client.app_certificate = "changed"
    assert prepare_start_body(session)["transport"]["token"] == "rtc-generated"
    assert signed[0]["app_certificate"] == "certificate"
    assert prepare_start_body(session)["transport"]["token"] == "rtc-generated" and len(signed) == 1
    for uid in (None, "0", "bot"):
        other = agent.create_ephemeral_session(channel="room", agent_uid=uid, remote_uids=["customer"] if uid == "bot" else ["2"])
        assert "token" not in prepare_start_body(other)["transport"]
    explicit = agent.create_ephemeral_session(channel="room", agent_uid="1", remote_uids=["2"], token="provided")
    assert prepare_start_body(explicit)["transport"]["token"] == "provided" and len(signed) == 1


def test_import_has_no_invalid_pydantic_config_warning():
    result = subprocess.run([sys.executable, "-W", "error::UserWarning", "-c", "import agora_agent"], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_response_metadata_fields_are_preserved():
    from agora_agent.v3.types import SecretKey, SecretSet, SessionResponse
    assert "analysis" in SessionResponse.__annotations__
    assert {"key", "create_ts", "update_ts"} <= SecretKey.__annotations__.keys()
    assert "keys" in SecretSet.__annotations__
    responses = [
        {"agent_session_id": "s", "status": "STOPPED", "analysis": {"status": "completed", "complete_ts": 12, "result": {"resolved": True}}},
        {"name": "prod", "keys": [{"key": "llm", "create_ts": 1, "update_ts": 2}]},
        {"name": "prod", "keys": ["llm"]},
        {"key": "llm", "create_ts": 1, "update_ts": 2},
    ]
    client = make_client(lambda _: httpx.Response(200, json=responses.pop(0)))
    assert client.v3.sessions.get(agent_session_id="s")["analysis"]["result"] == {"resolved": True}
    assert client.v3.secrets.get(name="prod")["keys"][0]["update_ts"] == 2
    assert client.v3.secrets.get(name="prod")["keys"] == ["llm"]
    assert client.v3.secrets.set_key(name="prod", key="llm", value="new", if_match='"1"')["update_ts"] == 2


def test_rtc_token_identity_range_and_non_idempotent_refresh(monkeypatch):
    signed = []
    monkeypatch.setattr("agora_agent.agentkit.token.generate_convo_ai_token", lambda **kw: signed.append(kw) or str(len(signed)))
    client = make_client(lambda _: pytest.fail("no HTTP"))
    client.app_certificate = "cert"
    agent = Agent(client).with_llm(OpenAI(model="gpt-5-mini"))
    session = agent.create_ephemeral_session(channel="r", agent_uid="1", remote_uids=["2"])
    assert prepare_start_body(session)["transport"]["token"] == "1"
    session._session_backend["successfully_started"] = True
    assert prepare_start_body(session)["transport"]["token"] == "2"
    large = agent.create_ephemeral_session(channel="r", agent_uid="4294967296", remote_uids=["2"])
    with pytest.raises(ValueError, match="32-bit"):
        prepare_start_body(large)


def test_raw_gemini_query_key_migrates_to_credentials():
    result = module({"vendor": "gemini", "url": "https://gemini.example/stream?alt=sse&key=inline", "params": {"model": "gemini"}}, "llm", [])
    assert result["credential"] == {"mode": "byok", "fields": {"api_key": "inline"}}
    assert result["url"] == "https://gemini.example/stream?alt=sse"


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_rtc_token_refreshes_on_restart_not_failed_retry(async_, monkeypatch):
    tokens = []
    bodies = []
    monkeypatch.setattr("agora_agent.agentkit.token.generate_convo_ai_token", lambda **kw: tokens.append(kw) or f"token-{len(tokens)}")
    def handler(request):
        if request.url.path.endswith("/stop"):
            return httpx.Response(200, json={})
        bodies.append(json.loads(request.content))
        if len(bodies) == 1:
            return httpx.Response(500, json={"reason": "Unknown", "detail": "retry"})
        return httpx.Response(200, json={"agent_session_id": "s", "status": "RUNNING", "create_ts": 1})
    client = make_client(handler, async_)
    client.app_certificate = "certificate"
    agent = Agent(client).with_llm(OpenAI(model="gpt-5-mini"))
    create = agent.create_async_ephemeral_session if async_ else agent.create_ephemeral_session
    session = create(channel="room", agent_uid="1", remote_uids=["2"])
    with pytest.raises(Exception):
        result = session.start()
        if async_:
            await result
    result = session.start()
    if async_:
        await result
    assert bodies[0] == bodies[1] and len(tokens) == 1
    result = session.stop()
    if async_:
        await result
    result = session.start()
    if async_:
        await result
    assert bodies[-1]["transport"]["token"] == "token-2" and len(tokens) == 2
