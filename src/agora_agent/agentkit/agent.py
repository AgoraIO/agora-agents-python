from __future__ import annotations

import time
import typing
import typing_extensions

if typing.TYPE_CHECKING:
    from .agent_session import AgentSession, AsyncAgentSession

from ..agents.types.start_agents_request_properties import StartAgentsRequestProperties
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
from ..agents.types.start_agents_request_properties_mllm_turn_detection import StartAgentsRequestPropertiesMllmTurnDetection
from ..agents.types.start_agents_request_properties_mllm_turn_detection_mode import StartAgentsRequestPropertiesMllmTurnDetectionMode
from ..agents.types.start_agents_request_properties_llm_greeting_configs import StartAgentsRequestPropertiesLlmGreetingConfigs
from ..agents.types.start_agents_request_properties_llm_greeting_configs_mode import StartAgentsRequestPropertiesLlmGreetingConfigsMode
from ..agents.types.start_agents_request_properties_llm_mcp_servers_item import StartAgentsRequestPropertiesLlmMcpServersItem
from ..agents.types.start_agents_request_properties_geofence import StartAgentsRequestPropertiesGeofence
from ..agents.types.start_agents_request_properties_rtc import StartAgentsRequestPropertiesRtc
from ..agents.types.start_agents_request_properties_advanced_features import StartAgentsRequestPropertiesAdvancedFeatures
from ..agents.types.start_agents_request_properties_filler_words import StartAgentsRequestPropertiesFillerWords
from ..agents.types.start_agents_request_properties_filler_words_trigger import StartAgentsRequestPropertiesFillerWordsTrigger
from ..agents.types.start_agents_request_properties_filler_words_trigger_fixed_time_config import StartAgentsRequestPropertiesFillerWordsTriggerFixedTimeConfig
from ..agents.types.start_agents_request_properties_filler_words_content import StartAgentsRequestPropertiesFillerWordsContent
from ..agents.types.start_agents_request_properties_filler_words_content_static_config import StartAgentsRequestPropertiesFillerWordsContentStaticConfig
from .token import generate_convo_ai_token, _validate_expires_in
from .vendors.base import BaseAvatar, BaseLLM, BaseMLLM, BaseSTT, BaseTTS

# Top-level aliases
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
MllmTurnDetectionConfig = StartAgentsRequestPropertiesMllmTurnDetection
MllmTurnDetectionMode = StartAgentsRequestPropertiesMllmTurnDetectionMode


class SessionParamsInput(typing_extensions.TypedDict, total=False):
    silence_config: StartAgentsRequestPropertiesParametersSilenceConfig
    farewell_config: StartAgentsRequestPropertiesParametersFarewellConfig
    data_channel: StartAgentsRequestPropertiesParametersDataChannel
    enable_metrics: bool
    enable_error_message: bool
    audio_scenario: ParametersAudioScenario

# LLM sub-type aliases
LlmGreetingConfigs = StartAgentsRequestPropertiesLlmGreetingConfigs
LlmGreetingConfigsMode = StartAgentsRequestPropertiesLlmGreetingConfigsMode
McpServersItem = StartAgentsRequestPropertiesLlmMcpServersItem

# Additional top-level config aliases
GeofenceConfig = StartAgentsRequestPropertiesGeofence
RtcConfig = StartAgentsRequestPropertiesRtc
FillerWordsConfig = StartAgentsRequestPropertiesFillerWords
FillerWordsTrigger = StartAgentsRequestPropertiesFillerWordsTrigger
FillerWordsTriggerFixedTimeConfig = StartAgentsRequestPropertiesFillerWordsTriggerFixedTimeConfig
FillerWordsContent = StartAgentsRequestPropertiesFillerWordsContent
FillerWordsContentStaticConfig = StartAgentsRequestPropertiesFillerWordsContentStaticConfig


class Agent:
    """A reusable agent definition.

    Use the fluent builder methods (.with_llm(), .with_tts(), .with_stt(), .with_mllm())
    to configure vendor settings after construction.

    Examples
    --------
    >>> from agora_agent.agentkit import Agent
    >>> from agora_agent.agentkit.vendors import OpenAI, ElevenLabsTTS, DeepgramSTT
    >>>
    >>> agent = Agent(instructions="You are a helpful voice assistant.")
    >>> agent = (
    ...     agent
    ...     .with_llm(OpenAI(api_key="...", model="gpt-4"))
    ...     .with_tts(ElevenLabsTTS(key="...", model_id="...", voice_id="...", sample_rate=24000))
    ...     .with_stt(DeepgramSTT(api_key="...", model="nova-2"))
    ... )
    """

    def __init__(
        self,
        name: typing.Optional[str] = None,
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
    ):
        self._name = name
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

    def with_llm(self, vendor: BaseLLM) -> "Agent":
        new_agent = self._clone()
        new_agent._llm = vendor.to_config()
        return new_agent

    def with_tts(self, vendor: BaseTTS) -> "Agent":
        new_agent = self._clone()
        new_agent._tts = vendor.to_config()
        new_agent._tts_sample_rate = vendor.sample_rate
        return new_agent

    def with_stt(self, vendor: BaseSTT) -> "Agent":
        new_agent = self._clone()
        new_agent._stt = vendor.to_config()
        return new_agent

    def with_mllm(self, vendor: BaseMLLM) -> "Agent":
        new_agent = self._clone()
        new_agent._mllm = vendor.to_config()
        if isinstance(new_agent._mllm, dict):
            new_agent._mllm["enable"] = True
        if isinstance(new_agent._advanced_features, dict):
            advanced_features = {key: value for key, value in new_agent._advanced_features.items() if key != "enable_mllm"}
            new_agent._advanced_features = typing.cast(AdvancedFeatures, advanced_features) if advanced_features else None
        elif isinstance(new_agent._advanced_features, StartAgentsRequestPropertiesAdvancedFeatures):
            advanced_features_model = new_agent._advanced_features.model_copy(update={"enable_mllm": None})
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
        new_agent = self._clone()
        new_agent._avatar = vendor.to_config()
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
        new_agent = self._clone()
        new_agent._instructions = instructions
        return new_agent

    def with_greeting(self, greeting: str) -> "Agent":
        new_agent = self._clone()
        new_agent._greeting = greeting
        return new_agent

    def with_name(self, name: str) -> "Agent":
        new_agent = self._clone()
        new_agent._name = name
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
            new_agent._advanced_features = new_agent._advanced_features.model_copy(update={"enable_tools": enabled})
        return new_agent

    def with_parameters(self, parameters: typing.Union[SessionParams, SessionParamsInput]) -> "Agent":
        """Returns a new Agent with the specified session parameters.

        Use this to configure silence behaviour, graceful hang-up, data channel, and more.
        """
        new_agent = self._clone()
        new_agent._parameters = parameters
        return new_agent

    def with_failure_message(self, message: str) -> "Agent":
        """Returns a new Agent with the specified failure message.

        The failure message is played via TTS when the LLM call fails.
        """
        new_agent = self._clone()
        new_agent._failure_message = message
        return new_agent

    def with_max_history(self, max_history: int) -> "Agent":
        """Returns a new Agent with the specified maximum conversation history length."""
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

    @property
    def name(self) -> typing.Optional[str]:
        return self._name

    @property
    def llm(self) -> typing.Optional[typing.Dict[str, typing.Any]]:
        return self._llm

    @property
    def tts(self) -> typing.Optional[typing.Dict[str, typing.Any]]:
        return self._tts

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
        return {
            "name": self._name,
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
        }

    def create_session(
        self,
        client: typing.Any,
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
        from .agent_session import AgentSession

        session_name = name or self._name or f"agent-{int(time.time())}"
        return AgentSession(
            client=client,
            agent=self,
            app_id=client.app_id if hasattr(client, "app_id") else "",
            app_certificate=client.app_certificate if hasattr(client, "app_certificate") else None,
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
        client: typing.Any,
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
        :class:`~agora_agent.agentkit.AsyncAgentSession`.
        """
        from .agent_session import AsyncAgentSession

        session_name = name or self._name or f"agent-{int(time.time())}"
        return AsyncAgentSession(
            client=client,
            agent=self,
            app_id=client.app_id if hasattr(client, "app_id") else "",
            app_certificate=client.app_certificate if hasattr(client, "app_certificate") else None,
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
    ) -> StartAgentsRequestProperties:
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
                account=agent_uid,
                **token_kwargs,
            )

        mllm_flag = isinstance(self._mllm, dict) and self._mllm.get("enable") is True
        is_mllm_mode = bool(mllm_flag or self._mllm is not None)

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
        if self._parameters is not None:
            if isinstance(self._parameters, dict):
                base_kwargs["parameters"] = StartAgentsRequestPropertiesParameters(**self._parameters)
            else:
                base_kwargs["parameters"] = self._parameters
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
                if self._greeting:
                    mllm_config.setdefault("greeting_message", self._greeting)
                if self._failure_message:
                    mllm_config.setdefault("failure_message", self._failure_message)
                if self._max_history is not None:
                    mllm_config.setdefault("max_history", self._max_history)
                base_kwargs["mllm"] = mllm_config
            return StartAgentsRequestProperties(**base_kwargs)

        if skip_vendor_validation:
            return StartAgentsRequestProperties(**base_kwargs)

        if self._tts is None:
            raise ValueError("TTS configuration is required. Use with_tts() to set it.")

        if self._llm is None:
            raise ValueError("LLM configuration is required. Use with_llm() to set it.")

        llm_config = dict(self._llm)
        # Agent-level fields take priority over the vendor's defaults.
        # This matches the TS SDK where agent-level values override vendor config.
        if self._instructions:
            llm_config["system_messages"] = [{"role": "system", "content": self._instructions}]
        if self._greeting:
            llm_config.setdefault("greeting_message", self._greeting)
        if self._failure_message:
            llm_config.setdefault("failure_message", self._failure_message)
        if self._max_history is not None:
            llm_config.setdefault("max_history", self._max_history)

        base_kwargs["llm"] = llm_config
        base_kwargs["tts"] = self._tts
        if self._stt is not None:
            base_kwargs["asr"] = self._stt

        return StartAgentsRequestProperties(**base_kwargs)

    def _clone(self) -> "Agent":
        new_agent = Agent.__new__(Agent)
        new_agent._name = self._name
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
        return new_agent
