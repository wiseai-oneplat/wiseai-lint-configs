# 아키텍처

조직 내 저장소에 적용되는 코드 분석 + AI 리뷰 파이프라인.

## 4-Tier 흐름

```
┌─────────────────────────────────────────────────────────┐
│ 개발자: 로컬 commit                                      │
│   └─ pre-commit (shared-hooks.yaml, 옵션)               │
│        ├─ 언어별 표준 린터 (각 repo의 ruff/golangci/…)   │
│        ├─ semgrep (shared rules)                        │
│        ├─ ast-grep (shared rules)                       │
│        ├─ shellcheck / hadolint / yamllint (해당 시)     │
└─────────────────────────────────────────────────────────┘
            │
            ▼ PR push
┌─────────────────────────────────────────────────────────┐
│ TIER 1: 결정론적 분석기 (~10-60s)                       │
│  reusable-lint.yml의 각 잡 (languages 인자로 활성화):     │
│   - shellcheck    (shell)                               │
│   - hadolint      (dockerfile)                          │
│   - cppcheck      (c, cpp)                              │
│   - stylelint     (css)                                 │
│   - yamllint      (yaml)                                │
│   - tfsec         (terraform)                           │
│   - helm-lint     (helm)                                │
│   - kubeconform   (kubernetes, helm)                    │
│  결과 → reviewdog → PR diff 라인 코멘트                  │
└─────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────┐
│ TIER 2: 패턴 분석 (~30s-2min)                           │
│   - semgrep (공유 룰: base + 언어별)                     │
│   - ast-grep (구조 패턴 룰)                             │
└─────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────┐
│ TIER 3: AI 리뷰 (~1-3min, 옵션)                         │
│   reusable-ai-review.yml + PR-Agent (qodo-merge):        │
│    ai_provider: anthropic | openai-api | gemini | none   │
│    /review   — 변경 요약 + 점수 + 보안 평가             │
│    /describe — PR 본문 보강                             │
│    /improve  — 코드 개선 제안                           │
│  provider profile + common-review.toml 조립              │
└─────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────┐
│ TIER 4: 인터랙티브 (로컬, 옵션)                          │
│   AI 코딩 에이전트(Claude Code 등) + MCP 도구            │
│   개발자가 변경 컨텍스트를 LLM과 함께 탐색               │
└─────────────────────────────────────────────────────────┘
```

## 데이터 흐름

```
공유 lint-configs 리포 (public)
    │ git tag v0.4.2
    ▼
호출 측 .github/workflows/lint.yml
    │ uses: .../reusable-lint.yml@v0.4.2
    │ inputs: languages, reporter_mode, reviewdog_level, lint_mode, fail_on_error
    ▼
GitHub Action runner
    │ checkout 대상 저장소 + 공유 lint-configs
    ▼
도구 실행 (semgrep/ast-grep/shellcheck/hadolint/cppcheck/stylelint/yamllint/tfsec/helm-lint/kubeconform)
    │ SARIF / errorformat / JSON
    ▼
reviewdog
    │ PR diff와 매칭하여 inline 코멘트 변환
    ▼
GitHub PR
    │ (Tier 3) reusable-ai-review.yml이 ai_provider별 PR-Agent 리뷰 수행 (옵션)
    ▼
머지 결정
```

## 자체 검증 흐름

```
룰/워크플로우 변경
    │
    ├─ scripts/test-rules.sh
    │    ├─ fixtures/semgrep/positive, fixtures/semgrep/negative
    │    └─ fixtures/ast-grep/positive, fixtures/ast-grep/negative
    │
    ├─ python3 -m unittest discover -s tests -v
    │    ├─ reusable workflow 계약
    │    ├─ provider config 조립
    │    └─ reporting/blocking 정책
    │
    └─ .github/workflows/ci.yml
         └─ 위 검증을 PR/push에서 재실행
```

## 보안 모델

- **시크릿 노출 방지**:
  - `ANTHROPIC_API_KEY` → Anthropic provider 사용 저장소의 GitHub Secrets 전용
  - `OPENAI_KEY` → `ai_provider: openai-api` 사용 저장소의 GitHub Secrets 전용
  - `GEMINI_API_KEY` → `ai_provider: gemini` 사용 저장소의 GitHub Secrets 전용
  - 공유 리포에는 시크릿 zero
- **권한 최소화**:
  - PR-Agent: PR comment 권한만, merge 불가
  - reviewdog: 동일
- **인증 경계**:
  - GitHub Actions에서는 API key 기반 provider만 지원
  - ChatGPT 웹 세션/Auth 방식은 재현성·보안 문제로 reusable workflow에서 차단
- **공급망 방어**:
  - 공유 리포는 tag 기반 참조 (`@v0.x.y`), branch 참조 금지
  - 외부 action은 가능하면 SHA 핀

## 버전/롤백

- 공유 리포: SemVer
- 호출 측은 자기 페이스로 업그레이드 (`ref:` 라인만 수정)
- 룰 1개가 false positive 폭발 시 → patch 릴리스
- 긴급 시 호출 측 ref를 이전 tag로 되돌리면 즉시 롤백
- 기본 lint 운영은 `lint_mode: advisory`; 저장소별 준비도에 따라 `lint_mode: blocking`으로 승격

## 향후 확장 후보

- Java Gradle 공유 플러그인 모듈 (SpotBugs/Checkstyle/PMD)
- 메트릭 수집 (룰 적중률 / false positive 비율 주간 리포트)
- 공급망 보안 (Bearer, semgrep-supply-chain)
- ast-grep 룰 자동 fix 적용 PR 봇
