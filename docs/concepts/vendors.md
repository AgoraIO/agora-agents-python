---
sidebar_position: 4
title: Vendors
description: Typed vendor classes for LLM, TTS, STT, MLLM, and Avatar providers.
---

# Vendors

The SDK provides typed vendor classes for every supported provider. Each vendor class validates its configuration with Pydantic and produces the correct API payload automatically.

All vendor classes are available from `agora_agent.agentkit.vendors`:

<!-- snippet: executable -->
```python
from agora_agent.agentkit.vendors import OpenAI, ElevenLabsTTS, DeepgramTTS, DeepgramSTT
```

## LLM Vendors

Used with `agent.with_llm()` for the cascading flow (ASR → LLM → TTS).

| Class | Provider | Required Parameters |
|---|---|---|
| `OpenAI` | OpenAI | `api_key` |
| `AzureOpenAI` | Azure OpenAI | `api_key`, `endpoint`, `deployment_name` |
| `Anthropic` | Anthropic | `api_key` |
| `Gemini` | Google Gemini | `api_key` |

<!-- snippet: executable -->
```python
from agora_agent.agentkit.vendors import OpenAI

llm = OpenAI(api_key='your-openai-key', model='gpt-4o-mini')
```

## TTS Vendors

Used with `agent.with_tts()`. Each TTS vendor produces audio at a specific sample rate — this matters when using [avatars](../guides/avatars.md).

| Class | Provider | Required Parameters | Sample Rate |
|---|---|---|---|
| `ElevenLabsTTS` | ElevenLabs | `key`, `model_id`, `voice_id` | 16000, 22050, 24000, or 44100 Hz |
| `MicrosoftTTS` | Microsoft Azure | `key`, `region`, `voice_name` | 8000, 16000, 24000, or 48000 Hz |
| `OpenAITTS` | OpenAI | `key`, `voice` | 24000 Hz (fixed) |
| `CartesiaTTS` | Cartesia | `key`, `voice_id` | 8000–48000 Hz |
| `GoogleTTS` | Google Cloud | `key`, `voice_name` | — |
| `AmazonTTS` | Amazon Polly | `access_key`, `secret_key`, `region`, `voice_id` | — |
| `HumeAITTS` | Hume AI | `key` | — |
| `RimeTTS` | Rime | `key`, `speaker` | — |
| `FishAudioTTS` | Fish Audio | `key`, `reference_id` | — |
| `GroqTTS` | Groq | `key` | — |
| `MiniMaxTTS` | MiniMax | `key` | — |
| `DeepgramTTS` | Deepgram | `api_key`, `model` | Configurable |
| `SarvamTTS` | Sarvam | `api_key` | — |

<!-- snippet: executable -->
```python
from agora_agent.agentkit.vendors import ElevenLabsTTS

tts = ElevenLabsTTS(
    key='your-elevenlabs-key',
    model_id='eleven_flash_v2_5',
    voice_id='your-voice-id',
    sample_rate=24000,
)
```

## STT Vendors

Used with `agent.with_stt()`.

| Class | Provider | Required Parameters |
|---|---|---|
| `SpeechmaticsSTT` | Speechmatics | `api_key`, `language` |
| `DeepgramSTT` | Deepgram | — (all optional) |
| `MicrosoftSTT` | Microsoft Azure | `key`, `region` |
| `OpenAISTT` | OpenAI | `api_key` |
| `GoogleSTT` | Google Cloud | `api_key` |
| `AmazonSTT` | Amazon Transcribe | `access_key`, `secret_key`, `region` |
| `AssemblyAISTT` | AssemblyAI | `api_key` |
| `AresSTT` | Ares | — (all optional) |
| `SarvamSTT` | Sarvam | `api_key`, `language` |

<!-- snippet: executable -->
```python
from agora_agent.agentkit.vendors import DeepgramSTT

stt = DeepgramSTT(api_key='your-deepgram-key', language='en-US', model='nova-2')
```

## MLLM Vendors

Used with `agent.with_mllm()` for the [MLLM flow](../guides/mllm-flow.md). These handle audio input and output end-to-end.

| Class | Provider | Required Parameters |
|---|---|---|
| `OpenAIRealtime` | OpenAI Realtime | `api_key`; optional `turn_detection` |
| `GeminiLive` | Google Gemini Live API | `api_key`, `model`; optional `turn_detection` |
| `VertexAI` | Vertex AI (Gemini Live) | `model`, `project_id`, `location`, `adc_credentials_string`; optional `turn_detection` |

<!-- snippet: executable -->
```python
from agora_agent.agentkit.vendors import OpenAIRealtime

mllm = OpenAIRealtime(api_key='your-openai-key', model='gpt-4o-realtime-preview')
```

## Avatar Vendors

Used with `agent.with_avatar()`. Avatars require specific TTS sample rates — see [Avatar Integration](../guides/avatars.md).

| Class | Provider | Required Parameters | Required TTS Sample Rate |
|---|---|---|---|
| `HeyGenAvatar` | HeyGen | `api_key`, `quality`, `agora_uid` | 24000 Hz |
| `AkoolAvatar` | Akool | `api_key`, `agora_uid` | 16000 Hz |

<!-- snippet: executable -->
```python
from agora_agent.agentkit.vendors import HeyGenAvatar

avatar = HeyGenAvatar(api_key='your-heygen-key', quality='medium', agora_uid='2')
```

## Base Classes

If you need to create a custom vendor, extend the appropriate base class:

| Base Class | Abstract Method |
|---|---|
| `BaseLLM` | `to_config() -> Dict[str, Any]` |
| `BaseTTS` | `to_config() -> Dict[str, Any]`, `sample_rate -> Optional[int]` |
| `BaseSTT` | `to_config() -> Dict[str, Any]` |
| `BaseMLLM` | `to_config() -> Dict[str, Any]` |
| `BaseAvatar` | `to_config() -> Dict[str, Any]`, `required_sample_rate -> int` |

For the full constructor options for every vendor, see the [Vendor Reference](../reference/vendors.md).
