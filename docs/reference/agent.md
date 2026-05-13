---
sidebar_position: 2
title: Agent
description: Full API reference for the Python Agent builder class.
---

# Agent Reference

**Import:** `from agora_agent.agentkit import Agent` or `from agora_agent import Agent`

## Constructor

<!-- snippet: fragment -->
```python
Agent(
    name: Optional[str] = None,
    instructions: Optional[str] = None,
    turn_detection: Optional[TurnDetectionConfig] = None,
    interruption: Optional[InterruptionConfig] = None,
    sal: Optional[SalConfig] = None,
    advanced_features: Optional[Dict[str, Any]] = None,
    parameters: Optional[SessionParams] = None,
    greeting: Optional[str] = None,
    failure_message: Optional[str] = None,
    max_history: Optional[int] = None,
    geofence: Optional[GeofenceConfig] = None,
    labels: Optional[Dict[str, str]] = None,
    rtc: Optional[RtcConfig] = None,
    filler_words: Optional[FillerWordsConfig] = None,
)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `name` | `Optional[str]` | `None` | Agent name, used as default session name |
| `instructions` | `Optional[str]` | `None` | System prompt for the LLM |
| `turn_detection` | `Optional[TurnDetectionConfig]` | `None` | Turn detection configuration |
| `interruption` | `Optional[InterruptionConfig]` | `None` | Unified interruption control configuration |
| `sal` | `Optional[SalConfig]` | `None` | Speech Activity Level configuration |
| `advanced_features` | `Optional[Dict[str, Any]]` | `None` | Advanced features dict (e.g., `{'enable_rtm': True}`) |
| `parameters` | `Optional[SessionParams]` | `None` | Additional session parameters |
| `greeting` | `Optional[str]` | `None` | Auto-spoken greeting when agent joins |
| `failure_message` | `Optional[str]` | `None` | Spoken on error |
| `max_history` | `Optional[int]` | `None` | Max conversation history length |
| `geofence` | `Optional[GeofenceConfig]` | `None` | Regional access restriction |
| `labels` | `Optional[Dict[str, str]]` | `None` | Custom key-value labels (returned in callbacks) |
| `rtc` | `Optional[RtcConfig]` | `None` | RTC media encryption |
| `filler_words` | `Optional[FillerWordsConfig]` | `None` | Filler words while waiting for LLM |

## Builder Methods

All builder methods return a new `Agent` instance (immutable pattern).

### `with_llm(vendor: BaseLLM) -> Agent`

Set the LLM vendor for cascading flow.

<!-- snippet: fragment -->
```python
from agora_agent.agentkit.vendors import OpenAI
agent = Agent().with_llm(OpenAI(api_key='your-key', model='gpt-4o-mini'))
```

### `with_tts(vendor: BaseTTS) -> Agent`

Set the TTS vendor. Records the vendor's `sample_rate` for avatar validation.

<!-- snippet: fragment -->
```python
from agora_agent.agentkit.vendors import ElevenLabsTTS
agent = Agent().with_tts(ElevenLabsTTS(key='your-key', model_id='eleven_flash_v2_5', voice_id='your-voice-id'))
```

### `with_stt(vendor: BaseSTT) -> Agent`

Set the STT (ASR) vendor.

<!-- snippet: fragment -->
```python
from agora_agent.agentkit.vendors import DeepgramSTT
agent = Agent().with_stt(DeepgramSTT(api_key='your-key', language='en-US'))
```

### `with_mllm(vendor: BaseMLLM) -> Agent`

Set the MLLM vendor for multimodal flow. Calling `with_mllm()` automatically sets `mllm.enable = True`.

<!-- snippet: fragment -->
```python
from agora_agent.agentkit.vendors import OpenAIRealtime
agent = Agent().with_mllm(OpenAIRealtime(api_key='your-key'))
```

### `with_avatar(vendor: BaseAvatar) -> Agent`

Set the avatar vendor. Raises `ValueError` if TTS sample rate does not match the avatar's `required_sample_rate`.

<!-- snippet: fragment -->
```python
from agora_agent.agentkit.vendors import HeyGenAvatar
agent = agent.with_avatar(HeyGenAvatar(api_key='your-key', quality='medium', agora_uid='2'))
```

**Raises:** `ValueError` — `"Avatar requires TTS sample rate of {required} Hz, but TTS is configured with {actual} Hz. Please update your TTS sample_rate to {required}."`

### `with_turn_detection(config: TurnDetectionConfig) -> Agent`

Override cascading-flow turn detection settings. Use `config.start_of_speech` and `config.end_of_speech` for SOS/EOS detection. Use `with_interruption()` for interruption behavior and MLLM vendor `turn_detection` for MLLM turn detection.

### `with_interruption(config: InterruptionConfig) -> Agent`

Configure unified interruption behavior using the top-level `interruption` object. Use this for `start_of_speech` and `keywords` interruption modes.

### `with_instructions(instructions: str) -> Agent`

Override the system prompt.

### `with_greeting(greeting: str) -> Agent`

Override the greeting message.

### `with_name(name: str) -> Agent`

Override the agent name.

### `with_sal(config: SalConfig) -> Agent`

Set SAL (Selective Attention Locking) configuration.

### `with_advanced_features(features: AdvancedFeatures) -> Agent`

Set advanced features (e.g. `{'enable_rtm': True}`).

### `with_tools(enabled: bool = True) -> Agent`

Enable or disable MCP tool invocation by setting `advanced_features.enable_tools`.

### `with_parameters(parameters: SessionParams) -> Agent`

Set session parameters (silence config, farewell config, data channel, etc.).

### `with_failure_message(message: str) -> Agent`

Set the message spoken via TTS when the LLM call fails.

### `with_max_history(max_history: int) -> Agent`

Set the maximum conversation history length.

### `with_geofence(geofence: GeofenceConfig) -> Agent`

Set geofence configuration (restricts backend server regions).

### `with_labels(labels: Dict[str, str]) -> Agent`

Set custom labels (key-value pairs returned in notification callbacks).

### `with_rtc(rtc: RtcConfig) -> Agent`

Set RTC configuration.

### `with_filler_words(filler_words: FillerWordsConfig) -> Agent`

Set filler words configuration (played while waiting for LLM response).

## `create_session()`

<!-- snippet: fragment -->
```python
create_session(
    client: Any,
    channel: str,
    agent_uid: str,
    remote_uids: List[str],
    name: Optional[str] = None,
    token: Optional[str] = None,
    idle_timeout: Optional[int] = None,
    enable_string_uid: Optional[bool] = None,
    expires_in: Optional[int] = None,
) -> AgentSession
```

Creates an `AgentSession` bound to the given client and channel.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `client` | `Agora` or `AsyncAgora` | Yes | Authenticated client |
| `channel` | `str` | Yes | Channel name |
| `agent_uid` | `str` | Yes | UID for the agent |
| `remote_uids` | `List[str]` | Yes | UIDs of remote participants |
| `name` | `Optional[str]` | No | Session name (defaults to agent name) |
| `token` | `Optional[str]` | No | Pre-built RTC+RTM token |
| `expires_in` | `Optional[int]` | No | Token lifetime in seconds (default: `86400` = 24 h, Agora max). Only applies when the token is auto-generated. Use `expires_in_hours()` or `expires_in_minutes()` for clarity. Valid range: 1–86400. |
| `idle_timeout` | `Optional[int]` | No | Idle timeout in seconds |
| `enable_string_uid` | `Optional[bool]` | No | Enable string UIDs |

**Returns:** `AgentSession`

## `to_properties()`

Converts the agent configuration into a `StartAgentsRequestProperties` object for the Agora API. Called internally by `AgentSession.start()`.

<!-- snippet: fragment -->
```python
to_properties(
    channel: str,
    agent_uid: str,
    remote_uids: List[str],
    idle_timeout: Optional[int] = None,
    enable_string_uid: Optional[bool] = None,
    token: Optional[str] = None,
    app_id: Optional[str] = None,
    app_certificate: Optional[str] = None,
    expires_in: Optional[int] = None,
) -> StartAgentsRequestProperties
```

**Raises:** `ValueError` if neither `token` nor `app_id`+`app_certificate` is provided, or if required vendors (LLM, TTS) are missing in cascading mode.

## Properties

| Property | Type | Description |
|---|---|---|
| `name` | `Optional[str]` | Agent name |
| `instructions` | `Optional[str]` | System prompt |
| `greeting` | `Optional[str]` | Greeting message |
| `failure_message` | `Optional[str]` | Message spoken when LLM fails |
| `max_history` | `Optional[int]` | Max conversation history length |
| `llm` | `Optional[Dict[str, Any]]` | LLM config dict (from `to_config()`) |
| `tts` | `Optional[Dict[str, Any]]` | TTS config dict |
| `stt` | `Optional[Dict[str, Any]]` | STT config dict |
| `mllm` | `Optional[Dict[str, Any]]` | MLLM config dict |
| `avatar` | `Optional[Dict[str, Any]]` | Avatar config dict |
| `turn_detection` | `Optional[TurnDetectionConfig]` | Turn detection settings |
| `sal` | `Optional[SalConfig]` | SAL configuration |
| `advanced_features` | `Optional[Dict[str, Any]]` | Advanced features |
| `parameters` | `Optional[SessionParams]` | Session parameters |
| `geofence` | `Optional[GeofenceConfig]` | Geofence configuration |
| `labels` | `Optional[Dict[str, str]]` | Custom labels |
| `rtc` | `Optional[RtcConfig]` | RTC configuration |
| `filler_words` | `Optional[FillerWordsConfig]` | Filler words configuration |
| `config` | `Dict[str, Any]` | Full configuration dict |
