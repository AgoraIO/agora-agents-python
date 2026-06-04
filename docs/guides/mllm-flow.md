---
sidebar_position: 2
title: MLLM Flow (Multimodal)
description: Use OpenAI Realtime, Gemini Live, Vertex AI, or xAI for end-to-end audio processing.
---

# MLLM Flow (Multimodal)

The MLLM (Multimodal LLM) flow uses a single model to handle both audio input and output — no separate STT or TTS step. This gives the model direct access to voice tone, pacing, and emotion.

MLLM vendors supported by AgentKit:

- **OpenAI Realtime** — `gpt-4o-realtime-preview` and related models
- **Gemini Live** — direct Google AI API access for audio-native Gemini models
- **Vertex AI** — Gemini Live through Google Cloud Vertex AI
- **xAI Grok** — xAI Realtime API

## Enable MLLM Mode

Call `agent.with_mllm(vendor)` to enable MLLM mode. The builder sets `mllm.enable = True` automatically. MLLM sessions do not require TTS, STT, or LLM vendors. Avatars are currently supported only with the cascading ASR + LLM + TTS pipeline.

```python
from agora_agent import Agent

agent = Agent(name='realtime-agent')
```

## OpenAI Realtime

### Sync

```python
from agora_agent import Agent, Agora, Area, OpenAIRealtime

client = Agora(
    area=Area.US,
    app_id='your-app-id',
    app_certificate='your-app-certificate',
)

agent = (
    Agent(name='realtime-agent')
    .with_mllm(OpenAIRealtime(
        api_key='your-openai-key',
        model='gpt-4o-realtime-preview',
    ))
)

session = agent.create_session(client, channel='realtime-room', agent_uid='1', remote_uids=['100'])
agent_id = session.start()
# Agent handles audio end-to-end — no separate STT/TTS needed
session.stop()
```

### Async

```python
import asyncio
from agora_agent import Agent, AsyncAgora, Area, OpenAIRealtime

async def main():
    client = AsyncAgora(
        area=Area.US,
        app_id='your-app-id',
        app_certificate='your-app-certificate',
        )

    agent = (
        Agent(name='realtime-agent')
        .with_mllm(OpenAIRealtime(
            api_key='your-openai-key',
            model='gpt-4o-realtime-preview',
        ))
    )

    session = agent.create_session(client, channel='realtime-room', agent_uid='1', remote_uids=['100'])
    agent_id = await session.start()
    await session.stop()

asyncio.run(main())
```

## Gemini Live

Gemini Live uses a Google AI API key:

```python
from agora_agent import Agent, Agora, Area, GeminiLive

client = Agora(
    area=Area.AP,
    app_id='your-app-id',
    app_certificate='your-app-certificate',
)

agent = (
    Agent(name='gemini-agent')
    .with_mllm(GeminiLive(
        api_key='your-google-ai-api-key',
        model='gemini-live-2.5-flash',
        voice='Aoede',
    ))
)

session = agent.create_session(client, channel='gemini-room', agent_uid='1', remote_uids=['100'])
agent_id = session.start()
session.stop()
```

## xAI Grok

```python
from agora_agent import Agent, Agora, Area, XaiGrok

client = Agora(area=Area.US, app_id='your-app-id', app_certificate='your-app-certificate')

agent = (
    Agent(name='xai-agent')
    .with_mllm(XaiGrok(
        api_key='your-xai-key',
        voice='eve',
        language='en',
        sample_rate=24000,
        output_modalities=['audio', 'text'],
    ))
)

session = agent.create_session(client, channel='xai-room', agent_uid='1', remote_uids=['100'])
agent_id = session.start()
session.stop()
```

For xAI turn detection, use `mllm.turn_detection` with `agora_vad` or `server_vad`.

## OpenAI Realtime with Custom Options

```python
from agora_agent import OpenAIRealtime

mllm = OpenAIRealtime(
    api_key='your-openai-key',
    model='gpt-4o-realtime-preview',
    url='wss://custom-endpoint.example.com',
    greeting_message='Hello! I am ready to help.',
    input_modalities=['audio', 'text'],
    output_modalities=['audio', 'text'],
    params={'temperature': 0.8},
)
```

## When to Use MLLM vs. Cascading

| Consideration | MLLM | Cascading |
|---|---|---|
| Latency | Lower — single model, no pipeline | Higher — three models in sequence |
| Voice control | Model-dependent | Full vendor choice for TTS |
| Vendor flexibility | Limited to supported MLLM providers (OpenAI Realtime, Gemini Live, Vertex AI, xAI Grok) | Mix and match LLM, TTS, and STT vendors |
| Audio understanding | Model hears tone, pacing, emotion | STT produces text only |

## Next Steps

- For the cascading pipeline, see [Cascading Flow](./cascading-flow.md)
- To add a visual avatar, use the cascading pipeline and see [Avatars](./avatars.md)
