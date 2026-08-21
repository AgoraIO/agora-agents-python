"""Preview endpoint clients.

Preview providers are not served by the production Conversational AI gateway.
They live behind a single partner host and are gated by an ``agora-feature``
header. :class:`AgoraPreview` and :class:`AsyncAgoraPreview` are drop-in
replacements for ``Agora`` / ``AsyncAgora`` that point every request at that
host and send the header, so the rest of agentkit (``Agent``, ``AgentSession``,
vendor classes) works unchanged.

Everything under ``agentkit/preview/`` is temporary. When these providers ship
on the production gateway, delete this package and move the vendor classes into
``vendors/mllm.py``.
"""

from __future__ import annotations

import typing

from ...pool_client import Agora, AsyncAgora
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

    #: The Gemini walkie-talkie / clever-chatter MLLMs.
    GEMINI_LIVE = "gemini-live"


PreviewFeature = str

_DEFAULT_PREVIEW_FEATURES: typing.Tuple[str, ...] = (PreviewFeatures.GEMINI_LIVE,)


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


class AgoraPreview(Agora):
    """Client for the Agora Conversational AI preview endpoint.

    Use it exactly like ``Agora`` — same auth modes, same ``Agent`` and
    ``AgentSession`` API. It differs only in where requests go and in the
    ``agora-feature`` header it attaches.

    Parameters
    ----------
    features : Sequence[str], optional
        Preview families to request via the ``agora-feature`` header.
        Defaults to ``("gemini-live",)``.
    base_url : str, optional
        Override the preview base URL. For internal testing against a staging host.

    Examples
    --------
    >>> from agora_agent import Area
    >>> from agora_agent.agentkit import Agent
    >>> from agora_agent.agentkit.preview import AgoraPreview, GeminiCleverChatter
    >>> client = AgoraPreview(area=Area.US, app_id="...", app_certificate="...")
    >>> session = (
    ...     Agent(client=client)
    ...     .with_mllm(GeminiCleverChatter(api_key="...", thinking_level="medium"))
    ...     .create_session(channel="demo", agent_uid="1", remote_uids=["100"])
    ... )
    """

    def __init__(
        self,
        *,
        area: typing.Any,
        app_id: str,
        app_certificate: str,
        features: typing.Optional[typing.Sequence[str]] = None,
        base_url: typing.Optional[str] = None,
        headers: typing.Optional[typing.Dict[str, str]] = None,
        **kwargs: typing.Any,
    ):
        self.preview_features: typing.Tuple[str, ...] = tuple(
            features if features is not None else _DEFAULT_PREVIEW_FEATURES
        )
        self._preview_base_url = base_url or PREVIEW_API_BASE_URL

        super().__init__(
            area=area,
            app_id=app_id,
            app_certificate=app_certificate,
            headers=_preview_headers(self.preview_features, headers),
            **kwargs,
        )
        # The base class resolves the URL from the regional pool; repoint it.
        self._update_base_url()

    def _update_base_url(self) -> None:
        self._client_wrapper._base_url = self._preview_base_url

    def get_current_url(self) -> str:
        return self._preview_base_url

    def next_region(self) -> None:
        """No-op: the preview endpoint has no regional replicas to fail over to."""

    def select_best_domain(self) -> None:
        """No-op: the preview endpoint has a single fixed host."""


class AsyncAgoraPreview(AsyncAgora):
    """Async client for the Agora Conversational AI preview endpoint.

    See :class:`AgoraPreview`.
    """

    def __init__(
        self,
        *,
        area: typing.Any,
        app_id: str,
        app_certificate: str,
        features: typing.Optional[typing.Sequence[str]] = None,
        base_url: typing.Optional[str] = None,
        headers: typing.Optional[typing.Dict[str, str]] = None,
        **kwargs: typing.Any,
    ):
        self.preview_features: typing.Tuple[str, ...] = tuple(
            features if features is not None else _DEFAULT_PREVIEW_FEATURES
        )
        self._preview_base_url = base_url or PREVIEW_API_BASE_URL

        super().__init__(
            area=area,
            app_id=app_id,
            app_certificate=app_certificate,
            headers=_preview_headers(self.preview_features, headers),
            **kwargs,
        )
        self._update_base_url()

    def _update_base_url(self) -> None:
        self._client_wrapper._base_url = self._preview_base_url

    def get_current_url(self) -> str:
        return self._preview_base_url

    def next_region(self) -> None:
        """No-op: the preview endpoint has no regional replicas to fail over to."""

    async def select_best_domain(self) -> None:
        """No-op: the preview endpoint has a single fixed host."""


#: Preview MLLM models. ``mllm.vendor`` is ``"gemini"`` for both the production
#: Gemini Live provider and the preview ones, so the model name is one of two
#: things that mark a config as preview-only; see :func:`_has_preview_mllm_envelope`
#: for the other.
#:
#: Both the codenames and their post-rename IDs are listed, so recognition keeps
#: working through Google's rollout whichever name a caller sends.
_PREVIEW_MLLM_MODELS = frozenset(
    {
        "walkie-talkie",
        "clever-chatter",
        "gemini-3.5-live",
        "gemini-3.5-live-thinking",
    }
)


def _has_preview_mllm_envelope(mllm: typing.Mapping[str, typing.Any]) -> bool:
    """Whether a config carries the envelope the preview MLLM classes emit.

    That envelope is the API key repeated inside ``params`` plus a ``url`` on the
    Gemini Developer API host. The production ``GeminiLive`` vendor emits
    neither — it leaves ``params.api_key`` unset and defaults ``url`` to ``""``
    or a WebSocket endpoint.

    This is the second recognition path, and it exists because keying only off
    :data:`_PREVIEW_MLLM_MODELS` makes an unrecognised model name fail silently:
    :func:`apply_preview_shape` would stop retargeting ``greeting_message``, the
    greeting would land in a field these models ignore, and the agent would
    simply never greet. A model name we have not listed yet is reachable by
    following this SDK's own advice to override ``model`` when Google renames
    one ahead of a release, so the failure has to not be silent.
    """
    params = mllm.get("params")
    api_key = params.get("api_key") if isinstance(params, dict) else None
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

    if _is_preview_mllm(properties.get("mllm")):
        features.append(PreviewFeatures.GEMINI_LIVE)

    return features


def assert_preview_support(client: typing.Any, properties: typing.Mapping[str, typing.Any]) -> None:
    """Fail fast when preview providers are paired with a non-preview client.

    Raises before the request goes out, instead of surfacing an opaque gateway
    error — or worse, silently succeeding against the production environment.
    """
    required = required_preview_features(properties)
    if not required:
        return

    enabled = getattr(client, "preview_features", ())
    missing = [feature for feature in required if feature not in enabled]
    if not missing:
        return

    joined = ", ".join(missing)
    raise ValueError(
        f"This agent uses preview providers that require the preview endpoint ({joined}). "
        "Create the session with AgoraPreview instead of Agora, and make sure its "
        f"`features` include: {joined}."
    )


__all__ = [
    "PREVIEW_API_BASE_URL",
    "PREVIEW_FEATURE_HEADER",
    "AgoraPreview",
    "AsyncAgoraPreview",
    "PreviewFeature",
    "PreviewFeatures",
    "apply_preview_shape",
    "assert_preview_support",
    "required_preview_features",
]
