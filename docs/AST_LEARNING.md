# AST 학습 로드맵

목표: 여러 언어에서 동일한 사고방식으로 코드 패턴을 다루는 능력 습득.

## 왜 tree-sitter / ast-grep인가

- **언어 무관 query 사고방식**: 한 번 배우면 여러 언어에 적용.
- **AI 코딩 도구의 기반**: Cursor, Aider, Sourcegraph 등 다수가 tree-sitter 사용.
- **점진적 도입 가능**: 룰 1개부터 시작해서 확장.

## 단계별 커리큘럼

### S0. 개념 학습 (1시간)
- **읽을 자료**: tree-sitter 공식 docs의 "Using Parsers" 챕터.
- **핵심 개념**:
  - CST(Concrete Syntax Tree) vs AST
  - tree-sitter query language (S-expression)
  - ast-grep의 pattern syntax (실제 코드처럼 작성)

### S1. Playground 실습 (2시간)
- [ast-grep playground](https://ast-grep.github.io/playground.html) 접속.
- 다양한 언어로 패턴 작성 연습:
  - Python: `print($ARG)` 매칭
  - Go: `panic($MSG)` 매칭
  - Java: `System.out.println($ARG)` 매칭
  - TypeScript: `console.log($ARG)` 매칭
  - C/C++: 안전하지 않은 함수 호출 패턴

### S2. 첫 실용 룰 (1시간)
- 이 리포의 `ast-grep/rules/<lang>/`의 기존 룰을 복사·수정.
- 자신의 저장소에서 실행: `sg scan --config <path>/ast-grep/sgconfig.yml`
- 결과 검토, false positive 분석.
- 이 리포에 룰을 추가할 때는 fixture를 먼저 둔다:
  - positive: `fixtures/ast-grep/positive/`
  - negative: `fixtures/ast-grep/negative/`
- 로컬 검증은 `scripts/test-rules.sh`로 실행한다. ast-grep이 설치되어 있으면 positive fixture에서
  기대 finding을 확인하고, negative fixture에서 false positive가 없는지 확인한다.

### S3. 도메인 특화 룰 작성 (반나절)
- 작성 후보 (자신의 도메인 특성에 맞춰):
  1. 외부 호출에서 timeout 미설정 패턴
  2. WebSocket/HTTP handler에서 인증 누락 패턴
  3. 비동기 호출 context 전파 누락 패턴
  4. 멱등성 키 미설정 패턴
  5. 트랜잭션 경계 위반 패턴
- 각 룰을 `ast-grep/rules/<lang>/`에 추가, PR.

### S4. tree-sitter 바인딩 직접 사용 (반나절)
- `py-tree-sitter` 또는 `tree-sitter-cli`로 분석 스크립트 작성:
  - 예: 모든 handler 메소드 시그니처 매트릭 추출
  - 예: 모든 워커의 retry/timeout 설정 커버리지 비교
- ast-grep으로 안 되는 영역(통계, 그래프 분석)에 활용.

### S5. semgrep vs ast-grep 분담 (1시간)
- **semgrep**: taint 분석, dataflow, 복잡한 패턴 조합. 보안 룰에 강함.
- **ast-grep**: 구조 일치 + 빠른 fix. 안티패턴 자동 수정에 강함.
- `RULE_AUTHORING.md`의 결정 트리 참고.
- semgrep 룰도 동일하게 fixture를 둔다:
  - positive: `fixtures/semgrep/positive/`
  - negative: `fixtures/semgrep/negative/`
  - 실행: `scripts/test-rules.sh`

## 학습 자료

- tree-sitter playground: https://tree-sitter.github.io/tree-sitter/playground
- ast-grep playground: https://ast-grep.github.io/playground.html
- semgrep registry: https://semgrep.dev/r

## 학습 완료 신호

- [ ] 주력 언어에서 ast-grep 룰 1개 이상 작성
- [ ] 도메인 룰 3개 이상 작성
- [ ] semgrep과 ast-grep 중 어느 도구를 쓸지 결정 가능
- [ ] tree-sitter 바인딩으로 간단한 분석 스크립트 1개 작성
