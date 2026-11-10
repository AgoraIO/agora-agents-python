"""MLLM is enabled through ``advanced_features.enable_mllm``, never ``mllm.enable``.

Live A/B tests showed that when ``mllm.enable`` is in the join body (alone or
together with ``advanced_features.enable_mllm``) RTM ``message.metrics`` never
arrive. Audio and transcripts are unaffected, so the SDK must never send it.
"""

import json
from typing import Any, Dict, List

import httpx
import pytest

from agora_agent import Agent, Agora, Area, Gemini, GeminiSTT, GoogleTTS
from agora_agent.agentkit.vendors import (
    AzureOpenAIRealtime,
    GeminiLive,
    GeminiLiveModels,
    OpenAIGPTLive,
    OpenAIRealtime,
    QwenOmni,
    VertexAI,
    XaiGrok,
)
from agora_agent.agentkit.vendors.base import BaseMLLM
from agora_agent.agents.types.start_agents_request_properties_advanced_features import (
    StartAgentsRequestPropertiesAdvancedFeatures,
)

API_KEY = "test-mllm-api-key"
APP_ID = "0" * 32
APP_CERTIFICATE = "1" * 32


class _Recorder(httpx.MockTransport):
    def __init__(self) -> None:
        self.requests: List[httpx.Request] = []
        super().__init__(self._handle)

    def _handle(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return httpx.Response(200, json={"agent_id": "agent-1"})


class _RawMLLM(BaseMLLM):
    """A custom vendor whose raw config still carries the old ``enable`` flag."""

    def to_config(self) -> Dict[str, Any]:
        return {"enable": True, "vendor": "openai", "api_key": API_KEY, "params": {"model": "gpt-realtime"}}


def _start(agent_factory, area: Area = Area.US) -> httpx.Request:
    recorder = _Recorder()
    client = Agora(
        area=area, app_id=APP_ID, app_certificate=APP_CERTIFICATE, httpx_client=httpx.Client(transport=recorder)
    )
    agent_factory(Agent(client=client)).create_session(
        name="enable-fix", channel="enable-fix-channel", agent_uid="1", remote_uids=["100"]
    ).start()
    assert len(recorder.requests) == 1
    return recorder.requests[0]


def _properties(request: httpx.Request) -> Dict[str, Any]:
    return json.loads(request.content)["properties"]


MLLM_VENDORS = {
    "gemini-ga": lambda: GeminiLive(api_key=API_KEY, model=GeminiLiveModels.LIVE_38),
    "gemini-ga-extended-thinking": lambda: GeminiLive(
        api_key=API_KEY, model=GeminiLiveModels.LIVE_38_EXTENDED_THINKING, thinking_level="low"
    ),
    "openai-realtime": lambda: OpenAIRealtime(api_key=API_KEY),
    "openai-gpt-live": lambda: OpenAIGPTLive(api_key=API_KEY),
    "azure-openai-realtime": lambda: AzureOpenAIRealtime(
        url="wss://azure.example/realtime", api_key=API_KEY, turn_detection={"mode": "server_vad"}
    ),
    "xai-grok": lambda: XaiGrok(api_key=API_KEY),
    "vertex-ai": lambda: VertexAI(
        model="gemini-live", project_id="project", location="us-central1", adc_credentials_string="{}"
    ),
    "raw-config-with-enable": lambda: _RawMLLM(),
}


@pytest.mark.parametrize("vendor", sorted(MLLM_VENDORS))
def test_every_mllm_vendor_sends_enable_mllm_and_never_mllm_enable(vendor: str) -> None:
    properties = _properties(_start(lambda agent: agent.with_mllm(MLLM_VENDORS[vendor]())))

    assert properties["advanced_features"] == {"enable_mllm": True}
    assert "enable" not in properties["mllm"]
    for absent in ("asr", "llm", "tts"):
        assert properties.get(absent) is None


def test_cn_mllm_vendor_sends_enable_mllm_and_never_mllm_enable() -> None:
    properties = _properties(
        _start(lambda agent: agent.with_mllm(QwenOmni(api_key=API_KEY, url="wss://qwen.example/realtime")), Area.CN)
    )

    assert properties["advanced_features"] == {"enable_mllm": True}
    assert "enable" not in properties["mllm"]


def test_raw_mllm_enable_is_dropped_from_builder_and_session_paths() -> None:
    agent = Agent(client=Agora(area=Area.US, app_id=APP_ID, app_certificate=APP_CERTIFICATE)).with_mllm(_RawMLLM())
    properties = agent.to_properties(channel="c", agent_uid="1", remote_uids=["100"], token="rtc-token")

    assert properties.mllm is not None and properties.mllm.enable is None
    assert properties.advanced_features is not None and properties.advanced_features.enable_mllm is True


@pytest.mark.parametrize(
    "features",
    [
        {"enable_rtm": True},
        {"enable_rtm": True, "enable_mllm": False},
        StartAgentsRequestPropertiesAdvancedFeatures(enable_rtm=True),
        StartAgentsRequestPropertiesAdvancedFeatures(enable_rtm=True, enable_mllm=False),
    ],
    ids=["dict", "dict-with-false", "model", "model-with-false"],
)
def test_enable_mllm_merges_with_caller_advanced_features(features: Any) -> None:
    properties = _properties(
        _start(lambda agent: agent.with_advanced_features(features).with_mllm(OpenAIRealtime(api_key=API_KEY)))
    )

    assert properties["advanced_features"] == {"enable_rtm": True, "enable_mllm": True}
    assert properties["parameters"]["data_channel"] == "rtm"
    assert "enable" not in properties["mllm"]


def test_enable_mllm_merges_regardless_of_builder_order() -> None:
    properties = _properties(
        _start(
            lambda agent: agent.with_mllm(GeminiLive(api_key=API_KEY))
            .with_advanced_features({"enable_rtm": True})
            .with_tools()
        )
    )

    assert properties["advanced_features"] == {"enable_rtm": True, "enable_tools": True, "enable_mllm": True}


def test_builder_keeps_the_caller_advanced_features_unchanged() -> None:
    agent = Agent(client=Agora(area=Area.US, app_id=APP_ID, app_certificate=APP_CERTIFICATE))
    agent = agent.with_advanced_features({"enable_rtm": True}).with_mllm(OpenAIRealtime(api_key=API_KEY))

    assert agent.advanced_features == {"enable_rtm": True}
    assert agent.mllm is not None and "enable" not in agent.mllm


def _cascading(agent: Agent) -> Agent:
    return (
        agent.with_stt(GeminiSTT(api_key=API_KEY, model="gemini-3.7-transcribe-live", language="en-US"))
        .with_llm(Gemini(api_key=API_KEY, model="gemini-2.0-flash"))
        .with_tts(GoogleTTS(key=API_KEY, voice_name="en-US-Chirp3-HD-Charon", language_code="en-US"))
    )


def test_cascading_path_never_gets_enable_mllm() -> None:
    properties = _properties(_start(_cascading))

    assert "advanced_features" not in properties
    assert "mllm" not in properties
    for present in ("asr", "llm", "tts"):
        assert present in properties


@pytest.mark.parametrize(
    "features",
    [
        {"enable_rtm": True, "enable_mllm": True},
        StartAgentsRequestPropertiesAdvancedFeatures(enable_rtm=True, enable_mllm=True),
    ],
    ids=["dict", "model"],
)
def test_cascading_path_keeps_caller_flags_and_drops_enable_mllm(features: Any) -> None:
    properties = _properties(_start(lambda agent: _cascading(agent.with_advanced_features(features))))

    assert properties["advanced_features"] == {"enable_rtm": True}
    assert "mllm" not in properties


def test_cascading_path_omits_advanced_features_left_empty() -> None:
    properties = _properties(_start(lambda agent: _cascading(agent.with_advanced_features({"enable_mllm": True}))))

    assert "advanced_features" not in properties
