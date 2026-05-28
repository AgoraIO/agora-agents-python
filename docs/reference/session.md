---
sidebar_position: 3
title: AgentSession
description: Full API reference for the Python AgentSession class.
---

# AgentSession / AsyncAgentSession Reference

**Import:**
<!-- snippet: fragment -->
```python
from agora_agent import AgentSession
from agora_agent import AsyncAgentSession
# or from top-level:
from agora_agent import AgentSession, AsyncAgentSession
```

## Constructor

Sessions are normally created via `Agent.create_session()`. Direct construction is available for advanced use:

<!-- snippet: fragment -->
```python
AgentSession(
    client: Any,
    agent: Agent,
    app_id: str,
    name: str,
    channel: str,
    agent_uid: str,
    remote_uids: List[str],
    app_certificate: Optional[str] = None,
    token: Optional[str] = None,
    idle_timeout: Optional[int] = None,
    enable_string_uid: Optional[bool] = None,
)
```

`AsyncAgentSession` has the same constructor signature.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `client` | `Agora` or `AsyncAgora` | Yes | Authenticated client |
| `agent` | `Agent` | Yes | Agent configuration |
| `app_id` | `str` | Yes | Agora App ID |
| `name` | `str` | Yes | Session name |
| `channel` | `str` | Yes | Channel name |
| `agent_uid` | `str` | Yes | UID for the agent |
| `remote_uids` | `List[str]` | Yes | UIDs of remote participants |
| `app_certificate` | `Optional[str]` | No | App Certificate (for auto token generation) |
| `token` | `Optional[str]` | No | Pre-built RTC token |
| `idle_timeout` | `Optional[int]` | No | Idle timeout in seconds |
| `enable_string_uid` | `Optional[bool]` | No | Enable string UIDs |

## Methods

### `start()`

Start the agent session. Generates an RTC token if not provided, validates avatar/TTS config for cascading sessions, and calls the Agora API. MLLM sessions do not require TTS; an enabled avatar is rejected when MLLM is configured (a disabled avatar is allowed).

| | Sync (`AgentSession`) | Async (`AsyncAgentSession`) |
|---|---|---|
| **Signature** | `start() -> str` | `async start() -> str` |
| **Returns** | Agent ID | Agent ID |
| **Raises** | `RuntimeError` if not in `idle`, `stopped`, or `error` state | Same |
| **Raises** | `ValueError` if avatar/TTS sample rate mismatch or an enabled avatar is used with MLLM | Same |

<!-- snippet: fragment -->
```python
# Sync
agent_id = session.start()

# Async
agent_id = await session.start()
```

### `stop()`

Stop the agent session. If the agent has already stopped (404 from API), transitions to `stopped` without raising.

| | Sync | Async |
|---|---|---|
| **Signature** | `stop() -> None` | `async stop() -> None` |
| **Raises** | `RuntimeError` if not in `running` state | Same |

<!-- snippet: fragment -->
```python
# Sync
session.stop()

# Async
await session.stop()
```

### `say(text, priority=None, interruptable=None)`

Send text to be spoken by the agent's TTS.

| | Sync | Async |
|---|---|---|
| **Signature** | `say(text: str, priority: Optional[str] = None, interruptable: Optional[bool] = None) -> None` | Same with `async` |
| **Raises** | `RuntimeError` if not in `running` state | Same |

| Parameter | Type | Required | Description |
|---|---|---|---|
| `text` | `str` | Yes | Text to speak |
| `priority` | `str` | No | `INTERRUPT`, `APPEND`, or `IGNORE` |
| `interruptable` | `bool` | No | Whether the message can be interrupted |

<!-- snippet: fragment -->
```python
# Sync
session.say('Hello!', priority='INTERRUPT', interruptable=False)

# Async
await session.say('Hello!', priority='INTERRUPT', interruptable=False)
```

### `interrupt()`

Interrupt the agent while speaking or thinking.

| | Sync | Async |
|---|---|---|
| **Signature** | `interrupt() -> None` | `async interrupt() -> None` |
| **Raises** | `RuntimeError` if not in `running` state | Same |

<!-- snippet: fragment -->
```python
# Sync
session.interrupt()

# Async
await session.interrupt()
```

### `update(properties)`

Update the agent configuration at runtime.

| | Sync | Async |
|---|---|---|
| **Signature** | `update(properties: Any) -> None` | `async update(properties: Any) -> None` |
| **Raises** | `RuntimeError` if not in `running` state | Same |

<!-- snippet: fragment -->
```python
from agora_agent.agents.types import UpdateAgentsRequestProperties

# Sync
session.update(properties)

# Async
await session.update(properties)
```

### `think(text, ...)`

Inject a custom text instruction into the running agent.

In API v2.7, omitting `on_listening_action` uses the server default `interrupt`. Pass `on_listening_action='inject'` explicitly to preserve the pre-v2.7 behavior.

```python
session.think('Summarize the last answer', on_listening_action='inject')
```

### `get_history()`

Retrieve the conversation history.

| | Sync | Async |
|---|---|---|
| **Signature** | `get_history() -> Any` | `async get_history() -> Any` |
| **Raises** | `RuntimeError` if no agent ID | Same |

<!-- snippet: fragment -->
```python
# Sync
history = session.get_history()

# Async
history = await session.get_history()
```

### `get_info()`

Retrieve the current session info.

| | Sync | Async |
|---|---|---|
| **Signature** | `get_info() -> Any` | `async get_info() -> Any` |
| **Raises** | `RuntimeError` if no agent ID | Same |

<!-- snippet: fragment -->
```python
# Sync
info = session.get_info()

# Async
info = await session.get_info()
```

### `get_turns(page_index=None, page_size=None)`

Retrieve paginated turn analytics for a completed or running session. In v2.7, the API defaults to page 1 and up to 50 turns per page. Responses include `agent_id`, `name`, `channel`, `total_turn_count`, `pagination`, and `turns`.

```python
page = session.get_turns(page_index=1, page_size=50)
```

### `get_all_turns(page_size=None)`

Fetch all turn pages and return a single `GetTurnsAgentsResponse` with the combined `turns` list.

```python
all_turns = session.get_all_turns(page_size=50)
```

### `on(event, handler)`

Register an event handler. This method is synchronous on both `AgentSession` and `AsyncAgentSession`.

<!-- snippet: fragment -->
```python
session.on('started', lambda data: print(f'Started: {data}'))
```

| Parameter | Type | Description |
|---|---|---|
| `event` | `str` | Event type: `started`, `stopped`, or `error` |
| `handler` | `Callable[..., None]` | Callback function |

### `off(event, handler)`

Remove a previously registered event handler.

<!-- snippet: fragment -->
```python
session.off('started', my_handler)
```

## Properties

| Property | Type | Description |
|---|---|---|
| `id` | `Optional[str]` | Agent ID (set after `start()`) |
| `status` | `str` | Current state: `idle`, `starting`, `running`, `stopping`, `stopped`, `error` |
| `agent` | `Agent` | The agent configuration |
| `app_id` | `str` | Agora App ID |
| `raw` | `AgentsClient` / `AsyncAgentsClient` | Direct access to Fern-generated agents client |

## State Transitions

| Current State | Allowed Actions |
|---|---|
| `idle` | `start()` |
| `starting` | (waiting for API) |
| `running` | `stop()`, `say()`, `interrupt()`, `update()`, `get_history()`, `get_info()` |
| `stopping` | (waiting for API) |
| `stopped` | `start()` (restart) |
| `error` | `start()` (retry) |
