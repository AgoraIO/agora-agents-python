# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [v2.7.0] — 2026-08-26

### Added

- **Preview endpoint support** — `Agora` and `AsyncAgora` detect preview features from each resolved session body, then pin that session's requests to the preview gateway and `agora-feature` header without mutating the production client.
- **Gemini preview ASR** — `GeminiSTT` (`gemini-3.5-transcribe-live`), under `agora_agent.agentkit.preview`, a cascading ASR stage served only by the preview gateway.
- **Gemini ASR language selection** — `language_codes` serializes to `params.language_codes`, replacing the singular `params.language` this vendor previously sent. Omitted from the request when unset, which is how the provider spells auto-detect. `GeminiSTT` has no `language` argument: the top-level `asr.language` comes from turn detection, as it does for every STT vendor.
- **Gemini ASR custom vocabulary** — `custom_vocabulary` biases recognition toward supplied words and phrases via `params.custom_vocabulary`. Omitted from the request when unset.
- **Session-scoped routing** — GA sessions remain on the production regional endpoint, while preview session lifecycle calls use the preview endpoint. Top-level `stop_agent()` remains production-only.
- **Debug redaction** — `redact_secrets` replaces vendor API keys, RTC tokens, and the App ID with `[REDACTED]`. Empty strings stay visible so an unset environment variable remains diagnosable.

### Fixed

- **Gemini ASR parameter compatibility** — `word_timestamp` is now omitted unless explicitly set. Enabling it together with `custom_vocabulary` fails locally instead of sending a combination Gemini does not support.
- **Debug logging leaked credentials** — the httpx debug hook logged raw request bodies, so vendor API keys and RTC tokens reached the log unredacted. Bodies are now JSON-decoded and redacted; a non-JSON body is described by size rather than echoed.
- **Malformed credentials are rejected before signing** — the Python signing path HMACs whatever it is given, so an `app_id` or `app_certificate` with a trailing newline or a truncated paste produced a well-formed token that the gateway rejected with an error naming neither field. `generate_rtc_token` and `generate_convo_ai_token` now raise `ValueError` and say which field is the wrong length. Credential values are never included in the message.
- **Preview vendors reject an empty API key** — `GeminiSTT(api_key="")` previously accepted the empty string and sent it as a blank credential. It now fails at construction, matching the TypeScript and Go vendors.

### Changed

- **Preview configs bypass request validation** — the generated request models mirror what production serves, so `asr.vendor = "gemini"` fails validation. Configs that `required_preview_features()` recognises are now passed through unvalidated, with `None` entries stripped so the bypass puts the same bytes on the wire as the typed path. Production configs are unaffected.

### Documentation

- Added [Preview Endpoint](docs/guides/preview-endpoint.md), covering the gate header, intake-node failure signatures, the validation bypass, and how to add a future preview family.
- Documented every field `Agent.to_properties` injects into a vendor config, and why a preview provider must be verified against the resolved request body rather than the vendor class output — a value written under a spelling the route ignores fails silently.

## [v2.4.0] — 2026-06-30

### Added

- **Area-aware default ASR vendor selection** — The default ASR vendor is now chosen based on the client area, with updated documentation and tests.
- **New engine API vendors** — Adapted agentkit to the new engine API vendors, with refreshed vendor and regional routing guides.

### Changed

- **Gemini / Vertex LLM configuration** — Aligned Gemini and Vertex LLM config handling; the URL is now always included in Gemini and Vertex LLM configurations, and `project_id`, `location`, and `adc_credentials_string` are passed under `params` in the VertexAI configuration.

### Fixed

- **Avatar configurations** — `SenseTimeAvatar` now treats `sceneList` as optional, and `AnamAvatar` requires `avatar_id` instead of `persona_id`.

## [v2.3.0] — 2026-06-17

### Added

- **CN vendor support** — Area-aware `Agora`/`AsyncAgora` clients and `Agent` builders (`CNAgent`/`GlobalAgent`) with a CN vendor catalog and CN/global API routing. The bound client does not enforce area/vendor compatibility, so CN and global vendors can be mixed.
- **SenseTime avatar** — Added `SenseTimeAvatar` configuration and validation.

### Changed

- **`turn_detection` accepts a dict** — `Agent(turn_detection=...)` now also accepts a plain mapping in addition to the typed config; it is coerced into the request model when the start request is built.

### Fixed

- **Python 3.8 compatibility** — Replaced PEP 585 builtin generics (`list[...]`) in the new vendor models with `typing` equivalents so pydantic can build the models on Python 3.8.

## [v2.2.0] — 2026-06-05

### Added

- **Expanded provider surface** — Added generated API support for the latest Conversational AI vendors and configuration types, including Dify LLM and Generic Avatar.
- **Interaction language handling** — AgentKit now consistently derives REST `asr.language` from `turn_detection.language` while keeping provider-specific STT language values under `asr.params`.
- **Deepgram keyterm** — Added `keyterm` support on `DeepgramSTT`, serialized as `asr.params.keyterm`.

### Changed

- **MiniMax managed presets** — MiniMax preset-backed TTS now keeps the preset model as an internal hint while sending only supported partial TTS settings such as `voice_setting.voice_id`.
- **Vertex AI LLM routing** — `VertexAILLM` now keeps project and location in the generated endpoint URL instead of duplicating them in `llm.params`.

### Fixed

- **Provider wire keys** — Corrected alias-sensitive TTS payloads so Google TTS emits `VoiceSelectionParams` and `AudioConfig`, Rime TTS emits `modelId`, and Murf TTS preserves `voiceId`.
- **AgentKit request validation** — Start request validation now de-aliases REST-shaped provider dictionaries before constructing generated request models, while still allowing preset and pipeline-backed partial configs.
- **Request body coverage** — Added regression tests for BYOK, preset-backed, mixed preset/BYOK, and pipeline override request shapes across provider configurations.
- **Python docs examples** — Added a docs guard to keep Python examples on snake_case kwargs while allowing documented JSON wire keys.

## [v2.1.0] — 2026-06-02

### Added

- **Turn detection language** — AgentKit now manages Agora interaction language through `turn_detection.language`, validates it against the supported BCP-47 language list, and sends the default `en-US` when no language is provided.
- **Provider parameter parity** — ASR, LLM, MLLM, TTS, and avatar wrappers expose typed provider parameters plus passthrough fields where the generated core supports additional properties.

### Changed

- **Generated core refresh** — Regenerated core types from the v2.1 API schema.
- **Deepgram TTS passthrough** — `DeepgramTTS` now uses `additional_params` for passthrough fields and flattens them into `tts.params`; the removed nested `params.params` shape is no longer documented or emitted.
- **OpenAI TTS** — Docs and tests now reflect the generated core shape, including `instructions` and `speed` under `tts.params`.
- **TTS provider docs** — Updated TTS provider reference tables to match implemented wrapper fields and generated core params.

### Fixed

- **Managed-provider validation** — AgentKit validation now distinguishes preset-backed providers from BYOK providers so required provider fields are only required when credentials are caller-supplied.
- **Language placement** — Provider-specific STT language values remain under `asr.params`; the REST `asr.language` field is populated from `turn_detection.language`.

## [v2.0.0] — 2026-05-21

### Added

- **Type aliases** — `AsrConfig` (= `SttConfig`), `is_avatar_token_managed`, think type aliases (`ThinkOnListeningAction`, etc.), and think value constants.
- **`XaiGrok`** — New MLLM wrapper for xAI Grok (`mllm.vendor`: `"xai"`), including Realtime API URL, voice, language, sample rate, modalities, messages, and MLLM turn detection support.
- **`GenericAvatar`** — New generic avatar wrapper (`vendor: "generic"`) for custom avatar providers.
- **Avatar token enrichment** — `AgentSession.start()` now fills missing generic avatar `agora_appid` and `agora_channel` from the session and generates missing avatar `agora_token` values for HeyGen, LiveAvatar, and Generic avatars using each avatar's `agora_uid`.
- **Turn pagination** — `AgentSession.get_turns()` and `AsyncAgentSession.get_turns()` now accept `page_index` and `page_size`. New `get_all_turns()` helpers fetch and combine all pages.
- **Greeting interruption control** — LLM vendor `greeting_configs` now accepts the typed `LlmGreetingConfigs` shape, including v2.7 `interruptable`.
- **Type alias parity** — Added public aliases for v2.7 generated types such as `LlmConfig`, `TtsConfig`, `SttConfig`, `MllmConfig`, `AvatarConfig`, `AgentConfigUpdate`, `ConversationTurns`, `ConversationHistory`, `SessionInfo`, `Labels`, `SpeakPriority`, and `FillerWordsContentSelectionRule`.

### Changed

- **ConvoAI token options** — `generate_convo_ai_token()` now accepts an integer `uid` and handles the internal token string conversion for users, agents, and avatars.
- **Avatar token generation** — Removed the dedicated `generate_avatar_rtc_token()` wrapper; avatar RTC tokens use the existing ConvoAI token helper.
- **Avatar token gating** — Session enrichment uses `is_avatar_token_managed` (vendor-only); UID checks remain in session logic.
- **`XaiGrok` is the primary xAI MLLM class** — Matches the product name ([xAI Grok](https://docs.agora.io/en/conversational-ai/models/mllm/xai)) and the TypeScript/Go SDKs.
- **Package version** — Bumped to `v2.0.0` to match the Fern-generated SDK headers.
- **PyPI distribution rename** — The published package name is now `agora-agents` (formerly `agora-agent-server-sdk`). The Python import path remains `agora_agent`.
- **RTM data channel default** — When `advanced_features.enable_rtm=True`, AgentKit now defaults `parameters.data_channel` to `"rtm"` unless the caller explicitly sets a data channel.
- **Agent-level LLM overrides** — In the standard ASR + LLM + TTS pipeline, agent-level `greeting`, `failure_message`, and `max_history` now override vendor defaults, matching the TypeScript SDK. In MLLM mode, agent-level `greeting` and `failure_message` fill only missing fields.
- **MLLM core alignment** — MLLM wrappers no longer expose or emit unsupported `predefined_tools` or `max_history` fields because they are not present in the generated v2.7 core `mllm` type.
- **MLLM without TTS** — MLLM sessions no longer require separate TTS, STT, or LLM vendor configuration.
- **Avatar pipeline support** — Avatar vendors are now explicitly limited to the cascading ASR + LLM + TTS pipeline. Combining `with_avatar()` with `with_mllm()` is rejected at `Agent.to_properties()` and `AgentSession.start()` (matching the TypeScript SDK), with a disabled avatar (`enable=False`) still permitted alongside MLLM.
- **VertexAI parity** — `VertexAI.to_config()` now spreads `additional_params` first so explicit `model`, `project_id`, `location`, and `adc_credentials_string` fields always win, matching the TypeScript and Gemini Live wrappers.
- **Pagination guard parity** — `AgentSession.get_all_turns()` and `AsyncAgentSession.get_all_turns()` now raise `RuntimeError` if the server's pagination metadata is missing (`page_index`/`total_pages`/`is_last_page`) or if the next page does not advance, matching the TypeScript SDK.

### Migration notes

- **PyPI package rename** — Install `agora-agents` instead of `agora-agent-server-sdk` (`pip install agora-agents` or `poetry add agora-agents`). The import path is unchanged (`from agora_agent import ...`). The legacy PyPI distribution name remains available as a compatibility shim that re-exports the public API from `agora-agents`.
- **Deprecated aliases** — Use `LiveAvatarAvatar` instead of `HeyGenAvatar`, `is_avatar_token_managed` instead of `is_rtc_avatar`, and `ThinkOn*` / `ThinkResponse` instead of `AgentThinkRequestOn*` / `AgentThinkResponse`.

- **`think()` default** — The server default for `on_listening_action` changed from `inject` to `interrupt` in API v2.7. Pass `on_listening_action="inject"` explicitly to preserve the old behavior.
- **Turn analytics pagination** — Sessions with more than 50 turns must request additional pages via `get_turns(page_index=..., page_size=...)` or use `get_all_turns()`.
- **Error reasons** — API v2.7 adds status codes `401`, `429`, and `500`; `InvalidRequest` is split into `InvalidRequestBody`, `MissingRequiredField`, and `InvalidFieldValue`, with new reasons such as `ServiceNotEnabled`, `AccountSuspended`, and `ResourceAllocationFailed`.
- **Event `112`** — Webhook event `112 turns finished` can be used as an alternative batch delivery path for post-session turn data.

## [v1.4.1] — 2026-05-18

### Fixed

- **Release workflow** — Publish to PyPI with the `PYPI_API_TOKEN` secret.

## [v1.4.0] — 2026-05-13

### Added

- **`DeepgramTTS`** — New TTS vendor wrapper for Deepgram (Beta). Accepts `api_key`, `model`, `base_url`, `sample_rate`, `additional_params`, and `skip_patterns`.
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

- **`AresSTT`** — Removed redundant `language` key from the `params` dict. Ares only selects the provider; AgentKit populates REST `asr.language` from `turn_detection.language`. `params` is only included when `additional_params` is provided.
- **`OpenAIRealtime` / `VertexAI` (MLLM)** — Agent-level `greeting` and `failure_message` defaults are now correctly applied when missing in MLLM mode. Previously these values were silently dropped.
- **`VertexAI` (MLLM)** — `messages` is emitted at the MLLM top level, matching the generated core SDK contract.

### Changed

- **`OpenAITTS`** — Renamed constructor parameter `key` → `api_key` to match the Agora server API expectation. ⚠️ **Breaking change.**
- **`CartesiaTTS`** — Renamed constructor parameter `key` → `api_key`. Voice is now serialized as `{"mode": "id", "id": "<voice_id>"}` instead of a flat `voice_id` string. ⚠️ **Breaking change.**
- **`HeyGenAvatar`** — Removed legacy fields `avatar_name`, `voice_id`, `language`, `version`. Added `agora_token`, `avatar_id`, `enable`, `disable_idle_timeout`, `activity_idle_timeout`. The config now includes a top-level `enable` field (defaults `true`). ⚠️ **Breaking change.**

### Added

- **`OpenAITTS`** — New optional parameters: `instructions` (str) and `speed` (float).
- **`CartesiaTTS`** — `voice_id` user-facing field is preserved; voice is serialized to the required nested object format automatically.
- **`RimeTTS`** — New optional parameters: `lang` (str), `sampling_rate` (int, serialized as `samplingRate`), `speed_alpha` (float, serialized as `speedAlpha`).
- **`OpenAIRealtime`** — New optional parameter: `failure_message` (str).
- **`VertexAI` (MLLM)** — New optional parameter: `failure_message` (str).
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
