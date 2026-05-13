---
sidebar_position: 5
title: Agent Builder Features
description: Configure SAL, advanced features, parameters, geofence, labels, RTC, filler words, and more.
---

# Agent Builder Features

The Agent builder supports many configuration options beyond the core LLM, TTS, and STT vendors. This guide shows how to use each feature.

For string values with a finite set of options (e.g. `data_channel`, `sal_mode`, `area`), use the type-safe constants (`DataChannel`, `SalModeValues`, `GeofenceArea`, etc.) instead of raw strings to avoid typos and get IDE autocomplete.

## Overview

| Feature | Method | Description |
|---|---|---|
| `sal` | `with_sal(config)` | Selective Attention Locking — speaker recognition and noise suppression |
| `advanced_features` | `with_advanced_features(features)` | Enable MLLM, RTM, SAL, tools |
| `tools` | `with_tools(enabled=True)` | Enable MCP tool invocation |
| `parameters` | `with_parameters(params)` | Silence config, farewell config, data channel |
| `failure_message` | `with_failure_message(msg)` | Message spoken when LLM fails |
| `max_history` | `with_max_history(n)` | Max conversation turns in LLM context |
| `geofence` | `with_geofence(config)` | Restrict backend server regions |
| `labels` | `with_labels(labels)` | Custom key-value labels (returned in callbacks) |
| `rtc` | `with_rtc(config)` | RTC media encryption |
| `filler_words` | `with_filler_words(config)` | Filler words while waiting for LLM |

## SAL (Selective Attention Locking)

SAL helps the agent focus on the primary speaker and suppress background noise. Enable it via `advanced_features` and configure with `with_sal`:

```python
from agora_agent import Agora, Area
from agora_agent.agentkit import Agent, AdvancedFeatures, SalConfig, SalModeValues
from agora_agent.agentkit.vendors import OpenAI, ElevenLabsTTS, DeepgramSTT

agent = (
    Agent(
        name='sal-assistant',
        instructions='You are a helpful assistant.',
        advanced_features=AdvancedFeatures(enable_sal=True),
    )
    .with_sal(SalConfig(
        sal_mode=SalModeValues.LOCKING,
        sample_urls={'primary-speaker': 'https://example.com/voiceprint.pcm'},
    ))
    .with_llm(OpenAI(api_key='your-key', model='gpt-4o-mini'))
    .with_tts(ElevenLabsTTS(key='your-key', model_id='eleven_flash_v2_5', voice_id='your-voice-id', sample_rate=24000))
    .with_stt(DeepgramSTT(api_key='your-key', model='nova-2', language='en-US'))
)
```

Use `SalModeValues.LOCKING` or `SalModeValues.RECOGNITION` for type safety.

## Advanced Features

Enable MLLM, RTM, SAL, or tools:

```python
from agora_agent.agentkit import Agent, AdvancedFeatures
from agora_agent.agentkit.vendors import OpenAIRealtime

# MLLM mode (see mllm-flow guide)
agent = Agent().with_mllm(OpenAIRealtime(api_key='...'))

# RTM signaling for custom data delivery
agent = Agent(advanced_features=AdvancedFeatures(enable_rtm=True))

# Enable tool invocation via MCP
agent = Agent().with_tools()
```

## Session Parameters

Configure silence handling, farewell behavior, and data channel:

```python
from agora_agent.agentkit import (
    Agent,
    SessionParams,
    SilenceConfig,
    FarewellConfig,
    SilenceActionValues,
    DataChannel,
)

agent = (
    Agent(name='params-agent')
    .with_parameters(SessionParams(
        silence_config=SilenceConfig(
            timeout_ms=10000,
            action=SilenceActionValues.SPEAK,
            content="I'm still here. Take your time.",
        ),
        farewell_config=FarewellConfig(
            graceful_enabled=True,
            graceful_timeout_seconds=10,
        ),
        data_channel=DataChannel.RTM,  # or DataChannel.DATASTREAM
    ))
    .with_llm(OpenAI(api_key='...', model='gpt-4o-mini'))
    .with_tts(ElevenLabsTTS(key='...', model_id='...', voice_id='...', sample_rate=24000))
    .with_stt(DeepgramSTT(api_key='...', model='nova-2'))
)
```

## Failure Message and Max History

```python
agent = (
    Agent(
        name='assistant',
        failure_message='Sorry, I encountered an error. Please try again.',
        max_history=20,
    )
    .with_llm(OpenAI(api_key='...', model='gpt-4o-mini'))
    .with_tts(ElevenLabsTTS(key='...', model_id='...', voice_id='...', sample_rate=24000))
    .with_stt(DeepgramSTT(api_key='...', model='nova-2'))
)

# Or via builder methods
agent = (
    Agent()
    .with_failure_message('Something went wrong.')
    .with_max_history(15)
    .with_llm(OpenAI(api_key='...', model='gpt-4o-mini'))
    .with_tts(ElevenLabsTTS(key='...', model_id='...', voice_id='...', sample_rate=24000))
    .with_stt(DeepgramSTT(api_key='...', model='nova-2'))
)
```

## Geofence

Restrict which geographic regions the backend can use:

```python
from agora_agent.agentkit import Agent, GeofenceConfig, GeofenceArea, GeofenceExcludeArea

agent = (
    Agent()
    .with_geofence(GeofenceConfig(area=GeofenceArea.NORTH_AMERICA))
    .with_llm(OpenAI(api_key='...', model='gpt-4o-mini'))
    .with_tts(ElevenLabsTTS(key='...', model_id='...', voice_id='...', sample_rate=24000))
    .with_stt(DeepgramSTT(api_key='...', model='nova-2'))
)

# Global with exclusion
agent = (
    Agent()
    .with_geofence(GeofenceConfig(area=GeofenceArea.GLOBAL, exclude_area=GeofenceExcludeArea.EUROPE))
    .with_llm(OpenAI(api_key='...', model='gpt-4o-mini'))
    .with_tts(ElevenLabsTTS(key='...', model_id='...', voice_id='...', sample_rate=24000))
    .with_stt(DeepgramSTT(api_key='...', model='nova-2'))
)
```

Use `GeofenceArea` and `GeofenceExcludeArea` for type-safe region values.

## Labels

Attach custom labels returned in notification callbacks:

```python
agent = (
    Agent()
    .with_labels({
        'environment': 'production',
        'team': 'support',
        'version': '1.2.0',
    })
    .with_llm(OpenAI(api_key='...', model='gpt-4o-mini'))
    .with_tts(ElevenLabsTTS(key='...', model_id='...', voice_id='...', sample_rate=24000))
    .with_stt(DeepgramSTT(api_key='...', model='nova-2'))
)
```

## RTC Encryption

Configure RTC media encryption:

```python
from agora_agent.agentkit import Agent, RtcConfig

agent = (
    Agent()
    .with_rtc(RtcConfig(
        encryption_key='your-32-byte-key',
        encryption_mode=5,  # AES_128_GCM
    ))
    .with_llm(OpenAI(api_key='...', model='gpt-4o-mini'))
    .with_tts(ElevenLabsTTS(key='...', model_id='...', voice_id='...', sample_rate=24000))
    .with_stt(DeepgramSTT(api_key='...', model='nova-2'))
)
```

## Filler Words

Play filler words while waiting for the LLM response:

```python
from agora_agent.agentkit import (
    Agent,
    FillerWordsConfig,
    FillerWordsTrigger,
    FillerWordsTriggerFixedTimeConfig,
    FillerWordsContent,
    FillerWordsContentStaticConfig,
    FillerWordsSelectionRule,
)

agent = (
    Agent()
    .with_filler_words(FillerWordsConfig(
        enable=True,
        trigger=FillerWordsTrigger(
            mode='fixed_time',
            fixed_time_config=FillerWordsTriggerFixedTimeConfig(response_wait_ms=2000),
        ),
        content=FillerWordsContent(
            mode='static',
            static_config=FillerWordsContentStaticConfig(
                phrases=['Let me think...', 'One moment...', 'Hmm...'],
                selection_rule=FillerWordsSelectionRule.SHUFFLE,
            ),
        ),
    ))
    .with_llm(OpenAI(api_key='...', model='gpt-4o-mini'))
    .with_tts(ElevenLabsTTS(key='...', model_id='...', voice_id='...', sample_rate=24000))
    .with_stt(DeepgramSTT(api_key='...', model='nova-2'))
)
```

## Properties (Getters)

Read back configuration via properties:

```python
from agora_agent.agentkit import Agent, GeofenceConfig, GeofenceArea

agent = (
    Agent(max_history=20)
    .with_geofence(GeofenceConfig(area=GeofenceArea.EUROPE))
    .with_labels({'env': 'staging'})
)

agent.name           # str | None
agent.max_history    # 20
agent.geofence       # GeofenceConfig(area='EUROPE')
agent.labels         # {'env': 'staging'}
agent.sal            # SalConfig | None
agent.advanced_features
agent.parameters
agent.failure_message
agent.rtc
agent.filler_words
agent.config         # Full read-only snapshot
```

## Chaining All Features

```python
from agora_agent import Agora, Area
from agora_agent.agentkit import (
    Agent,
    AdvancedFeatures,
    SessionParams,
    SilenceConfig,
    FarewellConfig,
    GeofenceConfig,
    GeofenceArea,
    FillerWordsConfig,
    FillerWordsTrigger,
    FillerWordsTriggerFixedTimeConfig,
    FillerWordsContent,
    FillerWordsContentStaticConfig,
    SilenceActionValues,
    DataChannel,
    FillerWordsSelectionRule,
)
from agora_agent.agentkit.vendors import OpenAI, ElevenLabsTTS, DeepgramSTT

client = Agora(
    area=Area.US,
    app_id='your-app-id',
    app_certificate='your-app-certificate',
)

agent = (
    Agent(
        name='full-featured-assistant',
        instructions='You are a helpful voice assistant.',
        greeting='Hello! How can I help?',
        failure_message='Sorry, I had trouble processing that.',
        max_history=20,
    )
    .with_llm(OpenAI(api_key='your-key', model='gpt-4o-mini'))
    .with_tts(ElevenLabsTTS(key='your-key', model_id='eleven_flash_v2_5', voice_id='your-voice-id', sample_rate=24000))
    .with_stt(DeepgramSTT(api_key='your-key', model='nova-2', language='en-US'))
    .with_advanced_features(AdvancedFeatures(enable_rtm=True))
    .with_parameters(SessionParams(
        silence_config=SilenceConfig(
            timeout_ms=8000,
            action=SilenceActionValues.SPEAK,
            content="I'm listening.",
        ),
        farewell_config=FarewellConfig(
            graceful_enabled=True,
            graceful_timeout_seconds=5,
        ),
    ))
    .with_geofence(GeofenceConfig(area=GeofenceArea.NORTH_AMERICA))
    .with_labels({'app': 'voice-assistant', 'version': '2.0'})
    .with_filler_words(FillerWordsConfig(
        enable=True,
        trigger=FillerWordsTrigger(
            mode='fixed_time',
            fixed_time_config=FillerWordsTriggerFixedTimeConfig(response_wait_ms=1500),
        ),
        content=FillerWordsContent(
            mode='static',
            static_config=FillerWordsContentStaticConfig(
                phrases=['Let me think...', 'One moment please.'],
                selection_rule=FillerWordsSelectionRule.SHUFFLE,
            ),
        ),
    ))
)

session = agent.create_session(
    client,
    channel='demo-room',
    agent_uid='1',
    remote_uids=['100'],
    idle_timeout=120,
)

agent_id = session.start()
```

## Next steps

- [Agent Reference](../reference/agent.md) — full API signatures
- [Cascading Flow](./cascading-flow.md) — ASR → LLM → TTS setup
- [MLLM Flow](./mllm-flow.md) — multimodal flow with `mllm.enable`
- [Regional Routing](./regional-routing.md) — client area and geofence
