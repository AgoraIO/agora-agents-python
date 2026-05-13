import typing
import warnings

from ..core.api_error import ApiError
from ..agent_management.types.agent_think_request_on_listening_action import (
    AgentThinkRequestOnListeningAction,
)
from ..agent_management.types.agent_think_request_on_speaking_action import (
    AgentThinkRequestOnSpeakingAction,
)
from ..agent_management.types.agent_think_request_on_thinking_action import (
    AgentThinkRequestOnThinkingAction,
)
from ..agent_management.types.agent_think_response import AgentThinkResponse
from ..agents.types.start_agents_request_properties import StartAgentsRequestProperties
from .agent import Agent
from .avatar_types import (
    is_akool_avatar,
    is_anam_avatar,
    is_heygen_avatar,
    is_live_avatar_avatar,
    validate_avatar_config,
    validate_tts_sample_rate,
)
from .presets import resolve_session_presets
from .token import generate_convo_ai_token


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
    app_certificate, token, idle_timeout, enable_string_uid, expires_in
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
            account=self._agent_uid,
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

        if (
            is_heygen_avatar(avatar)
            or is_live_avatar_avatar(avatar)
            or is_akool_avatar(avatar)
            or is_anam_avatar(avatar)
        ):
            validate_avatar_config(avatar)

        tts_params = tts.get("params") if isinstance(tts, dict) else None
        sample_rate = tts_params.get("sample_rate") if isinstance(tts_params, dict) else None
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

    def _build_start_properties(self, token_opts: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        base_properties = self._agent.to_properties(
            channel=self._channel,
            agent_uid=self._agent_uid,
            remote_uids=self._remote_uids,
            idle_timeout=self._idle_timeout,
            enable_string_uid=self._enable_string_uid,
            skip_vendor_validation=True,
            **token_opts,
        )
        properties = self._dump_model(base_properties)

        if self._is_mllm_mode():
            if self._agent.mllm is not None:
                mllm = dict(self._agent.mllm)
                if self._agent.greeting:
                    mllm.setdefault("greeting_message", self._agent.greeting)
                properties["mllm"] = mllm
            return properties

        if self._agent.tts is not None:
            properties["tts"] = self._dump_model(self._agent.tts)
        if self._agent.llm is not None:
            llm = dict(self._agent.llm)
            if self._agent.instructions:
                llm["system_messages"] = [{"role": "system", "content": self._agent.instructions}]
            if self._agent.greeting:
                llm.setdefault("greeting_message", self._agent.greeting)
            if self._agent.failure_message:
                llm.setdefault("failure_message", self._agent.failure_message)
            if self._agent.max_history is not None:
                llm.setdefault("max_history", self._agent.max_history)
            properties["llm"] = llm
        if self._agent.stt is not None:
            properties["asr"] = self._dump_model(self._agent.stt)

        return properties

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
    >>> from agora_agent import Agora, Area
    >>> from agora_agent.agentkit import Agent
    >>>
    >>> client = Agora(area=Area.US, app_id="...", app_certificate="...")
    >>> agent = Agent(name="assistant", instructions="You are a helpful voice assistant.")
    >>> from agora_agent.agentkit.vendors import OpenAI, ElevenLabsTTS
    >>> agent = agent.with_llm(OpenAI(api_key="...", model="gpt-4")).with_tts(ElevenLabsTTS(key="...", model_id="...", voice_id="..."))
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
            if self._token:
                token_opts: typing.Dict[str, typing.Any] = {"token": self._token}
            else:
                token_opts = {
                    "app_id": self._app_id,
                    "app_certificate": self._app_certificate,
                    "expires_in": self._expires_in,
                }

            properties = self._build_start_properties(token_opts)
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
                    "pipeline_id": self._pipeline_id,
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
                pipeline_id=self._pipeline_id,
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
    ) -> AgentThinkResponse:
        """Inject a custom text instruction into the current session pipeline."""
        if self._status != "running":
            raise RuntimeError(f"Cannot think in {self._status} state")
        if not self._agent_id:
            raise RuntimeError("No agent ID available")

        kwargs: typing.Dict[str, typing.Any] = {"text": text}
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

    def get_turns(self) -> typing.Any:
        """Get turn-by-turn analytics and timing details for this session."""
        if not self._agent_id:
            raise RuntimeError("No agent ID available")

        return self._client.agents.get_turns(
            self._app_id, self._agent_id, request_options=self._request_options()
        )


class AsyncAgentSession(_AgentSessionBase):
    """Async version of :class:`AgentSession` for use with :class:`AsyncAgora`.

    Use :meth:`Agent.create_async_session` to create a session — this is the
    recommended entry point.

    Examples
    --------
    >>> from agora_agent import AsyncAgora, Area
    >>> from agora_agent.agentkit import Agent
    >>>
    >>> client = AsyncAgora(area=Area.US, app_id="...", app_certificate="...")
    >>> agent = Agent(name="assistant", instructions="You are helpful.")
    >>> from agora_agent.agentkit.vendors import OpenAI, ElevenLabsTTS
    >>> agent = agent.with_llm(OpenAI(api_key="...", model="gpt-4")).with_tts(ElevenLabsTTS(key="...", model_id="...", voice_id="..."))
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
            if self._token:
                token_opts: typing.Dict[str, typing.Any] = {"token": self._token}
            else:
                token_opts = {
                    "app_id": self._app_id,
                    "app_certificate": self._app_certificate,
                    "expires_in": self._expires_in,
                }

            properties = self._build_start_properties(token_opts)
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
                    "pipeline_id": self._pipeline_id,
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
                pipeline_id=self._pipeline_id,
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
    ) -> AgentThinkResponse:
        """Inject a custom text instruction into the current session pipeline."""
        if self._status != "running":
            raise RuntimeError(f"Cannot think in {self._status} state")
        if not self._agent_id:
            raise RuntimeError("No agent ID available")

        kwargs: typing.Dict[str, typing.Any] = {"text": text}
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

    async def get_turns(self) -> typing.Any:
        """Get turn-by-turn analytics and timing details for this session."""
        if not self._agent_id:
            raise RuntimeError("No agent ID available")

        return await self._client.agents.get_turns(
            self._app_id, self._agent_id, request_options=self._request_options()
        )
