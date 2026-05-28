# 운영 체크리스트

## 릴리스

1. `VERSION`을 새 patch/minor tag로 올린다.
2. `python3 scripts/generate-rule-catalog.py --write`로 룰 카탈로그 헤더를 동기화한다.
3. 문서와 reusable workflow 기본 `configs_ref`가 같은 tag를 가리키는지 확인한다.
4. 로컬 검증을 실행한다.

```bash
python3 -m unittest discover -s tests -v
go run "github.com/rhysd/actionlint/cmd/actionlint@v1.7.7"
python3 scripts/generate-rule-catalog.py --check
python3 -m py_compile scripts/*.py tests/*.py
ruby -e 'require "yaml"; Dir[".github/workflows/*.yml", "rules/**/*.yml", ".pre-commit-hooks.yaml"].each { |path| YAML.load_file(path) }'
git diff --check
```

5. 외부 action exact tag가 실제로 존재하는지 확인한다. 특히 reviewdog action은 repo별 release
   번호가 서로 다르므로 같은 버전을 일괄 적용하지 않는다.
6. main에 push한 뒤 `gh run watch <run-id> --exit-status`로 원격 CI를 확인한다.
7. 기존 tag는 덮어쓰지 않는다. 후속 수정은 새 patch tag로 릴리스한다.

## 소비 Repo 검증

소비 repo를 찾을 때는 로컬 clone과 GitHub code search를 모두 확인한다.

```bash
rg --hidden -n "wiseai-oneplat/wiseai-lint-configs|reusable-lint.yml|reusable-ai-review.yml" \
  /Users/ojm/Dev/wiseai -g ".github/workflows/*.yml" -g ".github/workflows/*.yaml"
gh search code "wiseai-oneplat/wiseai-lint-configs" --owner wiseai-oneplat --limit 20
```

실제 소비 repo가 발견되면 다음을 확인한다.

- 호출부 `uses:`와 `configs_ref`가 현재 권장 tag를 참조한다.
- `reviewdog_token`은 `${{ secrets.GITHUB_TOKEN }}`로 전달된다.
- AI 리뷰는 선택 provider 하나에 필요한 secret만 전달한다.
- PR diff에 일부러 작은 위반을 넣어 reviewdog 코멘트가 붙는지 확인한다.
- `lint_mode: advisory`에서는 코멘트만 남고, `lint_mode: blocking` 또는 `fail_on_error: true`에서는 실패가 전파된다.

## AI Review Smoke

이 repo에서 항상 가능한 smoke는 provider config assembly다.

```bash
python3 scripts/assemble-pr-agent-config.py --provider pr-agent/providers/openai-api.toml --common pr-agent/fragments/common-review.toml --output /tmp/pr-agent-openai.toml
python3 scripts/assemble-pr-agent-config.py --provider pr-agent/providers/anthropic.toml --common pr-agent/fragments/common-review.toml --output /tmp/pr-agent-anthropic.toml
python3 scripts/assemble-pr-agent-config.py --provider pr-agent/providers/gemini.toml --common pr-agent/fragments/common-review.toml --output /tmp/pr-agent-gemini.toml
```

실제 provider 호출 smoke에는 별도 소비 repo PR과 secret이 필요하다.

| Provider | 필요 secret | 성공 기준 |
|----------|-------------|-----------|
| `openai-api` | `OPENAI_KEY` | PR-Agent가 한국어 리뷰 코멘트 작성 |
| `anthropic` | `ANTHROPIC_API_KEY` | PR-Agent가 한국어 리뷰 코멘트 작성 |
| `gemini` | `GEMINI_API_KEY` | PR-Agent가 한국어 리뷰 코멘트 작성 |
| `chatgpt-auth` | 없음 | GitHub Actions에서 명시적으로 실패 |

repo secret이 없거나 org secret 조회 권한이 없으면 실제 호출 smoke는 blocked로 기록한다.

## CI 안정화

- 공식 actions는 Node24-compatible v6 계열 exact tag로 고정한다.
- reviewdog actions는 각 action repo에 존재하는 exact tag로 고정한다.
- 이 repo의 `actions/setup-go`는 `go.sum`이 없으므로 `cache: false`를 유지한다.
- 원격 CI watch 출력에 Node.js 20 deprecation annotation과 `go.sum` cache warning이 없어야 한다.
- reusable workflow 자체는 소비 repo PR에서 최종 확인한다.

## 다음 리팩토링 후보

- 소비 repo fixture를 별도 test repo로 만들고 `workflow_call` smoke를 정기 실행한다.
- workflow input schema를 JSON/YAML manifest로 선언하고 docs와 테스트를 생성한다.
- provider secret presence를 사전 검증하는 lightweight job을 추가한다.
- review 결과 포맷을 PR summary와 inline comment로 분리해 리포팅 일관성을 높인다.
- pre-commit hook별 tool availability check를 더 명확한 에러 메시지로 개선한다.
