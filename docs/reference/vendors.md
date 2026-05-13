---
sidebar_position: 4
title: Vendor Reference
description: Constructor options for all LLM, TTS, STT, MLLM, and Avatar vendor classes.
---

# Vendor Reference

All vendor classes are available from `agora_agent.agentkit.vendors`:

<!-- snippet: fragment -->
```python
from agora_agent.agentkit.vendors import OpenAI, ElevenLabsTTS, DeepgramTTS, DeepgramSTT, OpenAIRealtime, GeminiLive, HeyGenAvatar
```

---

## LLM Vendors

### `OpenAI`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | OpenAI API key |
| `model` | `str` | No | `gpt-4o-mini` | Model name |
| `base_url` | `str` | No | `None` | Custom base URL (overrides default OpenAI endpoint) |
| `temperature` | `float` | No | `None` | Sampling temperature (0.0–2.0) |
| `top_p` | `float` | No | `None` | Nucleus sampling (0.0–1.0) |
| `max_tokens` | `int` | No | `None` | Maximum tokens to generate |
| `system_messages` | `List[Dict]` | No | `None` | System messages |
| `greeting_message` | `str` | No | `None` | Greeting message |
| `failure_message` | `str` | No | `None` | Failure message |
| `input_modalities` | `List[str]` | No | `None` | Input modalities |
| `output_modalities` | `List[str]` | No | `None` | Output modalities |
| `params` | `Dict[str, Any]` | No | `None` | Additional model parameters |
| `headers` | `Dict[str, str]` | No | `None` | Custom HTTP headers forwarded to the LLM provider |
| `greeting_configs` | `Dict[str, Any]` | No | `None` | Greeting playback configuration |
| `template_variables` | `Dict[str, str]` | No | `None` | Template variables for messages |

<!-- snippet: fragment -->
```python
from agora_agent.agentkit.vendors import OpenAI

llm = OpenAI(api_key='your-key', model='gpt-4o-mini', temperature=0.7)
```

### `AzureOpenAI`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | Azure OpenAI API key |
| `endpoint` | `str` | Yes | — | Azure endpoint URL |
| `deployment_name` | `str` | Yes | — | Azure deployment name |
| `api_version` | `str` | No | `2024-08-01-preview` | Azure API version |
| `temperature` | `float` | No | `None` | Sampling temperature (0.0–2.0) |
| `top_p` | `float` | No | `None` | Nucleus sampling (0.0–1.0) |
| `max_tokens` | `int` | No | `None` | Maximum tokens |
| `system_messages` | `List[Dict]` | No | `None` | System messages |
| `greeting_message` | `str` | No | `None` | Greeting message |
| `failure_message` | `str` | No | `None` | Failure message |
| `input_modalities` | `List[str]` | No | `None` | Input modalities |
| `output_modalities` | `List[str]` | No | `None` | Output modalities |
| `params` | `Dict[str, Any]` | No | `None` | Additional model parameters |
| `headers` | `Dict[str, str]` | No | `None` | Custom HTTP headers forwarded to the LLM provider |
| `greeting_configs` | `Dict[str, Any]` | No | `None` | Greeting playback configuration |
| `template_variables` | `Dict[str, str]` | No | `None` | Template variables for messages |

<!-- snippet: fragment -->
```python
from agora_agent.agentkit.vendors import AzureOpenAI

llm = AzureOpenAI(
    api_key='your-azure-key',
    endpoint='https://your-resource.openai.azure.com',
    deployment_name='gpt-4o-mini',
)
```

### `Anthropic`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | Anthropic API key |
| `model` | `str` | No | `claude-3-5-sonnet-20241022` | Model name |
| `max_tokens` | `int` | No | `None` | Maximum tokens |
| `temperature` | `float` | No | `None` | Sampling temperature (0.0–1.0) |
| `top_p` | `float` | No | `None` | Nucleus sampling (0.0–1.0) |
| `system_messages` | `List[Dict]` | No | `None` | System messages |
| `greeting_message` | `str` | No | `None` | Greeting message |
| `failure_message` | `str` | No | `None` | Failure message |
| `input_modalities` | `List[str]` | No | `None` | Input modalities |
| `output_modalities` | `List[str]` | No | `None` | Output modalities |
| `params` | `Dict[str, Any]` | No | `None` | Additional model parameters |
| `headers` | `Dict[str, str]` | No | `None` | Custom HTTP headers forwarded to the LLM provider |
| `greeting_configs` | `Dict[str, Any]` | No | `None` | Greeting playback configuration |
| `template_variables` | `Dict[str, str]` | No | `None` | Template variables for messages |

<!-- snippet: fragment -->
```python
from agora_agent.agentkit.vendors import Anthropic

llm = Anthropic(api_key='your-anthropic-key', model='claude-3-5-sonnet-20241022')
```

### `Gemini`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | Google AI API key |
| `model` | `str` | No | `gemini-2.0-flash-exp` | Model name |
| `temperature` | `float` | No | `None` | Sampling temperature (0.0–2.0) |
| `top_p` | `float` | No | `None` | Nucleus sampling (0.0–1.0) |
| `top_k` | `int` | No | `None` | Top-k sampling |
| `max_output_tokens` | `int` | No | `None` | Maximum output tokens |
| `system_messages` | `List[Dict]` | No | `None` | System messages |
| `greeting_message` | `str` | No | `None` | Greeting message |
| `failure_message` | `str` | No | `None` | Failure message |
| `input_modalities` | `List[str]` | No | `None` | Input modalities |
| `output_modalities` | `List[str]` | No | `None` | Output modalities |
| `params` | `Dict[str, Any]` | No | `None` | Additional model parameters |
| `headers` | `Dict[str, str]` | No | `None` | Custom HTTP headers forwarded to the LLM provider |
| `greeting_configs` | `Dict[str, Any]` | No | `None` | Greeting playback configuration |
| `template_variables` | `Dict[str, str]` | No | `None` | Template variables for messages |

<!-- snippet: fragment -->
```python
from agora_agent.agentkit.vendors import Gemini

llm = Gemini(api_key='your-google-key', model='gemini-2.0-flash-exp')
```

---

## TTS Vendors

### `ElevenLabsTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `key` | `str` | Yes | — | ElevenLabs API key |
| `model_id` | `str` | Yes | — | Model ID (e.g., `eleven_flash_v2_5`) |
| `voice_id` | `str` | Yes | — | Voice ID |
| `base_url` | `str` | No | `None` | Custom WebSocket base URL |
| `sample_rate` | `int` | No | `None` | Sample rate: 16000, 22050, 24000, or 44100 Hz |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |
| `optimize_streaming_latency` | `int` | No | `None` | Latency optimization level (0–4) |
| `stability` | `float` | No | `None` | Voice stability (0.0–1.0) |
| `similarity_boost` | `float` | No | `None` | Similarity boost (0.0–1.0) |
| `style` | `float` | No | `None` | Style exaggeration (0.0–1.0) |
| `use_speaker_boost` | `bool` | No | `None` | Enable speaker boost |

### `MicrosoftTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `key` | `str` | Yes | — | Azure subscription key |
| `region` | `str` | Yes | — | Azure region (e.g., `eastus`) |
| `voice_name` | `str` | Yes | — | Voice name (e.g., `en-US-JennyNeural`) |
| `sample_rate` | `int` | No | `None` | Sample rate: 8000, 16000, 24000, or 48000 Hz |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

### `OpenAITTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | OpenAI API key |
| `voice` | `str` | Yes | — | Voice: `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer` |
| `model` | `str` | No | `None` | Model: `tts-1` or `tts-1-hd` |
| `response_format` | `str` | No | `None` | Audio format (e.g., `pcm`) |
| `speed` | `float` | No | `None` | Speech speed multiplier |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

Fixed sample rate: 24000 Hz.

### `CartesiaTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | Cartesia API key |
| `voice_id` | `str` | Yes | — | Voice ID (serialized as `{"mode": "id", "id": "..."}`) |
| `model_id` | `str` | No | `None` | Model ID |
| `sample_rate` | `int` | No | `None` | Sample rate: 8000–48000 Hz |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

### `GoogleTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `key` | `str` | Yes | — | Google Cloud API key |
| `voice_name` | `str` | Yes | — | Voice name |
| `language_code` | `str` | No | `None` | Language code (e.g., `en-US`) |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

### `AmazonTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `access_key` | `str` | Yes | — | AWS access key |
| `secret_key` | `str` | Yes | — | AWS secret key |
| `region` | `str` | Yes | — | AWS region (e.g., `us-east-1`) |
| `voice_id` | `str` | Yes | — | Amazon Polly voice ID |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

### `DeepgramTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | Deepgram API key |
| `model` | `str` | Yes | — | Deepgram TTS model (e.g., `aura-2-thalia-en`) |
| `base_url` | `str` | No | `None` | WebSocket endpoint; defaults server-side to `wss://api.deepgram.com/v1/speak` |
| `sample_rate` | `int` | No | `None` | Sample rate in Hz (for example, `24000`) |
| `params` | `Dict[str, Any]` | No | `None` | Additional Deepgram TTS parameters |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

### `HumeAITTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `key` | `str` | Yes | — | Hume AI API key |
| `config_id` | `str` | No | `None` | Configuration ID |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

### `RimeTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `key` | `str` | Yes | — | Rime API key |
| `speaker` | `str` | Yes | — | Speaker ID |
| `model_id` | `str` | No | `None` | Model ID |
| `lang` | `str` | No | `None` | Language code |
| `sampling_rate` | `int` | No | `None` | Sampling rate in Hz (serialized as `samplingRate`) |
| `speed_alpha` | `float` | No | `None` | Speed multiplier (serialized as `speedAlpha`) |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

### `FishAudioTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `key` | `str` | Yes | — | Fish Audio API key |
| `reference_id` | `str` | Yes | — | Reference ID |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

### `MiniMaxTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `key` | `str` | Yes | — | MiniMax API key |
| `group_id` | `str` | Yes | — | MiniMax group ID |
| `model` | `str` | Yes | — | Model name (e.g., `speech-02-turbo`) |
| `voice_id` | `str` | Yes | — | Voice style identifier |
| `url` | `str` | Yes | — | WebSocket endpoint |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

### `MurfTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `key` | `str` | Yes | — | Murf API key |
| `voice_id` | `str` | Yes | — | Voice ID (e.g., `Ariana`, `Natalie`) |
| `style` | `str` | No | `None` | Voice style (e.g., `Conversational`) |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

### `SarvamTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `key` | `str` | Yes | — | Sarvam API key |
| `speaker` | `str` | Yes | — | Speaker name |
| `target_language_code` | `str` | Yes | — | Target language code |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

---

## STT Vendors

### `SpeechmaticsSTT`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | Speechmatics API key |
| `language` | `str` | Yes | — | Language code (e.g., `en`) |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional parameters |

### `DeepgramSTT`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | No | `None` | Deepgram API key |
| `model` | `str` | No | `None` | Model (e.g., `nova-2`) |
| `language` | `str` | No | `None` | Language code (e.g., `en-US`) |
| `smart_format` | `bool` | No | `None` | Enable smart formatting |
| `punctuation` | `bool` | No | `None` | Enable punctuation |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional parameters |

### `MicrosoftSTT`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `key` | `str` | Yes | — | Azure subscription key |
| `region` | `str` | Yes | — | Azure region (e.g., `eastus`) |
| `language` | `str` | No | `None` | Language code (e.g., `en-US`) |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional parameters |

### `OpenAISTT`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | OpenAI API key |
| `model` | `str` | No | `None` | Model (default: `whisper-1`) |
| `language` | `str` | No | `None` | Language code |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional parameters |

### `GoogleSTT`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | Google Cloud API key |
| `language` | `str` | No | `None` | Language code (e.g., `en-US`) |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional parameters |

### `AmazonSTT`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `access_key` | `str` | Yes | — | AWS Access Key ID |
| `secret_key` | `str` | Yes | — | AWS Secret Access Key |
| `region` | `str` | Yes | — | AWS region (e.g., `us-east-1`) |
| `language` | `str` | No | `None` | Language code |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional parameters |

### `AssemblyAISTT`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | AssemblyAI API key |
| `language` | `str` | No | `None` | Language code |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional parameters |

### `AresSTT`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `language` | `str` | No | `None` | Language code |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional parameters |

### `SarvamSTT`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | Sarvam API key |
| `language` | `str` | Yes | — | Language code (e.g., `en`, `hi`) |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional parameters |

---

## MLLM Vendors

### `OpenAIRealtime`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | OpenAI API key |
| `model` | `str` | No | `None` | Model (e.g., `gpt-4o-realtime-preview`) |
| `url` | `str` | No | `None` | Custom WebSocket URL |
| `greeting_message` | `str` | No | `None` | Greeting message |
| `failure_message` | `str` | No | `None` | Message played when the model call fails |
| `max_history` | `int` | No | `None` | Maximum conversation history length |
| `predefined_tools` | `List[str]` | No | `None` | Predefined tools (e.g., `["_publish_message"]`) |
| `input_modalities` | `List[str]` | No | `None` | Input modalities |
| `output_modalities` | `List[str]` | No | `None` | Output modalities |
| `messages` | `List[Dict]` | No | `None` | Conversation messages |
| `params` | `Dict[str, Any]` | No | `None` | Additional parameters |
| `turn_detection` | `MllmTurnDetectionConfig` | No | `None` | MLLM turn detection configuration; overrides top-level `turn_detection` |

### `GeminiLive`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | Google Gemini API key |
| `model` | `str` | Yes | — | Gemini Live model name |
| `url` | `str` | No | `None` | Custom WebSocket URL |
| `instructions` | `str` | No | `None` | System instructions |
| `voice` | `str` | No | `None` | Voice name |
| `greeting_message` | `str` | No | `None` | Greeting message |
| `failure_message` | `str` | No | `None` | Message played when the model call fails |
| `max_history` | `int` | No | `None` | Maximum conversation history length |
| `predefined_tools` | `List[str]` | No | `None` | Predefined tools (e.g., `["_publish_message"]`) |
| `input_modalities` | `List[str]` | No | `None` | Input modalities |
| `output_modalities` | `List[str]` | No | `None` | Output modalities |
| `messages` | `List[Dict]` | No | `None` | Conversation messages |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional parameters |
| `turn_detection` | `MllmTurnDetectionConfig` | No | `None` | MLLM turn detection configuration; overrides top-level `turn_detection` |

### `VertexAI`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `model` | `str` | Yes | — | Model name (e.g., `gemini-2.0-flash-exp`) |
| `project_id` | `str` | Yes | — | Google Cloud project ID |
| `location` | `str` | Yes | — | Google Cloud location (e.g., `us-central1`) |
| `adc_credentials_string` | `str` | Yes | — | Application Default Credentials JSON string |
| `instructions` | `str` | No | `None` | System instructions |
| `voice` | `str` | No | `None` | Voice name (e.g., `Aoede`, `Charon`) |
| `greeting_message` | `str` | No | `None` | Greeting message |
| `failure_message` | `str` | No | `None` | Message played when the model call fails |
| `max_history` | `int` | No | `None` | Maximum conversation history length |
| `predefined_tools` | `List[str]` | No | `None` | Predefined tools (e.g., `["_publish_message"]`) |
| `input_modalities` | `List[str]` | No | `None` | Input modalities |
| `output_modalities` | `List[str]` | No | `None` | Output modalities |
| `messages` | `List[Dict]` | No | `None` | Conversation messages |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional parameters |
| `turn_detection` | `MllmTurnDetectionConfig` | No | `None` | MLLM turn detection configuration; overrides top-level `turn_detection` |

---

## Avatar Vendors

### `HeyGenAvatar`

Required TTS sample rate: **24000 Hz**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | HeyGen API key |
| `quality` | `str` | Yes | — | Avatar quality: `low`, `medium`, or `high` |
| `agora_uid` | `str` | Yes | — | Agora UID for avatar video stream |
| `agora_token` | `str` | No | `None` | RTC token for avatar authentication |
| `avatar_id` | `str` | No | `None` | HeyGen avatar ID |
| `enable` | `bool` | No | `True` | Enable or disable the avatar |
| `disable_idle_timeout` | `bool` | No | `None` | Disable the idle timeout |
| `activity_idle_timeout` | `int` | No | `None` | Idle timeout in seconds (default: 120) |

### `AkoolAvatar`

Required TTS sample rate: **16000 Hz**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | Akool API key |
| `agora_uid` | `str` | Yes | — | Agora UID for avatar video stream |
| `avatar_id` | `str` | No | `None` | Avatar ID |
