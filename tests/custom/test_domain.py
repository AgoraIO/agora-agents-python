from typing import List

import httpx
import pytest

from agora_agent import Agora
from agora_agent.core.domain import Area, AsyncResolverImpl, Pool, ResolverImpl

_API_BASE_URL_ENV = "AGORA_AGENTS_API_BASE_URL"


@pytest.mark.parametrize(
    ("area", "expected"),
    [
        (Area.US, "https://api-test.agora.io/api/conversational-ai-agent"),
        (Area.EU, "https://api-test.agora.io/api/conversational-ai-agent"),
        (Area.AP, "https://api-test.agora.io/api/conversational-ai-agent"),
        (Area.CN, "https://api-test.agora.io/cn/api/conversational-ai-agent"),
    ],
)
def test_pool_uses_configured_base_url(
    monkeypatch: pytest.MonkeyPatch,
    area: Area,
    expected: str,
) -> None:
    monkeypatch.setenv(_API_BASE_URL_ENV, "https://api-test.agora.io/")

    assert Pool(area).get_current_url() == expected


@pytest.mark.parametrize(
    ("base_url", "expected"),
    [
        (
            "https://staging.example.com/",
            "https://staging.example.com/api/conversational-ai-agent",
        ),
        (
            "http://localhost:8080",
            "http://localhost:8080/api/conversational-ai-agent",
        ),
        (
            "https://user:password@staging.example.com/gateway?debug=true#section",
            "https://user:password@staging.example.com/gateway/api/conversational-ai-agent?debug=true#section",
        ),
    ],
)
def test_pool_accepts_configured_base_url(
    monkeypatch: pytest.MonkeyPatch,
    base_url: str,
    expected: str,
) -> None:
    monkeypatch.setenv(_API_BASE_URL_ENV, base_url)

    assert Pool(Area.US).get_current_url() == expected


def test_configured_base_url_disables_dynamic_routing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(_API_BASE_URL_ENV, "https://api-test.agora.io")
    pool = Pool(Area.US)
    pool._resolver = _FailingResolver()

    expected = "https://api-test.agora.io/api/conversational-ai-agent"
    for _ in range(3):
        pool.next_region()
        pool.select_best_domain()
        assert pool.get_current_url() == expected


@pytest.mark.asyncio
async def test_configured_base_url_disables_async_domain_selection(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(_API_BASE_URL_ENV, "https://api-test.agora.io")
    pool = Pool(Area.CN)
    pool._async_resolver = _FailingAsyncResolver()

    await pool.select_best_domain_async()

    assert pool.get_current_url() == "https://api-test.agora.io/cn/api/conversational-ai-agent"


def test_pool_without_configured_base_url_keeps_regional_routing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(_API_BASE_URL_ENV, raising=False)
    pool = Pool(Area.US)

    assert pool.get_current_url() == "https://api-us-west-1.agora.io/api/conversational-ai-agent"

    pool.next_region()

    assert pool.get_current_url() == "https://api-us-east-1.agora.io/api/conversational-ai-agent"


def test_client_uses_configured_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(_API_BASE_URL_ENV, "https://api-test.agora.io")

    with httpx.Client() as httpx_client:
        client = Agora(
            area=Area.CN,
            app_id="0" * 32,
            app_certificate="1" * 32,
            httpx_client=httpx_client,
        )

        expected = "https://api-test.agora.io/cn/api/conversational-ai-agent"
        assert client.get_current_url() == expected
        assert client._client_wrapper.get_base_url() == expected


class _FailingResolver(ResolverImpl):
    def resolve(self, domains: List[str], region_prefix: str) -> str:
        raise AssertionError("resolver should not be called")


class _FailingAsyncResolver(AsyncResolverImpl):
    async def resolve_async(self, domains: List[str], region_prefix: str) -> str:
        raise AssertionError("async resolver should not be called")
