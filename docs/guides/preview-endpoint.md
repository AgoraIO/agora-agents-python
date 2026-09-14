---
sidebar_position: 10
title: Preview Endpoint
description: How AgentSession routes preview providers and pins the agora-feature gate header.
---

# Preview Endpoint

Some providers may be released through a preview gateway before their production API is available. `AgentSession`
and `AsyncAgentSession` detect registered preview providers from the resolved start request and route the entire
session automatically.

OpenAI GPT Live is registered for preview routing with the `live-models` feature. Gemini STT has graduated to
production and uses the normal regional endpoint. Existing imports of `GeminiSTT` and `GeminiSTTModels` from
`agora_agent.agentkit.preview` remain supported as compatibility aliases.

```python
from agora_agent import Agent, OpenAIGPTLive

session = (
    Agent(client)
    .with_mllm(OpenAIGPTLive(api_key=openai_api_key, prompt="Be concise"))
    .create_session(channel="demo", agent_uid="1", remote_uids=["100"])
)
agent_id = session.start()
```

This session uses the preview base URL and sends `agora-feature: live-models`. A session using `GeminiSTT` uses the
client's normal GA regional endpoint without that header.

## Session-scoped routing

Preview routing does not mutate the bound `Agora` or `AsyncAgora` client. A session that needs a preview feature
receives private generated clients configured with:

- `https://partner.ai.agora.io/preview/api/conversational-ai-agent` as the base URL.
- `agora-feature` as the feature gate header.
- All custom headers, authentication settings, timeouts, and the supplied `httpx` client from the original client.

The gate header is applied after caller-provided headers, so it cannot be accidentally blanked or replaced. It is
kept on every request made through that session. Production sessions created from the same client continue using
the regional production endpoint.

## Adding a preview provider

Preview vendor classes should use the same `BaseSTT`, `BaseLLM`, `BaseMLLM`, `BaseTTS`, or `BaseAvatar` interfaces
as production vendors. Register the vendor and its feature gate in `_PREVIEW_FEATURES_BY_CATEGORY` in
`agentkit/preview/client.py`.

The registry is keyed first by request category and then by the serialized vendor name:

```python
_PREVIEW_FEATURES_BY_CATEGORY = {
    "asr": {"new_vendor": "new-vendor-feature"},
    "mllm": {"openai_gpt_live": "live-models"},
}
```

Detection uses the fully resolved request body rather than the Python class, so hand-written configs and preset
resolution follow the same routing behavior. If Fern's production request union does not contain the preview
vendor yet, the registered config bypasses that generated union while retaining normal validation for production
providers. `None` values are removed before the preview request is sent.

Add routing tests for both synchronous and asynchronous sessions when registering a provider. Tests should verify
the preview base URL, exact feature header, all lifecycle requests, caller-header precedence, and that the original
client remains configured for production.
