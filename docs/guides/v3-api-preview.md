# v3 stored-agent preview (P1)

Use `Agent.deploy()` to save a reusable configuration and assign it to an existing inbound number. The additive `client.v3` namespace covers all 20 published staging operations. See the [complete v3 reference](../reference/v3.md) for method arguments and required headers.

| Object or API | Meaning | Available now |
|---|---|---|
| `Agent` | Immutable local builder | Existing vendor configuration plus `with_variable` and deploy |
| v3 stored agent / `DeployedAgent` | Persisted configuration identified by `agent_id` | Create, read, conditional update, delete, inbound-number assignment and number listing |
| v2 `AgentSession` | Running RTC instance, also historically called an agent | Existing `create_session(...).start()` lifecycle |
| v3 session | Running instance identified by `agent_session_id` | Low-level list and get only |

Deploying stores configuration; it does not start a session. v3 session writes, outbound calls, AgentKit analysis helpers and campaigns await backend schemas and are not implemented. The SDK package version continues to describe package compatibility independently of the REST API version.

## Quick start with staging

Install from this repository's `feat/v3-api-preview` checkout:

```sh
python -m pip install -e .
```

See [installation](../getting-started/installation.md) for prerequisites. v3 is a preview branch feature; these examples do not imply that a released package contains it. Obtain an approved staging origin and gateway credentials, then set:

```sh
export AGORA_APP_ID='YOUR_APP_ID'
export AGORA_APP_CERTIFICATE='YOUR_APP_CERTIFICATE'
export AGORA_AGENTS_V3_BASE_URL='https://YOUR_STAGING_HOST'
export AGORA_V3_GATEWAY_SECRET='YOUR_GATEWAY_SECRET'
export AGORA_V3_CONSUMER_USERNAME='YOUR_CONSUMER_USERNAME'
export OPENAI_API_KEY='YOUR_OPENAI_KEY'
export DEEPGRAM_API_KEY='YOUR_DEEPGRAM_KEY'
```

The base URL is an HTTP(S) **origin**, without a project path, query or fragment. The SDK appends `/conversational-ai/v3/projects/{appid}`. `V3Options(base_url=...)` overrides the environment variable; headers apply only to v3. Existing client authentication still supplies the Authorization header. Production paths, regional availability and Basic-auth acceptance remain unconfirmed; use the supplied staging configuration for evaluation.

This complete cascaded configuration stores one project secret set, then deploys a stored agent. Set creation is a one-time provisioning step; subsequent runs can update secrets separately using the [secret methods](../reference/v3.md#secrets-eight-operations).

```python
import os
from agora_agent import (
    Agent, Agora, Area, DeepgramSTT, OpenAI, OpenAITTS, V3Options, secret_ref,
)

client = Agora(
    area=Area.US,
    app_id=os.environ["AGORA_APP_ID"],
    app_certificate=os.environ["AGORA_APP_CERTIFICATE"],
    v3=V3Options(headers={
        "X-Studio-V2-Gateway-Secret": os.environ["AGORA_V3_GATEWAY_SECRET"],
        "X-Consumer-Username": os.environ["AGORA_V3_CONSUMER_USERNAME"],
    }),
)
client.v3.secrets.create(
    name="support",
    secrets={"openai": os.environ["OPENAI_API_KEY"], "deepgram": os.environ["DEEPGRAM_API_KEY"]},
    idempotency_key="support-secrets-initial-provisioning",
)
agent = (
    Agent(client=client)
    .with_stt(DeepgramSTT(api_key=secret_ref("support", "deepgram"), model="nova-3"))
    .with_llm(OpenAI(
        api_key=secret_ref("support", "openai"), model="gpt-4o-mini",
        base_url="https://api.openai.com/v1/chat/completions",
        system_messages=[{"role": "system", "content": "Help callers briefly."}],
        greeting_message="Hello. How can I help?",
    ))
    .with_tts(OpenAITTS(
        api_key=secret_ref("support", "openai"), model="tts-1", voice="alloy",
        base_url="https://api.openai.com/v1/audio/speech",
    ))
    .with_variable("customer_name", type="str", required=True)
    .with_variable("resolved", type="bool", extract=True, description="Was the issue resolved?")
)
support = agent.deploy(name="Support")
print(support.id, support.etag)  # Persist the ID for the next deploy.
```

The example endpoints are existing vendor configuration, not additional v3 defaults. Use backend-approved provider endpoints/models for your staging deployment. Managed mode may also require an explicit provider URL on staging.

## Redeploy, load and delete

Pass the saved ID to update the same stored agent. Omitting `agent_id` always creates another configuration; matching names do not provide upsert or deduplication.

```python
from agora_agent import DeployedAgent

support = agent.deploy(name="Support", agent_id=support.id)
loaded = DeployedAgent.get(client, support.id)
print(loaded.id, loaded.name, loaded.etag, loaded.data)
# loaded.delete()  # Delete the stored configuration when it is no longer needed.
```

Redeploy GETs the latest ETag, then sends one conditional PATCH. It recursively nulls stale readable mutable fields, including nested provider params; IDs, timestamps and resolved credential metadata are excluded. Credentials come from the builder. Switching an existing module to managed mode explicitly nulls `api_key`.

This is a merge patch rather than a guaranteed replacement. Write-only keys and headers cannot be reconstructed from GET, and omitted hidden values remain subject to backend merge semantics. Keep intended credentials in the builder or use a targeted [low-level update](../reference/v3.md#agents-five-operations) when retaining existing hidden credentials matters. Agent deploy conflicts are surfaced without retry.

## Assign and discover inbound numbers

Create the SIP number in the same project before assignment, either through your provisioning workflow or `client.v3.numbers.create(number=..., sip_trunk={"hostname": ...})`. Number registration details and unsupported staging options are in the [reference](../reference/v3.md#numbers-five-operations).

```python
support.assign_number("+12025550123", max_call_duration_seconds=900,
                      max_silence_duration_ms=30000)
assigned = support.list_numbers()
for number in assigned:
    print(number["number_id"], number["number"])
support.unassign_number("+12025550123")
```

Assignment accepts an E.164 string, a number ID (without assuming UUID format), or a v3 number dictionary with `number_id`. A leading `+` selects E.164 lookup. The lookup scans project number pages with `limit=100` and normalizes spaces, parentheses, periods and hyphens. Unknown numbers raise `NumberNotFoundError` naming the project.

An ID assignment costs one GET for its ETag and one PATCH of `inbound.agent`; E.164 resolution adds list requests. A 412 triggers one fresh GET and one retry, adding two requests. Policy options map directly to `inbound.call_policy` and must be positive integers. Unassignment sets `inbound.agent` to JSON null.

`list_numbers()` scans **every project number page** at 100 items per request, filters `inbound.agent == support.id`, and returns a list of matching wire dictionaries. It performs no per-number GETs. A scan costs one request per page and is not an atomic snapshot of concurrent assignment changes.

There is no reliable stored-agent session filter: the current session summary lacks `agent_id`, and detail provides only a potentially nonunique `agent_name`. Use project-wide `client.v3.sessions.list(...)` / `.get(...)`; no guessed name-based `list_sessions()` helper is provided.

## Raw responses, pagination and conflicts

Normal methods return typed wire dictionaries from `agora_agent.v3.types`. The same methods under `.with_raw_response` return `.data`, `.headers`, `.etag`, `.status_code` and the underlying httpx `.response`.

```python
from agora_agent import PreconditionFailedError

response = client.v3.agents.with_raw_response.get(agent_id=support.id)
if response.etag is None:
    raise RuntimeError("Server omitted ETag; refusing an unguarded update")
try:
    client.v3.agents.update(agent_id=support.id, if_match=response.etag,
                            instructions="Updated support instructions")
except PreconditionFailedError as error:
    latest = error.latest()  # GET current data; does not repeat the write.
    print(error.status_code, error.headers.get("agora-request-id"), latest)

page = client.v3.sessions.list(limit=20, status="RUNNING", channel="room")
if page["has_more"]:
    next_page = client.v3.sessions.list(limit=20, status="RUNNING", channel="room",
                                       cursor=page["next_cursor"])
for number in client.v3.numbers.iter_all(limit=100):
    print(number["number_id"])
```

`iter_pages()` yields complete pages with `data.count`, `data.list`, `has_more` and `next_cursor`; `iter_all()` yields their items. Both reject missing or repeated continuation cursors. Cursor state is opaque: keep the same filters on subsequent requests. `list()` itself fetches one page. Session reads default to running sessions at the backend; request a historical filter such as `status="STOPPED,FAILED"` when needed. Iteration preserves the chosen filter rather than implicitly scanning every status.

A 412 raises `PreconditionFailedError`, a subclass of `ApiError`; other HTTP failures raise `ApiError`. Both retain status, response headers and body (including server `detail` / `reason`). `latest()` reloads the affected resource; a secret-key conflict reloads its set. It returns normal parsed data rather than a raw response. To obtain the new ETag for a deliberate retry, GET through `.with_raw_response` again.

## Async applications

Use `AsyncAgora`, the same low-level keyword arguments, and `await agent.deploy_async(...)`. The deployed handle is `AsyncDeployedAgent`; `get`, `delete`, `assign_number`, `unassign_number` and `list_numbers` are awaitable. `with_variable` and the vendor builders stay local and synchronous.

```python
import os
from agora_agent import Agent, AsyncAgora, AsyncDeployedAgent, Area, V3Options

async def inspect_stored_agent(agent_id: str):
    client = AsyncAgora(
        area=Area.US, app_id=os.environ["AGORA_APP_ID"],
        app_certificate=os.environ["AGORA_APP_CERTIFICATE"],
        v3=V3Options(headers={
            "X-Studio-V2-Gateway-Secret": os.environ["AGORA_V3_GATEWAY_SECRET"],
            "X-Consumer-Username": os.environ["AGORA_V3_CONSUMER_USERNAME"],
        }),
    )
    support = await AsyncDeployedAgent.get(client, agent_id)
    numbers = await support.list_numbers()
    async for page in client.v3.sessions.iter_pages(limit=20, status="RUNNING"):
        print(page["data"]["count"])
    return support, numbers

# With a fully configured Agent bound to AsyncAgora:
# support = await agent.deploy_async(name="Support", agent_id=saved_id)
# await support.assign_number("+12025550123")
# await support.unassign_number("+12025550123")
# await support.delete()
```

Use `await error.latest()` after an async 412. `deploy()` requires an `Agora` client; `deploy_async()` requires `AsyncAgora`. Passing the other client kind raises `TypeError` before deployment.

## Compatibility and backend limits

Existing v2 resources and `Agent.create_session()` behavior remain available. A v3 `secret_ref` cannot be sent as a v2 API key: `create_session`, `create_async_session` and `to_properties` reject it with `SecretRefNotSupportedError("secret_ref requires deploy()")`. Build a separate configuration with inline credentials for an existing v2 session. Variables configure stored-agent definitions; this phase does not add session-start variable values or an AgentKit extraction-results helper.

`with_variable` returns a new builder. Names match `^[a-z][a-z0-9_]{0,63}$`; supported types are `str`, `int`, `float`, `bool`, `date`, `datetime`; `extract=True` requires a nonempty description. `secret_ref(set_name, key)` validates 1–64 letters, digits, underscores or hyphens per component and returns `$secrets.<set>.<key>`. It creates a reference, not a secret value.

The central mapper reuses existing vendor configs. Vendor instructions and greetings take precedence over deprecated Agent fields; realtime `params.instructions` moves to top-level instructions, and supported vendor messages move to top-level `messages`. Provider API keys become `{mode: "byok", api_key: ...}`, while absent keys select `managed`. Realtime Agora, server and semantic VAD settings, supported text/audio greetings, silence settings and filler words are converted to v3 shapes. Greeting playback modes `single_every` and `single_first` map to `each_join` and `first_join`; other v2 modes without a v3 equivalent are rejected. A managed MiniMax TTS preset model is retained in `tts.params.model`.

| Constraint | Current behavior |
|---|---|
| Builder fields without stored-agent equivalents | One `UnsupportedFieldError.fields` list before network access: SAL, advanced features, geofence, labels, RTC, pipeline IDs, parameters other than `silence_config` |
| Value-valued `template_variables` | Rejected; use `with_variable` definitions |
| Multipart AWS/Vertex credentials, removed avatar vendors, numeric v2 TTS `skip_patterns`, unmappable deprecated turn/greeting settings | Rejected rather than guessed or silently omitted |
| Tools/MCP/custom provider destinations | Deferred backend support; the server may reject otherwise typed fields |
| Number `end_call`, `transfer`, `allowed_ips`, SIP-password secret references | Currently rejected or unsupported on staging |
| Writes and retry options | All low-level writes disable automatic retries, even when `max_retries` is requested; assignment has only its explicit one-conflict retry |
| Agent and number creation | Agent POST has no idempotency key; numbers currently ignore their declared key. An uncertain create outcome requires inspection before manual retry |
| CN and production | AgentKit CN deployment is refused; production path, regional coverage and Basic-auth support remain unconfirmed |
| Session writes, outbound calling, AgentKit analysis and campaigns | No implementation until schemas are published |

The adapter shares the existing client's HTTP transport, authentication and current regional-pool origin. The staging override applies only to v3. These docs and offline tests do not establish live backend availability.

## Maintainer provenance

The v3 low-level methods and TypedDict wire schemas were generated locally from the staging OpenAPI reviewed for this preview. They are protected custom code under `src/agora_agent/v3`, with a handwritten shared-transport adapter and AgentKit mapping. **They are not output from the repository's Fern generation pipeline.** This Python checkout does not contain the local generator or a vendored OpenAPI snapshot, so a reproducible generation workflow is not currently checked in.

See [the v3 source](../../src/agora_agent/v3/client.py), [wire schemas](../../src/agora_agent/v3/types.py), [AgentKit mapping](../../src/agora_agent/agentkit/v3.py), and [offline contract tests](../../tests/custom/test_v3_preview.py). Preserve `.fernignore` protection when integrating a future canonical Fern namespace.
