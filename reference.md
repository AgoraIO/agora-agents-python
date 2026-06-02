# Reference
## Agents
<details><summary><code>client.agents.<a href="src/agora_agent/agents/client.py">start</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create and start a Conversational AI agent instance.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from agora_agent import (
    Agora,
    Asr_Ares,
    Llm,
    LlmParams,
    MicrosoftTtsParams,
    Tts_Microsoft,
)
from agora_agent.agents import (
    StartAgentsRequestProperties,
    StartAgentsRequestPropertiesTurnDetection,
    StartAgentsRequestPropertiesTurnDetectionConfig,
    StartAgentsRequestPropertiesTurnDetectionConfigEndOfSpeech,
)

client = Agora(
    authorization="YOUR_AUTHORIZATION",
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD",
)
client.agents.start(
    appid="appid",
    name="unique_name",
    properties=StartAgentsRequestProperties(
        channel="channel_name",
        token="token",
        agent_rtc_uid="1001",
        remote_rtc_uids=["1002"],
        idle_timeout=120,
        asr=Asr_Ares(),
        tts=Tts_Microsoft(
            params=MicrosoftTtsParams(
                key="key",
                region="region",
                voice_name="voice_name",
            ),
        ),
        llm=Llm(
            url="https://api.openai.com/v1/chat/completions",
            api_key="<your_llm_key>",
            system_messages=[
                {"role": "system", "content": "You are a helpful chatbot."}
            ],
            params=LlmParams(
                model="gpt-4o-mini",
            ),
            max_history=32,
            greeting_message="Hello, how can I assist you today?",
            failure_message="Please hold on a second.",
        ),
        turn_detection=StartAgentsRequestPropertiesTurnDetection(
            config=StartAgentsRequestPropertiesTurnDetectionConfig(
                end_of_speech=StartAgentsRequestPropertiesTurnDetectionConfigEndOfSpeech(
                    mode="semantic",
                ),
            ),
        ),
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**appid:** `str` — The App ID of the project.
    
</dd>
</dl>

<dl>
<dd>

**name:** `str` — The unique identifier of the agent. The same identifier cannot be used repeatedly.
    
</dd>
</dl>

<dl>
<dd>

**properties:** `StartAgentsRequestProperties` — Configuration details of the agent.
    
</dd>
</dl>

<dl>
<dd>

**preset:** `typing.Optional[str]` 

A comma-separated string of one or more presets. Each preset provides a predefined configuration for ASR, LLM, and TTS. You can specify a preset for any or all of ASR, LLM, and TTS. When a preset is specified, you do not need to provide the endpoint URL, API key, or model for the preset providers. Use the `asr`, `llm`, and `tts` fields to configure additional settings.

Available presets:
- ASR: `deepgram_nova_2`, `deepgram_nova_3`
- LLM: `openai_gpt_4o_mini`, `openai_gpt_4_1_mini`, `openai_gpt_5_nano`, `openai_gpt_5_mini`
- TTS: `minimax_speech_2_6_turbo`, `minimax_speech_2_8_turbo`, `openai_tts_1`
    
</dd>
</dl>

<dl>
<dd>

**pipeline_id:** `typing.Optional[str]` — The unique ID of a published agent in AI Studio. When provided, the saved agent configuration is used as the base configuration. Any fields specified in `properties` override the corresponding agent settings. When you specify a `pipeline_id`, the `asr`, `tts`, and `llm` fields in `properties` are optional.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.agents.<a href="src/agora_agent/agents/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve a list of agents that meet the specified conditions.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from agora_agent import Agora

client = Agora(
    authorization="YOUR_AUTHORIZATION",
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD",
)
response = client.agents.list(
    appid="appid",
)
for item in response:
    yield item
# alternatively, you can paginate page-by-page
for page in response.iter_pages():
    yield page

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**appid:** `str` — The App ID of the project.
    
</dd>
</dl>

<dl>
<dd>

**channel:** `typing.Optional[str]` — The channel to query for a list of agents.
    
</dd>
</dl>

<dl>
<dd>

**from_time:** `typing.Optional[float]` — The start timestamp (in seconds) for the query. Default is 2 hours ago.
    
</dd>
</dl>

<dl>
<dd>

**to_time:** `typing.Optional[float]` — The end timestamp (in seconds) for the query. Default is current time.
    
</dd>
</dl>

<dl>
<dd>

**state:** `typing.Optional[ListAgentsRequestState]` 

The agent state to filter by. Only one state can be specified per query:
- `IDLE` (0): Agent is idle.
- `STARTING` (1): The agent is being started.
- `RUNNING` (2): The agent is running.
- `STOPPING` (3): The agent is stopping.
- `STOPPED` (4): The agent has exited.
- `FAILED` (6): The agent failed to execute.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — The maximum number of entries returned per page.
    
</dd>
</dl>

<dl>
<dd>

**cursor:** `typing.Optional[str]` — The paging cursor, indicating the starting position (`agent_id`) of the next page of results.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.agents.<a href="src/agora_agent/agents/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get the current state information of the specified agent instance.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from agora_agent import Agora

client = Agora(
    authorization="YOUR_AUTHORIZATION",
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD",
)
client.agents.get(
    appid="appid",
    agent_id="agentId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**appid:** `str` — The App ID of the project.
    
</dd>
</dl>

<dl>
<dd>

**agent_id:** `str` — The agent instance ID you obtained after successfully calling `join` to start a conversational AI agent.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.agents.<a href="src/agora_agent/agents/client.py">get_history</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get the history of the conversation between the user and the agent.

Call this endpoint while the agent is running to retrieve the conversation history. You can set the maximum number of cached entries using the `llm.max_history` parameter when calling the start agent endpoint. The default value is `32`.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from agora_agent import Agora

client = Agora(
    authorization="YOUR_AUTHORIZATION",
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD",
)
client.agents.get_history(
    appid="appid",
    agent_id="agentId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**appid:** `str` — The App ID of the project.
    
</dd>
</dl>

<dl>
<dd>

**agent_id:** `str` — The agent instance ID you obtained after successfully calling `join` to start a conversational AI agent.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.agents.<a href="src/agora_agent/agents/client.py">get_turns</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Query conversation turn information for a conversational AI agent session.

After a conversation with the agent ends, use this endpoint to query the conversation turn information, including the start information, end information, and performance metrics of each conversation turn.

You can query sessions within the last 7 days.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from agora_agent import Agora

client = Agora(
    authorization="YOUR_AUTHORIZATION",
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD",
)
client.agents.get_turns(
    appid="appid",
    agent_id="agentId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**appid:** `str` — The App ID of the project.
    
</dd>
</dl>

<dl>
<dd>

**agent_id:** `str` — The agent instance ID you obtained after successfully calling `join` to start a conversational AI agent.
    
</dd>
</dl>

<dl>
<dd>

**page_index:** `typing.Optional[int]` — The page number. Starts from 1.
    
</dd>
</dl>

<dl>
<dd>

**page_size:** `typing.Optional[int]` — The number of dialogue turns returned per page.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.agents.<a href="src/agora_agent/agents/client.py">stop</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Stop the specified conversational agent instance. The API responds after request parameters are validated, and the stop operation is processed asynchronously after the response is returned.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from agora_agent import Agora

client = Agora(
    authorization="YOUR_AUTHORIZATION",
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD",
)
client.agents.stop(
    appid="appid",
    agent_id="agentId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**appid:** `str` — The App ID of the project.
    
</dd>
</dl>

<dl>
<dd>

**agent_id:** `str` — The agent instance ID you obtained after successfully calling `join` to start a conversational AI agent.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.agents.<a href="src/agora_agent/agents/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Adjust Conversation AI Engine parameters at runtime.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from agora_agent import Agora
from agora_agent.agents import (
    UpdateAgentsRequestProperties,
    UpdateAgentsRequestPropertiesLlm,
)

client = Agora(
    authorization="YOUR_AUTHORIZATION",
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD",
)
client.agents.update(
    appid="appid",
    agent_id="agentId",
    properties=UpdateAgentsRequestProperties(
        token="007eJxTYxxxxxxxxxxIaHMLAAAA0ex66",
        llm=UpdateAgentsRequestPropertiesLlm(
            system_messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. xxx",
                },
                {
                    "role": "system",
                    "content": "Previously, user has talked about their favorite hobbies with some key topics: xxx",
                },
            ],
            params={"model": "abab6.5s-chat", "max_token": 1024},
        ),
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**appid:** `str` — The App ID of the project.
    
</dd>
</dl>

<dl>
<dd>

**agent_id:** `str` — The agent instance ID you obtained after successfully calling `join` to start a conversational AI agent.
    
</dd>
</dl>

<dl>
<dd>

**properties:** `typing.Optional[UpdateAgentsRequestProperties]` — Configuration properties to update.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.agents.<a href="src/agora_agent/agents/client.py">speak</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Broadcast a custom message using the TTS module.

During a conversation with an agent, call this endpoint to immediately broadcast a custom message using the TTS module. Upon receiving the request, the system interrupts the agent's speech and thought process to deliver the message. This broadcast can be interrupted by human voice.

Note: The speak API is not supported when using `mllm` configuration.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from agora_agent import Agora

client = Agora(
    authorization="YOUR_AUTHORIZATION",
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD",
)
client.agents.speak(
    appid="appid",
    agent_id="agentId",
    text="Sorry, the conversation content is not compliant.",
    priority="INTERRUPT",
    interruptable=False,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**appid:** `str` — The App ID of the project.
    
</dd>
</dl>

<dl>
<dd>

**agent_id:** `str` — The agent instance ID you obtained after successfully calling `join` to start a conversational AI agent.
    
</dd>
</dl>

<dl>
<dd>

**text:** `str` — The broadcast message text. The maximum length of the text content is 512 bytes.
    
</dd>
</dl>

<dl>
<dd>

**priority:** `typing.Optional[SpeakAgentsRequestPriority]` 

Sets the priority of the message broadcast:
- `INTERRUPT`: High priority. The agent immediately interrupts the current interaction to announce the message.
- `APPEND`: Medium priority. The agent announces the message after the current interaction ends.
- `IGNORE`: Low priority. If the agent is busy interacting, it ignores and discards the broadcast; the message is only announced if the agent is not interacting.
    
</dd>
</dl>

<dl>
<dd>

**interruptable:** `typing.Optional[bool]` 

Whether to allow users to interrupt the agent's broadcast by speaking:
- `true`: Allow
- `false`: Don't allow
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.agents.<a href="src/agora_agent/agents/client.py">interrupt</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Interrupt the specified agent while speaking or thinking.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from agora_agent import Agora

client = Agora(
    authorization="YOUR_AUTHORIZATION",
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD",
)
client.agents.interrupt(
    appid="appid",
    agent_id="agentId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**appid:** `str` — The App ID of the project.
    
</dd>
</dl>

<dl>
<dd>

**agent_id:** `str` — The agent instance ID you obtained after successfully calling `join` to start a conversational AI agent.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Agent Management
<details><summary><code>client.agent_management.<a href="src/agora_agent/agent_management/client.py">agent_think</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Send a custom text instruction to the specified conversational AI agent instance.

The instruction is injected into the current conversation pipeline as user input, and the agent processes and responds to it following the standard user input logic.

Use this endpoint for the following scenarios:
- **Implicit instruction injection**: Inject hidden context or directives into the conversation.
- **Client-side event triggering**: Notify the agent of client-side events, such as a user clicking a button.
- **Voice and text collaboration**: Combine text instructions with voice input for richer interaction.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from agora_agent import Agora

client = Agora(
    authorization="YOUR_AUTHORIZATION",
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD",
)
client.agent_management.agent_think(
    appid="appid",
    agent_id="agentId",
    text="The user just clicked the purchase button.",
    on_listening_action="inject",
    on_thinking_action="interrupt",
    on_speaking_action="ignore",
    interruptable=True,
    metadata={"publisher": "user123", "model": "deepseek-r1"},
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**appid:** `str` — The App ID of the project.
    
</dd>
</dl>

<dl>
<dd>

**agent_id:** `str` — The agent instance ID you obtained after successfully calling `join` to start a conversational AI agent.
    
</dd>
</dl>

<dl>
<dd>

**text:** `str` — The custom instruction text to inject into the current conversation pipeline. The system processes this as user input.
    
</dd>
</dl>

<dl>
<dd>

**on_listening_action:** `typing.Optional[AgentThinkAgentManagementRequestOnListeningAction]` 

The action to take when the agent is in a listening state:
- `inject`: Inject the custom text instruction into the current turn without interrupting it.
- `interrupt`: Immediately interrupt the current flow and initiate a new round of dialogue.
- `ignore`: Ignore the request.
    
</dd>
</dl>

<dl>
<dd>

**on_thinking_action:** `typing.Optional[AgentThinkAgentManagementRequestOnThinkingAction]` 

The action to take when the agent is in a thinking state:
- `interrupt`: Interrupt the current state and start a new conversation turn.
- `ignore`: Ignore the request.
    
</dd>
</dl>

<dl>
<dd>

**on_speaking_action:** `typing.Optional[AgentThinkAgentManagementRequestOnSpeakingAction]` 

The action to take when the agent is in a speaking state:
- `interrupt`: Interrupt the current state and start a new conversation turn.
- `ignore`: Ignore the request.
    
</dd>
</dl>

<dl>
<dd>

**interruptable:** `typing.Optional[bool]` 

Whether user speech can interrupt the injected instruction:
- `true`: User speech can interrupt the instruction.
- `false`: User speech cannot interrupt the instruction.
    
</dd>
</dl>

<dl>
<dd>

**metadata:** `typing.Optional[typing.Dict[str, str]]` — Custom metadata in key-value pair format. Use this field to pass additional business information such as identifiers or model references.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Telephony
<details><summary><code>client.telephony.<a href="src/agora_agent/telephony/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Query historical call records for a specified appid based on the filter criteria.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from agora_agent import Agora

client = Agora(
    authorization="YOUR_AUTHORIZATION",
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD",
)
response = client.telephony.list(
    appid="appid",
)
for item in response:
    yield item
# alternatively, you can paginate page-by-page
for page in response.iter_pages():
    yield page

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**appid:** `str` — The App ID of the project.
    
</dd>
</dl>

<dl>
<dd>

**number:** `typing.Optional[str]` — Filter by phone number. Can be either the calling number or the called number.
    
</dd>
</dl>

<dl>
<dd>

**from_time:** `typing.Optional[int]` — Query list start timestamp (in seconds). Default is 60 days ago.
    
</dd>
</dl>

<dl>
<dd>

**to_time:** `typing.Optional[int]` — Query list end timestamp (in seconds). Default is current time.
    
</dd>
</dl>

<dl>
<dd>

**type:** `typing.Optional[ListTelephonyRequestType]` 

Call type filter:
- `inbound`: Inbound call.
- `outbound`: Outbound call.

If not specified, all call types are returned.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Maximum number of items returned in a single page.
    
</dd>
</dl>

<dl>
<dd>

**cursor:** `typing.Optional[str]` — Pagination cursor. Use the `agent_id` from the previous page as the cursor for the next page.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.telephony.<a href="src/agora_agent/telephony/client.py">call</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Initiate an outbound call to a specified number and create an agent to join the specified RTC channel.

Use this endpoint to initiate an outbound call to the specified number and create an agent that joins the target RTC channel. The agent waits for the callee to answer.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from agora_agent import Agora
from agora_agent.telephony import (
    CallTelephonyRequestProperties,
    CallTelephonyRequestSip,
)

client = Agora(
    authorization="YOUR_AUTHORIZATION",
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD",
)
client.telephony.call(
    appid="appid",
    name="customer_service",
    sip=CallTelephonyRequestSip(
        to_number="+19876543210",
        from_number="+11234567890",
        rtc_uid="100",
        rtc_token="<agora_sip_rtc_token>",
    ),
    properties=CallTelephonyRequestProperties(
        channel="<agora_channel>",
        token="<agora_channel_token>",
        agent_rtc_uid="111",
        remote_rtc_uids=["100"],
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**appid:** `str` — The App ID of the project.
    
</dd>
</dl>

<dl>
<dd>

**name:** `str` — The name identifier of the call session.
    
</dd>
</dl>

<dl>
<dd>

**sip:** `CallTelephonyRequestSip` — SIP (Session Initiation Protocol) call configuration object.
    
</dd>
</dl>

<dl>
<dd>

**properties:** `CallTelephonyRequestProperties` 

Call attribute configuration. The content of this field varies depending on the invocation method:
- **Using pipeline ID**: Simply pass in `channel`, `token`, `agent_rtc_uid`, and `remote_rtc_uids`.
- **Using complete configuration**: Pass in the complete parameters of the [Start a conversational AI agent](https://docs.agora.io/en/conversational-ai/rest-api/agent/join) `properties`, including all required fields such as `channel`, `token`, `agent_rtc_uid`, `remote_rtc_uids`, `tts`, and `llm`.
    
</dd>
</dl>

<dl>
<dd>

**pipeline_id:** `typing.Optional[str]` — The unique ID of a published project in AI Studio.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.telephony.<a href="src/agora_agent/telephony/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve the call status and related information of a specified agent.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from agora_agent import Agora

client = Agora(
    authorization="YOUR_AUTHORIZATION",
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD",
)
client.telephony.get(
    appid="appid",
    agent_id="agent_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**appid:** `str` — The App ID of the project.
    
</dd>
</dl>

<dl>
<dd>

**agent_id:** `str` — The agent ID you obtained after successfully calling the API to initiate an outbound call.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.telephony.<a href="src/agora_agent/telephony/client.py">hangup</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Instruct the agent to proactively hang up the ongoing call and leave the RTC channel.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from agora_agent import Agora

client = Agora(
    authorization="YOUR_AUTHORIZATION",
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD",
)
client.telephony.hangup(
    appid="appid",
    agent_id="agent_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**appid:** `str` — The App ID of the project.
    
</dd>
</dl>

<dl>
<dd>

**agent_id:** `str` — The agent ID you obtained after successfully calling the API to initiate an outbound call.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## PhoneNumbers
<details><summary><code>client.phone_numbers.<a href="src/agora_agent/phone_numbers/client.py">list</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve a list of all imported phone numbers under the current account.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from agora_agent import Agora

client = Agora(
    authorization="YOUR_AUTHORIZATION",
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD",
)
client.phone_numbers.list()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.phone_numbers.<a href="src/agora_agent/phone_numbers/client.py">add</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Import a pre-configured phone number that can be used for inbound or outbound calls.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from agora_agent import Agora
from agora_agent.phone_numbers import (
    AddPhoneNumbersRequestInboundConfig,
    AddPhoneNumbersRequestOutboundConfig,
)

client = Agora(
    authorization="YOUR_AUTHORIZATION",
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD",
)
client.phone_numbers.add(
    provider="byo",
    phone_number="+19876543210",
    label="Sales Hotline",
    inbound=True,
    outbound=True,
    inbound_config=AddPhoneNumbersRequestInboundConfig(
        allowed_addresses=["112.126.15.64/27"],
    ),
    outbound_config=AddPhoneNumbersRequestOutboundConfig(
        address="xxx:xxx@sip.example.com",
        transport="tls",
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**provider:** `AddPhoneNumbersRequestProvider` 

Number provider:
- `byo`: BYO (Bring Your Own)
- `twilio`: Twilio
    
</dd>
</dl>

<dl>
<dd>

**phone_number:** `str` — Telephone number in E.164 format.
    
</dd>
</dl>

<dl>
<dd>

**label:** `str` — A label used to identify the number.
    
</dd>
</dl>

<dl>
<dd>

**inbound_config:** `AddPhoneNumbersRequestInboundConfig` — SIP inbound call configuration.
    
</dd>
</dl>

<dl>
<dd>

**outbound_config:** `AddPhoneNumbersRequestOutboundConfig` — SIP outbound call configuration.
    
</dd>
</dl>

<dl>
<dd>

**inbound:** `typing.Optional[bool]` — Whether the number supports inbound calls.
    
</dd>
</dl>

<dl>
<dd>

**outbound:** `typing.Optional[bool]` — Whether the number supports outbound calls.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.phone_numbers.<a href="src/agora_agent/phone_numbers/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve detailed information for a specific phone number.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from agora_agent import Agora

client = Agora(
    authorization="YOUR_AUTHORIZATION",
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD",
)
client.phone_numbers.get(
    phone_number="phone_number",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**phone_number:** `str` — Telephone number in E.164 format. For example, +11234567890.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.phone_numbers.<a href="src/agora_agent/phone_numbers/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Remove an imported phone number from the system.

After calling this endpoint, the number stops receiving calls routed through this system. To delete the number from the service provider, remove it in the service provider's console.
> This operation only removes the number configuration from the Agora system; the number stored with the phone service provider is not deleted.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from agora_agent import Agora

client = Agora(
    authorization="YOUR_AUTHORIZATION",
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD",
)
client.phone_numbers.delete(
    phone_number="phone_number",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**phone_number:** `str` — Telephone number in E.164 format. For example, +11234567890.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.phone_numbers.<a href="src/agora_agent/phone_numbers/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update the configuration for a phone number.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from agora_agent import Agora
from agora_agent.phone_numbers import (
    UpdatePhoneNumbersRequestInboundConfig,
    UpdatePhoneNumbersRequestOutboundConfig,
)

client = Agora(
    authorization="YOUR_AUTHORIZATION",
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD",
)
client.phone_numbers.update(
    phone_number="phone_number",
    inbound_config=UpdatePhoneNumbersRequestInboundConfig(
        pipeline_id="xxxxx",
    ),
    outbound_config=UpdatePhoneNumbersRequestOutboundConfig(
        pipeline_id="xxxxx",
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**phone_number:** `str` — Telephone number in E.164 format. For example, +11234567890.
    
</dd>
</dl>

<dl>
<dd>

**inbound_config:** `typing.Optional[UpdatePhoneNumbersRequestInboundConfig]` — Update inbound call configuration. Passing `null` will clear the configuration.
    
</dd>
</dl>

<dl>
<dd>

**outbound_config:** `typing.Optional[UpdatePhoneNumbersRequestOutboundConfig]` — Update outbound call configuration. Passing `null` will clear the configuration.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

