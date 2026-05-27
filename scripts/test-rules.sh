#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
export SEMGREP_SEND_METRICS=off
STRICT_RULE_TOOLS="${STRICT_RULE_TOOLS:-false}"

skip_or_fail() {
  local message="$1"
  if [ "$STRICT_RULE_TOOLS" = "true" ]; then
    echo "::error::$message"
    return 1
  fi
  echo "::warning::$message"
}

if command -v semgrep >/dev/null 2>&1; then
  if semgrep --metrics off --version > /dev/null 2> "$TMP_DIR/semgrep-version.err"; then
    semgrep --metrics off --config "$ROOT/semgrep/rules/" --json "$ROOT/fixtures/semgrep/positive" > "$TMP_DIR/semgrep-positive.json" || true
    python3 "$ROOT/scripts/assert-rule-findings.py" --tool semgrep --input "$TMP_DIR/semgrep-positive.json" --min-count 8

    semgrep --metrics off --config "$ROOT/semgrep/rules/" --json "$ROOT/fixtures/semgrep/negative" > "$TMP_DIR/semgrep-negative.json" || true
    python3 "$ROOT/scripts/assert-rule-findings.py" --tool semgrep --input "$TMP_DIR/semgrep-negative.json" --max-count 0
  else
    cat "$TMP_DIR/semgrep-version.err"
    skip_or_fail "semgrep is installed but not runnable; skipping semgrep runtime fixtures"
  fi
else
  skip_or_fail "semgrep not installed; skipping semgrep runtime fixtures"
fi

if command -v sg >/dev/null 2>&1; then
  if sg --version > /dev/null 2> "$TMP_DIR/ast-grep-version.err"; then
    sg scan --config "$ROOT/ast-grep/sgconfig.yml" --json "$ROOT/fixtures/ast-grep/positive" > "$TMP_DIR/ast-grep-positive.json" || true
    python3 "$ROOT/scripts/assert-rule-findings.py" --tool ast-grep --input "$TMP_DIR/ast-grep-positive.json" --min-count 4

    sg scan --config "$ROOT/ast-grep/sgconfig.yml" --json "$ROOT/fixtures/ast-grep/negative" > "$TMP_DIR/ast-grep-negative.json" || true
    python3 "$ROOT/scripts/assert-rule-findings.py" --tool ast-grep --input "$TMP_DIR/ast-grep-negative.json" --max-count 0
  else
    cat "$TMP_DIR/ast-grep-version.err"
    skip_or_fail "sg scan is installed but not runnable; skipping ast-grep runtime fixtures"
  fi
else
  skip_or_fail "sg scan not installed; skipping ast-grep runtime fixtures"
fi
