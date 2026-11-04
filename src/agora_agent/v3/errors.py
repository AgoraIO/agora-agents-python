"""Structured errors raised by v3 operations.

Every error a v3 operation raises (``client.v3.*`` and the AgentKit stored-agent,
session and number helpers built on it) derives from :class:`AgoraV3Error` and
belongs to exactly one category::

    AgoraV3Error
    ├── V3ValidationError    (also ValueError)     input rejected before any request
    ├── V3ConfigurationError (also ValueError)     the client itself is misconfigured
    ├── V3ConnectionError    (also ConnectionError) the request could not complete
    │   └── V3TimeoutError   (also TimeoutError)
    └── V3ApiError           (also core ApiError)  non-2xx, or a 2xx that violates the contract
        └── PreconditionFailedError                HTTP 412; ``latest()`` reloads

The categories also inherit the built-in exceptions callers caught before this
hierarchy existed, so ``except ValueError`` and ``except ApiError`` keep working.
Transport errors are raised ``from`` the underlying ``httpx`` exception, which
remains available as ``__cause__``. Messages never include credentials, tokens or
``Authorization`` values.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Mapping, Optional

from ..core.api_error import ApiError

__all__ = [
    "AgoraV3Error",
    "V3ValidationError",
    "V3ConfigurationError",
    "V3ConnectionError",
    "V3TimeoutError",
    "V3ApiError",
    "PreconditionFailedError",
]

REQUEST_ID_HEADER = "Agora-Request-Id"
_MAX_TEXT_BODY_IN_MESSAGE = 200


class AgoraV3Error(Exception):
    """Base class for every error raised by a v3 operation.

    Catch this to handle any v3 failure; catch a category subclass to react to
    one kind of failure.
    """


class V3ValidationError(AgoraV3Error, ValueError):
    """The caller's input was rejected locally, before any HTTP request was sent.

    Examples: empty or dot-segment identifiers, bodies that do not match the
    public contract, invalid secret names or references, malformed
    ``Idempotency-Key`` values, unsupported builder fields and conflicting
    options. Retrying the same call will fail again; fix the input instead.
    """


class V3ConfigurationError(AgoraV3Error, ValueError):
    """The client is misconfigured, independent of any particular request.

    Examples: an invalid ``V3Options.base_url`` or ``AGORA_AGENTS_V3_BASE_URL``
    origin, internal or malformed client-level headers, missing authorization,
    or HTTPX client authentication that would override SDK credentials. This is
    a deployment problem rather than a bad request.
    """


class V3ConnectionError(AgoraV3Error, ConnectionError):
    """The request could not complete (DNS, refused or reset connection, TLS,
    protocol or aborted body).

    The originating ``httpx`` exception is available as ``__cause__``. A write
    may or may not have reached the server; v3 writes are never retried
    automatically.
    """


class V3TimeoutError(V3ConnectionError, TimeoutError):
    """The request timed out while connecting, writing, reading or waiting for
    a pooled connection. A subtype of :class:`V3ConnectionError`."""


class V3ApiError(AgoraV3Error, ApiError):
    """The server responded with a non-2xx HTTP status, or with a 2xx response
    that violates the API contract and cannot be used.

    Contract violations keep the real 2xx ``status_code`` and set
    ``violation``: for example a body that is not JSON, a missing ``ETag``
    before a guarded update, a missing or repeated pagination cursor, or a
    session response without ``agent_session_id``.

    Also an :class:`agora_agent.core.api_error.ApiError`, so existing
    ``except ApiError`` handlers keep working.

    Attributes:
        status_code: HTTP status code.
        headers: Response headers with lower-case names.
        body: Parsed JSON body, the response text when it is not JSON, or
            ``None`` when the response is empty.
        raw_body: Undecoded response body bytes.
        violation: For a 2xx response, what made it unusable; otherwise ``None``.
    """

    status_code: Optional[int]
    headers: Dict[str, str]
    body: Any
    raw_body: bytes
    violation: Optional[str]

    def __init__(
        self,
        *,
        status_code: Optional[int] = None,
        headers: Optional[Mapping[str, str]] = None,
        body: Any = None,
        raw_body: bytes = b"",
        violation: Optional[str] = None,
    ) -> None:
        normalized = {str(key).lower(): value for key, value in (headers or {}).items()}
        ApiError.__init__(self, status_code=status_code, headers=normalized, body=body)
        self.headers = normalized
        self.raw_body = raw_body
        self.violation = violation
        # ApiError does not populate ``args``; keep repr() and tracebacks useful.
        Exception.__init__(self, self._message())

    def _field(self, name: str) -> Optional[str]:
        value = self.body.get(name) if isinstance(self.body, dict) else None
        return value if isinstance(value, str) and value else None

    @property
    def detail(self) -> Optional[str]:
        """The server's human-readable ``detail`` string, when present."""
        return self._field("detail")

    @property
    def reason(self) -> Optional[str]:
        """The server's machine-readable ``reason`` code (e.g. ``TaskNotFound``), when present."""
        return self._field("reason")

    @property
    def request_id(self) -> Optional[str]:
        """The ``Agora-Request-Id`` response header, when present. Include it in support requests."""
        return self.headers.get(REQUEST_ID_HEADER.lower())

    def _message(self) -> str:
        if self.violation:
            message = f"v3 response with status {self.status_code} violates the API contract: {self.violation}"
        else:
            message = f"v3 request failed with status {self.status_code}" + self._summary()
        if self.request_id:
            message += f" (request ID: {self.request_id})"
        return message

    def _summary(self) -> str:
        reason, detail = self.reason, self.detail
        if reason and detail:
            return f": {reason}: {detail}"
        if reason or detail:
            return f": {reason or detail}"
        if isinstance(self.body, str) and self.body:
            text = self.body[:_MAX_TEXT_BODY_IN_MESSAGE]
            return f": {text}{'...' if len(self.body) > len(text) else ''}"
        return ""

    def __str__(self) -> str:
        return self._message()


class PreconditionFailedError(V3ApiError):
    """The server rejected an outdated ``If-Match`` / ``If-None-Match`` (HTTP 412).

    ``latest()`` reloads the affected resource (a secret-key conflict reloads
    its secret set) and returns the parsed data. With ``AsyncAgora``, await
    ``error.latest()``. No write is automatically retried.
    """

    _latest: Callable[[], Any]

    def latest(self) -> Any:
        """Reload the current resource without repeating the failed write."""
        reload = getattr(self, "_latest", None)
        if reload is None:
            raise RuntimeError("latest() is only available on errors raised by a v3 request")
        return reload()
