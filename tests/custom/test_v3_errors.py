"""v3 error taxonomy: one rooted hierarchy, categories, cause chains and compatibility."""

import json

import httpx
import pytest

import agora_agent
import agora_agent.v3 as v3
from agora_agent import (
    Agent,
    Agora,
    AgoraV3Error,
    Area,
    AsyncAgora,
    DeployedAgent,
    NumberNotFoundError,
    PreconditionFailedError,
    SecretRefNotSupportedError,
    UnsupportedFieldError,
    V3ApiError,
    V3ConfigurationError,
    V3ConnectionError,
    V3Options,
    V3TimeoutError,
    V3ValidationError,
    secret_ref,
)
from agora_agent.core.api_error import ApiError
from agora_agent.v3 import RawResponse

TOKEN = "raw-token-must-not-leak"
CATEGORIES = (V3ValidationError, V3ConfigurationError, V3ConnectionError, V3ApiError)


def never(request):
    pytest.fail("must not send " + str(request.url))


def make_client(handler, async_=False, *, v3_options=None, **http_kwargs):
    transport = httpx.MockTransport(handler)
    http = (httpx.AsyncClient if async_ else httpx.Client)(transport=transport, **http_kwargs)
    return (AsyncAgora if async_ else Agora)(
        area=Area.US,
        app_id="project",
        auth_token=TOKEN,
        httpx_client=http,
        v3=v3_options or V3Options(base_url="https://stage.example"),
    )


async def run(result, async_):
    return await result if async_ else result


def raising(exc_type, message="boom"):
    def handler(request):
        raise exc_type(message, request=request)

    return handler


def assert_no_secret(error):
    text = str(error) + repr(error)
    assert TOKEN not in text
    assert "agora token=" not in text.lower() and "nope" not in text


# --- hierarchy and exports ---------------------------------------------------


def test_hierarchy_is_rooted_and_keeps_builtin_bases():
    for category in CATEGORIES:
        assert issubclass(category, AgoraV3Error)
    assert issubclass(V3ValidationError, ValueError)
    assert issubclass(V3ConfigurationError, ValueError)
    assert issubclass(V3ConnectionError, ConnectionError)
    assert issubclass(V3TimeoutError, V3ConnectionError)
    assert issubclass(V3TimeoutError, TimeoutError)
    assert issubclass(V3ApiError, ApiError)
    assert not issubclass(V3ApiError, ValueError)
    assert issubclass(PreconditionFailedError, V3ApiError)
    # Categories are mutually exclusive.
    for left in CATEGORIES:
        for right in CATEGORIES:
            assert left is right or not issubclass(left, right)


def test_agentkit_errors_fold_into_validation_without_renaming():
    assert issubclass(UnsupportedFieldError, V3ValidationError)
    assert issubclass(SecretRefNotSupportedError, V3ValidationError)
    assert issubclass(NumberNotFoundError, V3ValidationError)
    assert issubclass(NumberNotFoundError, LookupError)
    assert UnsupportedFieldError(["b", "a", "a"]).fields == ["a", "b"]


def test_error_classes_are_exported_from_v3_and_package_root():
    names = [
        "AgoraV3Error",
        "V3ValidationError",
        "V3ConfigurationError",
        "V3ConnectionError",
        "V3TimeoutError",
        "V3ApiError",
        "PreconditionFailedError",
    ]
    for name in names:
        assert name in v3.__all__
        assert name in agora_agent.__all__
        assert getattr(v3, name) is getattr(agora_agent, name)
    from agora_agent.v3._transport import PreconditionFailedError as legacy_location

    assert legacy_location is PreconditionFailedError


# --- validation ----------------------------------------------------------------


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.parametrize(
    "call",
    [
        lambda c: c.v3.agents.get(agent_id=""),
        lambda c: c.v3.agents.get(agent_id=".."),
        lambda c: c.v3.agents.create(agent_name=""),
        lambda c: c.v3.secrets.create(
            name="prod", secrets={"k": "v"}, request_options={"additional_headers": {"Idempotency-Key": "k"}}
        ),
        lambda c: c.v3.sessions.get(
            agent_session_id="s", request_options={"additional_headers": {"Idempotency-Key": "bad key"}}
        ),
        lambda c: c.v3.agents.list(request_options={"customer_secret": "nope"}),
        lambda c: c.v3.sessions.stop(agent_session_id="s", request_options={"additional_body_parameters": {"x": 1}}),
        lambda c: c.v3.sessions.start(
            agent_id="a", transport={"type": "rtc", "channel": "room", "subscribe_uids": ["*"]}
        ),
    ],
)
@pytest.mark.asyncio
async def test_validation_errors_are_raised_before_http(async_, call):
    client = make_client(never, async_)
    with pytest.raises(V3ValidationError) as caught:
        await run(call(client), async_)
    assert isinstance(caught.value, ValueError) and isinstance(caught.value, AgoraV3Error)
    assert_no_secret(caught.value)


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_backward_compatible_except_value_error(async_):
    client = make_client(never, async_)
    try:
        await run(client.v3.agents.get(agent_id=""), async_)
    except ValueError as error:
        assert type(error) is V3ValidationError
    else:
        pytest.fail("expected ValueError")


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_unknown_keyword_arguments_stay_type_errors(async_):
    client = make_client(never, async_)
    with pytest.raises(TypeError) as caught:
        client.v3.agents.get(agent_idd="a")
    assert not isinstance(caught.value, AgoraV3Error)


def test_agentkit_validation_errors():
    client = make_client(never)
    with pytest.raises(V3ValidationError, match="secret_set"):
        secret_ref("bad name", "key")
    with pytest.raises(V3ValidationError, match="Variable name"):
        Agent(client=client).with_variable("Bad", type="str")
    agent = DeployedAgent(client, RawResponse({"agent_id": "a", "agent_name": "Support"}, httpx.Headers(), 200, None))
    with pytest.raises(V3ValidationError, match="channel"):
        agent.create_session(channel="", agent_uid="1", remote_uids=["2"])
    with pytest.raises(V3ValidationError, match="Idempotency-Key") as caught:
        agent.create_session(channel="room", agent_uid="1", remote_uids=["2"], idempotency_key="bad key")
    assert isinstance(caught.value.__cause__, ValueError)


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_number_not_found_is_validation_and_lookup_error(async_):
    page = {"data": {"list": []}, "has_more": False, "next_cursor": None}
    client = make_client(lambda _: httpx.Response(200, json=page), async_)
    cls = agora_agent.AsyncDeployedAgent if async_ else DeployedAgent
    deployed = cls(client, RawResponse({"agent_id": "a", "agent_name": "Support"}, httpx.Headers(), 200, None))
    for expected in (NumberNotFoundError, V3ValidationError, LookupError, ValueError):
        with pytest.raises(expected):
            await run(deployed.assign_number("+12025550123"), async_)


def test_v2_shared_message_shortcut_keeps_plain_value_error():
    from agora_agent.agentkit.session_backend import legacy_update_body

    with pytest.raises(ValueError) as caught:
        legacy_update_body({"messages": "not-a-list"})
    assert type(caught.value) is ValueError
    assert not isinstance(caught.value, AgoraV3Error)


# --- configuration -------------------------------------------------------------


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.parametrize(
    "origin", ["ftp://preview.ai.agora.io", "https://user:pass@preview.ai.agora.io", "https://preview.ai.agora.io/path"]
)
@pytest.mark.asyncio
async def test_invalid_base_url_is_configuration_error(async_, origin):
    client = make_client(never, async_, v3_options=V3Options(base_url=origin))
    with pytest.raises(V3ConfigurationError, match="origin") as caught:
        await run(client.v3.agents.list(), async_)
    assert isinstance(caught.value, ValueError)
    assert not isinstance(caught.value, V3ValidationError)
    assert "pass" not in str(caught.value)


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_invalid_environment_origin_is_configuration_error(async_, monkeypatch):
    monkeypatch.setenv("AGORA_AGENTS_V3_BASE_URL", "https://preview.ai.agora.io?debug=1")
    client = make_client(never, async_, v3_options=V3Options())
    with pytest.raises(V3ConfigurationError):
        await run(client.v3.agents.list(), async_)


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_internal_option_headers_are_configuration_errors(async_):
    options = V3Options(base_url="https://stage.example", headers={"X-Studio-Region": "us"})
    client = make_client(never, async_, v3_options=options)
    with pytest.raises(V3ConfigurationError, match="Internal") as caught:
        await run(client.v3.agents.list(), async_)
    assert isinstance(caught.value.__cause__, ValueError)


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_httpx_client_auth_is_configuration_error(async_):
    client = make_client(never, async_, auth=httpx.BasicAuth("user", "pass"))
    with pytest.raises(V3ConfigurationError, match="httpx auth"):
        await run(client.v3.agents.list(), async_)


# --- connection and timeout ----------------------------------------------------


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.parametrize("exc_type", [httpx.ConnectError, httpx.RemoteProtocolError, httpx.ReadError])
@pytest.mark.asyncio
async def test_transport_failures_are_connection_errors_with_cause(async_, exc_type):
    client = make_client(raising(exc_type, "connection reset"), async_)
    with pytest.raises(V3ConnectionError) as caught:
        await run(client.v3.agents.get(agent_id="a"), async_)
    error = caught.value
    assert type(error) is V3ConnectionError
    assert isinstance(error, ConnectionError) and isinstance(error, AgoraV3Error)
    assert not isinstance(error, (TimeoutError, ApiError, ValueError))
    assert isinstance(error.__cause__, exc_type)
    assert str(error).startswith("v3 GET request could not complete: " + exc_type.__name__)
    assert_no_secret(error)


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.parametrize("exc_type", [httpx.ConnectTimeout, httpx.ReadTimeout, httpx.WriteTimeout, httpx.PoolTimeout])
@pytest.mark.asyncio
async def test_timeouts_are_connection_subtype_and_builtin_timeout(async_, exc_type):
    client = make_client(raising(exc_type, "timed out"), async_)
    with pytest.raises(V3TimeoutError) as caught:
        await run(client.v3.agents.create(agent_name="Support"), async_)
    error = caught.value
    assert isinstance(error, V3ConnectionError)
    assert isinstance(error, TimeoutError)
    assert isinstance(error.__cause__, httpx.TimeoutException)
    assert "POST request timed out" in str(error)
    assert_no_secret(error)


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_connection_errors_are_not_retried_for_writes(async_):
    calls = []

    def handler(request):
        calls.append(request)
        raise httpx.ConnectError("refused", request=request)

    client = make_client(handler, async_)
    with pytest.raises(V3ConnectionError):
        await run(client.v3.agents.create(agent_name="Support", request_options={"max_retries": 3}), async_)
    assert len(calls) == 1


# --- API errors ----------------------------------------------------------------


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_api_error_exposes_status_headers_body_detail_reason_request_id(async_):
    payload = {"reason": "AgentNotFound", "detail": "Agent a does not exist"}
    client = make_client(lambda _: httpx.Response(404, json=payload, headers={"Agora-Request-Id": "req-123"}), async_)
    with pytest.raises(V3ApiError) as caught:
        await run(client.v3.agents.get(agent_id="a"), async_)
    error = caught.value
    assert type(error) is V3ApiError
    assert error.status_code == 404
    assert error.headers["agora-request-id"] == "req-123"
    assert error.body == payload
    assert json.loads(error.raw_body) == payload
    assert (error.detail, error.reason, error.request_id) == ("Agent a does not exist", "AgentNotFound", "req-123")
    assert (
        str(error) == "v3 request failed with status 404: AgentNotFound: Agent a does not exist (request ID: req-123)"
    )
    assert error.args == (str(error),)
    assert_no_secret(error)


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_api_error_with_non_json_and_empty_bodies(async_):
    responses = iter([httpx.Response(502, text="upstream unavailable"), httpx.Response(500)])
    client = make_client(lambda _: next(responses), async_)
    with pytest.raises(V3ApiError) as caught:
        await run(client.v3.agents.list(), async_)
    assert caught.value.body == "upstream unavailable"
    assert caught.value.raw_body == b"upstream unavailable"
    assert caught.value.detail is None and caught.value.reason is None and caught.value.request_id is None
    assert str(caught.value) == "v3 request failed with status 502: upstream unavailable"
    with pytest.raises(V3ApiError) as caught:
        await run(client.v3.agents.list(), async_)
    assert caught.value.body is None and caught.value.raw_body == b""
    assert str(caught.value) == "v3 request failed with status 500"


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_backward_compatible_except_api_error(async_):
    client = make_client(lambda _: httpx.Response(409, json={"reason": "TaskConflict", "detail": "busy"}), async_)
    try:
        await run(client.v3.sessions.stop(agent_session_id="s"), async_)
    except ApiError as error:
        assert isinstance(error, V3ApiError)
        assert error.status_code == 409 and error.body["reason"] == "TaskConflict"
    else:
        pytest.fail("expected ApiError")


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_precondition_failed_is_api_subtype_and_keeps_latest(async_):
    def handler(request):
        if request.method == "PATCH":
            return httpx.Response(
                412, json={"reason": "PreconditionFailed", "detail": "stale"}, headers={"Agora-Request-Id": "r412"}
            )
        return httpx.Response(200, json={"agent_id": "a", "agent_name": "fresh"})

    client = make_client(handler, async_)
    for expected in (PreconditionFailedError, V3ApiError, ApiError, AgoraV3Error):
        with pytest.raises(expected) as caught:
            await run(client.v3.agents.update(agent_id="a", if_match='"old"', instructions="x"), async_)
    error = caught.value
    assert type(error) is PreconditionFailedError
    assert (error.status_code, error.reason, error.detail, error.request_id) == (
        412,
        "PreconditionFailed",
        "stale",
        "r412",
    )
    assert await run(error.latest(), async_) == {"agent_id": "a", "agent_name": "fresh"}


def test_precondition_failed_constructed_directly():
    error = PreconditionFailedError(
        status_code=412, headers={"Agora-Request-Id": "x"}, body={"reason": "PreconditionFailed"}
    )
    assert error.request_id == "x" and error.headers == {"agora-request-id": "x"}
    with pytest.raises(RuntimeError, match="latest"):
        error.latest()


def test_v2_generated_api_errors_are_unchanged():
    from agora_agent.client import Agora as GeneratedAgora

    http = httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(404, json={"reason": "NotFound"})))
    raw = GeneratedAgora(authorization="agora token=abc", httpx_client=http)
    with pytest.raises(ApiError) as caught:
        raw.agents.get("project", "agent")
    assert not isinstance(caught.value, AgoraV3Error)


# --- AgentKit paths over v3 --------------------------------------------------------


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_agentkit_saved_agent_surfaces_v3_categories(async_):
    client = make_client(raising(httpx.ConnectError, "refused"), async_)
    cls = agora_agent.AsyncSavedAgent if async_ else agora_agent.SavedAgent
    with pytest.raises(V3ConnectionError):
        await run(cls.get(client, "a"), async_)
    client = make_client(lambda _: httpx.Response(404, json={"reason": "AgentNotFound", "detail": "missing"}), async_)
    with pytest.raises(V3ApiError) as caught:
        await run(cls.get(client, "a"), async_)
    assert caught.value.reason == "AgentNotFound"


# --- 2xx responses that violate the API contract ----------------------------------


def deployed(client, async_):
    cls = agora_agent.AsyncDeployedAgent if async_ else DeployedAgent
    return cls(client, RawResponse({"agent_id": "a", "agent_name": "Support"}, httpx.Headers(), 200, None))


def assert_contract_violation(error, status_code, violation):
    assert type(error) is V3ApiError
    assert isinstance(error, ApiError) and isinstance(error, AgoraV3Error)
    assert not isinstance(error, ValueError)
    assert error.status_code == status_code
    assert error.violation == violation
    assert error.request_id == "req-2xx"
    assert str(error) == (
        f"v3 response with status {status_code} violates the API contract: {violation} (request ID: req-2xx)"
    )


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_repeated_pagination_cursor_is_api_contract_error(async_):
    page = {"data": {"count": 0, "list": []}, "has_more": True, "next_cursor": "same"}
    client = make_client(lambda _: httpx.Response(200, json=page, headers={"Agora-Request-Id": "req-2xx"}), async_)
    pages = []
    with pytest.raises(V3ApiError) as caught:
        if async_:
            async for item in client.v3.agents.iter_pages():
                pages.append(item)
        else:
            for item in client.v3.agents.iter_pages():
                pages.append(item)
    assert len(pages) == 2  # The repeated cursor is detected on the second page.
    assert_contract_violation(caught.value, 200, "Invalid or repeated v3 pagination cursor")
    assert caught.value.body == page
    assert json.loads(caught.value.raw_body) == page


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_missing_pagination_cursor_is_api_contract_error(async_):
    page = {"data": {"count": 0, "list": []}, "has_more": True, "next_cursor": None}
    client = make_client(lambda _: httpx.Response(200, json=page, headers={"Agora-Request-Id": "req-2xx"}), async_)
    with pytest.raises(V3ApiError) as caught:
        if async_:
            async for _ in client.v3.numbers.iter_all():
                pass
        else:
            for _ in client.v3.numbers.iter_all():
                pass
    assert_contract_violation(caught.value, 200, "Invalid or repeated v3 pagination cursor")


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_non_json_success_body_is_api_contract_error(async_):
    client = make_client(
        lambda _: httpx.Response(201, text="<html>proxy</html>", headers={"Agora-Request-Id": "req-2xx"}), async_
    )
    with pytest.raises(V3ApiError) as caught:
        await run(client.v3.agents.create(agent_name="Support"), async_)
    assert_contract_violation(caught.value, 201, "response body is not valid JSON")
    assert caught.value.body == "<html>proxy</html>"
    assert caught.value.raw_body == b"<html>proxy</html>"
    assert caught.value.__cause__ is None and caught.value.__suppress_context__


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_empty_success_body_still_returns_none(async_):
    client = make_client(lambda _: httpx.Response(204), async_)
    assert await run(client.v3.agents.delete(agent_id="a"), async_) is None


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_number_lookup_repeated_cursor_is_api_contract_error(async_):
    page = {"data": {"list": []}, "has_more": True, "next_cursor": "same"}
    client = make_client(lambda _: httpx.Response(200, json=page, headers={"Agora-Request-Id": "req-2xx"}), async_)
    with pytest.raises(V3ApiError) as caught:
        await run(deployed(client, async_).assign_number("+12025550123"), async_)
    assert_contract_violation(caught.value, 200, "Invalid or repeated number pagination cursor")


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_missing_etag_is_api_contract_error_before_write(async_):
    calls = []

    def handler(request):
        calls.append(request.method)
        return httpx.Response(200, json={"number_id": "n"}, headers={"Agora-Request-Id": "req-2xx"})

    client = make_client(handler, async_)
    with pytest.raises(V3ApiError) as caught:
        await run(deployed(client, async_).assign_number("n"), async_)
    assert_contract_violation(caught.value, 200, "v3 response omitted ETag; refusing an unguarded update")
    assert caught.value.body == {"number_id": "n"}
    assert calls == ["GET"]  # The unguarded PATCH is never sent.


@pytest.mark.parametrize("async_", [False, True])
@pytest.mark.asyncio
async def test_session_start_without_session_id_is_api_contract_error(async_):
    client = make_client(
        lambda _: httpx.Response(
            200, json={"status": "STARTING", "create_ts": 1}, headers={"Agora-Request-Id": "req-2xx"}
        ),
        async_,
    )
    session = deployed(client, async_).create_session(channel="room", agent_uid="1", remote_uids=["2"])
    with pytest.raises(V3ApiError) as caught:
        await run(session.start(), async_)
    assert_contract_violation(caught.value, 200, "Session response is missing agent_session_id")
    assert session.status == "error"
