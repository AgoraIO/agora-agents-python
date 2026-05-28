# Agora Conversational AI Python SDK

[![fern shield](https://img.shields.io/badge/%F0%9F%8C%BF-Built%20with%20Fern-brightgreen)](https://buildwithfern.com?utm_source=github&utm_medium=github&utm_campaign=readme&utm_source=https%3A%2F%2Fgithub.com%2FAgoraIO-Conversational-AI%2Fagent-server-sdk-python)
[![pypi](https://img.shields.io/pypi/v/agora-agents)](https://pypi.python.org/pypi/agora-agents)

The Agora Conversational AI SDK provides convenient access to the Agora Conversational AI APIs, 
enabling you to build voice-powered AI agents with support for both cascading flows (ASR -> LLM -> TTS) 
and multimodal flows (MLLM) for real-time audio processing.


## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [BYOK](#byok)
- [MLLM (Realtime / Multimodal)](#mllm-realtime--multimodal)
- [Documentation](#documentation)
- [Reference](#reference)
- [Exception Handling](#exception-handling)
- [Pagination](#pagination)
- [Advanced](#advanced)
  - [Access Raw Response Data](#access-raw-response-data)
  - [Retries](#retries)
  - [Timeouts](#timeouts)
  - [Custom Client](#custom-client)
- [Contributing](#contributing)

## Requirements

- Python 3.8+

## Installation

```sh
pip install agora-agents
```

## Quick Start

The recommended onboarding path is a server-side builder flow: define the agent once, configure vendors on the builder, and let AgentKit infer Agora-managed configuration when credentials are omitted.

```python
import os
import time

from agora_agent import (
    Agent,
    Agora,
    Area,
    DataChannel,
    DeepgramSTT,
    GenericAvatar,
    MiniMaxTTS,
    OpenAI,
    XaiGrok,
    expires_in_hours,
)

AGENT_PROMPT = (
    "You are a concise, technically credible voice assistant. "
    "Keep replies short unless the user asks for detail."
)

GREETING = "Hi there! I am your Agora voice assistant. How can I help?"


def start_conversation() -> str:
    app_id = os.environ["AGORA_APP_ID"]
    app_certificate = os.environ["AGORA_APP_CERTIFICATE"]

    client = Agora(
        area=Area.US,
        app_id=app_id,
        app_certificate=app_certificate,
    )

    agent = Agent(
        name=f"conversation-{int(time.time())}",
        instructions=AGENT_PROMPT,
        greeting=GREETING,
        failure_message="Please wait a moment.",
        max_history=50,
        turn_detection={
            "config": {
                "speech_threshold": 0.5,
                "start_of_speech": {
                    "mode": "vad",
                    "vad_config": {
                        "interrupt_duration_ms": 160,
                        "prefix_padding_ms": 300,
                    },
                },
                "end_of_speech": {
                    "mode": "vad",
                    "vad_config": {
                        "silence_duration_ms": 480,
                    },
                },
            },
        },
        advanced_features={
            "enable_rtm": True,
            "enable_tools": True,
        },
        parameters={
            "data_channel": DataChannel.RTM,
            "enable_error_message": True,
        },
    ).with_stt(
        DeepgramSTT(
            model="nova-3",
            language="en",
        )
    ).with_llm(
        OpenAI(
            model="gpt-4o-mini",
            greeting_message=GREETING,
            failure_message="Please wait a moment.",
            max_history=15,
            params={
                "max_tokens": 1024,
                "temperature": 0.7,
                "top_p": 0.95,
            },
        )
    ).with_tts(
        MiniMaxTTS(
            model="speech_2_6_turbo",
            voice_id="English_captivating_female1",
        )
    )

    session = agent.create_session(
        client,
        channel=f"demo-channel-{int(time.time())}",
        agent_uid="123456",
        remote_uids=["*"],
        idle_timeout=30,
        expires_in=expires_in_hours(1),
        debug=False,
    )

    return session.start()
```

### Why no token or vendor key in the example?

`Agora` generates the required ConvoAI REST auth and RTC join tokens automatically when you provide `app_id` and `app_certificate`. AgentKit inspects the builder-provided vendor configs and infers Agora-managed configuration for supported models, so you do not pass vendor API keys in this flow.

### BYOK version of the same builder flow

Use the same `Agent` builder shape, but provide credentials explicitly when you want vendor-managed billing and routing instead of Agora-managed presets.

```python
agent = Agent(
    instructions=AGENT_PROMPT,
    greeting=GREETING,
).with_stt(
    DeepgramSTT(
        api_key=os.environ["DEEPGRAM_API_KEY"],
        model="nova-3",
        language="en",
    )
).with_llm(
    OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        model="gpt-4o-mini",
        max_tokens=1024,
        temperature=0.7,
        top_p=0.95,
    )
).with_tts(
    MiniMaxTTS(
        key=os.environ["MINIMAX_API_KEY"],
        group_id=os.environ["MINIMAX_GROUP_ID"],
        model="speech_2_6_turbo",
        voice_id="English_captivating_female1",
        url="wss://api-uw.minimax.io/ws/v1/t2a_v2",
    )
)
```

Migrating from `agora-agent-server-sdk` on PyPI? Use `pip install agora-agents`; imports stay `agora_agent` — see [changelog migration notes](./changelog.md#migration-notes) or [installation guide](./docs/getting-started/installation.md#migrating-from-a-previous-package-name).

## BYOK

If you want to bring your own vendor credentials instead of using Agora-managed models, use the BYOK guide:

- [BYOK Guide](./docs/guides/byok.md)

## MLLM (Realtime / Multimodal)

Use `with_mllm()` for OpenAI Realtime, Gemini Live, Vertex AI, or xAI Grok. No STT, LLM, or TTS vendor is needed when MLLM mode is enabled.

```python
from agora_agent import Agent, OpenAIRealtime

agent = Agent(name="realtime-assistant").with_mllm(
    OpenAIRealtime(
        api_key=os.environ["OPENAI_API_KEY"],
        model="gpt-4o-realtime-preview",
        greeting_message="Hello! Ready to chat.",
    )
)
```

See the [MLLM Flow guide](./docs/guides/mllm-flow.md) for full examples with Gemini Live and Vertex AI.

## Documentation

API reference documentation is available [here](https://docs.agora.io/en/conversational-ai/overview).

## Reference

A full reference for this library is available [here](https://github.com/AgoraIO-Conversational-AI/agent-server-sdk-python/blob/HEAD/./reference.md).

## Exception Handling

When the API returns a non-success status code (4xx or 5xx response), a subclass of the following error
will be thrown.

```python
from agora_agent.core.api_error import ApiError

try:
    client.agents.start(...)
except ApiError as e:
    print(e.status_code)
    print(e.body)
```

## Pagination

Paginated requests will return a `SyncPager` or `AsyncPager`, which can be used as generators for the underlying object.

```python
from agora_agent import Agora, Area

client = Agora(
    area=Area.US,
    app_id="your-app-id",
    app_certificate="your-app-certificate",
)
response = client.agents.list(
    appid=client.app_id,
)
for item in response:
    yield item
# alternatively, you can paginate page-by-page
for page in response.iter_pages():
    yield page
```

```python
# You can also iterate through pages and access the typed response per page
pager = client.agents.list(...)
for page in pager.iter_pages():
    print(page.response)  # access the typed response for each page
    for item in page:
        print(item)
```

## Advanced

### Access Raw Response Data

The SDK provides access to raw response data, including headers, through the `.with_raw_response` property.
The `.with_raw_response` property returns a "raw" client that can be used to access the `.headers` and `.data` attributes.

```python
from agora_agent import Agora

client = Agora(
    ...,
)
response = client.agents.with_raw_response.start(...)
print(response.headers)  # access the response headers
print(response.data)  # access the underlying object
pager = client.agents.list(...)
print(pager.response)  # access the typed response for the first page
for item in pager:
    print(item)  # access the underlying object(s)
for page in pager.iter_pages():
    print(page.response)  # access the typed response for each page
    for item in page:
        print(item)  # access the underlying object(s)
```

### Retries

The SDK is instrumented with automatic retries with exponential backoff. A request will be retried as long
as the request is deemed retryable and the number of retry attempts has not grown larger than the configured
retry limit (default: 2).

A request is deemed retryable when any of the following HTTP status codes is returned:

- [408](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/408) (Timeout)
- [429](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429) (Too Many Requests)
- [5XX](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500) (Internal Server Errors)

Use the `max_retries` request option to configure this behavior.

```python
client.agents.start(..., request_options={
    "max_retries": 1
})
```

### Timeouts

The SDK defaults to a 60 second timeout. You can configure this with a timeout option at the client or request level.

```python

from agora_agent import Agora

client = Agora(
    ...,
    timeout=20.0,
)


# Override timeout for a specific method
client.agents.start(..., request_options={
    "timeout_in_seconds": 1
})
```

### Custom Client

You can override the `httpx` client to customize it for your use-case. Some common use-cases include support for proxies
and transports.

```python
import httpx
from agora_agent import Agora

client = Agora(
    ...,
    httpx_client=httpx.Client(
        proxy="http://my.test.proxy.example.com",
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    ),
)
```

## Contributing

While we value open-source contributions to this SDK, this library is generated programmatically.
Additions made directly to this library would have to be moved over to our generation code,
otherwise they would be overwritten upon the next generated release. Feel free to open a PR as
a proof of concept, but know that we will not be able to merge it as-is. We suggest opening
an issue first to discuss with us!

On the other hand, contributions to the README are always very welcome!
