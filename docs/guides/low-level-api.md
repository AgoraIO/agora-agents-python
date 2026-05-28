---
sidebar_position: 10
title: Low-Level API
description: Use generated clients for escape-hatch APIs while keeping agent sessions on AgentKit.
---

# Low-Level API

Use the `Agent` builder and `AgentSession` for conversational agent starts. That path generates ConvoAI REST auth and RTC join tokens from `app_id` and `app_certificate`, so application code does not need prebuilt REST tokens, RTC tokens, Customer ID, or Customer Secret.

Generated clients are still available for API surface that AgentKit does not wrap yet, such as telephony and phone-number management.

## Client setup

```python
from agora_agent import Agora, Area

client = Agora(
    area=Area.US,
    app_id="your-app-id",
    app_certificate="your-app-certificate",
)
```

## Raw telephony and phone-number APIs

AgentKit focuses on realtime agent session helpers. Use generated clients for operational APIs:

- `client.telephony` for call status and hangup operations
- `client.phone_numbers` for phone-number list, create, retrieve, update, and delete operations

```python
calls = client.telephony.list(
    appid=client.app_id,
    type="sip",
)

for call in calls:
    print(call.id, call.state)
```

## Direct agent APIs

`client.agents` exposes the generated REST surface for advanced integrations. Prefer `agent.create_session(...).start()` for new session starts because it handles auth, token generation, vendor serialization, lifecycle state, and avatar enrichment.

If you need an endpoint that is not wrapped by `AgentSession`, use `session.raw` after creating the session:

```python
info = session.raw.get(
    appid=session.app_id,
    agent_id=session.id,
)
```

You must pass `appid` and `agent_id` manually when using generated raw methods.
