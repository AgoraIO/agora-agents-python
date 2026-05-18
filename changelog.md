# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [v1.4.1] — 2026-05-18

### Fixed

- **Release workflow** — Publish to PyPI with the `PYPI_API_TOKEN` secret.

## [v1.4.0] — 2026-05-13

### Added

- **`DeepgramTTS`** — New TTS vendor wrapper for Deepgram (Beta). Accepts `api_key`, `model`, `base_url`, `sample_rate`, `params`, and `skip_patterns`.
- **`Agent.with_tools(enabled=True)`** — Dedicated builder method to enable MCP tool invocation (`advanced_features.enable_tools`). Replaces the raw `with_advanced_features(AdvancedFeatures(enable_tools=True))` call.
- **LLM vendors: `headers` field** — All four LLM vendors (`OpenAI`, `AzureOpenAI`, `Anthropic`, `Gemini`) now accept an optional `headers: Dict[str, str]` parameter. Use this to pass custom HTTP headers to the LLM provider (e.g., tenant identifiers, routing headers).
- **`AgentSession.think()` / `AsyncAgentSession.think()`** — Send a custom instruction to a running agent through the `agent_management` API.
- **`Agent.with_interruption()`** — Configure the new top-level `interruption` object for unified interruption control.
- **MLLM turn detection** — `OpenAIRealtime`, `GeminiLive`, and `VertexAI` now accept `turn_detection`, which maps to `mllm.turn_detection` and overrides top-level turn detection for MLLM sessions.
- **`audio_scenario` AgentKit support** — `SessionParams` and AgentKit request construction now expose the top-level `parameters.audio_scenario` field.
- **MLLM vendor parity** — `GeminiLive` is documented and exposed as the direct Google Gemini Live API wrapper.

### Fixed

- **MiniMax TTS preset stripping** — When a MiniMax reseller preset is inferred (`minimax_speech_2_6_turbo` or `minimax_speech_2_8_turbo`), the `group_id` and `url` fields are now correctly stripped from `tts.params` alongside `key` and `model`. Previously they were forwarded to the API, causing request failures.
- **MLLM enable flag** — `Agent.with_mllm()` now sets `mllm.enable = True` and removes the deprecated `advanced_features.enable_mllm` flag from generated requests.
- **MLLM wrapper shape** — MLLM vendors no longer emit removed fields such as `style`; docs and tests now reflect the v2.6 MLLM contract.
- **Preset-backed OpenAI TTS** — `OpenAITTS` no longer requires `api_key` when a reseller preset supplies credentials server-side.
- **AgentKit parity coverage** — Added regression coverage for interruption, MLLM turn detection, Deepgram TTS, LLM headers, and deprecated MLLM flag cleanup.

## [v1.3.0] — 2026-04-02

### Added

- **`AgentSession`** — Added `get_turns()` for turn analytics in both sync and async sessions.
- **`Agent` / `AgentSession`** — Added session-level `preset` and `pipeline_id` support, including preset normalization and automatic inference for supported reseller-backed models.
- **`AgentKit`** — Added preset constants and helper utilities for discoverable preset usage.
- **`AgentKit`** — Added missing public vendor surface for `GeminiLive`, `LiveAvatarAvatar`, and `AnamAvatar`.
- **Tests** — Added AgentKit parity and vendor regression coverage for presets, session behavior, and wrapper mappings.

### Changed

- **`OpenAI` / `OpenAITTS` / `MiniMaxTTS`** — Relaxed no-key preset paths so reseller-backed usage can be expressed without forcing credential fields.
- **`GeminiLive`** — Aligned wrapper output with the Agora low-level MLLM contract and kept `messages` at the top level.
- **`Avatar` wrappers** — Updated avatar handling for `LiveAvatar` and `Anam`, including sample-rate validation behavior.

### Fixed

- **`AgentKit` MLLM** — Removed unsupported wrapper-only fields so the Python surface stays aligned with the generated Agora API contract.
- **`pydantic_utilities`** — Updated Pydantic compatibility handling for Python 3.14-safe operation.
- **Mypy/test packaging** — Added explicit test package markers to avoid duplicate module resolution during type checking.

## [v1.2.0] — 2026-03-27

### Fixed

- **`AresSTT`** — Removed redundant `language` key from the `params` dict. Language is now emitted only at the top level. `params` is only included when `additional_params` is provided.
- **`OpenAIRealtime` / `VertexAI` (MLLM)** — Agent-level `greeting`, `failure_message`, and `max_history` overrides are now correctly applied when the agent is in MLLM mode. Previously these values were silently dropped.
- **`VertexAI` (MLLM)** — `messages` is now correctly placed inside `params` (required by the Gemini Live API). Previously it was emitted at the top level and silently ignored.

### Changed

- **`OpenAITTS`** — Renamed constructor parameter `key` → `api_key` to match the Agora server API expectation. ⚠️ **Breaking change.**
- **`CartesiaTTS`** — Renamed constructor parameter `key` → `api_key`. Voice is now serialized as `{"mode": "id", "id": "<voice_id>"}` instead of a flat `voice_id` string. ⚠️ **Breaking change.**
- **`HeyGenAvatar`** — Removed legacy fields `avatar_name`, `voice_id`, `language`, `version`. Added `agora_token`, `avatar_id`, `enable`, `disable_idle_timeout`, `activity_idle_timeout`. The config now includes a top-level `enable` field (defaults `true`). ⚠️ **Breaking change.**

### Added

- **`OpenAITTS`** — New optional parameters: `response_format` (str, e.g. `"pcm"`) and `speed` (float).
- **`CartesiaTTS`** — `voice_id` user-facing field is preserved; voice is serialized to the required nested object format automatically.
- **`RimeTTS`** — New optional parameters: `lang` (str), `sampling_rate` (int, serialized as `samplingRate`), `speed_alpha` (float, serialized as `speedAlpha`).
- **`OpenAIRealtime`** — New optional parameters: `predefined_tools` (List[str]), `failure_message` (str), `max_history` (int).
- **`VertexAI` (MLLM)** — New optional parameters: `predefined_tools` (List[str]), `failure_message` (str), `max_history` (int).
- **`HeyGenAvatar`** — New fields: `agora_token` (str, optional), `avatar_id` (str, optional), `enable` (bool, optional, default `True`), `disable_idle_timeout` (bool, optional), `activity_idle_timeout` (int, optional).

## [v1.1.0] — 2026-03-17

### Added

- `MurfTTS` vendor


### Fixed

- `MiniMaxTTS`: added required `group_id`, `url`, and correctly nested `voice_setting.voice_id` — previously missing, requiring users to bypass the SDK entirely
- `SarvamTTS`: corrected schema to `key` + `speaker` + `target_language_code` (was incorrectly using `api_key`, `voice_id`, `model`)
- All LLM vendors: added `max_history` field for conversation history caching
- `AzureOpenAI` LLM: added `params` escape hatch for passing arbitrary API parameters
- `Anthropic` LLM: added `url` for custom endpoints and `params` escape hatch
- `Gemini` LLM: added `url` for custom endpoints and `params` escape hatch; named model params (`temperature`, `top_p`, `top_k`, `max_output_tokens`) now take precedence over `params` dict
- `SpeechmaticsSTT`, `SarvamSTT`: added optional `model` field

## [v1.0.0] — 2026-03-11

Initial stable release of the Agora Agent Server SDK for Python.

### Added

- `Agent` builder with fluent API (`.with_llm()`, `.with_tts()`, `.with_stt()`, `.with_mllm()`, `.with_avatar()`)
- `AgentSession` and `AsyncAgentSession` for synchronous and async session lifecycle management
- Automatic token generation — pass `app_id` + `app_certificate` and tokens are handled internally
- Token utilities: `generate_rtc_token`, `generate_convo_ai_token`, `expires_in_hours`, `expires_in_minutes`
- Turn detection configuration via `TurnDetectionConfig` with nested `StartOfSpeechConfig` and `EndOfSpeechConfig`
- SAL (Selective Attention Locking) via `SalConfig` with `SalMode`
- Filler words support: `FillerWordsConfig`, `FillerWordsTrigger`, `FillerWordsContent`
- Session parameters: `SessionParams`, `SilenceConfig`, `FarewellConfig`, `ParametersDataChannel`
- Geofencing via `GeofenceConfig`
- Advanced features (MLLM mode) via `AdvancedFeatures`
- Type-safe constants: `DataChannel`, `SilenceActionValues`, `SalModeValues`, `GeofenceArea`, `FillerWordsSelectionRule`, `TurnDetectionTypeValues`
- Vendor integrations:
  - **LLM**: `OpenAI`, `AzureOpenAI`, `Anthropic`, `Gemini`, `VertexAI`
  - **MLLM**: `OpenAIRealtime`
  - **TTS**: `ElevenLabsTTS`, `MicrosoftTTS`, `OpenAITTS`, `CartesiaTTS`, `GoogleTTS`, `AmazonTTS`, `HumeAITTS`, `RimeTTS`, `FishAudioTTS`, `MiniMaxTTS`, `SarvamTTS`
  - **STT**: `DeepgramSTT`, `MicrosoftSTT`, `OpenAISTT`, `GoogleSTT`, `AmazonSTT`, `AssemblyAISTT`, `AresSTT`, `SarvamSTT`, `SpeechmaticsSTT`
  - **Avatar**: `HeyGenAvatar`, `AkoolAvatar`
