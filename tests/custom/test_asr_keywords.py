import pytest
from pydantic import ValidationError

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


@pytest.mark.parametrize("vendor", [AresSTT, FengmingSTT])
def test_keywords_cannot_be_duplicated_in_vendor_params(vendor: type) -> None:
    with pytest.raises(ValidationError, match="use the top-level keywords field"):
        vendor(additional_params={"keywords": ["Agora"]})
