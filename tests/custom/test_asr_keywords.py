from agora_agent import AresSTT, FengmingSTT


def test_ares_keywords_are_top_level() -> None:
    assert AresSTT(
        keywords=["Agora"],
        additional_params={"custom": True},
    ).to_config() == {
        "vendor": "ares",
        "keywords": ["Agora"],
        "params": {"custom": True},
    }


def test_fengming_keywords_are_top_level() -> None:
    assert FengmingSTT(
        keywords=["Agora"],
        additional_params={"custom": True},
    ).to_config() == {
        "vendor": "fengming",
        "keywords": ["Agora"],
        "params": {"custom": True},
    }
