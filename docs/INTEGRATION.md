# 저장소별 통합 가이드

12개 wiseai-oneplat 저장소에 공유 설정을 도입하는 절차.

## 공통 사전 작업

1. 이 리포의 현재 권장 tag는 `v0.2.0` 이상. (v0.1.x는 private repo 접근 권한 처리 누락으로 deprecated)
2. **wiseai-oneplat org secret 등록 (필수)**:
   - `LINT_CONFIGS_READ_PAT` — 이 리포를 읽을 권한이 있는 PAT
   - 생성 방법: GitHub → Settings → Developer settings → Personal access tokens
     → Fine-grained tokens 권장. Resource owner: `wiseai-oneplat`, Repository access:
     `wiseai-oneplat/wiseai-lint-configs`, Permissions: Contents = Read-only.
   - 등록: GitHub → wiseai-oneplat org → Settings → Secrets and variables → Actions
     → New organization secret. Name: `LINT_CONFIGS_READ_PAT`, Visibility: All repositories.
3. 각 저장소 GitHub Secrets에 다음 등록 (PR-Agent를 쓰는 경우):
   - `ANTHROPIC_API_KEY`
4. `GITHUB_TOKEN`은 기본 제공 → 별도 설정 불필요.

## 통합 매트릭스

| 저장소 | languages 인자 | PR-Agent | pre-commit |
|--------|----------------|----------|-----------|
| `voxBridge` | `python,go,typescript,dockerfile` | yes | yes |
| `wiseai-aiu` | `java,dockerfile` | yes | (Gradle wrapper) |
| `wiseai-emr-pipeline` | `go,kubernetes,shell` | yes | yes |
| `inbound-project` | `python,dockerfile` | yes | yes |
| `outbound-project` | `python,typescript,dockerfile,shell` | yes | yes |
| `service-planning-agent` | `python` | yes | optional |
| `wiseai-rpa-dental` | (RPA 전용, 별도 가이드 필요) | yes | no |
| `wiseai-rpa-medical` | (RPA 전용, 별도 가이드 필요) | yes | no |
| `livekit-inbound` | `python,shell,kubernetes` | yes | optional |
| `infra` | `shell,kubernetes` | yes | yes |
| `wiseai-helm-charts` | `helm,kubernetes` | yes | yes |
| `homebrew-tools` | `typescript,shell` | yes | yes |

## 저장소별 워크플로우 예시

각 저장소의 `.github/workflows/lint.yml`:

### 애플리케이션 (예: voxBridge)
```yaml
name: Lint
on: [pull_request]
jobs:
  lint:
    uses: wiseai-oneplat/wiseai-lint-configs/.github/workflows/reusable-lint.yml@v0.2.0
    with:
      languages: 'python,go,typescript,dockerfile'
    secrets:
      reviewdog_token: ${{ secrets.GITHUB_TOKEN }}
      configs_token:   ${{ secrets.LINT_CONFIGS_READ_PAT }}
```

### Java (wiseai-aiu)
```yaml
jobs:
  lint:
    uses: wiseai-oneplat/wiseai-lint-configs/.github/workflows/reusable-lint.yml@v0.2.0
    with:
      languages: 'java,dockerfile'
    secrets:
      reviewdog_token: ${{ secrets.GITHUB_TOKEN }}
      configs_token:   ${{ secrets.LINT_CONFIGS_READ_PAT }}
```

Gradle 빌드 측에는 별도로 SpotBugs/Checkstyle 플러그인 추가 (각 저장소에서 설정).

### 인프라 (infra, wiseai-helm-charts)
```yaml
jobs:
  lint:
    uses: wiseai-oneplat/wiseai-lint-configs/.github/workflows/reusable-lint.yml@v0.2.0
    with:
      languages: 'shell,kubernetes'   # 또는 'helm,kubernetes'
    secrets:
      reviewdog_token: ${{ secrets.GITHUB_TOKEN }}
      configs_token:   ${{ secrets.LINT_CONFIGS_READ_PAT }}
```

### homebrew-tools
```yaml
jobs:
  lint:
    uses: wiseai-oneplat/wiseai-lint-configs/.github/workflows/reusable-lint.yml@v0.2.0
    with:
      languages: 'typescript,shell'
    secrets:
      reviewdog_token: ${{ secrets.GITHUB_TOKEN }}
      configs_token:   ${{ secrets.LINT_CONFIGS_READ_PAT }}
```

## pre-commit 통합 (해당 저장소)

`.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/wiseai-oneplat/wiseai-lint-configs
    rev: v0.2.0
    hooks:
      - id: semgrep-shared
      - id: ast-grep-shared
      # 필요한 것만 활성화
      - id: shellcheck-shared
      - id: hadolint-shared
```

## PR-Agent 활성화

각 저장소 `.github/workflows/pr-agent.yml` (template 별도 제공 예정):
- `ANTHROPIC_API_KEY` 시크릿 필요
- 공유 `.pr_agent.toml`을 복사하거나 git submodule로 참조

## RPA 저장소 특이사항

`wiseai-rpa-dental`, `wiseai-rpa-medical`은:
- Windows AutoIt/MFC 등 표준 SAST 도구가 적용 안 됨
- 변형 디렉토리(`EMR_RPA_DENTWEB_DENTON - 담덕치과/` 등)가 많아 base.yaml의 시크릿/FIXME 룰만 우선 적용 권장
- PR-Agent는 활성화 가능 (LLM은 텍스트 기반이라 도메인 무관)
- 별도 RPA 전용 가이드는 v0.2 이후 작성

## 통합 검증 체크리스트

각 저장소 통합 후 확인:
- [ ] PR 생성 시 reviewdog 코멘트 출현
- [ ] 의도된 위반에 대한 코멘트 정확성
- [ ] False-positive 비율 < 10%
- [ ] CI 시간 증가 < 2분
- [ ] PR-Agent 한국어 리뷰 출력 (활성화 시)

## 롤아웃 권장 순서

가장 빠르게 효과를 볼 수 있는 순서:
1. `voxBridge` (Python+Go+TS, 가장 활발)
2. `wiseai-emr-pipeline` (Go 단일, 단순)
3. `wiseai-aiu` (Java, 별도 Gradle 작업 필요)
4. `inbound-project` / `outbound-project` (Python 중심)
5. `infra`, `wiseai-helm-charts` (인프라)
6. 나머지 (`homebrew-tools`, `service-planning-agent`, `livekit-inbound`)
7. RPA 2개는 v0.2에서
