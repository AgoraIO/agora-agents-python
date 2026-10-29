import httpx
import pytest

from agora_agent import Agent, Agora, Area, AsyncAgora

TURN_ENDS = [
    pytest.param({"type": "ok", "metadata": {"playback_duration_ms": 300}}, id="normal-completion"),
    pytest.param(
        {
            "type": "interrupted",
            "metadata": {
                "playback_duration_ms": 120,
                "intended_playback_duration_ms": 300,
                "caused_by": "start_of_speech",
            },
        },
        id="interrupted-playback",
    ),
    pytest.param(
        {"type": "interrupted", "metadata": {"playback_duration_ms": 0, "intended_playback_duration_ms": 0}},
        id="zero-durations",
    ),
    pytest.param({"type": "interrupted", "metadata": {"caused_by": "api_interrupt"}}, id="legacy-response"),
]


def turn_transport(end, pages):
    def handle(request):
        if request.method == "POST":
            return httpx.Response(200, json={"agent_id": "agent-1"})
        assert request.url.path.endswith("/agents/agent-1/turns")
        page = int(request.url.params.get("page_index", "1"))
        pages.append(page)
        return httpx.Response(
            200,
            json={
                "pagination": {"page_index": page, "is_last_page": page == 2},
                "turns": [{"turn_id": page, "end": end}],
            },
        )

    return httpx.MockTransport(handle)


def assert_playback(response, end, turn_count):
    assert len(response.turns) == turn_count
    for turn in response.turns:
        metadata = turn.end.metadata
        assert metadata.playback_duration_ms == end["metadata"].get("playback_duration_ms")
        assert metadata.intended_playback_duration_ms == end["metadata"].get("intended_playback_duration_ms")
        assert turn.end.model_dump(exclude_none=True) == end


@pytest.mark.parametrize("end", TURN_ENDS)
def test_sync_turn_playback_survives_deserialization_and_pagination(end):
    pages = []
    with httpx.Client(transport=turn_transport(end, pages)) as http_client:
        client = Agora(area=Area.US, app_id="0" * 32, app_certificate="1" * 32, httpx_client=http_client)
        session = Agent(client, pipeline_id="pipeline-id").create_session(
            channel="test", token="rtc-token", agent_uid="1", remote_uids=["100"]
        )
        session.start()
        assert_playback(session.get_turns(page_index=1, page_size=1), end, 1)
        assert_playback(session.get_all_turns(page_size=1), end, 2)
    assert pages == [1, 1, 2]


@pytest.mark.asyncio
@pytest.mark.parametrize("end", TURN_ENDS)
async def test_async_turn_playback_survives_deserialization_and_pagination(end):
    pages = []
    async with httpx.AsyncClient(transport=turn_transport(end, pages)) as http_client:
        client = AsyncAgora(area=Area.US, app_id="0" * 32, app_certificate="1" * 32, httpx_client=http_client)
        session = Agent(client, pipeline_id="pipeline-id").create_async_session(
            channel="test", token="rtc-token", agent_uid="1", remote_uids=["100"]
        )
        await session.start()
        assert_playback(await session.get_turns(page_index=1, page_size=1), end, 1)
        assert_playback(await session.get_all_turns(page_size=1), end, 2)
    assert pages == [1, 1, 2]
