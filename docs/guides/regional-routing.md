---
sidebar_position: 4
title: Regional Routing
description: Configure the Agora client to route requests to the nearest region.
---

# Regional Routing

The `Agora` and `AsyncAgora` clients include a built-in domain pool that automatically routes requests to the best available regional endpoint. This page explains how the pool works and how to control it.

## Area Enum

When you create a client, you specify an `Area` that determines the pool of regional endpoints:

```python
from agora_agent import Agora, Area

client = Agora(area=Area.US, app_id='your-app-id', app_certificate='your-app-certificate')
```

| Area | Primary Region | Fallback Region | Domain |
|---|---|---|---|
| `Area.US` | `api-us-west-1` | `api-us-east-1` | `agora.io` |
| `Area.EU` | `api-eu-west-1` | `api-eu-central-1` | `agora.io` |
| `Area.AP` | `api-ap-southeast-1` | `api-ap-northeast-1` | `agora.io` |
| `Area.CN` | `api-cn-east-1` | `api-cn-north-1` | `sd-rtn.com` |

## Pool Behavior

The `Pool` manages region prefixes and domain suffixes:

1. **Initial URL** — constructed from the first region prefix and domain: `https://api-us-west-1.agora.io/api/conversational-ai-agent`
2. **DNS-based domain selection** — `select_best_domain()` races DNS lookups against all domain suffixes and picks the fastest responder
3. **Region cycling** — `next_region()` rotates to the next region prefix (e.g., from `api-us-west-1` to `api-us-east-1`), wrapping around to the start when exhausted
4. **Auto-refresh** — domain selection is cached for 30 seconds, then refreshed on the next call

## Manual Domain Selection

### Sync (`Agora`)

`select_best_domain()` is a regular method on the sync client:

```python
from agora_agent import Agora, Area

client = Agora(area=Area.US, app_id='your-app-id', app_certificate='your-app-certificate')

# Manually trigger DNS-based domain selection
client.select_best_domain()

print(client.get_current_url())
# https://api-us-west-1.agora.io/api/conversational-ai-agent
```

### Async (`AsyncAgora`)

On `AsyncAgora`, `select_best_domain()` is a **coroutine** — you must call it with `await`:

```python
import asyncio
from agora_agent import AsyncAgora, Area

async def main():
    client = AsyncAgora(area=Area.US, app_id='your-app-id', app_certificate='your-app-certificate')

    # IMPORTANT: select_best_domain() is async on AsyncAgora
    await client.select_best_domain()

    print(client.get_current_url())

asyncio.run(main())
```

**Common mistake:** Calling `client.select_best_domain()` without `await` on `AsyncAgora` returns a coroutine object instead of executing the domain selection. No error is raised — the call silently does nothing. Always use `await`:

```python
# Wrong — returns a coroutine object, does not execute
client.select_best_domain()

# Correct
await client.select_best_domain()
```

## Region Cycling

If a request fails, cycle to the next region prefix:

```python
from agora_agent import Agora, Area

client = Agora(area=Area.US, app_id='your-app-id', app_certificate='your-app-certificate')

print(client.get_current_url())
# https://api-us-west-1.agora.io/api/conversational-ai-agent

client.next_region()

print(client.get_current_url())
# https://api-us-east-1.agora.io/api/conversational-ai-agent

# Wraps around after exhausting all prefixes
client.next_region()
print(client.get_current_url())
# https://api-us-west-1.agora.io/api/conversational-ai-agent
```

`next_region()` is a regular (non-async) method on both `Agora` and `AsyncAgora`.

## Accessing the Pool Directly

For advanced use, access the `Pool` object:

```python
pool = client.pool

pool.next_region()
pool.select_best_domain()  # sync only

url = pool.get_current_url()
area = pool.get_area()
```

## Client Method Summary

| Method | `Agora` | `AsyncAgora` | Description |
|---|---|---|---|
| `next_region()` | sync | sync | Cycle to next region prefix |
| `select_best_domain()` | sync | **`async` (requires `await`)** | DNS-based domain selection |
| `get_current_url()` | sync | sync | Get the current base URL |
| `pool` (property) | sync | sync | Access the `Pool` object |
