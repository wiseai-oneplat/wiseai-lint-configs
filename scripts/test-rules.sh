#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
export SEMGREP_SEND_METRICS=off
STRICT_RULE_TOOLS="${STRICT_RULE_TOOLS:-false}"
RULE_PACKS_TO_TEST="${RULE_PACKS_TO_TEST:-all security reliability style infra}"

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
    for pack in $RULE_PACKS_TO_TEST; do
      args_file="$TMP_DIR/semgrep-$pack.args"
      python3 "$ROOT/scripts/resolve-rule-packs.py" \
        --tool semgrep \
        --packs "$pack" \
        --root "$ROOT" \
        --write-args "$args_file"
      mapfile -t semgrep_args < "$args_file"
      if [ "${#semgrep_args[@]}" -eq 0 ]; then
        echo "semgrep: no rules selected for pack '$pack'; skipping"
        continue
      fi

      semgrep --metrics off "${semgrep_args[@]}" --json "$ROOT/fixtures/semgrep/positive" > "$TMP_DIR/semgrep-$pack-positive.json" || true
      python3 "$ROOT/scripts/assert-rule-findings.py" --tool semgrep --input "$TMP_DIR/semgrep-$pack-positive.json" --min-count 1

      semgrep --metrics off "${semgrep_args[@]}" --json "$ROOT/fixtures/semgrep/negative" > "$TMP_DIR/semgrep-$pack-negative.json" || true
      python3 "$ROOT/scripts/assert-rule-findings.py" --tool semgrep --input "$TMP_DIR/semgrep-$pack-negative.json" --max-count 0
    done
  else
    cat "$TMP_DIR/semgrep-version.err"
    skip_or_fail "semgrep is installed but not runnable; skipping semgrep runtime fixtures"
  fi
else
  skip_or_fail "semgrep not installed; skipping semgrep runtime fixtures"
fi

if command -v sg >/dev/null 2>&1; then
  if sg --version > /dev/null 2> "$TMP_DIR/ast-grep-version.err"; then
    for pack in $RULE_PACKS_TO_TEST; do
      paths_json="$TMP_DIR/ast-grep-$pack.json"
      config_file="$TMP_DIR/ast-grep-$pack-sgconfig.yml"
      python3 "$ROOT/scripts/resolve-rule-packs.py" \
        --tool ast-grep \
        --packs "$pack" \
        --root "$ROOT" \
        --json > "$paths_json"
      selected_count="$(python3 - "$paths_json" <<'PY'
import json
import sys

print(len(json.loads(open(sys.argv[1]).read())["paths"]))
PY
)"
      if [ "$selected_count" -eq 0 ]; then
        echo "ast-grep: no rules selected for pack '$pack'; skipping"
        continue
      fi

      python3 "$ROOT/scripts/resolve-rule-packs.py" \
        --tool ast-grep \
        --packs "$pack" \
        --root "$ROOT" \
        --write-config "$config_file"

      sg scan --config "$config_file" --json "$ROOT/fixtures/ast-grep/positive" > "$TMP_DIR/ast-grep-$pack-positive.json" || true
      python3 "$ROOT/scripts/assert-rule-findings.py" --tool ast-grep --input "$TMP_DIR/ast-grep-$pack-positive.json" --min-count 1

      sg scan --config "$config_file" --json "$ROOT/fixtures/ast-grep/negative" > "$TMP_DIR/ast-grep-$pack-negative.json" || true
      python3 "$ROOT/scripts/assert-rule-findings.py" --tool ast-grep --input "$TMP_DIR/ast-grep-$pack-negative.json" --max-count 0
    done
  else
    cat "$TMP_DIR/ast-grep-version.err"
    skip_or_fail "sg scan is installed but not runnable; skipping ast-grep runtime fixtures"
  fi
else
  skip_or_fail "sg scan not installed; skipping ast-grep runtime fixtures"
fi
