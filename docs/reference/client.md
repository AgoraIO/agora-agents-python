---
sidebar_position: 1
title: Agora / AsyncAgora Client
description: Constructor options and public methods for the Agora Python client.
---

# Agora / AsyncAgora Client

**Import:** `from agora_agent import Agora, AsyncAgora, AgentClient, AsyncAgentClient`

`AgentClient` and `AsyncAgentClient` are aliases for `Agora` and `AsyncAgora`.

## `Agora` Constructor

<!-- snippet: fragment -->
```python
from agora_agent import Agora, Area

client = Agora(
    area=Area.US,
    app_id='your-app-id',
    app_certificate='your-app-certificate',
)
```

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `area` | `Area` | Yes | — | Region for API routing (`Area.US`, `Area.EU`, `Area.AP`, `Area.CN`) |
| `app_id` | `str` | Yes | — | Agora App ID (app-credentials mode) |
| `app_certificate` | `str` | Yes | — | Agora App Certificate (app-credentials mode) |
| `customer_id` | `str` | Yes* | — | Customer ID (Basic Auth mode) |
| `customer_secret` | `str` | Yes* | — | Customer Secret (Basic Auth mode) |
| `auth_token` | `str` | No | — | Pre-built raw REST token; SDK sets `Authorization: agora token=<auth_token>` |
| `headers` | `Dict[str, str]` | No | `None` | Additional headers sent with every request |
| `timeout` | `float` | No | `60` | Request timeout in seconds |
| `follow_redirects` | `bool` | No | `True` | Whether to follow HTTP redirects |
| `httpx_client` | `httpx.Client` | No | `None` | Custom httpx client instance |
| `debug` | `bool` | No | `False` | Log HTTP requests and responses when `True` |
| `v3` | `V3Options` | No | `None` | Preview-only origin and headers; see the [v3 reference](./v3.md) |

*`app_id` and `app_certificate` are required constructor arguments in every auth mode; the certificate is used for automatic app-credential auth. Supply `customer_id` and `customer_secret` together to select Basic auth. `auth_token` is mutually exclusive with that pair.

When `area=Area.CN`, the constructor returns a `CNAgora` instance; global areas return `GlobalAgoraClient`. Both are subclasses of `Agora` and behave the same at runtime.

## `AsyncAgora` Constructor

Identical to `Agora` except:

| Parameter | Difference |
|---|---|
| `httpx_client` | Accepts `httpx.AsyncClient` instead of `httpx.Client` |

`AsyncAgora(area=Area.CN, ...)` returns `CNAsyncAgora`; global areas return `GlobalAsyncAgoraClient`.

<!-- snippet: fragment -->
```python
from agora_agent import AsyncAgora, Area

client = AsyncAgora(
    area=Area.US,
    app_id='your-app-id',
    app_certificate='your-app-certificate',
)
```

## Properties

| Property | Type | Description |
|---|---|---|
| `client.area` | `Area` | Configured API area |
| `client.area_scope` | `Literal["cn", "global"]` | Vendor scope implied by `area` (`"cn"` for `Area.CN`, otherwise `"global"`) |
| `client.app_id` | `str` | Agora App ID |
| `client.app_certificate` | `str` | Agora App Certificate |
| `client.auth_mode` | `Literal["app-credentials", "basic", "token"]` | Active authentication mode |
| `client.pool` | `Pool` | Domain pool for regional URL cycling |

## Public Methods

### `stop_agent(agent_id: str) -> None`

Stop a running agent by ID without holding an `AgentSession` reference. Idempotent when the agent has already stopped (404 is treated as success).

<!-- snippet: fragment -->
```python
client.stop_agent(agent_id)
```

- **`AsyncAgora`:** `await client.stop_agent(agent_id)`

### `validate_agent_region(agent) -> None`

No-op. The SDK does not enforce area and vendor compatibility.

### `next_region()`

Cycle to the next region prefix in the pool. Call this when a request fails to try a different endpoint.

<!-- snippet: fragment -->
```python
client.next_region()
```

- **Returns:** `None`
- **Sync on both `Agora` and `AsyncAgora`**

### `select_best_domain()`

Trigger DNS-based domain selection to find the fastest-responding domain suffix.

<!-- snippet: fragment -->
```python
# Sync (Agora)
client.select_best_domain()

# Async (AsyncAgora) — MUST use await
await client.select_best_domain()
```

- **Returns:** `None`
- **`Agora`:** regular method
- **`AsyncAgora`:** coroutine — requires `await`
- Results are cached for 30 seconds

### `get_current_url()`

Get the current base URL being used for requests.

<!-- snippet: fragment -->
```python
url = client.get_current_url()
# "https://api-us-west-1.agora.io/api/conversational-ai-agent"
```

- **Returns:** `str`
- **Sync on both `Agora` and `AsyncAgora`**

## Sub-Clients (Fern-Generated)

Both `Agora` and `AsyncAgora` expose Fern-generated sub-clients as properties:

| Property | Type (sync / async) | Description |
|---|---|---|
| `client.agents` | `AgentsClient` / `AsyncAgentsClient` | Start, stop, list, update agents |
| `client.telephony` | `TelephonyClient` / `AsyncTelephonyClient` | Telephony operations |
| `client.phone_numbers` | `PhoneNumbersClient` / `AsyncPhoneNumbersClient` | Phone number management |

These are lazily initialized on first access. For most use cases, prefer the [AgentSession](./session.md) API instead of calling `client.agents` directly.

## v3 preview sub-client

`client.v3` / `async_client.v3` provide stored agents, secrets, numbers and project-wide session reads with the owning client's transport/auth. This protected custom adapter is separate from the Fern-generated v2 resources above. See [v3 workflows](../guides/v3-api-preview.md) for staging configuration and [all 20 operations](./v3.md) for conditional headers, typed dictionary responses and cursor iterators. Preview availability requires this checkout, not an assumed PyPI release.

## Project provisioning

Use `client.secrets` and `client.numbers` for project provisioning (await methods with `AsyncAgora`). They share the underlying resources and transport with the advanced namespace. The [agent workflow](../guides/agent-workflow.md) combines these with `Agent.save()` and saved-handle updates. Existing `client.agents` continues to manage running sessions, so stored-agent CRUD stays available through `SavedAgent` or advanced `client.v3.agents`.
