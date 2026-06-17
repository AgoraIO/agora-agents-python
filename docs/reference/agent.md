---
sidebar_position: 2
title: Agent
description: Full API reference for the Python Agent builder class.
---

# Agent Reference

**Import:** `from agora_agent import Agent`

Bind the client once on `Agent(client=client, ...)`, then pass vendor classes directly. The bound client sets the API routing region and provides area-specific IDE hints via `CNAgent` / `GlobalAgent`:

<!-- snippet: fragment -->
```python
from agora_agent import Agent, Agora, Area

client = Agora(area=Area.US, app_id="...", app_certificate="...")
agent = Agent(client=client, name="global-agent")
```

## Constructor

<!-- snippet: fragment -->
```python
Agent(
    client: Optional[Any] = None,
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
    pipeline_id: Optional[str] = None,
)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `name` | `Optional[str]` | `None` | Agent name, used as default session name |
| `client` | `Optional[Any]` | `None` | Bound Agora client used later by `create_session()` and `create_async_session()` |
| `instructions` | `Optional[str]` | `None` | Deprecated. Use LLM vendor `system_messages` instead. |
| `turn_detection` | `Optional[TurnDetectionConfig]` | `None` | Interaction language and turn detection configuration |
| `interruption` | `Optional[InterruptionConfig]` | `None` | Unified interruption control configuration |
| `sal` | `Optional[SalConfig]` | `None` | Speech Activity Level configuration |
| `advanced_features` | `Optional[Dict[str, Any]]` | `None` | Advanced features dict (e.g., `{'enable_rtm': True}`) |
| `parameters` | `Optional[SessionParams]` | `None` | Additional session parameters |
| `greeting` | `Optional[str]` | `None` | Deprecated. Use LLM/MLLM vendor `greeting_message` instead. |
| `failure_message` | `Optional[str]` | `None` | Deprecated. Use LLM/MLLM vendor `failure_message` instead. |
| `max_history` | `Optional[int]` | `None` | Deprecated. Use LLM vendor `max_history` instead. |
| `geofence` | `Optional[GeofenceConfig]` | `None` | Regional access restriction |
| `labels` | `Optional[Dict[str, str]]` | `None` | Custom key-value labels (returned in callbacks) |
| `rtc` | `Optional[RtcConfig]` | `None` | RTC media encryption |
| `filler_words` | `Optional[FillerWordsConfig]` | `None` | Filler words while waiting for LLM |
| `pipeline_id` | `Optional[str]` | `None` | Published AI Studio pipeline ID used as this agent's base configuration |

`pipeline_id` is an AI Studio base configuration. Explicit Agent config such as `with_llm()`, `with_tts()`, `with_stt()`, `with_mllm()`, `advanced_features`, and other builder options may send fields in `properties` that override the saved pipeline settings. Session-level `pipeline_id` overrides the agent-level value.

The Agent-level `instructions`, `greeting`, `failure_message`, `max_history`, and `greeting_configs` fields are compatibility shims. New code should configure those values on the LLM or MLLM vendor because that matches the core request schema.

## Builder Methods

All builder methods return a new `Agent` instance (immutable pattern).

### `with_llm(vendor: BaseLLM) -> Agent`

Set the LLM vendor for cascading flow.

<!-- snippet: fragment -->
```python
from agora_agent import Agora, Area, Agent, OpenAI
client = Agora(area=Area.US, app_id='your-app-id', app_certificate='your-app-certificate')
agent = Agent(client=client).with_llm(OpenAI(model='gpt-4o-mini'))
```

### `with_tts(vendor: BaseTTS) -> Agent`

Set the TTS vendor. Records the vendor's `sample_rate` for avatar validation.

<!-- snippet: fragment -->
```python
from agora_agent import Agora, Area, Agent, ElevenLabsTTS
client = Agora(area=Area.US, app_id='your-app-id', app_certificate='your-app-certificate')
agent = Agent(client=client).with_tts(ElevenLabsTTS(key='your-key', model_id='eleven_flash_v2_5', voice_id='your-voice-id', base_url='wss://api.elevenlabs.io/v1'))
```

### `with_stt(vendor: BaseSTT) -> Agent`

Set the STT (ASR) vendor.

<!-- snippet: fragment -->
```python
from agora_agent import Agora, Area, Agent, DeepgramSTT
client = Agora(area=Area.US, app_id='your-app-id', app_certificate='your-app-certificate')
agent = Agent(client=client).with_stt(DeepgramSTT(api_key='your-key', language='en-US'))
```

### `with_mllm(vendor: BaseMLLM) -> Agent`

Set the MLLM vendor for multimodal flow. Calling `with_mllm()` automatically sets `mllm.enable = True`. MLLM sessions do not require TTS, STT, or LLM vendors.

<!-- snippet: fragment -->
```python
from agora_agent import Agent, OpenAIRealtime
agent = Agent().with_mllm(OpenAIRealtime(api_key='your-key'))
```

### `with_avatar(vendor: BaseAvatar) -> Agent`

Set the avatar vendor for the cascading ASR + LLM + TTS pipeline. Avatars are not supported when MLLM is enabled — combining `with_mllm()` and an enabled `with_avatar()` is rejected at `to_properties()` and `AgentSession.start()`. A disabled avatar (`enable=False`) is allowed alongside MLLM.

Raises `ValueError` if the TTS sample rate does not match the avatar's `required_sample_rate`.

<!-- snippet: fragment -->
```python
from agora_agent import HeyGenAvatar
agent = agent.with_avatar(HeyGenAvatar(api_key='your-key', quality='medium', agora_uid='2'))
```

**Raises:** `ValueError` — `"Avatar requires TTS sample rate of {required} Hz, but TTS is configured with {actual} Hz. Please update your TTS sample_rate to {required}."`

### `with_turn_detection(config: TurnDetectionConfig) -> Agent`

Override cascading-flow turn detection settings. Use `language` for the Agora interaction language, `config.start_of_speech` and `config.end_of_speech` for SOS/EOS detection, `with_interruption()` for interruption behavior, and MLLM vendor `turn_detection` for MLLM turn detection.

Pause-state detection is configured under semantic end-of-speech:

```python
agent = agent.with_turn_detection({
    "mode": "default",
    "config": {
        "end_of_speech": {
            "mode": "semantic",
            "semantic_config": {
                "pause_state_enabled": True,
            },
        },
    },
})
```

### `with_interruption(config: InterruptionConfig) -> Agent`

Configure unified interruption behavior using the top-level `interruption` object. Use this for `start_of_speech` and `keywords` interruption modes.

### `with_instructions(instructions: str) -> Agent`

Deprecated. Configure `system_messages` on the LLM vendor instead.

### `with_greeting(greeting: str) -> Agent`

Deprecated. Configure `greeting_message` on the LLM or MLLM vendor instead.

### `with_name(name: str) -> Agent`

Override the agent name.

### `with_sal(config: SalConfig) -> Agent`

Set SAL (Selective Attention Locking) configuration.

### `with_advanced_features(features: AdvancedFeatures) -> Agent`

Set advanced features (e.g. `{'enable_rtm': True}`).

When `enable_rtm=True`, AgentKit defaults `parameters.data_channel` to `"rtm"` unless you explicitly set another data channel.

### `with_tools(enabled: bool = True) -> Agent`

Enable or disable MCP tool invocation by setting `advanced_features.enable_tools`.

### `with_parameters(parameters: SessionParams) -> Agent`

Set session parameters (silence config, farewell config, data channel, audio scenario, etc.).

### `with_audio_scenario(audio_scenario: ParametersAudioScenario) -> Agent`

Set `parameters.audio_scenario` without replacing existing session parameters.

### `with_failure_message(message: str) -> Agent`

Deprecated. Configure `failure_message` on the LLM or MLLM vendor instead.

### `with_max_history(max_history: int) -> Agent`

Deprecated. Configure `max_history` on the LLM vendor instead.

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
    channel: str,
    agent_uid: str,
    remote_uids: List[str],
    name: Optional[str] = None,
    token: Optional[str] = None,
    idle_timeout: Optional[int] = None,
    enable_string_uid: Optional[bool] = None,
    preset: Optional[Union[str, Sequence[str]]] = None,
    pipeline_id: Optional[str] = None,
    expires_in: Optional[int] = None,
) -> AgentSession
```

Creates an `AgentSession` using the client already bound to `Agent(client=...)`.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `channel` | `str` | Yes | Channel name |
| `agent_uid` | `str` | Yes | UID for the agent |
| `remote_uids` | `List[str]` | Yes | UIDs of remote participants |
| `name` | `Optional[str]` | No | Session name (defaults to agent name) |
| `token` | `Optional[str]` | No | Pre-built RTC+RTM token |
| `expires_in` | `Optional[int]` | No | Token lifetime in seconds (default: `86400` = 24 h, Agora max). Only applies when the token is auto-generated. Use `expires_in_hours()` or `expires_in_minutes()` for clarity. Valid range: 1–86400. |
| `idle_timeout` | `Optional[int]` | No | Idle timeout in seconds |
| `enable_string_uid` | `Optional[bool]` | No | Enable string UIDs |
| `preset` | `Optional[Union[str, Sequence[str]]]` | No | Advanced preset value for project-specific routing |
| `pipeline_id` | `Optional[str]` | No | Published AI Studio pipeline ID for this session. Overrides `agent.pipeline_id`. |

`pipeline_id` is sent as the top-level `/join` field `pipeline_id`, not inside `properties`.

`create_session()` requires that the agent was constructed with `client=...`. If no client is bound, it raises `ValueError`.

**Returns:** `AgentSession`

When you omit credentials for supported Agora-managed global models, AgentKit sends the matching Agora-managed configuration automatically:

- Deepgram STT: `nova-2`, `nova-3`
- OpenAI LLM: `gpt-4o-mini`, `gpt-4.1-mini`, `gpt-5-nano`, `gpt-5-mini`
- OpenAI TTS: `tts-1`
- MiniMax TTS: `speech-2.6-turbo`, `speech-2.8-turbo`, `speech_2_6_turbo`, `speech_2_8_turbo`

If you provide your own vendor API key for those same models, AgentKit keeps the request in BYOK mode.

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
| `instructions` | `Optional[str]` | Deprecated Agent-level system prompt |
| `greeting` | `Optional[str]` | Deprecated Agent-level greeting message |
| `failure_message` | `Optional[str]` | Deprecated Agent-level failure message |
| `max_history` | `Optional[int]` | Deprecated Agent-level max history |
| `llm` | `Optional[Dict[str, Any]]` | LLM config dict (from `to_config()`) |
| `tts` | `Optional[Dict[str, Any]]` | TTS config dict |
| `stt` | `Optional[Dict[str, Any]]` | STT config dict |
| `mllm` | `Optional[Dict[str, Any]]` | MLLM config dict |
| `avatar` | `Optional[Dict[str, Any]]` | Avatar config dict |
| `turn_detection` | `Optional[TurnDetectionConfig]` | Interaction language and turn detection settings |
| `sal` | `Optional[SalConfig]` | SAL configuration |
| `advanced_features` | `Optional[Dict[str, Any]]` | Advanced features |
| `parameters` | `Optional[SessionParams]` | Session parameters |
| `geofence` | `Optional[GeofenceConfig]` | Geofence configuration |
| `labels` | `Optional[Dict[str, str]]` | Custom labels |
| `rtc` | `Optional[RtcConfig]` | RTC configuration |
| `filler_words` | `Optional[FillerWordsConfig]` | Filler words configuration |
| `config` | `Dict[str, Any]` | Full configuration dict |

## Type aliases

Public aliases over Fern-generated types: `LlmConfig`, `SttConfig`, `AsrConfig` (= `SttConfig`), `MllmConfig`, `AvatarConfig`, session/conversation types, and think types (`ThinkOnListeningAction`, etc.).

Think value constants: `ThinkOnListeningActionInject`, `ThinkOnListeningActionInterrupt`, `ThinkOnListeningActionIgnore`, `ThinkOnThinkingActionInterrupt`, `ThinkOnThinkingActionIgnore`, `ThinkOnSpeakingActionInterrupt`, `ThinkOnSpeakingActionIgnore`.
