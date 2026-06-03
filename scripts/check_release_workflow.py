#!/usr/bin/env python3

import re
import sys
from pathlib import Path
from typing import NoReturn


def fail(message: str) -> NoReturn:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def read_version(path: str) -> str:
    text = Path(path).read_text()
    match = re.search(r'^version\s*=\s*"v?([^"]+)"', text, re.M)
    if not match:
        fail(f"version not found in {path}")
    return match.group(1)


def read_compat_dependency(path: str) -> str:
    text = Path(path).read_text()
    match = re.search(r'^agora-agents\s*=\s*"([^"]+)"', text, re.M)
    if not match:
        fail(f"agora-agents dependency not found in {path}")
    return match.group(1)


root_version = read_version("pyproject.toml")
compat_pyproject = "compat/agora-agent-server-sdk/pyproject.toml"
compat_version = read_version(compat_pyproject)
compat_dependency = read_compat_dependency(compat_pyproject)

if compat_version != root_version:
    fail(f"Compat package version ({compat_version}) must match root package version ({root_version}).")

expected_dependency = f">={root_version},<3.0.0"
if compat_dependency != expected_dependency:
    fail(f"Compat package dependency on agora-agents ({compat_dependency}) must be {expected_dependency}.")

release_workflow = Path(".github/workflows/release.yml").read_text()
required_workflow_markers = [
    ("contents: write", "release workflow must have contents: write so it can create GitHub releases"),
    ("gh release create", "release workflow must create a GitHub release when one does not exist"),
    ("gh release edit", "release workflow must update an existing GitHub release"),
    ("release_notes.md", "release workflow must generate and use a release notes file"),
]

for marker, message in required_workflow_markers:
    if marker not in release_workflow:
        fail(message)

print("Release metadata and workflow checks passed.")
