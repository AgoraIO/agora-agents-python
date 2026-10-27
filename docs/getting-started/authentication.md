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
import time

client = Agora(
    area=Area.US,
    app_id="your-app-id",
    app_certificate="your-app-certificate",
)

agent = (
    Agent(client=client)
    .with_stt(DeepgramSTT(model="nova-3"))
    .with_llm(OpenAI(
        model="gpt-4o-mini",
        system_messages=[{"role": "system", "content": "Be concise."}],
    ))
    .with_tts(MiniMaxTTS(model="speech_2_6_turbo", voice_id="English_captivating_female1"))
)

session = agent.create_session(
    channel=f"demo-channel-{int(time.time())}",
    agent_uid="1",
    remote_uids=["100"],
    name=f"conversation-{int(time.time())}",
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

## Pre-built REST tokens

The public SDK supports token authentication only: pass a raw `auth_token`, or let the SDK sign tokens from `app_id` and `app_certificate`. Customer ID/secret, client ID/secret and Basic authorization overrides are rejected. REST authentication is separate from the optional RTC transport token.

### Pre-built REST token

Pass the raw token string. The SDK sets `Authorization: agora token=<auth_token>` automatically.

```python
client = Agora(
    area=Area.US,
    app_id="your-app-id",
    app_certificate="your-app-certificate",
    auth_token="your-raw-token",
)
print(client.auth_mode)  # "token"
```

New resources use `https://preview.ai.agora.io/conversational-ai/v1/projects/{appid}`. Do not send internal gateway headers or `X-Studio-Region`.
