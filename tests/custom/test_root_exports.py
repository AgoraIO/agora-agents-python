import pytest

import agora_agent
import agora_agent.agentkit as agentkit


def test_root_exports_match_agentkit_for_common_symbols() -> None:
    for name in (
        "Agent",
        "CNAgent",
        "GlobalAgent",
        "RegionalAgent",
        "DeepgramSTT",
        "GradiumTTS",
        "MistralTTS",
        "MiniMaxCNTTS",
        "TencentSTT",
        "OpenAI",
        "SpatiusAvatar",
        "AgentPresets",
        "generate_rtc_token",
        "generate_client_token",
        "CredentialMode",
        "DataChannel",
    ):
        assert getattr(agora_agent, name) is getattr(agentkit, name)


def test_root_exports_fern_client_symbols() -> None:
    assert agora_agent.Agora is not None
    assert agora_agent.AgentClient is not None
    assert agora_agent.Area is not None
    assert agora_agent.AsyncAgora is not None


def test_credential_mode_constants() -> None:
    assert agora_agent.CredentialMode.MANAGED == "managed"
    assert agora_agent.CredentialMode.BYOK == "byok"


def test_unknown_root_export_raises_attribute_error() -> None:
    with pytest.raises(AttributeError):
        _ = agora_agent.NotARealExportName


def test_dir_includes_agentkit_vendor_exports() -> None:
    assert "DeepgramSTT" in dir(agora_agent)
    assert "GradiumTTS" in dir(agora_agent)
    assert "MistralTTS" in dir(agora_agent)
    assert "MiniMaxCNTTS" in dir(agora_agent)
    assert "TencentSTT" in dir(agora_agent)
    assert "CNAgent" in dir(agora_agent)
    assert "AgentClient" in dir(agora_agent)


def test_all_includes_agentkit_vendor_exports() -> None:
    assert "CredentialMode" in agora_agent.__all__
    assert "DeepgramSTT" in agora_agent.__all__
    assert "GradiumTTS" in agora_agent.__all__
    assert "MistralTTS" in agora_agent.__all__
    assert "MiniMaxCNTTS" in agora_agent.__all__
    assert "TencentSTT" in agora_agent.__all__
    assert "OpenAI" in agora_agent.__all__
    assert "SpatiusAvatar" in agora_agent.__all__
    assert "CNAgent" in agora_agent.__all__
    assert "AgentClient" in agora_agent.__all__
