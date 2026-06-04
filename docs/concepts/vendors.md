---
sidebar_position: 4
title: Vendors
description: Typed vendor classes for LLM, TTS, STT, MLLM, and Avatar providers.
---

# Vendors

The SDK provides typed vendor classes for every supported provider. Each vendor class validates its configuration with Pydantic and produces the correct API payload automatically.

All vendor classes are imported from `agora_agent`.

<!-- snippet: executable -->
```python
from agora_agent import OpenAI, ElevenLabsTTS, DeepgramTTS, DeepgramSTT
```

## LLM Vendors

Used with `agent.with_llm()` for the cascading flow (ASR → LLM → TTS).

| Class | Provider | Required Parameters |
|---|---|---|
| `OpenAI` | OpenAI | `model` for Agora-managed models; `api_key`, `base_url`, `model` for BYOK |
| `AzureOpenAI` | Azure OpenAI | `api_key`, `model`, `endpoint`, `deployment_name` |
| `Anthropic` | Anthropic | `api_key`, `model`, `url`, `headers`, `max_tokens` |
| `Gemini` | Google Gemini | `api_key`, `model` |
| `Groq` | Groq | `api_key`, `model`, `base_url` |
| `VertexAILLM` | Google Vertex AI | `api_key`, `model`, `project_id`, `location` |
| `AmazonBedrock` | Amazon Bedrock | `access_key`, `secret_key`, `region`, `model` |
| `Dify` | Dify | `api_key`, `url`, `model` |
| `CustomLLM` | OpenAI-compatible LLM | `api_key`, `base_url`, `model` |

<!-- snippet: executable -->
```python
from agora_agent import OpenAI

llm = OpenAI(api_key='your-openai-key', base_url='https://api.openai.com/v1/chat/completions', model='gpt-4o-mini')
```

## TTS Vendors

Used with `agent.with_tts()`. Each TTS vendor produces audio at a specific sample rate — this matters when using [avatars](../guides/avatars.md).

| Class | Provider | Required Parameters | Sample Rate |
|---|---|---|---|
| `ElevenLabsTTS` | ElevenLabs | `key`, `model_id`, `voice_id`, `base_url` | 16000, 22050, 24000, or 44100 Hz |
| `MicrosoftTTS` | Microsoft Azure | `key`, `region`, `voice_name` | 8000, 16000, 24000, or 48000 Hz |
| `OpenAITTS` | OpenAI | `voice` for Agora-managed `tts-1`; `api_key`, `model`, `base_url`, `voice` for BYOK | 24000 Hz (fixed) |
| `CartesiaTTS` | Cartesia | `api_key`, `voice_id`, `model_id` | 8000–48000 Hz |
| `GoogleTTS` | Google Cloud | `key`, `voice_name` | — |
| `AmazonTTS` | Amazon Polly | `access_key`, `secret_key`, `region`, `voice_id`, `engine` | — |
| `HumeAITTS` | Hume AI | `key`, `voice_id`, `provider` | — |
| `RimeTTS` | Rime | `key`, `speaker`, `model_id` | — |
| `FishAudioTTS` | Fish Audio | `key`, `reference_id`, `backend` | — |
| `GroqTTS` | Groq | `key` | — |
| `MiniMaxTTS` | MiniMax | `model` for supported Agora-managed models; `key`, `group_id`, `model`, `voice_id`, `url` for BYOK | — |
| `DeepgramTTS` | Deepgram | `api_key`, `model` | Configurable |
| `SarvamTTS` | Sarvam | `api_key` | — |

<!-- snippet: executable -->
```python
from agora_agent import ElevenLabsTTS

tts = ElevenLabsTTS(
    key='your-elevenlabs-key',
    model_id='eleven_flash_v2_5',
    voice_id='your-voice-id',
    base_url='wss://api.elevenlabs.io/v1',
    sample_rate=24000,
)
```

## STT Vendors

Used with `agent.with_stt()`.

Use `turn_detection.language` for Agora interaction language; it defaults to `en-US`. STT vendor `language` options are serialized under `asr.params` using each provider's own format.

| Class | Provider | Required Parameters |
|---|---|---|
| `SpeechmaticsSTT` | Speechmatics | `api_key`, `language` |
| `DeepgramSTT` | Deepgram | `model` for Agora-managed `nova-2`/`nova-3`; `api_key` for BYOK |
| `MicrosoftSTT` | Microsoft Azure | `key`, `region`, `language` |
| `OpenAISTT` | OpenAI | `api_key` |
| `GoogleSTT` | Google Cloud | `project_id`, `location`, `adc_credentials_string`, `language` |
| `AmazonSTT` | Amazon Transcribe | `access_key`, `secret_key`, `region`, `language` |
| `AssemblyAISTT` | AssemblyAI | `api_key`, `language` |
| `AresSTT` | Ares | — (all optional) |
| `SarvamSTT` | Sarvam | `api_key`, `language` |

<!-- snippet: executable -->
```python
from agora_agent import DeepgramSTT

stt = DeepgramSTT(api_key='your-deepgram-key', language='en-US', model='nova-2')
```

## MLLM Vendors

Used with `agent.with_mllm()` for the [MLLM flow](../guides/mllm-flow.md). These handle audio input and output end-to-end.

| Class | Provider | Required Parameters |
|---|---|---|
| `OpenAIRealtime` | OpenAI Realtime | `api_key`; optional `turn_detection` |
| `GeminiLive` | Google Gemini Live API | `api_key`, `model`; optional `turn_detection` |
| `VertexAI` | Vertex AI (Gemini Live) | `model`, `project_id`, `location`, `adc_credentials_string`; optional `turn_detection` |
| `XaiGrok` | xAI Grok (`mllm.vendor`: `xai`) | `api_key`; optional `voice`, `language`, `sample_rate`, `turn_detection` |

<!-- snippet: executable -->
```python
from agora_agent import OpenAIRealtime

mllm = OpenAIRealtime(api_key='your-openai-key', model='gpt-4o-realtime-preview')
```

## Avatar Vendors

Used with `agent.with_avatar()` in the cascading ASR + LLM + TTS pipeline. Some avatars require specific TTS sample rates — see [Avatar Integration](../guides/avatars.md).

| Class | Provider | Required Parameters | Required TTS Sample Rate |
|---|---|---|---|
| `HeyGenAvatar` | HeyGen (deprecated alias) | `api_key`, `quality`, `agora_uid` | 24000 Hz |
| `LiveAvatarAvatar` | LiveAvatar | `api_key`, `quality`, `agora_uid` | 24000 Hz |
| `AkoolAvatar` | Akool | `api_key` | 16000 Hz |
| `AnamAvatar` | Anam | `api_key` | None |
| `GenericAvatar` | Generic Avatar | `api_key`, `api_base_url`, `avatar_id`, `agora_uid` | None |

<!-- snippet: executable -->
```python
from agora_agent import HeyGenAvatar

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
