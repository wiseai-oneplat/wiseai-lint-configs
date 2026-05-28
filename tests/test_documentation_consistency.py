import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class DocumentationConsistencyTest(unittest.TestCase):
    def test_recommended_tag_is_synchronized(self):
        version = (ROOT / "VERSION").read_text().strip()
        required_paths = [
            ".github/workflows/reusable-ai-review.yml",
            ".github/workflows/reusable-lint.yml",
            "docs/ARCHITECTURE.md",
            "docs/INTEGRATION.md",
            "docs/RULE_AUTHORING.md",
            "pre-commit/shared-hooks.yaml",
        ]

        for relative in required_paths:
            with self.subTest(file=relative):
                self.assertIn(version, (ROOT / relative).read_text())

    def test_markdown_files_reference_current_refactor_contracts(self):
        required_tokens = {
            "README.md": [
                "reusable-ai-review.yml",
                "scripts/test-rules.sh",
                "lint_mode",
            ],
            "docs/ARCHITECTURE.md": [
                "reusable-ai-review.yml",
                "ai_provider",
                "lint_mode",
                "scripts/test-rules.sh",
            ],
            "docs/AST_LEARNING.md": [
                "fixtures/ast-grep/positive",
                "fixtures/semgrep/positive",
                "scripts/test-rules.sh",
            ],
            "docs/ETC_REFACTOR_PR_SPLIT.md": [
                "P0-P3",
                "reusable-ai-review.yml",
                "scripts/test-rules.sh",
            ],
            "docs/INTEGRATION.md": [
                "reusable-ai-review.yml",
                "ai_provider",
                "lint_mode",
                "scripts/test-rules.sh",
            ],
            "docs/OPERATIONS.md": [
                "gh run watch",
                "AI Review Smoke",
                "Node24-compatible",
                "workflow_call",
            ],
            "docs/RULE_AUTHORING.md": [
                "fixtures/semgrep/positive",
                "fixtures/ast-grep/positive",
                "scripts/test-rules.sh",
                "v0.4.4",
            ],
            "pr-agent/providers/chatgpt-auth.experimental.md": [
                "reusable-ai-review.yml",
                "openai-api",
                "GitHub Actions",
            ],
        }

        for relative, tokens in required_tokens.items():
            with self.subTest(file=relative):
                text = (ROOT / relative).read_text()
                for token in tokens:
                    self.assertIn(token, text)

    def test_markdown_files_do_not_use_stale_recommended_tags(self):
        stale_references = []
        for path in ROOT.rglob("*.md"):
            if ".git" in path.parts:
                continue
            text = path.read_text()
            for stale_tag in ("v0.4.0", "v0.4.1", "v0.4.2", "v0.4.3"):
                if stale_tag in text:
                    stale_references.append(f"{path.relative_to(ROOT)}:{stale_tag}")

        self.assertEqual([], stale_references)


if __name__ == "__main__":
    unittest.main()
