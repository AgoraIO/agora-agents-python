# One agent configuration, two explicit outcomes

Configure an immutable `Agent` with providers once. Create a session when you want a running conversation, or save the configuration when you want a persistent agent and inbound-number assignments. Async clients follow the same flow with awaitable network methods.

Saving and project secrets/numbers require this preview checkout, installed with `python -m pip install -e .` from the repository root. These features are not implied by a published PyPI version. Configure the approved staging origin and gateway headers as described in the [transport setup](./v3-api-preview.md#quick-start-with-staging).

```python
import os
from agora_agent import Agent, DeepgramSTT, OpenAI, OpenAITTS, SavedAgent

# `client` is the Agora instance configured once in the linked transport setup.
agent = (
    Agent(client=client)
    .with_stt(DeepgramSTT(api_key=os.environ["DEEPGRAM_API_KEY"], model="nova-3"))
    .with_llm(OpenAI(
        api_key=os.environ["OPENAI_API_KEY"], model="gpt-4o-mini",
        base_url="https://api.openai.com/v1/chat/completions",
        system_messages=[{"role": "system", "content": "Help callers briefly."}],
    ))
    .with_tts(OpenAITTS(
        api_key=os.environ["OPENAI_API_KEY"], model="tts-1", voice="alloy",
        base_url="https://api.openai.com/v1/audio/speech",
    ))
)

# Choose a running conversation. Constructing the handle is local; start() calls the service.
session = agent.create_session(channel="room", agent_uid="1", remote_uids=["*"])
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

Secret creation and number registration are provisioning operations, not steps to repeat for every conversation. Save IDs and use conditional updates for existing resources. `list_numbers()` scans all project pages and filters assignments locally; it costs one request per page, with no individual number GETs.

Secret references remain server-side persistence inputs. A current session must use inline or managed credentials from its original builder; passing a literal secret reference to session start is rejected before the request. No secret values are recoverable through GET, and the SDK does not implicitly cache or reverse saved credentials. A saved handle does not yet start sessions: the new start API is expected to accept `agent_id`, but its endpoint and complete request contract are still pending.

## Async applications

Bind the builder to `AsyncAgora`, keep the same provider methods, and use:

```python
async def use_async_agent(agent):
    session = agent.create_async_session(channel="room", agent_uid="1", remote_uids=["*"])
    await session.start()
    saved = await agent.save_async(name="Support")
    saved = await saved.update(agent.with_greeting("Hello"))
    numbers = await saved.list_numbers()
    return session, saved, numbers
```

Use `await AsyncSavedAgent.get(client, saved_id)` to load another handle, and await secret/number provisioning, assignment and deletion. `with_variable` stays a local synchronous builder operation.

## Advanced transport and compatibility

Application code does not select a REST version. The current transport uses the established session API for running conversations and the stored-agent preview API for persistence/provisioning. See [transport behavior and limits](./v3-api-preview.md) and the [complete low-level reference](../reference/v3.md) for ETags, raw headers, cursor pagination, strict mapping, project session reads, staging overrides and deferred features.

`deploy()` / `deploy_async()` remain compatibility wrappers for `save()` / `save_async()`. `DeployedAgent` is exactly `SavedAgent`; the async handle names are likewise identical aliases. Advanced `client.v3` resources remain available, including read-only project session queries; the existing `client.agents` running-session resource retains its behavior.
