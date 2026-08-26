"""Preview endpoint routing helpers.

Preview providers are served by a partner host gated by an ``agora-feature``
header. Agent sessions use these helpers to create private generated clients
for preview traffic while the caller's ``Agora`` / ``AsyncAgora`` client stays
on its production endpoint.

Everything under ``agentkit/preview/`` is temporary. When these providers ship
on the production gateway, delete this package and move the vendor classes into
``vendors/stt.py``.
"""

from __future__ import annotations

import typing

from ...agent_management.client import AgentManagementClient, AsyncAgentManagementClient
from ...agents.client import AgentsClient, AsyncAgentsClient
from ...core.client_wrapper import AsyncClientWrapper, SyncClientWrapper

#: Base URL that serves the preview providers.
PREVIEW_API_BASE_URL = "https://partner.ai.agora.io/preview/api/conversational-ai-agent"

#: Request header that opts a request into a preview provider family.
#:
#: This is the header the preview gateway routes on. A request that reaches the
#: gateway without it is not rejected — it is routed to the production
#: environment, where the preview providers do not exist.
PREVIEW_FEATURE_HEADER = "agora-feature"


class PreviewFeatures:
    """Preview provider families.

    Each value is one entry in the ``agora-feature`` header and gates a set of
    vendors on the preview endpoint.
    """

    #: Gemini 3.5 Transcribe ASR.
    GEMINI_LIVE = "gemini-live"


PreviewFeature = str

def _preview_headers(
    features: typing.Sequence[str],
    headers: typing.Optional[typing.Dict[str, str]],
) -> typing.Dict[str, str]:
    """Merge the gate header over caller headers.

    The gate goes last on purpose: caller-supplied headers must not be able to
    drop or blank it. A preview request that loses the header is not rejected —
    it routes to the production environment, where the preview providers do not
    exist. Use ``features`` to change the value.
    """
    merged: typing.Dict[str, str] = dict(headers or {})
    merged[PREVIEW_FEATURE_HEADER] = ",".join(features)
    return merged


def create_preview_session_clients(
    client: typing.Any,
    features: typing.Sequence[str],
) -> typing.Tuple[typing.Any, typing.Any]:
    """Create generated clients pinned to the preview host and feature gate."""
    source = client._client_wrapper
    kwargs = {
        "authorization": source._authorization,
        "username": source._username,
        "password": source._password,
        "headers": _preview_headers(features, source.get_custom_headers()),
        "base_url": PREVIEW_API_BASE_URL,
        "timeout": source.get_timeout(),
        "httpx_client": source.httpx_client.httpx_client,
    }
    if isinstance(source, AsyncClientWrapper):
        wrapper = AsyncClientWrapper(**kwargs)
        return (
            AsyncAgentsClient(client_wrapper=wrapper),
            AsyncAgentManagementClient(client_wrapper=wrapper),
        )
    if isinstance(source, SyncClientWrapper):
        wrapper = SyncClientWrapper(**kwargs)
        return (
            AgentsClient(client_wrapper=wrapper),
            AgentManagementClient(client_wrapper=wrapper),
        )
    raise TypeError("Unsupported Agora client wrapper")


#: ASR vendors served only by the preview endpoint.
_PREVIEW_ASR_VENDORS = frozenset({"gemini"})


def required_preview_features(properties: typing.Mapping[str, typing.Any]) -> typing.List[str]:
    """Return the preview features a start request needs.

    Derived from the request body rather than from the vendor classes, so
    hand-written configs are covered too.
    """
    features: typing.List[str] = []

    asr = properties.get("asr")
    if isinstance(asr, dict) and asr.get("vendor") in _PREVIEW_ASR_VENDORS:
        features.append(PreviewFeatures.GEMINI_LIVE)

    return features


__all__ = [
    "PREVIEW_API_BASE_URL",
    "PREVIEW_FEATURE_HEADER",
    "PreviewFeature",
    "PreviewFeatures",
    "create_preview_session_clients",
    "required_preview_features",
]
