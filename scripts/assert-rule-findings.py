#!/usr/bin/env python3
"""Assert finding counts from semgrep or ast-grep JSON output."""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any


def count_semgrep(data: Any) -> int:
    if not isinstance(data, dict):
        raise ValueError("semgrep JSON must be an object")
    return len(data.get("results", []))


def count_ast_grep(data: Any) -> int:
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict):
        if isinstance(data.get("matches"), list):
            return len(data["matches"])
        if isinstance(data.get("diagnostics"), list):
            return len(data["diagnostics"])
    raise ValueError("unsupported ast-grep JSON shape")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool", required=True, choices=["semgrep", "ast-grep"])
    parser.add_argument("--input", required=True, type=pathlib.Path)
    parser.add_argument("--min-count", type=int)
    parser.add_argument("--max-count", type=int)
    args = parser.parse_args()

    data = json.loads(args.input.read_text() or "[]")
    count = count_semgrep(data) if args.tool == "semgrep" else count_ast_grep(data)

    if args.min_count is not None and count < args.min_count:
        raise SystemExit(f"{args.tool}: expected at least {args.min_count} findings, got {count}")
    if args.max_count is not None and count > args.max_count:
        raise SystemExit(f"{args.tool}: expected at most {args.max_count} findings, got {count}")

    print(f"{args.tool}: finding count ok ({count})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
