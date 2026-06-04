---
sidebar_position: 3
title: Quick Start
description: Build and run your first Agora Conversational AI agent in Python with app credentials and the builder API.
---

# Quick Start

This guide starts with the standard AgentKit path:

- `app_id`, `app_certificate`, and `area` on `Agora` or `AsyncAgora`
- the `Agent` builder with `.with_stt()`, `.with_llm()`, and `.with_tts()`
- automatic ConvoAI REST auth and RTC join token generation
- no vendor API keys when using supported Agora-managed models

## Sync example

```python
from agora_agent import Agent, Agora, Area, DeepgramSTT, OpenAI, MiniMaxTTS


def main() -> None:
    client = Agora(
        area=Area.US,
        app_id="your-app-id",
        app_certificate="your-app-certificate",
    )

    agent = (
        Agent(name="support-assistant")
        .with_stt(DeepgramSTT(model="nova-3", language="en"))
        .with_llm(OpenAI(
            model="gpt-4o-mini",
            system_messages=[{"role": "system", "content": "You are a concise support voice assistant."}],
            greeting_message="Hello! How can I help you today?",
            max_history=10,
        ))
        .with_tts(MiniMaxTTS(model="speech_2_6_turbo", voice_id="English_captivating_female1"))
    )

    session = agent.create_session(
        client,
        channel="support-room-123",
        agent_uid="1",
        remote_uids=["100"],
        idle_timeout=120,
    )

    agent_session_id = session.start()
    print(f"Agent started: {agent_session_id}")

    session.say("Thanks for calling Agora support.")
    session.stop()


if __name__ == "__main__":
    main()
```

## What this does

1. `Agora` runs in app-credentials mode when you pass `app_id` and `app_certificate` only.
2. `Agent` holds reusable behavior such as instructions, greeting, and history settings.
3. Vendor classes on the builder select the ASR, LLM, and TTS stack. Leave vendor credentials unset for supported Agora-managed models, or provide keys when you want BYOK.
4. `session.start()` generates the required auth tokens and returns the unique agent session ID.

## Async applications

For `asyncio` services, switch to `AsyncAgora` and `await` the session methods. The builder and app-credentials flow stay the same.

## When to use BYOK instead

Use the builder without vendor API keys when you are using supported Agora-managed models.

Use BYOK when you need to:

- supply your own vendor API keys
- use models outside the Agora-managed catalog
- point at custom vendor endpoints
- manage vendor-specific parameters directly

See [BYOK Guide](../guides/byok.md).

## Next steps

- [Authentication](./authentication.md)
- [BYOK Guide](../guides/byok.md)
- [MLLM Flow](../guides/mllm-flow.md)
- [Agent Reference](../reference/agent.md)
