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
│   PR-Agent (qodo-merge):                                │
│    /review   — 변경 요약 + 점수 + 보안 평가             │
│    /describe — PR 본문 보강                             │
│    /improve  — 코드 개선 제안                           │
│  공유 .pr_agent.toml에 한국어 페르소나 + 일반 가이드     │
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
    │ git tag v0.4.0
    ▼
호출 측 .github/workflows/lint.yml
    │ uses: .../reusable-lint.yml@v0.4.0
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
    │ (Tier 3) PR-Agent가 추가 리뷰 (옵션)
    ▼
머지 결정
```

## 보안 모델

- **시크릿 노출 방지**:
  - `ANTHROPIC_API_KEY` → 호출 측 저장소 GitHub Secrets 전용
  - 공유 리포에는 시크릿 zero
- **권한 최소화**:
  - PR-Agent: PR comment 권한만, merge 불가
  - reviewdog: 동일
- **공급망 방어**:
  - 공유 리포는 tag 기반 참조 (`@v0.x.y`), branch 참조 금지
  - 외부 action은 가능하면 SHA 핀

## 버전/롤백

- 공유 리포: SemVer
- 호출 측은 자기 페이스로 업그레이드 (`ref:` 라인만 수정)
- 룰 1개가 false positive 폭발 시 → patch 릴리스
- 긴급 시 호출 측 ref를 이전 tag로 되돌리면 즉시 롤백

## 향후 확장 후보

- Java Gradle 공유 플러그인 모듈 (SpotBugs/Checkstyle/PMD)
- 메트릭 수집 (룰 적중률 / false positive 비율 주간 리포트)
- 공급망 보안 (Bearer, semgrep-supply-chain)
- ast-grep 룰 자동 fix 적용 PR 봇
