# 아키텍처

wiseai-oneplat 조직 12개 저장소에 적용되는 코드 분석 + AI 리뷰 파이프라인.

## 4-Tier 흐름

```
┌─────────────────────────────────────────────────────────┐
│ 개발자: 로컬 commit                                      │
│   └─ pre-commit (shared-hooks.yaml)                     │
│        ├─ ruff / mypy / golangci-lint / biome           │
│        ├─ semgrep (shared rules)                        │
│        ├─ ast-grep (shared rules)                       │
│        ├─ shellcheck / hadolint (해당 파일 변경 시)      │
└─────────────────────────────────────────────────────────┘
            │
            ▼ PR push
┌─────────────────────────────────────────────────────────┐
│ TIER 1: 결정론적 분석기 (~10-30s)                       │
│  reusable-lint.yml의 각 잡 (languages 인자로 활성화):     │
│   - Python:     ruff + mypy + bandit                    │
│   - Go:         golangci-lint + govulncheck             │
│   - Java:       SpotBugs + Checkstyle (저장소측 Gradle) │
│   - TypeScript: biome + tsc                             │
│   - Shell:      shellcheck (via reviewdog action)       │
│   - Dockerfile: hadolint (via reviewdog action)         │
│   - K8s/Helm:   kubeconform                             │
└─────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────┐
│ TIER 2: 패턴 분석 (~30s-2min)                           │
│   - semgrep (공유 룰: base + python + go + java         │
│              + typescript + kubernetes)                 │
│   - ast-grep (조직 안티패턴: 코드 4언어)                 │
└─────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────┐
│ TIER 3: AI 리뷰 (~1-3min)                               │
│   PR-Agent (qodo-merge):                                │
│    /review   — 변경 요약 + 점수 + 보안 평가             │
│    /describe — PR 본문 보강                             │
│    /improve  — 코드 개선 제안                           │
│  공유 .pr_agent.toml에 12개 저장소 컨텍스트 내장         │
└─────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────┐
│ TIER 4: 인터랙티브 (로컬, 옵션)                          │
│   Claude Code + serena MCP / claude-context             │
│   개발자가 변경 컨텍스트를 LLM과 함께 탐색               │
└─────────────────────────────────────────────────────────┘
```

## 저장소 × Tier 매트릭스

| 저장소 | Tier 1 활성화 | Tier 2 | Tier 3 |
|--------|--------------|--------|--------|
| `voxBridge` | ruff, golangci, biome, hadolint | semgrep(py+go+ts+k8s), ast-grep | PR-Agent |
| `wiseai-aiu` | SpotBugs (Gradle), hadolint | semgrep(java) | PR-Agent |
| `wiseai-emr-pipeline` | golangci, shellcheck, kubeconform | semgrep(go+k8s), ast-grep | PR-Agent |
| `inbound-project` | ruff, hadolint | semgrep(py), ast-grep | PR-Agent |
| `outbound-project` | ruff, biome, shellcheck, hadolint | semgrep(py+ts), ast-grep | PR-Agent |
| `service-planning-agent` | ruff | semgrep(py), ast-grep | PR-Agent |
| `wiseai-rpa-dental` | (없음) | semgrep(base만) | PR-Agent |
| `wiseai-rpa-medical` | (없음) | semgrep(base만) | PR-Agent |
| `livekit-inbound` | shellcheck, kubeconform | semgrep(py+k8s) | PR-Agent |
| `infra` | shellcheck, kubeconform | semgrep(k8s) | PR-Agent |
| `wiseai-helm-charts` | kubeconform (helm template 출력) | semgrep(k8s) | PR-Agent |
| `homebrew-tools` | biome, shellcheck | semgrep(ts) | PR-Agent |

## 데이터 흐름

```
wiseai-oneplat/wiseai-lint-configs
    │ git tag v0.2.0
    ▼
각 저장소 .github/workflows/lint.yml
    │ uses: .../reusable-lint.yml@v0.2.0
    ▼
GitHub Action runner
    │ checkout 저장소 + 공유 lint-configs
    ▼
semgrep / ast-grep / shellcheck / hadolint / kubeconform / 언어 린터
    │ JSON 또는 errorformat
    ▼
reviewdog
    │ PR diff와 매칭하여 inline 코멘트 변환
    ▼
GitHub PR
    │ (Tier 3) PR-Agent가 추가 리뷰
    ▼
머지 결정
```

## 보안 모델

- **시크릿 노출 방지**:
  - `ANTHROPIC_API_KEY` → 각 저장소 GitHub Secrets 전용
  - 공유 리포에는 시크릿 zero
- **권한 최소화**:
  - PR-Agent: PR comment 권한만, merge 불가
  - reviewdog: 동일
- **공급망 방어**:
  - 공유 리포는 tag 기반 참조 (`@v0.1.0`), branch 참조 금지
  - 외부 action(reviewdog/action-shellcheck 등)은 SHA 핀 권장

## 버전/롤백

- 공유 리포: SemVer (`v0.1.0` → `v0.2.0`)
- 각 저장소는 자기 페이스로 업그레이드 (`ref:` 라인만 수정)
- 룰 1개가 false positive 폭발 시 → 공유 리포에 patch 릴리스 (`v0.1.1`)
- 긴급 시 저장소 측에서 ref를 이전 tag로 되돌리면 즉시 롤백

## 향후 확장

- **v0.2 RPA 가이드**: AutoIt/MFC 코드 보안 가이드 + 좌표/타이밍 의존성 룰
- **Java Gradle 플러그인 모듈**: SpotBugs/Checkstyle/PMD 설정을 buildSrc로 공유
- **메트릭 수집**: 룰 적중률 / false positive 비율 주간 리포트 (자체 Action으로 GitHub Issue에 게시)
- **Tier 5 (선택)**: Bearer/semgrep-supply-chain 등 공급망 보안
