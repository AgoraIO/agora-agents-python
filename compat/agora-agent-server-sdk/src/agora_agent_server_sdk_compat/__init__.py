"""Compatibility re-exports for the renamed agora-agents package."""

import agora_agent as _agora_agent

__all__ = getattr(_agora_agent, "__all__", [])


def __getattr__(name: str):
    return getattr(_agora_agent, name)


def __dir__():
    return dir(_agora_agent)
