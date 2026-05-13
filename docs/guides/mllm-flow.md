---
sidebar_position: 2
title: MLLM Flow (Multimodal)
description: Use OpenAI Realtime or Gemini Live for end-to-end audio processing.
---

# MLLM Flow (Multimodal)

The MLLM (Multimodal LLM) flow uses a single model to handle both audio input and output — no separate STT or TTS step. This gives the model direct access to voice tone, pacing, and emotion.

Two MLLM vendors are supported:

- **OpenAI Realtime** — `gpt-4o-realtime-preview` and related models
- **Gemini Live** — direct Google AI API access for audio-native Gemini models

## Enable MLLM Mode

Call `agent.with_mllm(vendor)` to enable MLLM mode. The builder sets `mllm.enable = True` automatically.

```python
from agora_agent.agentkit import Agent

agent = Agent(
    name='realtime-agent',
    instructions='You are a voice assistant.',
)
```

## OpenAI Realtime

### Sync

```python
from agora_agent import Agora, Area
from agora_agent.agentkit import Agent
from agora_agent.agentkit.vendors import OpenAIRealtime

client = Agora(
    area=Area.US,
    app_id='your-app-id',
    app_certificate='your-app-certificate',
)

agent = (
    Agent(
        name='realtime-agent',
        instructions='You are a helpful voice assistant.',
    )
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
from agora_agent import AsyncAgora, Area
from agora_agent.agentkit import Agent
from agora_agent.agentkit.vendors import OpenAIRealtime

async def main():
    client = AsyncAgora(
        area=Area.US,
        app_id='your-app-id',
        app_certificate='your-app-certificate',
        )

    agent = (
        Agent(
            name='realtime-agent',
            instructions='You are a helpful voice assistant.',
        )
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
from agora_agent import Agora, Area
from agora_agent.agentkit import Agent
from agora_agent.agentkit.vendors import GeminiLive

client = Agora(
    area=Area.AP,
    app_id='your-app-id',
    app_certificate='your-app-certificate',
)

agent = (
    Agent(
        name='gemini-agent',
        instructions='You are a helpful multilingual assistant.',
    )
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

## OpenAI Realtime with Custom Options

```python
from agora_agent.agentkit.vendors import OpenAIRealtime

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
| Vendor flexibility | Limited (OpenAI Realtime or Gemini Live) | Mix and match 4 LLMs, 12 TTS, 10 STT |
| Audio understanding | Model hears tone, pacing, emotion | STT produces text only |

## Next Steps

- For the cascading pipeline, see [Cascading Flow](./cascading-flow.md)
- To add a visual avatar, see [Avatars](./avatars.md)
