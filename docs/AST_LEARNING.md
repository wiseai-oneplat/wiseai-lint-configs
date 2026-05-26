# AST 학습 로드맵

목표: 4개 언어(Python, Go, Java, TypeScript)에서 동일한 사고방식으로 코드 패턴을 다루는 능력 습득.

## 왜 tree-sitter / ast-grep인가

- **언어 무관 query 사고방식**: 한 번 배우면 4언어에 모두 적용.
- **AI 코딩 도구의 기반**: Cursor, Aider, Sourcegraph 등 대부분 tree-sitter 사용.
- **점진적 도입 가능**: 룰 1개부터 시작해서 늘려갈 수 있음.

## 단계별 커리큘럼

### S0. 개념 학습 (1시간)
- **읽을 자료**: tree-sitter 공식 docs의 "Using Parsers" 챕터.
- **핵심 개념**:
  - CST(Concrete Syntax Tree) vs AST 차이
  - tree-sitter query language (S-expression 기반)
  - ast-grep의 pattern syntax (실제 코드처럼 작성)

### S1. Playground 실습 (2시간)
- [ast-grep playground](https://ast-grep.github.io/playground.html) 접속.
- 각 언어로 1개 패턴 작성:
  - Python: `print($ARG)` 매칭
  - Go: `panic($MSG)` 매칭
  - Java: `System.out.println($ARG)` 매칭
  - TypeScript: `console.log($ARG)` 매칭

### S2. 첫 실용 룰 (1시간)
- 이 리포의 `ast-grep/rules/python/no-print.yaml`을 변형.
- 실 프로젝트(`voxBridge` 또는 `inbound-project`)에 실행:
  `sg scan --config ../wiseai-lint-configs/ast-grep/sgconfig.yml`
- 결과 검토, false positive 분석.

### S3. 도메인 특화 룰 작성 (반나절)
- 작성 후보:
  1. `voxBridge`/`livekit-inbound`: WebSocket handler에서 auth 검증 누락 탐지
  2. `wiseai-emr-pipeline`: 외부 호출에서 idempotency_key 누락 탐지
  3. `inbound-project`/`outbound-project`: LLM 호출에서 timeout/fallback model 미설정 탐지
  4. `wiseai-aiu`: `@Transactional` + RuntimeException catch 패턴 탐지
- 각 룰을 `ast-grep/rules/python/` 또는 `ast-grep/rules/go/` 등에 추가.

### S4. tree-sitter Python 바인딩 직접 사용 (반나절)
- `py-tree-sitter`로 분석 스크립트 작성:
  - 예: `voxBridge` agent 코드에서 모든 LiveKit handler 메소드 시그니처 매트릭 추출
  - 예: `wiseai-emr-pipeline`에서 모든 워커의 retry/timeout 설정 커버리지 비교
- ast-grep으로 안 되는 영역(통계, 그래프 분석)을 메우는 용도.

### S5. semgrep vs ast-grep 분담 (1시간)
- semgrep: taint 분석, dataflow, 복잡한 패턴 조합. 보안 룰 작성에 강함.
- ast-grep: 구조 일치 + 빠른 fix. 안티패턴 자동 수정에 강함.
- `RULE_AUTHORING.md`에 결정 트리 추가.

## 학습 자료

- tree-sitter playground: https://tree-sitter.github.io/tree-sitter/playground
- ast-grep playground: https://ast-grep.github.io/playground.html
- semgrep registry (예제 풀): https://semgrep.dev/r
- "The Tree-sitter Book" (커뮤니티): 검색.

## 학습 완료 신호

- [ ] 4언어 각각 ast-grep 룰 1개 이상 작성
- [ ] EMR 도메인 룰 3개 이상 작성
- [ ] semgrep과 ast-grep 중 어느 도구를 쓸지 결정할 수 있음
- [ ] tree-sitter Python 바인딩으로 간단한 분석 스크립트 1개 작성
