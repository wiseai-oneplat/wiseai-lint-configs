import pathlib
import stat
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class CiAndRuleHarnessTest(unittest.TestCase):
    def test_rule_harness_script_exists_and_references_expected_tools(self):
        path = ROOT / "scripts" / "test-rules.sh"
        self.assertTrue(path.exists(), f"missing {path}")
        mode = path.stat().st_mode
        self.assertTrue(mode & stat.S_IXUSR, "scripts/test-rules.sh must be executable")

        text = path.read_text()
        for needle in (
            "semgrep",
            "sg scan",
            "fixtures/semgrep/positive",
            "fixtures/semgrep/negative",
            "fixtures/ast-grep/positive",
            "fixtures/ast-grep/negative",
            "assert-rule-findings.py",
            "resolve-rule-packs.py",
            "RULE_PACKS_TO_TEST",
            "SEMGREP_SEND_METRICS=off",
            "--metrics off",
            "STRICT_RULE_TOOLS",
        ):
            self.assertIn(needle, text)

    def test_rule_fixtures_exist_for_positive_and_negative_paths(self):
        fixture_dirs = [
            ROOT / "fixtures" / "semgrep" / "positive",
            ROOT / "fixtures" / "semgrep" / "negative",
            ROOT / "fixtures" / "ast-grep" / "positive",
            ROOT / "fixtures" / "ast-grep" / "negative",
        ]

        for directory in fixture_dirs:
            with self.subTest(directory=directory):
                self.assertTrue(directory.is_dir(), f"missing {directory}")
                files = [path for path in directory.rglob("*") if path.is_file()]
                self.assertGreaterEqual(len(files), 2, f"not enough fixtures in {directory}")

    def test_assert_rule_findings_script_exists(self):
        path = ROOT / "scripts" / "assert-rule-findings.py"
        self.assertTrue(path.exists(), f"missing {path}")
        text = path.read_text()
        self.assertIn("--min-count", text)
        self.assertIn("--max-count", text)
        self.assertIn("semgrep", text)
        self.assertIn("ast-grep", text)

    def test_ci_workflow_runs_harness_and_static_validation(self):
        path = ROOT / ".github" / "workflows" / "ci.yml"
        self.assertTrue(path.exists(), f"missing {path}")
        text = path.read_text()

        for needle in (
            "python3 -m unittest discover -s tests -v",
            "python3 -m py_compile",
            "scripts/generate-rule-catalog.py --check",
            "scripts/test-rules.sh",
            "STRICT_RULE_TOOLS: 'true'",
            "SEMGREP_VERSION:",
            "AST_GREP_VERSION:",
            "semgrep==${SEMGREP_VERSION}",
            "@ast-grep/cli@${AST_GREP_VERSION}",
            "pre-commit validate-manifest .pre-commit-hooks.yaml",
            "pre-commit try-repo",
            "YAML.load_file",
        ):
            self.assertIn(needle, text)

    def test_rule_authoring_docs_describe_fixture_harness(self):
        text = (ROOT / "docs" / "RULE_AUTHORING.md").read_text()
        for needle in (
            "fixtures/semgrep/positive",
            "fixtures/semgrep/negative",
            "fixtures/ast-grep/positive",
            "fixtures/ast-grep/negative",
            "scripts/test-rules.sh",
        ):
            self.assertIn(needle, text)


if __name__ == "__main__":
    unittest.main()
