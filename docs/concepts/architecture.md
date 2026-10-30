---
sidebar_position: 1
title: Architecture
description: How the Python SDK layers are structured and when to use each.
---

# Architecture

## Three-Layer Design

The Python SDK has three layers:

```
+--------------------------------------------------+
|                Developer API                      |
|  Agent  ·  AgentSession  ·  Vendors  ·  Token     |  <- agora_agent.agentkit (hand-written)
+--------------------------------------------------+
|             Agora / AsyncAgora + Pool             |  <- agora_agent.pool_client (hand-written)
+--------------------------------------------------+
|          Fern-generated Client Core               |
|  AgentsClient · TelephonyClient · TypeSystem      |  <- auto-generated
+--------------------------------------------------+
```

### AgentKit Layer (`agora_agent.agentkit`)

This is the primary developer-facing API. It provides:

- **`Agent`** — a fluent builder for configuring AI agents with LLM, TTS, STT, MLLM, and avatar vendors. Requires a bound `Agora` / `AsyncAgora` client via `client=...`.
- **`AgentSession` / `AsyncAgentSession`** — lifecycle management for running agents (start, stop, say, interrupt)
- **Vendor classes** — typed configuration for 28+ vendor integrations across 5 categories
- **`generate_rtc_token()`** — helper for building RTC tokens

### Pool Client Layer (`agora_agent.pool_client`)

`Agora` and `AsyncAgora` extend the Fern-generated base client with regional routing:

- Automatic DNS-based domain selection
- Region prefix cycling on failures
- Support for US, EU, AP, and CN areas

### Fern-Generated Layer

The auto-generated core provides typed HTTP methods for the existing v2 API endpoints. You rarely need this directly, but it is accessible via `session.raw` for advanced use cases or new endpoints that the agentkit layer does not yet cover.

### v3 Preview Adapter

`client.v3` adds typed wire dictionaries and agents/secrets/numbers/session-read resources alongside the v2 generated clients. It reuses the pool client's HTTP transport and authentication, with separate staging origin/header overrides. This is protected custom/local-generated code rather than canonical Fern output. AgentKit adds `SavedAgent` / `AsyncSavedAgent` for persisted configurations; existing session handles remain v2. See [v3 workflows](../guides/v3-api-preview.md) and [reference](../reference/v3.md).

## Sync vs. Async

The SDK provides two parallel client hierarchies:

| Sync | Async | HTTP Backend |
|---|---|---|
| `Agora` | `AsyncAgora` | `httpx.Client` / `httpx.AsyncClient` |
| `AgentSession` | `AsyncAgentSession` | Blocking calls / Coroutines |
| `SavedAgent` (preview) | `AsyncSavedAgent` (preview) | Stored configuration and number assignment calls |

### When to Use Each

**Use `Agora` (sync)** when:
- You are writing scripts, CLI tools, or batch jobs
- Your web framework is synchronous (Flask, Django without async views)
- You want the simplest possible code

**Use `AsyncAgora` (async)** when:
- Your application uses `asyncio` (FastAPI, Starlette, aiohttp)
- You need to manage multiple concurrent agent sessions
- You want non-blocking I/O

### Key Difference

Every method on `AgentSession` that makes an HTTP call (`start()`, `stop()`, `say()`, `interrupt()`, `update()`, `get_history()`, `get_info()`) has an `async` equivalent on `AsyncAgentSession` that must be called with `await`:

<!-- snippet: fragment -->
```python
# Sync
agent_id = session.start()
session.say('Hello!')
session.stop()

# Async
agent_id = await session.start()
await session.say('Hello!')
await session.stop()
```

The `Agent` builder class is the same for both — it does not make HTTP calls, so it has no async variant.

## Import paths

```python
from agora_agent import (
    Agent,
    AgentSession,
    AsyncAgentSession,
    Agora,
    AsyncAgora,
    Area,
    Pool,
    OpenAI,
    ElevenLabsTTS,
    DeepgramSTT,
    generate_rtc_token,
)
```
