---
sidebar_position: 2
title: Authentication
description: Configure the Python SDK with app credentials and understand other supported auth modes.
---

# Authentication

By default, create `Agora` or `AsyncAgora` with `app_id` and `app_certificate`. The SDK mints a fresh ConvoAI REST token for each API call and generates the RTC join token when the session starts.

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

The SDK supports Token007 and Basic REST authentication. Pass a raw `auth_token`, let the SDK sign tokens from `app_id` and `app_certificate`, or configure a Customer ID/Secret pair. REST authentication is separate from the optional RTC transport token.

### Pre-built REST token

Pass the raw token string. The SDK sets `Authorization: agora token=<auth_token>` automatically.

```python
client = Agora(
    area=Area.US,
    app_id="your-app-id",
    auth_token="your-raw-token",  # No certificate needed for prebuilt REST auth.
)
print(client.auth_mode)  # "token"
```

New resources use `https://preview.ai.agora.io/conversational-ai/v1/projects/{appid}`. Do not send internal gateway headers or `X-Studio-Region`.

A client with only a REST `auth_token` or Basic credentials cannot generate RTC join tokens. Supply `token=` when starting an ordinary legacy RTC session, or also configure the App Certificate for RTC signing. Saved/ephemeral RTC sessions accept their optional token through `transport.token`.

## Basic REST authentication

```python
client = Agora(
    area=Area.US,
    app_id="your-app-id",
    customer_id="your-customer-id",
    customer_secret="your-customer-secret",
    # app_certificate="your-app-certificate",  # Optional RTC token signing.
)
print(client.auth_mode)  # "basic"
```

The same options work with `AsyncAgora`. Both credentials must be nonempty, and Customer ID must not contain a colon. Do not combine them with `auth_token`. The SDK sends `Authorization: Basic <base64(customer_id:customer_secret)>` on REST requests, including saved-agent and ephemeral sessions. An optional App Certificate signs RTC tokens without replacing Basic REST authentication.

For low-level overrides, a valid Basic `Authorization` header is accepted in request options. Configure credentials on the SDK client instead of attaching `httpx.BasicAuth` to the underlying HTTP client, which would silently override SDK authentication.
