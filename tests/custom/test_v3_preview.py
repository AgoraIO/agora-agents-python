"""Offline contract tests for the additive v3 preview and v2 boundary."""
import asyncio
import json
import threading

import httpx
import pytest

from agora_agent import (
    Agent,
    Agora,
    Area,
    AsyncAgora,
    AsyncDeployedAgent,
    DeepgramSTT,
    DeployedAgent,
    NumberNotFoundError,
    OpenAI,
    OpenAITTS,
    PreconditionFailedError,
    SecretRefNotSupportedError,
    UnsupportedFieldError,
    V3Options,
    secret_ref,
)
from agora_agent.agentkit.v3 import build_body, module

OPERATIONS = [
    ("agents", "create", {"agent_name": "Support"}, "POST", "agents", {"agent_name": "Support"}),
    ("agents", "list", {"limit": 5, "cursor": "next", "order": "create_ts.asc"}, "GET", "agents", None),
    ("agents", "get", {"agent_id": "agent/a"}, "GET", "agents/agent%2Fa", None),
    ("agents", "update", {"agent_id": "a", "if_match": '"1"', "instructions": None}, "PATCH", "agents/a", {"instructions": None}),
    ("agents", "delete", {"agent_id": "a"}, "DELETE", "agents/a", None),
    ("secrets", "create", {"name": "prod", "secrets": {"key": "private"}}, "POST", "secrets", {"name": "prod", "secrets": {"key": "private"}}),
    ("secrets", "list", {}, "GET", "secrets", None),
    ("secrets", "get", {"name": "prod"}, "GET", "secrets/prod", None),
    ("secrets", "replace", {"name": "prod", "if_match": '"1"', "secrets": {"k": "v"}}, "PUT", "secrets/prod", {"secrets": {"k": "v"}}),
    ("secrets", "update", {"name": "prod", "if_match": '"1"', "secrets": {"k": None}}, "PATCH", "secrets/prod", {"secrets": {"k": None}}),
    ("secrets", "delete", {"name": "prod", "if_match": '"1"'}, "DELETE", "secrets/prod", None),
    ("secrets", "set_key", {"name": "prod", "key": "k", "if_none_match": "*", "value": "v"}, "PUT", "secrets/prod/keys/k", {"value": "v"}),
    ("secrets", "delete_key", {"name": "prod", "key": "k", "if_match": '"1"'}, "DELETE", "secrets/prod/keys/k", None),
    ("numbers", "create", {"number": "+12025550123", "sip_trunk": {"hostname": "sip.example"}}, "POST", "numbers", {"number": "+12025550123", "sip_trunk": {"hostname": "sip.example"}}),
    ("numbers", "list", {}, "GET", "numbers", None),
    ("numbers", "get", {"number_id": "n"}, "GET", "numbers/n", None),
    ("numbers", "update", {"number_id": "n", "if_match": '"1"', "inbound": {"agent": None}}, "PATCH", "numbers/n", {"inbound": {"agent": None}}),
    ("numbers", "delete", {"number_id": "n"}, "DELETE", "numbers/n", None),
    ("sessions", "list", {"channel": "room", "status": "ACTIVE", "started_after": 12, "started_before": 25}, "GET", "sessions", None),
    ("sessions", "get", {"agent_session_id": "s"}, "GET", "sessions/s", None),
    ("sessions", "start", {"agent_id": "saved", "transport": {"type": "rtc", "channel": "room", "uid": "1", "subscribe_uids": ["2"]}, "labels": {"owner": "test"}}, "POST", "sessions", {"agent_id": "saved", "transport": {"type": "rtc", "channel": "room", "uid": "1", "subscribe_uids": ["2"]}, "labels": {"owner": "test"}}),
    ("sessions", "start_ephemeral", {"agent": {"instructions": "Help"}, "transport": {"type": "rtc", "channel": "room", "uid": "1", "subscribe_uids": ["2"]}, "lifecycle": {"max_duration_ms": 120000}}, "POST", "sessions/ephemeral", {"agent": {"instructions": "Help"}, "transport": {"type": "rtc", "channel": "room", "uid": "1", "subscribe_uids": ["2"]}, "lifecycle": {"max_duration_ms": 120000}}),
    ("sessions", "update", {"agent_session_id": "s", "transport": {"token": "new-token"}, "agent": {"overrides": {"pipeline": {"llm": {"params": {"temperature": 0.2}}}}}}, "PATCH", "sessions/s", {"transport": {"token": "new-token"}, "agent": {"overrides": {"pipeline": {"llm": {"params": {"temperature": 0.2}}}}}}),
    ("sessions", "stop", {"agent_session_id": "session/a"}, "POST", "sessions/session%2Fa/stop", None),
    ('campaigns', 'create', {'name': 'Outreach', 'agent_id': 'a', 'contacts': [{'phone': '+12025550123'}], 'schedule': {'mode': 'immediate'}, 'transport': {'type': 'telephony', 'from': 'n'}, 'idempotency_key': 'key'}, 'POST', 'campaigns', {'name': 'Outreach', 'agent_id': 'a', 'contacts': [{'phone': '+12025550123'}], 'schedule': {'mode': 'immediate'}, 'transport': {'type': 'telephony', 'from': 'n'}}),
    ('campaigns', 'list', {'limit': 5, 'status': 'running'}, 'GET', 'campaigns', None),
    ('campaigns', 'get', {'campaign_id': 'c/a'}, 'GET', 'campaigns/c%2Fa', None),
    ('campaigns', 'update', {'campaign_id': 'c', 'if_match': '"1"', 'pacing': {'max_concurrent': 5}}, 'PATCH', 'campaigns/c', {'pacing': {'max_concurrent': 5}}),
    ('campaigns', 'delete', {'campaign_id': 'c'}, 'DELETE', 'campaigns/c', None),
    ('campaigns', 'pause', {'campaign_id': 'c', 'idempotency_key': 'key'}, 'POST', 'campaigns/c:pause', None),
    ('campaigns', 'resume', {'campaign_id': 'c', 'idempotency_key': 'key'}, 'POST', 'campaigns/c:resume', None),
    ('campaigns', 'cancel', {'campaign_id': 'c', 'idempotency_key': 'key'}, 'POST', 'campaigns/c:cancel', None),
]


def make_client(handler, async_=False, **kwargs):
    transport = httpx.MockTransport(handler)
    cls = AsyncAgora if async_ else Agora
    http = httpx.AsyncClient(transport=transport) if async_ else httpx.Client(transport=transport)
    return cls(area=Area.US, app_id="project", auth_token="raw-token",
               httpx_client=http, v3=V3Options(base_url="https://stage.example/", headers={"X-Test-Context": "test"}), **kwargs)


def check_request(request, operation):
    _, _, kwargs, method, suffix, body = operation
    assert request.method == method
    assert request.url.raw_path.split(b"?")[0] == ("/conversational-ai/v1/projects/project/" + suffix).encode()
    assert request.headers["Authorization"] == "agora token=raw-token"
    assert request.headers["X-Test-Context"] == "test"
    if body is not None:
        assert json.loads(request.content) == body
    elif method == "POST":
        assert request.content == b""
    for key, header in (("if_match", "If-Match"), ("if_none_match", "If-None-Match"), ("idempotency_key", "Idempotency-Key")):
        if key in kwargs:
            assert request.headers[header] == kwargs[key]
    for key in ("limit", "cursor", "order", "status", "channel", "started_after", "started_before"):
        if key in kwargs:
            assert request.url.params[key] == str(kwargs[key])


@pytest.mark.parametrize("operation", OPERATIONS)
def test_all_documented_sync_wire_operations(operation):
    def handler(request):
        check_request(request, operation)
        return httpx.Response(200, json={"ok": True}, headers={"ETag": '"etag"', "Agora-Request-Id": "trace"})
    client = make_client(handler)
    resource, method, kwargs, *_ = operation
    response = getattr(getattr(client.v3, resource).with_raw_response, method)(**kwargs)
    assert response.data == {"ok": True}
    assert response.etag == '"etag"'
    assert response.headers["Agora-Request-Id"] == "trace"
    assert getattr(getattr(client.v3, resource), method)(**kwargs) == {"ok": True}


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", OPERATIONS)
async def test_all_documented_async_wire_operations(operation):
    def handler(request):
        check_request(request, operation)
        return httpx.Response(200, json={"ok": True}, headers={"ETag": '"etag"'})
    client = make_client(handler, True)
    resource, method, kwargs, *_ = operation
    response = await getattr(getattr(client.v3, resource).with_raw_response, method)(**kwargs)
    assert response.etag == '"etag"'
    assert await getattr(getattr(client.v3, resource), method)(**kwargs) == {"ok": True}


def test_namespace_is_additive_and_out_of_scope_features_absent():
    client = make_client(lambda _: httpx.Response(200, json={}))
    assert client.agents is not client.v3.agents
    assert not hasattr(client.v3.sessions, "create")
    assert client.campaigns is client.v3.campaigns
    assert not hasattr(DeployedAgent, "start_call")


def test_reject_empty_identifiers_and_required_etag():
    client = make_client(lambda _: pytest.fail("request must not be sent"))
    for kwargs in ({"agent_id": ""}, {"agent_id": "  "}, {"agent_id": "."}, {"agent_id": ".."}, {"agent_id": "a", "appid": ""}):
        with pytest.raises(ValueError):
            client.v3.agents.get(**kwargs)
    with pytest.raises(TypeError):
        client.v3.agents.update(agent_id="a", instructions="x")


def test_no_write_retries_and_latest_conflict():
    calls = []
    def handler(request):
        calls.append(request)
        return httpx.Response(412 if request.method == "PATCH" else 200, json={"agent_id": "a"}, headers={"Agora-Request-Id": "trace"})
    client = make_client(handler)
    with pytest.raises(PreconditionFailedError) as exc:
        client.v3.agents.update(agent_id="a", if_match='"old"', instructions="x", request_options={"max_retries": 3})
    assert len(calls) == 1
    assert exc.value.headers["agora-request-id"] == "trace"
    assert exc.value.latest() == {"agent_id": "a"}
    assert calls[-1].method == "GET"


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_latest_reload_does_not_replay_additional_write_body(async_):
    calls = []
    def handler(request):
        calls.append(request)
        return httpx.Response(412 if request.method == "PATCH" else 200, json={"agent_id": "a"})
    client = make_client(handler, async_)
    with pytest.raises(PreconditionFailedError) as caught:
        result = client.v3.agents.update(
            agent_id="a", if_match='"old"', instructions="updated",
            request_options={"additional_body_parameters": {"messages": [{"role": "user", "content": "write-only"}]}},
        )
        if async_:
            await result
    latest = caught.value.latest()
    if async_:
        latest = await latest
    assert latest == {"agent_id": "a"}
    assert calls[0].method == "PATCH"
    assert json.loads(calls[0].content)["messages"] == [{"role": "user", "content": "write-only"}]
    assert calls[1].method == "GET"
    assert calls[1].content == b""


@pytest.mark.parametrize("resource,kwargs", [("agents", {"agent_name": "x"}), ("numbers", {"number": "+12025550123", "sip_trunk": {"hostname": "sip.example"}})])
def test_nonidempotent_create_is_never_retried(resource, kwargs):
    calls = []
    def handler(request):
        calls.append(request)
        return httpx.Response(500, json={"detail": "unknown outcome"})
    client = make_client(handler)
    with pytest.raises(Exception):
        getattr(client.v3, resource).create(**kwargs, request_options={"max_retries": 4})
    assert len(calls) == 1


def test_cursor_pagination_and_loop_guard():
    calls = []
    def handler(request):
        calls.append(request)
        cursor = request.url.params.get("cursor")
        return httpx.Response(200, json={"data": {"count": 1, "list": [{"number_id": cursor or "first"}]}, "has_more": not cursor, "next_cursor": "second" if not cursor else None})
    client = make_client(handler)
    assert [x["number_id"] for x in client.v3.numbers.iter_all(limit=1)] == ["first", "second"]
    assert calls[-1].url.params["cursor"] == "second"


def configured(client):
    return (Agent(client=client)
        .with_stt(DeepgramSTT(api_key=secret_ref("prod", "dg"), model="nova-3"))
        .with_llm(OpenAI(api_key=secret_ref("prod", "openai"), base_url="https://api.openai.com/v1/chat/completions", model="gpt-4o-mini",
                        system_messages=[{"role": "system", "content": "Vendor instructions"}, {"role": "user", "content": "Hello"}], greeting_message="Hi"))
        .with_tts(OpenAITTS(api_key=secret_ref("prod", "tts"), base_url="https://api.openai.com/v1/audio/speech", voice="alloy", model="tts-1")))


def test_deploy_mapping_and_immutable_variables():
    calls = []
    def handler(request):
        calls.append(request)
        return httpx.Response(201, json={"agent_id": "a", "agent_name": "Support"}, headers={"ETag": '"1"'})
    client = make_client(handler)
    base = configured(client)
    agent = base.with_variable("resolved", {"type": "bool", "extract": True, "description": "Was the issue resolved?"}).with_greeting("fallback")
    deployed = agent.deploy(name="Support")
    body = json.loads(calls[0].content)
    assert body["instructions"] == "Vendor instructions"
    assert body["messages"] == [{"role": "user", "content": "Hello"}]
    assert body["greeting"] == {"mode": "text", "text": "Hi"}
    assert body["variables"]["resolved"]["type"] == "bool"
    assert body["pipeline"]["asr"] == {"vendor": "deepgram", "model": "nova-3", "credential": {"mode": "byok", "fields": {"api_key": "$secrets.prod.dg"}}}
    assert body["pipeline"]["llm"]["credential"]["fields"]["api_key"] == "$secrets.prod.openai"
    assert "variables" not in build_body(base)
    assert deployed.raw is client.v3.agents
    assert (deployed.id, deployed.name, deployed.etag) == ("a", "Support", '"1"')


def test_redeploy_recursively_clears_readable_fields_and_writeonly_key():
    calls = []
    old = {"agent_id": "a", "agent_name": "Old", "create_ts": 1, "update_ts": 2,
           "instructions": "stale", "variables": {"stale": {"type": "str"}},
           "pipeline": {"mode": "cascaded", "llm": {"params": {"stale": True}, "credential": {"mode": "byok", "has_api_key": True, "api_key_source": "secret"}}, "asr": {"vendor": "old"}}}
    def handler(request):
        calls.append(request)
        return httpx.Response(200, json=old if request.method == "GET" else {"agent_id": "a", "agent_name": "New"}, headers={"ETag": '"old"'})
    agent = Agent(client=make_client(handler)).with_llm(OpenAI(model="gpt-4o-mini", temperature=.3))
    agent.deploy(name="New", agent_id="a")
    patch = json.loads(calls[-1].content)
    assert calls[-1].headers["If-Match"] == '"old"'
    assert patch["instructions"] is None and patch["variables"] is None
    assert "agent_id" not in patch and "create_ts" not in patch and "update_ts" not in patch
    assert patch["pipeline"]["asr"] is None
    assert patch["pipeline"]["llm"]["params"]["stale"] is None
    assert patch["pipeline"]["llm"]["credential"] == {"mode": "managed", "fields": None}


def test_real_turn_interruption_greeting_and_silence_mapping():
    client = make_client(lambda _: pytest.fail("pure mapping"))
    agent = (configured(client)
        .with_turn_detection({"mode": "default", "language": "en-US", "config": {"speech_threshold": .7,
            "start_of_speech": {"mode": "vad", "vad_config": {"interrupt_duration_ms": 180, "prefix_padding_ms": 500}},
            "end_of_speech": {"mode": "semantic", "semantic_config": {"max_wait_ms": 2000, "silence_duration_ms": 320}}}})
        .with_interruption({"enable": True, "mode": "keywords", "keywords_config": {"trigger_keywords": ["stop"]}})
        .with_parameters({"silence_config": {"timeout_ms": 5000, "action": "speak", "content": "Hello?"}}))
    body = build_body(agent)
    turn = body["pipeline"]["turn_detection"]
    assert turn["speech_threshold"] == .7
    assert turn["start_of_speech"] == {"type": "vad", "interrupt_duration_ms": 180, "prefix_padding_ms": 500}
    assert turn["end_of_speech"]["max_wait_ms"] == 2000
    assert turn["interruption"] == {"mode": "keywords", "keywords": ["stop"]}
    assert body["pipeline"]["asr"]["language"] == "en-US"
    assert body["pipeline"]["silence_config"]["enabled"] is True
    disabled = build_body(agent.with_interruption({"enable": False, "disabled_config": {"strategy": "ignore"}}))
    assert disabled["pipeline"]["turn_detection"]["interruption"] == {"mode": "off", "when_off": "ignore"}


@pytest.mark.parametrize("name,definition", [("Bad", {"type": "str"}), ("x", {"type": "string"}), ("x", {"type": "bool", "extract": True}), ("x", {"type": "str", "extract": True, "description": " "})])
def test_variable_validation(name, definition):
    with pytest.raises(ValueError):
        Agent(client=make_client(lambda _: None)).with_variable(name, definition)


def test_strict_unsupported_fields_are_aggregated_before_network():
    agent = (Agent(client=make_client(lambda _: pytest.fail("must not send")), labels={"tag": "v"}, rtc={}, sal={}, pipeline_id="p")
             .with_parameters({"enable_metrics": True, "data_channel": "rtm"}))
    with pytest.raises(UnsupportedFieldError) as exc:
        agent.deploy()
    assert {"labels", "rtc", "sal", "pipeline_id", "parameters.enable_metrics", "parameters.data_channel"} <= set(exc.value.fields)


def test_multipart_credentials_and_numeric_skip_patterns_rejected():
    errors = []
    module({"vendor": "amazon", "params": {"aws_access_key_id": "a", "aws_secret_access_key": "s"}, "skip_patterns": [1]}, "tts", errors)
    assert not any("aws_secret_access_key" in x for x in errors)
    assert any("skip_patterns" in x for x in errors)
    errors = []
    result = module({"vendor": "microsoft", "params": {"api_subscription_key": "key", "region": "eastus"}}, "tts", errors)
    assert not errors
    assert result["credential"] == {"mode": "byok", "fields": {"key": "key"}}
    assert result["params"] == {"region": "eastus"}


def test_secret_ref_v2_guard_at_all_boundaries():
    agent = configured(make_client(lambda _: pytest.fail("must not send")))
    with pytest.raises(SecretRefNotSupportedError, match="requires save"):
        agent.to_properties(channel="c", agent_uid="1", remote_uids=["*"])
    assert agent.create_session(channel="c", agent_uid="1", remote_uids=["2"]).status == "idle"
    assert configured(make_client(lambda _: pytest.fail("must not send"), True)).create_async_session(channel="c", agent_uid="1", remote_uids=["2"]).status == "idle"


def test_number_resolution_pagination_conflict_retry_and_unassign():
    calls = []
    patches = []
    def handler(request):
        calls.append(request)
        if request.url.path.endswith("/numbers"):
            second = "cursor" in request.url.params
            return httpx.Response(200, json={"data": {"list": [{"number_id": "n", "number": "+1 (202) 555-0123"}] if second else []}, "has_more": not second, "next_cursor": "second" if not second else None})
        if request.method == "GET":
            return httpx.Response(200, json={"number_id": "n"}, headers={"ETag": '"fresh"'})
        patches.append(json.loads(request.content))
        return httpx.Response(412 if len(patches) == 1 else 200, json={"number_id": "n"})
    client = make_client(handler)
    from agora_agent.v3 import RawResponse
    deployed = DeployedAgent(client, RawResponse({"agent_id": "a", "agent_name": "Support"}, httpx.Headers(), 200, None))
    assert deployed.assign_number("+12025550123", max_call_duration_seconds=900)["number_id"] == "n"
    assert len(calls) == 6  # Two list pages, two GETs and two PATCH attempts.
    assert patches[-1] == {"inbound": {"agent": "a", "call_policy": {"max_call_duration_seconds": 900}}}
    deployed.unassign_number({"number_id": "n"})
    assert patches[-1] == {"inbound": {"agent": None}}


def test_number_not_found_scoped_to_project():
    client = make_client(lambda _: httpx.Response(200, json={"data": {"list": []}, "has_more": False, "next_cursor": None}))
    from agora_agent.v3 import RawResponse
    deployed = DeployedAgent(client, RawResponse({"agent_id": "a", "agent_name": "Support"}, httpx.Headers(), 200, None))
    with pytest.raises(NumberNotFoundError, match="project"):
        deployed.assign_number("+12025550123")


@pytest.mark.asyncio
async def test_async_deploy_assign_get_delete_and_conflict_latest():
    calls = []
    conflict = False
    def handler(request):
        nonlocal conflict
        calls.append(request)
        if "/numbers/n" in request.url.path:
            if request.method == "PATCH" and not conflict:
                conflict = True
                return httpx.Response(412, json={"reason": "stale"})
            return httpx.Response(200, json={"number_id": "n"}, headers={"ETag": '"n"'})
        return httpx.Response(200, json={"agent_id": "a", "agent_name": "Support"}, headers={"ETag": '"a"'})
    client = make_client(handler, True)
    deployed = await configured(client).deploy_async(name="Support")
    assert isinstance(deployed, AsyncDeployedAgent)
    assert (await deployed.assign_number("n"))["number_id"] == "n"
    assert (await deployed.unassign_number("n"))["number_id"] == "n"
    assert (await AsyncDeployedAgent.get(client, "a")).id == "a"
    await deployed.delete()
    assert calls[-1].method == "DELETE"
    with pytest.raises(TypeError):
        configured(client).deploy()
    with pytest.raises(TypeError):
        await configured(make_client(handler)).deploy_async()


@pytest.mark.asyncio
async def test_async_cursor_pages_conflict_latest_and_redeploy():
    calls = []
    def handler(request):
        calls.append(request)
        if request.url.path.endswith("/sessions"):
            second = request.url.params.get("cursor") == "second"
            return httpx.Response(200, json={"data": {"count": 1, "list": [{"agent_session_id": "s2" if second else "s1"}]}, "has_more": not second, "next_cursor": None if second else "second"})
        if "/secrets/" in request.url.path:
            if request.method != "GET":
                return httpx.Response(412, json={"detail": "stale"})
            return httpx.Response(200, json={"name": "prod"}, headers={"ETag": '"new"'})
        if request.method == "GET":
            return httpx.Response(200, json={"agent_id": "a", "agent_name": "Old", "instructions": "remove"}, headers={"ETag": '"v1"'})
        return httpx.Response(200, json={"agent_id": "a", "agent_name": "New"}, headers={"ETag": '"v2"'})
    client = make_client(handler, True)
    assert [x["agent_session_id"] async for x in client.v3.sessions.iter_all(limit=1)] == ["s1", "s2"]
    with pytest.raises(PreconditionFailedError) as exc:
        await client.v3.secrets.set_key(name="prod", key="k", value="hidden", if_match='"old"')
    assert await exc.value.latest() == {"name": "prod"}
    assert calls[-1].url.path.endswith("/secrets/prod")
    deployed = await Agent(client=client).deploy_async(name="New", agent_id="a")
    assert deployed.etag == '"v2"'
    assert json.loads(calls[-1].content)["instructions"] is None


def test_environment_override_and_shared_token_auth(monkeypatch):
    calls = []
    monkeypatch.setenv("AGORA_AGENTS_V3_BASE_URL", "https://env-stage.example")
    client = Agora(area=Area.US, app_id="project", app_certificate="cert", auth_token="raw-token",
                   httpx_client=httpx.Client(transport=httpx.MockTransport(lambda r: calls.append(r) or httpx.Response(200, json={}))))
    client.v3.agents.list()
    assert calls[-1].url.host == "env-stage.example"
    assert calls[-1].headers["Authorization"] == "agora token=raw-token"
    # An explicit option wins, and does not change v2's configured base URL.
    explicit = make_client(lambda r: calls.append(r) or httpx.Response(200, json={}))
    before = explicit._client_wrapper.get_base_url()
    explicit.v3.agents.list()
    assert calls[-1].url.host == "stage.example"
    assert explicit._client_wrapper.get_base_url() == before


def test_default_auth_token_is_refreshed_per_v3_call(monkeypatch):
    calls = []
    generated = []
    def token(**kwargs):
        generated.append(kwargs)
        return "fresh-" + str(len(generated))
    monkeypatch.setattr("agora_agent.v3._transport.generate_convo_ai_token", token)
    client = Agora(area=Area.US, app_id="0" * 32, app_certificate="1" * 32,
                   httpx_client=httpx.Client(transport=httpx.MockTransport(lambda r: calls.append(r) or httpx.Response(200, json={}))))
    client.v3.agents.list()
    client.v3.sessions.list()
    assert [r.headers["Authorization"] for r in calls] == ["agora token=fresh-1", "agora token=fresh-2"]
    assert generated[0]["app_id"] == "0" * 32


def test_audio_greeting_mapping():
    base = configured(make_client(lambda _: None))
    base._llm = {**base._llm, "greeting_audio_url": "https://audio.example/greeting.wav",
                 "greeting_configs": {"audio_download_timeout_ms": 1000, "audio_pcm_sample_rate": 16000}}
    greeting = build_body(base)["greeting"]
    assert greeting == {"mode": "audio", "url": "https://audio.example/greeting.wav", "text": "Hi", "download_timeout_ms": 1000, "pcm_sample_rate": 16000}


def test_greeting_playback_mode_aliases_and_unsupported_mode():
    client = make_client(lambda _: pytest.fail("pure mapping"))
    for old, new in (("single_first", "first_join"), ("single_every", "each_join")):
        body = build_body(Agent(client=client, greeting="Hello", greeting_configs={"mode": old}))
        assert body["greeting"] == {"mode": "text", "text": "Hello", "on": new}
    with pytest.raises(UnsupportedFieldError, match="greeting_configs.mode"):
        build_body(Agent(client=client, greeting="Hello", greeting_configs={"mode": "unknown"}))
    with pytest.raises(UnsupportedFieldError, match="greeting_configs.pcm_sample_rate"):
        build_body(Agent(client=client, greeting="Hello", greeting_configs={"audio_pcm_sample_rate": 16000}))


def test_managed_minimax_preset_hint_becomes_provider_param():
    from agora_agent import MiniMaxTTS
    client = make_client(lambda _: pytest.fail("pure mapping"))
    agent = Agent(client=client).with_tts(MiniMaxTTS(model="speech-2.6-turbo", voice_id="voice"))
    tts = build_body(agent)["pipeline"]["tts"]
    assert tts["credential"] == {"mode": "managed"}
    assert tts["params"]["model"] == "speech-2.6-turbo"
    assert "_minimax_preset_model" not in tts
    explicit = Agent(client=client).with_tts(MiniMaxTTS(
        model="speech-2.6-turbo", voice_id="voice", additional_params={"model": "speech-2.8-turbo"}
    ))
    assert build_body(explicit)["pipeline"]["tts"]["params"]["model"] == "speech-2.8-turbo"


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_list_numbers_scans_pages_filters_agent_and_avoids_detail_gets(async_):
    calls = []
    def handler(request):
        calls.append(request)
        assert request.method == "GET" and request.url.path.endswith("/numbers")
        assert request.url.params["limit"] == "100"
        second = request.url.params.get("cursor") == "second"
        numbers = ([{"number_id": "match2", "inbound": {"agent": "a"}},
                    {"number_id": "unassigned", "inbound": {"agent": None}}] if second else
                   [{"number_id": "match1", "inbound": {"agent": "a"}},
                    {"number_id": "other", "inbound": {"agent": "b"}},
                    {"number_id": "null", "inbound": None}, {"number_id": "missing"}])
        return httpx.Response(200, json={"data": {"count": len(numbers), "list": numbers},
                                        "has_more": not second, "next_cursor": None if second else "second"})
    from agora_agent.v3 import RawResponse
    client = make_client(handler, async_)
    cls = AsyncDeployedAgent if async_ else DeployedAgent
    deployed = cls(client, RawResponse({"agent_id": "a", "agent_name": "Support"}, httpx.Headers(), 200, None))
    numbers = await deployed.list_numbers() if async_ else deployed.list_numbers()
    assert [number["number_id"] for number in numbers] == ["match1", "match2"]
    assert len(calls) == 2


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_deploy_preserves_interaction_and_provider_languages(async_):
    requests = []
    def handler(request):
        requests.append(request)
        return httpx.Response(201, json={"agent_id": "a", "agent_name": "German"}, headers={"ETag": '"1"'})
    agent = (Agent(client=make_client(handler, async_))
             .with_stt(DeepgramSTT(api_key=secret_ref("prod", "dg"), model="nova-3", language="fr"))
             .with_turn_detection({"mode": "default", "language": "de-DE"}))
    if async_:
        await agent.deploy_async(name="German")
    else:
        agent.deploy(name="German")
    pipeline = json.loads(requests[0].content)["pipeline"]
    assert pipeline["asr"]["language"] == "de-DE"
    assert "language" not in pipeline["asr"].get("params", {})
    assert "language" not in pipeline.get("turn_detection", {})
    v2 = agent.with_stt(DeepgramSTT(api_key="inline", model="nova-3", language="fr")).to_properties(channel="room", agent_uid="1", remote_uids=["*"], token="rtc",
                             allow_missing_vendor_categories={"llm", "tts"}).model_dump(exclude_none=True)
    assert v2["asr"]["language"] == pipeline["asr"]["language"]
    assert v2["asr"]["params"]["language"] == "fr"


def test_explicit_interaction_language_uses_existing_managed_asr_fallback():
    requests = []
    def handler(request):
        requests.append(request)
        return httpx.Response(201, json={"agent_id": "a", "agent_name": "Japanese"}, headers={"ETag": '"1"'})
    client = make_client(handler)
    Agent(client=client).with_turn_detection({"language": "ja-JP"}).deploy(name="Japanese")
    pipeline = json.loads(requests[0].content)["pipeline"]
    assert pipeline["asr"] == {"vendor": "ares", "language": "ja-JP", "credential": {"mode": "managed"}}
    assert "language" not in pipeline.get("turn_detection", {})
    assert "asr" not in build_body(Agent(client=client))["pipeline"]
    assert "asr" not in build_body(Agent(client=client).with_llm(OpenAI(model="gpt-4o-mini")))["pipeline"]
    default = build_body(Agent(client=client).with_stt(DeepgramSTT(api_key=secret_ref("prod", "dg"), model="nova-3", language="fr")))
    assert default["pipeline"]["asr"]["language"] == "fr"
    assert "language" not in default["pipeline"]["asr"].get("params", {})


@pytest.mark.parametrize("options", [["same", "same"], [1, 1.0], [0, -0.0]])
def test_variable_options_reject_json_numeric_duplicates(options):
    with pytest.raises(ValueError, match="unique"):
        Agent(client=make_client(lambda _: pytest.fail("no network expected"))).with_variable("choice", type="float", options=options)


def test_variable_options_distinguish_booleans_strings_and_numbers():
    Agent(client=make_client(lambda _: pytest.fail("no network expected"))).with_variable("choice", type="str", options=[True, 1, "1", False, 0])


@pytest.mark.asyncio
@pytest.mark.parametrize("async_client", [False, True])
async def test_conflict_latest_preserves_context_without_write_conditions(async_client):
    calls = []
    extra = {"iF-mAtCh": '"old"', "If-None-Match": "*", "Idempotency-Key": "once",
             "Authorization": "agora token=override", "X-Custom": "kept"}
    def handler(request):
        calls.append(request)
        if request.method == "PATCH":
            return httpx.Response(412, json={"error": "stale"})
        assert not any(key in request.headers for key in ("If-Match", "If-None-Match", "Idempotency-Key"))
        assert request.headers["Authorization"] == "agora token=override"
        assert request.headers["X-Custom"] == "kept"
        return httpx.Response(200, json={"agent_id": "a"})
    client = make_client(handler, async_client)
    with pytest.raises(PreconditionFailedError) as exc:
        result = client.v3.agents.update(agent_id="a", if_match='"old"', request_options={"additional_headers": extra})
        if async_client:
            await result
    result = exc.value.latest()
    if async_client:
        result = await result
    assert result == {"agent_id": "a"}
    assert len(calls) == 2
    assert extra["iF-mAtCh"] == '"old"'


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_one_builder_creates_session_or_saved_handle_with_unversioned_provisioning(async_):
    import copy

    from agora_agent import AsyncSavedAgent, SavedAgent
    from agora_agent.agentkit import AsyncSavedAgent as AgentKitAsyncSavedAgent
    from agora_agent.agentkit import SavedAgent as AgentKitSavedAgent
    assert SavedAgent is DeployedAgent is AgentKitSavedAgent
    assert AsyncSavedAgent is AsyncDeployedAgent is AgentKitAsyncSavedAgent
    calls = []
    stored = {}
    def handler(request):
        calls.append(request)
        path = request.url.path
        if path.endswith("/join"):
            payload = json.loads(request.content)
            assert payload["properties"]["llm"]["api_key"] == "inline-key"
            return httpx.Response(200, json={"agent_id": "running-session"})
        if path.endswith("/secrets"):
            return httpx.Response(201, json={"name": "support", "keys": ["openai"], "create_ts": 1, "update_ts": 1})
        if path.endswith("/numbers"):
            return httpx.Response(201, json={"number_id": "n", "number": "+12025550123", "create_ts": 1})
        if "/numbers/n" in path:
            return httpx.Response(200, json={"number_id": "n", "number": "+12025550123", "create_ts": 1}, headers={"ETag": '"n"'})
        if request.method in ("POST", "PATCH"):
            payload = json.loads(request.content)
            stored.update(payload)
            stored.update(agent_id="a", create_ts=1, update_ts=2)
            return httpx.Response(200, json=stored, headers={"ETag": '"saved"'})
        return httpx.Response(200, json=stored, headers={"ETag": '"current"'})
    client = make_client(handler, async_)
    assert client.secrets is client.v3.secrets
    assert client.numbers is client.v3.numbers
    agent = (Agent(client=client)
             .with_stt(DeepgramSTT(api_key="asr-key", model="nova-3"))
             .with_llm(OpenAI(api_key="inline-key", base_url="https://api.openai.com/v1/chat/completions", model="gpt-4o-mini"))
             .with_tts(OpenAITTS(api_key="tts-key", base_url="https://api.openai.com/v1/audio/speech", model="tts-1", voice="alloy")))
    snapshot = copy.deepcopy(agent.config)
    saved_config = configured(client)
    if async_:
        session = agent.create_async_session(channel="room", agent_uid="1", remote_uids=["*"], token="rtc")
        assert await session.start() == "running-session"
        await client.secrets.create(name="support", secrets={"openai": "key"})
        number = await client.numbers.create(number="+12025550123", sip_trunk={"hostname": "sip.example"})
        saved = await saved_config.save_async(name="Support")
        await saved.assign_number(number)
        updated = await saved.update(saved_config.with_greeting("Updated"))
        assert isinstance(saved, AsyncSavedAgent)
        loaded = await AsyncSavedAgent.get(client, saved.id)
    else:
        session = agent.create_session(channel="room", agent_uid="1", remote_uids=["*"], token="rtc")
        assert session.start() == "running-session"
        client.secrets.create(name="support", secrets={"openai": "key"})
        number = client.numbers.create(number="+12025550123", sip_trunk={"hostname": "sip.example"})
        saved = saved_config.save(name="Support")
        saved.assign_number(number)
        updated = saved.update(saved_config.with_greeting("Updated"))
        assert isinstance(saved, SavedAgent)
        loaded = SavedAgent.get(client, saved.id)
    assert updated.id == loaded.id == saved.id == "a"
    assert updated.name == saved.name == "Support"
    assert agent.config == snapshot
    assert callable(saved.create_session)
    assert hasattr(saved, "create_async_session") is async_
    assert sum(r.method == "POST" and r.url.path.endswith("/agents") for r in calls) == 1
    patch = next(r for r in calls if r.method == "PATCH" and r.url.path.endswith("/agents/a"))
    assert patch.headers["If-Match"] == '"current"'
    assert json.loads(patch.content)["agent_name"] == "Support"
    if async_:
        renamed = await saved.update(saved_config, name="Renamed")
    else:
        renamed = saved.update(saved_config, name="Renamed")
    assert renamed.name == "Renamed"
    assert saved.name == "Support"


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_saved_update_rejects_another_client_before_network(async_):
    from agora_agent import AsyncSavedAgent, SavedAgent
    from agora_agent.v3 import RawResponse
    client = make_client(lambda _: pytest.fail("must not send"), async_)
    other = make_client(lambda _: pytest.fail("must not send"), async_)
    cls = AsyncSavedAgent if async_ else SavedAgent
    saved = cls(client, RawResponse({"agent_id": "a", "agent_name": "Support"}, httpx.Headers(), 200, None))
    with pytest.raises(ValueError, match="same client"):
        if async_:
            await saved.update(Agent(client=other))
        else:
            saved.update(Agent(client=other))


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.parametrize("stored", [False, True])
@pytest.mark.asyncio
async def test_saved_and_secret_ephemeral_lifecycle(async_, stored):
    from agora_agent import AsyncSavedAgent, SavedAgent
    from agora_agent.v3 import RawResponse
    calls = []
    def handler(request):
        calls.append(request)
        path = request.url.path
        if request.method == "POST" and not path.endswith("/stop"):
            body = json.loads(request.content)
            assert body["transport"] == {"type": "rtc", "channel": "room", "uid": "1", "subscribe_uids": ["2"]}
            assert body["lifecycle"] == {"idle_timeout_ms": 1500, "max_duration_ms": 120000}
            assert "client_reference" not in body
            if stored:
                assert body["agent_id"] == "stored-id"
                assert body["labels"] == {"owner": "test"}
                assert path.endswith("/sessions")
            else:
                assert path.endswith("/sessions/ephemeral")
                assert "agent_name" not in body["agent"]
                assert body["agent"]["pipeline"]["llm"]["credential"]["fields"]["api_key"] == "$secrets.prod.openai"
                assert "variables" in body["agent"]
            return httpx.Response(201, json={"agent_session_id": "new-session-id", "status": "running", "created_at": "unspecified"})
        assert path.endswith("/sessions/new-session-id" + ("/stop" if request.method == "POST" else ""))
        if request.method == "POST":
            assert request.content == b""
            return httpx.Response(200, json={})
        return httpx.Response(200, json={"agent_session_id": "new-session-id", "status": "RUNNING", "start_ts": 1})
    client = make_client(handler, async_)
    if stored:
        cls = AsyncSavedAgent if async_ else SavedAgent
        owner = cls(client, RawResponse(data={"agent_id": "stored-id", "agent_name": "Support"}, headers=httpx.Headers(), status_code=200, response=httpx.Response(200)))
    else:
        owner = configured(client).with_variable("customer", type="str")
    remote = ["2"]
    kwargs = dict(channel="room", agent_uid="1", remote_uids=remote, name="reference", idle_timeout=1.5, max_duration=120)
    if stored:
        kwargs["labels"] = {"owner": "test"}
    session = (owner.create_async_session(**kwargs) if async_ and not stored else owner.create_session(**kwargs))
    remote.append("mutation")
    assert session.raw is client.v3.sessions
    assert session.raw_agent_management is None
    if async_:
        assert await session.start() == "new-session-id"
        assert (await session.get_info())["status"] == "RUNNING"
        with pytest.raises(NotImplementedError):
            await session.say("No unsupported controls")
        await session.stop()
    else:
        assert session.start() == "new-session-id"
        assert session.get_info()["status"] == "RUNNING"
        with pytest.raises(NotImplementedError):
            session.say("No unsupported controls")
        session.stop()
    assert session.status == "stopped"
    assert len(calls) == 3


@pytest.mark.parametrize("option,value", [("preset", "test"), ("pipeline_id", "id"), ("expires_in", 60), ("enable_string_uid", False), ("client_reference", "removed")])
def test_ephemeral_rejects_undocumented_options(option, value):
    agent = configured(make_client(lambda _: pytest.fail("must not send")))
    with pytest.raises(ValueError):
        agent.create_session(channel="room", agent_uid="1", remote_uids=["*"], **{option: value})


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_new_session_stop_404_propagates_and_controls_never_request(async_):
    calls = []
    def handler(request):
        calls.append(request)
        if request.url.path.endswith("/stop"):
            return httpx.Response(404, json={"reason": "TaskNotFound"})
        return httpx.Response(201, json={"agent_session_id": "new", "status": "running", "created_at": 1})
    agent = configured(make_client(handler, async_))
    session = (agent.create_async_session if async_ else agent.create_session)(channel="room", agent_uid="1", remote_uids=["2"])
    if async_:
        await session.start()
    else:
        session.start()
    for method, args in (("interrupt", ()), ("think", ("test",)), ("get_history", ()), ("get_turns", ()), ("get_all_turns", ())):
        with pytest.raises(NotImplementedError):
            result = getattr(session, method)(*args)
            if async_:
                await result
    from agora_agent.core.api_error import ApiError
    with pytest.raises(ApiError, match="TaskNotFound"):
        if async_:
            await session.stop()
        else:
            session.stop()
    assert session.status == "error"
    assert len(calls) == 2


@pytest.mark.parametrize("seconds", [-1, float("nan"), float("inf"), True, 0.00001])
def test_new_session_duration_rejects_invalid_precision(seconds):
    with pytest.raises(ValueError):
        configured(make_client(lambda _: pytest.fail("must not send"))).create_session(channel="r", agent_uid="1", remote_uids=["2"], max_duration=seconds)


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_new_session_stop_does_not_hide_unrelated_404(async_):
    def handler(request):
        if request.url.path.endswith("/stop"):
            return httpx.Response(404, json={"reason": "ProjectNotFound"})
        return httpx.Response(201, json={"agent_session_id": "new", "status": "running", "created_at": 1})
    agent = configured(make_client(handler, async_))
    session = (agent.create_async_session if async_ else agent.create_session)(channel="r", agent_uid="1", remote_uids=["2"])
    if async_:
        await session.start()
        with pytest.raises(Exception) as caught:
            await session.stop()
    else:
        session.start()
        with pytest.raises(Exception) as caught:
            session.stop()
    assert caught.value.status_code == 404
    assert session.status == "error"


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.parametrize("stored", [False, True])
def test_preview_does_not_hardcode_rollout_regions(async_, stored):
    from agora_agent import AsyncSavedAgent, SavedAgent
    from agora_agent.v3 import RawResponse
    client = make_client(lambda _: pytest.fail("must not send"), async_)
    client._area = Area.CN
    owner = ((AsyncSavedAgent if async_ else SavedAgent)(client, RawResponse(data={"agent_id": "id", "agent_name": "name"}, headers=httpx.Headers(), status_code=200, response=httpx.Response(200))) if stored else configured(client))
    method = owner.create_async_session if async_ and not stored else owner.create_session
    session = method(channel="r", agent_uid="1", remote_uids=["2"])
    assert session.status == "idle"


def test_new_sessions_reference_precedence_and_whitespace_uids():
    from agora_agent.agentkit.session_backend import create_session
    agent = configured(make_client(lambda _: pytest.fail("must not send")))
    session = create_session(agent, channel="r", agent_uid="1", remote_uids=["2"], name="fallback")
    assert "client_reference" not in session._session_backend["body"]
    with pytest.raises(ValueError, match="remote_uids"):
        create_session(agent, channel="r", agent_uid="1", remote_uids=[" "])


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.parametrize("status,http_status,timestamp", [("STARTING", 200, "create_ts"), ("running", 201, "created_at")])
@pytest.mark.asyncio
async def test_corrected_sessions_supported_fields_and_rollout(async_, status, http_status, timestamp):
    calls = []
    def handler(request):
        calls.append(request)
        if request.url.path.endswith("/stop"):
            assert request.content == b""
            return httpx.Response(200, json={})
        if request.method == "GET":
            return httpx.Response(200, json={"agent_session_id": "s", "status": "FAILED", "start_ts": 1})
        body = json.loads(request.content)
        assert "client_reference" not in body
        assert body["values"] == {"customer": "Ada"}
        assert body["labels"] == {"team": "support"}
        assert body["data_policy"] == {"retention": "none"}
        assert body["transport"]["token"] == "rtc-only"
        assert body["transport"]["audio_scenario"] == "chorus"
        assert body["transport"]["encryption"] == {"mode": "aes_128_gcm", "key": "secret"}
        assert body["lifecycle"]["graceful_stop"] == {"enabled": True, "timeout_ms": 10000}
        assert request.headers["Idempotency-Key"] == "session-key"
        assert "rtc-only" not in request.headers["Authorization"]
        return httpx.Response(http_status, json={"agent_session_id": "s", "status": status, timestamp: 1}, headers={"Idempotent-Replayed": "true"})
    client = make_client(handler, async_)
    agent = configured(client)
    method = agent.create_async_session if async_ else agent.create_session
    session = method(channel="room", agent_uid="bot", remote_uids=["customer"], values={"customer": "Ada"}, labels={"team": "support"}, token="rtc-only", encryption={"mode": "aes_128_gcm", "key": "secret"}, audio_scenario="chorus", graceful_stop={"enabled": True, "timeout_ms": 10000}, data_policy={"retention": "none"}, idempotency_key="session-key")
    if async_:
        await session.start()
        assert session.status == status.lower()
        await session.stop()
        assert (await session.get_info())["status"] == "FAILED"
    else:
        session.start()
        assert session.status == status.lower()
        session.stop()
        assert session.get_info()["status"] == "FAILED"
    assert session.status == "error"


def test_sync_session_info_cannot_overwrite_a_later_stop():
    entered = threading.Event()
    release = threading.Event()
    def handler(request):
        if request.method == "GET":
            entered.set()
            assert release.wait(3)
            return httpx.Response(200, json={"agent_session_id": "s", "status": "RUNNING"})
        if request.url.path.endswith("/stop"):
            return httpx.Response(200, json={})
        return httpx.Response(200, json={"agent_session_id": "s", "create_ts": 1, "status": "RUNNING"})
    session = configured(make_client(handler)).create_session(channel="r", agent_uid="1", remote_uids=["2"], max_duration=1)
    session.start()
    thread = threading.Thread(target=session.get_info)
    thread.start()
    assert entered.wait(3)
    session.stop()
    release.set()
    thread.join(3)
    assert not thread.is_alive()
    assert session.status == "stopped"


@pytest.mark.asyncio
async def test_async_session_info_cannot_overwrite_a_later_stop():
    entered = asyncio.Event()
    release = asyncio.Event()
    async def handler(request):
        if request.method == "GET":
            entered.set()
            await asyncio.wait_for(release.wait(), timeout=3)
            return httpx.Response(200, json={"agent_session_id": "s", "status": "RUNNING"})
        if request.url.path.endswith("/stop"):
            return httpx.Response(200, json={})
        return httpx.Response(200, json={"agent_session_id": "s", "create_ts": 1, "status": "RUNNING"})
    session = configured(make_client(handler, True)).create_async_session(channel="r", agent_uid="1", remote_uids=["2"], max_duration=1)
    await session.start()
    pending = asyncio.create_task(session.get_info())
    await asyncio.wait_for(entered.wait(), timeout=3)
    await session.stop()
    release.set()
    await pending
    assert session.status == "stopped"


@pytest.mark.asyncio
async def test_async_session_restart_does_not_expose_previous_id_while_starting():
    entered = asyncio.Event()
    release = asyncio.Event()
    starts = 0
    stopped_ids = []
    async def handler(request):
        nonlocal starts
        if request.url.path.endswith("/stop"):
            stopped_ids.append(request.url.path.split("/")[-2])
            return httpx.Response(200, json={})
        starts += 1
        if starts == 2:
            entered.set()
            await asyncio.wait_for(release.wait(), timeout=3)
        return httpx.Response(200, json={"agent_session_id": f"s{starts}", "create_ts": starts, "status": "RUNNING"})
    session = configured(make_client(handler, True)).create_async_session(channel="r", agent_uid="1", remote_uids=["2"], max_duration=1)
    assert await session.start() == "s1"
    await session.stop()
    restart = asyncio.create_task(session.start())
    await asyncio.wait_for(entered.wait(), timeout=3)
    assert session.id is None
    with pytest.raises(RuntimeError, match="starting"):
        await session.stop()
    release.set()
    assert await restart == "s2"
    await session.stop()
    assert stopped_ids == ["s1", "s2"]


@pytest.mark.asyncio
async def test_async_session_info_uses_newest_issued_read():
    first_entered = asyncio.Event()
    release_first = asyncio.Event()
    gets = 0
    async def handler(request):
        nonlocal gets
        if request.method == "GET":
            gets += 1
            if gets == 1:
                first_entered.set()
                await asyncio.wait_for(release_first.wait(), timeout=3)
                return httpx.Response(200, json={"agent_session_id": "s", "status": "RUNNING"})
            return httpx.Response(200, json={"agent_session_id": "s", "status": "STOPPED"})
        return httpx.Response(200, json={"agent_session_id": "s", "create_ts": 1, "status": "RUNNING"})
    session = configured(make_client(handler, True)).create_async_session(channel="r", agent_uid="1", remote_uids=["2"], max_duration=1)
    await session.start()
    older = asyncio.create_task(session.get_info())
    await asyncio.wait_for(first_entered.wait(), timeout=3)
    await session.get_info()
    assert session.status == "stopped"
    release_first.set()
    await older
    assert session.status == "stopped"


@pytest.mark.asyncio
async def test_async_session_get_info_during_stop_cannot_restore_running():
    stop_entered = asyncio.Event()
    release_stop = asyncio.Event()
    async def handler(request):
        if request.url.path.endswith("/stop"):
            stop_entered.set()
            await asyncio.wait_for(release_stop.wait(), timeout=3)
            return httpx.Response(200, json={})
        if request.method == "GET":
            return httpx.Response(200, json={"agent_session_id": "s", "status": "RUNNING"})
        return httpx.Response(200, json={"agent_session_id": "s", "create_ts": 1, "status": "RUNNING"})
    session = configured(make_client(handler, True)).create_async_session(channel="r", agent_uid="1", remote_uids=["2"], max_duration=1)
    await session.start()
    stopping = asyncio.create_task(session.stop())
    await asyncio.wait_for(stop_entered.wait(), timeout=3)
    await session.get_info()
    assert session.status == "stopping"
    release_stop.set()
    await stopping
    assert session.status == "stopped"


@pytest.mark.asyncio
async def test_async_stop_cancellation_clears_transition_and_allows_refresh():
    stop_entered = asyncio.Event()
    async def handler(request):
        if request.url.path.endswith("/stop"):
            stop_entered.set()
            await asyncio.Event().wait()
        if request.method == "GET":
            return httpx.Response(200, json={"agent_session_id": "s", "status": "STOPPED"})
        return httpx.Response(200, json={"agent_session_id": "s", "create_ts": 1, "status": "RUNNING"})
    session = configured(make_client(handler, True)).create_async_session(channel="r", agent_uid="1", remote_uids=["2"], max_duration=1)
    await session.start()
    stopping = asyncio.create_task(session.stop())
    await asyncio.wait_for(stop_entered.wait(), timeout=3)
    stopping.cancel()
    with pytest.raises(asyncio.CancelledError):
        await stopping
    assert session.status == "error"
    assert await session.get_info() == {"agent_session_id": "s", "status": "STOPPED"}
    assert session.status == "stopped"


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.parametrize("reason,expected", [("TaskNotRunning", "stopped"), ("TaskConflict", "stopping"), ("Other", "error")])
@pytest.mark.asyncio
async def test_new_stop_conflict_distinctions(async_, reason, expected):
    from agora_agent.core.api_error import ApiError
    def handler(request):
        return httpx.Response(409, json={"reason": reason}) if request.url.path.endswith("/stop") else httpx.Response(200, json={"agent_session_id": "s", "create_ts": 1, "status": "STARTING"})
    agent = configured(make_client(handler, async_))
    session = (agent.create_async_session if async_ else agent.create_session)(channel="r", agent_uid="1", remote_uids=["2"])
    if async_:
        await session.start()
        with pytest.raises(ApiError):
            await session.stop()
    else:
        session.start()
        with pytest.raises(ApiError):
            session.stop()
    assert session.status == expected


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_session_can_refresh_after_stop_conflict_finishes(async_):
    calls = []
    def handler(request):
        calls.append(request)
        if request.url.path.endswith("/stop"):
            return httpx.Response(409, json={"reason": "TaskConflict"})
        if request.method == "POST":
            return httpx.Response(200, json={"agent_session_id": "s", "status": "RUNNING", "create_ts": 1})
        return httpx.Response(200, json={"agent_session_id": "s", "status": "STOPPED", "create_ts": 1})
    agent = configured(make_client(handler, async_))
    session = (agent.create_async_session if async_ else agent.create_session)(channel="r", agent_uid="1", remote_uids=["2"])
    if async_:
        await session.start()
        with pytest.raises(Exception):
            await session.stop()
        assert session.status == "stopping"
        await session.get_info()
    else:
        session.start()
        with pytest.raises(Exception):
            session.stop()
        assert session.status == "stopping"
        session.get_info()
    assert session.status == "stopped"
    assert len(calls) == 3


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_default_public_origin_and_signed_token(async_):
    calls = []
    http = (httpx.AsyncClient if async_ else httpx.Client)(transport=httpx.MockTransport(lambda r: calls.append(r) or httpx.Response(200, json={})))
    client = (AsyncAgora if async_ else Agora)(area=Area.US, app_id="0" * 32, app_certificate="1" * 32, httpx_client=http)
    result = client.v3.agents.list()
    if async_:
        await result
    assert calls[0].url.host == "preview.ai.agora.io"
    assert calls[0].url.path.startswith("/conversational-ai/v1/projects/")
    assert calls[0].headers["Authorization"].startswith("agora token=")


@pytest.mark.parametrize("field", ["customer_id", "customer_secret", "client_id", "client_secret", "customerId", "customerSecret", "clientId", "clientSecret", "username", "password"])
def test_removed_basic_credentials_rejected_every_entrypoint(field):
    for cls in (Agora, AsyncAgora):
        with pytest.raises(TypeError):
            cls(area=Area.US, app_id="p", app_certificate="c", **{field: "stale"})
    client = make_client(lambda _: pytest.fail("must not send"))
    with pytest.raises(ValueError, match="Basic"):
        client.v3.agents.list(request_options={field: "stale"})


@pytest.mark.parametrize("header,value", [("Authorization", "Basic stale"), ("X-Studio-Region", "us"), ("X-Studio-V2-Gateway-Secret", "secret"), ("X-Consumer-Username", "user")])
def test_forbidden_headers_rejected_in_all_new_transport_layers(header, value):
    for location in ("base", "v3", "request"):
        client = make_client(lambda _: pytest.fail("must not send"))
        options = {}
        if location == "base":
            client._client_wrapper._headers = {header: value}
            # Authorization normally overwrites custom headers; inspect custom values too.
        elif location == "v3":
            client._v3_options = V3Options(headers={header: value})
        else:
            options = {"additional_headers": {header: value}}
        with pytest.raises(ValueError):
            client.v3.agents.list(request_options=options)


def test_blank_authorization_overrides_rejected_before_request():
    with pytest.raises(ValueError):
        Agora(area=Area.US, app_id="project", app_certificate="cert", auth_token="token", headers={"Authorization": ""})
    for location in ("v3", "request"):
        client = make_client(lambda _: pytest.fail("must not send"))
        if location == "v3":
            client._v3_options = V3Options(headers={"Authorization": ""})
            options = {}
        else:
            options = {"additional_headers": {"Authorization": ""}}
        with pytest.raises(ValueError):
            client.v3.agents.list(request_options=options)
    from agora_agent.client import Agora as GeneratedAgora
    raw = GeneratedAgora(authorization="", httpx_client=httpx.Client(transport=httpx.MockTransport(lambda _: pytest.fail("must not send"))))
    with pytest.raises(ValueError):
        raw.agents.get("project", "agent")
    sent = []
    raw = GeneratedAgora(authorization="", httpx_client=httpx.Client(transport=httpx.MockTransport(lambda request: sent.append(request) or httpx.Response(200, json={}))))
    raw.agents.get("project", "agent", request_options={"additional_headers": {"authorization": "agora token=override"}})
    assert sent[0].headers.get_list("authorization") == ["agora token=override"]


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_generated_client_requires_effective_token_before_http(async_):
    from agora_agent.client import Agora as GeneratedAgora
    from agora_agent.client import AsyncAgora as GeneratedAsyncAgora

    http = (httpx.AsyncClient if async_ else httpx.Client)(
        transport=httpx.MockTransport(lambda _: pytest.fail("must not send"))
    )
    raw = (GeneratedAsyncAgora if async_ else GeneratedAgora)(authorization=None, httpx_client=http)
    with pytest.raises(ValueError, match="authorization is required"):
        result = raw.agents.get("project", "agent")
        if async_:
            await result
    if async_:
        await http.aclose()
    else:
        http.close()


@pytest.mark.parametrize("resource,kwargs", [("secrets", {"name": "s", "secrets": {"k": "v"}}), ("numbers", {"number": "+12025550123", "sip_trunk": {"hostname": "sip.example"}})])
def test_unsupported_provisioning_idempotency_rejected(resource, kwargs):
    method = getattr(make_client(lambda _: pytest.fail("must not send")).v3, resource).create
    with pytest.raises(TypeError):
        method(**kwargs, idempotency_key="old")
    with pytest.raises(ValueError):
        method(**kwargs, request_options={"additional_headers": {"Idempotency-Key": "old"}})


def test_managed_endpoints_removed_byok_preserved_and_supported_avatar():
    managed = module({"vendor": "openai", "url": "https://old", "params": {"url": "https://old", "base_url": "https://old"}}, "llm", [])
    assert "url" not in managed and "params" not in managed
    byok = module({"vendor": "openai", "api_key": "key", "url": "https://byok"}, "llm", [])
    assert byok["url"] == "https://byok"
    for vendor in ("sensetime", "spatius"):
        errors = []
        assert module({"vendor": vendor, "enable": True, "params": {}}, "avatar", errors)["vendor"] == vendor
        assert not errors


def test_builder_retention_farewell_mapping_uses_session_envelope():
    session = configured(make_client(lambda _: pytest.fail("must not send"))).with_parameters({"opt_out": True, "farewell_config": {"graceful_enabled": True, "graceful_timeout_seconds": 10}}).create_session(channel="r", agent_uid="1", remote_uids=["2"])
    body = session._session_backend["body"]
    assert body["data_policy"] == {"retention": "none"}
    assert body["lifecycle"]["graceful_stop"] == {"enabled": True, "timeout_ms": 10000}
    assert "data_policy" not in body["agent"]


def test_builder_labels_map_to_new_session_labels():
    agent = configured(make_client(lambda _: pytest.fail("must not send"))).with_labels({"team": "support"}).with_variable("customer", type="str")
    session = agent.create_session(channel="r", agent_uid="1", remote_uids=["2"])
    assert session._session_backend["body"]["labels"] == {"team": "support"}
    assert "labels" not in session._session_backend["body"]["agent"]


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.parametrize("override", ["header", "basic_client", "credentials"])
@pytest.mark.asyncio
async def test_legacy_resource_token_policy_at_http_boundary(async_, override):
    http = (httpx.AsyncClient if async_ else httpx.Client)(transport=httpx.MockTransport(lambda _: pytest.fail("must not send")), **({"auth": httpx.BasicAuth("id", "secret")} if override == "basic_client" else {}))
    client = (AsyncAgora if async_ else Agora)(area=Area.US, app_id="p", app_certificate="c", auth_token="token", httpx_client=http)
    options = {"additional_headers": {"authorization": "Basic stale"}} if override == "header" else {"clientSecret": "old"} if override == "credentials" else {}
    with pytest.raises(ValueError):
        result = client.agents.get("p", "legacy-id", request_options=options)
        if async_:
            await result


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_campaign_pages_and_conditional_reload(async_):
    calls = []
    def handler(request):
        calls.append(request)
        if request.method == "PATCH":
            return httpx.Response(412, json={"reason": "PreconditionFailed"}, headers={"ETag": '"fresh"'})
        if request.url.path.endswith("/campaigns/c"):
            assert "If-Match" not in request.headers
            return httpx.Response(200, json={"campaign_id": "c", "name": "Fresh"})
        second = request.url.params.get("cursor") == "next"
        return httpx.Response(200, json={"data": {"list": [{"campaign_id": "b" if second else "a"}]}, "has_more": not second, "next_cursor": None if second else "next"})
    client = make_client(handler, async_)
    assert client.campaigns is client.v3.campaigns
    if async_:
        assert [item["campaign_id"] async for item in client.campaigns.iter_all(limit=1)] == ["a", "b"]
        with pytest.raises(PreconditionFailedError) as caught:
            await client.campaigns.update(campaign_id="c", if_match='"old"', pacing={"max_concurrent": 2})
        assert (await caught.value.latest())["name"] == "Fresh"
    else:
        assert [item["campaign_id"] for item in client.campaigns.iter_all(limit=1)] == ["a", "b"]
        with pytest.raises(PreconditionFailedError) as caught:
            client.campaigns.update(campaign_id="c", if_match='"old"', pacing={"max_concurrent": 2})
        assert caught.value.latest()["name"] == "Fresh"
    assert len(calls) == 4


@pytest.mark.parametrize("extra", [{"remote_uids": ["*"]}, {"remote_uids": ["2", "3"]}, {"remote_uids": []}, {"remote_uids": ["name"]}, {"max_duration": 0}, {"idle_timeout": 3601}, {"graceful_stop": {"timeout_ms": 120001}}, {"data_policy": {"retention": "forever"}}, {"encryption": {"mode": "bad", "key": "key"}}])
def test_session_schema_limits_reject_before_network(extra):
    options = {"channel": "r", "agent_uid": "1", "remote_uids": ["2"], **extra}
    with pytest.raises(ValueError):
        configured(make_client(lambda _: pytest.fail("must not send"))).create_session(**options)


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_session_raw_rollout_normalizes_data_preserves_http_and_replay(async_):
    client = make_client(lambda _: httpx.Response(201, json={"agent_session_id": "s", "created_at": 42, "status": "starting"}, headers={"Idempotent-Replayed": "true"}), async_)
    result = client.v3.sessions.with_raw_response.start(agent_id="a", transport={"type": "rtc", "channel": "r", "uid": "1", "subscribe_uids": ["2"]}, idempotency_key="same")
    raw = await result if async_ else result
    assert raw.data == {"agent_session_id": "s", "create_ts": 42, "status": "STARTING"}
    assert raw.status_code == 201
    assert raw.response.json()["created_at"] == 42
    assert raw.headers["Idempotent-Replayed"] == "true"


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_successful_idempotent_handle_requires_new_handle_for_restart(async_):
    calls = []
    def handler(request):
        calls.append(request)
        return httpx.Response(200, json={} if request.url.path.endswith("/stop") else {"agent_session_id": "s", "create_ts": 1, "status": "RUNNING"})
    agent = configured(make_client(handler, async_))
    session = (agent.create_async_session if async_ else agent.create_session)(channel="r", agent_uid="1", remote_uids=["2"], idempotency_key="one-session")
    if async_:
        await session.start()
        await session.stop()
        with pytest.raises(RuntimeError, match="new session handle"):
            await session.start()
    else:
        session.start()
        session.stop()
        with pytest.raises(RuntimeError, match="new session handle"):
            session.start()
    assert len(calls) == 2


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_unknown_start_can_retry_original_idempotency_key(async_):
    calls = []
    def handler(request):
        calls.append(request)
        assert request.headers["Idempotency-Key"] == "original"
        return httpx.Response(503, json={"reason": "Busy"}) if len(calls) == 1 else httpx.Response(200, json={"agent_session_id": "s", "create_ts": 1, "status": "STARTING"})
    agent = configured(make_client(handler, async_))
    session = (agent.create_async_session if async_ else agent.create_session)(channel="r", agent_uid="1", remote_uids=["2"], idempotency_key="original")
    if async_:
        with pytest.raises(Exception):
            await session.start()
        assert await session.start() == "s"
    else:
        with pytest.raises(Exception):
            session.start()
        assert session.start() == "s"
    assert len(calls) == 2


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.parametrize("ephemeral", [False, True])
@pytest.mark.asyncio
async def test_lowlevel_telephony_session_transport_union(async_, ephemeral):
    calls = []
    source = "7b1e4c2d-5a6f-4e8b-9c0d-1f2a3b4c5d6e"
    transport = {"type": "telephony", "from": source, "to": "+16505550188", "call_policy": {"max_ring_duration_ms": 30000, "max_call_duration_seconds": 900, "max_silence_duration_ms": 5000, "voicemail": {"mode": "hangup"}, "end_call": {"on_user_request": True}, "transfer": {"phone_number": "+12025550123", "description": "Talk to a person"}}}
    def handler(request):
        calls.append(request)
        assert json.loads(request.content)["transport"] == transport
        assert request.headers["Idempotency-Key"] == "call-1"
        return httpx.Response(200, json={"agent_session_id": "phone-session", "create_ts": 1, "status": "STARTING"})
    client = make_client(handler, async_)
    method = client.v3.sessions.start_ephemeral if ephemeral else client.v3.sessions.start
    result = method(**({"agent": {"instructions": "Help"}} if ephemeral else {"agent_id": "saved"}), transport=transport, idempotency_key="call-1")
    response = await result if async_ else result
    assert response["agent_session_id"] == "phone-session"
    assert len(calls) == 1


@pytest.mark.parametrize("transport", [{"type": "telephony", "from": "+16505550188", "to": "+12025550123"}, {"type": "telephony", "from": "7b1e4c2d-5a6f-4e8b-9c0d-1f2a3b4c5d6e", "to": "national"}, {"type": "telephony", "from": "7b1e4c2d-5a6f-4e8b-9c0d-1f2a3b4c5d6e", "to": "+12025550123", "call_policy": {"max_ring_duration_ms": 0}}])
def test_lowlevel_telephony_rejects_invalid_source_destination_and_policy(transport):
    client = make_client(lambda _: pytest.fail("must not send"))
    with pytest.raises(ValueError):
        client.v3.sessions.start(agent_id="a", transport=transport)


@pytest.mark.parametrize("vendor", ["sensetime", "spatius"])
@pytest.mark.parametrize("reference", [False, True])
def test_public_avatar_vendor_keys_use_write_only_credential_envelope(vendor, reference):
    import copy

    from agora_agent.agentkit.vendors.cn import SenseTimeAvatar, SpatiusAvatar
    calls = []
    key = secret_ref("avatars", vendor) if reference else "inline-avatar-key"
    avatar = (SenseTimeAvatar(agora_uid="3", app_id="app", app_key=key) if vendor == "sensetime" else SpatiusAvatar(agora_uid="3", spatius_app_id="app", spatius_avatar_id="avatar", spatius_api_key=key))
    def handler(request):
        calls.append(request)
        return httpx.Response(201, json={"agent_id": "a", "agent_name": "Avatar"}, headers={"ETag": '"1"'})
    agent = configured(make_client(handler)).with_avatar(avatar)
    before = copy.deepcopy(agent.config)
    if reference:
        agent.save(name="Avatar")
        body = json.loads(calls[0].content)["pipeline"]["avatar"]
    else:
        with pytest.raises(ValueError, match="secret_ref"):
            agent.save(name="Avatar")
        assert not calls
        body = build_body(agent)["pipeline"]["avatar"]
    assert body["vendor"] == vendor
    assert body["credential"] == {"mode": "byok", "fields": {"app_key" if vendor == "sensetime" else "spatius_api_key": key}}
    assert "app_key" not in body.get("params", {})
    assert "spatius_api_key" not in body.get("params", {})
    assert body["params"]["agora_uid"] == "3"
    assert agent.config == before


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.parametrize("origin", ["https://customer:secret@preview.ai.agora.io", "https://preview.ai.agora.io?", "https://preview.ai.agora.io#"])
@pytest.mark.asyncio
async def test_public_origin_rejects_embedded_credentials(async_, origin):
    client = make_client(lambda _: pytest.fail("must not send"), async_)
    client._v3_options = V3Options(base_url=origin)
    with pytest.raises(ValueError, match="origin"):
        result = client.v3.agents.list()
        if async_:
            await result


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_advertised_app_credentials_sign_raw_legacy_reads_each_call(async_, monkeypatch):
    calls = []
    tokens = []
    def sign(**kwargs):
        assert kwargs["app_id"] == "app" and kwargs["app_certificate"] == "certificate"
        token = "fresh-" + str(len(tokens))
        tokens.append(token)
        return token
    monkeypatch.setattr("agora_agent.pool_client.generate_convo_ai_token", sign)
    http = (httpx.AsyncClient if async_ else httpx.Client)(transport=httpx.MockTransport(lambda r: calls.append(r) or httpx.Response(200, json={"agent_id": "legacy", "status": "RUNNING"})))
    client = (AsyncAgora if async_ else Agora)(area=Area.US, app_id="app", app_certificate="certificate", httpx_client=http)
    for _ in range(2):
        result = client.agents.get("app", "legacy")
        if async_:
            await result
    assert len(calls) == 2
    assert all(r.headers["Authorization"].startswith("agora token=fresh-") for r in calls)
    assert calls[0].headers["Authorization"] != calls[1].headers["Authorization"]


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.parametrize("extra", [False, True])
@pytest.mark.asyncio
async def test_new_session_geofence_maps_builder_or_explicit_option(async_, extra):
    calls = []
    client = make_client(lambda r: calls.append(r) or httpx.Response(200, json={"agent_session_id": "s", "create_ts": 1, "status": "RUNNING"}), async_)
    agent = configured(client).with_geofence({"area": "GLOBAL", "exclude_area": "INDIA"})
    method = agent.create_async_session if async_ else agent.create_session
    session = method(channel="r", agent_uid="1", remote_uids=["2"], **({"geofence": {"area": "europe"}} if extra else {}))
    if async_:
        await session.start()
    else:
        session.start()
    body = json.loads(calls[0].content)
    assert body["transport"]["geofence"] == ({"area": "europe"} if extra else {"area": "global", "exclude_area": "india"})
    assert "geofence" not in body["agent"]
    assert agent.config["geofence"] == {"area": "GLOBAL", "exclude_area": "INDIA"}


@pytest.mark.parametrize("fence", [{"area": "invalid"}, {"area": "europe", "exclude_area": "india"}, {"area": "global", "exclude_area": "global"}])
def test_new_session_geofence_invalid_combinations_reject_locally(fence):
    with pytest.raises(ValueError, match="geofence"):
        configured(make_client(lambda _: pytest.fail("must not send"))).create_session(channel="r", agent_uid="1", remote_uids=["2"], geofence=fence)


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_duplicate_authorization_values_never_allow_hidden_basic(async_):
    client = make_client(lambda _: pytest.fail("must not send"), async_)
    headers = httpx.Headers([("Authorization", "agora token=valid"), ("Authorization", "Basic hidden")])
    for resource in (client.v3.agents, client.agents):
        with pytest.raises(ValueError, match="token"):
            result = (resource.get(agent_id="a", request_options={"additional_headers": headers}) if resource is client.v3.agents else resource.get("p", "legacy", request_options={"additional_headers": headers}))
            if async_:
                await result


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_prebuilt_rest_token_needs_no_app_certificate(async_):
    calls = []
    http = (httpx.AsyncClient if async_ else httpx.Client)(transport=httpx.MockTransport(lambda r: calls.append(r) or httpx.Response(200, json={"agent_id": "legacy", "status": "RUNNING"})))
    client = (AsyncAgora if async_ else Agora)(area=Area.US, app_id="project", auth_token="existing-token", httpx_client=http)
    result = client.agents.get("project", "legacy")
    if async_:
        await result
    result = client.v3.agents.list()
    if async_:
        await result
    assert len(calls) == 2
    assert all(r.headers["Authorization"] == "agora token=existing-token" for r in calls)
    assert client.app_certificate is None


@pytest.mark.parametrize("cls", [Agora, AsyncAgora])
@pytest.mark.parametrize("options", [{}, {"auth_token": ""}, {"auth_token": " "}, {"app_certificate": ""}])
def test_client_requires_nonempty_token_or_signing_credentials(cls, options):
    with pytest.raises(ValueError):
        cls(area=Area.US, app_id="project", **options)


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_duplicate_auth_in_resource_header_overrides_is_rejected(async_):
    client = make_client(lambda _: pytest.fail("must not send"), async_)
    client._v3_options = V3Options(headers=httpx.Headers([("Authorization", "agora token=good"), ("Authorization", "Basic hidden")]))
    with pytest.raises(ValueError, match="token"):
        result = client.v3.agents.list()
        if async_:
            await result


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_latest_strips_global_and_http_client_write_conditions_without_mutation(async_):
    calls = []
    defaults = httpx.Headers({"If-Match": "http-default", "If-None-Match": "*", "Idempotency-Key": "http-key", "X-HTTP-Context": "kept"})
    def handler(request):
        calls.append(request)
        if request.method == "PATCH":
            return httpx.Response(412, json={"reason": "PreconditionFailed"})
        assert all(name not in request.headers for name in ("If-Match", "If-None-Match", "Idempotency-Key"))
        assert request.headers["X-HTTP-Context"] == "kept"
        assert request.headers["X-SDK-Context"] == "kept"
        assert request.headers["X-V3-Context"] == "kept"
        return httpx.Response(200, json={"agent_id": "a", "agent_name": "Latest"})
    http = (httpx.AsyncClient if async_ else httpx.Client)(headers=defaults, transport=httpx.MockTransport(handler))
    client = (AsyncAgora if async_ else Agora)(area=Area.US, app_id="p", auth_token="token", httpx_client=http, headers={"If-Match": "sdk-default", "X-SDK-Context": "kept"}, v3=V3Options(headers={"If-None-Match": "v3-default", "X-V3-Context": "kept"}))
    with pytest.raises(PreconditionFailedError) as caught:
        result = client.v3.agents.update(agent_id="a", if_match="explicit", instructions="next")
        if async_:
            await result
    latest = await caught.value.latest() if async_ else caught.value.latest()
    assert latest["agent_name"] == "Latest"
    assert len(calls) == 2
    assert http.headers["If-Match"] == "http-default"
    assert client._client_wrapper.get_custom_headers()["If-Match"] == "sdk-default"
    assert client._v3_options.headers["If-None-Match"] == "v3-default"


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.parametrize("payload", ["plain conflict", ["unexpected", "array"]])
@pytest.mark.asyncio
async def test_stop_preserves_nonobject_409_api_error(async_, payload):
    from agora_agent.core.api_error import ApiError
    def handler(request):
        if request.url.path.endswith("/stop"):
            return httpx.Response(409, text=payload) if isinstance(payload, str) else httpx.Response(409, json=payload)
        return httpx.Response(200, json={"agent_session_id": "s", "status": "RUNNING", "create_ts": 1})
    agent = configured(make_client(handler, async_))
    session = (agent.create_async_session if async_ else agent.create_session)(channel="r", agent_uid="1", remote_uids=["2"])
    if async_:
        await session.start()
        with pytest.raises(ApiError) as caught:
            await session.stop()
    else:
        session.start()
        with pytest.raises(ApiError) as caught:
            session.stop()
    assert caught.value.status_code == 409
    assert caught.value.body == payload
    assert session.status == "error"


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.parametrize("agent_uid", ["0", "1"])
@pytest.mark.parametrize("subscriber_uid", ["0", "00", "000"])
@pytest.mark.asyncio
async def test_subscriber_zero_rejected_even_when_agent_zero_is_allowed(async_, agent_uid, subscriber_uid):
    client = make_client(lambda _: pytest.fail("must not send"), async_)
    with pytest.raises(ValueError, match="subscribe_uids"):
        result = client.v3.sessions.start(agent_id="a", transport={"type": "rtc", "channel": "r", "uid": agent_uid, "subscribe_uids": [subscriber_uid]})
        if async_:
            await result


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.parametrize("key", ["", " ", "\t"])
@pytest.mark.parametrize("resource,method,kwargs", [
    ("sessions", "start", {"agent_id": "a", "transport": {"type": "rtc", "channel": "r", "uid": "1", "subscribe_uids": ["2"]}}),
    ("sessions", "start_ephemeral", {"agent": {"instructions": "Help"}, "transport": {"type": "rtc", "channel": "r", "uid": "1", "subscribe_uids": ["2"]}}),
    ("campaigns", "create", {"name": "Campaign", "agent_id": "a", "transport": {"type": "telephony", "from": ["n"]}, "contacts": [{"phone": "+12025550123"}], "schedule": {"mode": "immediate"}}),
    ("campaigns", "pause", {"campaign_id": "c"}),
    ("campaigns", "resume", {"campaign_id": "c"}),
    ("campaigns", "cancel", {"campaign_id": "c"}),
])
@pytest.mark.asyncio
async def test_explicit_blank_idempotency_key_rejected_before_http(async_, key, resource, method, kwargs):
    client = make_client(lambda _: pytest.fail("must not send"), async_)
    with pytest.raises(ValueError, match="Idempotency-Key"):
        result = getattr(getattr(client.v3, resource), method)(**kwargs, idempotency_key=key)
        if async_:
            await result


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.parametrize("key", ["", " ", "\t"])
def test_agentkit_blank_idempotency_key_rejected_on_local_creation(async_, key):
    agent = configured(make_client(lambda _: pytest.fail("must not send"), async_))
    with pytest.raises(ValueError, match="Idempotency-Key"):
        (agent.create_async_session if async_ else agent.create_session)(channel="r", agent_uid="1", remote_uids=["2"], idempotency_key=key)
