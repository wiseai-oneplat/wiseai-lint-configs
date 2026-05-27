#!/usr/bin/env python3
"""Merge a provider profile and shared PR-Agent review policy into one TOML file."""

from __future__ import annotations

import argparse
import json
import pathlib
import tomllib
from typing import Any


def merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged


def format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "[" + ", ".join(format_value(item) for item in value) + "]"
    if isinstance(value, int | float):
        return str(value)
    raise TypeError(f"Unsupported TOML value type: {type(value).__name__}")


def emit_toml(data: dict[str, Any]) -> str:
    lines: list[str] = []

    for table, values in data.items():
        if not isinstance(values, dict):
            lines.append(f"{table} = {format_value(values)}")
            continue

        if lines:
            lines.append("")
        lines.append(f"[{table}]")
        for key, value in values.items():
            if isinstance(value, dict):
                raise TypeError(f"Nested TOML tables deeper than one level are not supported: {table}.{key}")
            lines.append(f"{key} = {format_value(value)}")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", required=True, type=pathlib.Path)
    parser.add_argument("--common", required=True, type=pathlib.Path)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    args = parser.parse_args()

    common = tomllib.loads(args.common.read_text())
    provider = tomllib.loads(args.provider.read_text())
    config = merge_dicts(common, provider)

    args.output.write_text(emit_toml(config))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
