# 룰 작성 가이드

## 결정 트리: 어느 도구를 쓸까

```
새 룰 작성 필요
├── 단순 패턴 매칭 + 자동 수정 → ast-grep
├── 복잡한 dataflow / taint 분석 → semgrep
├── 통계/그래프 분석 → 직접 tree-sitter 스크립트
├── Shell/Dockerfile/CSS/Terraform/Helm/YAML/K8s → 전용 린터
│   (shellcheck/hadolint/stylelint/tfsec/helm lint/yamllint/kubeconform)
├── C/C++ 메모리/포인터 분석 → cppcheck (또는 clang-tidy)
└── 언어별 표준 룰 (스타일/타입) → 각 저장소의 표준 린터
```

## 워크플로우

1. **playground에서 검증** (먼저)
   - ast-grep: https://ast-grep.github.io/playground.html
   - semgrep: https://semgrep.dev/playground
2. **테스트 코드 작성**
   - semgrep positive: `fixtures/semgrep/positive/`
   - semgrep negative: `fixtures/semgrep/negative/`
   - ast-grep positive: `fixtures/ast-grep/positive/`
   - ast-grep negative: `fixtures/ast-grep/negative/`
   - 일부 룰은 `tests/**` 경로를 제외하므로 fixture는 `fixtures/**`에 둔다.
   - 실행: `scripts/test-rules.sh`
3. **PR 생성** (이 리포에)
4. **severity 정책**
   - 신규 룰: `INFO` 또는 `WARNING`으로 시작
   - 1주 관찰 후 false positive 비율 < 5%면 `ERROR` 승격
5. **버전 태그 후 호출 측에 전파**

## 작성 체크리스트

- [ ] `id`는 kebab-case (예: `python-naive-datetime`)
- [ ] `message`는 한국어, **무엇을 어떻게 바꾸라**고 명시
- [ ] `paths.exclude` 또는 `ignores`에 테스트/스크립트 제외
- [ ] `severity`는 신중하게 (`ERROR`는 머지 차단 가능)
- [ ] false positive 시나리오 최소 3개 검증
- [ ] 가능하면 `fix` 또는 `autofix` 제공

## 메시지 작성 규칙

좋은 예:
> "timezone-naive datetime을 사용하지 마세요. datetime.now(tz=...) 또는 datetime.now(timezone.utc) 사용."

나쁜 예:
> "Bad datetime usage"

이유 + 대안을 한 문장 안에 담을 것.

## 룰 비활성화 절차

특정 룰이 false positive 폭발 시:
1. 룰 파일 상단에 주석 `# DISABLED YYYY-MM-DD: 사유`
2. 룰 정의의 `severity: OFF` 또는 파일 자체를 임시 rename (`.yaml.disabled`)
3. 트래킹 이슈 생성 → 수정 후 재활성화

## 룰 카탈로그 (v0.4.1)

<!-- RULE_CATALOG:START -->
| ID | 도구 | 언어/도메인 | severity |
|----|------|------------|----------|
| hardcoded-secret-key | semgrep | all | ERROR |
| unresolved-fixme | semgrep | all | INFO |
| c-gets-unsafe | semgrep | c | ERROR |
| c-strcpy-unsafe | semgrep | c | WARNING |
| c-sprintf-unsafe | semgrep | c | WARNING |
| cpp-using-namespace-std-in-header | semgrep | cpp | WARNING |
| cpp-naked-new | semgrep | cpp | WARNING |
| go-panic-in-library | semgrep | go | ERROR |
| go-context-background-in-handler | semgrep | go | WARNING |
| java-system-out-println | semgrep | java | WARNING |
| java-field-autowired | semgrep | java | WARNING |
| javascript-eval-usage | semgrep | javascript | ERROR |
| javascript-document-write | semgrep | javascript | WARNING |
| k8s-image-tag-latest | semgrep | kubernetes | ERROR |
| k8s-image-tag-missing | semgrep | kubernetes | WARNING |
| k8s-privileged-true | semgrep | kubernetes | ERROR |
| k8s-hostnetwork-true | semgrep | kubernetes | ERROR |
| k8s-imagepullpolicy-always-missing | semgrep | kubernetes | INFO |
| python-naive-datetime | semgrep | python | WARNING |
| python-print-in-source | semgrep | python | WARNING |
| terraform-public-s3 | semgrep | terraform | ERROR |
| terraform-missing-tags | semgrep | terraform | INFO |
| typescript-console-log | semgrep | typescript/javascript | WARNING |
| typescript-as-any | semgrep | typescript | WARNING |
| no-panic | ast-grep | go | error |
| no-system-out | ast-grep | java | warning |
| no-print | ast-grep | python | warning |
| no-console | ast-grep | typescript | warning |
<!-- RULE_CATALOG:END -->

룰 추가/제거 시 `python3 scripts/generate-rule-catalog.py --write`로 이 표를 갱신하고,
CI에서는 `python3 scripts/generate-rule-catalog.py --check`로 drift를 차단한다.

## 룰 작성 일반 가이드

- **언어별 표준 도구로 잡히는 룰은 만들지 않기**: ruff/golangci-lint/biome가 이미 잡는 룰을 semgrep에 중복 작성하면 노이즈.
- **도메인 룰에 집중**: 비즈니스 규칙, 안전성, 보안, 도메인 invariants 위주.
- **autofix 가능하면 제공**: ast-grep의 `fix:` 필드 활용 → 개발자 부담 감소.
- **부정 경로 명시**: `pattern-not` / `ignores`로 false positive를 사전 차단.
