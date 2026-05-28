#!/usr/bin/env python3
"""Resolve rule pack manifests into semgrep args or an ast-grep sgconfig."""

from __future__ import annotations

import argparse
import json
import pathlib
from collections.abc import Iterable


ROOT = pathlib.Path(__file__).resolve().parents[1]
PACK_NAMES = ("security", "reliability", "style", "infra")


def normalize_packs(value: str) -> list[str]:
    raw_packs = [pack.strip().lower() for pack in value.split(",") if pack.strip()]
    if not raw_packs or "all" in raw_packs:
        return list(PACK_NAMES)

    seen: set[str] = set()
    packs: list[str] = []
    unknown: list[str] = []
    for pack in raw_packs:
        if pack not in PACK_NAMES:
            unknown.append(pack)
            continue
        if pack not in seen:
            seen.add(pack)
            packs.append(pack)
    if unknown:
        raise SystemExit(f"unsupported rule packs: {','.join(unknown)}")
    return packs


def read_manifest(root: pathlib.Path, tool: str, pack: str) -> list[str]:
    manifest = root / tool / "packs" / f"{pack}.txt"
    if not manifest.exists():
        return []

    paths: list[str] = []
    for line in manifest.read_text().splitlines():
        item = line.strip()
        if not item or item.startswith("#"):
            continue
        paths.append(item)
    return paths


def resolve_paths(root: pathlib.Path, tool: str, packs: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    paths: list[str] = []
    for pack in packs:
        for relative in read_manifest(root, tool, pack):
            if relative in seen:
                continue
            candidate = root / relative
            if not candidate.exists():
                raise SystemExit(f"pack path does not exist: {relative}")
            seen.add(relative)
            paths.append(relative)
    return paths


def write_semgrep_args(root: pathlib.Path, paths: list[str], output: pathlib.Path) -> None:
    lines: list[str] = []
    for relative in paths:
        lines.extend(["--config", str(root / relative)])
    output.write_text("\n".join(lines) + ("\n" if lines else ""))


def write_ast_grep_config(root: pathlib.Path, paths: list[str], output: pathlib.Path) -> None:
    lines = ["ruleDirs:"]
    for relative in paths:
        lines.append(f"  - {root / relative}")
    if len(lines) == 1:
        lines.append("  - __no_ast_grep_rules_selected__")
    output.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool", required=True, choices=["semgrep", "ast-grep"])
    parser.add_argument("--packs", default="all")
    parser.add_argument("--root", type=pathlib.Path, default=ROOT)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write-args", type=pathlib.Path)
    parser.add_argument("--write-config", type=pathlib.Path)
    args = parser.parse_args()

    packs = normalize_packs(args.packs)
    paths = resolve_paths(args.root, args.tool, packs)

    if args.write_args:
        if args.tool != "semgrep":
            parser.error("--write-args is only valid for semgrep")
        write_semgrep_args(args.root, paths, args.write_args)

    if args.write_config:
        if args.tool != "ast-grep":
            parser.error("--write-config is only valid for ast-grep")
        write_ast_grep_config(args.root, paths, args.write_config)

    if args.json:
        print(json.dumps({"packs": packs, "paths": paths}, sort_keys=True))

    if not args.json and not args.write_args and not args.write_config:
        parser.error("choose --json, --write-args, or --write-config")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
