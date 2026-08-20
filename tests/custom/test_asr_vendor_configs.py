from agora_agent import AresSTT, GeminiSTT
from agora_agent.agentkit.vendors.catalog import GLOBAL_VENDOR_NAMESPACE
from agora_agent.agentkit.vendors.region import GLOBAL_ASR_VENDORS


def test_gemini_stt_serializes_generated_params() -> None:
    config = GeminiSTT(
        api_key="gemini-key",
        model="gemini-transcribe",
        sample_rate=16000,
        language="en-US",
        word_timestamp=True,
    ).to_config()

    assert config == {
        "vendor": "gemini",
        "params": {
            "api_key": "gemini-key",
            "model": "gemini-transcribe",
            "sample_rate": 16000,
            "language": "en-US",
            "word_timestamp": True,
        },
    }
    assert "gemini" in GLOBAL_ASR_VENDORS
    assert GLOBAL_VENDOR_NAMESPACE.asr["gemini"] is GeminiSTT


def test_ares_keywords_are_top_level() -> None:
    assert AresSTT(keywords=["Agora"]).to_config() == {
        "vendor": "ares",
        "keywords": ["Agora"],
    }
