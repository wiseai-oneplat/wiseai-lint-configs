# 통합 가이드

## 공통 사전 작업

1. 권장 tag: `v0.4.1` 이상.
2. 호출 측 저장소 secret 등록 (AI 리뷰 사용 시, provider별 1개만 필요):
   - Anthropic: `ANTHROPIC_API_KEY`
   - OpenAI/ChatGPT API: `OPENAI_KEY`
   - Gemini: `GEMINI_API_KEY`
3. `GITHUB_TOKEN`은 기본 제공 → 별도 설정 불필요.
4. 본 리포는 public이므로 checkout용 PAT 불필요.

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
    uses: wiseai-oneplat/wiseai-lint-configs/.github/workflows/reusable-lint.yml@v0.4.1
    with:
      languages: '<쉼표 구분 언어 목록>'
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
    rev: v0.4.1
    hooks:
      - id: semgrep-shared
      - id: ast-grep-shared
      - id: shellcheck-shared    # *.sh 있는 저장소만
      - id: hadolint-shared      # Dockerfile 있는 저장소만
      - id: yamllint-shared      # yaml 검사 원할 시
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
    uses: wiseai-oneplat/wiseai-lint-configs/.github/workflows/reusable-ai-review.yml@v0.4.1
    with:
      ai_provider: openai-api # anthropic | openai-api | gemini | none
    secrets:
      github_token: ${{ secrets.GITHUB_TOKEN }}
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

## 로컬/공유 룰 검증

공유 룰을 수정하거나 호출 측에 적용 전 smoke test를 돌릴 때는 이 리포에서 다음을 실행합니다.

```bash
scripts/test-rules.sh
```

이 스크립트는 `fixtures/semgrep/positive`, `fixtures/semgrep/negative`,
`fixtures/ast-grep/positive`, `fixtures/ast-grep/negative`를 기준으로 룰의 기대 finding과
false positive를 확인합니다. 로컬에 semgrep 또는 ast-grep이 없으면 해당 도구 검증은 skip됩니다.

## 통합 검증 체크리스트

각 저장소 통합 후 확인:
- [ ] 공유 룰 수정 시 `scripts/test-rules.sh` 통과
- [ ] PR 생성 시 reviewdog 코멘트 출현 (PR diff 내 위반 시)
- [ ] 의도된 위반에 대한 코멘트 정확성
- [ ] False-positive 비율 < 10%
- [ ] CI 시간 증가 < 2분
- [ ] PR-Agent 한국어 리뷰 출력 (활성화 시)

## reviewdog 코멘트 동작

기본 `reporter_mode: github-pr-review`는 **PR diff에 포함된 라인에만 코멘트**합니다.
변경되지 않은 기존 코드의 위반은 코멘트로 표시되지 않습니다. PR 변경 라인을 통해 점진적으로 코드 품질을 개선하는 방식입니다.
