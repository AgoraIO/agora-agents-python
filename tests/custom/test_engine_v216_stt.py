from __future__ import annotations

import json
from typing import Type, Union, get_args

import httpx
import pytest
from pydantic import ValidationError

from agora_agent import Agent, AgentClient, Area, ElevenLabsSTT, ElevenLabsTTS, FishAudioSTT, OpenAI
from agora_agent.agentkit.regional_agent import CNSTT, GlobalSTT
from agora_agent.agentkit.vendors.catalog import CN_VENDOR_NAMESPACE, GLOBAL_VENDOR_NAMESPACE
from agora_agent.agentkit.vendors.namespaces import CNSTTVendors, GlobalSTTVendors
from agora_agent.agentkit.vendors.region import CN_ASR_VENDORS, GLOBAL_ASR_VENDORS
from agora_agent.cn import QwenSTT

AsrProvider = Union[ElevenLabsSTT, FishAudioSTT, QwenSTT]


@pytest.mark.parametrize(
    "provider,vendor,area",
    [(ElevenLabsSTT, "elevenlabs", Area.US), (FishAudioSTT, "fishaudio", Area.US), (QwenSTT, "qwen", Area.CN)],
)
def test_new_asr_survives_start_request(provider: Type[AsrProvider], vendor: str, area: Area) -> None:
    requests = []

    def record(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"agent_id": "agent-1"})

    client = AgentClient(
        area=area, app_id="0" * 32, app_certificate="1" * 32,
        httpx_client=httpx.Client(transport=httpx.MockTransport(record)),
    )
    additional = {"api_key": "ignored", "enabled": False, "keywords": []}
    stt = provider(api_key="asr-key", additional_params=additional)
    agent = (
        Agent(client, turn_detection={"language": "zh-CN"}).with_stt(stt)
        .with_llm(OpenAI(model="gpt-4o-mini"))
        .with_tts(ElevenLabsTTS(
            key="tts-key", voice_id="voice", model_id="eleven_flash_v2_5", base_url="wss://api.elevenlabs.io/v1",
        ))
    )
    props = agent.to_properties(
        channel="room", token="rtc-token", agent_uid="1", remote_uids=["100"],
    )
    expected = {
        "vendor": vendor, "language": "zh-CN",
        "params": {"api_key": "asr-key", "enabled": False, "keywords": []},
    }
    assert props.model_dump(exclude_none=True)["asr"] == expected
    agent.create_session(channel="room", token="rtc-token", agent_uid="1", remote_uids=["100"]).start()
    assert len(requests) == 1
    assert json.loads(requests[0].content)["properties"]["asr"] == expected
    assert additional["api_key"] == "ignored"

    for invalid in ({}, {"api_key": ""}):
        with pytest.raises(ValidationError, match="api_key"):
            provider(**invalid)


@pytest.mark.parametrize("provider,vendor", [(ElevenLabsSTT, "elevenlabs"), (FishAudioSTT, "fishaudio")])
def test_new_global_asr_catalogs(provider: Type[AsrProvider], vendor: str) -> None:
    assert GLOBAL_VENDOR_NAMESPACE.asr[vendor] is provider
    assert vendor not in CN_VENDOR_NAMESPACE.asr
    assert getattr(GlobalSTTVendors, vendor) is provider
    assert not hasattr(CNSTTVendors, vendor)
    assert provider in get_args(GlobalSTT)
    assert provider not in get_args(CNSTT)
    assert vendor in GLOBAL_ASR_VENDORS
    assert vendor not in CN_ASR_VENDORS


def test_qwen_is_a_cn_asr_provider() -> None:
    assert CN_VENDOR_NAMESPACE.asr["qwen"] is QwenSTT
    assert "qwen" not in GLOBAL_VENDOR_NAMESPACE.asr
    assert CNSTTVendors.qwen is QwenSTT
    assert not hasattr(GlobalSTTVendors, "qwen")
    assert QwenSTT in get_args(CNSTT)
    assert QwenSTT not in get_args(GlobalSTT)
    assert "qwen" in CN_ASR_VENDORS
    assert "qwen" not in GLOBAL_ASR_VENDORS
