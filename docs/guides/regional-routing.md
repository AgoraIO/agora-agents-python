---
sidebar_position: 4
title: Regional Routing
description: Configure the Agora client to route requests to the nearest Agora region.
---

# Regional Routing

The `Agora` and `AsyncAgora` clients use a domain pool to route API requests to the nearest Agora region. This is configured via the `Area` enum.

## Area enum

```python
from agora_agent import Area
```

| Value | Region |
|---|---|
| `Area.US` | United States (west + east) |
| `Area.EU` | Europe (west + central) |
| `Area.AP` | Asia-Pacific (southeast + northeast) |
| `Area.CN` | Chinese mainland (east + north) |

Pass the area when creating the client:

```python
from agora_agent import Agora, Area

client = Agora(
    area=Area.EU,
    app_id="your-app-id",
    app_certificate="your-app-certificate",
)
```

## Recommended vendors by area

Bind `client` into `Agent(client=client, ...)` and construct vendors directly with SDK classes. The bound client selects `CNAgent` or `GlobalAgent` for IDE hints based on `area`, but does not restrict which vendor classes you can configure.

| Client area | STT classes | LLM classes | TTS classes | Avatar classes |
|---|---|---|---|---|
| `Area.US`, `Area.EU`, `Area.AP` | `DeepgramSTT`, `SpeechmaticsSTT`, `MicrosoftSTT`, `OpenAISTT`, `GoogleSTT`, `AmazonSTT`, `AssemblyAISTT`, `AresSTT`, `SarvamSTT`, `XaiSTT` | `OpenAI`, `AzureOpenAI`, `Anthropic`, `Gemini`, `Groq`, `VertexAILLM`, `AmazonBedrock`, `Dify`, `CustomLLM` | `ElevenLabsTTS`, `MicrosoftTTS`, `OpenAITTS`, `CartesiaTTS`, `GoogleTTS`, `AmazonTTS`, `DeepgramTTS`, `HumeAITTS`, `RimeTTS`, `FishAudioTTS`, `MiniMaxTTS`, `MurfTTS`, `SarvamTTS`, `GenericTTS`, `XaiTTS` | `LiveAvatarAvatar`, `HeyGenAvatar`, `AkoolAvatar`, `AnamAvatar`, `GenericAvatar` |
| `Area.CN` | `FengmingSTT`, `TencentSTT`, `MicrosoftCNSTT`, `XfyunSTT`, `XfyunBigModelSTT`, `XfyunDialectSTT` | `AliyunLLM`, `BytedanceLLM`, `DeepSeekLLM`, `TencentLLM` | `MiniMaxCNTTS`, `TencentTTS`, `BytedanceTTS`, `MicrosoftCNTTS`, `CosyVoiceTTS`, `BytedanceDuplexTTS`, `StepFunTTS`, `GenericTTS` | `SenseTimeAvatar`, `SpatiusAvatar` |

Global client example:

```python
from agora_agent import Agent, Agora, Area, DeepgramSTT, MiniMaxTTS, OpenAI
import time

client = Agora(
    area=Area.US,
    app_id="your-app-id",
    app_certificate="your-app-certificate",
)

agent = (
    Agent(
        client=client,
        turn_detection={"language": "en-US"},
    )
    .with_stt(DeepgramSTT(model="nova-3", language="en-US"))
    .with_llm(OpenAI(model="gpt-4o-mini"))
    .with_tts(MiniMaxTTS(
        model="speech_2_6_turbo",
        voice_id="English_captivating_female1",
    ))
)

session = agent.create_session(
    channel=f"demo-channel-{int(time.time())}",
    agent_uid="1001",
    remote_uids=["*"],
    name=f"conversation-{int(time.time())}",
)
```

CN client example:

```python
import os

from agora_agent import Agent, Agora, Area, AliyunLLM, FengmingSTT, MiniMaxCNTTS
import time

client = Agora(
    area=Area.CN,
    app_id="your-app-id",
    app_certificate="your-app-certificate",
)

agent = (
    Agent(
        client=client,
        turn_detection={"language": "zh-CN"},
    )
    .with_stt(FengmingSTT())
    .with_llm(AliyunLLM(
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        model="qwen-plus",
        api_key=os.environ["ALIYUN_API_KEY"],
    ))
    .with_tts(MiniMaxCNTTS(
        key=os.environ["MINIMAX_API_KEY"],
        model="speech-01-turbo",
        voice_id="female-shaonv",
        sample_rate=16000,
    ))
)

session = agent.create_session(
    channel=f"demo-channel-{int(time.time())}",
    agent_uid="1001",
    remote_uids=["*"],
    name=f"conversation-{int(time.time())}",
)
```

## Area-aware agent construction

```python
from agora_agent import Agent

agent = Agent(client=client, turn_detection={"language": "zh-CN"})
```

`Agent(client=...)` returns `CNAgent` for `Area.CN` and `GlobalAgent` for global areas. A bound `client` is required. The SDK does not reject mismatched vendor classes at build time or session start.

## How the domain pool works

Each area has two regional domain prefixes and two domain suffixes. The `Pool` class:

1. Starts with the first regional prefix and the first domain suffix
2. Resolves the best domain suffix via DNS every **30 seconds**
3. Constructs the full URL as `https://{prefix}.{suffix}/api/conversational-ai-agent` for global areas, and `https://{prefix}.{suffix}/cn/api/conversational-ai-agent` for `Area.CN`

## Region-to-domain mapping

| Area | Primary prefix | Fallback prefix | Primary suffix | Fallback suffix |
|---|---|---|---|---|
| `Area.US` | `api-us-west-1` | `api-us-east-1` | `agora.io` | `sd-rtn.com` |
| `Area.EU` | `api-eu-west-1` | `api-eu-central-1` | `agora.io` | `sd-rtn.com` |
| `Area.AP` | `api-ap-southeast-1` | `api-ap-northeast-1` | `agora.io` | `sd-rtn.com` |
| `Area.CN` | `api-cn-east-1` | `api-cn-north-1` | `sd-rtn.com` | `agora.io` |

Note: `Area.CN` uses `sd-rtn.com` as the primary suffix and the `/cn/api/conversational-ai-agent` path.

## Manual failover

If a request fails, call `client.next_region()` to cycle to the next domain prefix, then retry:

```python
from agora_agent import Agent, Agora, Area, DeepgramSTT, ElevenLabsTTS, OpenAI
import time

client = Agora(
    area=Area.EU,
    app_id="your-app-id",
    app_certificate="your-app-certificate",
)

agent = (
    Agent(client=client)
    .with_llm(OpenAI(
        api_key="your-openai-key",
        base_url="https://api.openai.com/v1/chat/completions",
        model="gpt-4o-mini",
        system_messages=[{"role": "system", "content": "You are helpful."}],
    ))
    .with_tts(ElevenLabsTTS(
        key="your-elevenlabs-key",
        model_id="eleven_flash_v2_5",
        voice_id="your-voice-id",
        base_url="wss://api.elevenlabs.io/v1",
        sample_rate=24000,
    ))
    .with_stt(DeepgramSTT(
        api_key="your-deepgram-key",
        model="nova-2",
    ))
)

session = agent.create_session(
    channel=f"demo-channel-{int(time.time())}",
    agent_uid="1",
    remote_uids=["100"],
    name=f"conversation-{int(time.time())}",
)

try:
    session.start()
except Exception as err:
    print(f"First attempt failed, cycling region: {err}")
    client.next_region()
    session.start()
```

## Additional methods

| Method | `Agora` | `AsyncAgora` | Description |
|---|---|---|---|
| `next_region()` | sync | sync | Cycle to the next domain prefix in the pool |
| `select_best_domain()` | sync | `async` (requires `await`) | Trigger a manual DNS resolution check |
| `get_current_url()` | sync | sync | Inspect the full URL currently being used |
| `pool` | sync | sync | Access the `Pool` instance for advanced usage |

```python
print(client.get_current_url())

client.select_best_domain()

# AsyncAgora requires await:
# await client.select_best_domain()
```
