# v3 stored-agent preview (P1)

The package version continues to describe SDK compatibility. Existing v2 resources and `Agent.create_session()` remain available. The additive `client.v3` namespace covers all 20 published staging operations: agents and numbers CRUD, secrets CRUD plus individual key writes/deletes, and session list/get. Session writes, outbound calls, analysis helpers and campaigns await backend schemas and are not implemented.

```python
from agora_agent import Agora, Area, Agent, DeepgramSTT, OpenAI, V3Options, secret_ref

client = Agora(
    area=Area.US, app_id="APP_ID", app_certificate="APP_CERTIFICATE",
    # Staging origin only. Supply the gateway's required headers explicitly.
    v3=V3Options(base_url="https://YOUR_STAGING_HOST", headers={
        "X-Studio-V2-Gateway-Secret": "GATEWAY_SECRET",
        "X-Consumer-Username": "CONSUMER",
    }),
)

client.v3.secrets.create(name="prod", secrets={"openai": "OPENAI_KEY", "deepgram": "DEEPGRAM_KEY"},
                         idempotency_key="initial-prod-secrets")
agent = (Agent(client=client)
    .with_stt(DeepgramSTT(api_key=secret_ref("prod", "deepgram"), model="nova-3"))
    .with_llm(OpenAI(api_key=secret_ref("prod", "openai"), model="gpt-4o-mini",
                    base_url="https://api.openai.com/v1/chat/completions",
                    system_messages=[{"role": "system", "content": "Help callers briefly."}]))
    .with_variable("resolved", type="bool", extract=True, description="Was the issue resolved?"))
# Add your usual .with_tts(...) configuration for a complete voice pipeline.
support = agent.deploy(name="Support")
print(support.id, support.etag)
support.assign_number("+12025550123", max_call_duration_seconds=900)
support.unassign_number("+12025550123")

# Save the ID; a later deploy to that ID GETs its ETag then PATCHes.
support = agent.deploy(name="Support", agent_id=support.id)
loaded = type(support).get(client, support.id)
# loaded.delete() deletes the stored configuration.
```

Numbers must already exist in the same project. `assign_number` accepts an E.164 string, a number ID (without assuming UUID format), or a v3 number dictionary with `number_id`. E.164 lookup scans cursor pages at 100 items per request and compares formatting-normalized numbers. Assignment GETs the number for its ETag, then PATCHes `inbound.agent`; a 412 triggers one fresh GET and one retry. An ID usually costs two requests, E.164 adds list requests, and a conflict adds two requests. `max_silence_duration_ms` is the other supported call-policy option. Unknown numbers raise `NumberNotFoundError` naming the project.

## Low-level access, headers and pagination

Every resource has explicit snake_case methods. `appid` defaults to the owning client's `app_id` and may be overridden per call. Agents, numbers and sessions use `agent_id`, `number_id` and `agent_session_id` respectively. Secret sets use `name`, and individual key operations also take `key`.

```python
created = client.v3.agents.create(agent_name="Minimal stored agent")
response = client.v3.agents.with_raw_response.get(agent_id=created["agent_id"])
updated = client.v3.agents.update(agent_id=created["agent_id"], if_match=response.etag,
                                  instructions="New instructions")
print(response.headers.get("Agora-Request-Id"), response.status_code)

page = client.v3.sessions.list(limit=20, status="ACTIVE", channel="room",
                              started_after=100, started_before=200)
next_page = client.v3.sessions.list(limit=20, cursor=page["next_cursor"]) if page["has_more"] else None
for number in client.v3.numbers.iter_all(limit=100):
    print(number["number_id"])
# iter_pages() yields complete pages, including count/has_more/next_cursor.

client.v3.secrets.set_key(name="prod", key="new_key", value="VALUE", if_none_match="*")
```

Responses are typed wire dictionaries defined in `agora_agent.v3.types`. Raw responses expose `.data`, `.headers`, `.etag`, `.status_code` and the underlying httpx `.response`. They preserve server pagination metadata and error `{detail, reason}` bodies. `PreconditionFailedError` is an `ApiError` with status/body/headers and `latest()` to GET the current resource (a secret key conflict reloads its set). `latest()` does not repeat the write. Required `If-Match` values are explicit arguments. Omitted optional body fields remain absent; explicit `None` survives as JSON null. PATCH uses the staging contract's `application/json` content type.

## Async

Bind an `AsyncAgora` client, use `await agent.deploy_async(...)`, and receive an `AsyncDeployedAgent`. Its `get`, `delete`, `assign_number`, and `unassign_number` methods are awaitable. Low-level methods have identical arguments under `async_client.v3`, including `.with_raw_response`. Use `async for` with `.iter_pages()` / `.iter_all()`, and `await error.latest()` after an async conflict. `deploy()` requires `Agora`; `deploy_async()` requires `AsyncAgora`.

## Mapping and preview limitations

`with_variable` is pure and immutable. Variable names match `^[a-z][a-z0-9_]{0,63}$`; types are `str`, `int`, `float`, `bool`, `date`, `datetime`; extraction requires a nonempty description. Existing builder/vendor configuration maps centrally to v3 provider modules, instructions/messages, text/audio greetings, turn detection/interruption, silence settings and filler words. Vendor instructions/greetings take precedence over deprecated Agent fields. API keys become `credential: {mode: "byok", api_key: ...}`; absent keys become `managed`. Provider URLs already serialized by existing vendor classes are preserved, and no additional endpoint defaults are invented.

Strict mapping raises one `UnsupportedFieldError` listing unmappable fields before any request. These include SAL, advanced features, geofence, labels, RTC configuration, pipeline IDs, and parameters other than `silence_config`. Value-valued `template_variables` cannot be converted into variable definitions; use `with_variable`. Multipart AWS/Vertex credentials, removed avatar vendors, and numeric v2 TTS `skip_patterns` are rejected because no lossless mapping is confirmed. Unsupported deprecated turn settings and greeting policies are also reported rather than silently dropped. Secret references on `create_session`, `create_async_session`, or `to_properties` raise `SecretRefNotSupportedError` before a v2 network request.

Redeploy recursively nulls stale **readable** mutable configuration fields, including nested provider params, because JSON merge patch does not imply nested replacement. IDs, timestamps, and resolved credential metadata are never echoed. Credentials come from the builder; switching to managed explicitly nulls `api_key`. Write-only keys/headers cannot be reconstructed from GET, so omitted hidden values and mode-switch behavior remain subject to backend merge semantics. Deploy is an ETag-guarded patch, not a guaranteed PUT/replace. Use the low-level raw resource to make targeted patches when retaining hidden credentials matters. Agent conflicts are not retried. All low-level writes disable automatic HTTP retries, even if `max_retries` was requested; staging agent POST has no idempotency protection and numbers currently ignore their declared key. A failed create may have succeeded remotely: inspect resources before manually retrying.

The shared existing HTTP transport, auth and regional pool are reused; v3 overrides only its origin and headers. `AGORA_AGENTS_V3_BASE_URL` provides the same origin override as `V3Options.base_url` (the explicit option wins). The request path is `/conversational-ai/v3/projects/{appid}`. Production origins/path, all regional availability and Basic-auth support remain unconfirmed. CN deployment is deliberately refused. Staging may require a URL even with managed credentials; supply a backend-approved provider URL through existing vendor configuration. Deferred tools/MCP/custom destinations may be rejected by the server. Number `end_call`, `transfer`, `allowed_ips` and SIP secret references are also currently unsupported by staging. No live staging write was performed for this preview.
