---
sidebar_position: 2
title: Authentication
description: Configure the Python SDK with app credentials and understand other supported auth modes.
---

# Authentication

Create `Agora` or `AsyncAgora` with `app_id` and `app_certificate` only. The SDK mints a fresh ConvoAI REST token for each API call and generates the RTC join token when the session starts.

## App credentials

```python
from agora_agent import Agent, Agora, Area, DeepgramSTT, OpenAI, MiniMaxTTS

client = Agora(
    area=Area.US,
    app_id="your-app-id",
    app_certificate="your-app-certificate",
)

agent = (
    Agent()
    .with_stt(DeepgramSTT(model="nova-3"))
    .with_llm(OpenAI(
        model="gpt-4o-mini",
        system_messages=[{"role": "system", "content": "Be concise."}],
    ))
    .with_tts(MiniMaxTTS(model="speech_2_6_turbo", voice_id="English_captivating_female1"))
)

session = agent.create_session(
    client,
    channel="room-123",
    agent_uid="1",
    remote_uids=["100"],
)
```

## Why app credentials

- Fresh short-lived tokens per API call instead of reusing long-lived credentials
- No Customer ID / Customer Secret in request headers
- No manual REST or RTC token provisioning in application code

## Inspecting auth mode

```python
print(client.auth_mode)  # "app-credentials"
```

## Legacy auth modes

The generated client still supports pre-minted REST tokens and HTTP Basic Auth for legacy integrations. Do not use those modes for new session integrations. Use app credentials so AgentKit can mint short-lived ConvoAI REST auth and RTC join tokens for each session.
