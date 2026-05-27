# ChatGPT Auth Experimental Profile

ChatGPT Auth means an interactive ChatGPT web/session credential. This is not the same as the
OpenAI API key path used by Qodo Merge / PR-Agent.

## Policy

GitHub Actions에서는 ChatGPT Auth를 지원하지 않습니다. `reusable-ai-review.yml`은
`ai_provider: chatgpt-auth`를 CI provider로 받지 않으며, 브라우저 세션이나 개인 ChatGPT
쿠키를 사용하는 방식은 재현성, 보안, 계정 정책 측면에서 운영 경로로 두지 않습니다.

## Supported Alternative

Use the `openai-api` provider profile with an OpenAI API key:

- reusable workflow provider: `openai-api`
- repository secret: `OPENAI_KEY`
- provider profile: `pr-agent/providers/openai-api.toml`

If local experimentation with ChatGPT Auth becomes necessary, keep it outside the reusable CI
workflow and document the local runner separately.
