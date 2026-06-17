from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

SCANNED_MARKDOWN = [
    ROOT / "README.md",
    *sorted((ROOT / "docs").rglob("*.md")),
]

SKIP_LANGS = {
    "bash",
    "console",
    "go",
    "javascript",
    "js",
    "json",
    "shell",
    "sh",
    "text",
    "ts",
    "typescript",
    "yaml",
    "yml",
}

PYTHON_HINTS = (
    "from agora_agent",
    "import agora_agent",
    "Agent(",
    "OpenAI(",
    "OpenAITTS(",
    "OpenAISTT(",
    "MiniMaxTTS(",
    "DeepgramSTT(",
    "GoogleTTS(",
    "RimeTTS(",
    "VertexAI(",
    "VertexAILLM(",
)

BLOCKED_TERMS = {
    "apiKey": "api_key",
    "baseUrl": "base_url",
    "modelId": "model_id",
    "voiceId": "voice_id",
    "groupId": "group_id",
    "projectId": "project_id",
    "resourceName": "resource_name",
    "deploymentName": "deployment_name",
    "inputAudioTranscription": "input_audio_transcription",
    "greetingMessage": "greeting_message",
    "failureMessage": "failure_message",
    "turnDetection": "turn_detection",
    "adcCredentialsString": "adc_credentials_string",
    "sampleRate": "sample_rate",
    "targetLanguageCode": "target_language_code",
}

FENCE_RE = re.compile(r"^```(?P<lang>[^\n`]*)\n(?P<body>.*?)(?:^```)", re.MULTILINE | re.DOTALL)


def _should_scan(lang: str, body: str) -> bool:
    lang_parts = lang.strip().split(maxsplit=1)
    normalized = lang_parts[0].lower() if lang_parts else ""
    if normalized in {"python", "py"}:
        return True
    if normalized in SKIP_LANGS:
        return False
    if normalized:
        return False
    return any(hint in body for hint in PYTHON_HINTS)


def test_python_docs_examples_use_snake_case_kwargs() -> None:
    failures: list[str] = []

    for path in SCANNED_MARKDOWN:
        text = path.read_text()
        for match in FENCE_RE.finditer(text):
            body = match.group("body")
            if not _should_scan(match.group("lang"), body):
                continue

            line_offset = text[: match.start("body")].count("\n")
            for term, replacement in BLOCKED_TERMS.items():
                for term_match in re.finditer(rf"\b{re.escape(term)}\b", body):
                    line = line_offset + body[: term_match.start()].count("\n") + 1
                    failures.append(f"{path.relative_to(ROOT)}:{line}: use {replacement} instead of {term}")

    assert not failures, "CamelCase kwargs found in Python docs examples:\n" + "\n".join(failures)
