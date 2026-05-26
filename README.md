# wiseai-lint-configs

`wiseai-oneplat` 조직의 모든 저장소를 위한 공유 코드 분석 설정.

## 적용 대상 저장소 (12개)

### 애플리케이션 (6)
| 저장소 | 주 언어 | 도메인 |
|--------|--------|--------|
| `voxBridge` | Python + Go + TypeScript | LiveKit 음성 인프라 |
| `wiseai-aiu` | Java/Gradle (Spring DDD) | 통합 백엔드 |
| `wiseai-emr-pipeline` | Go | EMR 데이터 파이프라인 |
| `inbound-project` | Python (uv) | 인바운드 콜 에이전트 |
| `outbound-project` | Python + Node.js | 아웃바운드 콜 에이전트 |
| `service-planning-agent` | (문서/Python) | 서비스 기획 에이전트 |

### RPA (2)
| 저장소 | 주 언어 | 비고 |
|--------|--------|------|
| `wiseai-rpa-dental` | Windows 자동화 (다수 변형) | 치과 EMR RPA |
| `wiseai-rpa-medical` | Windows 자동화 | 의료 EMR RPA |

### 인프라/도구 (4)
| 저장소 | 주 언어 | 비고 |
|--------|--------|------|
| `livekit-inbound` | Python + Shell | LiveKit 인바운드 |
| `infra` | Shell + YAML (k8s manifests, NCP) | 클러스터/IAM |
| `wiseai-helm-charts` | YAML (Helm) | 차트 |
| `homebrew-tools` | Ruby + TypeScript + Shell | 사내 CLI 모음 |

## 디렉토리

| 경로 | 내용 |
|------|------|
| `semgrep/rules/` | 언어별 semgrep 룰 (base + python/go/java/typescript/kubernetes) |
| `ast-grep/rules/` | 언어별 ast-grep 룰 |
| `pre-commit/` | pre-commit remote repo로 참조할 hooks |
| `reviewdog/workflows/` | GitHub reusable workflow (언어 매트릭스 + shellcheck/hadolint/kubeconform) |
| `pr-agent/` | PR-Agent 공유 설정 (한국어 페르소나, 12개 프로젝트 컨텍스트) |
| `docs/` | 통합/학습/룰 작성 문서 |

## 빠른 시작

`docs/INTEGRATION.md`에 12개 저장소별 통합 절차가 있습니다.

## 버전 정책

- `main`은 항상 안정. 모든 저장소는 git tag (`v0.x.0`)로 참조.
- 룰 추가/변경은 PR + 1명 리뷰 필수.
- 신규 룰은 `INFO`로 시작 → 1주 관찰 후 `WARNING`/`ERROR` 승격.

## 학습 시작점

- AST/룰 작성이 처음이라면 `docs/AST_LEARNING.md`.
- 룰을 새로 쓰려면 `docs/RULE_AUTHORING.md`.
- 전체 파이프라인은 `docs/ARCHITECTURE.md`.
