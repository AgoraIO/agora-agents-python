import typing
import warnings

from ..core.api_error import ApiError
from ..agent_management.types.agent_think_agent_management_request_on_listening_action import (
    AgentThinkAgentManagementRequestOnListeningAction as AgentThinkRequestOnListeningAction,
)
from ..agent_management.types.agent_think_agent_management_request_on_speaking_action import (
    AgentThinkAgentManagementRequestOnSpeakingAction as AgentThinkRequestOnSpeakingAction,
)
from ..agent_management.types.agent_think_agent_management_request_on_thinking_action import (
    AgentThinkAgentManagementRequestOnThinkingAction as AgentThinkRequestOnThinkingAction,
)
from ..agent_management.types.agent_think_agent_management_response import (
    AgentThinkAgentManagementResponse as AgentThinkResponse,
)
from ..agents.types.get_turns_agents_response import GetTurnsAgentsResponse
from ..agents.types.start_agents_request_properties import StartAgentsRequestProperties
from .agent import Agent, GetTurnsOptions, SayOptions, ThinkOptions
from .avatar_types import (
    is_akool_avatar,
    is_anam_avatar,
    is_avatar_token_managed,
    is_generic_avatar,
    is_heygen_avatar,
    is_live_avatar_avatar,
    validate_avatar_config,
    validate_tts_sample_rate,
)
from .presets import (
    get_preset_category,
    infer_asr_preset,
    infer_llm_preset,
    infer_tts_preset,
    normalize_preset_input,
    resolve_session_presets,
)
from .token import generate_convo_ai_token, _parse_numeric_uid


class _AgentSessionRequiredOptions(typing.TypedDict, total=True):
    """Required fields shared by both sync and async session constructors."""

    client: typing.Any
    agent: Agent
    app_id: str
    name: str
    channel: str
    agent_uid: str
    remote_uids: typing.List[str]


class AgentSessionOptions(_AgentSessionRequiredOptions, total=False):
    """Configuration options for creating an agent session.

    Required fields
    ---------------
    client, agent, app_id, name, channel, agent_uid, remote_uids

    Optional fields
    ---------------
    app_certificate, token, idle_timeout, enable_string_uid, preset,
    pipeline_id, expires_in, debug, warn
    """

    app_certificate: str
    token: str
    idle_timeout: int
    enable_string_uid: bool
    preset: typing.Union[str, typing.Sequence[str]]
    pipeline_id: str
    expires_in: int
    debug: bool
    warn: typing.Callable[[str], None]


class _AgentSessionBase:
    """Shared state and helpers for :class:`AgentSession` and :class:`AsyncAgentSession`.

    Not intended for direct use — instantiate one of the concrete subclasses or
    call :meth:`Agent.create_session` / :meth:`Agent.create_async_session`.
    """

    def __init__(
        self,
        client: typing.Any,
        agent: Agent,
        app_id: str,
        name: str,
        channel: str,
        agent_uid: str,
        remote_uids: typing.List[str],
        app_certificate: typing.Optional[str] = None,
        token: typing.Optional[str] = None,
        idle_timeout: typing.Optional[int] = None,
        enable_string_uid: typing.Optional[bool] = None,
        preset: typing.Optional[typing.Union[str, typing.Sequence[str]]] = None,
        pipeline_id: typing.Optional[str] = None,
        expires_in: typing.Optional[int] = None,
        debug: typing.Optional[bool] = None,
        warn: typing.Optional[typing.Callable[[str], None]] = None,
    ):
        self._client = client
        self._agent = agent
        self._app_id = app_id
        self._app_certificate = app_certificate
        self._name = name
        self._channel = channel
        self._token = token
        self._agent_uid = agent_uid
        self._remote_uids = remote_uids
        self._idle_timeout = idle_timeout
        self._enable_string_uid = enable_string_uid
        self._preset = preset
        self._pipeline_id = pipeline_id
        self._expires_in = expires_in
        self._debug = debug
        self._warn = warn or warnings.warn
        self._agent_id: typing.Optional[str] = None
        self._status: str = "idle"
        self._event_handlers: typing.Dict[str, typing.List[typing.Callable[..., None]]] = {}

    # ------------------------------------------------------------------
    # Public read-only properties
    # ------------------------------------------------------------------

    @property
    def id(self) -> typing.Optional[str]:
        return self._agent_id

    @property
    def status(self) -> str:
        return self._status

    @property
    def agent(self) -> Agent:
        return self._agent

    @property
    def app_id(self) -> str:
        return self._app_id

    @property
    def raw(self) -> typing.Any:
        """Direct access to the underlying Fern-generated AgentsClient.

        Use this to access any new endpoints that Fern generates without
        waiting for agentkit method updates.
        """
        return self._client.agents

    @property
    def raw_agent_management(self) -> typing.Any:
        """Direct access to the underlying Fern-generated AgentManagement client."""
        return self._client.agent_management

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _convo_ai_headers(self) -> typing.Optional[typing.Dict[str, str]]:
        """Return per-request auth headers when client is in app-credentials mode.

        In app-credentials mode a fresh ConvoAI token (RTC + RTM) is generated
        for every request and returned as ``Authorization: agora token=<token>``.
        In basic-auth mode this returns ``None`` (the client-level header is used).
        """
        if getattr(self._client, "auth_mode", None) != "app-credentials":
            return None
        app_id: str = getattr(self._client, "app_id", self._app_id)
        app_certificate: typing.Optional[str] = getattr(
            self._client, "app_certificate", self._app_certificate
        )
        if not app_certificate:
            raise RuntimeError("app_certificate is required for app-credentials auth mode")
        token = generate_convo_ai_token(
            app_id=app_id,
            app_certificate=app_certificate,
            channel_name=self._channel,
            uid=_parse_numeric_uid(self._agent_uid, "agent_uid"),
        )
        return {"Authorization": f"agora token={token}"}

    def _request_options(self) -> typing.Optional[typing.Dict[str, typing.Any]]:
        """Build request_options dict with per-request auth headers if needed."""
        headers = self._convo_ai_headers()
        if headers is None:
            return None
        return {"additional_headers": headers}

    def _validate_avatar_config(self) -> None:
        avatar = self._agent.avatar
        tts = self._agent.tts
        if not avatar or avatar.get("enable", True) is False:
            return
        if self._is_mllm_mode():
            raise ValueError(
                "Avatars are only supported with the cascading ASR + LLM + TTS pipeline. "
                "Remove the avatar configuration when using MLLM, or switch to a cascading session."
            )

        if (
            is_heygen_avatar(avatar)
            or is_live_avatar_avatar(avatar)
            or is_akool_avatar(avatar)
            or is_anam_avatar(avatar)
            or is_generic_avatar(avatar)
        ):
            validate_avatar_config(avatar)

        tts_params = tts.get("params") if isinstance(tts, dict) else None
        sample_rate = self._agent.tts_sample_rate
        if sample_rate is None and isinstance(tts_params, dict):
            sample_rate = (
                tts_params.get("sample_rate")
                or tts_params.get("sample_rate_hertz")
                or tts_params.get("samplingRate")
            )
        if isinstance(sample_rate, int):
            validate_tts_sample_rate(avatar, sample_rate)
        elif is_heygen_avatar(avatar):
            self._warn(
                "Warning: HeyGen avatar detected but TTS sample_rate is not explicitly set. "
                "HeyGen requires 24,000 Hz. Please ensure your TTS provider is configured for 24kHz."
            )
        elif is_live_avatar_avatar(avatar):
            self._warn(
                "Warning: LiveAvatar avatar detected but TTS sample_rate is not explicitly set. "
                "LiveAvatar requires 24,000 Hz. Please ensure your TTS provider is configured for 24kHz."
            )
        elif is_akool_avatar(avatar):
            self._warn(
                "Warning: Akool avatar detected but TTS sample_rate is not explicitly set. "
                "Akool requires 16,000 Hz. Please ensure your TTS provider is configured for 16kHz."
            )

    def _enrich_avatar_for_session(self, properties: typing.Dict[str, typing.Any]) -> None:
        avatar = properties.get("avatar")
        if not isinstance(avatar, dict) or avatar.get("enable", True) is False:
            return

        params = avatar.get("params")
        if not isinstance(params, dict):
            params = {}
            avatar["params"] = params

        if is_generic_avatar(avatar):
            if not params.get("agora_appid"):
                params["agora_appid"] = self._app_id
            if not params.get("agora_channel"):
                params["agora_channel"] = self._channel

        if not is_avatar_token_managed(avatar):
            validate_avatar_config(avatar, require_session_fields=is_generic_avatar(avatar))
            return

        if not params.get("agora_uid"):
            validate_avatar_config(avatar, require_session_fields=is_generic_avatar(avatar))
            return

        if not params.get("agora_token"):
            if not self._app_certificate:
                raise ValueError(
                    "Cannot auto-generate avatar RTC token: app_certificate is required when agora_token is omitted. "
                    "Pass app_certificate on the Agora client or supply agora_token explicitly on the avatar vendor."
                )
            token_kwargs: typing.Dict[str, typing.Any] = {}
            if self._expires_in is not None:
                token_kwargs["token_expire"] = self._expires_in
            params["agora_token"] = generate_convo_ai_token(
                app_id=self._app_id,
                app_certificate=self._app_certificate,
                channel_name=self._channel,
                uid=_parse_numeric_uid(str(params["agora_uid"]), "avatar agora_uid"),
                **token_kwargs,
            )

        if str(params.get("agora_uid")) == self._agent_uid:
            self._warn(
                "Warning: avatar agora_uid matches agent_rtc_uid. Use a unique UID for the avatar video publisher."
            )

        validate_avatar_config(avatar, require_session_fields=True)

    @staticmethod
    def _dump_model(value: typing.Any) -> typing.Any:
        if hasattr(value, "model_dump"):
            return value.model_dump(exclude_none=True)
        if isinstance(value, dict):
            return {k: _AgentSessionBase._dump_model(v) for k, v in value.items() if v is not None}
        if isinstance(value, list):
            return [_AgentSessionBase._dump_model(item) for item in value]
        return value

    def _is_mllm_mode(self) -> bool:
        mllm = self._agent.mllm
        if isinstance(mllm, dict) and mllm.get("enable") is True:
            return True
        return mllm is not None

    def _build_start_properties(
        self,
        token_opts: typing.Dict[str, typing.Any],
        skip_vendor_validation_categories: typing.AbstractSet[str],
        allow_missing_vendor_categories: typing.AbstractSet[str],
    ) -> typing.Dict[str, typing.Any]:
        base_properties = self._agent.to_properties(
            channel=self._channel,
            agent_uid=self._agent_uid,
            remote_uids=self._remote_uids,
            idle_timeout=self._idle_timeout,
            enable_string_uid=self._enable_string_uid,
            skip_vendor_validation_categories=skip_vendor_validation_categories,
            allow_missing_vendor_categories=allow_missing_vendor_categories,
            **token_opts,
        )
        properties = self._dump_model(base_properties)
        self._enrich_avatar_for_session(properties)

        if self._is_mllm_mode():
            if self._agent.mllm is not None:
                mllm = self._dump_model(self._agent.mllm)
                if not isinstance(mllm, dict):
                    mllm = {}
                if self._agent.greeting is not None:
                    mllm.setdefault("greeting_message", self._agent.greeting)
                if self._agent.failure_message is not None:
                    mllm.setdefault("failure_message", self._agent.failure_message)
                properties["mllm"] = mllm
            return properties

        if self._agent.tts is not None:
            properties["tts"] = self._dump_model(self._agent.tts)
        if self._agent.llm is not None:
            llm = dict(self._agent.llm)
            if self._agent.instructions is not None:
                llm["system_messages"] = [{"role": "system", "content": self._agent.instructions}]
            if self._agent.greeting is not None:
                llm["greeting_message"] = self._agent.greeting
            if self._agent.greeting_configs is not None:
                llm["greeting_configs"] = self._dump_model(self._agent.greeting_configs)
            if self._agent.failure_message is not None:
                llm["failure_message"] = self._agent.failure_message
            if self._agent.max_history is not None:
                llm["max_history"] = self._agent.max_history
            properties["llm"] = llm
        if self._agent.stt is not None:
            properties["asr"] = self._dump_model(self._agent.stt)

        return properties

    def _vendor_validation_categories(
        self,
        pipeline_id: typing.Optional[str],
    ) -> typing.Tuple[typing.Set[str], typing.Set[str]]:
        skip_categories: typing.Set[str] = set()
        allow_missing_categories: typing.Set[str] = {"asr", "llm", "tts"} if pipeline_id else set()

        preset = normalize_preset_input(self._preset)
        if preset:
            for item in preset.split(","):
                category = get_preset_category(item)
                if category is not None:
                    skip_categories.add(category)
                    allow_missing_categories.add(category)

        if infer_asr_preset(self._agent.stt):
            skip_categories.add("asr")
        if infer_llm_preset(self._agent.llm):
            skip_categories.add("llm")
        if infer_tts_preset(self._agent.tts):
            skip_categories.add("tts")
        return skip_categories, allow_missing_categories

    @staticmethod
    def _page_value(pagination: typing.Any, field: str) -> typing.Any:
        if pagination is None:
            return None
        if isinstance(pagination, dict):
            return pagination.get(field)
        return getattr(pagination, field, None)

    @staticmethod
    def _response_turns(response: typing.Any) -> typing.List[typing.Any]:
        turns = response.get("turns") if isinstance(response, dict) else getattr(response, "turns", None)
        return list(turns or [])

    @staticmethod
    def _response_pagination(response: typing.Any) -> typing.Any:
        if isinstance(response, dict):
            return response.get("pagination")
        return getattr(response, "pagination", None)

    @classmethod
    def _with_all_turns(cls, first_response: typing.Any, turns: typing.List[typing.Any]) -> GetTurnsAgentsResponse:
        data = cls._dump_model(first_response)
        if not isinstance(data, dict):
            data = {}
        data["turns"] = turns
        return GetTurnsAgentsResponse(**data)

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def on(self, event: str, handler: typing.Callable[..., None]) -> None:
        """Register an event handler.

        Parameters
        ----------
        event : str
            The event type (``started``, ``stopped``, ``error``).
        handler : callable
            The event handler to invoke when the event fires.
        """
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)

    def off(self, event: str, handler: typing.Callable[..., None]) -> None:
        """Unregister a previously registered event handler."""
        handlers = self._event_handlers.get(event)
        if handlers and handler in handlers:
            handlers.remove(handler)

    def _emit(self, event: str, data: typing.Any) -> None:
        handlers = self._event_handlers.get(event)
        if handlers:
            for handler in handlers:
                try:
                    handler(data)
                except Exception as exc:
                    # Prevent a misbehaving handler from blocking other handlers or
                    # the session lifecycle. Warn so the error is not silently lost.
                    warnings.warn(
                        f"Event handler for '{event}' raised an exception: {exc}",
                        stacklevel=2,
                    )


class AgentSession(_AgentSessionBase):
    """Manages the lifecycle of an agent session (synchronous).

    This class provides a high-level interface for managing agent sessions,
    including starting, stopping, and interacting with the agent.

    Use :meth:`Agent.create_session` to create a session — this is the
    recommended entry point.

    Examples
    --------
    >>> from agora_agent import Agora, Area, Agent, OpenAI, ElevenLabsTTS
    >>>
    >>> client = Agora(area=Area.US, app_id="...", app_certificate="...")
    >>> agent = Agent(name="assistant", instructions="You are a helpful voice assistant.")
    >>> agent = agent.with_llm(OpenAI(api_key="...", base_url="https://api.openai.com/v1/chat/completions", model="gpt-4")).with_tts(ElevenLabsTTS(key="...", model_id="...", voice_id="...", base_url="wss://api.elevenlabs.io/v1"))
    >>> session = agent.create_session(client, channel="room-123", agent_uid="1", remote_uids=["100"])
    >>> agent_id = session.start()
    >>> session.say("Hello!")
    >>> session.stop()
    """

    def start(self) -> str:
        """Start the agent session.

        Returns
        -------
        str
            The agent ID.

        Raises
        ------
        RuntimeError
            If the session is not in a startable state.
        ValueError
            If avatar/TTS configuration is invalid.
        """
        if self._status not in ("idle", "stopped", "error"):
            raise RuntimeError(f"Cannot start session in {self._status} state")

        self._validate_avatar_config()
        self._status = "starting"

        try:
            pipeline_id = self._pipeline_id if self._pipeline_id is not None else self._agent.pipeline_id
            if self._token:
                token_opts: typing.Dict[str, typing.Any] = {"token": self._token}
            else:
                token_opts = {
                    "app_id": self._app_id,
                    "app_certificate": self._app_certificate,
                    "expires_in": self._expires_in,
                }

            skip_categories, allow_missing_categories = self._vendor_validation_categories(pipeline_id)
            properties = self._build_start_properties(
                token_opts,
                skip_vendor_validation_categories=skip_categories,
                allow_missing_vendor_categories=allow_missing_categories,
            )
            resolved_preset, resolved_properties = resolve_session_presets(
                self._preset,
                properties,
            )

            if self._debug:
                print("[Agora Debug] Starting agent session...")
                print("[Agora Debug] Request:", {
                    "appid": self._app_id,
                    "name": self._name,
                    "preset": resolved_preset,
                    "pipeline_id": pipeline_id,
                    "properties": resolved_properties,
                })

            try:
                request_properties: typing.Any = StartAgentsRequestProperties(**resolved_properties)
            except Exception:
                request_properties = resolved_properties

            response = self._client.agents.start(
                self._app_id,
                name=self._name,
                properties=request_properties,
                preset=resolved_preset,
                pipeline_id=pipeline_id,
                request_options=self._request_options(),
            )

            self._agent_id = response.agent_id if hasattr(response, "agent_id") else None
            self._status = "running"
            self._emit("started", {"agent_id": self._agent_id})
            return self._agent_id or ""
        except Exception as e:
            self._status = "error"
            self._emit("error", e)
            raise

    def stop(self) -> None:
        """Stop the agent session.

        If the agent has already stopped (e.g., crashed or timed out), the
        server returns 404, which this method treats as a successful stop
        rather than raising an error.
        """
        if self._status != "running":
            raise RuntimeError(f"Cannot stop session in {self._status} state")
        if not self._agent_id:
            raise RuntimeError("No agent ID available")

        self._status = "stopping"

        try:
            self._client.agents.stop(
                self._app_id, self._agent_id, request_options=self._request_options()
            )
            self._status = "stopped"
            self._emit("stopped", {"agent_id": self._agent_id})
        except ApiError as e:
            if e.status_code == 404:
                self._status = "stopped"
                self._emit("stopped", {"agent_id": self._agent_id})
                return
            self._status = "error"
            self._emit("error", e)
            raise
        except Exception as e:
            self._status = "error"
            self._emit("error", e)
            raise

    def say(
        self,
        text: str,
        priority: typing.Optional[str] = None,
        interruptable: typing.Optional[bool] = None,
        *,
        options: typing.Optional["SayOptions"] = None,
    ) -> None:
        """Send a message to be spoken by the agent.

        Parameters
        ----------
        text : str
            The text to speak.
        priority : str, optional
            Priority of the message (``INTERRUPT``, ``APPEND``, ``IGNORE``).
        interruptable : bool, optional
            Whether the message can be interrupted by the user.
        """
        if self._status != "running":
            raise RuntimeError(f"Cannot say in {self._status} state")
        if not self._agent_id:
            raise RuntimeError("No agent ID available")

        kwargs: typing.Dict[str, typing.Any] = {"text": text}
        if options is not None:
            kwargs.update(options)
        if priority is not None:
            kwargs["priority"] = priority
        if interruptable is not None:
            kwargs["interruptable"] = interruptable

        self._client.agents.speak(
            self._app_id, self._agent_id, request_options=self._request_options(), **kwargs
        )

    def interrupt(self) -> None:
        """Interrupt the agent while it is speaking or thinking."""
        if self._status != "running":
            raise RuntimeError(f"Cannot interrupt in {self._status} state")
        if not self._agent_id:
            raise RuntimeError("No agent ID available")

        self._client.agents.interrupt(
            self._app_id, self._agent_id, request_options=self._request_options()
        )

    def think(
        self,
        text: str,
        *,
        on_listening_action: typing.Optional[AgentThinkRequestOnListeningAction] = None,
        on_thinking_action: typing.Optional[AgentThinkRequestOnThinkingAction] = None,
        on_speaking_action: typing.Optional[AgentThinkRequestOnSpeakingAction] = None,
        interruptable: typing.Optional[bool] = None,
        metadata: typing.Optional[typing.Dict[str, str]] = None,
        options: typing.Optional["ThinkOptions"] = None,
    ) -> AgentThinkResponse:
        """Inject a custom text instruction into the current session pipeline.

        In API v2.7, omitting ``on_listening_action`` uses the server default
        ``"interrupt"``. Pass ``on_listening_action="inject"`` explicitly to
        preserve the pre-v2.7 behavior.
        """
        if self._status != "running":
            raise RuntimeError(f"Cannot think in {self._status} state")
        if not self._agent_id:
            raise RuntimeError("No agent ID available")

        kwargs: typing.Dict[str, typing.Any] = {"text": text}
        if options is not None:
            kwargs.update(options)
        if on_listening_action is not None:
            kwargs["on_listening_action"] = on_listening_action
        if on_thinking_action is not None:
            kwargs["on_thinking_action"] = on_thinking_action
        if on_speaking_action is not None:
            kwargs["on_speaking_action"] = on_speaking_action
        if interruptable is not None:
            kwargs["interruptable"] = interruptable
        if metadata is not None:
            kwargs["metadata"] = metadata

        return self._client.agent_management.agent_think(
            self._app_id,
            self._agent_id,
            request_options=self._request_options(),
            **kwargs,
        )

    def update(self, properties: typing.Any) -> None:
        """Update the agent configuration at runtime.

        Parameters
        ----------
        properties : UpdateAgentsRequestProperties
            Partial configuration to update.
        """
        if self._status != "running":
            raise RuntimeError(f"Cannot update in {self._status} state")
        if not self._agent_id:
            raise RuntimeError("No agent ID available")

        self._client.agents.update(
            self._app_id,
            self._agent_id,
            properties=properties,
            request_options=self._request_options(),
        )

    def get_history(self) -> typing.Any:
        """Get the conversation history."""
        if not self._agent_id:
            raise RuntimeError("No agent ID available")

        return self._client.agents.get_history(
            self._app_id, self._agent_id, request_options=self._request_options()
        )

    def get_info(self) -> typing.Any:
        """Get the current session info."""
        if not self._agent_id:
            raise RuntimeError("No agent ID available")

        return self._client.agents.get(
            self._app_id, self._agent_id, request_options=self._request_options()
        )

    def get_turns(
        self,
        *,
        page_index: typing.Optional[int] = None,
        page_size: typing.Optional[int] = None,
        options: typing.Optional["GetTurnsOptions"] = None,
    ) -> GetTurnsAgentsResponse:
        """Get turn-by-turn analytics and timing details for this session."""
        if not self._agent_id:
            raise RuntimeError("No agent ID available")

        kwargs: typing.Dict[str, typing.Any] = {}
        if options is not None:
            kwargs.update(options)
        if page_index is not None:
            kwargs["page_index"] = page_index
        if page_size is not None:
            kwargs["page_size"] = page_size

        return self._client.agents.get_turns(
            self._app_id,
            self._agent_id,
            request_options=self._request_options(),
            **kwargs,
        )

    def get_all_turns(self, *, page_size: typing.Optional[int] = None) -> GetTurnsAgentsResponse:
        """Get all turn analytics pages for this session.

        Raises ``RuntimeError`` if the server's pagination metadata is missing
        the fields required to advance, or if requesting the next page returns
        a page index that did not advance.
        """
        response = self.get_turns(page_index=1, page_size=page_size)
        all_turns = self._response_turns(response)
        pagination = self._response_pagination(response)
        current_page = self._page_value(pagination, "page_index") or 1
        while pagination is not None and self._page_value(pagination, "is_last_page") is False:
            total_pages = self._page_value(pagination, "total_pages")
            returned_index = self._page_value(pagination, "page_index")
            if returned_index is None and total_pages is None:
                raise RuntimeError(
                    "get_all_turns pagination cannot continue: response must include "
                    "page_index, total_pages, or is_last_page=true."
                )
            if total_pages is not None and current_page >= total_pages:
                break
            next_page = current_page + 1
            response = self.get_turns(page_index=next_page, page_size=page_size)
            all_turns.extend(self._response_turns(response))
            pagination = self._response_pagination(response)
            returned_index = self._page_value(pagination, "page_index") if pagination else None
            if returned_index is not None:
                if returned_index <= current_page and self._page_value(pagination, "is_last_page") is not True:
                    raise RuntimeError(
                        f"get_all_turns pagination did not advance: requested page {next_page}, "
                        f"received page {returned_index}."
                    )
                current_page = returned_index
            else:
                total_pages = self._page_value(pagination, "total_pages") if pagination else None
                is_last_page = self._page_value(pagination, "is_last_page") if pagination else None
                if total_pages is None and is_last_page is not True:
                    raise RuntimeError(
                        "get_all_turns pagination cannot continue: response must include "
                        "page_index, total_pages, or is_last_page=true."
                    )
                current_page = next_page
        return self._with_all_turns(response, all_turns)


class AsyncAgentSession(_AgentSessionBase):
    """Async version of :class:`AgentSession` for use with :class:`AsyncAgora`.

    Use :meth:`Agent.create_async_session` to create a session — this is the
    recommended entry point.

    Examples
    --------
    >>> from agora_agent import AsyncAgora, Area, Agent, OpenAI, ElevenLabsTTS
    >>>
    >>> client = AsyncAgora(area=Area.US, app_id="...", app_certificate="...")
    >>> agent = Agent(name="assistant", instructions="You are helpful.")
    >>> agent = agent.with_llm(OpenAI(api_key="...", base_url="https://api.openai.com/v1/chat/completions", model="gpt-4")).with_tts(ElevenLabsTTS(key="...", model_id="...", voice_id="...", base_url="wss://api.elevenlabs.io/v1"))
    >>> session = agent.create_async_session(client, channel="room-123", agent_uid="1", remote_uids=["100"])
    >>> agent_id = await session.start()
    >>> await session.say("Hello!")
    >>> await session.stop()
    """

    async def start(self) -> str:
        """Start the agent session.

        Returns
        -------
        str
            The agent ID.

        Raises
        ------
        RuntimeError
            If the session is not in a startable state.
        ValueError
            If avatar/TTS configuration is invalid.
        """
        if self._status not in ("idle", "stopped", "error"):
            raise RuntimeError(f"Cannot start session in {self._status} state")

        self._validate_avatar_config()
        self._status = "starting"

        try:
            pipeline_id = self._pipeline_id if self._pipeline_id is not None else self._agent.pipeline_id
            if self._token:
                token_opts: typing.Dict[str, typing.Any] = {"token": self._token}
            else:
                token_opts = {
                    "app_id": self._app_id,
                    "app_certificate": self._app_certificate,
                    "expires_in": self._expires_in,
                }

            skip_categories, allow_missing_categories = self._vendor_validation_categories(pipeline_id)
            properties = self._build_start_properties(
                token_opts,
                skip_vendor_validation_categories=skip_categories,
                allow_missing_vendor_categories=allow_missing_categories,
            )
            resolved_preset, resolved_properties = resolve_session_presets(
                self._preset,
                properties,
            )

            if self._debug:
                print("[Agora Debug] Starting agent session...")
                print("[Agora Debug] Request:", {
                    "appid": self._app_id,
                    "name": self._name,
                    "preset": resolved_preset,
                    "pipeline_id": pipeline_id,
                    "properties": resolved_properties,
                })

            try:
                request_properties: typing.Any = StartAgentsRequestProperties(**resolved_properties)
            except Exception:
                request_properties = resolved_properties

            response = await self._client.agents.start(
                self._app_id,
                name=self._name,
                properties=request_properties,
                preset=resolved_preset,
                pipeline_id=pipeline_id,
                request_options=self._request_options(),
            )

            self._agent_id = response.agent_id if hasattr(response, "agent_id") else None
            self._status = "running"
            self._emit("started", {"agent_id": self._agent_id})
            return self._agent_id or ""
        except Exception as e:
            self._status = "error"
            self._emit("error", e)
            raise

    async def stop(self) -> None:
        """Stop the agent session.

        If the agent has already stopped (e.g., crashed or timed out), the
        server returns 404, which this method treats as a successful stop
        rather than raising an error.
        """
        if self._status != "running":
            raise RuntimeError(f"Cannot stop session in {self._status} state")
        if not self._agent_id:
            raise RuntimeError("No agent ID available")

        self._status = "stopping"

        try:
            await self._client.agents.stop(
                self._app_id, self._agent_id, request_options=self._request_options()
            )
            self._status = "stopped"
            self._emit("stopped", {"agent_id": self._agent_id})
        except ApiError as e:
            if e.status_code == 404:
                self._status = "stopped"
                self._emit("stopped", {"agent_id": self._agent_id})
                return
            self._status = "error"
            self._emit("error", e)
            raise
        except Exception as e:
            self._status = "error"
            self._emit("error", e)
            raise

    async def say(
        self,
        text: str,
        priority: typing.Optional[str] = None,
        interruptable: typing.Optional[bool] = None,
        *,
        options: typing.Optional["SayOptions"] = None,
    ) -> None:
        """Send a message to be spoken by the agent.

        Parameters
        ----------
        text : str
            The text to speak.
        priority : str, optional
            Priority of the message (``INTERRUPT``, ``APPEND``, ``IGNORE``).
        interruptable : bool, optional
            Whether the message can be interrupted by the user.
        """
        if self._status != "running":
            raise RuntimeError(f"Cannot say in {self._status} state")
        if not self._agent_id:
            raise RuntimeError("No agent ID available")

        kwargs: typing.Dict[str, typing.Any] = {"text": text}
        if options is not None:
            kwargs.update(options)
        if priority is not None:
            kwargs["priority"] = priority
        if interruptable is not None:
            kwargs["interruptable"] = interruptable

        await self._client.agents.speak(
            self._app_id, self._agent_id, request_options=self._request_options(), **kwargs
        )

    async def interrupt(self) -> None:
        """Interrupt the agent while it is speaking or thinking."""
        if self._status != "running":
            raise RuntimeError(f"Cannot interrupt in {self._status} state")
        if not self._agent_id:
            raise RuntimeError("No agent ID available")

        await self._client.agents.interrupt(
            self._app_id, self._agent_id, request_options=self._request_options()
        )

    async def think(
        self,
        text: str,
        *,
        on_listening_action: typing.Optional[AgentThinkRequestOnListeningAction] = None,
        on_thinking_action: typing.Optional[AgentThinkRequestOnThinkingAction] = None,
        on_speaking_action: typing.Optional[AgentThinkRequestOnSpeakingAction] = None,
        interruptable: typing.Optional[bool] = None,
        metadata: typing.Optional[typing.Dict[str, str]] = None,
        options: typing.Optional["ThinkOptions"] = None,
    ) -> AgentThinkResponse:
        """Inject a custom text instruction into the current session pipeline.

        In API v2.7, omitting ``on_listening_action`` uses the server default
        ``"interrupt"``. Pass ``on_listening_action="inject"`` explicitly to
        preserve the pre-v2.7 behavior.
        """
        if self._status != "running":
            raise RuntimeError(f"Cannot think in {self._status} state")
        if not self._agent_id:
            raise RuntimeError("No agent ID available")

        kwargs: typing.Dict[str, typing.Any] = {"text": text}
        if options is not None:
            kwargs.update(options)
        if on_listening_action is not None:
            kwargs["on_listening_action"] = on_listening_action
        if on_thinking_action is not None:
            kwargs["on_thinking_action"] = on_thinking_action
        if on_speaking_action is not None:
            kwargs["on_speaking_action"] = on_speaking_action
        if interruptable is not None:
            kwargs["interruptable"] = interruptable
        if metadata is not None:
            kwargs["metadata"] = metadata

        return await self._client.agent_management.agent_think(
            self._app_id,
            self._agent_id,
            request_options=self._request_options(),
            **kwargs,
        )

    async def update(self, properties: typing.Any) -> None:
        """Update the agent configuration at runtime.

        Parameters
        ----------
        properties : UpdateAgentsRequestProperties
            Partial configuration to update.
        """
        if self._status != "running":
            raise RuntimeError(f"Cannot update in {self._status} state")
        if not self._agent_id:
            raise RuntimeError("No agent ID available")

        await self._client.agents.update(
            self._app_id,
            self._agent_id,
            properties=properties,
            request_options=self._request_options(),
        )

    async def get_history(self) -> typing.Any:
        """Get the conversation history."""
        if not self._agent_id:
            raise RuntimeError("No agent ID available")

        return await self._client.agents.get_history(
            self._app_id, self._agent_id, request_options=self._request_options()
        )

    async def get_info(self) -> typing.Any:
        """Get the current session info."""
        if not self._agent_id:
            raise RuntimeError("No agent ID available")

        return await self._client.agents.get(
            self._app_id, self._agent_id, request_options=self._request_options()
        )

    async def get_turns(
        self,
        *,
        page_index: typing.Optional[int] = None,
        page_size: typing.Optional[int] = None,
        options: typing.Optional["GetTurnsOptions"] = None,
    ) -> GetTurnsAgentsResponse:
        """Get turn-by-turn analytics and timing details for this session."""
        if not self._agent_id:
            raise RuntimeError("No agent ID available")

        kwargs: typing.Dict[str, typing.Any] = {}
        if options is not None:
            kwargs.update(options)
        if page_index is not None:
            kwargs["page_index"] = page_index
        if page_size is not None:
            kwargs["page_size"] = page_size

        return await self._client.agents.get_turns(
            self._app_id,
            self._agent_id,
            request_options=self._request_options(),
            **kwargs,
        )

    async def get_all_turns(self, *, page_size: typing.Optional[int] = None) -> GetTurnsAgentsResponse:
        """Get all turn analytics pages for this session.

        Raises ``RuntimeError`` if the server's pagination metadata is missing
        the fields required to advance, or if requesting the next page returns
        a page index that did not advance.
        """
        response = await self.get_turns(page_index=1, page_size=page_size)
        all_turns = self._response_turns(response)
        pagination = self._response_pagination(response)
        current_page = self._page_value(pagination, "page_index") or 1
        while pagination is not None and self._page_value(pagination, "is_last_page") is False:
            total_pages = self._page_value(pagination, "total_pages")
            returned_index = self._page_value(pagination, "page_index")
            if returned_index is None and total_pages is None:
                raise RuntimeError(
                    "get_all_turns pagination cannot continue: response must include "
                    "page_index, total_pages, or is_last_page=true."
                )
            if total_pages is not None and current_page >= total_pages:
                break
            next_page = current_page + 1
            response = await self.get_turns(page_index=next_page, page_size=page_size)
            all_turns.extend(self._response_turns(response))
            pagination = self._response_pagination(response)
            returned_index = self._page_value(pagination, "page_index") if pagination else None
            if returned_index is not None:
                if returned_index <= current_page and self._page_value(pagination, "is_last_page") is not True:
                    raise RuntimeError(
                        f"get_all_turns pagination did not advance: requested page {next_page}, "
                        f"received page {returned_index}."
                    )
                current_page = returned_index
            else:
                total_pages = self._page_value(pagination, "total_pages") if pagination else None
                is_last_page = self._page_value(pagination, "is_last_page") if pagination else None
                if total_pages is None and is_last_page is not True:
                    raise RuntimeError(
                        "get_all_turns pagination cannot continue: response must include "
                        "page_index, total_pages, or is_last_page=true."
                    )
                current_page = next_page
        return self._with_all_turns(response, all_turns)
