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

## Legacy auth modes

The generated client still supports pre-minted REST tokens and HTTP Basic Auth for legacy integrations. Do not use those modes for new session integrations. Use app credentials so AgentKit can mint short-lived ConvoAI REST auth and RTC join tokens for each session.

### HTTP Basic Auth

```python
client = Agora(
    area=Area.US,
    app_id="your-app-id",
    app_certificate="your-app-certificate",
    customer_id="your-customer-id",
    customer_secret="your-customer-secret",
)
print(client.auth_mode)  # "basic"
```

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

`auth_token` is mutually exclusive with `customer_id` / `customer_secret`.

## Client tokens

Browsers and apps need their own token to join the channel and log in to RTM, which carries agent transcripts and state. Mint it on your server with `generate_client_token`:

```python
import os

from agora_agent import generate_client_token

token = generate_client_token(
    app_id=os.environ["AGORA_APP_ID"],
    app_certificate=os.environ["AGORA_APP_CERTIFICATE"],
    channel_name="my-room",
    uid=100,  # or a string user account; also the RTM user ID
    token_expire=3600,
)
```

The token grants RTC (publisher) and RTM login only. Never hand a client a token from `generate_convo_ai_token`: its ConvoAI service authenticates REST calls, so a client holding it could control agents in your project. Keep ConvoAI tokens on the server.
