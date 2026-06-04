---
sidebar_position: 3
title: Avatar Integration
description: Add a digital avatar to your Conversational AI agent.
---

# Avatar Integration

You can attach a digital avatar to your voice agent so that users see a visual representation of the AI speaking.

Avatars are currently supported only with the cascading ASR + LLM + TTS pipeline. MLLM sessions handle audio end-to-end and do not support avatars at this time.

| Provider | Class | Required TTS Sample Rate |
|---|---|---|
| LiveAvatar | `LiveAvatarAvatar` | 24000 Hz |
| HeyGen (deprecated alias) | `HeyGenAvatar` | 24000 Hz |
| Akool | `AkoolAvatar` | 16000 Hz |
| Anam | `AnamAvatar` | None |
| Generic | `GenericAvatar` | None |

## Token Model

The agent and avatar join the same RTC channel with separate UIDs. The agent token is scoped to `agent_uid`; `avatar.params.agora_token` is scoped to the avatar `agora_uid`.

When using `AgentSession.start()`, `agora_token` is optional for LiveAvatar, HeyGen, and Generic avatars. If omitted, AgentKit generates it with the same ConvoAI token path as the agent, using the avatar UID. You can still pass `agora_token` explicitly.

## Sample Rate Constraint

Each avatar vendor requires a specific TTS sample rate. The SDK validates this when you add TTS or avatar configuration and again when the session starts. If the TTS sample rate does not match, a `ValueError` is raised:

```
ValueError: Avatar requires TTS sample rate of 24000 Hz, but TTS is configured with 16000 Hz. Please update your TTS sample_rate to 24000.
```

Python raises this as a `ValueError` — there is no compile-time check as in statically typed languages.

Additionally, if the TTS sample rate is not explicitly available, the SDK issues a warning through the session warning callback:

```
Warning: LiveAvatar avatar detected but TTS sample_rate is not explicitly set. LiveAvatar requires 24,000 Hz. Please ensure your TTS provider is configured for 24kHz.
```

## HeyGen Avatar (24 kHz)

HeyGen requires a TTS vendor configured at 24000 Hz:

```python
from agora_agent import Agent, Agora, Area, OpenAI, ElevenLabsTTS, DeepgramSTT, HeyGenAvatar

client = Agora(
    area=Area.US,
    app_id='your-app-id',
    app_certificate='your-app-certificate',
)

agent = (
    Agent(name='avatar-agent')
    .with_llm(OpenAI(
        api_key='your-openai-key',
        base_url='https://api.openai.com/v1/chat/completions',
        model='gpt-4o-mini',
        system_messages=[{'role': 'system', 'content': 'You are a helpful assistant with a visual avatar.'}],
    ))
    .with_tts(ElevenLabsTTS(
        key='your-elevenlabs-key',
        model_id='eleven_flash_v2_5',
        voice_id='your-voice-id',
        base_url='wss://api.elevenlabs.io/v1',
        sample_rate=24000,  # Must be 24000 for HeyGen
    ))
    .with_stt(DeepgramSTT(api_key='your-deepgram-key', language='en-US'))
    .with_avatar(HeyGenAvatar(
        api_key='your-heygen-key',
        quality='medium',
        agora_uid='2',
        avatar_id='your-avatar-id',
    ))
)

session = agent.create_session(client, channel='avatar-room', agent_uid='1', remote_uids=['100'])
agent_id = session.start()
session.say('Hello! I am your visual assistant.')
session.stop()
```

## Generic Avatar

`GenericAvatar` supports custom avatar providers. `agora_appid`, `agora_channel`, and `agora_token` are optional when using `AgentSession.start()`.

```python
from agora_agent import GenericAvatar

agent = agent.with_avatar(GenericAvatar(
    api_key='your-avatar-provider-key',
    api_base_url='https://avatar-provider.example.com',
    avatar_id='avatar-123',
    agora_uid='2',
))
```

## Akool Avatar (16 kHz)

Akool requires a TTS vendor configured at 16000 Hz:

```python
from agora_agent import ElevenLabsTTS, AkoolAvatar

agent = (
    Agent(name='akool-agent')
    .with_llm(OpenAI(
        api_key='your-openai-key',
        base_url='https://api.openai.com/v1/chat/completions',
        model='gpt-4o-mini',
        system_messages=[{'role': 'system', 'content': 'You are a helpful assistant.'}],
    ))
    .with_tts(ElevenLabsTTS(
        key='your-elevenlabs-key',
        model_id='eleven_flash_v2_5',
        voice_id='your-voice-id',
        base_url='wss://api.elevenlabs.io/v1',
        sample_rate=16000,  # Must be 16000 for Akool
    ))
    .with_stt(DeepgramSTT(api_key='your-deepgram-key', language='en-US'))
    .with_avatar(AkoolAvatar(
        api_key='your-akool-key',
        agora_uid='2',
        avatar_id='your-avatar-id',
    ))
)
```

## Common Mistake: Wrong Sample Rate

This example shows what happens when the TTS sample rate does not match the avatar's requirement:

```python
# This raises ValueError at build time
agent = (
    Agent(name='broken-agent')
    .with_llm(OpenAI(
        api_key='your-openai-key',
        base_url='https://api.openai.com/v1/chat/completions',
        model='gpt-4o-mini',
        system_messages=[{'role': 'system', 'content': 'You are a helpful assistant.'}],
    ))
    .with_tts(ElevenLabsTTS(
        key='your-elevenlabs-key',
        model_id='eleven_flash_v2_5',
        voice_id='your-voice-id',
        base_url='wss://api.elevenlabs.io/v1',
        sample_rate=16000,  # 16 kHz
    ))
    .with_stt(DeepgramSTT(api_key='your-deepgram-key', language='en-US'))
    .with_avatar(HeyGenAvatar(  # Requires 24 kHz — mismatch!
        api_key='your-heygen-key',
        quality='medium',
        agora_uid='2',
    ))
)
# ValueError: Avatar requires TTS sample rate of 24000 Hz, but TTS is configured
# with 16000 Hz. Please update your TTS sample_rate to 24000.
```

**Fix:** Change `sample_rate=16000` to `sample_rate=24000` on the TTS vendor.

## Order Matters

The `with_avatar()` call validates against the currently configured TTS. Always call `with_tts()` before `with_avatar()`:

```python
# Correct order: TTS first, then avatar
agent = (
    Agent(name='my-agent')
    .with_tts(ElevenLabsTTS(key='your-elevenlabs-key', model_id='eleven_flash_v2_5', voice_id='your-voice-id', base_url='wss://api.elevenlabs.io/v1', sample_rate=24000))
    .with_avatar(HeyGenAvatar(api_key='your-heygen-key', quality='medium', agora_uid='2'))
)
```

If you call `with_avatar()` before `with_tts()`, the sample rate check is deferred to `session.start()`, which validates the configuration before making the API call.

## HeyGen Options

| Parameter | Type | Required | Description |
|---|---|---|---|
| `api_key` | `str` | Yes | HeyGen API key |
| `quality` | `str` | Yes | Avatar quality: `low`, `medium`, or `high` |
| `agora_uid` | `str` | Yes | Agora UID for the avatar video stream |
| `agora_token` | `str` | No | Avatar token, generated at session start when omitted |
| `avatar_id` | `str` | No | Avatar ID |
| `disable_idle_timeout` | `bool` | No | Disable idle timeout |
| `activity_idle_timeout` | `int` | No | Idle timeout in seconds |

## Akool Options

| Parameter | Type | Required | Description |
|---|---|---|---|
| `api_key` | `str` | Yes | Akool API key |
| `avatar_id` | `str` | No | Avatar ID |
