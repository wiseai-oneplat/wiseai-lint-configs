#!/usr/bin/env python3
"""Generate and verify the rule catalog in docs/RULE_AUTHORING.md."""

from __future__ import annotations

import argparse
import pathlib
import re


ROOT = pathlib.Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "VERSION"
GUIDE = ROOT / "docs" / "RULE_AUTHORING.md"
START = "<!-- RULE_CATALOG:START -->"
END = "<!-- RULE_CATALOG:END -->"


def scalar_value(line: str) -> str:
    return line.split(":", 1)[1].strip().strip("'\"")


def parse_bracket_list(value: str) -> list[str]:
    value = value.strip()
    if not value.startswith("["):
        return [value]
    return [item.strip().strip("'\"") for item in value.strip("[]").split(",") if item.strip()]


def semgrep_domain(path: pathlib.Path, languages: list[str]) -> str:
    stem = path.stem
    if stem == "base" or languages == ["generic"]:
        return "all"
    if stem == "typescript" and set(languages) == {"typescript", "javascript"}:
        return "typescript/javascript"
    return stem


def iter_semgrep_rules() -> list[tuple[str, str, str, str]]:
    rows: list[tuple[str, str, str, str]] = []
    for path in sorted((ROOT / "semgrep" / "rules").glob("*.yaml")):
        current_id: str | None = None
        severity: str | None = None
        languages: list[str] = []

        def flush() -> None:
            nonlocal current_id, severity, languages
            if current_id and severity:
                rows.append((current_id, "semgrep", semgrep_domain(path, languages), severity))
            current_id = None
            severity = None
            languages = []

        for line in path.read_text().splitlines():
            stripped = line.strip()
            if stripped.startswith("- id:"):
                flush()
                current_id = scalar_value(stripped.removeprefix("- "))
            elif stripped.startswith("severity:"):
                severity = scalar_value(stripped)
            elif stripped.startswith("languages:"):
                languages = parse_bracket_list(scalar_value(stripped))
        flush()
    return rows


def iter_ast_grep_rules() -> list[tuple[str, str, str, str]]:
    rows: list[tuple[str, str, str, str]] = []
    for path in sorted((ROOT / "ast-grep" / "rules").glob("*/*.yaml")):
        rule_id: str | None = None
        language: str | None = None
        severity: str | None = None
        for line in path.read_text().splitlines():
            stripped = line.strip()
            if stripped.startswith("id:"):
                rule_id = scalar_value(stripped)
            elif stripped.startswith("language:"):
                language = scalar_value(stripped)
            elif stripped.startswith("severity:"):
                severity = scalar_value(stripped)
        if rule_id and language and severity:
            rows.append((rule_id, "ast-grep", language, severity))
    return rows


def render_catalog() -> str:
    version = VERSION_FILE.read_text().strip()
    rows = iter_semgrep_rules() + iter_ast_grep_rules()
    lines = [
        f"## 룰 카탈로그 ({version})",
        "",
        START,
        "| ID | 도구 | 언어/도메인 | severity |",
        "|----|------|------------|----------|",
    ]
    for rule_id, tool, domain, severity in rows:
        lines.append(f"| {rule_id} | {tool} | {domain} | {severity} |")
    lines.append(END)
    return "\n".join(lines)


def replace_catalog(text: str, catalog: str) -> str:
    pattern = re.compile(r"## 룰 카탈로그 \(.*?\)\n\n<!-- RULE_CATALOG:START -->.*?<!-- RULE_CATALOG:END -->", re.S)
    if pattern.search(text):
        return pattern.sub(catalog, text)

    legacy_pattern = re.compile(
        r"## 룰 카탈로그 \(.*?\)\n\n\| ID \| 도구 \| 언어/도메인 \| severity \|\n"
        r"\|----\|------\|------------\|----------\|\n"
        r"(?:\|.*\|\n?)+",
        re.S,
    )
    if not legacy_pattern.search(text):
        raise SystemExit("RULE_AUTHORING.md is missing a replaceable rule catalog")
    return legacy_pattern.sub(catalog + "\n", text)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()

    text = GUIDE.read_text()
    catalog = render_catalog()
    updated = replace_catalog(text, catalog)

    if args.check:
        if text != updated:
            raise SystemExit("docs/RULE_AUTHORING.md rule catalog is out of date")
        print("rule catalog ok")
    else:
        GUIDE.write_text(updated)
        print("updated docs/RULE_AUTHORING.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
