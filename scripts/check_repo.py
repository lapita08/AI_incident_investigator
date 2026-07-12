#!/usr/bin/env python3
"""Run lightweight repository checks that do not need project dependencies."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PATHS = [
    "README.md",
    "LICENSE",
    "Makefile",
    "docker-compose.yml",
    ".env.example",
    "backend/pyproject.toml",
    "backend/app/main.py",
    "frontend/package.json",
    "frontend/src/App.tsx",
    "docs/architecture.md",
    "docs/threat-model.md",
    "sample-data/db-latency-incident/scenario.json",
    "sample-data/memory-leak-incident/scenario.json",
]


def check_required_paths() -> list[str]:
    errors: list[str] = []
    for relative_path in REQUIRED_PATHS:
        if not (ROOT / relative_path).exists():
            errors.append(f"Missing required path: {relative_path}")
    return errors


def check_sample_json() -> list[str]:
    errors: list[str] = []
    for path in sorted((ROOT / "sample-data").glob("*/scenario.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}")
            continue

        if "incident" not in payload:
            errors.append(f"{path.relative_to(ROOT)} is missing incident metadata")
        if not payload.get("evidence"):
            errors.append(f"{path.relative_to(ROOT)} has no evidence items")
    return errors


def check_readme_style() -> list[str]:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    errors: list[str] = []
    if "\u2014" in readme or "\u2013" in readme:
        errors.append("README.md contains an en dash or em dash")
    if "```mermaid" not in readme:
        errors.append("README.md should include at least one Mermaid flowchart")
    return errors


def check_git_status() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return []

    changes = [line for line in result.stdout.splitlines() if not line.startswith("?? scripts/")]
    if changes:
        return ["Working tree has uncommitted changes outside the new scripts"]
    return []


def main() -> int:
    checks = [
        ("required paths", check_required_paths),
        ("sample JSON", check_sample_json),
        ("README style", check_readme_style),
        ("git status", check_git_status),
    ]
    all_errors: list[str] = []
    for label, check in checks:
        errors = check()
        if errors:
            print(f"FAIL {label}")
            for error in errors:
                print(f"  - {error}")
            all_errors.extend(errors)
        else:
            print(f"OK   {label}")

    return 1 if all_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
