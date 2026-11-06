"""v3 transport adapter: share the owning client's auth, HTTP client and pool."""
from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Generic, Iterator, Mapping, Optional, Type, TypeVar
from urllib.parse import quote, urlsplit

import httpx
from ..agentkit.token import generate_convo_ai_token
from ..core.public_auth import validate_public_headers as _validate_public_headers
from .errors import (
    AgoraV3Error,
    PreconditionFailedError,
    V3ApiError,
    V3ConfigurationError,
    V3ConnectionError,
    V3TimeoutError,
    V3ValidationError,
)

_UNSET: Any = object()
T = TypeVar("T")


@dataclass(frozen=True)
class V3Options:
    """Optional origin/header overrides; default public preview uses the v1 project path."""
    base_url: Optional[str] = None
    headers: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class RawResponse(Generic[T]):
    data: T
    headers: httpx.Headers
    status_code: int
    response: httpx.Response

    @property
    def etag(self) -> Optional[str]:
        return self.headers.get("ETag")


def contract_violation(raw: RawResponse[Any], violation: str) -> V3ApiError:
    """Build the API error for a 2xx response the SDK cannot use."""
    response = raw.response
    return V3ApiError(
        status_code=raw.status_code,
        headers=dict(raw.headers or {}),
        body=raw.data,
        raw_body=response.content if response is not None else b"",
        violation=violation,
    )


def _next_cursor(raw: RawResponse[Any], seen: set) -> Optional[str]:
    """Return the continuation cursor, or None on the last page."""
    page = raw.data
    if not page.get("has_more"):
        return None
    cursor = page.get("next_cursor")
    if not cursor or cursor in seen:
        raise contract_violation(raw, "Invalid or repeated v3 pagination cursor")
    seen.add(cursor)
    return cursor


@contextmanager
def _reclassify(category: Type[AgoraV3Error]) -> Iterator[None]:
    """Re-raise a plain ValueError from shared (v2-compatible) checks as a v3 category."""
    try:
        yield
    except AgoraV3Error:
        raise
    except ValueError as exc:
        raise category(str(exc)) from exc


def _connection_error(exc: httpx.RequestError, method: str) -> V3ConnectionError:
    """Map an HTTPX request failure to a v3 connection error; the HTTPX error stays the cause.

    The message names the method and HTTPX error type only, never the request
    URL or headers, so it cannot carry credentials.
    """
    kind = V3TimeoutError if isinstance(exc, httpx.TimeoutException) else V3ConnectionError
    summary = "timed out" if kind is V3TimeoutError else "could not complete"
    detail = str(exc)
    return kind(f"v3 {method} request {summary}: {type(exc).__name__}" + (f": {detail}" if detail else ""))


def segment(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise V3ValidationError("v3 path identifiers must be nonempty strings")
    # RFC 3986 permits unescaped dots in a path segment. HTTP clients and
    # proxies normalize the two dot-segments before sending the request.
    if value in (".", ".."):
        raise V3ValidationError("v3 path identifiers cannot be dot segments")
    return quote(value, safe="")


def _body(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        value = value.model_dump(exclude_unset=True)
    if isinstance(value, dict):
        return {k: _body(v) for k, v in value.items() if v is not _UNSET}
    if isinstance(value, (list, tuple)):
        return [_body(v) for v in value]
    return value


class Resource:
    def __init__(self, owner: Any, options: Optional[V3Options]):
        self.owner = owner
        self.options = options or V3Options()

    def _arguments(self, method, path, body, headers, params, request_options):
        wrapper = self.owner._client_wrapper
        body = _body(body)
        from .contract import validate_write
        additional = (request_options or {}).get("additional_body_parameters", {}) or {}
        if body is None and additional and method not in {"GET", "DELETE"}:
            raise V3ValidationError("This operation does not accept a request body")
        validate_write(method, path, {**body, **additional} if isinstance(body, dict) else body)
        if method == "POST" and path.endswith(("/sessions", "/sessions/ephemeral")):
            from .session_contract import validate_session
            validate_session({**body, **((request_options or {}).get("additional_body_parameters", {}) or {})})
        # Blank values (e.g. `AGORA_AGENTS_V3_BASE_URL=` in a .env file) mean
        # "unset"; surrounding whitespace is ignored. Matches the Go and TS SDKs.
        base = (
            (self.options.base_url or "").strip()
            or os.environ.get("AGORA_AGENTS_V3_BASE_URL", "").strip()
            or "https://preview.ai.agora.io"
        )
        parsed = urlsplit(base)
        if parsed.scheme not in ("https", "http") or not parsed.netloc or parsed.path not in ("", "/") or parsed.query or parsed.fragment or parsed.username is not None or parsed.password is not None or "?" in base or "#" in base:
            raise V3ConfigurationError("v3 base_url must be an HTTP(S) origin without query or fragment")
        base = base.rstrip("/")
        with _reclassify(V3ConfigurationError):
            _validate_public_headers(self.options.headers)
        merged = dict(self.options.headers)
        merged.update({k: v for k, v in headers.items() if v is not None})
        if getattr(self.owner, "auth_mode", None) == "app-credentials" and not any(name.lower() == "authorization" for name in merged):
            with _reclassify(V3ConfigurationError):
                token = generate_convo_ai_token(app_id=self.owner.app_id,
                    app_certificate=self.owner.app_certificate, channel_name="v3", uid=0)
            merged["Authorization"] = f"agora token={token}"
        options = dict(request_options or {})
        forbidden = {"customer_id", "customer_secret", "client_id", "client_secret", "customerId", "customerSecret", "clientId", "clientSecret", "username", "password"}
        if forbidden.intersection(options):
            raise V3ValidationError("Configure Basic credentials with customer_id/customer_secret on the client, or an Authorization header")
        with _reclassify(V3ConfigurationError):
            _validate_public_headers(wrapper.get_headers())
            _validate_public_headers(wrapper.get_custom_headers() or {})
        with _reclassify(V3ValidationError):
            _validate_public_headers(merged)
            _validate_public_headers(options.get("additional_headers", {}))
        if method == "POST" and path.endswith(("/secrets", "/numbers", "/agents")):
            message = "Idempotency-Key is not supported for agent, secret or number creation"
            if any(k.lower() == "idempotency-key" for k in wrapper.get_headers()):
                raise V3ConfigurationError(message)
            if any(k.lower() == "idempotency-key" for source in (merged, options.get("additional_headers", {})) for k in source):
                raise V3ValidationError(message)
        # Retrying these POSTs can create duplicate resources; staging ignores number idempotency.
        if method != "GET":
            options["max_retries"] = 0
        return dict(path=path, method=method, base_url=base, json=_body(body),
                    headers=merged, params=params, request_options=options)

    @staticmethod
    def _parse(response):
        success = 200 <= response.status_code < 300
        try:
            data = response.json() if response.content else None
        except ValueError:
            data = response.text
            if success:
                # Every v3 endpoint returns JSON (or an empty body).
                raise V3ApiError(status_code=response.status_code, headers=dict(response.headers), body=data,
                                 raw_body=response.content, violation="response body is not valid JSON") from None
        if not success:
            error = PreconditionFailedError if response.status_code == 412 else V3ApiError
            raise error(status_code=response.status_code, headers=dict(response.headers), body=data, raw_body=response.content)
        if isinstance(data, dict) and "agent_session_id" in data:
            data = dict(data)
            if "created_at" in data and "create_ts" not in data:
                data["create_ts"] = data.pop("created_at")
            if isinstance(data.get("status"), str):
                data["status"] = data["status"].upper()
        return RawResponse(data=data, headers=response.headers, status_code=response.status_code, response=response)

    def _request(self, method, path, *, body, headers, params, request_options):
        arguments = self._arguments(method, path, body, headers, params, request_options)
        try:
            # The shared client's remaining preflight checks (client headers,
            # HTTPX auth, required Authorization) concern client configuration.
            with _reclassify(V3ConfigurationError):
                try:
                    response = self.owner._client_wrapper.httpx_client.request(**arguments)
                except httpx.RequestError as exc:
                    raise _connection_error(exc, method) from exc
            return self._parse(response)
        except PreconditionFailedError as error:
            latest_path = path.split("/keys/")[0]
            error._latest = lambda: self._request("GET", latest_path, body=None, headers={}, params={}, request_options=_reload_options(request_options)).data
            raise

    def iter_pages(self, **kwargs):
        """Yield cursor pages for this resource; list() itself returns one typed wire page."""
        seen: set = set()
        while True:
            raw = self.with_raw_response.list(**kwargs)
            yield raw.data
            cursor = _next_cursor(raw, seen)
            if cursor is None:
                return
            kwargs["cursor"] = cursor

    def iter_all(self, **kwargs):
        for page in self.iter_pages(**kwargs):
            yield from page["data"]["list"]


def _reload_options(request_options):
    """Keep request context without replaying write preconditions on the reload."""
    options = dict(request_options or {})
    options["_strip_write_preconditions"] = True
    # Additional body parameters belong to the failed write. The reload is a
    # GET and must not carry that body into the fresh read.
    options.pop("additional_body_parameters", None)
    options["additional_headers"] = {
        key: value for key, value in options.get("additional_headers", {}).items()
        if key.lower() not in {"if-match", "if-none-match", "idempotency-key"}
    }
    return options


class AsyncResource(Resource):
    async def _request(self, method, path, *, body, headers, params, request_options):
        arguments = self._arguments(method, path, body, headers, params, request_options)
        try:
            with _reclassify(V3ConfigurationError):
                try:
                    response = await self.owner._client_wrapper.httpx_client.request(**arguments)
                except httpx.RequestError as exc:
                    raise _connection_error(exc, method) from exc
            return self._parse(response)
        except PreconditionFailedError as error:
            async def latest():
                response = await self._request("GET", path.split("/keys/")[0], body=None, headers={}, params={}, request_options=_reload_options(request_options))
                return response.data
            error._latest = latest
            raise

    async def iter_pages(self, **kwargs):
        seen: set = set()
        while True:
            raw = await self.with_raw_response.list(**kwargs)
            yield raw.data
            cursor = _next_cursor(raw, seen)
            if cursor is None:
                return
            kwargs["cursor"] = cursor

    async def iter_all(self, **kwargs):
        async for page in self.iter_pages(**kwargs):
            for item in page["data"]["list"]:
                yield item
