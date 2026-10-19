"""v3 transport adapter: share the owning client's auth, HTTP client and pool."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Generic, Mapping, Optional, TypeVar
from urllib.parse import quote, urlsplit

import httpx
from ..agentkit.token import generate_convo_ai_token
from ..core.api_error import ApiError

_UNSET: Any = object()
T = TypeVar("T")


@dataclass(frozen=True)
class V3Options:
    """Staging overrides. base_url is the origin, without the v3 project path."""
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


class PreconditionFailedError(ApiError):
    """The server rejected an outdated If-Match. latest() reloads the resource.

    With AsyncAgora, await error.latest(). No write is automatically retried.
    """
    def latest(self):
        return self._latest()



def segment(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("v3 path identifiers must be nonempty strings")
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
        base = self.options.base_url or os.environ.get("AGORA_AGENTS_V3_BASE_URL")
        if not base:
            # The existing pool's base may include the v2 path; v3 uses the same origin.
            current = urlsplit(wrapper.get_base_url())
            base = f"{current.scheme}://{current.netloc}"
        parsed = urlsplit(base)
        if parsed.scheme not in ("https", "http") or not parsed.netloc or parsed.path not in ("", "/") or parsed.query or parsed.fragment:
            raise ValueError("v3 base_url must be an HTTP(S) origin without query or fragment")
        base = base.rstrip("/")
        merged = dict(self.options.headers)
        merged.update({k: v for k, v in headers.items() if v is not None})
        if getattr(self.owner, "auth_mode", None) == "app-credentials":
            token = generate_convo_ai_token(app_id=self.owner.app_id,
                app_certificate=self.owner.app_certificate, channel_name="v3", uid=0)
            merged.setdefault("Authorization", f"agora token={token}")
        options = dict(request_options or {})
        # Retrying these POSTs can create duplicate resources; staging ignores number idempotency.
        if method != "GET":
            options["max_retries"] = 0
        return dict(path=path, method=method, base_url=base, json=_body(body),
                    headers=merged, params=params, request_options=options)

    @staticmethod
    def _parse(response):
        try:
            data = response.json() if response.content else None
        except ValueError:
            data = response.text
        if not 200 <= response.status_code < 300:
            error = PreconditionFailedError if response.status_code == 412 else ApiError
            raise error(status_code=response.status_code, headers=dict(response.headers), body=data)
        return RawResponse(data=data, headers=response.headers, status_code=response.status_code, response=response)

    def _request(self, method, path, *, body, headers, params, request_options):
        try:
            return self._parse(self.owner._client_wrapper.httpx_client.request(
                **self._arguments(method, path, body, headers, params, request_options)))
        except PreconditionFailedError as error:
            latest_path = path.split("/keys/")[0]
            error._latest = lambda: self._request("GET", latest_path, body=None, headers={}, params={}, request_options=_reload_options(request_options)).data
            raise

    def iter_pages(self, **kwargs):
        """Yield cursor pages for this resource; list() itself returns one typed wire page."""
        seen = set()
        while True:
            page = self.list(**kwargs)
            yield page
            if not page.get("has_more"):
                return
            cursor = page.get("next_cursor")
            if not cursor or cursor in seen:
                raise ValueError("Invalid or repeated v3 pagination cursor")
            seen.add(cursor)
            kwargs["cursor"] = cursor

    def iter_all(self, **kwargs):
        for page in self.iter_pages(**kwargs):
            yield from page["data"]["list"]


def _reload_options(request_options):
    """Keep request context without replaying write preconditions on the reload."""
    options = dict(request_options or {})
    options["additional_headers"] = {
        key: value for key, value in options.get("additional_headers", {}).items()
        if key.lower() not in {"if-match", "if-none-match", "idempotency-key"}
    }
    return options


class AsyncResource(Resource):
    async def _request(self, method, path, *, body, headers, params, request_options):
        try:
            return self._parse(await self.owner._client_wrapper.httpx_client.request(
                **self._arguments(method, path, body, headers, params, request_options)))
        except PreconditionFailedError as error:
            async def latest():
                response = await self._request("GET", path.split("/keys/")[0], body=None, headers={}, params={}, request_options=_reload_options(request_options))
                return response.data
            error._latest = latest
            raise

    async def iter_pages(self, **kwargs):
        seen = set()
        while True:
            page = await self.list(**kwargs)
            yield page
            if not page.get("has_more"):
                return
            cursor = page.get("next_cursor")
            if not cursor or cursor in seen:
                raise ValueError("Invalid or repeated v3 pagination cursor")
            seen.add(cursor)
            kwargs["cursor"] = cursor

    async def iter_all(self, **kwargs):
        async for page in self.iter_pages(**kwargs):
            for item in page["data"]["list"]:
                yield item
