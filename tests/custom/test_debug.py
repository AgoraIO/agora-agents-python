import json
from typing import List

import httpx

from agora_agent import Agent, Agora, Area, Gemini, GeminiSTT, GoogleTTS
from agora_agent.agentkit.debug import REDACTED, redact_secrets

API_KEY = "test-google-api-key"
APP_ID = "0" * 32
APP_CERTIFICATE = "1" * 32


class _Recorder(httpx.MockTransport):
    def __init__(self) -> None:
        self.requests: List[httpx.Request] = []
        super().__init__(self._handle)

    def _handle(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return httpx.Response(200, json={"agent_id": "agent-1"})


def test_redact_secrets_walks_nested_structures() -> None:
    redacted = redact_secrets(
        {
            "appid": APP_ID,
            "properties": {
                "token": "007eJxTYKhsrH10",
                "asr": {"vendor": "gemini", "params": {"api_key": API_KEY, "model": "m"}},
                "mcp_servers": [{"name": "a", "headers": {"authorization": "Bearer x"}}],
            },
        }
    )

    assert redacted == {
        "appid": REDACTED,
        "properties": {
            "token": REDACTED,
            "asr": {"vendor": "gemini", "params": {"api_key": REDACTED, "model": "m"}},
            "mcp_servers": [{"name": "a", "headers": {"authorization": REDACTED}}],
        },
    }


def test_redact_secrets_covers_query_keys_and_google_credentials() -> None:
    redacted = redact_secrets(
        {
            "llm": {
                "url": (
                    "https://generativelanguage.googleapis.com/v1beta/models/"
                    f"gemini-2.0-flash:streamGenerateContent?alt=sse&key={API_KEY}"
                ),
            },
            "tts": {"params": {"credentials": API_KEY}},
        }
    )

    assert API_KEY not in json.dumps(redacted)


def test_redact_secrets_leaves_empty_values_visible() -> None:
    assert redact_secrets({"params": {"api_key": ""}}) == {"params": {"api_key": ""}}


def test_redact_secrets_does_not_mutate_input() -> None:
    original = {"properties": {"asr": {"params": {"api_key": API_KEY}}}}
    redact_secrets(original)

    assert original["properties"]["asr"]["params"]["api_key"] == API_KEY


def test_debug_output_redacts_credentials_without_changing_request(capsys) -> None:
    recorder = _Recorder()
    client = Agora(
        area=Area.US,
        app_id=APP_ID,
        app_certificate=APP_CERTIFICATE,
        httpx_client=httpx.Client(transport=recorder),
    )
    agent = (
        Agent(client=client)
        .with_stt(
            GeminiSTT(
                api_key=API_KEY,
                model="gemini-3.7-transcribe-live",
                language="en-US",
                word_timestamp=True,
            )
        )
        .with_llm(Gemini(api_key=API_KEY, model="gemini-2.0-flash"))
        .with_tts(
            GoogleTTS(
                key=API_KEY,
                voice_name="en-US-Chirp3-HD-Charon",
                language_code="en-US",
            )
        )
    )

    agent.create_session(
        channel="debug-channel",
        agent_uid="1",
        remote_uids=["100"],
        debug=True,
    ).start()

    output = capsys.readouterr().out
    assert API_KEY not in output
    assert "gemini-3.7-transcribe-live" in output

    sent = json.loads(recorder.requests[0].content)
    assert sent["properties"]["asr"]["params"]["api_key"] == API_KEY
