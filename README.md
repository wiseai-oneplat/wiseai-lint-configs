# wiseai-lint-configs

조직 내 저장소를 위한 공유 코드 분석 + AI 리뷰 설정.

## 디렉토리

| 경로 | 내용 |
|------|------|
| `semgrep/rules/`, `semgrep/packs/` | 언어별 semgrep 룰 + opt-in rule pack manifest |
| `ast-grep/rules/`, `ast-grep/packs/` | 언어별 ast-grep 룰 + opt-in rule pack manifest |
| `pre-commit/` | pre-commit remote repo 호환 hooks |
| `.github/workflows/` | GitHub reusable workflow (`reusable-lint.yml`, `reusable-ai-review.yml`) |
| `pr-agent/` | PR-Agent/Qodo Merge provider profiles + 한국어 리뷰 정책 |
| `docs/` | 통합/학습/룰 작성 문서 |
| `VERSION` | 문서/릴리스 권장 tag의 단일 기준 |

## 지원 언어/도메인

| 값 (`languages` 인자) | Tier 2 (semgrep/ast-grep) | Tier 1 (전용 도구) |
|----------------------|--------------------------|-------------------|
| `python` | semgrep + ast-grep | (각 repo의 ruff/mypy) |
| `go` | semgrep + ast-grep | (각 repo의 golangci-lint) |
| `java` | semgrep + ast-grep | (각 repo의 Gradle 플러그인) |
| `typescript` | semgrep + ast-grep | (각 repo의 biome/tsc) |
| `javascript` | semgrep + ast-grep | (각 repo의 biome/eslint) |
| `vue` | ast-grep (HTML/TS 부분) | (각 repo의 eslint-plugin-vue) |
| `c` | semgrep + ast-grep | cppcheck |
| `cpp` | semgrep + ast-grep | cppcheck |
| `css` | ast-grep | stylelint |
| `shell` | (해당 없음) | shellcheck |
| `dockerfile` | (해당 없음) | hadolint |
| `terraform` | semgrep | tfsec |
| `kubernetes` | semgrep | kubeconform |
| `helm` | semgrep | helm lint + kubeconform |
| `yaml` | (해당 없음) | yamllint |

호출 측 `languages` 인자에 쉼표 구분 문자열로 전달하면 해당 잡만 활성화.

## 빠른 시작

`docs/INTEGRATION.md` 참조.

## AI 리뷰 provider

`reusable-ai-review.yml`은 `ai_provider` 입력으로 Qodo Merge/PR-Agent 모델 provider를 선택합니다.

| `ai_provider` | 용도 | 필요한 secret |
|---------------|------|---------------|
| `anthropic` | Claude 계열 기본 프로필 | `ANTHROPIC_API_KEY` |
| `openai-api` | ChatGPT/OpenAI API key 기반 리뷰 | `OPENAI_KEY` |
| `gemini` | Google Gemini API 기반 리뷰 | `GEMINI_API_KEY` |
| `chatgpt-auth` | ChatGPT 웹 세션 방식 | CI 미지원, `openai-api` 사용 권장 |

공통 한국어 리뷰 정책은 `pr-agent/fragments/common-review.toml`, provider별 모델 설정은
`pr-agent/providers/*.toml`에 둡니다.

## 검증 및 운영 모드

- 룰 변경 전후에는 `scripts/test-rules.sh`로 semgrep/ast-grep fixture를 검증합니다.
- GitHub Actions 자체 검증은 `.github/workflows/ci.yml`에서 reusable workflow 계약, provider 설정,
  룰 fixture를 함께 확인합니다.
- `reusable-lint.yml`은 기본적으로 `lint_mode: advisory`로 PR 코멘트/요약만 남깁니다.
  머지 차단이 필요한 저장소는 `lint_mode: blocking` 또는 `fail_on_error: true`를 명시합니다.
- reviewdog 출력 방식은 `reporter_mode`, 코멘트 severity는 `reviewdog_level`로 조정합니다.
- `rule_packs`로 `security`, `reliability`, `style`, `infra` 룰 팩을 선택합니다. 기본값 `all`은 기존
  `languages` 동작과 호환됩니다.
- 룰 카탈로그는 `scripts/generate-rule-catalog.py --check`로 검증하고, 필요하면 `--write`로 갱신합니다.

## 버전 정책

- `main`은 항상 안정. 모든 호출 측은 git tag (`v0.x.y`)로 참조.
- 룰 추가/변경은 PR + 리뷰 필수.
- 신규 룰은 `INFO`/`WARNING`으로 시작 → 1주 관찰 후 false-positive < 5%면 `ERROR` 승격.

## 학습 시작점

- AST/룰 작성이 처음이라면 `docs/AST_LEARNING.md`.
- 룰을 새로 쓰려면 `docs/RULE_AUTHORING.md`.
- 전체 파이프라인은 `docs/ARCHITECTURE.md`.
