from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from typing_extensions import Literal

# Supported sample rates across all TTS providers.
SampleRate = Literal[8000, 16000, 22050, 24000, 44100, 48000]

# Provider-specific sample rate constraints.
# These are used to validate TTS/avatar compatibility at the type level and at runtime.
ElevenLabsSampleRate = Literal[16000, 22050, 24000, 44100]
MicrosoftSampleRate = Literal[8000, 16000, 24000, 48000]
OpenAISampleRate = Literal[24000]
CartesiaSampleRate = Literal[8000, 16000, 22050, 24000, 44100, 48000]
GoogleTTSSampleRate = Literal[8000, 16000, 22050, 24000, 44100, 48000]


def ensure_mcp_transport(servers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Copy MCP server configs and supply the transport required by the API."""
    result = []
    for server in servers:
        item = dict(server)
        if item.get("transport") is None:
            item["transport"] = "streamable_http"
        result.append(item)
    return result


class BaseLLM(BaseModel, ABC):
    """Abstract base class for all LLM vendor implementations.

    Subclasses must implement :meth:`to_config` to return a dict that maps to
    the ``llm`` field of the Agora ``StartAgentsRequest.Properties`` payload.
    """

    @abstractmethod
    def to_config(self) -> Dict[str, Any]:
        """Serialize the LLM configuration to a dict for the REST API."""


class BaseTTS(BaseModel, ABC):
    """Abstract base class for all TTS vendor implementations.

    Subclasses must implement :meth:`to_config`.

    :attr:`resolved_sample_rate` is used by
    :class:`~agora_agent.agentkit.AgentSession` to validate TTS/avatar
    compatibility at runtime (avatars require a specific sample rate).  It
    returns ``None`` when the user has not explicitly configured a sample rate,
    which will cause a warning at session start time rather than a hard error.
    """

    @abstractmethod
    def to_config(self) -> Dict[str, Any]:
        """Serialize the TTS configuration to a dict for the REST API."""

    @property
    def resolved_sample_rate(self) -> Optional[int]:
        """The effective configured sample rate in Hz, or None if not set."""
        return getattr(self, "sample_rate", None)


class BaseSTT(BaseModel, ABC):
    """Abstract base class for all STT vendor implementations.

    Subclasses must implement :meth:`to_config` to return a dict that maps to
    the ``stt`` field of the Agora ``StartAgentsRequest.Properties`` payload.
    """

    @abstractmethod
    def to_config(self) -> Dict[str, Any]:
        """Serialize the STT configuration to a dict for the REST API."""


class BaseMLLM(BaseModel, ABC):
    """Abstract base class for all MLLM (multimodal LLM) vendor implementations.

    When an MLLM is configured via :meth:`~agora_agent.agentkit.Agent.with_mllm`,
    the ``mllm.enable`` flag is set on the request and the ``llm``/``tts`` fields
    are omitted. Subclasses must implement :meth:`to_config` to return a dict
    that maps to the ``mllm`` field of the payload.
    """

    @abstractmethod
    def to_config(self) -> Dict[str, Any]:
        """Serialize the MLLM configuration to a dict for the REST API."""


class BaseAvatar(BaseModel, ABC):
    """Abstract base class for all avatar vendor implementations.

    Avatars render a visual representation of the agent and impose a specific TTS
    sample rate requirement.  Subclasses must expose :attr:`required_sample_rate`
    so that :class:`~agora_agent.agentkit.AgentSession` can verify that the
    configured TTS uses a compatible sample rate before starting the session.
    """

    @property
    @abstractmethod
    def required_sample_rate(self) -> int:
        """The TTS sample rate (Hz) that this avatar requires."""

    @abstractmethod
    def to_config(self) -> Dict[str, Any]:
        """Serialize the avatar configuration to a dict for the REST API."""
