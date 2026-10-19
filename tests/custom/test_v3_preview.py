"""Offline contract tests for the additive v3 preview and v2 boundary."""
import json

import httpx
import pytest

from agora_agent import (
    Agent, Agora, AsyncAgora, Area, AsyncDeployedAgent, DeployedAgent,
    DeepgramSTT, OpenAI, OpenAITTS, NumberNotFoundError, PreconditionFailedError,
    SecretRefNotSupportedError, UnsupportedFieldError, V3Options, secret_ref,
)
from agora_agent.agentkit.v3 import build_body, module


OPERATIONS = [
    ("agents", "create", {"agent_name": "Support"}, "POST", "agents", {"agent_name": "Support"}),
    ("agents", "list", {"limit": 5, "cursor": "next", "order": "create_ts.asc"}, "GET", "agents", None),
    ("agents", "get", {"agent_id": "agent/a"}, "GET", "agents/agent%2Fa", None),
    ("agents", "update", {"agent_id": "a", "if_match": '"1"', "instructions": None}, "PATCH", "agents/a", {"instructions": None}),
    ("agents", "delete", {"agent_id": "a"}, "DELETE", "agents/a", None),
    ("secrets", "create", {"name": "prod", "secrets": {"key": "private"}, "idempotency_key": "dedupe"}, "POST", "secrets", {"name": "prod", "secrets": {"key": "private"}}),
    ("secrets", "list", {}, "GET", "secrets", None),
    ("secrets", "get", {"name": "prod"}, "GET", "secrets/prod", None),
    ("secrets", "replace", {"name": "prod", "if_match": '"1"', "secrets": {"k": "v"}}, "PUT", "secrets/prod", {"secrets": {"k": "v"}}),
    ("secrets", "update", {"name": "prod", "if_match": '"1"', "secrets": {"k": None}}, "PATCH", "secrets/prod", {"secrets": {"k": None}}),
    ("secrets", "delete", {"name": "prod", "if_match": '"1"'}, "DELETE", "secrets/prod", None),
    ("secrets", "set_key", {"name": "prod", "key": "k", "if_none_match": "*", "value": "v"}, "PUT", "secrets/prod/keys/k", {"value": "v"}),
    ("secrets", "delete_key", {"name": "prod", "key": "k", "if_match": '"1"'}, "DELETE", "secrets/prod/keys/k", None),
    ("numbers", "create", {"number": "+12025550123", "sip_trunk": {"host": "sip.example"}, "idempotency_key": "number-key"}, "POST", "numbers", {"number": "+12025550123", "sip_trunk": {"host": "sip.example"}}),
    ("numbers", "list", {}, "GET", "numbers", None),
    ("numbers", "get", {"number_id": "n"}, "GET", "numbers/n", None),
    ("numbers", "update", {"number_id": "n", "if_match": '"1"', "inbound": {"agent": None}}, "PATCH", "numbers/n", {"inbound": {"agent": None}}),
    ("numbers", "delete", {"number_id": "n"}, "DELETE", "numbers/n", None),
    ("sessions", "list", {"channel": "room", "status": "ACTIVE", "started_after": 12, "started_before": 25}, "GET", "sessions", None),
    ("sessions", "get", {"agent_session_id": "s"}, "GET", "sessions/s", None),
]


def make_client(handler, async_=False, **kwargs):
    transport = httpx.MockTransport(handler)
    cls = AsyncAgora if async_ else Agora
    http = httpx.AsyncClient(transport=transport) if async_ else httpx.Client(transport=transport)
    return cls(area=Area.US, app_id="project", app_certificate="cert", auth_token="raw-token",
               httpx_client=http, v3=V3Options(base_url="https://stage.example/", headers={"Gateway": "secret"}), **kwargs)


def check_request(request, operation):
    _, _, kwargs, method, suffix, body = operation
    assert request.method == method
    assert request.url.raw_path.split(b"?")[0] == ("/conversational-ai/v3/projects/project/" + suffix).encode()
    assert request.headers["Authorization"] == "agora token=raw-token"
    assert request.headers["Gateway"] == "secret"
    if body is not None:
        assert json.loads(request.content) == body
    for key, header in (("if_match", "If-Match"), ("if_none_match", "If-None-Match"), ("idempotency_key", "Idempotency-Key")):
        if key in kwargs:
            assert request.headers[header] == kwargs[key]
    for key in ("limit", "cursor", "order", "status", "channel", "started_after", "started_before"):
        if key in kwargs:
            assert request.url.params[key] == str(kwargs[key])


@pytest.mark.parametrize("operation", OPERATIONS)
def test_all_twenty_sync_wire_operations(operation):
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
async def test_all_twenty_async_wire_operations(operation):
    def handler(request):
        check_request(request, operation)
        return httpx.Response(200, json={"ok": True}, headers={"ETag": '"etag"'})
    client = make_client(handler, True)
    resource, method, kwargs, *_ = operation
    response = await getattr(getattr(client.v3, resource).with_raw_response, method)(**kwargs)
    assert response.etag == '"etag"'
    assert await getattr(getattr(client.v3, resource), method)(**kwargs) == {"ok": True}


def test_namespace_is_additive_and_pending_writes_absent():
    client = make_client(lambda _: httpx.Response(200, json={}))
    assert client.agents is not client.v3.agents
    assert not hasattr(client.v3.sessions, "create")
    assert not hasattr(client.v3, "campaigns")
    assert not hasattr(DeployedAgent, "start_call")


def test_reject_empty_identifiers_and_required_etag():
    client = make_client(lambda _: pytest.fail("request must not be sent"))
    for kwargs in ({"agent_id": ""}, {"agent_id": "  "}, {"agent_id": "a", "appid": ""}):
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


@pytest.mark.parametrize("resource,kwargs", [("agents", {"agent_name": "x"}), ("numbers", {"number": "+1", "sip_trunk": {}})])
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
        .with_tts(OpenAITTS(api_key="tts-key", base_url="https://api.openai.com/v1/audio/speech", voice="alloy", model="tts-1")))


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
    assert body["pipeline"]["asr"] == {"vendor": "deepgram", "model": "nova-3", "credential": {"mode": "byok", "api_key": "$secrets.prod.dg"}}
    assert body["pipeline"]["llm"]["credential"]["api_key"] == "$secrets.prod.openai"
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
    assert patch["pipeline"]["llm"]["credential"] == {"mode": "managed", "api_key": None}


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
    assert any("aws_secret_access_key" in x for x in errors)
    assert any("skip_patterns" in x for x in errors)
    errors = []
    result = module({"vendor": "microsoft", "params": {"api_subscription_key": "key", "region": "eastus"}}, "tts", errors)
    assert not errors
    assert result["credential"] == {"mode": "byok", "api_key": "key"}
    assert result["params"] == {"region": "eastus"}


def test_secret_ref_v2_guard_at_all_boundaries():
    agent = configured(make_client(lambda _: pytest.fail("must not send")))
    for call in (lambda: agent.to_properties(channel="c", agent_uid="1", remote_uids=["*"]),
                 lambda: agent.create_session(channel="c", agent_uid="1", remote_uids=["*"]),
                 lambda: agent.create_async_session(channel="c", agent_uid="1", remote_uids=["*"])):
        with pytest.raises(SecretRefNotSupportedError, match="requires deploy"):
            call()
    with pytest.raises(ValueError):
        secret_ref("prod.bad", "key")


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


def test_staging_environment_override_and_shared_basic_auth(monkeypatch):
    calls = []
    monkeypatch.setenv("AGORA_AGENTS_V3_BASE_URL", "https://env-stage.example")
    client = Agora(area=Area.US, app_id="project", app_certificate="cert", customer_id="id", customer_secret="secret",
                   httpx_client=httpx.Client(transport=httpx.MockTransport(lambda r: calls.append(r) or httpx.Response(200, json={}))))
    client.v3.agents.list()
    assert calls[-1].url.host == "env-stage.example"
    assert calls[-1].headers["Authorization"] == "Basic aWQ6c2VjcmV0"
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
    client = Agora(area=Area.US, app_id="project", app_certificate="cert",
                   httpx_client=httpx.Client(transport=httpx.MockTransport(lambda r: calls.append(r) or httpx.Response(200, json={}))))
    client.v3.agents.list()
    client.v3.sessions.list()
    assert [r.headers["Authorization"] for r in calls] == ["agora token=fresh-1", "agora token=fresh-2"]
    assert generated[0]["app_id"] == "project"


def test_realtime_instructions_and_audio_greeting_mapping():
    from agora_agent import OpenAIRealtime
    agent = Agent(client=make_client(lambda _: pytest.fail("mapping only"))).with_mllm(
        OpenAIRealtime(api_key="key", model="gpt-realtime", instructions="Realtime instructions"))
    body = build_body(agent)
    assert body["instructions"] == "Realtime instructions"
    assert "instructions" not in body["pipeline"]["mllm"].get("params", {})
    base = configured(make_client(lambda _: None))
    base._llm = {**base._llm, "greeting_audio_url": "https://audio.example/greeting.wav",
                 "greeting_configs": {"audio_download_timeout_ms": 1000, "audio_pcm_sample_rate": 16000}}
    greeting = build_body(base)["greeting"]
    assert greeting == {"mode": "audio", "url": "https://audio.example/greeting.wav", "text": "Hi", "download_timeout_ms": 1000, "pcm_sample_rate": 16000}


def test_realtime_vendor_messages_use_top_level_and_preserve_instruction_precedence():
    from agora_agent import OpenAIRealtime
    client = make_client(lambda _: pytest.fail("pure mapping"))
    agent = Agent(client=client, instructions="Deprecated instructions").with_mllm(
        OpenAIRealtime(
            api_key="key", instructions="Provider instructions",
            messages=[{"role": "system", "content": "Explicit system message"},
                      {"role": "user", "content": "Hello"}],
        )
    )
    body = build_body(agent)
    assert body["instructions"] == "Explicit system message"
    assert body["messages"] == [{"role": "user", "content": "Hello"}]
    assert "messages" not in body["pipeline"]["mllm"]
    assert "instructions" not in body["pipeline"]["mllm"].get("params", {})

    params_only = build_body(Agent(client=client, instructions="Deprecated").with_mllm(
        OpenAIRealtime(api_key="key", instructions="Provider", messages=[{"role": "assistant", "content": "Hi"}])
    ))
    assert params_only["instructions"] == "Provider"
    assert params_only["messages"] == [{"role": "assistant", "content": "Hi"}]
    with pytest.raises(UnsupportedFieldError, match=r"mllm.messages\[0\]"):
        build_body(Agent(client=client).with_mllm(OpenAIRealtime(
            api_key="key", messages=[{"role": "tool", "content": "unsupported"}]
        )))


@pytest.mark.parametrize("mode,config,expected", [
    ("agora_vad", {"agora_vad_config": {"threshold": 0.5}}, {"type": "agora_vad", "threshold": 0.5}),
    ("server_vad", {"server_vad_config": {"threshold": 0.6, "idle_timeout_ms": 5000}},
     {"type": "server_vad", "threshold": 0.6, "idle_timeout_ms": 5000}),
    ("semantic_vad", {"semantic_vad_config": {"eagerness": "high"}},
     {"type": "semantic_vad", "eagerness": "high"}),
])
def test_real_realtime_vendor_turn_detection_flattens_create_schema_fields(mode, config, expected):
    from agora_agent import OpenAIRealtime
    from agora_agent.types.mllm_turn_detection import MllmTurnDetection
    client = make_client(lambda _: pytest.fail("pure mapping"))
    turn = MllmTurnDetection(mode=mode, **config)
    body = build_body(Agent(client=client).with_mllm(OpenAIRealtime(api_key="key", turn_detection=turn)))
    actual = body["pipeline"]["turn_detection"]
    assert actual == expected


def test_realtime_turn_detection_rejects_incompatible_config_without_dropping_it():
    from agora_agent import OpenAIRealtime
    from agora_agent.types.mllm_turn_detection import MllmTurnDetection
    client = make_client(lambda _: pytest.fail("pure mapping"))
    turn = MllmTurnDetection(mode="server_vad", semantic_vad_config={"eagerness": "high"})
    with pytest.raises(UnsupportedFieldError, match="semantic_vad_config"):
        build_body(Agent(client=client).with_mllm(OpenAIRealtime(api_key="key", turn_detection=turn)))


def test_greeting_playback_mode_aliases_and_unsupported_mode():
    client = make_client(lambda _: pytest.fail("pure mapping"))
    for old, new in (("single_first", "first_join"), ("single_every", "each_join")):
        body = build_body(Agent(client=client, greeting="Hello", greeting_configs={"mode": old}))
        assert body["greeting"] == {"mode": "text", "text": "Hello", "on": new}
    with pytest.raises(UnsupportedFieldError, match="greeting_configs.mode"):
        build_body(Agent(client=client, greeting="Hello", greeting_configs={"mode": "unknown"}))


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
