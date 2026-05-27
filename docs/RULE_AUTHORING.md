# 룰 작성 가이드

## 결정 트리: 어느 도구를 쓸까

```
새 룰 작성 필요
├── 단순 패턴 매칭 + 자동 수정 → ast-grep
├── 복잡한 dataflow / taint 분석 → semgrep
├── 통계/그래프 분석 → 직접 tree-sitter 스크립트
├── Shell/Dockerfile/K8s YAML → 전용 린터 (shellcheck/hadolint/kubeconform)
└── 언어별 표준 룰 (스타일/타입) → 기존 린터(ruff/golangci-lint/biome)
```

## 워크플로우

1. **playground에서 검증** (반드시 먼저)
   - ast-grep: https://ast-grep.github.io/playground.html
   - semgrep: https://semgrep.dev/playground
2. **테스트 코드 작성**
   - `tests/positive/` (룰이 잡아야 할 코드)
   - `tests/negative/` (룰이 잡으면 안 되는 코드)
3. **PR 생성** (이 리포에)
4. **severity 정책**
   - 신규 룰: `INFO` 또는 `WARNING`으로 시작
   - 1주 관찰 후 false positive 비율 < 5%면 `ERROR` 승격
5. **버전 태그 후 각 저장소에 전파**

## 작성 체크리스트

- [ ] `id`는 kebab-case (예: `python-naive-datetime`)
- [ ] `message`는 한국어로, **무엇을 어떻게 바꾸라**고 명시
- [ ] `paths.exclude` 또는 `ignores`에 테스트/스크립트 제외
- [ ] `severity`는 신중하게 (`ERROR`는 머지 차단)
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
1. 해당 룰 파일 상단에 주석으로 `# DISABLED YYYY-MM-DD: 사유`
2. 룰 정의의 `severity: OFF` 또는 파일 자체를 임시 rename (`.yaml.disabled`)
3. 트래킹 이슈 생성 → 수정 후 재활성화

## 룰 카탈로그 (v0.2.0)

| ID | 도구 | 언어/도메인 | severity |
|----|------|------------|----------|
| hardcoded-secret-key | semgrep | all | ERROR |
| unresolved-fixme | semgrep | all | INFO |
| python-naive-datetime | semgrep | python | WARNING |
| python-print-in-source | semgrep | python | WARNING |
| go-panic-in-library | semgrep | go | ERROR |
| go-context-background-in-handler | semgrep | go | WARNING |
| java-system-out-println | semgrep | java | WARNING |
| java-field-autowired | semgrep | java | WARNING |
| typescript-console-log | semgrep | typescript | WARNING |
| typescript-as-any | semgrep | typescript | WARNING |
| k8s-image-tag-latest | semgrep | kubernetes | ERROR |
| k8s-missing-resource-limits | semgrep | kubernetes | WARNING |
| k8s-runAsNonRoot-missing | semgrep | kubernetes | WARNING |
| no-print | ast-grep | python | warning |
| no-panic | ast-grep | go | error |
| no-system-out | ast-grep | java | warning |
| no-console | ast-grep | typescript | warning |

룰 추가/제거 시 이 표를 업데이트할 것.

## 도메인별 룰 작성 우선순위 (제안)

| 도메인 | 우선 룰 |
|--------|--------|
| voxBridge (음성) | WebSocket auth 누락, LiveKit room 생성 시 권한 검증, 스트림 close 누락 |
| wiseai-emr-pipeline | idempotency_key 누락, retry 정책 누락, 백프레셔 부재 |
| inbound/outbound | LLM API 호출에 timeout 미설정, fallback model 미설정 |
| wiseai-aiu | @Transactional + RuntimeException catch (롤백 안 됨), N+1 패턴 |
| infra/helm | hostNetwork: true, privileged: true, imagePullPolicy: Always 누락 |
| RPA | 좌표 하드코딩, sleep(상수) (대신 element wait) |
