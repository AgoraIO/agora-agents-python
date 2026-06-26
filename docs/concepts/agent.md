---
sidebar_position: 2
title: Agent
description: The Agent builder — configure an AI agent with LLM, TTS, STT, and more.
---

# Agent

The `Agent` class is a fluent builder for configuring AI agent properties. Pass a bound `Agora` or `AsyncAgora` client with `client=...` — it is required for `create_session()` and `create_async_session()`. The builder collects vendor settings (LLM, TTS, STT, MLLM, avatar) and produces a fully configured `AgentSession` when you call `create_session()`. The agent instance name is set on `create_session(name=...)`, not on the `Agent` constructor.

## Constructor

<!-- snippet: executable -->
```python
from agora_agent import Agent, Agora, Area, OpenAI

client = Agora(area=Area.US, app_id='your-app-id', app_certificate='your-app-certificate')

agent = Agent(client=client).with_llm(
    OpenAI(
        api_key='your-openai-key',
        base_url='https://api.openai.com/v1/chat/completions',
        model='gpt-4o-mini',
        system_messages=[{'role': 'system', 'content': 'You are a helpful voice assistant.'}],
        greeting_message='Hello! How can I help you?',
        failure_message='Sorry, something went wrong.',
        max_history=20,
    )
)
```

| Parameter | Type | Required | Description |
|---|---|---|---|
| `client` | `Agora` / `AsyncAgora` | Yes | Authenticated client from `Agora(...)` or `AsyncAgora(...)`. Required for `create_session()` and `create_async_session()`. |
| `pipeline_id` | `str` | No | Published AI Studio pipeline ID used as this agent's base configuration |
| `instructions` | `str` | No | Deprecated. Use LLM vendor `system_messages` instead. |
| `greeting` | `str` | No | Deprecated. Use LLM/MLLM vendor `greeting_message` instead. |
| `failure_message` | `str` | No | Deprecated. Use LLM/MLLM vendor `failure_message` instead. |
| `max_history` | `int` | No | Deprecated. Use LLM vendor `max_history` instead. |
| `turn_detection` | `TurnDetectionConfig` | No | Turn detection settings |
| `sal` | `SalConfig` | No | SAL (Speech Activity Level) configuration |
| `advanced_features` | `Dict[str, Any]` | No | Advanced features (e.g., `{'enable_rtm': True}`) |
| `parameters` | `SessionParams` | No | Additional session parameters |
| `geofence` | `GeofenceConfig` | No | Regional access restriction |
| `labels` | `Dict[str, str]` | No | Custom key-value labels (returned in callbacks) |
| `rtc` | `RtcConfig` | No | RTC media encryption |
| `filler_words` | `FillerWordsConfig` | No | Filler words while waiting for LLM |

When `client` is provided, `Agent(client=...)` returns `CNAgent` for `Area.CN` and `GlobalAgent` for global areas. If `with_stt()` is omitted, the bound client also determines the default ASR vendor: `Fengming` for `Area.CN`, otherwise `Ares`.

## Builder Methods

Each `with_*` method returns a **new** `Agent` instance — the original is unchanged. This immutability lets you safely reuse a base configuration for multiple sessions.

### Vendor Methods

| Method | Accepts | Purpose |
|---|---|---|
| `with_llm(vendor)` | `BaseLLM` | Set the LLM provider |
| `with_tts(vendor)` | `BaseTTS` | Set the TTS provider |
| `with_stt(vendor)` | `BaseSTT` | Set the STT provider |
| `with_mllm(vendor)` | `BaseMLLM` | Set the MLLM provider (for multimodal flow) |
| `with_avatar(vendor)` | `BaseAvatar` | Set the avatar provider |

### Configuration Methods

| Method | Accepts | Purpose |
|---|---|---|
| `with_instructions(text)` | `str` | Deprecated. Use LLM vendor `system_messages` instead. |
| `with_greeting(text)` | `str` | Deprecated. Use LLM/MLLM vendor `greeting_message` instead. |
| `with_turn_detection(config)` | `TurnDetectionConfig` | Configure `turn_detection.language` and cascading-flow SOS/EOS detection; use `with_interruption()` for interruption behavior |
| `with_sal(config)` | `SalConfig` | Set SAL configuration |
| `with_advanced_features(features)` | `Dict[str, Any]` | Set advanced features |
| `with_parameters(parameters)` | `SessionParams` | Set session parameters |
| `with_failure_message(message)` | `str` | Deprecated. Use LLM/MLLM vendor `failure_message` instead. |
| `with_max_history(max_history)` | `int` | Deprecated. Use LLM vendor `max_history` instead. |
| `with_geofence(geofence)` | `GeofenceConfig` | Set geofence configuration |
| `with_labels(labels)` | `Dict[str, str]` | Set custom labels |
| `with_rtc(rtc)` | `RtcConfig` | Set RTC configuration |
| `with_filler_words(filler_words)` | `FillerWordsConfig` | Set filler words configuration |

## Chaining Example

<!-- snippet: executable -->
```python
from agora_agent import Agent, Agora, Area, DeepgramSTT, ElevenLabsTTS, OpenAI

client = Agora(area=Area.US, app_id='your-app-id', app_certificate='your-app-certificate')

agent = (
    Agent(client=client)
    .with_llm(OpenAI(
        api_key='your-openai-key',
        base_url='https://api.openai.com/v1/chat/completions',
        model='gpt-4o-mini',
        system_messages=[{'role': 'system', 'content': 'You are a helpful assistant.'}],
    ))
    .with_tts(ElevenLabsTTS(key='your-elevenlabs-key', model_id='eleven_flash_v2_5', voice_id='your-voice-id', base_url='wss://api.elevenlabs.io/v1'))
    .with_stt(DeepgramSTT(api_key='your-deepgram-key', language='en-US'))
)
```

## Immutable Reuse

Because each `with_*` call returns a new `Agent`, you can build a base configuration and create multiple sessions from it:

<!-- snippet: executable -->
```python
from agora_agent import Agent, Agora, Area, DeepgramSTT, ElevenLabsTTS, OpenAI
import time

client = Agora(area=Area.US, app_id='your-app-id', app_certificate='your-app-certificate')

base = (
    Agent(client=client)
    .with_llm(OpenAI(
        api_key='your-openai-key',
        base_url='https://api.openai.com/v1/chat/completions',
        model='gpt-4o-mini',
        system_messages=[{'role': 'system', 'content': 'You are a helpful assistant.'}],
    ))
    .with_tts(ElevenLabsTTS(key='your-elevenlabs-key', model_id='eleven_flash_v2_5', voice_id='your-voice-id', base_url='wss://api.elevenlabs.io/v1'))
    .with_stt(DeepgramSTT(api_key='your-deepgram-key', language='en-US'))
)

# Same agent config, different channels and session names
session_a = base.create_session(channel=f"demo-channel-{int(time.time())}", agent_uid='1', remote_uids=['100'], name=f"conversation-{int(time.time())}")
session_b = base.create_session(channel=f"demo-channel-{int(time.time())}", agent_uid='1', remote_uids=['200'], name=f"conversation-{int(time.time())}")
```

## `create_session()`

Creates a new `AgentSession` using the client already bound to the agent. Pass the agent instance name via the `name` parameter here — it is sent to the Start Agent API when the session starts.

<!-- snippet: fragment -->
```python
import time
session = agent.create_session(
    channel=f"demo-channel-{int(time.time())}",
    agent_uid='1',
    remote_uids=['100'],
    name=f"conversation-{int(time.time())}",
    token='optional-pre-built-token',
    idle_timeout=300,
    enable_string_uid=True,
)
```

| Parameter | Type | Required | Description |
|---|---|---|---|
| `channel` | `str` | Yes | Agora channel name |
| `agent_uid` | `str` | Yes | UID for the agent in the channel |
| `remote_uids` | `List[str]` | Yes | UIDs of remote participants to listen to |
| `name` | `str` | No | Agent instance name for the Start Agent API (defaults to `agent-{timestamp}` if omitted) |
| `token` | `str` | No | Pre-built RTC token (if not provided, generated from client credentials) |
| `idle_timeout` | `int` | No | Idle timeout in seconds |
| `enable_string_uid` | `bool` | No | Enable string UIDs |

## Avatar Sample Rate Constraint

When using `with_avatar()`, the SDK validates that the TTS sample rate matches the avatar's requirement. If there is a mismatch, a `ValueError` is raised at build time:

```
ValueError: Avatar requires TTS sample rate of 24000 Hz, but TTS is configured with 16000 Hz. Please update your TTS sample_rate to 24000.
```

See [Avatar Integration](../guides/avatars.md) for details.

## Properties

| Property | Type | Description |
|---|---|---|
| `agent.instructions` | `Optional[str]` | System prompt |
| `agent.greeting` | `Optional[str]` | Greeting message |
| `agent.failure_message` | `Optional[str]` | Message spoken when LLM fails |
| `agent.max_history` | `Optional[int]` | Max conversation history length |
| `agent.llm` | `Optional[Dict]` | LLM configuration dict |
| `agent.tts` | `Optional[Dict]` | TTS configuration dict |
| `agent.stt` | `Optional[Dict]` | STT configuration dict |
| `agent.mllm` | `Optional[Dict]` | MLLM configuration dict |
| `agent.avatar` | `Optional[Dict]` | Avatar configuration dict |
| `agent.turn_detection` | `Optional[TurnDetectionConfig]` | Turn detection settings |
| `agent.sal` | `Optional[SalConfig]` | SAL configuration |
| `agent.advanced_features` | `Optional[Dict]` | Advanced features |
| `agent.parameters` | `Optional[SessionParams]` | Session parameters |
| `agent.geofence` | `Optional[GeofenceConfig]` | Geofence configuration |
| `agent.labels` | `Optional[Dict[str, str]]` | Custom labels |
| `agent.rtc` | `Optional[RtcConfig]` | RTC configuration |
| `agent.filler_words` | `Optional[FillerWordsConfig]` | Filler words configuration |
| `agent.config` | `Dict[str, Any]` | Full configuration dict |
