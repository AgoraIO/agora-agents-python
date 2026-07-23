---
sidebar_position: 4
title: Vendor Reference
description: Constructor options for all LLM, TTS, STT, MLLM, and Avatar vendor classes.
---

# Vendor Reference

All vendor classes are available from `agora_agent`:

<!-- snippet: fragment -->
```python
from agora_agent import OpenAI, ElevenLabsTTS, DeepgramTTS, DeepgramSTT, OpenAIRealtime, XaiGrok, GenericAvatar
```

## Recommended vendors by area

Construct vendors directly from `agora_agent`, then bind a client with `Agent(client=client, ...)`. The bound client selects `CNAgent` or `GlobalAgent` for IDE hints based on `area`, but does not restrict which vendor classes you can configure.

| Area | STT classes | LLM classes | TTS classes | Avatar classes |
|---|---|---|---|---|
| `Area.US`, `Area.EU`, `Area.AP` | `DeepgramSTT`, `SpeechmaticsSTT`, `MicrosoftSTT`, `OpenAISTT`, `GoogleSTT`, `AmazonSTT`, `AssemblyAISTT`, `AresSTT`, `SarvamSTT`, `XaiSTT` | `OpenAI`, `AzureOpenAI`, `Anthropic`, `Gemini`, `Groq`, `VertexAILLM`, `AmazonBedrock`, `Dify`, `CustomLLM` | `ElevenLabsTTS`, `MicrosoftTTS`, `OpenAITTS`, `CartesiaTTS`, `GoogleTTS`, `AmazonTTS`, `DeepgramTTS`, `GradiumTTS`, `MistralTTS`, `HumeAITTS`, `RimeTTS`, `FishAudioTTS`, `MiniMaxTTS`, `MurfTTS`, `SarvamTTS`, `GenericTTS`, `XaiTTS` | `LiveAvatarAvatar`, `HeyGenAvatar`, `AkoolAvatar`, `AnamAvatar`, `GenericAvatar` |
| `Area.CN` | `FengmingSTT`, `TencentSTT`, `MicrosoftCNSTT`, `XfyunSTT`, `XfyunBigModelSTT`, `XfyunDialectSTT` | `AliyunLLM`, `BytedanceLLM`, `DeepSeekLLM`, `TencentLLM` | `MiniMaxCNTTS`, `TencentTTS`, `BytedanceTTS`, `MicrosoftCNTTS`, `CosyVoiceTTS`, `BytedanceDuplexTTS`, `StepFunTTS`, `GenericTTS` | `SenseTimeAvatar`, `SpatiusAvatar` |

Global example:

```python
from agora_agent import Agora, Area, DeepgramSTT, MiniMaxTTS, OpenAI

client = Agora(
    area=Area.US,
    app_id="your-app-id",
    app_certificate="your-app-certificate",
)

stt = DeepgramSTT(model="nova-3", language="en-US")
llm = OpenAI(model="gpt-4o-mini")
tts = MiniMaxTTS(
    model="speech_2_6_turbo",
    voice_id="English_captivating_female1",
)
```

CN example:

```python
import os

from agora_agent import Agora, Area, AliyunLLM, FengmingSTT, MiniMaxCNTTS

client = Agora(
    area=Area.CN,
    app_id="your-app-id",
    app_certificate="your-app-certificate",
)

stt = FengmingSTT()
llm = AliyunLLM(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
    model="qwen-plus",
    api_key=os.environ["ALIYUN_API_KEY"],
)
tts = MiniMaxCNTTS(
    key=os.environ["MINIMAX_API_KEY"],
    model="speech-01-turbo",
    voice_id="female-shaonv",
)
```

---

## LLM Vendors

`greeting_configs` accepts either a dict or `LlmGreetingConfigs`. In v2.7, `greeting_configs.interruptable=False` makes the greeting uninterruptible; `True` follows the global `interruption` settings.

### `OpenAI`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | BYOK only | `None` | OpenAI API key. Optional for supported Agora-managed OpenAI models. |
| `model` | `str` | Yes | — | Model name |
| `base_url` | `str` | BYOK only | `None` | OpenAI Chat Completions endpoint URL. Required when `api_key` is set. |
| `temperature` | `float` | No | `None` | Sampling temperature (0.0–2.0) |
| `top_p` | `float` | No | `None` | Nucleus sampling (0.0–1.0) |
| `max_tokens` | `int` | No | `None` | Maximum tokens to generate |
| `system_messages` | `List[Dict]` | No | `None` | System messages |
| `greeting_message` | `str` | No | `None` | Greeting message |
| `greeting_audio_url` | `str` | No | `None` | Publicly accessible greeting audio URL |
| `failure_message` | `str` | No | `None` | Failure message |
| `input_modalities` | `List[str]` | No | `None` | Input modalities |
| `output_modalities` | `List[str]` | No | `None` | Output modalities |
| `params` | `Dict[str, Any]` | No | `None` | Additional model parameters |
| `headers` | `Dict[str, str]` | No | `None` | Custom HTTP headers forwarded to the LLM provider |
| `greeting_configs` | `Dict[str, Any]` | No | `None` | Greeting playback configuration |
| `template_variables` | `Dict[str, str]` | No | `None` | Template variables for messages |

`greeting_configs` may also include `audio_download_timeout_ms`, `audio_pcm_sample_rate`, and `uninterruptible_asr_policy`.

<!-- snippet: fragment -->
```python
from agora_agent import OpenAI

llm = OpenAI(api_key='your-key', base_url='https://api.openai.com/v1/chat/completions', model='gpt-4o-mini', temperature=0.7)
```

### `AzureOpenAI`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | Azure OpenAI API key |
| `model` | `str` | Yes | — | Deployment's base model name. Emitted as `params.model`. |
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
from agora_agent import AzureOpenAI

llm = AzureOpenAI(
    api_key='your-azure-key',
    model='gpt-4o-mini',
    endpoint='https://your-resource.openai.azure.com',
    deployment_name='gpt-4o-mini',
)
```

### `Anthropic`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | Anthropic API key |
| `model` | `str` | Yes | — | Model name |
| `url` | `str` | Yes | — | Anthropic messages endpoint URL |
| `headers` | `Dict[str, str]` | Yes | — | Request headers, including Anthropic API version |
| `max_tokens` | `int` | Yes | — | Maximum tokens |
| `temperature` | `float` | No | `None` | Sampling temperature (0.0–1.0) |
| `top_p` | `float` | No | `None` | Nucleus sampling (0.0–1.0) |
| `system_messages` | `List[Dict]` | No | `None` | System messages |
| `greeting_message` | `str` | No | `None` | Greeting message |
| `failure_message` | `str` | No | `None` | Failure message |
| `input_modalities` | `List[str]` | No | `None` | Input modalities |
| `output_modalities` | `List[str]` | No | `None` | Output modalities |
| `params` | `Dict[str, Any]` | No | `None` | Additional model parameters |
| `greeting_configs` | `Dict[str, Any]` | No | `None` | Greeting playback configuration |
| `template_variables` | `Dict[str, str]` | No | `None` | Template variables for messages |

<!-- snippet: fragment -->
```python
from agora_agent import Anthropic

llm = Anthropic(
    api_key='your-anthropic-key',
    url='https://api.anthropic.com/v1/messages',
    headers={'anthropic-version': '2023-06-01'},
    model='claude-3-5-sonnet-20241022',
    max_tokens=1024,
)
```

### `Gemini`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | Google AI API key |
| `model` | `str` | Yes | — | Model name |
| `url` | `str` | No | `None` | Custom Gemini `streamGenerateContent` URL. When omitted, the SDK constructs one from `model` and `api_key`. |
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
from agora_agent import Gemini

llm = Gemini(
    api_key='your-google-key',
    model='gemini-2.0-flash-exp',
)
```

### Other LLM vendors

The SDK also includes named helpers for the remaining Agora-supported LLM providers. These helpers choose the correct request format internally.

| Class | Provider | Key parameters |
|---|---|---|
| `Groq` | Groq | `api_key`, `model`, `base_url` |
| `VertexAILLM` | Google Vertex AI | `api_key`, `model`, `project_id`, `location`, `url?` |
| `AmazonBedrock` | Amazon Bedrock | `access_key`, `secret_key`, `region`, `model` |
| `Dify` | Dify | `api_key`, `url`, `model`, `user?`, `conversation_id?` |
| `CustomLLM` | OpenAI-compatible LLM | `api_key`, `model`, `base_url` |

---

## TTS Vendors

### `ElevenLabsTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `key` | `str` | Yes | — | ElevenLabs API key |
| `model_id` | `str` | Yes | — | Model ID (e.g., `eleven_flash_v2_5`) |
| `voice_id` | `str` | Yes | — | Voice ID |
| `base_url` | `str` | Yes | — | WebSocket base URL |
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
| `speed` | `float` | No | `None` | Speaking rate multiplier |
| `volume` | `float` | No | `None` | Audio volume |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

### `OpenAITTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | BYOK only | `None` | OpenAI API key |
| `voice` | `str` | Yes | — | Voice: `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer` |
| `model` | `str` | BYOK only | `None` | Model: `tts-1` or `tts-1-hd` |
| `base_url` | `str` | BYOK only | `None` | OpenAI TTS endpoint URL |
| `instructions` | `str` | No | `None` | Custom instructions for voice style, accent, pace, and tone |
| `speed` | `float` | No | `None` | Speech speed multiplier |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

`api_key`, `model`, and `base_url` are required together for BYOK. Without `api_key`, `model` must be omitted or set to the Agora-managed `tts-1` path. Fixed sample rate: 24000 Hz.

### `CartesiaTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | Cartesia API key |
| `voice_id` | `str` | Yes | — | Voice ID (serialized as `{"mode": "id", "id": "..."}`) |
| `model_id` | `str` | Yes | — | Model ID |
| `base_url` | `str` | No | `None` | WebSocket URL |
| `language` | `str` | No | `None` | Target language |
| `sample_rate` | `int` | No | `None` | Sample rate: 8000–48000 Hz |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

### `GoogleTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `key` | `str` | Yes | — | Google Cloud API key |
| `voice_name` | `str` | Yes | — | Voice name |
| `language_code` | `str` | No | `None` | Language code (e.g., `en-US`) |
| `sample_rate_hertz` | `int` | No | `None` | Sample rate in Hz |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

### `AmazonTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `access_key` | `str` | Yes | — | AWS access key |
| `secret_key` | `str` | Yes | — | AWS secret key |
| `region` | `str` | Yes | — | AWS region (e.g., `us-east-1`) |
| `voice_id` | `str` | Yes | — | Amazon Polly voice ID |
| `engine` | `str` | Yes | — | Amazon Polly engine type |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

### `DeepgramTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | Deepgram API key |
| `model` | `str` | Yes | — | Deepgram TTS model (e.g., `aura-2-thalia-en`) |
| `base_url` | `str` | No | `None` | WebSocket endpoint; defaults server-side to `wss://api.deepgram.com/v1/speak` |
| `sample_rate` | `int` | No | `None` | Sample rate in Hz (for example, `24000`) |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional Deepgram TTS parameters, flattened into `params` |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

### `GradiumTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | Gradium API key |
| `url` | `str` | No | `None` | WebSocket endpoint for streaming TTS output |
| `model_name` | `str` | No | `None` | Gradium TTS model name (e.g., `default`) |
| `voice_id` | `str` | No | `None` | Gradium voice identifier |
| `sample_rate` | `int` | No | `None` | Audio sample rate in Hz |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional Gradium TTS parameters, flattened into `params` |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

### `HumeAITTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `key` | `str` | Yes | — | Hume AI API key |
| `voice_id` | `str` | Yes | — | Hume AI voice ID |
| `provider` | `str` | Yes | — | Voice provider type, such as `CUSTOM_VOICE` or `HUME_AI` |
| `config_id` | `str` | No | `None` | Configuration ID |
| `base_url` | `str` | No | `None` | Base URL |
| `speed` | `float` | No | `None` | Playback speed |
| `trailing_silence` | `float` | No | `None` | Trailing silence in seconds |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

### `RimeTTS`

`CredentialMode` is exported from `agora_agent` as the shared credential mode constants for provider integrations.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `key` | `str` | BYOK: Yes; Managed: No | `None` | Rime API key |
| `speaker` | `str` | BYOK: Yes; Managed: No | `None` | Speaker ID |
| `model_id` | `str` | Yes | — | Model ID |
| `base_url` | `str` | Managed: Yes; BYOK: No | `None` | WebSocket URL |
| `credential_mode` | `CredentialMode` | No | `None` | Shared credential mode (`"managed"` or `"byok"`); omission uses BYOK validation |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

When `credential_mode` is omitted or set to `"byok"`, provide `key`, `speaker`, and `model_id`:

```python
import os

from agora_agent import RimeTTS

tts = RimeTTS(
    key=os.environ["RIME_API_KEY"],
    speaker="your-speaker-id",
    model_id="mist",
)
```

For Agora-managed credentials, set `credential_mode=CredentialMode.MANAGED` and provide `base_url` and `model_id`:

```python
from agora_agent import CredentialMode, RimeTTS

tts = RimeTTS(
    credential_mode=CredentialMode.MANAGED,
    base_url="wss://your-rime-endpoint.example.com",
    model_id="mist",
)
```

AgentKit serializes `credential_mode` at the top level of the Rime TTS configuration, alongside `vendor` and `params`. It omits the field when the option is not provided, preserving the existing BYOK request shape.

### `FishAudioTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `key` | `str` | Yes | — | Fish Audio API key |
| `reference_id` | `str` | Yes | — | Reference ID |
| `backend` | `str` | Yes | — | Backend model version |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

### `MiniMaxTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `key` | `str` | BYOK only | `None` | MiniMax API key. Optional for supported Agora-managed MiniMax models |
| `group_id` | `str` | BYOK only | `None` | MiniMax group ID |
| `model` | `str` | Yes | — | Model name (e.g., `speech-02-turbo`) |
| `voice_id` | `str` | Conditional | `None` | Voice style identifier. Exactly one of `voice_id` or `timber_weights` is required. |
| `timber_weights` | `List[Dict[str, Any]]` | Conditional | `None` | Voice mixing configuration. Exactly one of `voice_id` or `timber_weights` is required. |
| `speed` | `float` | No | `None` | Speaking speed |
| `vol` | `float` | No | `None` | Volume gain |
| `pitch` | `float` | No | `None` | Pitch adjustment |
| `emotion` | `str` | No | `None` | Emotion style |
| `latex_read` | `bool` | No | `None` | Whether to read LaTeX expressions |
| `english_normalization` | `bool` | No | `None` | Whether to normalize English text |
| `sample_rate` | `int` | No | `None` | Output sample rate in Hz. Serialized as `params.audio_setting.sample_rate`. |
| `pronunciation_dict` | `Dict[str, Any]` | No | `None` | Pronunciation replacement dictionary |
| `language_boost` | `str` | No | `None` | Language boost strategy |
| `url` | `str` | No | `None` | Optional endpoint override |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

`key` and `group_id` are required together for BYOK. `url` is optional. In both BYOK and managed modes, exactly one of `voice_id` or `timber_weights` must be provided. Without `key`, `model` must be one of the supported Agora-managed MiniMax models.

### `MistralTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | Mistral API key |
| `model` | `str` | No | `None` | Mistral TTS model name (e.g., `voxtral-mini-tts-2603`) |
| `voice` | `str` | No | `None` | Mistral voice identifier |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional Mistral TTS parameters, flattened into `params` |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

### `MurfTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `key` | `str` | Yes | — | Murf API key |
| `voice_id` | `str` | No | `None` | Voice ID (e.g., `Ariana`, `Natalie`) |
| `base_url` | `str` | No | `None` | WebSocket endpoint |
| `locale` | `str` | No | `None` | Voice locale |
| `rate` | `float` | No | `None` | Speech rate |
| `pitch` | `float` | No | `None` | Pitch adjustment |
| `model` | `str` | No | `None` | TTS model |
| `sample_rate` | `int` | No | `None` | Audio sample rate |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

### `SarvamTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `key` | `str` | Yes | — | Sarvam API key |
| `speaker` | `str` | Yes | — | Speaker name |
| `target_language_code` | `str` | Yes | — | Target language code |
| `pitch` | `float` | No | `None` | Pitch adjustment |
| `pace` | `float` | No | `None` | Speed of speech |
| `loudness` | `float` | No | `None` | Volume level |
| `sample_rate` | `int` | No | `None` | Audio sample rate |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

### `GenericTTS`

`GenericTTS` currently supports HTTP and HTTPS endpoints. WebSocket endpoints are rejected until a WebSocket-backed generic TTS implementation is available. AgentKit serializes the current HTTP implementation with the internal vendor value `generic_http`.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `url` | `str` | Yes | — | HTTP(S) endpoint of the generic TTS service |
| `headers` | `Dict[str, str]` | No | `None` | Custom headers to include in requests to the generic TTS service |
| `model` | `str` | No | `None` | TTS model name |
| `voice` | `str` | No | `None` | Voice name |
| `api_key` | `str` | No | `None` | API key for the generic TTS service |
| `speed` | `float` | No | `None` | Speech rate |
| `sample_rate` | `int` | No | `None` | Output audio sample rate in Hz |
| `response_format` | `str` | No | `None` | Output audio format; use `pcm` |
| `instruction` | `str` | No | `None` | Additional voice style control instruction |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional generic TTS parameters |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

### `XaiTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | xAI API key |
| `language` | `str` | Yes | — | BCP-47 language code for speech synthesis |
| `voice_id` | `str` | No | `None` | xAI voice identifier |
| `sample_rate` | `int` | No | `None` | Audio sample rate in Hz |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional xAI TTS parameters |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

---

## STT Vendors

Use `turn_detection.language` for Agora interaction language; it defaults to `en-US`. Provider-specific language values remain under `asr.params` and may use a different format. If `with_stt()` is omitted, AgentKit defaults to `AresSTT` for global clients and `FengmingSTT` for `Area.CN` clients. AgentKit populates REST `asr.language` from `turn_detection.language`.

### `SpeechmaticsSTT`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | Speechmatics API key |
| `language` | `str` | Yes | — | Language code (e.g., `en`) |
| `uri` | `str` | No | `None` | Speechmatics streaming WebSocket URL |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional parameters |

### `DeepgramSTT`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | BYOK only | `None` | Deepgram API key. Optional only for Agora-managed `nova-2` and `nova-3`. |
| `model` | `str` | No | `None` | Model (e.g., `nova-2`) |
| `language` | `str` | No | `None` | Language code (e.g., `en-US`) |
| `keyterm` | `str` | No | `None` | Boost specialized terms and brands; serialized as `asr.params.keyterm` |
| `smart_format` | `bool` | No | `None` | Enable smart formatting |
| `punctuation` | `bool` | No | `None` | Enable punctuation |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional parameters |

For `nova-2` and `nova-3`, omit `api_key` to use Agora-managed credentials. For all other Deepgram models, AgentKit requires `api_key`.

### `MicrosoftSTT`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `key` | `str` | Yes | — | Azure subscription key |
| `region` | `str` | Yes | — | Azure region (e.g., `eastus`) |
| `language` | `str` | Yes | — | Language code (e.g., `en-US`) |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional parameters |

### `OpenAISTT`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | OpenAI API key |
| `model` | `str` | No | `None` | Model (default: `whisper-1`) |
| `language` | `str` | No | `None` | Language code |
| `prompt` | `str` | No | `None` | Prompt for OpenAI transcription |
| `input_audio_transcription` | `Dict[str, Any]` | No | `None` | OpenAI transcription settings |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional parameters |

### `GoogleSTT`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `project_id` | `str` | Yes | — | Google Cloud project ID |
| `location` | `str` | Yes | — | Google Cloud region |
| `adc_credentials_string` | `str` | Yes | — | Google service account credentials JSON string |
| `language` | `str` | Yes | — | Language code (e.g., `en-US`) |
| `model` | `str` | No | `None` | Recognition model |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional parameters |

### `AmazonSTT`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `access_key` | `str` | Yes | — | AWS Access Key ID |
| `secret_key` | `str` | Yes | — | AWS Secret Access Key |
| `region` | `str` | Yes | — | AWS region (e.g., `us-east-1`) |
| `language` | `str` | Yes | — | Amazon `language_code` |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional parameters |

### `AssemblyAISTT`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | AssemblyAI API key |
| `language` | `str` | Yes | — | Language code |
| `uri` | `str` | No | `None` | AssemblyAI streaming WebSocket URL |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional parameters |

### `AresSTT`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional parameters |

### `SarvamSTT`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | Sarvam API key |
| `language` | `str` | Yes | — | Language code (e.g., `en`, `hi`) |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional parameters |

### `XaiSTT`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | xAI API key |
| `base_url` | `str` | No | `None` | WebSocket endpoint URL for the xAI streaming STT API |
| `sample_rate` | `int` | No | `None` | Audio sample rate in Hz |
| `language` | `str` | No | `None` | Language code for speech recognition |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional xAI STT parameters |

---

## CN Vendors

### CN LLM Vendors

All CN LLM helpers reuse the `OpenAI`-compatible shape and set a different vendor internally.

| Class | Key parameters |
|---|---|
| `AliyunLLM` | `base_url`, `model`, `api_key?`, `system_messages?`, `greeting_message?`, `failure_message?`, `max_history?`, `params?`, `headers?` |
| `BytedanceLLM` | `base_url`, `model`, `api_key?`, `system_messages?`, `greeting_message?`, `failure_message?`, `max_history?`, `params?`, `headers?` |
| `DeepSeekLLM` | `base_url`, `model`, `api_key?`, `system_messages?`, `greeting_message?`, `failure_message?`, `max_history?`, `params?`, `headers?` |
| `TencentLLM` | `base_url`, `model`, `api_key?`, `system_messages?`, `greeting_message?`, `failure_message?`, `max_history?`, `params?`, `headers?` |

### CN TTS Vendors

CN TTS classes use explicit names when they differ from the global implementations. Use `MiniMaxCNTTS` and `MicrosoftCNTTS` for the CN-specific variants.

All CN TTS vendor classes support `skip_patterns` and `additional_params`.

#### `MiniMaxCNTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `key` | `str` | No | `None` | MiniMax API key |
| `model` | `str` | Yes | — | MiniMax TTS model |
| `voice_id` | `str` | Conditional | `None` | Voice style identifier. Exactly one of `voice_id` or `timber_weights` is required. |
| `timber_weights` | `List[Dict[str, Any]]` | Conditional | `None` | Timbre mix configuration. Exactly one of `voice_id` or `timber_weights` is required. |
| `speed` | `float` | No | `None` | Speaking speed |
| `vol` | `float` | No | `None` | Volume gain |
| `pitch` | `float` | No | `None` | Pitch adjustment |
| `emotion` | `str` | No | `None` | Emotion style |
| `latex_read` | `bool` | No | `None` | Whether to read LaTeX expressions |
| `english_normalization` | `bool` | No | `None` | Whether to normalize English text |
| `sample_rate` | `int` | No | `None` | Output sample rate in Hz |
| `pronunciation_dict` | `Dict[str, Any]` | No | `None` | Pronunciation replacement dictionary |
| `language_boost` | `str` | No | `None` | Language boost strategy |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional MiniMax TTS parameters |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

#### `TencentTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `app_id` | `str` | Yes | — | Tencent TTS app id |
| `secret_id` | `str` | Yes | — | Tencent TTS secret id |
| `secret_key` | `str` | Yes | — | Tencent TTS secret key |
| `voice_type` | `int` | Yes | — | Tencent TTS voice type |
| `volume` | `int` | No | `None` | Tencent TTS volume |
| `speed` | `int` | No | `None` | Tencent TTS speed |
| `emotion_category` | `str` | No | `None` | Tencent TTS emotion category |
| `emotion_intensity` | `int` | No | `None` | Tencent TTS emotion intensity |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional Tencent TTS parameters |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

#### `BytedanceTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `token` | `str` | Yes | — | Bytedance TTS token |
| `app_id` | `str` | Yes | — | Bytedance TTS app id |
| `cluster` | `str` | Yes | — | Bytedance TTS cluster |
| `voice_type` | `str` | Yes | — | Bytedance TTS voice type |
| `speed_ratio` | `float` | No | `None` | Speed ratio |
| `volume_ratio` | `float` | No | `None` | Volume ratio |
| `pitch_ratio` | `float` | No | `None` | Pitch ratio |
| `emotion` | `str` | No | `None` | Emotion |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional Bytedance TTS parameters |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

#### `MicrosoftCNTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `key` | `str` | Yes | — | Microsoft Azure subscription key |
| `region` | `str` | Yes | — | Azure region |
| `voice_name` | `str` | Yes | — | Voice name |
| `sample_rate` | `int` | No | `None` | Sample rate in Hz |
| `speed` | `float` | No | `None` | Speaking rate multiplier |
| `volume` | `float` | No | `None` | Volume |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional Microsoft TTS parameters |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

#### `CosyVoiceTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | No | `None` | CosyVoice API key |
| `model` | `str` | No | `None` | CosyVoice model |
| `sample_rate` | `int` | No | `None` | Sample rate in Hz |
| `voice` | `str` | No | `None` | CosyVoice voice |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional CosyVoice TTS parameters |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

#### `BytedanceDuplexTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `app_id` | `str` | Yes | — | Bytedance Duplex TTS app id |
| `token` | `str` | Yes | — | Bytedance Duplex TTS token |
| `speaker` | `str` | Yes | — | Bytedance Duplex TTS speaker |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional Bytedance Duplex TTS parameters |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

#### `StepFunTTS`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | No | `None` | StepFun TTS API key |
| `model` | `str` | No | `None` | StepFun TTS model |
| `voice_id` | `str` | No | `None` | StepFun TTS voice id |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional StepFun TTS parameters |
| `skip_patterns` | `List[int]` | No | `None` | Skip patterns |

### CN STT Vendors

#### `TencentSTT`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `key` | `str` | Yes | — | Tencent ASR secret key |
| `app_id` | `str` | Yes | — | Tencent ASR app id |
| `secret` | `str` | Yes | — | Tencent ASR secret |
| `engine_model_type` | `str` | Yes | — | Tencent ASR engine model type |
| `voice_id` | `str` | Yes | — | Tencent ASR voice id |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional Tencent ASR parameters |

#### `FengmingSTT`

No constructor parameters. Use `FengmingSTT()`.

#### `XfyunSTT`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | No | `None` | Xfyun ASR API key |
| `app_id` | `str` | No | `None` | Xfyun ASR app id |
| `api_secret` | `str` | No | `None` | Xfyun ASR API secret |
| `language` | `str` | No | `None` | Xfyun ASR language |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional Xfyun ASR parameters |

#### `XfyunBigModelSTT`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | No | `None` | Xfyun BigModel ASR API key |
| `app_id` | `str` | No | `None` | Xfyun BigModel ASR app id |
| `api_secret` | `str` | No | `None` | Xfyun BigModel ASR API secret |
| `language_name` | `str` | No | `None` | Xfyun BigModel ASR language name |
| `language` | `str` | No | `None` | Xfyun BigModel ASR language |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional Xfyun BigModel ASR parameters |

#### `XfyunDialectSTT`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `app_id` | `str` | No | `None` | Xfyun Dialect ASR app id |
| `access_key_id` | `str` | No | `None` | Xfyun Dialect ASR access key id |
| `access_key_secret` | `str` | No | `None` | Xfyun Dialect ASR access key secret |
| `language` | `str` | No | `None` | Xfyun Dialect ASR language |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional Xfyun Dialect ASR parameters |

#### `MicrosoftCNSTT`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `key` | `str` | Yes | — | Microsoft Azure subscription key |
| `region` | `str` | Yes | — | Azure region (for example, `chinaeast2`) |
| `language` | `str` | Yes | — | Language code (for example, `zh-CN`) |
| `phrase_list` | `List[str]` | No | `None` | Phrase hints |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional Microsoft ASR parameters |

### CN Avatar Vendors

#### `SenseTimeAvatar`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `agora_token` | `str` | No | `None` | RTC token for avatar publisher; generated by AgentSession when omitted |
| `agora_uid` | `str` | Yes | — | Avatar RTC publisher uid |
| `appId` | `str` | No | `None` | SenseTime app id |
| `app_key` | `str` | Yes | — | SenseTime app key |
| `sceneList` | `List[Dict[str, Any]]` | No | `None` | SenseTime scene list |
| `enable` | `bool` | No | `None` | Whether to enable the avatar |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional SenseTime avatar parameters |

#### `SpatiusAvatar`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `spatius_api_key` | `str` | Yes | — | Spatius API key |
| `spatius_app_id` | `str` | Yes | — | Spatius application ID |
| `spatius_avatar_id` | `str` | Yes | — | Spatius avatar ID |
| `agora_uid` | `str` | Yes | — | Agora UID used by the avatar service |
| `agora_token` | `str` | No | `None` | RTC token for avatar publisher; generated by AgentSession when omitted |
| `region` | `str` | No | `None` | Spatius service region, for example `cn-beijing` |
| `sample_rate` | `int` | No | `None` | Optional avatar-declared sample rate; TTS sample rate should match when set |
| `session_expire_minutes` | `int` | No | `None` | Spatius session validity duration in minutes |
| `enable` | `bool` | No | `None` | Whether to enable the avatar |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional Spatius avatar parameters |

## MLLM Vendors

### `OpenAIRealtime`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | OpenAI API key |
| `model` | `str` | No | `None` | Model (e.g., `gpt-4o-realtime-preview`) |
| `url` | `str` | No | `wss://api.openai.com/v1/realtime` | OpenAI Realtime WebSocket URL |
| `greeting_message` | `str` | No | `None` | Greeting message |
| `failure_message` | `str` | No | `None` | Message played when the model call fails |
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
| `input_modalities` | `List[str]` | No | `None` | Input modalities |
| `output_modalities` | `List[str]` | No | `None` | Output modalities |
| `messages` | `List[Dict]` | No | `None` | Conversation messages |
| `additional_params` | `Dict[str, Any]` | No | `None` | Additional parameters |
| `turn_detection` | `MllmTurnDetectionConfig` | No | `None` | MLLM turn detection configuration; overrides top-level `turn_detection` |

### `XaiGrok`

xAI Grok MLLM vendor (`mllm.vendor`: `"xai"`). Matches the [xAI Grok](https://docs.agora.io/en/conversational-ai/models/mllm/xai) product docs.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | xAI API key |
| `url` | `str` | No | `wss://api.x.ai/v1/realtime` | xAI realtime WebSocket URL |
| `voice` | `str` | No | `None` | Voice identifier, for example `eve` or `rex` |
| `language` | `str` | No | `None` | Language code, for example `en` |
| `sample_rate` | `int` | No | `None` | Audio sample rate in Hz |
| `greeting_message` | `str` | No | `None` | Greeting message |
| `failure_message` | `str` | No | `None` | Message played when the model call fails |
| `input_modalities` | `List[str]` | No | `None` | Input modalities |
| `output_modalities` | `List[str]` | No | `None` | Output modalities |
| `messages` | `List[Dict]` | No | `None` | Conversation messages |
| `params` | `Dict[str, Any]` | No | `None` | Additional xAI parameters |
| `turn_detection` | `MllmTurnDetectionConfig` | No | `None` | Supports `agora_vad` and `server_vad` for xAI |

---

## Avatar Vendors

Avatar vendors are currently supported only with the cascading ASR + LLM + TTS pipeline.

### `HeyGenAvatar`

Required TTS sample rate: **24000 Hz**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | HeyGen API key |
| `quality` | `str` | Yes | — | Avatar quality: `low`, `medium`, or `high` |
| `agora_uid` | `str` | Yes | — | Agora UID for avatar video stream |
| `agora_token` | `str` | No | `None` | Avatar token. When omitted, `AgentSession.start()` generates one for `agora_uid` using the same token path as the agent. |
| `avatar_id` | `str` | No | `None` | HeyGen avatar ID |
| `enable` | `bool` | No | `True` | Enable or disable the avatar |
| `disable_idle_timeout` | `bool` | No | `None` | Disable the idle timeout |
| `activity_idle_timeout` | `int` | No | `None` | Idle timeout in seconds (default: 120) |

### `AkoolAvatar`

Required TTS sample rate: **16000 Hz**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | Akool API key |
| `avatar_id` | `str` | No | `None` | Avatar ID |

### `LiveAvatarAvatar`

Required TTS sample rate: **24000 Hz**

Same options as `HeyGenAvatar`, but serializes `vendor: "liveavatar"`. `agora_token` is optional and generated by `AgentSession.start()` when omitted.

### `AnamAvatar`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | Anam API key |
| `avatar_id` | `str` | Yes | — | Anam avatar ID |
| `enable` | `bool` | No | `True` | Enable or disable the avatar |

### `GenericAvatar`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `api_key` | `str` | Yes | — | Generic avatar provider API key |
| `agora_uid` | `str` | Yes | — | Avatar RTC UID. Must differ from the agent UID. |
| `api_base_url` | `str` | Yes | — | Avatar provider API base URL |
| `avatar_id` | `str` | Yes | — | Avatar ID |
| `agora_token` | `str` | No | `None` | Optional avatar token. Generated by `AgentSession.start()` when omitted. |
| `agora_appid` | `str` | No | `None` | Optional; filled from the session App ID when omitted. |
| `agora_channel` | `str` | No | `None` | Optional; filled from the session channel when omitted. |
| `enable` | `bool` | No | `True` | Enable or disable the avatar |

Avatar tokens are separate from the agent join token but generated with the same `generate_convo_ai_token` path, using the avatar's `agora_uid` as `uid`.
