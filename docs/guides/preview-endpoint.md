---
sidebar_position: 10
title: Preview Endpoint
description: How AgentSession routes preview providers and pins the gateway's agora-feature gate header.
---

# Preview Endpoint

Some providers ship on a preview gateway before they reach the production Conversational AI environment. Standard `Agora` and `AsyncAgora` clients detect these providers from the resolved start body and route that session automatically.

Everything in `agentkit/preview/` is temporary by design. When these providers go GA, the package is deleted and the vendor classes move into `vendors/stt.py`.

## Using a preview provider

```python
import os

from agora_agent import Agora, Area
from agora_agent.agentkit import Agent
from agora_agent.agentkit import Gemini, GoogleTTS
from agora_agent.agentkit.preview import GeminiSTT

client = Agora(
    area=Area.US,
    app_id=os.environ["AGORA_APP_ID"],
    app_certificate=os.environ["AGORA_APP_CERTIFICATE"],
)

google_api_key = os.environ["GOOGLE_API_KEY"]
session = (
    Agent(client=client)
    .with_stt(GeminiSTT(api_key=google_api_key, language_codes=["en-US"]))
    .with_llm(Gemini(api_key=google_api_key, model="gemini-2.0-flash"))
    .with_tts(GoogleTTS(
        key=google_api_key,
        voice_name="en-US-Chirp3-HD-Charon",
        language_code="en-US",
    ))
    .create_session(channel="demo", agent_uid="1", remote_uids=["100"])
)
agent_id = session.start()
```

`AsyncAgora` behaves the same, with `await session.start()`.

Routing is session-scoped. Preview session calls use the preview host and pinned gate header; GA sessions created from the same client continue using the production regional endpoint.

## The gate header

The gateway routes preview traffic on a single request header:

```
agora-feature: gemini-live
```

| Constant                      | Value           |
| ----------------------------- | --------------- |
| `PREVIEW_FEATURE_HEADER`      | `agora-feature` |
| `PreviewFeatures.GEMINI_LIVE` | `gemini-live`   |

### The header is not overridable

For preview sessions, the gate header is merged **after** caller-supplied client `headers`, so custom headers cannot drop or blank it:

```python
client = Agora(
    area=Area.US,
    app_id=...,
    app_certificate=...,
    headers={"agora-feature": "", "x-custom": "kept"},
)
# Requests still send agora-feature: gemini-live, and x-custom: kept
```

This ordering is deliberate and load-bearing. A preview request that loses the header is not rejected — it routes to the production environment, where the preview providers do not exist.

The header rides every session verb, not just `start()` — `say`, `interrupt`, `think`, `update`, `get_history`, `get_info`, `get_turns`, and `stop`. The top-level `Agora.stop_agent()` and `AsyncAgora.stop_agent()` methods remain production-only because they do not carry session routing state.

## Preview providers bypass request validation

The generated request models mirror what production serves, so `asr.vendor = "gemini"` is not a member of the generated `Asr` union and pydantic rejects it.

`_start_properties_from_mapping` catches that and, when `required_preview_features()` recognises the config, passes the mapping through unvalidated instead of raising. Production configs still get full validation — only configs the preview gateway understands take the bypass.

This is worth knowing when adding a preview provider: if a new vendor is missing from the generated unions, register it in the detection sets in `preview/client.py` rather than editing generated code.

## Intake node behavior

The gateway decides where a request goes before it validates the body. That produces failure modes that look like outages but are routing problems.

| Symptom                                                    | What it means                                                                                      |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `503` `{"reason":"ServiceUnavailable"}` on `POST .../join` | The gate header was not recognised. The request died before validation, so the body is irrelevant. |
| `401` `Missing authorization header`                       | Routing worked; auth did not.                                                                      |
| `404` `no Route matched with those values`                 | The base URL path is wrong.                                                                        |
| `400` validation error                                     | You are past the gate. The header is fine and the body is the problem.                             |

The 503 is the one that misleads. It reads as a partner-side outage and invites waiting it out, when the fix is usually a one-line header change.

Observed on the `gemini-live` rollout in August 2026, when the gateway had not yet been configured to route on `agora-feature` and every request fell through to a 503. That was fixed server-side on 2026-08-09, so the 503 is not currently reproducible — the mapping is recorded here because it is the failure signature a newly provisioned preview family is most likely to hit first.

### Diagnosing without starting a billable agent

Two probes, neither of which allocates an agent:

1. **`GET .../v2/projects/{appId}/agents`** — a `200` proves host, auth, and routing are all healthy. If this succeeds while `join` fails, the problem is specific to the start path.
2. **A deliberately invalid start body** — send properties with no `llm` and no `mllm` at all. A `400` means you are past the gate; a `503` means you are not. This is what separates "my config is wrong" from "my header is wrong".

### Known gap (as of 2026-08-09)

A missing gate header is _intended_ to route to the production environment, where a preview config would fail. In practice an ungated start currently **succeeds** against the preview host, so the fallback is not observable from the client side.

The SDK cannot control the intake node, and this does not affect SDK users because the header is pinned. It matters only for callers hitting the REST API directly, who may get a request that appears to succeed while silently landing in the wrong environment. Flag it to the endpoint owner rather than working around it in SDK code.

## Session routing detection

`required_preview_features()` reads the resolved request body rather than the vendor classes, so hand-written configs and preset resolution are covered too. It keys on `asr.vendor` — the vendor names served only by the preview endpoint, listed as `_PREVIEW_ASR_VENDORS` in `preview/client.py`.

## Preview vendors

| Class       | Wire vendor             | Model                        |
| ----------- | ----------------------- | ---------------------------- |
| `GeminiSTT` | `asr.vendor = "gemini"` | `gemini-3.5-transcribe-live` |

`GeminiSTT` is an ASR stage, so it needs an LLM and a TTS vendor alongside it. The sample above uses Gemini LLM and Google TTS with the same Google API key. Mixing in other vendors is still valid; preview routing triggers only on `asr.vendor`.

### ASR language selection

Gemini Transcribe takes `params.language_codes`, an **array**, in place of the singular `params.language` other ASR vendors use.

```python
# Auto-detect (the default) — language_codes is not sent at all
GeminiSTT(api_key=...)

# Commit to one language
GeminiSTT(api_key=..., language_codes=["en-US"])

# Let the model choose between several
GeminiSTT(api_key=..., language_codes=["en-US", "es-ES"])

# Auto-detect, stated outright
GeminiSTT(api_key=..., language_codes=[])
```

`language_codes` is omitted from the request unless you supply it, which is how the provider spells auto-detect. Omitting the field and sending `[]` mean the same thing.

`GeminiSTT` takes **no `language` argument**. `Agent` always derives the top-level `asr.language` from the turn detection language — as it does for every STT vendor — so a vendor-level copy would be a no-op the builder overwrites. Set the interaction language on turn detection, and the transcription languages on `language_codes`; they are separate settings and neither feeds the other. The model forbids extra fields, so a stale `language=` argument raises rather than being silently dropped.

| Setting                 | Where it belongs               | What it controls            |
| ----------------------- | ------------------------------ | --------------------------- |
| interaction language    | turn detection `language`      | top-level `asr.language`    |
| transcription languages | `language_codes` on the vendor | `asr.params.language_codes` |

`custom_vocabulary` biases recognition toward words the model would otherwise mis-hear — product names, jargon, proper nouns. It is omitted from the request entirely when unset.

```python
GeminiSTT(api_key=..., custom_vocabulary=["Agora", "Kubernetes"])
```

`word_timestamp` is also omitted unless you set it explicitly. Gemini does not support enabled word timestamps together with `custom_vocabulary`, so `to_config()` raises `ValueError` if both are requested. Explicit `word_timestamp=False` remains compatible with custom vocabulary.

```python
GeminiSTT(api_key=..., word_timestamp=True)
```

## The vendor class is not the whole wire shape

A vendor class emitting the right dict is not proof of what ships, because `Agent.to_properties` **also writes into the vendor config** after the vendor is done with it — using the Agora schema spellings, which are correct for every GA provider but need not match what a preview route reads.

Every field the shared builder injects is listed below. Each one is a candidate for a silent mismatch on a preview route:

| Category | Field                                                                                       | Written from                                                                                 | When                                              |
| -------- | ------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| `mllm`   | `greeting_message`                                                                          | agent-level `greeting`                                                                       | only when the vendor left it unset (`setdefault`) |
| `mllm`   | `failure_message`                                                                           | agent-level `failure_message`                                                                | only when the vendor left it unset (`setdefault`) |
| `mllm`   | `enable`                                                                                    | `with_mllm()`                                                                                | always                                            |
| `asr`    | `language`                                                                                  | turn detection `language`                                                                    | **always — overwrites any vendor value**          |
| `llm`    | `system_messages`, `greeting_message`, `greeting_configs`, `failure_message`, `max_history` | agent-level `instructions`, `greeting`, `greeting_configs`, `failure_message`, `max_history` | only when the vendor left them unset              |

So when a preview provider documents a field that appears in that table, putting it on the vendor class is not the whole fix. One of three things applies:

- **The builder always overwrites it** (`asr.language`) — do not expose it on the vendor class at all; it would be an argument the builder silently discards. `GeminiSTT` takes no `language` for exactly this reason, and `extra="forbid"` turns a stale `language=` into an error rather than a no-op.
- **It is an Agora engine field rather than the provider's** (`failure_message`) — leave it in the schema spelling.
- **The preview route spells it differently** — the translation belongs in `preview/client.py`, applied at session start, so it disappears with `agentkit/preview/` at GA rather than leaving a vestigial hook in the shared builder. Nothing in this release needs one, but a future preview family may.

### Verify against the request body, not the vendor output

`to_config()` returning the right dict proves nothing about what ships, because the builder runs after it. Both checks are needed:

1. A unit test on the vendor class, for the fields the vendor owns.
2. An **end-to-end test that starts a session against a mock transport and asserts on the captured request body** — the only check that sees the builder's injections. Every preview vendor has one in `tests/custom/test_preview.py`.

The manual version is `debug=True`, which logs the fully resolved body. Diff it against the payload the provider documented, key by key. A value sitting under a name the route ignores fails **silently** — no error, no validation complaint, the agent simply never greets. That is the failure mode this whole section exists to catch, and it is invisible to type checking, to pydantic validation, and to any test that stops at the vendor class.

Wire parity across the three SDKs is a hard requirement, so a change here lands in Python, TypeScript, and Go together, verified by diffing the serialized bodies.

## Adding a future preview family

Everything preview-only lives under `agentkit/preview/` so it can be deleted wholesale at GA. To add a family:

1. Add an attribute to `PreviewFeatures` in `preview/client.py`. The value is what goes in the `agora-feature` header.
2. Add the vendor classes to `preview/vendors.py`, extending the same `BaseSTT` / `BaseMLLM` / `BaseLLM` bases as production vendors so the builder accepts them unchanged.
3. Register the detection keys — for an ASR family, the vendor name in `_PREVIEW_ASR_VENDORS` — so `required_preview_features()` recognises configs that need the new family. This is also what lets the config through the validation bypass described above.
4. Export from `preview/__init__.py`. Preview symbols stay in that subpackage rather than being re-exported from `agentkit/__init__.py`, which is what makes the GA deletion a single-directory change.
5. **Diff the resolved request body against the payload the provider documented**, not the vendor class output — see [The vendor class is not the whole wire shape](#the-vendor-class-is-not-the-whole-wire-shape).
6. Add an end-to-end test that starts a session and asserts on the captured body, alongside the vendor-class unit test.

If the generated request models do not cover the new provider, rely on the bypass in `_start_properties_from_mapping` rather than editing generated code. Generated files are overwritten on the next Fern run; `.fernignore` protects `src/agora_agent/agentkit/`.

At GA, delete `preview/` and move the vendor classes into `vendors/stt.py`.

## Base URL

```
https://partner.ai.agora.io/preview/api/conversational-ai-agent
```

Request paths append to it exactly as they do in production — `POST {base}/v2/projects/{appId}/join`. The service path segment is part of the base: `https://partner.ai.agora.io/preview/api/` alone returns `404 no Route matched with those values`.

The preview host is a single partner endpoint with no regional replicas. The parent client's regional selection is not mutated; it remains available for GA sessions.

## Debug output

`debug=True` prints the resolved start request. The body is passed through `redact_secrets` first, which replaces vendor API keys, the RTC token, and the App ID with `[REDACTED]` while leaving model names, voices, and instructions readable. The same redaction is applied to the httpx request log.

Empty strings are left visible on purpose: `""` is the signature of an unset environment variable, and hiding it would disguise the exact misconfiguration the debug output exists to surface.

## Related

- [Regional Routing](./regional-routing.md) — the production domain pool the preview client bypasses
- [Error Handling](./error-handling.md) — `ApiError` and API error handling
