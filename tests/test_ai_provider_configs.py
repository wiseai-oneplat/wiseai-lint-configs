import pathlib
import re
import subprocess
import tempfile
import tomllib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class AiProviderConfigTest(unittest.TestCase):
    def test_provider_profiles_exist_and_parse(self):
        for provider in ("anthropic", "openai-api", "gemini"):
            with self.subTest(provider=provider):
                path = ROOT / "pr-agent" / "providers" / f"{provider}.toml"
                self.assertTrue(path.exists(), f"missing {path}")
                data = tomllib.loads(path.read_text())
                self.assertIn("config", data)
                self.assertIsInstance(data["config"].get("model"), str)
                self.assertTrue(data["config"]["model"])

    def test_common_review_fragment_keeps_korean_review_policy(self):
        path = ROOT / "pr-agent" / "fragments" / "common-review.toml"
        self.assertTrue(path.exists(), f"missing {path}")
        data = tomllib.loads(path.read_text())

        reviewer = data["pr_reviewer"]
        self.assertEqual(data["config"]["language"], "ko")
        self.assertIn("한국어로 리뷰하세요", reviewer["extra_instructions"])
        self.assertIn("표준 린터", reviewer["extra_instructions"])

    def test_provider_models_match_supported_contracts(self):
        providers = {
            "anthropic": "claude-4-sonnet",
            "openai-api": "gpt-5",
            "gemini": "gemini-2.5-pro",
        }

        for provider, expected_model in providers.items():
            with self.subTest(provider=provider):
                data = tomllib.loads(
                    (ROOT / "pr-agent" / "providers" / f"{provider}.toml").read_text()
                )
                self.assertEqual(data["config"]["model"], expected_model)
                self.assertIn(expected_model, data["config"]["fallback_models"])

    def test_chatgpt_auth_is_explicitly_experimental_and_not_ci_supported(self):
        path = ROOT / "pr-agent" / "providers" / "chatgpt-auth.experimental.md"
        self.assertTrue(path.exists(), f"missing {path}")
        text = path.read_text()
        self.assertRegex(text, re.compile(r"GitHub Actions.*지원하지 않습니다", re.S))
        self.assertIn("openai-api", text)
        self.assertIn("OPENAI_KEY", text)

    def test_reusable_ai_review_workflow_declares_provider_contract(self):
        path = ROOT / ".github" / "workflows" / "reusable-ai-review.yml"
        self.assertTrue(path.exists(), f"missing {path}")
        text = path.read_text()

        for needle in (
            "ai_provider",
            "anthropic",
            "openai-api",
            "gemini",
            "chatgpt-auth",
            "qodo-ai/pr-agent",
            "OPENAI_KEY",
            "OPENAI__KEY",
            "GEMINI_API_KEY",
            "ANTHROPIC_API_KEY",
        ):
            self.assertIn(needle, text)

        self.assertNotIn("ANTHROPIC.KEY:", text)
        self.assertNotIn("GOOGLE_AI_STUDIO.GEMINI_API_KEY:", text)
        self.assertRegex(text, re.compile(r"chatgpt-auth.*exit 1", re.S))

    def test_docs_explain_supported_ai_review_providers(self):
        docs = "\n".join(
            [
                (ROOT / "README.md").read_text(),
                (ROOT / "docs" / "INTEGRATION.md").read_text(),
            ]
        )

        for needle in (
            "reusable-ai-review.yml",
            "ai_provider",
            "openai-api",
            "gemini",
            "chatgpt-auth",
            "OPENAI_KEY",
            "GEMINI_API_KEY",
            "ANTHROPIC_API_KEY",
        ):
            self.assertIn(needle, docs)

    def test_provider_and_common_fragments_assemble_into_valid_toml(self):
        script = ROOT / "scripts" / "assemble-pr-agent-config.py"
        self.assertTrue(script.exists(), f"missing {script}")

        for provider in ("anthropic", "openai-api", "gemini"):
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as tmp:
                output = pathlib.Path(tmp) / ".pr_agent.toml"
                subprocess.run(
                    [
                        "python3",
                        str(script),
                        "--provider",
                        str(ROOT / "pr-agent" / "providers" / f"{provider}.toml"),
                        "--common",
                        str(ROOT / "pr-agent" / "fragments" / "common-review.toml"),
                        "--output",
                        str(output),
                    ],
                    check=True,
                    cwd=ROOT,
                )
                data = tomllib.loads(output.read_text())
                self.assertEqual(data["config"]["language"], "ko")
                self.assertTrue(data["config"]["model"])
                self.assertIn("pr_reviewer", data)


if __name__ == "__main__":
    unittest.main()
