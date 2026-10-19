"""Typed staging OpenAPI wire schemas. Dictionaries preserve omitted versus null fields."""
from __future__ import annotations

from typing import Any, Dict, List, Union

from typing_extensions import Literal, Required, TypedDict


class AgentDeleteResponse(TypedDict, total=False):
    deleted: Required[Literal[True]]

class AgentListData(TypedDict, total=False):
    count: Required[int]
    list: Required[List['AgentListItem']]

class AgentListItem(TypedDict, total=False):
    agent_id: Required[str]
    agent_name: Required[str]
    create_ts: Required[int]
    update_ts: Required[int]

class AgentListResponse(TypedDict, total=False):
    data: Required['AgentListData']
    has_more: Required[bool]
    next_cursor: Required[Union[str, None]]

class AgentResponse(TypedDict, total=False):
    agent_id: Required[str]
    create_ts: Required[int]
    update_ts: Required[int]
    agent_name: Required[str]
    instructions: Union[str, None]
    messages: Union[List['Message'], None]
    greeting: Union[Union['TextGreeting', 'AudioGreeting'], None]
    variables: Union[Dict[str, 'VariableDefinition'], None]
    pipeline: Union[Union['ResolvedCascadedPipeline', 'ResolvedRealtimePipeline'], None]
    filler_words: Union['FillerWords', None]

class AgoraVadTurnDetection(TypedDict, total=False):
    type: Required[Literal['agora_vad']]
    interrupt_duration_ms: Union[int, None]
    prefix_padding_ms: Union[int, None]
    silence_duration_ms: Union[int, None]
    threshold: Union[float, int, None]

class AudioGreeting(TypedDict, total=False):
    mode: Required[Literal['audio']]
    on: Literal['each_join', 'first_join']
    delay_ms: int
    url: Required[str]
    text: Required[str]
    download_timeout_ms: int
    pcm_sample_rate: int

class DisabledInterruption(TypedDict, total=False):
    mode: Required[Literal['off']]
    when_off: Literal['append', 'ignore']

class EndCallPolicy(TypedDict, total=False):
    on_conversation_complete: bool
    on_user_request: bool
    on_fax: bool
    on_ai_assistant: bool

ErrorReason = Literal['InvalidRequestBody', 'MissingRequiredField', 'InvalidFieldValue', 'InvalidModuleParameter', 'UnknownSecretReference', 'NotImplemented', 'InvalidPermission', 'ServiceNotEnabled', 'AccountSuspended', 'TaskNotFound', 'ResourceNotFound', 'AgentNotFound', 'NumberAlreadyExists', 'ResourceConflict', 'MethodNotAllowed', 'PayloadTooLarge', 'UnsupportedMediaType', 'TaskConflict', 'IdempotencyKeyConflict', 'SecretSetAlreadyExists', 'SecretSetInUse', 'SecretSetEmpty', 'TaskNotRunning', 'RateLimitExceeded', 'PreconditionFailed', 'PreconditionRequired', 'ResourceQuotaLimitExceeded', 'ConcurrencyLimitExceeded', 'InternalError', 'ServiceUnavailable', 'ResourceAllocationFailed', 'TaskOperationTimeout']

class ErrorResponse(TypedDict, total=False):
    detail: Required[str]
    reason: Required['ErrorReason']

class FillerTrigger(TypedDict, total=False):
    mode: Required[Literal['fixed_time']]
    response_wait_ms: Required[int]

class FillerWords(TypedDict, total=False):
    enable: Union[bool, None]
    trigger: Union['FillerTrigger', None]
    content: Union[Union['StaticFillerContent', 'GeneratedFillerContent'], None]

class GeneratedFillerContent(TypedDict, total=False):
    mode: Required[Literal['generated']]
    instructions: Required[str]
    fallback_strategy: Union[Literal['static'], None]

class InboundCallPolicy(TypedDict, total=False):
    max_call_duration_seconds: Union[int, None]
    max_silence_duration_ms: Union[int, None]
    end_call: Union['EndCallPolicy', None]
    transfer: Union['TransferPolicy', None]

class InboundInput(TypedDict, total=False):
    agent: Required[Union[str, None]]
    call_policy: Union['InboundCallPolicy', None]

class InboundOutput(TypedDict, total=False):
    agent: Required[Union[str, None]]
    call_policy: Union['InboundCallPolicy', None]

JsonValue = Any

class KeywordInterruption(TypedDict, total=False):
    mode: Required[Literal['keywords']]
    keywords: Required[List[str]]

class ManualTurnBoundary(TypedDict, total=False):
    type: Required[Literal['manual']]

class Message(TypedDict, total=False):
    role: Required[Literal['system', 'user', 'assistant']]
    content: Required[str]

class NumberCreate(TypedDict, total=False):
    number: Required[str]
    description: Union[str, None]
    sip_trunk: Required['SipTrunkInput']
    inbound: Union['InboundInput', None]

class NumberDeleteResponse(TypedDict, total=False):
    deleted: Literal[True]

class NumberListData(TypedDict, total=False):
    count: Required[int]
    list: Required[List['NumberResponse']]

class NumberListResponse(TypedDict, total=False):
    data: Required['NumberListData']
    has_more: Required[bool]
    next_cursor: Required[Union[str, None]]

class NumberPatch(TypedDict, total=False):
    number: Union[str, None]
    description: Union[str, None]
    sip_trunk: Union['SipTrunkInput', None]
    inbound: Union['InboundInput', None]

class NumberResponse(TypedDict, total=False):
    number_id: Required[str]
    number: Required[str]
    description: Union[str, None]
    sip_trunk: Union['SipTrunkOutput', None]
    inbound: Union['InboundOutput', None]
    create_ts: Required[int]

class ResolvedAsr(TypedDict, total=False):
    credential: Union['ResolvedCredential', None]
    url: Union[str, None]
    vendor: Union[str, None]
    model: Union[str, None]
    language: Union[str, None]
    params: Union[Dict[str, 'JsonValue'], None]

class ResolvedAvatar(TypedDict, total=False):
    enabled: Union[bool, None]
    credential: Union['ResolvedCredential', None]
    vendor: Union[str, None]
    params: Union[Dict[str, 'JsonValue'], None]

class ResolvedCascadedPipeline(TypedDict, total=False):
    mode: Required[Literal['cascaded']]
    avatar: Union['ResolvedAvatar', None]
    turn_detection: Union['TurnDetection', None]
    asr: Union['ResolvedAsr', None]
    tts: Union['ResolvedTts', None]
    llm: Union['ResolvedLlm', None]
    silence_config: Union['SilenceConfig', None]

class ResolvedCredential(TypedDict, total=False):
    mode: Required[Literal['managed', 'byok']]

class ResolvedLlm(TypedDict, total=False):
    credential: Union['ResolvedCredential', None]
    url: Union[str, None]
    vendor: Union[str, None]
    style: Union[str, None]
    model: Union[str, None]
    params: Union[Dict[str, 'JsonValue'], None]
    input_modalities: Union[List[str], None]
    output_modalities: Union[List[str], None]
    max_history: Union[int, None]
    failure_message: Union[str, None]
    mcp_servers: Union[List[Dict[str, 'JsonValue']], None]
    tools: Union[List[Dict[str, 'JsonValue']], None]

class ResolvedMllm(TypedDict, total=False):
    credential: Union['ResolvedCredential', None]
    vendor: Union[str, None]
    model: Union[str, None]
    url: Union[str, None]
    params: Union[Dict[str, 'JsonValue'], None]
    input_modalities: Union[List[str], None]
    output_modalities: Union[List[str], None]
    mcp_servers: Union[List[Dict[str, 'JsonValue']], None]

class ResolvedRealtimePipeline(TypedDict, total=False):
    mode: Required[Literal['realtime']]
    avatar: Union['ResolvedAvatar', None]
    turn_detection: Union[Union['AgoraVadTurnDetection', 'ServerVadTurnDetection', 'SemanticVadTurnDetection'], None]
    mllm: Union['ResolvedMllm', None]

class ResolvedTts(TypedDict, total=False):
    credential: Union['ResolvedCredential', None]
    url: Union[str, None]
    vendor: Union[str, None]
    model: Union[str, None]
    params: Union[Dict[str, 'JsonValue'], None]
    skip_patterns: Union[List[str], None]

class SecretCreate(TypedDict, total=False):
    name: Required[str]
    secrets: Required[Dict[str, str]]

class SecretDeleted(TypedDict, total=False):
    deleted: Required[Literal[True]]

class SecretKey(TypedDict, total=False):
    key: Required[str]

class SecretKeyWrite(TypedDict, total=False):
    value: Required[str]

class SecretList(TypedDict, total=False):
    data: Required['SecretPage']
    has_more: Required[bool]
    next_cursor: Required[Union[str, None]]

class SecretPage(TypedDict, total=False):
    count: Required[int]
    list: Required[List['SecretSet']]

class SecretReplace(TypedDict, total=False):
    secrets: Required[Dict[str, str]]

class SecretSet(TypedDict, total=False):
    name: Required[str]
    keys: Required[List[str]]
    create_ts: Required[int]
    update_ts: Required[int]

class SecretUpdate(TypedDict, total=False):
    secrets: Required[Dict[str, Union[str, None]]]

class SemanticTurnEnd(TypedDict, total=False):
    type: Required[Literal['semantic']]
    silence_duration_ms: Union[int, None]
    max_wait_ms: Union[int, None]
    pause_state_enabled: Union[bool, None]

class SemanticTurnStart(TypedDict, total=False):
    type: Required[Literal['semantic']]
    speaking_interrupt_duration_ms: Union[int, None]

class SemanticVadTurnDetection(TypedDict, total=False):
    type: Required[Literal['semantic_vad']]
    eagerness: Union[Literal['auto', 'low', 'medium', 'high'], None]

class ServerVadTurnDetection(TypedDict, total=False):
    type: Required[Literal['server_vad']]
    prefix_padding_ms: Union[int, None]
    silence_duration_ms: Union[int, None]
    threshold: Union[float, int, None]
    idle_timeout_ms: Union[int, None]
    start_of_speech_sensitivity: Union[Literal['START_SENSITIVITY_HIGH', 'START_SENSITIVITY_LOW'], None]
    end_of_speech_sensitivity: Union[Literal['END_SENSITIVITY_HIGH', 'END_SENSITIVITY_LOW'], None]

class SessionAnalysis(TypedDict, total=False):
    status: Required[Literal['pending', 'completed', 'failed', 'skipped']]
    skip_reason: Required[Union[Literal['no_user_turns', 'retention_none'], None]]
    complete_ts: Required[Union[int, None]]
    result: Required[Union[Dict[str, Union[str, int, float, bool, None]], None]]
    error: Required[Union[str, None]]

class SessionData(TypedDict, total=False):
    count: Required[int]
    list: Required[List['SessionSummary']]

class SessionList(TypedDict, total=False):
    data: Required['SessionData']
    has_more: Required[bool]
    next_cursor: Required[Union[str, None]]

class SessionResponse(TypedDict, total=False):
    agent_session_id: Required[str]
    start_ts: Required[int]
    status: Required[Literal['IDLE', 'STARTING', 'RUNNING', 'STOPPING', 'STOPPED', 'FAILED']]
    agent_name: str
    stop_ts: Union[int, None]
    message: Union[str, None]
    analysis: Union['SessionAnalysis', None]

class SessionSummary(TypedDict, total=False):
    agent_session_id: Required[str]
    start_ts: Required[int]
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
    auth: Union['SipAuth', None]
    allowed_ips: Any

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

class TextGreeting(TypedDict, total=False):
    mode: Required[Literal['text']]
    on: Literal['each_join', 'first_join']
    delay_ms: int
    text: Required[str]

class TransferPolicy(TypedDict, total=False):
    phone_number: Required[str]
    description: Required[str]

class TurnDetection(TypedDict, total=False):
    speech_threshold: Union[float, int, None]
    start_of_speech: Union[Union['SemanticTurnStart', 'VadTurnStart', 'ManualTurnBoundary'], None]
    end_of_speech: Union[Union['SemanticTurnEnd', 'VadTurnEnd', 'ManualTurnBoundary'], None]
    interruption: Union[Union['SpeechInterruption', 'KeywordInterruption', 'DisabledInterruption'], None]

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

class AgentCreateModel_AgoraVadTurnDetection(TypedDict, total=False):
    type: Required[Literal['agora_vad']]
    interrupt_duration_ms: Union[int, None]
    prefix_padding_ms: Union[int, None]
    silence_duration_ms: Union[int, None]
    threshold: Union[float, int, None]

class AgentCreateModel_AudioGreeting(TypedDict, total=False):
    mode: Required[Literal['audio']]
    on: Literal['each_join', 'first_join']
    delay_ms: int
    url: Required[str]
    text: Required[str]
    download_timeout_ms: int
    pcm_sample_rate: int

class AgentCreateModel_ByokCredential(TypedDict, total=False):
    mode: Required[Literal['byok']]
    api_key: Required[str]

class AgentCreateModel_CascadedPipeline(TypedDict, total=False):
    mode: Required[Literal['cascaded']]
    avatar: Union['AgentCreateModel_ProviderModule', None]
    turn_detection: Union['AgentCreateModel_TurnDetection', None]
    asr: Union['AgentCreateModel_ProviderModule', None]
    tts: Union['AgentCreateModel_ProviderModule', None]
    llm: Union['AgentCreateModel_ProviderModule', None]
    silence_config: Union['AgentCreateModel_SilenceConfig', None]

class AgentCreateModel_DisabledInterruption(TypedDict, total=False):
    mode: Required[Literal['off']]
    when_off: Literal['append', 'ignore']

class AgentCreateModel_FillerTrigger(TypedDict, total=False):
    mode: Required[Literal['fixed_time']]
    response_wait_ms: Required[int]

class AgentCreateModel_FillerWords(TypedDict, total=False):
    enable: Union[bool, None]
    trigger: Union['AgentCreateModel_FillerTrigger', None]
    content: Union[Union['AgentCreateModel_StaticFillerContent', 'AgentCreateModel_GeneratedFillerContent'], None]

class AgentCreateModel_GeneratedFillerContent(TypedDict, total=False):
    mode: Required[Literal['generated']]
    instructions: Required[str]
    fallback_strategy: Union[Literal['static'], None]

AgentCreateModel_JsonValue = Any

class AgentCreateModel_KeywordInterruption(TypedDict, total=False):
    mode: Required[Literal['keywords']]
    keywords: Required[List[str]]

class AgentCreateModel_ManagedCredential(TypedDict, total=False):
    mode: Required[Literal['managed']]

class AgentCreateModel_ManualTurnBoundary(TypedDict, total=False):
    type: Required[Literal['manual']]

class AgentCreateModel_Message(TypedDict, total=False):
    role: Required[Literal['system', 'user', 'assistant']]
    content: Required[str]

class AgentCreateModel_ProviderModule(TypedDict, total=False):
    credential: Union[Union['AgentCreateModel_ManagedCredential', 'AgentCreateModel_ByokCredential'], None]
    vendor: Union[str, None]
    model: Union[str, None]
    style: Union[str, None]
    language: Union[str, None]
    enabled: Union[bool, None]
    params: Union[Dict[str, 'AgentCreateModel_JsonValue'], None]
    url: Union[str, None]
    headers: Union[Dict[str, str], None]
    input_modalities: Union[List[str], None]
    output_modalities: Union[List[str], None]
    max_history: Union[int, None]
    failure_message: Union[str, None]
    mcp_servers: Union[List[Dict[str, 'AgentCreateModel_JsonValue']], None]
    tools: Union[List[Dict[str, 'AgentCreateModel_JsonValue']], None]
    skip_patterns: Union[List[str], None]

class AgentCreateModel_RealtimePipeline(TypedDict, total=False):
    mode: Required[Literal['realtime']]
    avatar: Union['AgentCreateModel_ProviderModule', None]
    turn_detection: Union[Union['AgentCreateModel_AgoraVadTurnDetection', 'AgentCreateModel_ServerVadTurnDetection', 'AgentCreateModel_SemanticVadTurnDetection'], None]
    mllm: Union['AgentCreateModel_ProviderModule', None]

class AgentCreateModel_SemanticTurnEnd(TypedDict, total=False):
    type: Required[Literal['semantic']]
    silence_duration_ms: Union[int, None]
    max_wait_ms: Union[int, None]
    pause_state_enabled: Union[bool, None]

class AgentCreateModel_SemanticTurnStart(TypedDict, total=False):
    type: Required[Literal['semantic']]
    speaking_interrupt_duration_ms: Union[int, None]

class AgentCreateModel_SemanticVadTurnDetection(TypedDict, total=False):
    type: Required[Literal['semantic_vad']]
    eagerness: Union[Literal['auto', 'low', 'medium', 'high'], None]

class AgentCreateModel_ServerVadTurnDetection(TypedDict, total=False):
    type: Required[Literal['server_vad']]
    prefix_padding_ms: Union[int, None]
    silence_duration_ms: Union[int, None]
    threshold: Union[float, int, None]
    idle_timeout_ms: Union[int, None]
    start_of_speech_sensitivity: Union[Literal['START_SENSITIVITY_HIGH', 'START_SENSITIVITY_LOW'], None]
    end_of_speech_sensitivity: Union[Literal['END_SENSITIVITY_HIGH', 'END_SENSITIVITY_LOW'], None]

class AgentCreateModel_SilenceConfig(TypedDict, total=False):
    enabled: Required[bool]
    timeout_ms: Required[int]
    action: Required[Literal['speak', 'think']]
    content: Required[str]

class AgentCreateModel_SpeechInterruption(TypedDict, total=False):
    mode: Required[Literal['start_of_speech']]

class AgentCreateModel_StaticFillerContent(TypedDict, total=False):
    mode: Required[Literal['static']]
    phrases: Required[List[str]]
    selection_rule: Literal['shuffle', 'round_robin']

class AgentCreateModel_TextGreeting(TypedDict, total=False):
    mode: Required[Literal['text']]
    on: Literal['each_join', 'first_join']
    delay_ms: int
    text: Required[str]

class AgentCreateModel_TurnDetection(TypedDict, total=False):
    speech_threshold: Union[float, int, None]
    start_of_speech: Union[Union['AgentCreateModel_SemanticTurnStart', 'AgentCreateModel_VadTurnStart', 'AgentCreateModel_ManualTurnBoundary'], None]
    end_of_speech: Union[Union['AgentCreateModel_SemanticTurnEnd', 'AgentCreateModel_VadTurnEnd', 'AgentCreateModel_ManualTurnBoundary'], None]
    interruption: Union[Union['AgentCreateModel_SpeechInterruption', 'AgentCreateModel_KeywordInterruption', 'AgentCreateModel_DisabledInterruption'], None]

class AgentCreateModel_VadTurnEnd(TypedDict, total=False):
    type: Required[Literal['vad']]
    silence_duration_ms: Union[int, None]

class AgentCreateModel_VadTurnStart(TypedDict, total=False):
    type: Required[Literal['vad']]
    interrupt_duration_ms: Union[int, None]
    speaking_interrupt_duration_ms: Union[int, None]
    prefix_padding_ms: Union[int, None]

class AgentCreateModel_VariableDefinition(TypedDict, total=False):
    type: Required[Literal['str', 'int', 'float', 'bool', 'date', 'datetime']]
    required: bool
    options: Union[List[Union[str, int, float, bool]], None]
    extract: bool
    description: Union[str, None]

class AgentCreateModel(TypedDict, total=False):
    agent_name: Required[str]
    instructions: Union[str, None]
    messages: Union[List['AgentCreateModel_Message'], None]
    greeting: Union[Union['AgentCreateModel_TextGreeting', 'AgentCreateModel_AudioGreeting'], None]
    variables: Union[Dict[str, 'AgentCreateModel_VariableDefinition'], None]
    pipeline: Union[Union['AgentCreateModel_CascadedPipeline', 'AgentCreateModel_RealtimePipeline'], None]
    filler_words: Union['AgentCreateModel_FillerWords', None]

class AgentPatchRequest_CredentialPatch(TypedDict, total=False):
    mode: Union[Literal['managed', 'byok'], None]
    api_key: Union[str, None]

class AgentPatchRequest_FillerContentPatch(TypedDict, total=False):
    mode: Union[Literal['static', 'generated'], None]
    phrases: Union[List[str], None]
    selection_rule: Union[Literal['shuffle', 'round_robin'], None]
    instructions: Union[str, None]
    fallback_strategy: Union[Literal['static'], None]

class AgentPatchRequest_FillerTriggerPatch(TypedDict, total=False):
    mode: Union[Literal['fixed_time'], None]
    response_wait_ms: Union[int, None]

class AgentPatchRequest_FillerWordsPatch(TypedDict, total=False):
    enable: Union[bool, None]
    trigger: Union['AgentPatchRequest_FillerTriggerPatch', None]
    content: Union['AgentPatchRequest_FillerContentPatch', None]

class AgentPatchRequest_GreetingPatch(TypedDict, total=False):
    mode: Union[Literal['text', 'audio'], None]
    on: Union[Literal['each_join', 'first_join'], None]
    delay_ms: Union[int, None]
    url: Union[str, None]
    text: Union[str, None]
    download_timeout_ms: Union[int, None]
    pcm_sample_rate: Union[int, None]

class AgentPatchRequest_InterruptionPatch(TypedDict, total=False):
    mode: Union[Literal['start_of_speech', 'keywords', 'off'], None]
    keywords: Union[List[str], None]
    when_off: Union[Literal['append', 'ignore'], None]

AgentPatchRequest_JsonValue = Any

class AgentPatchRequest_Message(TypedDict, total=False):
    role: Required[Literal['system', 'user', 'assistant']]
    content: Required[str]

class AgentPatchRequest_PipelinePatch(TypedDict, total=False):
    mode: Union[Literal['cascaded', 'realtime'], None]
    avatar: Union['AgentPatchRequest_ProviderModulePatch', None]
    turn_detection: Union['AgentPatchRequest_PipelineTurnDetectionPatch', None]
    asr: Union['AgentPatchRequest_ProviderModulePatch', None]
    tts: Union['AgentPatchRequest_ProviderModulePatch', None]
    llm: Union['AgentPatchRequest_ProviderModulePatch', None]
    mllm: Union['AgentPatchRequest_ProviderModulePatch', None]
    silence_config: Union['AgentPatchRequest_SilenceConfigPatch', None]

class AgentPatchRequest_PipelineTurnDetectionPatch(TypedDict, total=False):
    type: Union[Literal['agora_vad', 'server_vad', 'semantic_vad'], None]
    speech_threshold: Union[float, int, None]
    start_of_speech: Union['AgentPatchRequest_TurnBoundaryPatch', None]
    end_of_speech: Union['AgentPatchRequest_TurnBoundaryPatch', None]
    interruption: Union['AgentPatchRequest_InterruptionPatch', None]
    interrupt_duration_ms: Union[int, None]
    prefix_padding_ms: Union[int, None]
    silence_duration_ms: Union[int, None]
    threshold: Union[float, int, None]
    idle_timeout_ms: Union[int, None]
    start_of_speech_sensitivity: Union[Literal['START_SENSITIVITY_HIGH', 'START_SENSITIVITY_LOW'], None]
    end_of_speech_sensitivity: Union[Literal['END_SENSITIVITY_HIGH', 'END_SENSITIVITY_LOW'], None]
    eagerness: Union[Literal['auto', 'low', 'medium', 'high'], None]

class AgentPatchRequest_ProviderModulePatch(TypedDict, total=False):
    credential: Union['AgentPatchRequest_CredentialPatch', None]
    vendor: Union[str, None]
    model: Union[str, None]
    style: Union[str, None]
    language: Union[str, None]
    enabled: Union[bool, None]
    params: Union[Dict[str, 'AgentPatchRequest_JsonValue'], None]
    url: Union[str, None]
    headers: Union[Dict[str, str], None]
    input_modalities: Union[List[str], None]
    output_modalities: Union[List[str], None]
    max_history: Union[int, None]
    failure_message: Union[str, None]
    mcp_servers: Union[List[Dict[str, 'AgentPatchRequest_JsonValue']], None]
    tools: Union[List[Dict[str, 'AgentPatchRequest_JsonValue']], None]
    skip_patterns: Union[List[str], None]

class AgentPatchRequest_SilenceConfigPatch(TypedDict, total=False):
    enabled: Union[bool, None]
    timeout_ms: Union[int, None]
    action: Union[Literal['speak', 'think'], None]
    content: Union[str, None]

class AgentPatchRequest_TurnBoundaryPatch(TypedDict, total=False):
    type: Union[Literal['semantic', 'vad', 'manual'], None]
    interrupt_duration_ms: Union[int, None]
    speaking_interrupt_duration_ms: Union[int, None]
    prefix_padding_ms: Union[int, None]
    silence_duration_ms: Union[int, None]
    max_wait_ms: Union[int, None]
    pause_state_enabled: Union[bool, None]

class AgentPatchRequest_VariableDefinitionPatch(TypedDict, total=False):
    type: Union[Literal['str', 'int', 'float', 'bool', 'date', 'datetime'], None]
    required: Union[bool, None]
    options: Union[List[Union[str, int, float, bool]], None]
    extract: Union[bool, None]
    description: Union[str, None]

class AgentPatchRequest(TypedDict, total=False):
    agent_name: Union[str, None]
    instructions: Union[str, None]
    messages: Union[List['AgentPatchRequest_Message'], None]
    greeting: Union['AgentPatchRequest_GreetingPatch', None]
    variables: Union[Dict[str, Union['AgentPatchRequest_VariableDefinitionPatch', None]], None]
    pipeline: Union['AgentPatchRequest_PipelinePatch', None]
    filler_words: Union['AgentPatchRequest_FillerWordsPatch', None]

Contract_VariableDefinitions = Dict[str, 'Contract_VariableDefinition']

Contract_ModelCredential = Union[Dict[str, Any], Dict[str, Any]]

class Contract_Llm(TypedDict, total=False):
    credential: 'Contract_ModelCredential'
    url: str
    vendor: str
    style: str
    model: str
    params: Dict[str, Any]
    input_modalities: List[str]
    output_modalities: List[str]
    max_history: int
    failure_message: str
    mcp_servers: List['Contract_McpServer']
    tools: List['Contract_FunctionTool']
    headers: Dict[str, str]

class Contract_CascadedPipeline(TypedDict, total=False):
    mode: Required[Literal['cascaded']]
    avatar: 'Contract_Avatar'
    turn_detection: 'Contract_TurnDetection'
    asr: 'Contract_Asr'
    tts: 'Contract_Tts'
    llm: 'Contract_Llm'
    silence_config: 'Contract_SilenceConfig'

Contract_Pipeline = Union['Contract_CascadedPipeline', 'Contract_RealtimePipeline']

class Contract_SemanticVadTurnDetection(TypedDict, total=False):
    type: Required[Literal['semantic_vad']]
    eagerness: Literal['auto', 'low', 'medium', 'high']

class Contract_SilenceConfig(TypedDict, total=False):
    enabled: Required[bool]
    timeout_ms: Required[int]
    action: Required[Literal['speak', 'think']]
    content: Required[str]

class Contract_ServerVadTurnDetection(TypedDict, total=False):
    type: Required[Literal['server_vad']]
    prefix_padding_ms: int
    silence_duration_ms: int
    threshold: float
    idle_timeout_ms: int
    start_of_speech_sensitivity: Literal['START_SENSITIVITY_HIGH', 'START_SENSITIVITY_LOW']
    end_of_speech_sensitivity: Literal['END_SENSITIVITY_HIGH', 'END_SENSITIVITY_LOW']

class Contract_McpServer(TypedDict, total=False):
    name: Required[str]
    endpoint: Required[str]
    transport: Required[Literal['streamable_http']]
    headers: Dict[str, str]
    allowed_tools: List[str]
    timeout_ms: int

class Contract_VariableDefinition(TypedDict, total=False):
    type: Required[Literal['str', 'int', 'float', 'bool', 'date', 'datetime']]
    required: bool
    options: List[Union[str, float, bool]]
    extract: bool
    description: str

Contract_Greeting = Union[Dict[str, Any], Dict[str, Any]]

class Contract_Asr(TypedDict, total=False):
    credential: 'Contract_ModelCredential'
    url: str
    vendor: str
    model: str
    language: str
    params: Dict[str, Any]

class Contract_FillerWords(TypedDict, total=False):
    enable: bool
    trigger: Dict[str, Any]
    content: Union[Dict[str, Any], Dict[str, Any]]

Contract_Interruption = Union[Dict[str, Any], Dict[str, Any], Dict[str, Any]]

Contract_TurnStart = Union[Dict[str, Any], Dict[str, Any], Dict[str, Any]]

class Contract_FunctionTool(TypedDict, total=False):
    type: Required[Literal['function']]
    name: Required[str]
    description: Required[str]
    parameters: Required['Contract_JsonSchema']
    execution: Required['Contract_FunctionToolExecution']
    server: Required['Contract_FunctionToolServer']

class Contract_Tts(TypedDict, total=False):
    credential: 'Contract_ModelCredential'
    url: str
    headers: Dict[str, str]
    vendor: str
    params: Dict[str, Any]
    skip_patterns: List[Literal['fullwidth_parentheses', 'lenticular_brackets', 'parentheses', 'square_brackets', 'curly_braces']]

class Contract_RealtimePipeline(TypedDict, total=False):
    mode: Required[Literal['realtime']]
    avatar: 'Contract_Avatar'
    turn_detection: 'Contract_RealtimeTurnDetection'
    mllm: 'Contract_Mllm'

class Contract_Mllm(TypedDict, total=False):
    credential: 'Contract_ModelCredential'
    vendor: Required[str]
    model: str
    url: str
    params: Dict[str, Any]
    input_modalities: List[Literal['text', 'audio']]
    output_modalities: List[Literal['text', 'audio']]
    mcp_servers: List['Contract_McpServer']
    headers: Dict[str, str]

class Contract_Avatar(TypedDict, total=False):
    enabled: bool
    credential: 'Contract_ModelCredential'
    vendor: Literal['akool', 'liveavatar', 'anam', 'generic']
    params: Dict[str, Any]

Contract_RealtimeTurnDetection = Union['Contract_AgoraVadTurnDetection', 'Contract_ServerVadTurnDetection', 'Contract_SemanticVadTurnDetection']

class Contract_FunctionToolServer(TypedDict, total=False):
    method: Required[Literal['GET', 'POST']]
    url: Required[str]
    headers: Dict[str, str]
    body: Dict[str, Any]
    timeout_ms: int

Contract_TurnEnd = Union[Dict[str, Any], Dict[str, Any], Dict[str, Any]]

class Contract_Message(TypedDict, total=False):
    role: Required[Literal['system', 'user', 'assistant']]
    content: Required[str]

class Contract_AgentCreateInput(TypedDict, total=False):
    agent_name: Required[str]
    instructions: str
    messages: List['Contract_Message']
    greeting: 'Contract_Greeting'
    variables: 'Contract_VariableDefinitions'
    pipeline: 'Contract_Pipeline'
    filler_words: 'Contract_FillerWords'

class Contract_TurnDetection(TypedDict, total=False):
    speech_threshold: float
    start_of_speech: 'Contract_TurnStart'
    end_of_speech: 'Contract_TurnEnd'
    interruption: 'Contract_Interruption'

class Contract_AgoraVadTurnDetection(TypedDict, total=False):
    type: Required[Literal['agora_vad']]
    interrupt_duration_ms: int
    prefix_padding_ms: int
    silence_duration_ms: int
    threshold: float

class Contract_FunctionToolExecution(TypedDict, total=False):
    mode: Required[Literal['sync']]

Contract_JsonSchema = Union[Dict[str, Any], bool]

class AgentCreateRequest(TypedDict, total=False):
    agent_name: Required[str]
    instructions: Union[str, None]
    messages: Union[List['AgentCreateModel_Message'], None]
    greeting: Union[Union['AgentCreateModel_TextGreeting', 'AgentCreateModel_AudioGreeting'], None]
    variables: Union[Dict[str, 'AgentCreateModel_VariableDefinition'], None]
    pipeline: Union[Union['AgentCreateModel_CascadedPipeline', 'AgentCreateModel_RealtimePipeline'], None]
    filler_words: Union['AgentCreateModel_FillerWords', None]

__all__ = ['AgentDeleteResponse', 'AgentListData', 'AgentListItem', 'AgentListResponse', 'AgentResponse', 'AgoraVadTurnDetection', 'AudioGreeting', 'DisabledInterruption', 'EndCallPolicy', 'ErrorReason', 'ErrorResponse', 'FillerTrigger', 'FillerWords', 'GeneratedFillerContent', 'InboundCallPolicy', 'InboundInput', 'InboundOutput', 'JsonValue', 'KeywordInterruption', 'ManualTurnBoundary', 'Message', 'NumberCreate', 'NumberDeleteResponse', 'NumberListData', 'NumberListResponse', 'NumberPatch', 'NumberResponse', 'ResolvedAsr', 'ResolvedAvatar', 'ResolvedCascadedPipeline', 'ResolvedCredential', 'ResolvedLlm', 'ResolvedMllm', 'ResolvedRealtimePipeline', 'ResolvedTts', 'SecretCreate', 'SecretDeleted', 'SecretKey', 'SecretKeyWrite', 'SecretList', 'SecretPage', 'SecretReplace', 'SecretSet', 'SecretUpdate', 'SemanticTurnEnd', 'SemanticTurnStart', 'SemanticVadTurnDetection', 'ServerVadTurnDetection', 'SessionAnalysis', 'SessionData', 'SessionList', 'SessionResponse', 'SessionSummary', 'SilenceConfig', 'SipAuth', 'SipTrunkInput', 'SipTrunkOutput', 'SpeechInterruption', 'StaticFillerContent', 'TextGreeting', 'TransferPolicy', 'TurnDetection', 'VadTurnEnd', 'VadTurnStart', 'VariableDefinition', 'AgentCreateModel_AgoraVadTurnDetection', 'AgentCreateModel_AudioGreeting', 'AgentCreateModel_ByokCredential', 'AgentCreateModel_CascadedPipeline', 'AgentCreateModel_DisabledInterruption', 'AgentCreateModel_FillerTrigger', 'AgentCreateModel_FillerWords', 'AgentCreateModel_GeneratedFillerContent', 'AgentCreateModel_JsonValue', 'AgentCreateModel_KeywordInterruption', 'AgentCreateModel_ManagedCredential', 'AgentCreateModel_ManualTurnBoundary', 'AgentCreateModel_Message', 'AgentCreateModel_ProviderModule', 'AgentCreateModel_RealtimePipeline', 'AgentCreateModel_SemanticTurnEnd', 'AgentCreateModel_SemanticTurnStart', 'AgentCreateModel_SemanticVadTurnDetection', 'AgentCreateModel_ServerVadTurnDetection', 'AgentCreateModel_SilenceConfig', 'AgentCreateModel_SpeechInterruption', 'AgentCreateModel_StaticFillerContent', 'AgentCreateModel_TextGreeting', 'AgentCreateModel_TurnDetection', 'AgentCreateModel_VadTurnEnd', 'AgentCreateModel_VadTurnStart', 'AgentCreateModel_VariableDefinition', 'AgentCreateModel', 'AgentPatchRequest_CredentialPatch', 'AgentPatchRequest_FillerContentPatch', 'AgentPatchRequest_FillerTriggerPatch', 'AgentPatchRequest_FillerWordsPatch', 'AgentPatchRequest_GreetingPatch', 'AgentPatchRequest_InterruptionPatch', 'AgentPatchRequest_JsonValue', 'AgentPatchRequest_Message', 'AgentPatchRequest_PipelinePatch', 'AgentPatchRequest_PipelineTurnDetectionPatch', 'AgentPatchRequest_ProviderModulePatch', 'AgentPatchRequest_SilenceConfigPatch', 'AgentPatchRequest_TurnBoundaryPatch', 'AgentPatchRequest_VariableDefinitionPatch', 'AgentPatchRequest', 'Contract_VariableDefinitions', 'Contract_ModelCredential', 'Contract_Llm', 'Contract_CascadedPipeline', 'Contract_Pipeline', 'Contract_SemanticVadTurnDetection', 'Contract_SilenceConfig', 'Contract_ServerVadTurnDetection', 'Contract_McpServer', 'Contract_VariableDefinition', 'Contract_Greeting', 'Contract_Asr', 'Contract_FillerWords', 'Contract_Interruption', 'Contract_TurnStart', 'Contract_FunctionTool', 'Contract_Tts', 'Contract_RealtimePipeline', 'Contract_Mllm', 'Contract_Avatar', 'Contract_RealtimeTurnDetection', 'Contract_FunctionToolServer', 'Contract_TurnEnd', 'Contract_Message', 'Contract_AgentCreateInput', 'Contract_TurnDetection', 'Contract_AgoraVadTurnDetection', 'Contract_FunctionToolExecution', 'Contract_JsonSchema', 'AgentCreateRequest']