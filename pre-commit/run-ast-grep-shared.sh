#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec sg scan --config "$ROOT/ast-grep/sgconfig.yml"
