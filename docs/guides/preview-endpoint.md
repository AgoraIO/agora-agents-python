---
sidebar_position: 10
title: Preview Endpoint
description: How AgoraPreview routes to preview providers, and how the gateway's agora-feature gate header behaves.
---

# Preview Endpoint

Some providers ship on a preview gateway before they reach the production Conversational AI environment. `AgoraPreview` (and `AsyncAgoraPreview`) are drop-in replacements for `Agora` / `AsyncAgora` that point every request at that gateway and attach the header it routes on.

Everything in `agentkit/preview/` is temporary by design. When these providers go GA, the package is deleted and the vendor classes move into `vendors/mllm.py`.

## Using the preview client

```python
import os

from agora_agent import Area
from agora_agent.agentkit import Agent
from agora_agent.agentkit.preview import AgoraPreview, GeminiCleverChatter

client = AgoraPreview(
    area=Area.US,
    app_id=os.environ["AGORA_APP_ID"],
    app_certificate=os.environ["AGORA_APP_CERTIFICATE"],
)

session = (
    Agent(client=client)
    .with_mllm(GeminiCleverChatter(api_key=os.environ["GOOGLE_API_KEY"], thinking_level="medium"))
    .create_session(channel="demo", agent_uid="1", remote_uids=["100"])
)
agent_id = session.start()
```

`AsyncAgoraPreview` is the same, with `await session.start()`.

Auth, the `Agent` builder, `AgentSession`, and every vendor class work exactly as they do with `Agora`. Only two things differ: where requests go, and the gate header.

## The gate header

The gateway routes preview traffic on a single request header:

```
agora-feature: gemini-live
```

| Constant | Value |
|---|---|
| `PREVIEW_FEATURE_HEADER` | `agora-feature` |
| `PreviewFeatures.GEMINI_LIVE` | `gemini-live` |

Select the families a client requests with `features`:

```python
client = AgoraPreview(area=Area.US, app_id=..., app_certificate=..., features=["gemini-live"])
```

### The header is not overridable

The gate header is merged **after** caller-supplied `headers`, so custom headers cannot drop or blank it:

```python
client = AgoraPreview(
    area=Area.US,
    app_id=...,
    app_certificate=...,
    headers={"agora-feature": "", "x-custom": "kept"},
)
# Requests still send agora-feature: gemini-live, and x-custom: kept
```

This ordering is deliberate and load-bearing. A preview request that loses the header is not rejected — it routes to the production environment, where the preview providers do not exist. Use `features` to change the value; there is no supported way to remove it.

The header rides **every** verb, not just `start()` — `say`, `interrupt`, `get_history`, `stop`, `client.agents.*`, and `client.stop_agent()`. `stop_agent()` matters in particular, because services typically build a fresh client in an end-call route rather than holding the session that started the agent.

## Preview providers bypass request validation

The generated request models mirror what production serves, so `asr.vendor = "gemini"` is not a member of the generated `Asr` union and pydantic rejects it.

`_start_properties_from_mapping` catches that and, when `required_preview_features()` recognises the config, passes the mapping through unvalidated instead of raising. Production configs still get full validation — only configs the preview gateway understands take the bypass.

This is worth knowing when adding a preview provider: if a new vendor is missing from the generated unions, register it in the detection sets in `preview/client.py` rather than editing generated code.

## Intake node behavior

The gateway decides where a request goes before it validates the body. That produces failure modes that look like outages but are routing problems.

| Symptom | What it means |
|---|---|
| `503` `{"reason":"ServiceUnavailable"}` on `POST .../join` | The gate header was not recognised. The request died before validation, so the body is irrelevant. |
| `401` `Missing authorization header` | Routing worked; auth did not. |
| `404` `no Route matched with those values` | The base URL path is wrong. |
| `400` validation error | You are past the gate. The header is fine and the body is the problem. |

The 503 is the one that misleads. It reads as a partner-side outage and invites waiting it out, when the fix is usually a one-line header change.

Observed on the `gemini-live` rollout in August 2026, when the gateway had not yet been configured to route on `agora-feature` and every request fell through to a 503. That was fixed server-side on 2026-08-09, so the 503 is not currently reproducible — the mapping is recorded here because it is the failure signature a newly provisioned preview family is most likely to hit first.

### Diagnosing without starting a billable agent

Two probes, neither of which allocates an agent:

1. **`GET .../v2/projects/{appId}/agents`** — a `200` proves host, auth, and routing are all healthy. If this succeeds while `join` fails, the problem is specific to the start path.
2. **A deliberately invalid start body** — send properties with no `llm` and no `mllm` at all. A `400` means you are past the gate; a `503` means you are not. This is what separates "my config is wrong" from "my header is wrong".

### Known gap (as of 2026-08-09)

A missing gate header is *intended* to route to the production environment, where a preview config would fail. In practice an ungated start currently **succeeds** against the preview host, so the fallback is not observable from the client side.

The SDK cannot control the intake node, and this does not affect SDK users because the header is pinned. It matters only for callers hitting the REST API directly, who may get a request that appears to succeed while silently landing in the wrong environment. Flag it to the endpoint owner rather than working around it in SDK code.

## Guard against the wrong client

Preview providers used with a plain `Agora` client raise before any request is sent:

```
ValueError: This agent uses preview providers that require the preview endpoint
(gemini-live). Create the session with AgoraPreview instead of Agora, and make
sure its `features` include: gemini-live.
```

`assert_preview_support` reads the resolved request body rather than the vendor classes, so hand-written configs are covered too. `mllm.vendor` is `"gemini"` for both the production Gemini Live provider and the preview ones, so the vendor name alone settles nothing — see [How a config is recognised as preview](#how-a-config-is-recognised-as-preview) for the two signals it uses instead.

## Preview vendors

| Class | Wire vendor | Model |
|---|---|---|
| `GeminiWalkieTalkie` | `mllm.vendor = "gemini"` | `walkie-talkie` |
| `GeminiCleverChatter` | `mllm.vendor = "gemini"` | `clever-chatter` |

MLLM sessions have no ASR, LLM, or TTS stage — the model handles the whole exchange end to end, so `transcribe_agent` and `transcribe_user` are the only source of transcripts.

`thinking_level` is exclusive to clever-chatter, which is why it is a separate class rather than a field on a shared one — `GeminiWalkieTalkie(thinking_level=...)` is a validation error, not a silently ignored argument.

The preview MLLMs differ from the production `GeminiLive` in two ways the gateway requires: `params.api_key` is repeated inside `params`, and `url` defaults to the Gemini Developer API host rather than a WebSocket endpoint.

Language is set with `language_codes`, which serializes to `params.language_codes` and is omitted when unset. Note the plural: the singular `mllm.params.language` belongs to xAI Grok in the Agora schema, and the [production Gemini Live provider](https://docs.agora.io/en/ai/models/mllm/gemini) sends no language field at all — so the preview MLLMs never send it.

In MLLM mode, agent-level `instructions` is not sent — pass `instructions` to the vendor instead, where it serializes to `mllm.params.instructions`.

The greeting argument is `greeting`, not `greeting_message`, and it serializes to `greeting`. The new Gemini preview models read that spelling; `greeting_message` is what the production providers use.

Both placements work — an agent-level `greeting` and a vendor-level one both reach the model:

```python
Agent(client=client, greeting='Hello').with_mllm(GeminiWalkieTalkie(api_key=key))
Agent(client=client).with_mllm(GeminiWalkieTalkie(api_key=key, greeting='Hello'))
```

That is not automatic: `Agent.to_properties` writes an agent-level greeting to `mllm.greeting_message`, the production spelling, which these models ignore. `apply_preview_shape` retargets it at session start — see [Preview wire-shape translation](#preview-wire-shape-translation).

### The MLLM rename in flight

Google is renaming the MLLM codenames to conventional model IDs:

| Class | Model sent today | Post-rename model |
|---|---|---|
| `GeminiWalkieTalkie` | `walkie-talkie` | `gemini-3.5-live` |
| `GeminiCleverChatter` | `clever-chatter` | `gemini-3.5-live-thinking` |

The classes still send the codenames. As of 2026-08-19 the new IDs are propagating through Google's fleet and are not live everywhere, while the codenames work — Google will confirm when the rename lands. Both spellings are in the known-model set, and a name that is in neither is still recognised by its envelope (see [How a config is recognised as preview](#how-a-config-is-recognised-as-preview)), so `model=` opts a single instance into a new name safely:

```python
GeminiWalkieTalkie(api_key=..., model=GeminiPreviewMllmModels.LIVE_35)
```

When the rename lands, repoint `GEMINI_PREVIEW_MLLM_DEFAULTS` in `preview/vendors.py` at `LIVE_35` / `LIVE_35_THINKING`. That is the entire cutover.

## Preview wire-shape translation

The preview route spells two MLLM fields differently from the Agora schema. Where the vendor classes own the field they simply emit the preview spelling, but `greeting` is different: the shared `Agent` builder writes it, using the production spelling that is correct for every GA vendor.

So `apply_preview_shape` runs at session start, immediately after `assert_preview_support`, and retargets those fields on a preview config:

| Written by the builder | Sent to the preview route |
|---|---|
| `mllm.greeting_message` | `mllm.greeting` |

The vendor's own value wins; the production-spelled one is the fallback. That also migrates a hand-written `greeting_message` onto the preview key, so an existing MLLM config keeps working after only swapping the model.

`mllm.failure_message` is deliberately **not** translated — it is an Agora engine feature rather than a Gemini one, so it keeps its schema spelling.

A production MLLM is left untouched, so the translation is safe to run unconditionally. Teaching the shared builder about preview spellings was the alternative; keeping it here means the whole thing disappears with `agentkit/preview/` at GA instead of leaving a vestigial hook behind.

### How a config is recognised as preview

Two independent signals, either one sufficient:

1. **``mllm.params.model`` is in the known-model set** — the four names in ``preview/client.py`` (both codenames and both post-rename IDs).
2. **The config carries the preview envelope** — ``params.api_key`` set *and* ``url`` on the Gemini Developer API host. This is exactly what the preview vendor classes emit and what the production ``GeminiLive`` vendor does not: it leaves ``params.api_key`` unset and defaults ``url`` to ``""`` or a WebSocket endpoint.

The second signal exists because the first one fails silently on its own. Overriding ``model`` is the documented escape hatch for a rename that lands ahead of an SDK release, so a name this SDK has never seen is reachable by following the advice above — and with model-name matching alone, that config would quietly stop getting ``apply_preview_shape``. No error, no warning: the greeting would land in ``greeting_message``, which these models ignore, and the agent would simply never greet.

Adding a newly announced model name to the set is still worth doing — it keeps recognition working for hand-written configs, which carry no envelope. But forgetting to is no longer a silent failure.

### The vendor class is not the whole wire shape

This translation exists because of a bug worth not repeating. `GeminiWalkieTalkie` emitted `greeting` correctly and nothing in `preview/vendors.py` was wrong — but an agent-level greeting still never reached the model, because `Agent.to_properties` **also writes into the vendor config**, using production spellings, after the vendor is done with it.

Every field the shared builder injects is listed below. Each one is a candidate for the same bug on a preview route:

| Category | Field | Written from | When |
|---|---|---|---|
| `mllm` | `greeting_message` | agent-level `greeting` | only when the vendor left it unset (`setdefault`) |
| `mllm` | `failure_message` | agent-level `failure_message` | only when the vendor left it unset (`setdefault`) |
| `mllm` | `enable` | `with_mllm()` | always |
| `asr` | `language` | turn detection `language` | **always — overwrites any vendor value** |
| `llm` | `system_messages`, `greeting_message`, `greeting_configs`, `failure_message`, `max_history` | agent-level `instructions`, `greeting`, `greeting_configs`, `failure_message`, `max_history` | only when the vendor left them unset |

So when a preview provider documents a field that appears in that table, putting it on the vendor class is not the whole fix. One of three things applies:

- **The preview route spells it differently** — add an entry to `_PREVIEW_MLLM_FIELD_RENAMES` in `preview/client.py`. One entry, and both the vendor-level and agent-level placements start working.
- **The builder always overwrites it** (`asr.language`) — do not expose it on the vendor class at all; it would be an argument the builder silently discards, and `extra="forbid"` turns a stale keyword into an error rather than a no-op.
- **It is an Agora engine field rather than the provider's** (`failure_message`) — leave it in the schema spelling.

### Verify against the request body, not the vendor output

`to_config()` returning the right dict proves nothing about what ships, because the builder runs after it. Both checks are needed:

1. A unit test on the vendor class, for the fields the vendor owns.
2. An **end-to-end test that starts a session against a mock transport and asserts on the captured request body** — the only check that sees the builder's injections and the preview translation. Every preview vendor has one in `tests/custom/test_preview.py`.

The manual version is `debug=True`, which logs the fully resolved body. Diff it against the payload the provider documented, key by key. A value sitting under a name the route ignores fails **silently** — no error, no validation complaint, the agent simply never greets. That is the failure mode this whole section exists to catch, and it is invisible to type checking, to pydantic validation, and to any test that stops at the vendor class.

Wire parity across the three SDKs is a hard requirement, so a change here lands in Python, TypeScript, and Go together, verified by diffing the serialized bodies.

## Adding a future preview family

Everything preview-only lives under `agentkit/preview/` so it can be deleted wholesale at GA. To add a family:

1. Add an attribute to `PreviewFeatures` in `preview/client.py`. The value is what goes in the `agora-feature` header.
2. Add the vendor classes to `preview/vendors.py`, extending the same `BaseSTT` / `BaseMLLM` / `BaseLLM` bases as production vendors so the builder accepts them unchanged.
3. Register the detection keys — for an MLLM family, the model names in `_PREVIEW_MLLM_MODELS` plus an envelope check — so `required_preview_features()` recognises configs that need the new family. This is also what lets the config through the validation bypass described above.
4. Export from `preview/__init__.py`. Preview symbols stay in that subpackage rather than being re-exported from `agentkit/__init__.py`, which is what makes the GA deletion a single-directory change.
5. **Diff the resolved request body against the payload the provider documented**, not the vendor class output. Anything the shared builder writes under a different name belongs in `_PREVIEW_MLLM_FIELD_RENAMES` — see [The vendor class is not the whole wire shape](#the-vendor-class-is-not-the-whole-wire-shape).
6. Add an end-to-end test that starts a session and asserts on the captured body, alongside the vendor-class unit test.

If the generated request models do not cover the new provider, rely on the bypass in `_start_properties_from_mapping` rather than editing generated code. Generated files are overwritten on the next Fern run; `.fernignore` protects `src/agora_agent/agentkit/`.

At GA, delete `preview/` and move the vendor classes into `vendors/mllm.py`.

## Base URL

```
https://partner.ai.agora.io/preview/api/conversational-ai-agent
```

Request paths append to it exactly as they do in production — `POST {base}/v2/projects/{appId}/join`. The service path segment is part of the base: `https://partner.ai.agora.io/preview/api/` alone returns `404 no Route matched with those values`.

The preview host is a single partner endpoint with no regional replicas, so `next_region()` and `select_best_domain()` are no-ops and `area` affects only token generation. Override the host for a staging gateway with `base_url`.

## Debug output

`debug=True` prints the resolved start request. The body is passed through `redact_secrets` first, which replaces vendor API keys, the RTC token, and the App ID with `[REDACTED]` while leaving model names, voices, and instructions readable. The same redaction is applied to the httpx request log.

Empty strings are left visible on purpose: `""` is the signature of an unset environment variable, and hiding it would disguise the exact misconfiguration the debug output exists to surface.

## Related

- [Regional Routing](./regional-routing.md) — the production domain pool the preview client bypasses
- [Error Handling](./error-handling.md) — `ApiError` and API error handling
