---
sidebar_position: 1
title: Agora / AsyncAgora Client
description: Constructor options and public methods for the Agora Python client.
---

# Agora / AsyncAgora Client

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
| `app_id` | `str` | Yes* | — | Agora App ID (app-credentials mode) |
| `app_certificate` | `str` | Yes* | — | Agora App Certificate (app-credentials mode) |
| `username` | `str` | Yes* | — | Customer ID (Basic Auth mode) |
| `password` | `str` | Yes* | — | Customer Secret (Basic Auth mode) |
| `auth_token` | `str` | No | — | Pre-built `agora token=<value>` |
| `headers` | `Dict[str, str]` | No | `None` | Additional headers sent with every request |
| `timeout` | `float` | No | `60` | Request timeout in seconds |
| `follow_redirects` | `bool` | No | `True` | Whether to follow HTTP redirects |
| `httpx_client` | `httpx.Client` | No | `None` | Custom httpx client instance |

*Provide either `app_id` + `app_certificate`, or `username` + `password`.

## `AsyncAgora` Constructor

Identical to `Agora` except:

| Parameter | Difference |
|---|---|
| `httpx_client` | Accepts `httpx.AsyncClient` instead of `httpx.Client` |

<!-- snippet: fragment -->
```python
from agora_agent import AsyncAgora, Area

client = AsyncAgora(
    area=Area.US,
    app_id='your-app-id',
    app_certificate='your-app-certificate',
)
```

## Public Methods

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

### `pool` (property)

Access the `Pool` object for advanced domain management.

<!-- snippet: fragment -->
```python
pool = client.pool
pool.get_area()  # Area.US
```

- **Returns:** `Pool`

## Sub-Clients (Fern-Generated)

Both `Agora` and `AsyncAgora` expose Fern-generated sub-clients as properties:

| Property | Type (sync / async) | Description |
|---|---|---|
| `client.agents` | `AgentsClient` / `AsyncAgentsClient` | Start, stop, list, update agents |
| `client.telephony` | `TelephonyClient` / `AsyncTelephonyClient` | Telephony operations |
| `client.phone_numbers` | `PhoneNumbersClient` / `AsyncPhoneNumbersClient` | Phone number management |

These are lazily initialized on first access. For most use cases, prefer the [AgentSession](./session.md) API instead of calling `client.agents` directly.
