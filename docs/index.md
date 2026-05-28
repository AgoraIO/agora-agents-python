---
sidebar_position: 1
title: Overview
description: The Agora Conversational AI Python SDK — install, concepts, and examples.
---

# Agora Conversational AI Python SDK

The Agora Conversational AI Python SDK lets you build voice-powered AI agents on the [Agora Conversational AI](https://docs.agora.io/en/conversational-ai/overview) platform.

## Client models

- **`Agora`** for synchronous applications
- **`AsyncAgora`** for `asyncio` applications

## Conversation flows

**Cascading flow** uses ASR -> LLM -> TTS and supports the broadest set of vendor combinations.

**MLLM flow** uses a multimodal model such as OpenAI Realtime, Gemini Live, Vertex AI, or xAI Grok for end-to-end audio.

## Start here

- Start with [Quick Start](./getting-started/quick-start.md). It shows the baseline app-credentials setup and starts a cascading ASR -> LLM -> TTS agent.
- Use [MLLM Flow](./guides/mllm-flow.md) when your agent uses one realtime multimodal model, such as OpenAI Realtime, Gemini Live, Vertex AI, or xAI Grok.
- Use [Cascading Flow](./guides/cascading-flow.md) for more examples of the default ASR -> LLM -> TTS flow, including provider-specific configuration.

## How the SDK is organized

| Layer | What it does | When to use |
|---|---|---|
| **AgentKit** (`Agent`, `AgentSession`, vendor classes) | High-level builder pattern, lifecycle, typed vendors | Most use cases |
| **Generated REST clients** (`client.agents`, `client.telephony`) | Typed access to REST APIs not covered by AgentKit | Advanced use cases |

## Documentation

| Section | What you will learn |
|---|---|
| [Installation](./getting-started/installation.md) | Install the SDK and prerequisites |
| [Authentication](./getting-started/authentication.md) | App credentials and other auth modes |
| [Quick Start](./getting-started/quick-start.md) | App credentials and AgentKit |
| [Agent Builder Features](./guides/agent-builder-features.md) | Turn detection, SAL, filler words, and advanced agent options |
| [BYOK](./guides/byok.md) | Bring your own vendor credentials and config |
| [Architecture](./concepts/architecture.md) | SDK structure and generated REST clients |
| [Agent](./concepts/agent.md) | Configure agents with the fluent builder |
| [AgentSession](./concepts/session.md) | Manage the agent lifecycle |
| [Vendors](./concepts/vendors.md) | Browse all LLM, TTS, STT, MLLM, and Avatar providers |
| [Cascading Flow](./guides/cascading-flow.md) | Build an ASR -> LLM -> TTS pipeline |
| [MLLM Flow](./guides/mllm-flow.md) | Use OpenAI Realtime, Gemini Live, Vertex AI, or xAI Grok for end-to-end audio |
| [Avatars](./guides/avatars.md) | Add a digital avatar with LiveAvatar, Akool, Anam, or Generic Avatar |
| [Regional Routing](./guides/regional-routing.md) | Route requests to the nearest region |
| [Error Handling](./guides/error-handling.md) | Handle API errors with ApiError |
| [Pagination](./guides/pagination.md) | Iterate over paginated list endpoints |
| [Advanced](./guides/advanced.md) | Raw response, retries, timeouts, custom httpx client |
| [Low-Level API](./guides/low-level-api.md) | Generated REST APIs |
| [Client Reference](./reference/client.md) | Full `Agora` / `AsyncAgora` API |
| [Agent Reference](./reference/agent.md) | Full `Agent` builder API |
| [Session Reference](./reference/session.md) | Full `AgentSession` / `AsyncAgentSession` API |
| [Vendor Reference](./reference/vendors.md) | Constructor options for all vendor classes |
| [Error Reference](./reference/errors.md) | v2.7 status codes and error reason values |
