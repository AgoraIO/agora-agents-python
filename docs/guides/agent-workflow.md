# One agent configuration, two explicit outcomes

Configure an immutable `Agent` with providers once. Create a session when you want a running conversation, or save the configuration when you want a persistent agent and inbound-number assignments. Async clients follow the same flow with awaitable network methods.

Saving and project secrets/numbers require this preview checkout, installed with `python -m pip install -e .` from the repository root. These features are not implied by a published PyPI version. Use token authentication with the public preview origin as described in the [transport setup](./v3-api-preview.md#quick-start-with-staging).

```python
import os
from agora_agent import Agent, DeepgramSTT, OpenAI, OpenAITTS, SavedAgent, secret_ref

# `client` is the Agora instance configured once in the linked transport setup.
# Provision once; future runs reuse the stored secret set.
client.secrets.create(name="support", secrets={"deepgram": os.environ["DEEPGRAM_API_KEY"], "openai": os.environ["OPENAI_API_KEY"]})
agent = (
    Agent(client=client)
    .with_stt(DeepgramSTT(api_key=secret_ref("support", "deepgram"), model="nova-3"))
    .with_llm(OpenAI(
        api_key=secret_ref("support", "openai"), model="gpt-4o-mini",
        base_url="https://api.openai.com/v1/chat/completions",
        system_messages=[{"role": "system", "content": "Help callers briefly."}],
    ))
    .with_tts(OpenAITTS(
        api_key=secret_ref("support", "openai"), model="tts-1", voice="alloy",
        base_url="https://api.openai.com/v1/audio/speech",
    ))
)

# Choose a running conversation. Constructing the handle is local; start() calls the service.
session = agent.create_session(channel="room", agent_uid="1", remote_uids=["2"])
session_id = session.start()
# session.stop()

# Or explicitly persist the same configuration. Saving does not start a session.
saved = agent.save(name="Support")
print(saved.id)  # Store the ID so another process can load the handle.
saved = saved.update(agent.with_greeting("Hello. How can I help?"))
loaded = SavedAgent.get(client, saved.id)
# loaded.delete()
```

`save()` creates a configuration. `saved.update(config)` changes that saved ID and preserves its name; `name="New name"` optionally renames it. The configuration must use the same client object as the handle. Both paths return a fresh saved handle and leave the local builder unchanged. `save(agent_id=...)` remains an advanced alternative when working directly with persisted IDs.

## Provision secrets and numbers

Use `client.secrets` for project secret sets and `client.numbers` to register a SIP number. Both have synchronous and async methods with the same arguments.

```python
from agora_agent import secret_ref

client.secrets.create(name="support", secrets={"openai": os.environ["OPENAI_API_KEY"]})
number = client.numbers.create(
    number="+12025550123",
    sip_trunk={"hostname": "YOUR_APPROVED_SIP_HOST", "transport": "tls", "port": 5061},
)
saved.assign_number(number, max_call_duration_seconds=900)
for assigned in saved.list_numbers():
    print(assigned["number_id"], assigned["number"])
saved.unassign_number(number)

# Reference the stored secret when saving provider configuration.
referenced = agent.with_llm(OpenAI(
    api_key=secret_ref("support", "openai"), model="gpt-4o-mini",
    base_url="https://api.openai.com/v1/chat/completions",
)).with_variable("resolved", type="bool", extract=True, description="Was the issue resolved?")
saved = saved.update(referenced)
```

Saving BYOK configuration requires explicit secret references for every provider credential. Ephemeral sessions can also use inline credentials; saving those configurations fails locally and never creates secrets automatically. Omit `agent_uid` on the new transport to request server assignment; one nonzero subscriber is still required.

Secret creation and number registration are provisioning operations, not steps to repeat for every conversation. Save IDs and use conditional updates for existing resources. `list_numbers()` scans all project pages and filters assignments locally; it costs one request per page, with no individual number GETs.

The same builder can start directly with secret references and variable definitions: the SDK sends an ephemeral inline agent, without saving it or reading secret values back. Saved handles start by their stored ID. Neither flow implicitly caches or reverses write-only credentials.

```python
session = saved.create_session(
    channel="room", agent_uid="1", remote_uids=["2"],
    idle_timeout=60, max_duration=120, idempotency_key="support-call",
    labels={"owner": "support"},
)
session_id = session.start()
info = session.get_info()
session.stop()

# Secret references and variables use the same session interface.
ephemeral = referenced.create_session(channel="room", agent_uid="1", remote_uids=["2"])
ephemeral.start()
ephemeral.stop()
```

`idle_timeout` and `max_duration` are seconds, converted to integer milliseconds. `values`, `labels`, `token` (RTC only), `encryption`, `audio_scenario`, `graceful_stop`, `data_policy`, `geofence` and `idempotency_key` work for both saved and ephemeral sessions. Exactly one nonzero subscriber is required; wildcard subscriptions are unsupported. Agent UID `0` can request automatic assignment. Agent/subscriber UID types must match. The agreed contract permits string UIDs; numeric-only validation may remain during backend rollout.

`name` stays a local label for these sessions; it is never sent as `client_reference`. The obsolete `client_reference` option raises an error. Legacy inline sessions retain their existing name/transport behavior. Preset, pipeline-ID, expiry and explicit string-UID switches are rejected on saved/ephemeral sessions.

```python
session = saved.create_session(
    channel="room", agent_uid="1002", remote_uids=["1001"],
    values={"customer_name": "Ada"}, labels={"team": "support"},
    graceful_stop={"enabled": True, "timeout_ms": 10000},
    data_policy={"retention": "none"}, idempotency_key="support-call-4821",
)
```

Retention `none` disables retained conversation content and post-call extraction; the session resource and operational metadata can remain visible independently. Builder `parameters.opt_out` maps to session retention; `farewell_config.graceful_enabled` / `graceful_timeout_seconds` map to graceful stop (seconds × 1000). These are session options, not persisted agent fields; pass them when starting a saved agent. Graceful stop does not create a farewell message.

Start, stop, `get_info` and a limited `update` are available for new session IDs; say/interrupt/think/history/turn helpers fail locally. `session.update({"token": "renewed", "llm": {"params": {"temperature": 0.2}}})` updates token and replaces active provider params. `messages` (or `llm.system_messages`) updates conversation messages on either transport; supplying both spellings is rejected. Realtime uses `mllm.params`. Credentials, URLs and other fields are rejected. Start accepts corrected 200/`create_ts`/uppercase statuses and rollout 201/`created_at`/lowercase; low-level data normalizes to uppercase and `create_ts`. Handle states remain lowercase (`FAILED` becomes `error`). STARTING sessions can be stopped or read. Stop failures propagate: `404 TaskNotFound` is not success; `409 TaskNotRunning` records stopped and `409 TaskConflict` records stopping, while preserving the error for the caller.

## Async applications

Bind the builder to `AsyncAgora`, keep the same provider methods, and use:

```python
async def use_async_agent(agent):
    session = agent.create_async_session(channel="room", agent_uid="1", remote_uids=["2"])
    await session.start()
    saved = await agent.save_async(name="Support")
    saved = await saved.update(agent.with_greeting("Hello"))
    numbers = await saved.list_numbers()
    return session, saved, numbers
```

Use `await AsyncSavedAgent.get(client, saved_id)` to load another handle, and await secret/number provisioning, assignment and deletion. `with_variable` stays a local synchronous builder operation.

## Advanced transport and compatibility

Application code does not select a REST version. Ordinary inline configurations retain the established session transport. Configurations with secret references or variable definitions, or new session options such as `values`, `labels` or `max_duration`, use the documented ephemeral session transport. Saved handles use the documented start-by-ID transport. See [transport behavior and limits](./v3-api-preview.md) and the [complete low-level reference](../reference/v3.md) for ETags, raw headers, cursor pagination, strict mapping, project session reads, staging overrides and deferred features.

`deploy()` / `deploy_async()` remain compatibility wrappers for `save()` / `save_async()`. `DeployedAgent` is exactly `SavedAgent`; the async handle names are likewise identical aliases. Advanced `client.v3` resources remain available, including session start/stop and project queries; the existing `client.agents` running-session resource retains its behavior.


## Campaign provisioning

`client.campaigns` (or async `client.campaigns`) exposes the eight documented operations. Campaign creation and pause/resume/cancel accept `idempotency_key`; update requires `if_match`. Use raw GET to obtain the current ETag. Contact lists contain 1–5,000 entries and cannot be edited after creation. Retry pacing fields remain unconfirmed; the SDK implements no calling/retry algorithm. No contact-result, upload, event or webhook endpoints are invented. See the [campaign reference](../reference/v3.md#campaigns-eight-operations).

RTC geofence uses `area` (`global`, `north_america`, `europe`, `asia`, `india`, `japan`) and optional `exclude_area`, allowed only with global area. An existing builder geofence maps into new-session transport (uppercase legacy area names normalize to lowercase). This agreed correction still depends on backend rollout. Geofence is not saved-agent configuration.
