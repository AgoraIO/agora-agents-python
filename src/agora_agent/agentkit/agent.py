from __future__ import annotations

import time
import typing
import typing_extensions
import warnings

if typing.TYPE_CHECKING:
    from .agent_session import AgentSession, AsyncAgentSession
    from ..core.domain import Area
    from ..pool_client import Agora, AsyncAgora

from ..agents.types.start_agents_request_properties import StartAgentsRequestProperties
from ..agents.types.start_agents_request_properties_avatar import StartAgentsRequestPropertiesAvatar
from ..agents.types.start_agents_request_properties_avatar_vendor import StartAgentsRequestPropertiesAvatarVendor
from ..agents.types.update_agents_request_properties import UpdateAgentsRequestProperties
from ..agents.types.get_agents_response import GetAgentsResponse
from ..agents.types.list_agents_response import ListAgentsResponse
from ..agents.types.list_agents_response_data_list_item import ListAgentsResponseDataListItem
from ..agents.types.list_agents_response_data_list_item_status import ListAgentsResponseDataListItemStatus
from ..agents.types.get_history_agents_response import GetHistoryAgentsResponse
from ..agents.types.get_history_agents_response_contents_item import GetHistoryAgentsResponseContentsItem
from ..agents.types.get_history_agents_response_contents_item_role import GetHistoryAgentsResponseContentsItemRole
from ..agents.types.get_turns_agents_response import GetTurnsAgentsResponse
from ..agents.types.get_turns_agents_response_turns_item import GetTurnsAgentsResponseTurnsItem
from ..agents.types.speak_agents_request_priority import SpeakAgentsRequestPriority
from ..agents.types.start_agents_request_properties_turn_detection import StartAgentsRequestPropertiesTurnDetection
from ..agents.types.start_agents_request_properties_turn_detection_config import StartAgentsRequestPropertiesTurnDetectionConfig
from ..agents.types.start_agents_request_properties_turn_detection_config_start_of_speech import StartAgentsRequestPropertiesTurnDetectionConfigStartOfSpeech
from ..agents.types.start_agents_request_properties_turn_detection_config_start_of_speech_mode import StartAgentsRequestPropertiesTurnDetectionConfigStartOfSpeechMode
from ..agents.types.start_agents_request_properties_turn_detection_config_start_of_speech_vad_config import StartAgentsRequestPropertiesTurnDetectionConfigStartOfSpeechVadConfig
from ..agents.types.start_agents_request_properties_turn_detection_config_start_of_speech_keywords_config import StartAgentsRequestPropertiesTurnDetectionConfigStartOfSpeechKeywordsConfig
from ..agents.types.start_agents_request_properties_turn_detection_config_start_of_speech_disabled_config import StartAgentsRequestPropertiesTurnDetectionConfigStartOfSpeechDisabledConfig
from ..agents.types.start_agents_request_properties_turn_detection_config_start_of_speech_disabled_config_strategy import StartAgentsRequestPropertiesTurnDetectionConfigStartOfSpeechDisabledConfigStrategy
from ..agents.types.start_agents_request_properties_turn_detection_config_end_of_speech import StartAgentsRequestPropertiesTurnDetectionConfigEndOfSpeech
from ..agents.types.start_agents_request_properties_turn_detection_config_end_of_speech_mode import StartAgentsRequestPropertiesTurnDetectionConfigEndOfSpeechMode
from ..agents.types.start_agents_request_properties_turn_detection_config_end_of_speech_vad_config import StartAgentsRequestPropertiesTurnDetectionConfigEndOfSpeechVadConfig
from ..agents.types.start_agents_request_properties_turn_detection_config_end_of_speech_semantic_config import StartAgentsRequestPropertiesTurnDetectionConfigEndOfSpeechSemanticConfig
from ..agents.types.start_agents_request_properties_turn_detection_type import StartAgentsRequestPropertiesTurnDetectionType
from ..agents.types.start_agents_request_properties_turn_detection_interrupt_mode import StartAgentsRequestPropertiesTurnDetectionInterruptMode
from ..agents.types.start_agents_request_properties_turn_detection_eagerness import StartAgentsRequestPropertiesTurnDetectionEagerness
from ..agents.types.start_agents_request_properties_sal import StartAgentsRequestPropertiesSal
from ..agents.types.start_agents_request_properties_sal_sal_mode import StartAgentsRequestPropertiesSalSalMode
from ..agents.types.start_agents_request_properties_parameters import StartAgentsRequestPropertiesParameters
from ..agents.types.start_agents_request_properties_parameters_silence_config import StartAgentsRequestPropertiesParametersSilenceConfig
from ..agents.types.start_agents_request_properties_parameters_silence_config_action import StartAgentsRequestPropertiesParametersSilenceConfigAction
from ..agents.types.start_agents_request_properties_parameters_farewell_config import StartAgentsRequestPropertiesParametersFarewellConfig
from ..agents.types.start_agents_request_properties_parameters_data_channel import StartAgentsRequestPropertiesParametersDataChannel
from ..agents.types.start_agents_request_properties_parameters_audio_scenario import StartAgentsRequestPropertiesParametersAudioScenario
from ..agents.types.start_agents_request_properties_interruption import StartAgentsRequestPropertiesInterruption
from ..agents.types.start_agents_request_properties_interruption_mode import StartAgentsRequestPropertiesInterruptionMode
from ..agents.types.start_agents_request_properties_geofence import StartAgentsRequestPropertiesGeofence
from ..agents.types.start_agents_request_properties_rtc import StartAgentsRequestPropertiesRtc
from ..agents.types.start_agents_request_properties_advanced_features import StartAgentsRequestPropertiesAdvancedFeatures
from ..agents.types.start_agents_request_properties_filler_words import StartAgentsRequestPropertiesFillerWords
from ..agents.types.start_agents_request_properties_filler_words_trigger import StartAgentsRequestPropertiesFillerWordsTrigger
from ..agents.types.start_agents_request_properties_filler_words_trigger_fixed_time_config import StartAgentsRequestPropertiesFillerWordsTriggerFixedTimeConfig
from ..agents.types.start_agents_request_properties_filler_words_content import StartAgentsRequestPropertiesFillerWordsContent
from ..agents.types.start_agents_request_properties_filler_words_content_static_config import StartAgentsRequestPropertiesFillerWordsContentStaticConfig
from ..agents.types.start_agents_request_properties_filler_words_content_static_config_selection_rule import StartAgentsRequestPropertiesFillerWordsContentStaticConfigSelectionRule
from ..types.tts import Tts
from ..types.asr import Asr
from ..types.llm import Llm
from ..types.llm_style import LlmStyle as GeneratedLlmStyle
from ..types.mllm import Mllm
from ..types.mllm_turn_detection import MllmTurnDetection
from ..types.mllm_turn_detection_mode import MllmTurnDetectionMode as GeneratedMllmTurnDetectionMode
from ..types.mllm_vendor import MllmVendor as GeneratedMllmVendor
from ..agent_management.types.agent_think_agent_management_request_on_listening_action import (
    AgentThinkAgentManagementRequestOnListeningAction,
)
from ..agent_management.types.agent_think_agent_management_request_on_thinking_action import (
    AgentThinkAgentManagementRequestOnThinkingAction,
)
from ..agent_management.types.agent_think_agent_management_request_on_speaking_action import (
    AgentThinkAgentManagementRequestOnSpeakingAction,
)
from ..agent_management.types.agent_think_agent_management_response import (
    AgentThinkAgentManagementResponse,
)
from ..core.pydantic_utilities import parse_obj_as
from .vendors.base import BaseAvatar, BaseLLM, BaseMLLM, BaseSTT, BaseTTS

# Top-level aliases
LlmConfig = Llm
LlmStyle = GeneratedLlmStyle
SttConfig = Asr
AsrConfig = SttConfig
SttVendor = typing.Any
TtsConfig = Tts
MllmConfig = Mllm
MllmVendor = GeneratedMllmVendor
AvatarConfig = StartAgentsRequestPropertiesAvatar
AvatarVendor = StartAgentsRequestPropertiesAvatarVendor
TurnDetectionConfig = StartAgentsRequestPropertiesTurnDetection
SalConfig = StartAgentsRequestPropertiesSal
SalMode = StartAgentsRequestPropertiesSalSalMode
AdvancedFeatures = StartAgentsRequestPropertiesAdvancedFeatures
SessionParams = StartAgentsRequestPropertiesParameters

# SOS/EOS turn detection aliases (preferred)
TurnDetectionNestedConfig = StartAgentsRequestPropertiesTurnDetectionConfig
StartOfSpeechConfig = StartAgentsRequestPropertiesTurnDetectionConfigStartOfSpeech
StartOfSpeechMode = StartAgentsRequestPropertiesTurnDetectionConfigStartOfSpeechMode
StartOfSpeechVadConfig = StartAgentsRequestPropertiesTurnDetectionConfigStartOfSpeechVadConfig
StartOfSpeechKeywordsConfig = StartAgentsRequestPropertiesTurnDetectionConfigStartOfSpeechKeywordsConfig
StartOfSpeechDisabledConfig = StartAgentsRequestPropertiesTurnDetectionConfigStartOfSpeechDisabledConfig
StartOfSpeechDisabledConfigStrategy = StartAgentsRequestPropertiesTurnDetectionConfigStartOfSpeechDisabledConfigStrategy
EndOfSpeechConfig = StartAgentsRequestPropertiesTurnDetectionConfigEndOfSpeech
EndOfSpeechMode = StartAgentsRequestPropertiesTurnDetectionConfigEndOfSpeechMode
EndOfSpeechVadConfig = StartAgentsRequestPropertiesTurnDetectionConfigEndOfSpeechVadConfig
EndOfSpeechSemanticConfig = StartAgentsRequestPropertiesTurnDetectionConfigEndOfSpeechSemanticConfig

# Deprecated turn detection aliases
# Deprecated: Use TurnDetectionConfig with TurnDetectionNestedConfig.start_of_speech
# and .end_of_speech instead. The `type` field and agora_vad/server_vad/semantic_vad
# values will be removed in a future release.
TurnDetectionType = StartAgentsRequestPropertiesTurnDetectionType

# Deprecated: Use StartOfSpeechConfig with mode="vad"|"keywords"|"disabled" and the
# corresponding vad_config, keywords_config, or disabled_config instead.
InterruptMode = StartAgentsRequestPropertiesTurnDetectionInterruptMode

# Deprecated: Only applies to server_vad/semantic_vad modes with OpenAI Realtime
# (MLLM). Has no equivalent in the ASR + LLM + TTS pipeline.
Eagerness = StartAgentsRequestPropertiesTurnDetectionEagerness

# Parameters (SessionParams) sub-type aliases
SilenceConfig = StartAgentsRequestPropertiesParametersSilenceConfig
SilenceAction = StartAgentsRequestPropertiesParametersSilenceConfigAction
FarewellConfig = StartAgentsRequestPropertiesParametersFarewellConfig
ParametersDataChannel = StartAgentsRequestPropertiesParametersDataChannel
ParametersAudioScenario = StartAgentsRequestPropertiesParametersAudioScenario
InterruptionConfig = StartAgentsRequestPropertiesInterruption
InterruptionMode = StartAgentsRequestPropertiesInterruptionMode
MllmTurnDetectionConfig = MllmTurnDetection
MllmTurnDetectionMode = GeneratedMllmTurnDetectionMode
AgentConfig = StartAgentsRequestProperties
AgentConfigUpdate = UpdateAgentsRequestProperties
SessionInfo = GetAgentsResponse
SessionListResponse = ListAgentsResponse
SessionSummary = ListAgentsResponseDataListItem
SessionStatus = ListAgentsResponseDataListItemStatus
ConversationHistory = GetHistoryAgentsResponse
ConversationTurn = GetHistoryAgentsResponseContentsItem
ConversationRole = GetHistoryAgentsResponseContentsItemRole
ConversationTurns = GetTurnsAgentsResponse
ConversationSessionTurn = GetTurnsAgentsResponseTurnsItem
SpeakPriority = SpeakAgentsRequestPriority
Labels = typing.Dict[str, str]


class SessionParamsInput(typing_extensions.TypedDict, total=False):
    silence_config: StartAgentsRequestPropertiesParametersSilenceConfig
    farewell_config: StartAgentsRequestPropertiesParametersFarewellConfig
    data_channel: StartAgentsRequestPropertiesParametersDataChannel
    enable_metrics: bool
    enable_error_message: bool
    audio_scenario: ParametersAudioScenario


class ThinkOptions(typing_extensions.TypedDict, total=False):
    on_listening_action: AgentThinkAgentManagementRequestOnListeningAction
    on_thinking_action: AgentThinkAgentManagementRequestOnThinkingAction
    on_speaking_action: AgentThinkAgentManagementRequestOnSpeakingAction
    interruptable: bool
    metadata: typing.Dict[str, str]


class GetTurnsOptions(typing_extensions.TypedDict, total=False):
    page_index: int
    page_size: int


class SayOptions(typing_extensions.TypedDict, total=False):
    priority: SpeakAgentsRequestPriority
    interruptable: bool


class SessionOptions(typing_extensions.TypedDict, total=False):
    """Options accepted by :meth:`Agent.create_session` and :meth:`Agent.create_async_session`."""

    name: str  # Agent instance name sent to the Start Agent API; defaults to agent-{timestamp} when omitted.
    channel: str
    token: str
    agent_uid: str
    remote_uids: typing.List[str]
    idle_timeout: int
    enable_string_uid: bool
    preset: typing.Union[str, typing.Sequence[str]]
    pipeline_id: str
    expires_in: int
    debug: bool
    warn: typing.Callable[[str], None]


def _start_properties_from_mapping(
    properties: typing.Mapping[str, typing.Any],
) -> StartAgentsRequestProperties:
    return parse_obj_as(StartAgentsRequestProperties, dict(properties))


# LLM sub-type aliases
LlmGreetingConfigs = typing.Dict[str, typing.Any]
LlmGreetingConfigsMode = typing.Any
McpServersItem = typing.Dict[str, typing.Any]

# Additional top-level config aliases
GeofenceConfig = StartAgentsRequestPropertiesGeofence
RtcConfig = StartAgentsRequestPropertiesRtc
FillerWordsConfig = StartAgentsRequestPropertiesFillerWords
FillerWordsTrigger = StartAgentsRequestPropertiesFillerWordsTrigger
FillerWordsTriggerFixedTimeConfig = StartAgentsRequestPropertiesFillerWordsTriggerFixedTimeConfig
FillerWordsContent = StartAgentsRequestPropertiesFillerWordsContent
FillerWordsContentStaticConfig = StartAgentsRequestPropertiesFillerWordsContentStaticConfig
FillerWordsContentSelectionRule = StartAgentsRequestPropertiesFillerWordsContentStaticConfigSelectionRule

# Think type aliases and response
ThinkOnListeningAction = AgentThinkAgentManagementRequestOnListeningAction
ThinkOnThinkingAction = AgentThinkAgentManagementRequestOnThinkingAction
ThinkOnSpeakingAction = AgentThinkAgentManagementRequestOnSpeakingAction
ThinkResponse = AgentThinkAgentManagementResponse

from .token import generate_convo_ai_token, _parse_numeric_uid, _validate_expires_in

TurnDetectionLanguage = typing_extensions.Literal[
    "ar-EG",
    "ar-JO",
    "ar-SA",
    "ar-AE",
    "bn-IN",
    "zh-CN",
    "zh-HK",
    "zh-TW",
    "nl-NL",
    "en-IN",
    "en-US",
    "fil-PH",
    "fr-FR",
    "de-DE",
    "gu-IN",
    "he-IL",
    "hi-IN",
    "id-ID",
    "it-IT",
    "ja-JP",
    "kn-IN",
    "ko-KR",
    "ms-MY",
    "fa-IR",
    "pt-PT",
    "ru-RU",
    "es-ES",
    "ta-IN",
    "te-IN",
    "th-TH",
    "tr-TR",
    "vi-VN",
]

DEFAULT_TURN_DETECTION_LANGUAGE: TurnDetectionLanguage = "en-US"
TURN_DETECTION_LANGUAGE_VALUES: typing.Tuple[TurnDetectionLanguage, ...] = (
    "ar-EG",
    "ar-JO",
    "ar-SA",
    "ar-AE",
    "bn-IN",
    "zh-CN",
    "zh-HK",
    "zh-TW",
    "nl-NL",
    "en-IN",
    "en-US",
    "fil-PH",
    "fr-FR",
    "de-DE",
    "gu-IN",
    "he-IL",
    "hi-IN",
    "id-ID",
    "it-IT",
    "ja-JP",
    "kn-IN",
    "ko-KR",
    "ms-MY",
    "fa-IR",
    "pt-PT",
    "ru-RU",
    "es-ES",
    "ta-IN",
    "te-IN",
    "th-TH",
    "tr-TR",
    "vi-VN",
)
_TURN_DETECTION_LANGUAGES = set(TURN_DETECTION_LANGUAGE_VALUES)


def _dump_optional_model(value: typing.Any) -> typing.Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(exclude_none=True)
    if hasattr(value, "dict"):
        return value.dict(exclude_none=True)
    return value


def _is_turn_detection_language(value: typing.Any) -> bool:
    return isinstance(value, str) and value in _TURN_DETECTION_LANGUAGES


def _validate_turn_detection_language(value: typing.Any) -> TurnDetectionLanguage:
    if not _is_turn_detection_language(value):
        raise ValueError(f"Invalid turn_detection.language: {value}")
    return value  # type: ignore[return-value]


class Agent:
    """A reusable agent definition.

    Use the fluent builder methods (.with_llm(), .with_tts(), .with_stt(), .with_mllm())
    to configure vendor settings after construction. Every ``Agent`` must be
    constructed with a bound ``Agora`` or ``AsyncAgora`` client via
    ``Agent(client=client, ...)``.

    The agent instance name is **not** configured on ``Agent``. Pass it when creating
    a session via :meth:`create_session` / :meth:`create_async_session` ``name=...``.

    Deprecated:
        The Agent-level ``instructions``, ``greeting``, ``failure_message``,
        ``max_history``, and ``greeting_configs`` convenience fields are kept
        for compatibility. Configure those values on the LLM or MLLM vendor
        instead.

    Examples
    --------
    >>> from agora_agent import Agent, Agora, Area, OpenAI, ElevenLabsTTS, DeepgramSTT
    >>>
    >>> client = Agora(area=Area.US, app_id="...", app_certificate="...")
    >>> agent = (
    ...     Agent(client=client, instructions="You are a helpful voice assistant.")
    ...     .with_llm(OpenAI(api_key="...", base_url="https://api.openai.com/v1/chat/completions", model="gpt-4"))
    ...     .with_tts(ElevenLabsTTS(key="...", model_id="...", voice_id="...", base_url="wss://api.elevenlabs.io/v1", sample_rate=24000))
    ...     .with_stt(DeepgramSTT(api_key="...", model="nova-2"))
    ... )
    >>> session = agent.create_session(
    ...     channel="room-123",
    ...     agent_uid="1",
    ...     remote_uids=["100"],
    ...     name="assistant",
    ... )
    """

    if typing.TYPE_CHECKING:
        _GlobalArea = typing_extensions.Literal[Area.US, Area.EU, Area.AP]

        @typing.overload
        def __new__(
            cls,
            client: "Agora[typing_extensions.Literal[Area.CN]]",
            *args: typing.Any,
            **kwargs: typing.Any,
        ) -> "CNAgent":
            ...

        @typing.overload
        def __new__(
            cls,
            client: "Agora[_GlobalArea]",
            *args: typing.Any,
            **kwargs: typing.Any,
        ) -> "GlobalAgent":
            ...

        @typing.overload
        def __new__(
            cls,
            client: "AsyncAgora[typing_extensions.Literal[Area.CN]]",
            *args: typing.Any,
            **kwargs: typing.Any,
        ) -> "CNAgent":
            ...

        @typing.overload
        def __new__(
            cls,
            client: "AsyncAgora[_GlobalArea]",
            *args: typing.Any,
            **kwargs: typing.Any,
        ) -> "GlobalAgent":
            ...

        @typing.overload
        def __new__(
            cls,
            client: typing.Any,
            *args: typing.Any,
            **kwargs: typing.Any,
        ) -> "Agent":
            ...

    def __new__(
        cls,
        client: typing.Any = None,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> "Agent":
        if client is None:
            raise TypeError("client is required. Pass client=... to Agent(...).")
        if cls is Agent:
            area_scope = getattr(client, "area_scope", None)
            if area_scope == "cn":
                from .regional_agent import CNAgent

                cls = CNAgent
            elif area_scope == "global":
                from .regional_agent import GlobalAgent

                cls = GlobalAgent
        return typing.cast("Agent", super().__new__(cls))

    def __init__(
        self,
        client: typing.Any,
        instructions: typing.Optional[str] = None,
        turn_detection: typing.Optional[TurnDetectionConfig] = None,
        interruption: typing.Optional[InterruptionConfig] = None,
        sal: typing.Optional[SalConfig] = None,
        advanced_features: typing.Optional[AdvancedFeatures] = None,
        parameters: typing.Optional[typing.Union[SessionParams, SessionParamsInput]] = None,
        greeting: typing.Optional[str] = None,
        failure_message: typing.Optional[str] = None,
        max_history: typing.Optional[int] = None,
        geofence: typing.Optional[GeofenceConfig] = None,
        labels: typing.Optional[typing.Dict[str, str]] = None,
        rtc: typing.Optional[RtcConfig] = None,
        filler_words: typing.Optional[FillerWordsConfig] = None,
        greeting_configs: typing.Optional[LlmGreetingConfigs] = None,
        pipeline_id: typing.Optional[str] = None,
    ):
        if client is None:
            raise TypeError("client is required. Pass client=... to Agent(...).")
        self._client = client
        self._pipeline_id = pipeline_id
        self._instructions = instructions
        self._greeting = greeting
        self._failure_message = failure_message
        self._max_history = max_history
        self._llm: typing.Optional[typing.Dict[str, typing.Any]] = None
        self._tts: typing.Optional[typing.Dict[str, typing.Any]] = None
        self._stt: typing.Optional[typing.Dict[str, typing.Any]] = None
        self._mllm: typing.Optional[typing.Dict[str, typing.Any]] = None
        self._tts_sample_rate: typing.Optional[int] = None
        self._avatar: typing.Optional[typing.Dict[str, typing.Any]] = None
        self._avatar_required_sample_rate: typing.Optional[int] = None
        self._turn_detection = turn_detection
        self._interruption = interruption
        self._sal = sal
        self._advanced_features = advanced_features
        self._parameters = parameters
        self._geofence = geofence
        self._labels = labels
        self._rtc = rtc
        self._filler_words = filler_words
        self._greeting_configs = greeting_configs

    def with_llm(self, vendor: BaseLLM) -> "Agent":
        config = vendor.to_config()
        new_agent = self._clone()
        new_agent._llm = config
        return new_agent

    def with_tts(self, vendor: BaseTTS) -> "Agent":
        sample_rate = vendor.sample_rate
        if (
            self._avatar_required_sample_rate not in (None, 0)
            and sample_rate is not None
            and sample_rate != self._avatar_required_sample_rate
        ):
            raise ValueError(
                f"Avatar requires TTS sample rate of {self._avatar_required_sample_rate} Hz, "
                f"but TTS is configured with {sample_rate} Hz. "
                f"Please update your TTS sample_rate to {self._avatar_required_sample_rate}."
            )
        config = vendor.to_config()
        new_agent = self._clone()
        new_agent._tts = config
        new_agent._tts_sample_rate = sample_rate
        return new_agent

    def with_stt(self, vendor: BaseSTT) -> "Agent":
        config = vendor.to_config()
        new_agent = self._clone()
        new_agent._stt = config
        return new_agent

    def with_mllm(self, vendor: BaseMLLM) -> "Agent":
        # Note: avatars are not supported with MLLM. The combination is rejected
        # at ``to_properties`` / ``AgentSession.start`` so callers can still
        # configure both for tests, debugging, or disabled-avatar use cases.
        new_agent = self._clone()
        new_agent._mllm = vendor.to_config()
        if isinstance(new_agent._mllm, dict):
            new_agent._mllm["enable"] = True
        if isinstance(new_agent._advanced_features, dict):
            advanced_features = {key: value for key, value in new_agent._advanced_features.items() if key != "enable_mllm"}
            new_agent._advanced_features = typing.cast(AdvancedFeatures, advanced_features) if advanced_features else None
        elif isinstance(new_agent._advanced_features, StartAgentsRequestPropertiesAdvancedFeatures):
            advanced_features_model = self._copy_model_update(
                new_agent._advanced_features,
                {"enable_mllm": None},
            )
            if (
                advanced_features_model.enable_rtm is None
                and advanced_features_model.enable_sal is None
                and advanced_features_model.enable_tools is None
            ):
                new_agent._advanced_features = None
            else:
                new_agent._advanced_features = advanced_features_model
        return new_agent

    def with_avatar(self, vendor: BaseAvatar) -> "Agent":
        # Note: avatars are not supported with MLLM. The combination is rejected
        # at ``to_properties`` / ``AgentSession.start`` (only when the avatar is
        # enabled) so callers may still combine the two for testing or for the
        # disabled-avatar pattern.
        required_sample_rate = vendor.required_sample_rate
        if (
            required_sample_rate not in (None, 0)
            and self._tts_sample_rate is not None
            and self._tts_sample_rate != required_sample_rate
        ):
            raise ValueError(
                f"Avatar requires TTS sample rate of {required_sample_rate} Hz, "
                f"but TTS is configured with {self._tts_sample_rate} Hz. "
                f"Please update your TTS sample_rate to {required_sample_rate}."
            )
        config = vendor.to_config()
        new_agent = self._clone()
        new_agent._avatar = config
        new_agent._avatar_required_sample_rate = required_sample_rate
        return new_agent

    def with_turn_detection(self, config: TurnDetectionConfig) -> "Agent":
        new_agent = self._clone()
        new_agent._turn_detection = config
        return new_agent

    def with_interruption(self, config: InterruptionConfig) -> "Agent":
        """Returns a new Agent with unified interruption control configured."""
        new_agent = self._clone()
        new_agent._interruption = config
        return new_agent

    def with_instructions(self, instructions: str) -> "Agent":
        """Deprecated. Configure system messages on the LLM vendor instead."""
        new_agent = self._clone()
        new_agent._instructions = instructions
        return new_agent

    def with_greeting(self, greeting: str) -> "Agent":
        """Deprecated. Configure the greeting on the LLM or MLLM vendor instead."""
        new_agent = self._clone()
        new_agent._greeting = greeting
        return new_agent

    def with_greeting_configs(self, configs: LlmGreetingConfigs) -> "Agent":
        """Deprecated. Configure greeting playback on the LLM vendor instead."""
        new_agent = self._clone()
        new_agent._greeting_configs = configs
        return new_agent

    def with_sal(self, config: SalConfig) -> "Agent":
        """Returns a new Agent with the specified SAL (Selective Attention Locking) configuration."""
        new_agent = self._clone()
        new_agent._sal = config
        return new_agent

    def with_advanced_features(self, features: AdvancedFeatures) -> "Agent":
        """Returns a new Agent with the specified advanced features configuration.

        Use this to enable RTM and other advanced features.
        """
        new_agent = self._clone()
        new_agent._advanced_features = features
        return new_agent

    def with_tools(self, enabled: bool = True) -> "Agent":
        """Returns a new Agent with MCP tool invocation enabled or disabled."""
        new_agent = self._clone()
        if new_agent._advanced_features is None:
            new_agent._advanced_features = StartAgentsRequestPropertiesAdvancedFeatures(enable_tools=enabled)
        elif isinstance(new_agent._advanced_features, dict):
            new_agent._advanced_features = typing.cast(
                AdvancedFeatures,
                {**new_agent._advanced_features, "enable_tools": enabled},
            )
        else:
            new_agent._advanced_features = self._copy_model_update(
                new_agent._advanced_features,
                {"enable_tools": enabled},
            )
        return new_agent

    def with_parameters(self, parameters: typing.Union[SessionParams, SessionParamsInput]) -> "Agent":
        """Returns a new Agent with the specified session parameters.

        Use this to configure silence behaviour, graceful hang-up, data channel, and more.
        """
        new_agent = self._clone()
        new_agent._parameters = parameters
        return new_agent

    def with_audio_scenario(self, audio_scenario: ParametersAudioScenario) -> "Agent":
        """Returns a new Agent with the specified RTC audio scenario."""
        new_agent = self._clone()
        if new_agent._parameters is None:
            new_agent._parameters = StartAgentsRequestPropertiesParameters(audio_scenario=audio_scenario)
        elif isinstance(new_agent._parameters, dict):
            new_agent._parameters = typing.cast(
                SessionParamsInput,
                {**new_agent._parameters, "audio_scenario": audio_scenario},
            )
        else:
            new_agent._parameters = self._copy_model_update(
                new_agent._parameters,
                {"audio_scenario": audio_scenario},
            )
        return new_agent

    def with_failure_message(self, message: str) -> "Agent":
        """Deprecated. Configure the failure message on the LLM or MLLM vendor instead."""
        new_agent = self._clone()
        new_agent._failure_message = message
        return new_agent

    def with_max_history(self, max_history: int) -> "Agent":
        """Deprecated. Configure max history on the LLM vendor instead."""
        new_agent = self._clone()
        new_agent._max_history = max_history
        return new_agent

    def with_geofence(self, geofence: GeofenceConfig) -> "Agent":
        """Returns a new Agent with the specified geofence configuration.

        Restricts which geographic regions the agent's backend servers may run in.
        """
        new_agent = self._clone()
        new_agent._geofence = geofence
        return new_agent

    def with_labels(self, labels: typing.Dict[str, str]) -> "Agent":
        """Returns a new Agent with the specified custom labels.

        Labels are key-value pairs attached to the agent and returned in notification callbacks.
        """
        new_agent = self._clone()
        new_agent._labels = dict(labels)
        return new_agent

    def with_rtc(self, rtc: RtcConfig) -> "Agent":
        """Returns a new Agent with the specified RTC configuration."""
        new_agent = self._clone()
        new_agent._rtc = rtc
        return new_agent

    def with_filler_words(self, filler_words: FillerWordsConfig) -> "Agent":
        """Returns a new Agent with the specified filler words configuration.

        Filler words are played while the agent waits for the LLM to respond.
        """
        new_agent = self._clone()
        new_agent._filler_words = filler_words
        return new_agent

    @staticmethod
    def _field_value(value: typing.Any, field: str) -> typing.Any:
        if value is None:
            return None
        if isinstance(value, dict):
            return value.get(field)
        return getattr(value, field, None)

    @staticmethod
    def _copy_model_update(value: typing.Any, update: typing.Dict[str, typing.Any]) -> typing.Any:
        if hasattr(value, "model_copy"):
            return value.model_copy(update=update)
        if hasattr(value, "copy"):
            return value.copy(update=update)
        raise TypeError(f"Object of type {type(value).__name__} does not support model copying")

    def _resolved_parameters(self) -> typing.Optional[typing.Union[SessionParams, SessionParamsInput]]:
        parameters = self._parameters
        updates: typing.Dict[str, typing.Any] = {}

        enable_rtm = self._field_value(self._advanced_features, "enable_rtm") is True
        if enable_rtm and self._field_value(parameters, "data_channel") is None:
            updates["data_channel"] = "rtm"
        if self._field_value(parameters, "audio_scenario") is None:
            updates["audio_scenario"] = "default"

        if not updates:
            return parameters
        if parameters is None:
            return StartAgentsRequestPropertiesParameters(**updates)
        if isinstance(parameters, dict):
            return typing.cast(SessionParamsInput, {**parameters, **updates})
        return self._copy_model_update(parameters, updates)

    @property
    def pipeline_id(self) -> typing.Optional[str]:
        """Published AI Studio pipeline ID used as this agent's base configuration."""
        return self._pipeline_id

    @property
    def llm(self) -> typing.Optional[typing.Dict[str, typing.Any]]:
        return self._llm

    @property
    def tts(self) -> typing.Optional[typing.Dict[str, typing.Any]]:
        return self._tts

    @property
    def tts_sample_rate(self) -> typing.Optional[int]:
        return self._tts_sample_rate

    @property
    def stt(self) -> typing.Optional[typing.Dict[str, typing.Any]]:
        return self._stt

    @property
    def mllm(self) -> typing.Optional[typing.Dict[str, typing.Any]]:
        return self._mllm

    @property
    def turn_detection(self) -> typing.Optional[TurnDetectionConfig]:
        return self._turn_detection

    @property
    def interruption(self) -> typing.Optional[InterruptionConfig]:
        return self._interruption

    @property
    def instructions(self) -> typing.Optional[str]:
        return self._instructions

    @property
    def greeting(self) -> typing.Optional[str]:
        return self._greeting

    @property
    def greeting_configs(self) -> typing.Optional[LlmGreetingConfigs]:
        return self._greeting_configs

    @property
    def failure_message(self) -> typing.Optional[str]:
        return self._failure_message

    @property
    def max_history(self) -> typing.Optional[int]:
        return self._max_history

    @property
    def avatar(self) -> typing.Optional[typing.Dict[str, typing.Any]]:
        return self._avatar

    @property
    def sal(self) -> typing.Optional[SalConfig]:
        return self._sal

    @property
    def advanced_features(self) -> typing.Optional[AdvancedFeatures]:
        return self._advanced_features

    @property
    def parameters(self) -> typing.Optional[typing.Union[SessionParams, SessionParamsInput]]:
        return self._parameters

    @property
    def geofence(self) -> typing.Optional[GeofenceConfig]:
        return self._geofence

    @property
    def labels(self) -> typing.Optional[typing.Dict[str, str]]:
        return self._labels

    @property
    def rtc(self) -> typing.Optional[RtcConfig]:
        return self._rtc

    @property
    def filler_words(self) -> typing.Optional[FillerWordsConfig]:
        return self._filler_words

    @property
    def config(self) -> typing.Dict[str, typing.Any]:
        """Read-only snapshot of the agent builder configuration.

        Session-scoped fields such as the Start Agent API ``name`` are not included;
        set those on :meth:`create_session`.
        """
        return {
            "pipeline_id": self._pipeline_id,
            "instructions": self._instructions,
            "greeting": self._greeting,
            "failure_message": self._failure_message,
            "max_history": self._max_history,
            "llm": self._llm,
            "tts": self._tts,
            "stt": self._stt,
            "mllm": self._mllm,
            "turn_detection": self._turn_detection,
            "interruption": self._interruption,
            "sal": self._sal,
            "avatar": self._avatar,
            "advanced_features": self._advanced_features,
            "parameters": self._parameters,
            "geofence": self._geofence,
            "labels": self._labels,
            "rtc": self._rtc,
            "filler_words": self._filler_words,
            "greeting_configs": self._greeting_configs,
        }

    def create_session(
        self,
        channel: str,
        agent_uid: str,
        remote_uids: typing.List[str],
        name: typing.Optional[str] = None,
        token: typing.Optional[str] = None,
        idle_timeout: typing.Optional[int] = None,
        enable_string_uid: typing.Optional[bool] = None,
        preset: typing.Optional[typing.Union[str, typing.Sequence[str]]] = None,
        pipeline_id: typing.Optional[str] = None,
        expires_in: typing.Optional[int] = None,
        debug: typing.Optional[bool] = None,
        warn: typing.Optional[typing.Callable[[str], None]] = None,
    ) -> "AgentSession":
        """Create a synchronous session bound to this agent configuration.

        Parameters
        ----------
        channel, agent_uid, remote_uids
            Required RTC join settings.
        name
            Agent instance name sent to the Start Agent API. When omitted, the SDK
            generates ``agent-{timestamp}``.
        token, idle_timeout, enable_string_uid, preset, pipeline_id, expires_in, debug, warn
            Optional session overrides documented on :class:`AgentSession`.
        """
        from .agent_session import AgentSession

        resolved_client = self._client
        if resolved_client is None:
            raise ValueError("client is required. Pass client=... to Agent(...).")

        session_name = name or f"agent-{int(time.time())}"
        return AgentSession(
            client=resolved_client,
            agent=self,
            app_id=resolved_client.app_id if hasattr(resolved_client, "app_id") else "",
            app_certificate=resolved_client.app_certificate if hasattr(resolved_client, "app_certificate") else None,
            name=session_name,
            channel=channel,
            token=token,
            agent_uid=agent_uid,
            remote_uids=remote_uids,
            idle_timeout=idle_timeout,
            enable_string_uid=enable_string_uid,
            preset=preset,
            pipeline_id=pipeline_id,
            expires_in=expires_in,
            debug=debug,
            warn=warn,
        )

    def create_async_session(
        self,
        channel: str,
        agent_uid: str,
        remote_uids: typing.List[str],
        name: typing.Optional[str] = None,
        token: typing.Optional[str] = None,
        idle_timeout: typing.Optional[int] = None,
        enable_string_uid: typing.Optional[bool] = None,
        preset: typing.Optional[typing.Union[str, typing.Sequence[str]]] = None,
        pipeline_id: typing.Optional[str] = None,
        expires_in: typing.Optional[int] = None,
        debug: typing.Optional[bool] = None,
        warn: typing.Optional[typing.Callable[[str], None]] = None,
    ) -> "AsyncAgentSession":
        """Create an async session for use with :class:`~agora_agent.AsyncAgora`.

        Equivalent to :meth:`create_session` but returns an
        :class:`~agora_agent.agentkit.AsyncAgentSession`. Pass the agent instance
        name via ``name=...``; when omitted, the SDK generates ``agent-{timestamp}``.
        """
        from .agent_session import AsyncAgentSession

        resolved_client = self._client
        if resolved_client is None:
            raise ValueError("client is required. Pass client=... to Agent(...).")

        session_name = name or f"agent-{int(time.time())}"
        return AsyncAgentSession(
            client=resolved_client,
            agent=self,
            app_id=resolved_client.app_id if hasattr(resolved_client, "app_id") else "",
            app_certificate=resolved_client.app_certificate if hasattr(resolved_client, "app_certificate") else None,
            name=session_name,
            channel=channel,
            token=token,
            agent_uid=agent_uid,
            remote_uids=remote_uids,
            idle_timeout=idle_timeout,
            enable_string_uid=enable_string_uid,
            preset=preset,
            pipeline_id=pipeline_id,
            expires_in=expires_in,
            debug=debug,
            warn=warn,
        )

    def to_properties(
        self,
        channel: str,
        agent_uid: str,
        remote_uids: typing.List[str],
        idle_timeout: typing.Optional[int] = None,
        enable_string_uid: typing.Optional[bool] = None,
        token: typing.Optional[str] = None,
        app_id: typing.Optional[str] = None,
        app_certificate: typing.Optional[str] = None,
        expires_in: typing.Optional[int] = None,
        skip_vendor_validation: bool = False,
        skip_vendor_validation_categories: typing.Optional[typing.AbstractSet[str]] = None,
        allow_missing_vendor_categories: typing.Optional[typing.AbstractSet[str]] = None,
    ) -> StartAgentsRequestProperties:
        # Validate the MLLM + enabled-avatar combination BEFORE generating the
        # RTC token so callers get a clear, actionable error first (matches the
        # TypeScript and Go SDKs' fail-fast contract).
        mllm_flag = isinstance(self._mllm, dict) and self._mllm.get("enable") is True
        is_mllm_mode = bool(mllm_flag or self._mllm is not None)
        avatar_enabled = (
            isinstance(self._avatar, dict) and self._avatar.get("enable") is not False
        )
        if is_mllm_mode and avatar_enabled:
            raise ValueError(
                "Avatars are only supported with the cascading ASR + LLM + TTS pipeline. "
                "Remove the avatar configuration when using MLLM, or switch to a cascading session."
            )

        if token is None:
            if app_id is None or app_certificate is None:
                raise ValueError("Either token or app_id+app_certificate must be provided")
            validated_expires_in = _validate_expires_in(expires_in) if expires_in is not None else None
            # Use generate_convo_ai_token (RTC + RTM) so the token works whether or
            # not the caller enables advanced_features.enable_rtm.
            token_kwargs: typing.Dict[str, typing.Any] = {}
            if validated_expires_in is not None:
                token_kwargs["token_expire"] = validated_expires_in
            token = generate_convo_ai_token(
                app_id=app_id,
                app_certificate=app_certificate,
                channel_name=channel,
                uid=_parse_numeric_uid(agent_uid, "agent_uid"),
                **token_kwargs,
            )

        base_kwargs: typing.Dict[str, typing.Any] = {
            "channel": channel,
            "token": token,
            "agent_rtc_uid": agent_uid,
            "remote_rtc_uids": remote_uids,
        }

        if idle_timeout is not None:
            base_kwargs["idle_timeout"] = idle_timeout
        if enable_string_uid is not None:
            base_kwargs["enable_string_uid"] = enable_string_uid
        if self._mllm is not None:
            base_kwargs["mllm"] = self._mllm
        if self._turn_detection is not None:
            base_kwargs["turn_detection"] = self._turn_detection
        if self._interruption is not None:
            base_kwargs["interruption"] = self._interruption
        if self._sal is not None:
            base_kwargs["sal"] = self._sal
        if self._avatar is not None:
            base_kwargs["avatar"] = self._avatar
        if self._advanced_features is not None:
            base_kwargs["advanced_features"] = self._advanced_features
        parameters = self._resolved_parameters()
        if parameters is not None:
            if isinstance(parameters, dict):
                base_kwargs["parameters"] = StartAgentsRequestPropertiesParameters(**parameters)
            else:
                base_kwargs["parameters"] = parameters
        if self._geofence is not None:
            base_kwargs["geofence"] = self._geofence
        if self._labels is not None:
            base_kwargs["labels"] = self._labels
        if self._rtc is not None:
            base_kwargs["rtc"] = self._rtc
        if self._filler_words is not None:
            base_kwargs["filler_words"] = self._filler_words

        if is_mllm_mode:
            if self._mllm is not None:
                mllm_config = dict(self._mllm)
                if self._greeting is not None:
                    mllm_config.setdefault("greeting_message", self._greeting)
                if self._failure_message is not None:
                    mllm_config.setdefault("failure_message", self._failure_message)
                base_kwargs["mllm"] = mllm_config
            return _start_properties_from_mapping(base_kwargs)

        if skip_vendor_validation:
            warnings.warn(
                "skip_vendor_validation is deprecated and will be removed in a future release. "
                "Use skip_vendor_validation_categories and allow_missing_vendor_categories instead.",
                DeprecationWarning,
                stacklevel=2,
            )

        skip_categories = set(skip_vendor_validation_categories or ())
        allow_missing_categories = set(allow_missing_vendor_categories or ())
        if skip_vendor_validation:
            skip_categories.update({"asr", "llm", "tts"})
            allow_missing_categories.update({"asr", "llm", "tts"})

        skip_asr_validation = skip_vendor_validation or "asr" in skip_categories
        skip_llm_validation = skip_vendor_validation or "llm" in skip_categories
        skip_tts_validation = skip_vendor_validation or "tts" in skip_categories
        allow_missing_asr = "asr" in allow_missing_categories
        allow_missing_llm = "llm" in allow_missing_categories
        allow_missing_tts = "tts" in allow_missing_categories

        turn_detection_config = self._resolve_turn_detection_config()
        if not skip_asr_validation and (self._stt is not None or not allow_missing_asr):
            base_kwargs["asr"] = self._resolve_asr_config(turn_detection_config)
        base_kwargs["turn_detection"] = turn_detection_config

        if skip_vendor_validation:
            return _start_properties_from_mapping(base_kwargs)

        if self._tts is None and not (skip_tts_validation or allow_missing_tts):
            raise ValueError("TTS configuration is required. Use with_tts() to set it.")

        if self._llm is None and not (skip_llm_validation or allow_missing_llm):
            raise ValueError("LLM configuration is required. Use with_llm() to set it.")

        if self._llm is not None and not skip_llm_validation:
            base_kwargs["llm"] = self._resolve_llm_config()
        if self._tts is not None and not skip_tts_validation:
            base_kwargs["tts"] = self._tts

        return _start_properties_from_mapping(base_kwargs)

    def _resolve_llm_config(self) -> typing.Dict[str, typing.Any]:
        llm_config = dict(self._llm or {})
        if self._instructions is not None and "system_messages" not in llm_config:
            llm_config["system_messages"] = [{"role": "system", "content": self._instructions}]
        if self._greeting is not None and "greeting_message" not in llm_config:
            llm_config["greeting_message"] = self._greeting
        if self._greeting_configs is not None and "greeting_configs" not in llm_config:
            llm_config["greeting_configs"] = _dump_optional_model(self._greeting_configs)
        if self._failure_message is not None and "failure_message" not in llm_config:
            llm_config["failure_message"] = self._failure_message
        if self._max_history is not None and "max_history" not in llm_config:
            llm_config["max_history"] = self._max_history
        return llm_config

    def _resolve_asr_config(self, turn_detection_config: TurnDetectionConfig) -> typing.Dict[str, typing.Any]:
        asr_config = dict(self._stt or {})
        if not asr_config:
            asr_config["vendor"] = "ares"
        asr_config["language"] = self._field_value(turn_detection_config, "language")
        return asr_config

    def _resolve_turn_detection_config(self) -> TurnDetectionConfig:
        existing_turn_detection_language = self._field_value(self._turn_detection, "language")
        language = (
            existing_turn_detection_language
            if existing_turn_detection_language is not None
            else DEFAULT_TURN_DETECTION_LANGUAGE
        )
        language = _validate_turn_detection_language(language)
        if self._turn_detection is None:
            return StartAgentsRequestPropertiesTurnDetection(language=language)
        if isinstance(self._turn_detection, dict):
            return typing.cast(TurnDetectionConfig, {**self._turn_detection, "language": language})
        return self._copy_model_update(self._turn_detection, {"language": language})

    def _clone(self) -> "Agent":
        new_agent = self.__class__.__new__(self.__class__, self._client)
        new_agent._client = self._client
        new_agent._pipeline_id = self._pipeline_id
        new_agent._llm = self._llm
        new_agent._tts = self._tts
        new_agent._stt = self._stt
        new_agent._mllm = self._mllm
        new_agent._tts_sample_rate = self._tts_sample_rate
        new_agent._avatar = self._avatar
        new_agent._avatar_required_sample_rate = self._avatar_required_sample_rate
        new_agent._turn_detection = self._turn_detection
        new_agent._interruption = self._interruption
        new_agent._sal = self._sal
        new_agent._advanced_features = self._advanced_features
        new_agent._parameters = self._parameters
        new_agent._instructions = self._instructions
        new_agent._greeting = self._greeting
        new_agent._failure_message = self._failure_message
        new_agent._max_history = self._max_history
        new_agent._geofence = self._geofence
        new_agent._labels = self._labels
        new_agent._rtc = self._rtc
        new_agent._filler_words = self._filler_words
        new_agent._greeting_configs = self._greeting_configs
        return new_agent
