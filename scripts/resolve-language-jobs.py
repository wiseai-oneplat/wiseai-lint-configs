#!/usr/bin/env python3
"""Resolve a comma-separated language list into reusable workflow job switches."""

from __future__ import annotations

import argparse
import json
import pathlib
from collections.abc import Iterable


LANGUAGE_TO_JOBS = {
    "python": {"semgrep", "ast_grep"},
    "go": {"semgrep", "ast_grep"},
    "java": {"semgrep", "ast_grep"},
    "typescript": {"semgrep", "ast_grep"},
    "javascript": {"semgrep", "ast_grep"},
    "vue": {"ast_grep"},
    "c": {"semgrep", "ast_grep", "cppcheck"},
    "cpp": {"semgrep", "ast_grep", "cppcheck"},
    "css": {"ast_grep", "stylelint"},
    "shell": {"shellcheck"},
    "dockerfile": {"hadolint"},
    "terraform": {"semgrep", "tfsec"},
    "kubernetes": {"semgrep", "kubeconform"},
    "helm": {"semgrep", "helm_lint", "kubeconform"},
    "yaml": {"yamllint"},
}

JOB_NAMES = (
    "semgrep",
    "ast_grep",
    "shellcheck",
    "hadolint",
    "cppcheck",
    "stylelint",
    "yamllint",
    "tfsec",
    "helm_lint",
    "kubeconform",
)


def normalize_languages(value: str) -> list[str]:
    seen: set[str] = set()
    normalized: list[str] = []
    for raw in value.split(","):
        language = raw.strip().lower()
        if not language or language in seen:
            continue
        seen.add(language)
        normalized.append(language)
    return normalized


def resolve_jobs(languages: Iterable[str]) -> dict[str, bool | str]:
    selected_jobs: set[str] = set()
    unknown: list[str] = []
    normalized = list(languages)

    for language in normalized:
        jobs = LANGUAGE_TO_JOBS.get(language)
        if jobs is None:
            unknown.append(language)
            continue
        selected_jobs.update(jobs)

    result: dict[str, bool | str] = {
        job_name: job_name in selected_jobs for job_name in JOB_NAMES
    }
    result["languages"] = ",".join(normalized)
    result["unknown"] = ",".join(unknown)
    return result


def write_github_output(path: pathlib.Path, payload: dict[str, bool | str]) -> None:
    lines = []
    for key, value in payload.items():
        if isinstance(value, bool):
            rendered = "true" if value else "false"
        else:
            rendered = value
        lines.append(f"{key}={rendered}")
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--languages", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--github-output", type=pathlib.Path)
    args = parser.parse_args()

    payload = resolve_jobs(normalize_languages(args.languages))
    if payload["unknown"]:
        raise SystemExit(f"unsupported languages: {payload['unknown']}")

    if args.json:
        print(json.dumps(payload, sort_keys=True))
    if args.github_output:
        write_github_output(args.github_output, payload)
    if not args.json and not args.github_output:
        parser.error("choose --json or --github-output")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
