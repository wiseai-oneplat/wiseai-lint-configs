# 통합 가이드

## 공통 사전 작업

1. 권장 tag: `v0.4.3` 이상.
2. 호출 측 저장소 secret 등록 (AI 리뷰 사용 시, provider별 1개만 필요):
   - Anthropic: `ANTHROPIC_API_KEY`
   - OpenAI/ChatGPT API: `OPENAI_KEY`
   - Gemini: `GEMINI_API_KEY`
3. `GITHUB_TOKEN`은 기본 제공 → 별도 설정 불필요.
4. 본 리포는 public이므로 checkout용 PAT 불필요.

기존 호출부가 이전 tag를 참조한다면 먼저 `uses:`와 pre-commit `rev:`를 모두 권장 tag로 올립니다.
공유 workflow의 `configs_ref` 기본값도 같은 tag를 가리키므로, 별도 override가 있는 저장소는 같이 갱신합니다.

## 기본 워크플로우

호출 측 저장소의 `.github/workflows/lint.yml`:

```yaml
name: Lint
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pull-requests: write

jobs:
  shared-lint:
    uses: wiseai-oneplat/wiseai-lint-configs/.github/workflows/reusable-lint.yml@v0.4.3
    with:
      languages: '<쉼표 구분 언어 목록>'
      rule_packs: all
      lint_mode: advisory
      reporter_mode: github-pr-review
    secrets:
      reviewdog_token: ${{ secrets.GITHUB_TOKEN }}
```

## `languages` 인자 → 활성화되는 잡

| 값 | 활성화 잡 |
|----|----------|
| `python` | semgrep, ast-grep |
| `go` | semgrep, ast-grep |
| `java` | semgrep, ast-grep |
| `typescript` | semgrep, ast-grep |
| `javascript` | semgrep, ast-grep |
| `vue` | ast-grep |
| `c` | semgrep, ast-grep, cppcheck |
| `cpp` | semgrep, ast-grep, cppcheck |
| `css` | ast-grep, stylelint |
| `shell` | shellcheck |
| `dockerfile` | hadolint |
| `terraform` | tfsec |
| `kubernetes` | kubeconform |
| `helm` | helm-lint, kubeconform |
| `yaml` | yamllint |

여러 값을 쉼표로 결합. 예: `'python,go,dockerfile'`.

워크플로우 내부에서는 `scripts/resolve-language-jobs.py`가 이 값을 한 번 정규화한 뒤 각 job의 실행 여부를
`language-matrix` job output으로 전달합니다. 따라서 `c`는 `css`, `typescript`, `dockerfile`과 매칭되지 않습니다.

## `rule_packs` 인자 → 활성화되는 공유 룰 묶음

| 값 | 용도 |
|----|------|
| `all` | 기본값. 기존 `languages` 기반 동작과 호환되도록 모든 pack 사용. |
| `security` | 시크릿, 위험 API, 플랫폼 보안 관련 룰. |
| `reliability` | 런타임 안정성, context/시간 처리, 타입 안정성 룰. |
| `style` | logger/console/출력 등 유지보수성 룰. |
| `infra` | Kubernetes/Terraform 등 인프라 룰. |

여러 값을 쉼표로 결합할 수 있습니다. 예: `security,infra`.
semgrep pack manifest는 `semgrep/packs/*.txt`, ast-grep pack manifest는 `ast-grep/packs/*.txt`에 있습니다.

## reporting / blocking 정책

| 입력 | 기본값 | 설명 |
|------|--------|------|
| `reporter_mode` | `github-pr-review` | reviewdog reporter. 예: `github-pr-review`, `github-pr-check`, `github-check`. |
| `reviewdog_level` | `warning` | reviewdog 코멘트 레벨. |
| `lint_mode` | `advisory` | `advisory`는 코멘트/요약만 남기고, `blocking`은 실패를 CI 실패로 전파. |
| `fail_on_error` | `false` | `true`면 `lint_mode`와 무관하게 reviewdog error에서 실패. |

`helm-lint`와 `kubeconform`은 PR diff line comment로 안정적으로 매핑하기 어려워 `$GITHUB_STEP_SUMMARY`에 결과를 남깁니다.
`lint_mode: blocking` 또는 `fail_on_error: true`일 때는 이 summary-only 도구들도 실패 상태를 전파합니다.

## 호출 예시 (저장소 성격별)

### 백엔드 (Python + Go + Docker)
```yaml
with:
  languages: 'python,go,dockerfile'
```

### 풀스택 (TypeScript + Python + Docker)
```yaml
with:
  languages: 'python,typescript,dockerfile'
```

### Java/Spring
```yaml
with:
  languages: 'java,dockerfile'
```

### 프론트엔드 (Vue + CSS + TS)
```yaml
with:
  languages: 'vue,css,typescript'
```

### 시스템 프로그래밍 (C/C++)
```yaml
with:
  languages: 'c,cpp,shell'
```

### 인프라/플랫폼
```yaml
with:
  languages: 'shell,kubernetes,terraform,yaml'
```

### Helm chart 저장소
```yaml
with:
  languages: 'helm,yaml'
```

## pre-commit 통합 (옵션)

해당 저장소의 `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/wiseai-oneplat/wiseai-lint-configs
    rev: v0.4.3
    hooks:
      - id: semgrep-shared
      - id: ast-grep-shared
      - id: shellcheck-shared    # *.sh 있는 저장소만
      - id: hadolint-shared      # Dockerfile 있는 저장소만
      - id: yamllint-shared      # yaml 검사 원할 시
```

이 리포 자체에서는 pre-commit remote repo 호환성을 위해 루트 `.pre-commit-hooks.yaml`와
`pre-commit/shared-hooks.yaml`를 모두 유지합니다. `semgrep-shared`와 `ast-grep-shared`는 hook repo
내 wrapper script가 공유 룰 경로를 해석하므로, 호출 측 저장소에 룰 파일을 복사할 필요가 없습니다.
단, pre-commit 실행 환경의 `PATH`에는 선택한 hook에 필요한 도구(`semgrep`, `sg`, `shellcheck`,
`hadolint`, `yamllint`)가 있어야 합니다. 변경 후에는 다음 검증을 통과해야 합니다.

```bash
pre-commit validate-manifest .pre-commit-hooks.yaml
pre-commit validate-manifest pre-commit/shared-hooks.yaml
```

## AI 리뷰 활성화 (옵션)

호출 측 저장소의 `.github/workflows/ai-review.yml`:

```yaml
name: AI Review
on:
  pull_request:
    types: [opened, reopened, synchronize, ready_for_review]
  workflow_dispatch:

permissions:
  contents: read
  pull-requests: write
  issues: write

jobs:
  ai-review:
    uses: wiseai-oneplat/wiseai-lint-configs/.github/workflows/reusable-ai-review.yml@v0.4.3
    with:
      ai_provider: openai-api # anthropic | openai-api | gemini | none
    secrets:
      pr_agent_token: ${{ secrets.GITHUB_TOKEN }}
      openai_key: ${{ secrets.OPENAI_KEY }}
```

### `ai_provider` 인자

| 값 | 모델 프로필 | 필요한 secret |
|----|-------------|---------------|
| `anthropic` | `pr-agent/providers/anthropic.toml` | `ANTHROPIC_API_KEY` |
| `openai-api` | `pr-agent/providers/openai-api.toml` | `OPENAI_KEY` |
| `gemini` | `pr-agent/providers/gemini.toml` | `GEMINI_API_KEY` |
| `none` | AI 리뷰 비활성화 | 없음 |

`chatgpt-auth`는 ChatGPT 웹 세션/쿠키 기반 인증을 의미하므로 GitHub Actions에서는 지원하지 않습니다.
CI에서는 `openai-api`와 `OPENAI_KEY`를 사용하세요.

provider별 secret 전달 예시는 다음처럼 필요한 값만 넘깁니다.

```yaml
# Anthropic
with:
  ai_provider: anthropic
secrets:
  pr_agent_token: ${{ secrets.GITHUB_TOKEN }}
  anthropic_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

```yaml
# Gemini
with:
  ai_provider: gemini
secrets:
  pr_agent_token: ${{ secrets.GITHUB_TOKEN }}
  gemini_api_key: ${{ secrets.GEMINI_API_KEY }}
```

## 로컬/공유 룰 검증

공유 룰을 수정하거나 호출 측에 적용 전 smoke test를 돌릴 때는 이 리포에서 다음을 실행합니다.

```bash
scripts/test-rules.sh
```

이 스크립트는 `fixtures/semgrep/positive`, `fixtures/semgrep/negative`,
`fixtures/ast-grep/positive`, `fixtures/ast-grep/negative`를 기준으로 룰의 기대 finding과
false positive를 확인합니다. 기본적으로 `all security reliability style infra` pack을 모두 검증하며,
`RULE_PACKS_TO_TEST`로 대상 pack을 좁힐 수 있습니다. 로컬에 semgrep 또는 ast-grep이 없으면 해당 도구 검증은 skip됩니다.

## 통합 검증 체크리스트

각 저장소 통합 후 확인:
- [ ] 공유 룰 수정 시 `scripts/test-rules.sh` 통과
- [ ] 호출부 `uses:`가 권장 tag를 참조
- [ ] `configs_ref` override가 있다면 권장 tag와 일치
- [ ] AI 리뷰 사용 시 provider별 secret 이름이 workflow contract와 일치
- [ ] PR 생성 시 reviewdog 코멘트 출현 (PR diff 내 위반 시)
- [ ] 의도된 위반에 대한 코멘트 정확성
- [ ] False-positive 비율 < 10%
- [ ] CI 시간 증가 < 2분
- [ ] PR-Agent 한국어 리뷰 출력 (활성화 시)

실제 소비 repo가 아직 없거나 권한이 없으면 `docs/OPERATIONS.md`의 소비 repo 검색/AI smoke 절차로
검증 가능한 범위와 blocker를 분리해서 기록합니다.

## reviewdog 코멘트 동작

기본 `reporter_mode: github-pr-review`는 **PR diff에 포함된 라인에만 코멘트**합니다.
변경되지 않은 기존 코드의 위반은 코멘트로 표시되지 않습니다. PR 변경 라인을 통해 점진적으로 코드 품질을 개선하는 방식입니다.
