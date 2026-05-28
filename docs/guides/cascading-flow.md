---
sidebar_position: 1
title: Cascading Flow (ASR → LLM → TTS)
description: Build a voice agent using Speech-to-Text, a text LLM, and Text-to-Speech.
---

# Cascading Flow (ASR → LLM → TTS)

The cascading flow is the most common pattern for building voice agents. Audio from a user is transcribed by an STT (ASR) vendor, the transcript is sent to an LLM for a response, and the response is rendered as audio by a TTS vendor.

```
User audio → STT → LLM → TTS → Agent audio
```

## Combo 1: OpenAI + ElevenLabs + Deepgram

### Sync

```python
from agora_agent import Agent, Agora, Area, OpenAI, ElevenLabsTTS, DeepgramSTT

client = Agora(
    area=Area.US,
    app_id='your-app-id',
    app_certificate='your-app-certificate',
)

agent = (
    Agent(name='assistant', instructions='You are a friendly customer support agent.')
    .with_llm(OpenAI(api_key='your-openai-key', model='gpt-4o-mini'))
    .with_tts(ElevenLabsTTS(key='your-elevenlabs-key', model_id='eleven_flash_v2_5', voice_id='your-voice-id', sample_rate=24000))
    .with_stt(DeepgramSTT(api_key='your-deepgram-key', language='en-US', model='nova-2'))
)

session = agent.create_session(client, channel='support-room', agent_uid='1', remote_uids=['100'])
agent_id = session.start()
session.say('Welcome! How can I assist you today?')
# ... agent listens and responds automatically ...
session.stop()
```

### Async

```python
import asyncio
from agora_agent import Agent, AsyncAgora, Area, OpenAI, ElevenLabsTTS, DeepgramSTT

async def main():
    client = AsyncAgora(
        area=Area.US,
        app_id='your-app-id',
        app_certificate='your-app-certificate',
        )

    agent = (
        Agent(name='assistant', instructions='You are a friendly customer support agent.')
        .with_llm(OpenAI(api_key='your-openai-key', model='gpt-4o-mini'))
        .with_tts(ElevenLabsTTS(key='your-elevenlabs-key', model_id='eleven_flash_v2_5', voice_id='your-voice-id', sample_rate=24000))
        .with_stt(DeepgramSTT(api_key='your-deepgram-key', language='en-US', model='nova-2'))
    )

    session = agent.create_session(client, channel='support-room', agent_uid='1', remote_uids=['100'])
    agent_id = await session.start()
    await session.say('Welcome! How can I assist you today?')
    # ... agent listens and responds automatically ...
    await session.stop()

asyncio.run(main())
```

## Combo 2: Azure OpenAI + Microsoft TTS + Microsoft STT

This combination keeps everything within the Azure ecosystem:

```python
from agora_agent import Agent, Agora, Area, AzureOpenAI, MicrosoftTTS, MicrosoftSTT

client = Agora(
    area=Area.EU,
    app_id='your-app-id',
    app_certificate='your-app-certificate',
)

agent = (
    Agent(name='azure-agent', instructions='You are a helpful assistant for enterprise customers.')
    .with_llm(AzureOpenAI(
        api_key='your-azure-key',
        endpoint='https://your-resource.openai.azure.com',
        deployment_name='gpt-4o-mini',
    ))
    .with_tts(MicrosoftTTS(
        key='your-azure-speech-key',
        region='eastus',
        voice_name='en-US-JennyNeural',
        sample_rate=24000,
    ))
    .with_stt(MicrosoftSTT(
        key='your-azure-speech-key',
        region='eastus',
        language='en-US',
    ))
)

session = agent.create_session(client, channel='enterprise-room', agent_uid='1', remote_uids=['100'])
agent_id = session.start()
session.say('Hello! I am your enterprise assistant.')
session.stop()
```

## Customizing the LLM

All LLM vendors support optional parameters for fine-tuning:

```python
from agora_agent import OpenAI

llm = OpenAI(
    api_key='your-openai-key',
    model='gpt-4o-mini',
    temperature=0.7,
    top_p=0.9,
    max_tokens=1024,
)
```

## Adding a Greeting

The `greeting` parameter on `Agent` makes the agent speak automatically when the session starts:

```python
agent = Agent(
    name='greeter',
    instructions='You are a helpful assistant.',
    greeting='Hi there! What can I do for you?',
)
```

## Next Steps

- For audio-native models, see [MLLM Flow](./mllm-flow.md)
- To add a visual avatar, see [Avatars](./avatars.md)
- For the full vendor catalog, see [Vendors](../concepts/vendors.md)
