from agora_agent import (
    Agent,
    FillerWordsContentGeneratedConfig,
    FillerWordsContentGeneratedConfigLlmProvider,
    FillerWordsConfig,
    FillerWordsContent,
    FillerWordsContentStaticConfig,
    LlmToolConfig,
)
from test_helpers import test_client


def test_generated_filler_types_are_public_and_constructible() -> None:
    provider = FillerWordsContentGeneratedConfigLlmProvider(
        base_url="https://api.openai.com/v1/chat/completions",
        api_key="filler-key",
        params={"model": "gpt-4o-mini"},
    )
    config = FillerWordsContentGeneratedConfig(llm_provider=provider, prompt="Generate a short filler phrase")

    assert config.llm_provider.api_key == "filler-key"
    assert config.fallback_strategy == "static"
    assert LlmToolConfig.__name__ == "LlmTool"


def test_agentkit_serializes_generated_filler_words() -> None:
    generated = FillerWordsConfig(
        enable=True,
        content=FillerWordsContent(
            mode="generated",
            static_config=FillerWordsContentStaticConfig(phrases=["One moment..."]),
            generated_config=FillerWordsContentGeneratedConfig(
                llm_provider=FillerWordsContentGeneratedConfigLlmProvider(
                    base_url="https://api.openai.com/v1/chat/completions",
                    api_key="filler-key",
                    params={"model": "gpt-4o-mini"},
                ),
                prompt="Generate a short filler phrase",
            ),
        ),
    )
    properties = Agent(test_client()).with_filler_words(generated).to_properties(
        channel="test-channel",
        agent_uid="1",
        remote_uids=[],
        token="token",
        skip_vendor_validation=True,
    )

    filler_words = properties.filler_words
    assert filler_words is not None
    assert filler_words.content is not None
    assert filler_words.content.mode == "generated"
    assert filler_words.content.generated_config is not None
    assert filler_words.content.generated_config.prompt == "Generate a short filler phrase"
    assert filler_words.content.generated_config.llm_provider.api_key == "filler-key"
