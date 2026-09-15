"""Preview endpoint routing helpers.

Preview providers are served by a partner host gated by an ``agora-feature``
header. Agent sessions use these helpers to create private generated clients
for preview traffic while the caller's ``Agora`` / ``AsyncAgora`` client stays
on its production endpoint.

Everything under ``agentkit/preview/`` is temporary. When a provider ships on
the production gateway, remove its preview registration and move its class into
the corresponding production vendor module.
"""

from __future__ import annotations

import typing

import httpx
from ...agent_management.client import AgentManagementClient, AsyncAgentManagementClient
from ...agents.client import AgentsClient, AsyncAgentsClient
from ...core.client_wrapper import AsyncClientWrapper, SyncClientWrapper
from .vendors import GEMINI_PREVIEW_MLLM_URL

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

    #: Gemini preview MLLM gate. Gemini ASR uses the production endpoint.
    GEMINI_LIVE = "gemini-live"
    LIVE_MODELS = "live-models"


PreviewFeature = str


def _pinned_headers(headers: typing.Any, feature_header: str) -> httpx.Headers:
    merged = httpx.Headers(headers)
    merged[PREVIEW_FEATURE_HEADER] = feature_header
    return merged


class _GatedSyncHttpxClient:
    """Pin the preview header after generated per-call header overrides."""

    def __init__(self, inner: httpx.Client, features: typing.Sequence[str]):
        self._inner = inner
        self._feature_header = ",".join(features)

    def request(self, *args: typing.Any, **kwargs: typing.Any) -> httpx.Response:
        kwargs["headers"] = _pinned_headers(kwargs.get("headers"), self._feature_header)
        return self._inner.request(*args, **kwargs)

    def stream(self, *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        kwargs["headers"] = _pinned_headers(kwargs.get("headers"), self._feature_header)
        return self._inner.stream(*args, **kwargs)


class _GatedAsyncHttpxClient:
    def __init__(self, inner: httpx.AsyncClient, features: typing.Sequence[str]):
        self._inner = inner
        self._feature_header = ",".join(features)

    async def request(self, *args: typing.Any, **kwargs: typing.Any) -> httpx.Response:
        kwargs["headers"] = _pinned_headers(kwargs.get("headers"), self._feature_header)
        return await self._inner.request(*args, **kwargs)

    def stream(self, *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        kwargs["headers"] = _pinned_headers(kwargs.get("headers"), self._feature_header)
        return self._inner.stream(*args, **kwargs)


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
    merged: typing.Dict[str, str] = {
        key: value for key, value in (headers or {}).items()
        if key.lower() != PREVIEW_FEATURE_HEADER
    }
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
    }
    if isinstance(source, AsyncClientWrapper):
        kwargs["httpx_client"] = typing.cast(httpx.AsyncClient, _GatedAsyncHttpxClient(source.httpx_client.httpx_client, features))
        async_wrapper = AsyncClientWrapper(**kwargs)
        return (
            AsyncAgentsClient(client_wrapper=async_wrapper),
            AsyncAgentManagementClient(client_wrapper=async_wrapper),
        )
    if isinstance(source, SyncClientWrapper):
        kwargs["httpx_client"] = typing.cast(httpx.Client, _GatedSyncHttpxClient(source.httpx_client.httpx_client, features))
        sync_wrapper = SyncClientWrapper(**kwargs)
        return (
            AgentsClient(client_wrapper=sync_wrapper),
            AgentManagementClient(client_wrapper=sync_wrapper),
        )
    raise TypeError("Unsupported Agora client wrapper")


#: ASR vendors served only by the preview endpoint.
_PREVIEW_FEATURES_BY_CATEGORY: typing.Dict[str, typing.Dict[str, PreviewFeature]] = {
    "asr": {},
    "mllm": {"openai_gpt_live": PreviewFeatures.LIVE_MODELS},
}


_PREVIEW_MLLM_MODELS = frozenset(
    {
        "models/gemini-3.8-live",
        "models/gemini-3.8-live-extended-thinking",
    }
)


def _has_preview_mllm_envelope(mllm: typing.Mapping[str, typing.Any]) -> bool:
    """Whether a config carries the envelope the preview MLLM classes emit.

    That envelope is a top-level ``mllm.api_key`` plus a ``url`` on the Gemini
    Developer API host. ``GeminiLive`` configs for older model IDs use a
    different URL (an empty string or WebSocket endpoint).

    This is the second recognition path, and it exists because keying only off
    :data:`_PREVIEW_MLLM_MODELS` makes an unrecognised model name fail silently:
    :func:`apply_preview_shape` would stop retargeting ``greeting_message``, the
    greeting would land in a field these models ignore, and the agent would
    simply never greet. A model name we have not listed yet is reachable by
    following this SDK's own advice to override ``model`` when Google renames
    one ahead of a release, so the failure has to not be silent.
    """
    api_key = mllm.get("api_key")
    url = mllm.get("url")
    return isinstance(api_key, str) and isinstance(url, str) and url.startswith(GEMINI_PREVIEW_MLLM_URL)


def _is_preview_mllm(mllm: typing.Any) -> bool:
    """Whether an MLLM config targets a preview model.

    Recognised by model name, or by the wire envelope only the preview vendor
    classes produce.
    """
    if not isinstance(mllm, dict) or mllm.get("vendor") != "gemini":
        return False
    params = mllm.get("params")
    model = params.get("model") if isinstance(params, dict) else None
    if isinstance(model, str) and model in _PREVIEW_MLLM_MODELS:
        return True
    return _has_preview_mllm_envelope(mllm)


#: MLLM wire keys the preview route spells differently from the Agora schema,
#: as production spelling -> preview spelling.
#:
#: ``failure_message`` is deliberately absent: it is an Agora engine feature
#: rather than a Gemini one, so it keeps its schema spelling.
_PREVIEW_MLLM_FIELD_RENAMES = {"greeting_message": "greeting"}


def apply_preview_shape(properties: typing.MutableMapping[str, typing.Any]) -> None:
    """Retarget MLLM fields the shared builder wrote with production spellings.

    ``Agent`` fills ``mllm.greeting_message`` from an agent-level ``greeting``
    whenever the vendor has not set that key — correct for every GA vendor, but
    the preview Gemini models read ``greeting``, so the value would land in a
    field they ignore and the agent would silently never greet.

    Rather than teach the shared builder about preview providers, the
    translation lives here and disappears with this package at GA. The vendor's
    own value wins; the production-spelled one is the fallback, which also
    migrates a hand-written ``greeting_message`` onto the preview key so an
    existing config keeps working after only swapping the model.

    Mutates ``properties["mllm"]`` in place. Safe because the builder hands this
    a fresh copy of the MLLM config rather than the Agent's stored one.
    """
    mllm = properties.get("mllm")
    if not isinstance(mllm, dict) or not _is_preview_mllm(mllm):
        return
    for production, preview in _PREVIEW_MLLM_FIELD_RENAMES.items():
        if production not in mllm:
            continue
        value = mllm.pop(production)
        mllm.setdefault(preview, value)


def required_preview_features(properties: typing.Mapping[str, typing.Any]) -> typing.List[str]:
    """Return the preview features a start request needs.

    Derived from the request body rather than from the vendor classes, so
    hand-written configs are covered too.
    """
    features: typing.List[str] = []
    for category, vendors in _PREVIEW_FEATURES_BY_CATEGORY.items():
        config = properties.get(category)
        if not isinstance(config, dict):
            continue
        vendor = config.get("vendor")
        if not isinstance(vendor, str):
            continue
        feature = vendors.get(vendor)
        if feature is not None and feature not in features:
            features.append(feature)
    if _is_preview_mllm(properties.get("mllm")) and PreviewFeatures.GEMINI_LIVE not in features:
        features.append(PreviewFeatures.GEMINI_LIVE)
    return features


__all__ = [
    "PREVIEW_API_BASE_URL",
    "PREVIEW_FEATURE_HEADER",
    "PreviewFeature",
    "PreviewFeatures",
    "apply_preview_shape",
    "create_preview_session_clients",
    "required_preview_features",
]
