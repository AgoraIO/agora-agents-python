"""Generated wire types from root openapi.json; constraints live in the shared contract."""
from __future__ import annotations

from typing import Any, Dict, List, Union

from typing_extensions import Literal, Required, TypedDict


class AgentDeleteResponse(TypedDict, total=False):
    deleted: Required[Literal[True]]

class AgentListData(TypedDict, total=False):
    count: Required[int]
    list: Required[List[AgentListItem]]

class AgentListItem(TypedDict, total=False):
    agent_id: Required[str]
    agent_name: Required[str]
    create_ts: Required[int]
    update_ts: Required[int]

class AgentListResponse(TypedDict, total=False):
    data: Required[AgentListData]
    has_more: Required[bool]
    next_cursor: Required[Union[str, None]]

class AgentResponse(TypedDict, total=False):
    agent_id: Required[str]
    create_ts: Required[int]
    update_ts: Required[int]
    agent_name: Required[str]
    instructions: Union[str, None]
    messages: Union[List[Message], None]
    greeting: Union[Union[TextGreeting, AudioGreeting], None]
    variables: Union[Dict[str, VariableDefinition], None]
    pipeline: Union[ResolvedCascadedPipeline, None]
    filler_words: Union[FillerWords, None]

class AsrInput(TypedDict, total=False):
    credential: Union[Union[ManagedCredential, PublicByokCredential], None]
    vendor: Union[str, None]
    params: Union[JSONObject, None]
    url: Union[str, None]
    model: Union[str, None]
    language: Union[str, None]

class AudioGreeting(TypedDict, total=False):
    mode: Required[Literal['audio']]
    on: Literal['each_join', 'first_join']
    delay_ms: int
    url: Required[str]
    text: Required[str]
    download_timeout_ms: int
    pcm_sample_rate: int

class AvatarInput(TypedDict, total=False):
    credential: Union[Union[ManagedCredential, PublicByokCredential], None]
    vendor: Union[AvatarVendor, None]
    params: Union[JSONObject, None]
    enabled: Union[bool, None]

class CallPolicy(TypedDict, total=False):
    max_ring_duration_ms: Union[int, None]
    max_call_duration_seconds: Union[int, None]
    voicemail: Union[VoicemailPolicy, None]
    max_silence_duration_ms: Union[int, None]
    end_call: Union[SessionEndCallPolicy, None]
    transfer: Union[TransferPolicy, None]

class CallingDay(TypedDict, total=False):
    weekday: Required[Literal['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']]
    ranges: Required[List[TimeRange]]

class CampaignCallPolicy(TypedDict, total=False):
    max_ring_duration_ms: Union[int, None]
    max_call_duration_seconds: Union[int, None]
    voicemail: Union[CampaignVoicemailPolicy, None]
    max_silence_duration_ms: Union[int, None]
    end_call: Union[CampaignEndCallPolicy, None]
    transfer: Union[CampaignTransferPolicy, None]

class CampaignCounts(TypedDict, total=False):
    contacts: Required[int]
    pending: Required[int]
    calling: Required[int]
    completed: Required[int]
    failed: Required[int]
    canceled: Required[int]

class CampaignCreate(TypedDict, total=False):
    name: Required[str]
    agent_id: Required[str]
    transport: Required[CampaignTransport]
    contacts: Required[List[ContactInput]]
    lifecycle: CampaignLifecycle
    pacing: Pacing
    schedule: Required[Union[ImmediateSchedule, ScheduledSchedule]]
    data_policy: DataPolicy

class CampaignDeleteResponse(TypedDict, total=False):
    deleted: Literal[True]

class CampaignEndCallPolicy(TypedDict, total=False):
    on_conversation_complete: bool
    on_user_request: bool
    on_fax: bool
    on_ai_assistant: bool
    on_voicemail: bool

class CampaignFailure(TypedDict, total=False):
    code: Required[str]
    provider: Union[str, None]
    message: Required[str]
    ts: Required[int]

class CampaignLifecycle(TypedDict, total=False):
    idle_timeout_ms: int
    max_duration_ms: int
    graceful_stop: GracefulStop

class CampaignListData(TypedDict, total=False):
    count: Required[int]
    list: Required[List[CampaignResponse]]

class CampaignListResponse(TypedDict, total=False):
    data: Required[CampaignListData]
    has_more: Required[bool]
    next_cursor: Required[Union[str, None]]

class CampaignPatch(TypedDict, total=False):
    lifecycle: Union[CampaignLifecycle, None]
    pacing: Union[PacingPatch, None]
    schedule: Union[Union[ImmediateSchedule, ScheduledSchedule], None]
    transport: Union[CampaignTransportPatch, None]

class CampaignResponse(TypedDict, total=False):
    campaign_id: Required[str]
    name: Required[str]
    status: Required[Literal['scheduled', 'running', 'paused', 'completed', 'canceled', 'failed']]
    agent_id: Required[str]
    transport: Required[CampaignTransportResponse]
    lifecycle: Required[CampaignLifecycle]
    schedule: Required[Union[ImmediateSchedule, ScheduledSchedule]]
    counts: Required[CampaignCounts]
    create_ts: Required[int]
    start_ts: Required[Union[int, None]]
    complete_ts: Required[Union[int, None]]
    failure: Required[Union[CampaignFailure, None]]

class CampaignTransferPolicy(TypedDict, total=False):
    phone_number: Required[str]
    description: Required[str]

CampaignTransport = TypedDict('CampaignTransport', {'type': Required["Literal['telephony']"], 'from': Required['Union[str, List[str]]'], 'call_policy': 'Union[CampaignCallPolicy, None]'}, total=False)

class CampaignTransportPatch(TypedDict, total=False):
    call_policy: Union[CampaignCallPolicy, None]

CampaignTransportResponse = TypedDict('CampaignTransportResponse', {'type': Required["Literal['telephony']"], 'from': Required['List[str]'], 'call_policy': 'Union[CampaignCallPolicy, None]'}, total=False)

class CampaignVoicemailPolicy(TypedDict, total=False):
    mode: Required[Literal['continue', 'hangup']]

class CascadedPipelineInput(TypedDict, total=False):
    mode: Required[Literal['cascaded']]
    avatar: Union[AvatarInput, None]
    turn_detection: Union[TurnDetection, None]
    asr: Union[AsrInput, None]
    tts: Union[TtsInput, None]
    llm: Union[LlmInput, None]
    silence_config: Union[SilenceConfig, None]

class ContactInput(TypedDict, total=False):
    phone: Required[str]
    values: Dict[str, Union[str, int, float, bool]]

class DataPolicy(TypedDict, total=False):
    retention: Literal['30_days', 'none']

class DisabledInterruption(TypedDict, total=False):
    mode: Required[Literal['off']]
    when_off: Literal['append', 'ignore']

class ErrorResponse(TypedDict, total=False):
    detail: Required[str]
    reason: Required[ErrorReason]

class FillerTrigger(TypedDict, total=False):
    mode: Required[Literal['fixed_time']]
    response_wait_ms: Required[int]

class FillerWords(TypedDict, total=False):
    enable: Union[bool, None]
    trigger: Union[FillerTrigger, None]
    content: Union[Union[StaticFillerContent, GeneratedFillerContent], None]

class FunctionTool(TypedDict, total=False):
    type: Required[Literal['function']]
    name: Required[str]
    description: Required[str]
    parameters: Required[JSONObject]
    execution: Required[ToolExecution]
    server: Required[ToolServer]

class GeneratedFillerContent(TypedDict, total=False):
    mode: Required[Literal['generated']]
    instructions: Required[str]
    fallback_strategy: Union[Literal['static'], None]

class GracefulStop(TypedDict, total=False):
    enabled: bool
    timeout_ms: int

class ImmediateSchedule(TypedDict, total=False):
    mode: Required[Literal['immediate']]
    timezone: str
    days: List[CallingDay]

class InboundCallPolicy(TypedDict, total=False):
    max_call_duration_seconds: Union[int, None]
    max_silence_duration_ms: Union[int, None]
    end_call: Union[InboundEndCallPolicy, None]
    transfer: Union[TransferPolicy, None]

class InboundInput(TypedDict, total=False):
    agent: Required[Union[str, None]]
    call_policy: Union[InboundCallPolicy, None]

class InboundOutput(TypedDict, total=False):
    agent: Required[Union[str, None]]
    call_policy: Union[InboundCallPolicy, None]

class KeywordInterruption(TypedDict, total=False):
    mode: Required[Literal['keywords']]
    keywords: Required[List[str]]

class Lifecycle(TypedDict, total=False):
    idle_timeout_ms: int
    max_duration_ms: int
    graceful_stop: Union[GracefulStop, None]

class LlmInput(TypedDict, total=False):
    mcp_servers: Union[List[McpServer], None]
    tools: Union[List[FunctionTool], None]
    credential: Union[Union[ManagedCredential, PublicByokCredential], None]
    vendor: Union[str, None]
    params: Union[JSONObject, None]
    url: Union[str, None]
    style: Union[str, None]
    model: Union[str, None]
    headers: Union[Dict[str, str], None]
    input_modalities: Union[List[str], None]
    output_modalities: Union[List[str], None]
    max_history: Union[int, None]
    failure_message: Union[str, None]

class ManagedCredential(TypedDict, total=False):
    mode: Required[Literal['managed']]

class ManualTurnBoundary(TypedDict, total=False):
    type: Required[Literal['manual']]

class McpServer(TypedDict, total=False):
    name: Required[str]
    endpoint: Required[str]
    transport: Required[Literal['streamable_http']]
    headers: Union[Dict[str, str], None]
    allowed_tools: Union[List[str], None]
    timeout_ms: Union[int, None]

class Message(TypedDict, total=False):
    role: Required[Literal['system', 'user', 'assistant']]
    content: Required[str]

class NumberCreate(TypedDict, total=False):
    number: Required[str]
    description: Union[str, None]
    sip_trunk: Required[SipTrunkInput]
    inbound: Union[InboundInput, None]

class NumberDeleteResponse(TypedDict, total=False):
    deleted: Literal[True]

class NumberListData(TypedDict, total=False):
    count: Required[int]
    list: Required[List[NumberResponse]]

class NumberListResponse(TypedDict, total=False):
    data: Required[NumberListData]
    has_more: Required[bool]
    next_cursor: Required[Union[str, None]]

class NumberPatch(TypedDict, total=False):
    number: Union[str, None]
    description: Union[str, None]
    sip_trunk: Union[SipTrunkInput, None]
    inbound: Union[InboundInput, None]

class NumberResponse(TypedDict, total=False):
    number_id: Required[str]
    number: Required[str]
    description: Union[str, None]
    sip_trunk: Union[SipTrunkOutput, None]
    inbound: Union[InboundOutput, None]
    create_ts: Required[int]

class Pacing(TypedDict, total=False):
    max_concurrent: int
    max_calls_per_second: Union[int, None]

class PacingPatch(TypedDict, total=False):
    max_concurrent: Union[int, None]
    max_calls_per_second: Union[int, None]

class PublicAgentInput(TypedDict, total=False):
    instructions: Union[str, None]
    messages: Union[List[Message], None]
    greeting: Union[Union[TextGreeting, AudioGreeting], None]
    variables: Union[Dict[str, VariableDefinition], None]
    pipeline: Union[CascadedPipelineInput, None]
    filler_words: Union[FillerWords, None]

class PublicByokCredential(TypedDict, total=False):
    mode: Required[Literal['byok']]
    fields: Required[Dict[str, str]]

class PublicEphemeralSessionCreate(TypedDict, total=False):
    agent: Required[PublicAgentInput]
    values: Union[Dict[str, Union[str, int, float, bool]], None]
    labels: Union[Dict[str, str], None]
    transport: Required[Union[RtcTransport, TelephonyTransport]]
    lifecycle: Union[Lifecycle, None]
    data_policy: Union[DataPolicy, None]

class ResolvedAsr(TypedDict, total=False):
    credential: Union[ResolvedCredential, None]
    url: Union[str, None]
    vendor: Union[str, None]
    model: Union[str, None]
    language: Union[str, None]
    params: Union[Dict[str, JsonValue], None]

class ResolvedAvatar(TypedDict, total=False):
    enabled: Union[bool, None]
    credential: Union[ResolvedCredential, None]
    vendor: Union[str, None]
    params: Union[Dict[str, JsonValue], None]

class ResolvedCascadedPipeline(TypedDict, total=False):
    mode: Required[Literal['cascaded']]
    avatar: Union[ResolvedAvatar, None]
    turn_detection: Union[TurnDetection, None]
    asr: Union[ResolvedAsr, None]
    tts: Union[ResolvedTts, None]
    llm: Union[ResolvedLlm, None]
    silence_config: Union[SilenceConfig, None]

class ResolvedCredential(TypedDict, total=False):
    mode: Required[Literal['managed', 'byok']]

class ResolvedLlm(TypedDict, total=False):
    credential: Union[ResolvedCredential, None]
    url: Union[str, None]
    vendor: Union[str, None]
    style: Union[str, None]
    model: Union[str, None]
    params: Union[Dict[str, JsonValue], None]
    input_modalities: Union[List[str], None]
    output_modalities: Union[List[str], None]
    max_history: Union[int, None]
    failure_message: Union[str, None]
    mcp_servers: Union[List[McpServer], None]
    tools: Union[List[FunctionTool], None]

class ResolvedTts(TypedDict, total=False):
    credential: Union[ResolvedCredential, None]
    url: Union[str, None]
    vendor: Union[str, None]
    model: Union[str, None]
    params: Union[Dict[str, JsonValue], None]
    skip_patterns: Union[List[str], None]

class RtcEncryption(TypedDict, total=False):
    mode: Required[Literal['aes_128_xts', 'aes_128_ecb', 'aes_256_xts', 'sm4_128_ecb', 'aes_128_gcm', 'aes_256_gcm', 'aes_128_gcm2', 'aes_256_gcm2']]
    key: Required[str]
    salt: Union[str, None]

class RtcTransport(TypedDict, total=False):
    type: Required[Literal['rtc']]
    channel: Required[str]
    token: Union[str, None]
    uid: str
    subscribe_uids: Required[List[str]]
    encryption: Union[RtcEncryption, None]
    audio_scenario: Literal['aiserver', 'chorus']

class ScheduledSchedule(TypedDict, total=False):
    mode: Required[Literal['scheduled']]
    timezone: Required[str]
    start: Required[str]
    end: Required[str]
    days: List[CallingDay]

class SecretCreate(TypedDict, total=False):
    name: Required[str]
    secrets: Required[Dict[str, str]]

class SecretDeleted(TypedDict, total=False):
    deleted: Required[Literal[True]]

class SecretKey(TypedDict, total=False):
    key: Required[str]
    create_ts: int
    update_ts: int

class SecretKeyWrite(TypedDict, total=False):
    value: Required[str]

class SecretList(TypedDict, total=False):
    data: Required[SecretPage]
    has_more: Required[bool]
    next_cursor: Required[Union[str, None]]

class SecretPage(TypedDict, total=False):
    count: Required[int]
    list: Required[List[SecretSet]]

class SecretReplace(TypedDict, total=False):
    secrets: Required[Dict[str, str]]

class SecretSet(TypedDict, total=False):
    name: Required[str]
    keys: Required[List[Union[str, SecretKey]]]
    create_ts: Required[int]
    update_ts: Required[int]

class SecretUpdate(TypedDict, total=False):
    secrets: Required[Dict[str, Union[str, None]]]

class SemanticTurnEnd(TypedDict, total=False):
    type: Required[Literal['semantic']]
    silence_duration_ms: Union[int, None]
    max_wait_ms: Union[int, Literal[-1], None]
    pause_state_enabled: Union[bool, None]

class SemanticTurnStart(TypedDict, total=False):
    type: Required[Literal['semantic']]
    speaking_interrupt_duration_ms: Union[int, None]

class SessionAgentOverridesPatch(TypedDict, total=False):
    messages: List[Message]
    pipeline: SessionPipelinePatch

class SessionAgentPatch(TypedDict, total=False):
    overrides: SessionAgentOverridesPatch

class SessionCreate(TypedDict, total=False):
    agent_id: Required[str]
    values: Union[Dict[str, Union[str, int, float, bool]], None]
    labels: Union[Dict[str, str], None]
    transport: Required[Union[RtcTransport, TelephonyTransport]]
    lifecycle: Union[Lifecycle, None]
    data_policy: Union[DataPolicy, None]

class SessionData(TypedDict, total=False):
    count: Required[int]
    list: Required[List[SessionSummary]]

class SessionList(TypedDict, total=False):
    data: Required[SessionData]
    has_more: Required[bool]
    next_cursor: Required[Union[str, None]]

class SessionModulePatch(TypedDict, total=False):
    params: Dict[str, JsonValue]

class SessionPatch(TypedDict, total=False):
    transport: SessionTransportPatch
    agent: SessionAgentPatch

class SessionPipelinePatch(TypedDict, total=False):
    llm: SessionModulePatch

class SessionResponse(TypedDict, total=False):
    agent_session_id: Required[str]
    agent_name: str
    start_ts: Required[int]
    status: Required[Literal['IDLE', 'STARTING', 'RUNNING', 'STOPPING', 'STOPPED', 'FAILED']]
    stop_ts: Union[int, None]
    message: Union[str, None]
    analysis: Union[SessionAnalysis, None]

class SessionStartResponse(TypedDict, total=False):
    agent_session_id: Required[str]
    create_ts: Required[int]
    status: Required[Literal['STARTING', 'RUNNING']]

class SessionStopResponse(TypedDict, total=False):
    pass

class SessionSummary(TypedDict, total=False):
    agent_session_id: Required[str]
    start_ts: Required[int]
    status: Required[Literal['IDLE', 'STARTING', 'RUNNING', 'STOPPING', 'STOPPED', 'FAILED']]

class SessionTransportPatch(TypedDict, total=False):
    token: Required[str]

class SessionUpdateResponse(TypedDict, total=False):
    agent_session_id: Required[str]
    create_ts: Required[int]
    status: Required[Literal['IDLE', 'STARTING', 'RUNNING', 'STOPPING', 'STOPPED', 'FAILED']]

class SilenceConfig(TypedDict, total=False):
    enabled: Required[bool]
    timeout_ms: Required[int]
    action: Required[Literal['speak', 'think']]
    content: Required[str]

class SipAuth(TypedDict, total=False):
    username: Required[str]
    password: Required[str]

class SipTrunkInput(TypedDict, total=False):
    name: Union[str, None]
    hostname: Required[str]
    port: Union[int, None]
    transport: Literal['udp', 'tcp', 'tls']
    auth: Union[SipAuth, None]
    allowed_ips: Union[List[str], None]

class SipTrunkOutput(TypedDict, total=False):
    name: Union[str, None]
    hostname: Required[str]
    port: Required[int]
    transport: Required[Literal['udp', 'tcp', 'tls']]
    allowed_ips: Union[List[str], None]

class SpeechInterruption(TypedDict, total=False):
    mode: Required[Literal['start_of_speech']]

class StaticFillerContent(TypedDict, total=False):
    mode: Required[Literal['static']]
    phrases: Required[List[str]]
    selection_rule: Literal['shuffle', 'round_robin']

TelephonyTransport = TypedDict('TelephonyTransport', {'type': Required["Literal['telephony']"], 'from': Required['str'], 'to': Required['str'], 'call_policy': 'Union[CallPolicy, None]'}, total=False)

class TextGreeting(TypedDict, total=False):
    mode: Required[Literal['text']]
    on: Literal['each_join', 'first_join']
    delay_ms: int
    text: Required[str]

class TimeRange(TypedDict, total=False):
    start: Required[str]
    end: Required[str]

class ToolExecution(TypedDict, total=False):
    mode: Required[Literal['sync']]

class ToolServer(TypedDict, total=False):
    method: Required[Literal['GET', 'POST']]
    url: Required[str]
    headers: Union[Dict[str, str], None]
    body: Union[JSONObject, None]
    timeout_ms: Union[int, None]

class TransferPolicy(TypedDict, total=False):
    phone_number: Required[str]
    description: Required[str]

class TtsInput(TypedDict, total=False):
    skip_patterns: Union[List[SkipPattern], None]
    credential: Union[Union[ManagedCredential, PublicByokCredential], None]
    vendor: Union[str, None]
    params: Union[JSONObject, None]
    url: Union[str, None]
    headers: Union[Dict[str, str], None]

class TurnDetection(TypedDict, total=False):
    speech_threshold: Union[float, int, None]
    start_of_speech: Union[Union[SemanticTurnStart, VadTurnStart, ManualTurnBoundary], None]
    end_of_speech: Union[Union[SemanticTurnEnd, VadTurnEnd, ManualTurnBoundary], None]
    interruption: Union[Union[SpeechInterruption, KeywordInterruption, DisabledInterruption], None]

class VadTurnEnd(TypedDict, total=False):
    type: Required[Literal['vad']]
    silence_duration_ms: Union[int, None]

class VadTurnStart(TypedDict, total=False):
    type: Required[Literal['vad']]
    interrupt_duration_ms: Union[int, None]
    speaking_interrupt_duration_ms: Union[int, None]
    prefix_padding_ms: Union[int, None]

class VariableDefinition(TypedDict, total=False):
    type: Required[Literal['str', 'int', 'float', 'bool', 'date', 'datetime']]
    required: bool
    options: Union[List[Union[str, int, float, bool]], None]
    extract: bool
    description: Union[str, None]

class VoicemailPolicy(TypedDict, total=False):
    mode: Required[Literal['continue', 'hangup']]

class AgentRequest_AgentCreateInput(TypedDict, total=False):
    agent_name: Required[str]
    instructions: Union[str, None]
    messages: Union[List[AgentRequest_Message], None]
    greeting: Union[Union[AgentRequest_TextGreeting, AgentRequest_AudioGreeting], None]
    variables: Union[Dict[str, AgentRequest_VariableDefinition], None]
    pipeline: Union[AgentRequest_CascadedPipelineInput, None]
    filler_words: Union[AgentRequest_FillerWords, None]

class AgentRequest_AgentPatch(TypedDict, total=False):
    agent_name: Union[str, None]
    instructions: Union[str, None]
    messages: Union[List[AgentRequest_Message], None]
    greeting: Union[AgentRequest_GreetingPatch, None]
    variables: Union[Dict[str, Union[AgentRequest_VariableDefinitionPatch, None]], None]
    pipeline: Union[AgentRequest_CascadedPipelinePatch, None]
    filler_words: Union[AgentRequest_FillerWordsPatch, None]

class AgentRequest_AsrInput(TypedDict, total=False):
    credential: Union[Union[AgentRequest_ManagedCredential, AgentRequest_PublicByokCredential], None]
    vendor: Union[str, None]
    params: Union[AgentRequest_JSONObject, None]
    url: Union[str, None]
    model: Union[str, None]
    language: Union[str, None]

class AgentRequest_AsrPatch(TypedDict, total=False):
    credential: Union[AgentRequest_PublicCredentialPatch, None]
    vendor: Union[str, None]
    params: Union[AgentRequest_JSONObject, None]
    url: Union[str, None]
    model: Union[str, None]
    language: Union[str, None]

class AgentRequest_AudioGreeting(TypedDict, total=False):
    mode: Required[Literal['audio']]
    on: Literal['each_join', 'first_join']
    delay_ms: int
    url: Required[str]
    text: Required[str]
    download_timeout_ms: int
    pcm_sample_rate: int

class AgentRequest_AvatarInput(TypedDict, total=False):
    credential: Union[Union[AgentRequest_ManagedCredential, AgentRequest_PublicByokCredential], None]
    vendor: Union[AgentRequest_AvatarVendor, None]
    params: Union[AgentRequest_JSONObject, None]
    enabled: Union[bool, None]

class AgentRequest_AvatarPatch(TypedDict, total=False):
    credential: Union[AgentRequest_PublicCredentialPatch, None]
    vendor: Union[AgentRequest_AvatarVendor, None]
    params: Union[AgentRequest_JSONObject, None]
    enabled: Union[bool, None]

class AgentRequest_CascadedPipelineInput(TypedDict, total=False):
    mode: Required[Literal['cascaded']]
    avatar: Union[AgentRequest_AvatarInput, None]
    turn_detection: Union[AgentRequest_TurnDetection, None]
    asr: Union[AgentRequest_AsrInput, None]
    tts: Union[AgentRequest_TtsInput, None]
    llm: Union[AgentRequest_LlmInput, None]
    silence_config: Union[AgentRequest_SilenceConfig, None]

class AgentRequest_CascadedPipelinePatch(TypedDict, total=False):
    mode: Union[Literal['cascaded'], None]
    avatar: Union[AgentRequest_AvatarPatch, None]
    turn_detection: Union[AgentRequest_CascadedTurnDetectionPatch, None]
    asr: Union[AgentRequest_AsrPatch, None]
    tts: Union[AgentRequest_TtsPatch, None]
    llm: Union[AgentRequest_LlmPatch, None]
    silence_config: Union[AgentRequest_SilenceConfigPatch, None]

class AgentRequest_CascadedTurnDetectionPatch(TypedDict, total=False):
    speech_threshold: Union[float, int, None]
    start_of_speech: Union[AgentRequest_TurnBoundaryPatch, None]
    end_of_speech: Union[AgentRequest_TurnBoundaryPatch, None]
    interruption: Union[AgentRequest_InterruptionPatch, None]

class AgentRequest_DisabledInterruption(TypedDict, total=False):
    mode: Required[Literal['off']]
    when_off: Literal['append', 'ignore']

class AgentRequest_FillerContentPatch(TypedDict, total=False):
    mode: Union[Literal['static', 'generated'], None]
    phrases: Union[List[str], None]
    selection_rule: Union[Literal['shuffle', 'round_robin'], None]
    instructions: Union[str, None]
    fallback_strategy: Union[Literal['static'], None]

class AgentRequest_FillerTrigger(TypedDict, total=False):
    mode: Required[Literal['fixed_time']]
    response_wait_ms: Required[int]

class AgentRequest_FillerTriggerPatch(TypedDict, total=False):
    mode: Union[Literal['fixed_time'], None]
    response_wait_ms: Union[int, None]

class AgentRequest_FillerWords(TypedDict, total=False):
    enable: Union[bool, None]
    trigger: Union[AgentRequest_FillerTrigger, None]
    content: Union[Union[AgentRequest_StaticFillerContent, AgentRequest_GeneratedFillerContent], None]

class AgentRequest_FillerWordsPatch(TypedDict, total=False):
    enable: Union[bool, None]
    trigger: Union[AgentRequest_FillerTriggerPatch, None]
    content: Union[AgentRequest_FillerContentPatch, None]

class AgentRequest_FunctionTool(TypedDict, total=False):
    type: Required[Literal['function']]
    name: Required[str]
    description: Required[str]
    parameters: Required[AgentRequest_JSONObject]
    execution: Required[AgentRequest_ToolExecution]
    server: Required[AgentRequest_ToolServer]

class AgentRequest_GeneratedFillerContent(TypedDict, total=False):
    mode: Required[Literal['generated']]
    instructions: Required[str]
    fallback_strategy: Union[Literal['static'], None]

class AgentRequest_GreetingPatch(TypedDict, total=False):
    mode: Union[Literal['text', 'audio'], None]
    on: Union[Literal['each_join', 'first_join'], None]
    delay_ms: Union[int, None]
    url: Union[str, None]
    text: Union[str, None]
    download_timeout_ms: Union[int, None]
    pcm_sample_rate: Union[int, None]

class AgentRequest_InterruptionPatch(TypedDict, total=False):
    mode: Union[Literal['start_of_speech', 'keywords', 'off'], None]
    keywords: Union[List[str], None]
    when_off: Union[Literal['append', 'ignore'], None]

class AgentRequest_KeywordInterruption(TypedDict, total=False):
    mode: Required[Literal['keywords']]
    keywords: Required[List[str]]

class AgentRequest_LlmInput(TypedDict, total=False):
    mcp_servers: Union[List[AgentRequest_McpServer], None]
    tools: Union[List[AgentRequest_FunctionTool], None]
    credential: Union[Union[AgentRequest_ManagedCredential, AgentRequest_PublicByokCredential], None]
    vendor: Union[str, None]
    params: Union[AgentRequest_JSONObject, None]
    url: Union[str, None]
    style: Union[str, None]
    model: Union[str, None]
    headers: Union[Dict[str, str], None]
    input_modalities: Union[List[str], None]
    output_modalities: Union[List[str], None]
    max_history: Union[int, None]
    failure_message: Union[str, None]

class AgentRequest_LlmPatch(TypedDict, total=False):
    mcp_servers: Union[List[AgentRequest_McpServer], None]
    tools: Union[List[AgentRequest_FunctionTool], None]
    credential: Union[AgentRequest_PublicCredentialPatch, None]
    vendor: Union[str, None]
    params: Union[AgentRequest_JSONObject, None]
    url: Union[str, None]
    style: Union[str, None]
    model: Union[str, None]
    headers: Union[Dict[str, str], None]
    input_modalities: Union[List[str], None]
    output_modalities: Union[List[str], None]
    max_history: Union[int, None]
    failure_message: Union[str, None]

class AgentRequest_ManagedCredential(TypedDict, total=False):
    mode: Required[Literal['managed']]

class AgentRequest_ManualTurnBoundary(TypedDict, total=False):
    type: Required[Literal['manual']]

class AgentRequest_McpServer(TypedDict, total=False):
    name: Required[str]
    endpoint: Required[str]
    transport: Required[Literal['streamable_http']]
    headers: Union[Dict[str, str], None]
    allowed_tools: Union[List[str], None]
    timeout_ms: Union[int, None]

class AgentRequest_Message(TypedDict, total=False):
    role: Required[Literal['system', 'user', 'assistant']]
    content: Required[str]

class AgentRequest_PublicByokCredential(TypedDict, total=False):
    mode: Required[Literal['byok']]
    fields: Required[Dict[str, str]]

class AgentRequest_PublicCredentialPatch(TypedDict, total=False):
    mode: Union[Literal['managed', 'byok'], None]
    fields: Union[Dict[str, Union[str, None]], None]

class AgentRequest_SemanticTurnEnd(TypedDict, total=False):
    type: Required[Literal['semantic']]
    silence_duration_ms: Union[int, None]
    max_wait_ms: Union[int, Literal[-1], None]
    pause_state_enabled: Union[bool, None]

class AgentRequest_SemanticTurnStart(TypedDict, total=False):
    type: Required[Literal['semantic']]
    speaking_interrupt_duration_ms: Union[int, None]

class AgentRequest_SilenceConfig(TypedDict, total=False):
    enabled: Required[bool]
    timeout_ms: Required[int]
    action: Required[Literal['speak', 'think']]
    content: Required[str]

class AgentRequest_SilenceConfigPatch(TypedDict, total=False):
    enabled: Union[bool, None]
    timeout_ms: Union[int, None]
    action: Union[Literal['speak', 'think'], None]
    content: Union[str, None]

class AgentRequest_SpeechInterruption(TypedDict, total=False):
    mode: Required[Literal['start_of_speech']]

class AgentRequest_StaticFillerContent(TypedDict, total=False):
    mode: Required[Literal['static']]
    phrases: Required[List[str]]
    selection_rule: Literal['shuffle', 'round_robin']

class AgentRequest_TextGreeting(TypedDict, total=False):
    mode: Required[Literal['text']]
    on: Literal['each_join', 'first_join']
    delay_ms: int
    text: Required[str]

class AgentRequest_ToolExecution(TypedDict, total=False):
    mode: Required[Literal['sync']]

class AgentRequest_ToolServer(TypedDict, total=False):
    method: Required[Literal['GET', 'POST']]
    url: Required[str]
    headers: Union[Dict[str, str], None]
    body: Union[AgentRequest_JSONObject, None]
    timeout_ms: Union[int, None]

class AgentRequest_TtsInput(TypedDict, total=False):
    skip_patterns: Union[List[AgentRequest_SkipPattern], None]
    credential: Union[Union[AgentRequest_ManagedCredential, AgentRequest_PublicByokCredential], None]
    vendor: Union[str, None]
    params: Union[AgentRequest_JSONObject, None]
    url: Union[str, None]
    headers: Union[Dict[str, str], None]

class AgentRequest_TtsPatch(TypedDict, total=False):
    skip_patterns: Union[List[AgentRequest_SkipPattern], None]
    credential: Union[AgentRequest_PublicCredentialPatch, None]
    vendor: Union[str, None]
    params: Union[AgentRequest_JSONObject, None]
    url: Union[str, None]
    headers: Union[Dict[str, str], None]

class AgentRequest_TurnBoundaryPatch(TypedDict, total=False):
    type: Union[Literal['semantic', 'vad', 'manual'], None]
    interrupt_duration_ms: Union[int, None]
    speaking_interrupt_duration_ms: Union[int, None]
    prefix_padding_ms: Union[int, None]
    silence_duration_ms: Union[int, None]
    max_wait_ms: Union[int, Literal[-1], None]
    pause_state_enabled: Union[bool, None]

class AgentRequest_TurnDetection(TypedDict, total=False):
    speech_threshold: Union[float, int, None]
    start_of_speech: Union[Union[AgentRequest_SemanticTurnStart, AgentRequest_VadTurnStart, AgentRequest_ManualTurnBoundary], None]
    end_of_speech: Union[Union[AgentRequest_SemanticTurnEnd, AgentRequest_VadTurnEnd, AgentRequest_ManualTurnBoundary], None]
    interruption: Union[Union[AgentRequest_SpeechInterruption, AgentRequest_KeywordInterruption, AgentRequest_DisabledInterruption], None]

class AgentRequest_VadTurnEnd(TypedDict, total=False):
    type: Required[Literal['vad']]
    silence_duration_ms: Union[int, None]

class AgentRequest_VadTurnStart(TypedDict, total=False):
    type: Required[Literal['vad']]
    interrupt_duration_ms: Union[int, None]
    speaking_interrupt_duration_ms: Union[int, None]
    prefix_padding_ms: Union[int, None]

class AgentRequest_VariableDefinition(TypedDict, total=False):
    type: Required[Literal['str', 'int', 'float', 'bool', 'date', 'datetime']]
    required: bool
    options: Union[List[Union[str, int, float, bool]], None]
    extract: bool
    description: Union[str, None]

class AgentRequest_VariableDefinitionPatch(TypedDict, total=False):
    type: Union[Literal['str', 'int', 'float', 'bool', 'date', 'datetime'], None]
    required: Union[bool, None]
    options: Union[List[Union[str, int, float, bool]], None]
    extract: Union[bool, None]
    description: Union[str, None]

class SessionEndCallPolicy(TypedDict, total=False):
    on_conversation_complete: bool
    on_user_request: bool
    on_fax: bool
    on_ai_assistant: bool
    on_voicemail: bool

class InboundEndCallPolicy(TypedDict, total=False):
    on_conversation_complete: bool
    on_user_request: bool
    on_voicemail: bool
    on_ai_assistant: bool
    on_fax: bool

class SessionAnalysis(TypedDict, total=False):
    status: Required[Literal['pending', 'completed', 'failed', 'skipped']]
    skip_reason: Required[Union[Literal['no_user_turns', 'retention_none'], None]]
    complete_ts: Required[Union[int, None]]
    result: Required[Union[Dict[str, Union[str, int, float, bool, None]], None]]
    error: Required[Union[str, None]]

AvatarVendor = Literal['akool', 'liveavatar', 'anam', 'sensetime', 'spatius', 'generic']
ErrorReason = Literal['InvalidRequestBody', 'MissingRequiredField', 'InvalidFieldValue', 'InvalidModuleParameter', 'UnknownSecretReference', 'NotImplemented', 'InvalidPermission', 'ServiceNotEnabled', 'AccountSuspended', 'TaskNotFound', 'ResourceNotFound', 'AgentNotFound', 'NumberNotFound', 'NumberAlreadyExists', 'ResourceConflict', 'MethodNotAllowed', 'PayloadTooLarge', 'UnsupportedMediaType', 'TaskConflict', 'CampaignActive', 'CampaignInvalidState', 'CampaignNotEditable', 'IdempotencyKeyConflict', 'SecretSetAlreadyExists', 'SecretSetInUse', 'SecretSetEmpty', 'TaskNotRunning', 'RateLimitExceeded', 'PreconditionFailed', 'PreconditionRequired', 'ResourceQuotaLimitExceeded', 'ConcurrencyLimitExceeded', 'InternalError', 'ServiceUnavailable', 'ResourceAllocationFailed', 'TaskOperationTimeout']
JSONObject = Dict[str, 'JsonValue']
JsonValue = Any
SkipPattern = Literal['fullwidth_parentheses', 'lenticular_brackets', 'parentheses', 'square_brackets', 'curly_braces']
AgentRequest_AvatarVendor = Literal['akool', 'liveavatar', 'anam', 'sensetime', 'spatius', 'generic']
AgentRequest_JSONObject = Dict[str, 'AgentRequest_JsonValue']
AgentRequest_JsonValue = Any
AgentRequest_SkipPattern = Literal['fullwidth_parentheses', 'lenticular_brackets', 'parentheses', 'square_brackets', 'curly_braces']
AgentCreateInput = AgentRequest_AgentCreateInput
AgentPatch = AgentRequest_AgentPatch

# Compatibility names retained for the additive preview namespace.
AgentCreateModel = AgentCreateInput
AgentPatchRequest = AgentPatch
SessionLifecycle = Lifecycle
EphemeralSessionAgent = PublicAgentInput
StartSessionResponse = SessionStartResponse
class RtcGeofence(TypedDict, total=False):
    area: Required[Literal["global", "north_america", "europe", "asia", "india", "japan"]]
    exclude_area: Literal["north_america", "europe", "asia", "india", "japan"]
class RtcSessionTransport(RtcTransport, total=False):
    geofence: RtcGeofence
SessionTransport = Union[RtcSessionTransport, TelephonyTransport]

__all__ = ['AgentDeleteResponse', 'AgentListData', 'AgentListItem', 'AgentListResponse', 'AgentResponse', 'AsrInput', 'AudioGreeting', 'AvatarInput', 'AvatarVendor', 'CallPolicy', 'CallingDay', 'CampaignCallPolicy', 'CampaignCounts', 'CampaignCreate', 'CampaignDeleteResponse', 'CampaignEndCallPolicy', 'CampaignFailure', 'CampaignLifecycle', 'CampaignListData', 'CampaignListResponse', 'CampaignPatch', 'CampaignResponse', 'CampaignTransferPolicy', 'CampaignTransport', 'CampaignTransportPatch', 'CampaignTransportResponse', 'CampaignVoicemailPolicy', 'CascadedPipelineInput', 'ContactInput', 'DataPolicy', 'DisabledInterruption', 'ErrorReason', 'ErrorResponse', 'FillerTrigger', 'FillerWords', 'FunctionTool', 'GeneratedFillerContent', 'GracefulStop', 'ImmediateSchedule', 'InboundCallPolicy', 'InboundInput', 'InboundOutput', 'JSONObject', 'JsonValue', 'KeywordInterruption', 'Lifecycle', 'LlmInput', 'ManagedCredential', 'ManualTurnBoundary', 'McpServer', 'Message', 'NumberCreate', 'NumberDeleteResponse', 'NumberListData', 'NumberListResponse', 'NumberPatch', 'NumberResponse', 'Pacing', 'PacingPatch', 'PublicAgentInput', 'PublicByokCredential', 'PublicEphemeralSessionCreate', 'ResolvedAsr', 'ResolvedAvatar', 'ResolvedCascadedPipeline', 'ResolvedCredential', 'ResolvedLlm', 'ResolvedTts', 'RtcEncryption', 'RtcTransport', 'ScheduledSchedule', 'SecretCreate', 'SecretDeleted', 'SecretKey', 'SecretKeyWrite', 'SecretList', 'SecretPage', 'SecretReplace', 'SecretSet', 'SecretUpdate', 'SemanticTurnEnd', 'SemanticTurnStart', 'SessionAgentOverridesPatch', 'SessionAgentPatch', 'SessionCreate', 'SessionData', 'SessionList', 'SessionModulePatch', 'SessionPatch', 'SessionPipelinePatch', 'SessionResponse', 'SessionStartResponse', 'SessionStopResponse', 'SessionSummary', 'SessionTransportPatch', 'SessionUpdateResponse', 'SilenceConfig', 'SipAuth', 'SipTrunkInput', 'SipTrunkOutput', 'SkipPattern', 'SpeechInterruption', 'StaticFillerContent', 'TelephonyTransport', 'TextGreeting', 'TimeRange', 'ToolExecution', 'ToolServer', 'TransferPolicy', 'TtsInput', 'TurnDetection', 'VadTurnEnd', 'VadTurnStart', 'VariableDefinition', 'VoicemailPolicy', 'AgentRequest_AgentCreateInput', 'AgentRequest_AgentPatch', 'AgentRequest_AsrInput', 'AgentRequest_AsrPatch', 'AgentRequest_AudioGreeting', 'AgentRequest_AvatarInput', 'AgentRequest_AvatarPatch', 'AgentRequest_AvatarVendor', 'AgentRequest_CascadedPipelineInput', 'AgentRequest_CascadedPipelinePatch', 'AgentRequest_CascadedTurnDetectionPatch', 'AgentRequest_DisabledInterruption', 'AgentRequest_FillerContentPatch', 'AgentRequest_FillerTrigger', 'AgentRequest_FillerTriggerPatch', 'AgentRequest_FillerWords', 'AgentRequest_FillerWordsPatch', 'AgentRequest_FunctionTool', 'AgentRequest_GeneratedFillerContent', 'AgentRequest_GreetingPatch', 'AgentRequest_InterruptionPatch', 'AgentRequest_JSONObject', 'AgentRequest_JsonValue', 'AgentRequest_KeywordInterruption', 'AgentRequest_LlmInput', 'AgentRequest_LlmPatch', 'AgentRequest_ManagedCredential', 'AgentRequest_ManualTurnBoundary', 'AgentRequest_McpServer', 'AgentRequest_Message', 'AgentRequest_PublicByokCredential', 'AgentRequest_PublicCredentialPatch', 'AgentRequest_SemanticTurnEnd', 'AgentRequest_SemanticTurnStart', 'AgentRequest_SilenceConfig', 'AgentRequest_SilenceConfigPatch', 'AgentRequest_SkipPattern', 'AgentRequest_SpeechInterruption', 'AgentRequest_StaticFillerContent', 'AgentRequest_TextGreeting', 'AgentRequest_ToolExecution', 'AgentRequest_ToolServer', 'AgentRequest_TtsInput', 'AgentRequest_TtsPatch', 'AgentRequest_TurnBoundaryPatch', 'AgentRequest_TurnDetection', 'AgentRequest_VadTurnEnd', 'AgentRequest_VadTurnStart', 'AgentRequest_VariableDefinition', 'AgentRequest_VariableDefinitionPatch', 'AgentCreateInput', 'AgentPatch', 'SessionEndCallPolicy', 'InboundEndCallPolicy', 'SessionAnalysis', 'AgentCreateModel', 'AgentPatchRequest', 'SessionLifecycle', 'EphemeralSessionAgent', 'StartSessionResponse', 'RtcGeofence', 'RtcSessionTransport', 'SessionTransport']
