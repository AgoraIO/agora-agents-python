---
sidebar_position: 10
title: Low-Level API
description: Direct client.agents.start() usage without the builder pattern.
---

# Low-Level API

For full control over request payloads you can call the generated clients directly and pass raw types such as `StartAgentsRequestProperties`, `Tts_Elevenlabs`, and `StartAgentsRequestPropertiesAsr`. Use this when you need vendor or options not exposed by the agentkit, or when integrating with generated types from the API spec.

## Raw telephony and phone-number APIs

AgentKit focuses on realtime agent session helpers. Telephony call status, call hangup, and phone-number management are exposed through the generated low-level clients:

- `client.telephony` for call status and hangup operations
- `client.phone_numbers` for phone-number list, create, retrieve, update, and delete operations

## Cascading flow (ASR → LLM → TTS)

```python
from agora_agent import Agora, Area
from agora_agent.agents import (
    StartAgentsRequestProperties,
    StartAgentsRequestPropertiesAsr,
    StartAgentsRequestPropertiesLlm,
)
from agora_agent.types.eleven_labs_tts_params import ElevenLabsTtsParams
from agora_agent.types.tts import Tts_Elevenlabs

client = Agora(
    area=Area.US,
    app_id="YOUR_APP_ID",
    app_certificate="YOUR_APP_CERTIFICATE",
    auth_token="your-rest-auth-token",
)
client.agents.start(
    client.app_id,
    name="unique_name",
    properties=StartAgentsRequestProperties(
        channel="channel_name",
        token="token",
        agent_rtc_uid="1001",
        remote_rtc_uids=["1002"],
        idle_timeout=120,
        asr=StartAgentsRequestPropertiesAsr(
            language="en-US",
            vendor="deepgram",
            params={"api_key": "YOUR_DEEPGRAM_API_KEY"},
        ),
        tts=Tts_Elevenlabs(
            params=ElevenLabsTtsParams(
                key="YOUR_ELEVENLABS_API_KEY",
                model_id="eleven_flash_v2_5",
                voice_id="pNInz6obpgDQGcFmaJgB",
                sample_rate=24000,
            ),
        ),
        llm=StartAgentsRequestPropertiesLlm(
            url="https://api.openai.com/v1/chat/completions",
            api_key="<your_llm_key>",
            system_messages=[
                {"role": "system", "content": "You are a helpful chatbot."}
            ],
            params={"model": "gpt-4o-mini"},
            max_history=32,
            greeting_message="Hello, how can I assist you today?",
            failure_message="Please hold on a second.",
        ),
    ),
)
```

## Async (low-level)

```python
import asyncio
from agora_agent import Area, AsyncAgora
from agora_agent.agents import (
    StartAgentsRequestProperties,
    StartAgentsRequestPropertiesAsr,
    StartAgentsRequestPropertiesLlm,
)
from agora_agent.types.eleven_labs_tts_params import ElevenLabsTtsParams
from agora_agent.types.tts import Tts_Elevenlabs

client = AsyncAgora(
    area=Area.US,
    app_id="YOUR_APP_ID",
    app_certificate="YOUR_APP_CERTIFICATE",
    auth_token="your-rest-auth-token",
)

async def main() -> None:
    await client.agents.start(
        client.app_id,
        name="unique_name",
        properties=StartAgentsRequestProperties(
            channel="channel_name",
            token="token",
            agent_rtc_uid="1001",
            remote_rtc_uids=["1002"],
            idle_timeout=120,
            asr=StartAgentsRequestPropertiesAsr(
                language="en-US",
                vendor="deepgram",
                params={"api_key": "YOUR_DEEPGRAM_API_KEY"},
            ),
            tts=Tts_Elevenlabs(
                params=ElevenLabsTtsParams(
                    key="YOUR_ELEVENLABS_API_KEY",
                    model_id="eleven_flash_v2_5",
                    voice_id="pNInz6obpgDQGcFmaJgB",
                    sample_rate=24000,
                ),
            ),
            llm=StartAgentsRequestPropertiesLlm(
                url="https://api.openai.com/v1/chat/completions",
                api_key="<your_llm_key>",
                system_messages=[
                    {"role": "system", "content": "You are a helpful chatbot."}
                ],
                params={"model": "gpt-4o-mini"},
                max_history=32,
                greeting_message="Hello, how can I assist you today?",
                failure_message="Please hold on a second.",
            ),
        ),
    )

asyncio.run(main())
```

## MLLM flow (multimodal)

For real-time audio with OpenAI Realtime or Google Gemini Live, use the MLLM flow instead of the cascading ASR → LLM → TTS flow. See the [MLLM Overview](https://docs.agora.io/en/conversational-ai/models/mllm/overview).

```python
from agora_agent import Agora, Area
from agora_agent.agents import (
    StartAgentsRequestProperties,
    StartAgentsRequestPropertiesMllm,
    StartAgentsRequestPropertiesMllmVendor,
    StartAgentsRequestPropertiesTts,
    StartAgentsRequestPropertiesTtsVendor,
    StartAgentsRequestPropertiesLlm,
)

client = Agora(
    area=Area.US,
    app_id="YOUR_APP_ID",
    app_certificate="YOUR_APP_CERTIFICATE",
    auth_token="your-rest-auth-token",
)

client.agents.start(
    client.app_id,
    name="mllm_agent",
    properties=StartAgentsRequestProperties(
        channel="channel_name",
        token="your_token",
        agent_rtc_uid="1001",
        remote_rtc_uids=["1002"],
        idle_timeout=120,
        mllm=StartAgentsRequestPropertiesMllm(
            enable=True,
            url="wss://api.openai.com/v1/realtime",
            api_key="<your_openai_api_key>",
            vendor=StartAgentsRequestPropertiesMllmVendor.OPENAI,
            params={
                "model": "gpt-4o-realtime-preview",
                "voice": "alloy",
            },
            input_modalities=["audio"],
            output_modalities=["text", "audio"],
            greeting_message="Hello! I'm ready to chat in real-time.",
            turn_detection={
                "mode": "server_vad",
                "server_vad_config": {
                    "idle_timeout_ms": 5000,
                },
            },
        ),
    ),
)
```

For more on the agentkit-based MLLM flow, see [MLLM Flow](./mllm-flow.md).
