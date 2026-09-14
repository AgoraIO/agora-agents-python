# GPT Live v3 preview

This preview targets `gpt-live-1` on `/v1/live/sessions`. Use an alpha-enabled OpenAI key. Do not use this alpha for production traffic.

<!-- snippet: fragment -->
```python
from agora_agent import Agent, OpenAIGPTLive

agent = Agent(client=client).with_mllm(OpenAIGPTLive(
    api_key=openai_key,
    voice="cedar",
    tool_enabled=True,
    prompt="You are a helpful assistant. Keep responses concise.",
    greeting="Hello! I'm GPT Live. How can I help you today?",
    output_idle_end_ms=600,
    input_idle_end_ms=1500,
    mcp_servers=[{"name": "lookup", "endpoint": "https://tools.example/mcp"}],
))
agent = agent.with_tools()
```

Set MCP servers on `OpenAIGPTLive`; they serialize as `mllm.mcp_servers`. Enable `advanced_features.enable_tools` with the existing tools builder. To advertise graph tools to GPT Live, also set `tool_enabled` to true.

## Request placement

GPT Live places MCP at `properties.mllm.mcp_servers`, the tool gate at `properties.advanced_features.enable_tools`, and silence settings at `properties.parameters.silence_config`. MCP and MAIN settings are outside `properties.mllm.params`.

```json
{
  "properties": {
    "mllm": {
      "enable": true,
      "vendor": "openai_gpt_live",
      "api_key": "<alpha-enabled-key>",
      "url": "wss://api.openai.com/v1/live/sessions",
      "greeting_message": "Hello! I'm GPT Live. How can I help you today?",
      "params": {
        "model": "gpt-live-1",
        "voice": "cedar",
        "prompt": "You are a helpful assistant.",
        "tool_enabled": true
      },
      "mcp_servers": [{
        "name": "lookup",
        "endpoint": "https://tools.example/mcp",
        "transport": "streamable_http"
      }]
    },
    "advanced_features": {"enable_tools": true}
  }
}
```

This fragment omits the normal name, channel, token and UID fields populated by the SDK session. The preview route and `agora-feature: live-models` gate are selected automatically from the vendor.

The SDK omits `alpha_selector` by default. Set it only when a future preview contract requires an `OpenAI-Alpha` selector.

## Silence and backend rollout

Keep silence settings in the existing agent parameters builder, never in vendor params. The public API spelling is `silence_config`, with `{timeout_ms, action, content}`. The supplied extension contract describes internal `parameters.main.silence` and supports `action: "think"`; the public documentation currently says `silence_config` does not apply to MLLM. Serialization is covered by tests, but the public documentation does not establish that the preview allocator maps it to GPT Live's internal MAIN setting. Confirm that backend mapping before relying on silence nudges. The SDK does not invent a new public `main` field.

## Preview-only options

The supplied backend contract marks custom voice objects, `responses_params`, and first-class context management as pending PR #1522. The SDK does not expose typed options for those fields. Use raw params only once your target backend supports that PR. Until then, context management is reachable via `session_params.context_management`.

`session_params` cannot override `model`, `delegation`, `audio`, `instructions`, or `input`; put modelled values in their dedicated options instead. Unknown session fields may still be rejected by the alpha API. Delegation and voice are fixed for a session: apply changes when creating a new session. See the [vendor reference](../reference/vendors.md) for every option and provider default.
