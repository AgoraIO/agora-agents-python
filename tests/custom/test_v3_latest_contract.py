"""Corrected release contract regressions, entirely offline."""
import copy
import json
from pathlib import Path

import httpx
import pytest
from test_v3_preview import make_client

from agora_agent import Agent, OpenAI, secret_ref
from agora_agent.agentkit.v3 import build_body, replacement_patch
from agora_agent.agentkit.vendors.llm import AmazonBedrock
from agora_agent.agentkit.vendors.stt import AmazonSTT, GoogleSTT
from agora_agent.agentkit.vendors.tts import AmazonTTS, GoogleTTS, SarvamTTS
from agora_agent.v3.contract import validate_write


@pytest.mark.parametrize("category,vendor,expected", [
    ("asr", AmazonSTT(access_key="access", secret_key="secret", region="us-east-1", language="en-US"), {"access_key_id": "access", "secret_access_key": "secret"}),
    ("asr", GoogleSTT(project_id="p", location="global", adc_credentials_string="json", language="en"), {"adc_credentials_string": "json"}),
    ("llm", AmazonBedrock(access_key="access", secret_key="secret", region="us-east-1", model="model"), {"access_key": "access", "secret_key": "secret"}),
    ("tts", AmazonTTS(access_key="access", secret_key="secret", region="us-east-1", voice_id="Joanna", engine="neural"), {"aws_access_key_id": "access", "aws_secret_access_key": "secret"}),
    ("tts", GoogleTTS(key="json", voice_name="voice"), {"credentials": "json"}),
    ("tts", SarvamTTS(key="sarvam", target_language_code="en-IN", speaker="anushka"), {"api_subscription_key": "sarvam"}),
])
def test_public_vendor_credentials_are_lossless_and_ephemeral_only(category, vendor, expected):
    client = make_client(lambda _: pytest.fail("must not send"))
    agent = getattr(Agent(client=client), "with_" + ("stt" if category == "asr" else category))(vendor)
    before = copy.deepcopy(agent.config)
    body = build_body(agent, "test")
    assert body["pipeline"][category]["credential"] == {"mode": "byok", "fields": expected}
    ephemeral = {"agent": {k: v for k, v in body.items() if k != "agent_name"}, "transport": {"type": "rtc", "channel": "r", "subscribe_uids": ["2"]}}
    validate_write("POST", "/conversational-ai/v1/projects/p/sessions/ephemeral", ephemeral)
    with pytest.raises(ValueError, match="secret_ref"):
        agent.save(name="test")
    assert agent.config == before


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_new_runtime_update_and_auto_uid(async_):
    requests = []
    def handler(request):
        requests.append(request)
        return httpx.Response(200, json={"agent_session_id": "session", "create_ts": 1, "status": "RUNNING"})
    client = make_client(handler, async_)
    agent = Agent(client=client).with_llm(OpenAI(api_key="inline", model="gpt", base_url="https://api.openai.com/v1/chat/completions"))
    session = (agent.create_async_session if async_ else agent.create_session)(channel="r", remote_uids=["customer"])
    result = session.start()
    if async_:
        await result
    body = json.loads(requests[0].content)
    assert "uid" not in body["transport"]
    assert body["agent"]["pipeline"]["llm"]["credential"] == {"mode": "byok", "fields": {"api_key": "inline"}}
    properties = {"token": "renewed", "messages": [{"role": "user", "content": "Hi"}], "llm": {"params": {"temperature": 0.4}}}
    before = copy.deepcopy(properties)
    result = session.update(properties)
    if async_:
        await result
    assert requests[-1].method == "PATCH"
    assert json.loads(requests[-1].content) == {"transport": {"token": "renewed"}, "agent": {"overrides": {"messages": properties["messages"], "pipeline": {"llm": properties["llm"]}}}}
    assert properties == before
    for invalid in ({"mllm": {"params": {"temperature": 0.2}}}, {"llm": {"params": {}}, "mllm": {"params": {}}}, {"llm": {"params": {"url": "https://other"}}}, {"mllm": {"params": {"endpoint": "https://other"}}}, {"token": None}, {"instructions": "no"}):
        count = len(requests)
        with pytest.raises(ValueError):
            result = session.update(invalid)
            if async_:
                await result
        assert len(requests) == count


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_latest_campaign_number_policy_and_retention(async_):
    requests = []
    def handler(request):
        requests.append(request)
        return httpx.Response(200, json={})
    client = make_client(handler, async_)
    result = client.campaigns.create(name="campaign", agent_id="a", transport={"type": "telephony", "from": "n", "call_policy": {"end_call": {"on_voicemail": True}, "max_silence_duration_ms": 30000}}, schedule={"mode": "immediate"}, contacts=[{"phone": "+12025550123"}] * 2001, data_policy={"retention": "none"}, idempotency_key="campaign-1")
    if async_:
        await result
    assert len(json.loads(requests[-1].content)["contacts"]) == 2001
    assert json.loads(requests[-1].content)["data_policy"] == {"retention": "none"}
    result = client.numbers.create(number="+12025550123", sip_trunk={"hostname": "sip.example", "allowed_ips": ["*", "192.0.2.1/24"]}, inbound={"agent": "a", "call_policy": {"end_call": {"on_voicemail": True}}})
    if async_:
        await result
    assert json.loads(requests[-1].content)["inbound"]["call_policy"]["end_call"]["on_voicemail"]
    for invalid in ({"max_attempts": 2}, {"retry_backoff_ms": 1000}):
        with pytest.raises(ValueError):
            result = client.campaigns.update(campaign_id="c", if_match='"e"', pacing=invalid)
            if async_:
                await result
    for invalid in ("2001:db8::1", "192.0.2.1/024", "192.0.2.1/255.255.255.0", "example.org"):
        with pytest.raises(ValueError):
            result = client.numbers.create(number="+12025550123", sip_trunk={"hostname": "sip.example", "allowed_ips": [invalid]})
            if async_:
                await result


@pytest.mark.parametrize("key", ["x" * 257, "a b", "new\nline", "非ASCII"])
def test_idempotency_key_exact_contract(key):
    client = make_client(lambda _: pytest.fail("must not send"))
    with pytest.raises(ValueError):
        client.v3.sessions.start(agent_id="a", transport={"type": "rtc", "channel": "r", "subscribe_uids": ["2"]}, idempotency_key=key)
    with pytest.raises(ValueError):
        Agent(client=client).create_session(channel="r", remote_uids=["2"], idempotency_key=key)


def test_redeploy_clears_hidden_previous_vendor_fields_and_managed_fields():
    previous = {"pipeline": {"mode": "cascaded", "tts": {"vendor": "amazon", "credential": {"mode": "byok"}}}}
    desired = {"pipeline": {"mode": "cascaded", "tts": {"vendor": "google", "credential": {"mode": "byok", "fields": {"credentials": "$secrets.prod.google"}}}}}
    patch = replacement_patch(previous, desired)
    assert patch["pipeline"]["tts"]["credential"]["fields"] == {"aws_access_key_id": None, "aws_secret_access_key": None, "credentials": "$secrets.prod.google"}
    validate_write("PATCH", "/conversational-ai/v1/projects/p/agents/a", patch)
    managed = replacement_patch(previous, {"pipeline": {"mode": "cascaded", "tts": {"vendor": "google", "credential": {"mode": "managed"}}}})
    assert managed["pipeline"]["tts"]["credential"] == {"mode": "managed", "fields": None}
    validate_write("PATCH", "/conversational-ai/v1/projects/p/agents/a", managed)


def test_shared_snapshot_and_public_saved_reference_only():
    root = Path(__file__).resolve().parents[2]
    assert (root / "openapi.json").read_bytes() == (root / "src/agora_agent/v3/openapi.json").read_bytes()
    client = make_client(lambda _: pytest.fail("must not send"))
    with pytest.raises(ValueError):
        client.v3.agents.create(agent_name="unsafe", pipeline={"mode": "cascaded", "llm": {"credential": {"mode": "byok", "fields": {"api_key": "inline"}}}})
    with pytest.raises(ValueError):
        secret_ref("old-hyphen", "key")
    body = build_body(Agent(client=client).with_llm(OpenAI(api_key=secret_ref("prod", "key"), model="gpt-4o-mini", base_url="https://api.openai.com/v1/chat/completions")), "safe")
    validate_write("POST", "/conversational-ai/v1/projects/p/agents", body)


def test_campaign_contact_count_boundaries_and_body_size():
    body = {"name": "x", "agent_id": "a", "transport": {"type": "telephony", "from": "n"}, "schedule": {"mode": "immediate"}, "contacts": [{"phone": "+12025550123"}] * 50000}
    path = "/conversational-ai/v1/projects/p/campaigns"
    validate_write("POST", path, body)
    body["contacts"].append({"phone": "+12025550123"})
    with pytest.raises(ValueError):
        validate_write("POST", path, body)
    body["contacts"] = [{"phone": "+12025550123", "values": {"text": "x" * (10 * 1024 * 1024)}}]
    with pytest.raises(ValueError, match="10 MiB"):
        validate_write("POST", path, body)


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_no_body_operations_do_not_accept_hidden_write_body(async_):
    client = make_client(lambda _: pytest.fail("must not send"), async_)
    with pytest.raises(ValueError, match="request body"):
        result = client.v3.sessions.stop(agent_session_id="s", request_options={"additional_body_parameters": {"unsupported": True}})
        if async_:
            await result


def test_same_vendor_alternate_credential_form_clears_hidden_key():
    patch = replacement_patch({"vendor": "amazon", "credential": {"mode": "byok"}}, {"vendor": "amazon", "credential": {"mode": "byok", "fields": {"access_key": "$secrets.prod.access", "secret_key": "$secrets.prod.secret"}}}, "llm")
    assert patch["credential"]["fields"] == {"api_key": None, "access_key": "$secrets.prod.access", "secret_key": "$secrets.prod.secret"}


@pytest.mark.parametrize("module", [
    {"vendor": "amazon", "credential": {"mode": "byok", "fields": {"api_key": "wrong-field"}}},
    {"vendor": "deepgram", "credential": {"mode": "managed"}, "url": "https://custom.example"},
])
def test_vendor_conditional_credentials_are_validated(module):
    with pytest.raises(ValueError):
        validate_write("POST", "/conversational-ai/v1/projects/p/sessions/ephemeral", {"agent": {"pipeline": {"mode": "cascaded", "asr": module}}, "transport": {"type": "rtc", "channel": "r", "subscribe_uids": ["2"]}})


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_messages_shortcut_is_transport_independent(async_):
    requests = []
    def handler(request):
        requests.append(request)
        return httpx.Response(200, json={"agent_id": "legacy-session"})
    client = make_client(handler, async_)
    # Ordinary inline configuration keeps the established session transport.
    agent = Agent(client=client).with_llm(OpenAI(api_key="inline", model="gpt", base_url="https://api.openai.com/v1/chat/completions"))
    session = (agent.create_async_session if async_ else agent.create_session)(channel="r", agent_uid="1", remote_uids=["2"], token="rtc")
    session._status = "running"
    session._agent_id = "legacy-session"
    messages = [{"role": "system", "content": "Updated"}]
    properties = {"messages": messages, "llm": {"params": {"temperature": 0.2}}}
    before = copy.deepcopy(properties)
    result = session.update(properties)
    if async_:
        await result
    assert json.loads(requests[-1].content)["properties"] == {"llm": {"system_messages": messages, "params": {"temperature": 0.2}}}
    assert properties == before
    with pytest.raises(ValueError):
        result = session.update({"messages": messages, "llm": {"system_messages": messages}})
        if async_:
            await result


def test_llm_params_with_legacy_messages_spelling_is_supported():
    from agora_agent.agentkit.session_backend import update_body
    messages = [{"role": "system", "content": "Updated"}]
    assert update_body({"llm": {"system_messages": messages, "params": {"temperature": 0.2}}}) == {"agent": {"overrides": {"messages": messages, "pipeline": {"llm": {"params": {"temperature": 0.2}}}}}}
    with pytest.raises(ValueError):
        update_body({"messages": messages, "llm": {"system_messages": messages}})


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_preview_rejects_mllm_before_network(async_):
    from agora_agent import OpenAIRealtime, UnsupportedFieldError
    client = make_client(lambda _: pytest.fail("unsupported MLLM must not reach HTTP"), async_)
    agent = Agent(client=client).with_mllm(OpenAIRealtime(api_key="inline"))
    with pytest.raises(UnsupportedFieldError, match="realtime pipelines are not supported"):
        result = agent.save_async(name="realtime") if async_ else agent.save(name="realtime")
        if async_:
            await result
    create = agent.create_async_session if async_ else agent.create_session
    for options in ({}, {"agent_uid": "1", "values": {}}, {"agent_uid": "1", "idempotency_key": "start"}):
        with pytest.raises(UnsupportedFieldError, match="realtime pipelines are not supported"):
            create(channel="r", remote_uids=["2"], **options)
    for pipeline in ({"mode": "realtime"}, {"mode": "cascaded", "mllm": {}}, {"mllm": None}):
        for method, kwargs in ((client.v3.agents.create, {"agent_name": "realtime", "pipeline": pipeline}),
                               (client.v3.agents.update, {"agent_id": "a", "if_match": '"e"', "pipeline": pipeline}),
                               (client.v3.sessions.start_ephemeral, {"agent": {"pipeline": pipeline}, "transport": {"type": "rtc", "channel": "r", "subscribe_uids": ["2"]}})):
            with pytest.raises(ValueError):
                result = method(**kwargs)
                if async_:
                    await result
    with pytest.raises(ValueError):
        result = client.v3.sessions.update(agent_session_id="s", agent={"overrides": {"pipeline": {"mllm": {"params": {}}}}})
        if async_:
            await result


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_legacy_mllm_start_and_update_remain_supported(async_):
    from agora_agent import OpenAIRealtime
    requests = []
    def handler(request):
        requests.append(request)
        return httpx.Response(200, json={"agent_id": "legacy-session"})
    client = make_client(handler, async_)
    agent = Agent(client=client).with_mllm(OpenAIRealtime(api_key="inline"))
    session = (agent.create_async_session if async_ else agent.create_session)(channel="r", agent_uid="1", remote_uids=["2"], token="rtc")
    result = session.start()
    if async_:
        result = await result
    assert result == "legacy-session"
    assert requests[-1].url.path.endswith("/join")
    assert json.loads(requests[-1].content)["properties"]["mllm"]["api_key"] == "inline"
    result = session.update({"mllm": {"params": {"temperature": 0.2}}})
    if async_:
        await result
    assert requests[-1].url.path.endswith("/legacy-session/update")
    assert json.loads(requests[-1].content)["properties"] == {"mllm": {"params": {"temperature": 0.2}}}
