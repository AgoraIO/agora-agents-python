from agora_agent.agentkit import generate_convo_ai_token


def test_avatar_tokens_use_convo_ai_token_path_with_avatar_uid():
    token = generate_convo_ai_token(
        app_id="0" * 32,
        app_certificate="1" * 32,
        channel_name="room",
        uid=123,
    )

    assert token.startswith("007")
