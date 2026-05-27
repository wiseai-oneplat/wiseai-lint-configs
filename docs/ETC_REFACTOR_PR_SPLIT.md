# ETC Refactor PR Split

Do not bundle these with the provider, CI harness, reporting, or blocking-mode changes. Each PR
should be independently reviewable, reversible, and releasable.

## PR-A: Workflow Language Matrix

Scope: Replace repeated `contains(format(',{0},', inputs.languages), ',...,' )` expressions with a
single normalized language matrix or generated job condition strategy.

Files:
- `.github/workflows/reusable-lint.yml`
- `tests/test_reusable_lint_policy.py`
- `docs/INTEGRATION.md`

Verification:
- `python3 -m unittest discover -s tests -v`
- Add table-driven cases for `python,go,typescript,dockerfile`, `c`, `css`, `helm,yaml`.
- Confirm `c` does not match `css`, `typescript`, or `dockerfile`.

## PR-B: Tool Version Pinning

Scope: Pin externally installed tools and action dependencies so a tag produces reproducible lint
behavior.

Files:
- `.github/workflows/reusable-lint.yml`
- `.github/workflows/ci.yml`
- `docs/INTEGRATION.md`

Verification:
- `python3 -m unittest discover -s tests -v`
- CI log shows explicit versions for semgrep, stylelint, kubeconform, ast-grep, and reviewdog actions.
- No `latest` download URL remains except where explicitly documented as non-reproducible.

## PR-C: pre-commit Packaging

Scope: Make the repository directly consumable by pre-commit remote repo users.

Files:
- `.pre-commit-hooks.yaml`
- `pre-commit/shared-hooks.yaml`
- `docs/INTEGRATION.md`

Verification:
- `pre-commit validate-manifest .pre-commit-hooks.yaml`
- `pre-commit validate-manifest pre-commit/shared-hooks.yaml`
- `pre-commit try-repo . semgrep-shared --all-files` in a temporary repo when tools are available.

## PR-D: Version Sync and Catalog Generation

Scope: Remove manual version/catalog drift by generating docs from repository metadata and rule
files.

Files:
- `VERSION`
- `scripts/generate-rule-catalog.py`
- `docs/RULE_AUTHORING.md`
- `README.md`
- `docs/INTEGRATION.md`

Verification:
- `python3 scripts/generate-rule-catalog.py --check`
- `python3 -m unittest discover -s tests -v`
- Docs reference one current recommended tag.

## PR-E: Rule Pack Split

Scope: Split shared rules into opt-in packs so repositories can adopt security/infra/style rules at
different maturity levels.

Files:
- `semgrep/packs/`
- `ast-grep/packs/`
- `.github/workflows/reusable-lint.yml`
- `scripts/test-rules.sh`
- `docs/INTEGRATION.md`

Verification:
- `scripts/test-rules.sh`
- Positive/negative fixtures pass for every pack.
- Existing `languages` behavior remains backwards compatible unless a major version is planned.
