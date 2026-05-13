---
sidebar_position: 2
title: Agent
description: The Agent builder — configure an AI agent with LLM, TTS, STT, and more.
---

# Agent

The `Agent` class is a fluent builder for configuring AI agent properties. It collects vendor settings (LLM, TTS, STT, MLLM, avatar) and session parameters, then produces a fully configured `AgentSession` when you call `create_session()`.

## Constructor

<!-- snippet: executable -->
```python
from agora_agent.agentkit import Agent

agent = Agent(
    name='support-assistant',
    instructions='You are a helpful voice assistant.',
    greeting='Hello! How can I help you?',
    failure_message='Sorry, something went wrong.',
    max_history=20,
)
```

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | `str` | No | Agent display name (used as session name if not overridden) |
| `instructions` | `str` | No | System prompt for the LLM |
| `greeting` | `str` | No | Message spoken when the agent joins |
| `failure_message` | `str` | No | Message spoken on error |
| `max_history` | `int` | No | Maximum conversation history length |
| `turn_detection` | `TurnDetectionConfig` | No | Turn detection settings |
| `sal` | `SalConfig` | No | SAL (Speech Activity Level) configuration |
| `advanced_features` | `Dict[str, Any]` | No | Advanced features (e.g., `{'enable_rtm': True}`) |
| `parameters` | `SessionParams` | No | Additional session parameters |
| `geofence` | `GeofenceConfig` | No | Regional access restriction |
| `labels` | `Dict[str, str]` | No | Custom key-value labels (returned in callbacks) |
| `rtc` | `RtcConfig` | No | RTC media encryption |
| `filler_words` | `FillerWordsConfig` | No | Filler words while waiting for LLM |

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
| `with_instructions(text)` | `str` | Override the system prompt |
| `with_greeting(text)` | `str` | Override the greeting message |
| `with_name(name)` | `str` | Override the agent name |
| `with_turn_detection(config)` | `TurnDetectionConfig` | Override cascading-flow SOS/EOS detection; use `with_interruption()` for interruption behavior |
| `with_sal(config)` | `SalConfig` | Set SAL configuration |
| `with_advanced_features(features)` | `Dict[str, Any]` | Set advanced features |
| `with_parameters(parameters)` | `SessionParams` | Set session parameters |
| `with_failure_message(message)` | `str` | Set failure message |
| `with_max_history(max_history)` | `int` | Set max history length |
| `with_geofence(geofence)` | `GeofenceConfig` | Set geofence configuration |
| `with_labels(labels)` | `Dict[str, str]` | Set custom labels |
| `with_rtc(rtc)` | `RtcConfig` | Set RTC configuration |
| `with_filler_words(filler_words)` | `FillerWordsConfig` | Set filler words configuration |

## Chaining Example

<!-- snippet: executable -->
```python
from agora_agent.agentkit import Agent
from agora_agent.agentkit.vendors import OpenAI, ElevenLabsTTS, DeepgramSTT

agent = (
    Agent(name='my-agent', instructions='You are a helpful assistant.')
    .with_llm(OpenAI(api_key='your-openai-key', model='gpt-4o-mini'))
    .with_tts(ElevenLabsTTS(key='your-elevenlabs-key', model_id='eleven_flash_v2_5', voice_id='your-voice-id'))
    .with_stt(DeepgramSTT(api_key='your-deepgram-key', language='en-US'))
)
```

## Immutable Reuse

Because each `with_*` call returns a new `Agent`, you can build a base configuration and create multiple sessions from it:

<!-- snippet: executable -->
```python
from agora_agent import Agora, Area
from agora_agent.agentkit import Agent
from agora_agent.agentkit.vendors import OpenAI, ElevenLabsTTS, DeepgramSTT

client = Agora(area=Area.US, app_id='your-app-id', app_certificate='your-app-certificate')

base = (
    Agent(instructions='You are a helpful assistant.')
    .with_llm(OpenAI(api_key='your-openai-key', model='gpt-4o-mini'))
    .with_tts(ElevenLabsTTS(key='your-elevenlabs-key', model_id='eleven_flash_v2_5', voice_id='your-voice-id'))
    .with_stt(DeepgramSTT(api_key='your-deepgram-key', language='en-US'))
)

# Same agent config, different channels
session_a = base.create_session(client, channel='room-a', agent_uid='1', remote_uids=['100'])
session_b = base.create_session(client, channel='room-b', agent_uid='1', remote_uids=['200'])
```

## `create_session()`

Creates a new `AgentSession` bound to a client and channel.

<!-- snippet: fragment -->
```python
session = agent.create_session(
    client,
    channel='my-channel',
    agent_uid='1',
    remote_uids=['100'],
    name='optional-session-name',
    token='optional-pre-built-token',
    idle_timeout=300,
    enable_string_uid=True,
)
```

| Parameter | Type | Required | Description |
|---|---|---|---|
| `client` | `Agora` or `AsyncAgora` | Yes | The authenticated client |
| `channel` | `str` | Yes | Agora channel name |
| `agent_uid` | `str` | Yes | UID for the agent in the channel |
| `remote_uids` | `List[str]` | Yes | UIDs of remote participants to listen to |
| `name` | `str` | No | Session name (defaults to agent name or auto-generated) |
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
| `agent.name` | `Optional[str]` | Agent name |
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
