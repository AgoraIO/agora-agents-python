# Python AgentKit Snake Case API Audit

Scope: `agora-agents-python` public AgentKit wrappers, docs, and tests.

Search terms:

```bash
rg -n "apiKey|baseUrl|modelId|voiceId|groupId|keyTerm|turnDetection|inputAudioTranscription|greetingMessage|failureMessage|projectId|adcCredentialsString|sampleRate|targetLanguageCode|resourceName|deploymentName" agora-agents-python
```

## Result

No shipped camelCase public Python constructor kwargs were found in source or docs examples. No deprecated alias helper is required for this pass.

| File | Class / symbol | Public arg or example | Current spelling | Desired Python spelling | `to_config()` key | Wire key | Action | Compatibility needed | Test coverage |
|---|---|---|---|---|---|---|---|---|---|
| `src/agora_agent/agentkit/vendors/tts.py` | `GoogleTTS` | constructor arg | `voice_name` | `voice_name` | `params.VoiceSelectionParams` | `params.VoiceSelectionParams` | keep | no | `tests/custom/test_tts_vendors.py` |
| `src/agora_agent/agentkit/vendors/tts.py` | `RimeTTS` | constructor arg | `model_id` | `model_id` | `params.modelId` | `params.modelId` | keep | no | `tests/custom/test_tts_vendors.py` |
| `src/agora_agent/agentkit/vendors/tts.py` | `MurfTTS` | constructor arg | `voice_id` | `voice_id` | `params.voiceId` | `params.voiceId` | keep | no | `tests/custom/test_tts_vendors.py`, `tests/custom/test_request_body.py` |
| `src/agora_agent/types/rime_tts_params.py` | generated model | generated alias | `modelId` | n/a | `model_id` | `modelId` | keep | no | `tests/custom/test_tts_vendors.py` |
| `src/agora_agent/types/murf_tts_params.py` | generated model | generated alias | `voiceId` | n/a | `voice_id` | `voiceId` | keep | no | `tests/custom/test_tts_vendors.py` |
| `tests/custom/test_request_body.py` | wire assertion | payload key | `voiceId` | n/a | `params.voiceId` | `params.voiceId` | keep | no | request-body test |
| `tests/custom/test_tts_vendors.py` | wire assertion | payload key | `modelId`, `voiceId`, `VoiceSelectionParams` | n/a | generated model fields | wire aliases | keep | no | wire serialization test |

## Guardrail Added

`tests/custom/test_docs_snake_case.py` scans Python markdown code fences and fails on common camelCase kwargs such as `apiKey`, `baseUrl`, `modelId`, `voiceId`, `projectId`, and `greetingMessage`. JSON, TypeScript, Go, shell, and YAML examples are skipped so wire payload examples can retain required non-Python keys.
