# 통합 가이드

## 공통 사전 작업

1. 권장 tag: `v0.4.0` 이상.
2. 호출 측 저장소 secret 등록 (PR-Agent 사용 시):
   - `ANTHROPIC_API_KEY`
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
    uses: wiseai-oneplat/wiseai-lint-configs/.github/workflows/reusable-lint.yml@v0.4.0
    with:
      languages: '<쉼표 구분 언어 목록>'
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
    rev: v0.4.0
    hooks:
      - id: semgrep-shared
      - id: ast-grep-shared
      - id: shellcheck-shared    # *.sh 있는 저장소만
      - id: hadolint-shared      # Dockerfile 있는 저장소만
      - id: yamllint-shared      # yaml 검사 원할 시
```

## PR-Agent 활성화 (옵션)

호출 측 저장소에 `.github/workflows/pr-agent.yml` 추가 + `ANTHROPIC_API_KEY` secret 등록.
공유 `.pr_agent.toml`을 복사하거나 git submodule로 참조.

## 통합 검증 체크리스트

각 저장소 통합 후 확인:
- [ ] PR 생성 시 reviewdog 코멘트 출현 (PR diff 내 위반 시)
- [ ] 의도된 위반에 대한 코멘트 정확성
- [ ] False-positive 비율 < 10%
- [ ] CI 시간 증가 < 2분
- [ ] PR-Agent 한국어 리뷰 출력 (활성화 시)

## reviewdog 코멘트 동작

`-reporter=github-pr-review`는 **PR diff에 포함된 라인에만 코멘트**. 변경되지 않은 기존 코드의 위반은 코멘트로 표시되지 않음. PR 변경 라인을 통해 점진적으로 코드 품질을 개선하는 방식.
