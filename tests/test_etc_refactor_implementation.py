import json
import pathlib
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", *args],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class EtcRefactorImplementationTest(unittest.TestCase):
    def test_pr_a_language_matrix_resolver_matches_expected_jobs(self):
        script = ROOT / "scripts" / "resolve-language-jobs.py"
        self.assertTrue(script.exists(), f"missing {script}")

        cases = {
            "python,go,typescript,dockerfile": {
                "semgrep": True,
                "ast_grep": True,
                "hadolint": True,
                "cppcheck": False,
                "stylelint": False,
            },
            "c": {
                "semgrep": True,
                "ast_grep": True,
                "cppcheck": True,
                "stylelint": False,
                "hadolint": False,
            },
            "css": {
                "semgrep": False,
                "ast_grep": True,
                "cppcheck": False,
                "stylelint": True,
                "hadolint": False,
            },
            "helm,yaml": {
                "semgrep": True,
                "kubeconform": True,
                "helm_lint": True,
                "yamllint": True,
            },
        }

        for languages, expected in cases.items():
            with self.subTest(languages=languages):
                result = run_script(str(script), "--languages", languages, "--json")
                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)
                for job, enabled in expected.items():
                    self.assertEqual(enabled, payload[job], f"{languages} -> {job}")

    def test_pr_a_workflow_uses_generated_language_job_outputs(self):
        text = (ROOT / ".github" / "workflows" / "reusable-lint.yml").read_text()
        self.assertIn("language-matrix:", text)
        self.assertIn("scripts/resolve-language-jobs.py", text)
        self.assertNotIn("contains(format(',{0},', inputs.languages)", text)
        for output_name in ("semgrep", "ast_grep", "shellcheck", "hadolint", "cppcheck"):
            self.assertIn(f"needs.language-matrix.outputs.{output_name}", text)

    def test_pr_b_external_tools_and_actions_are_pinned(self):
        workflow_text = (ROOT / ".github" / "workflows" / "reusable-lint.yml").read_text()
        ci_text = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
        combined = workflow_text + "\n" + ci_text

        for needle in (
            "SEMGREP_VERSION:",
            "AST_GREP_VERSION:",
            "STYLELINT_VERSION:",
            "STYLELINT_CONFIG_STANDARD_VERSION:",
            "KUBECONFORM_VERSION:",
            "reviewdog/action-setup@v1.9.0",
            "reviewdog/action-shellcheck@v1.9.0",
            "reviewdog/action-hadolint@v1.9.0",
            "reviewdog/action-yamllint@v1.9.0",
            "reviewdog/action-tfsec@v1.9.0",
        ):
            self.assertIn(needle, combined)

        forbidden = (
            "releases/latest",
            "pip install semgrep",
            "npm install -g @ast-grep/cli",
            "npm install -g stylelint stylelint-config-standard",
            "reviewdog/action-setup@v1\n",
            "reviewdog/action-shellcheck@v1\n",
            "reviewdog/action-hadolint@v1\n",
            "reviewdog/action-yamllint@v1\n",
            "reviewdog/action-tfsec@v1\n",
        )
        for needle in forbidden:
            self.assertNotIn(needle, combined)

    def test_pr_c_pre_commit_remote_manifest_is_packaged(self):
        root_manifest = ROOT / ".pre-commit-hooks.yaml"
        shared_manifest = ROOT / "pre-commit" / "shared-hooks.yaml"
        self.assertTrue(root_manifest.exists(), f"missing {root_manifest}")
        self.assertTrue(shared_manifest.exists(), f"missing {shared_manifest}")

        root_text = root_manifest.read_text()
        shared_text = shared_manifest.read_text()
        for hook_id in (
            "semgrep-shared",
            "ast-grep-shared",
            "shellcheck-shared",
            "hadolint-shared",
            "yamllint-shared",
        ):
            self.assertIn(f"id: {hook_id}", root_text)
            self.assertIn(f"id: {hook_id}", shared_text)
        self.assertIn("minimum_pre_commit_version", root_text)
        self.assertTrue((ROOT / "pre-commit" / "run-semgrep-shared.sh").exists())
        self.assertTrue((ROOT / "pre-commit" / "run-ast-grep-shared.sh").exists())
        self.assertIn("pre-commit/run-semgrep-shared.sh", root_text)
        self.assertIn("pre-commit/run-ast-grep-shared.sh", root_text)
        self.assertNotIn("v0.4.0", root_text + shared_text)

    def test_pr_d_version_and_rule_catalog_are_generated(self):
        version = (ROOT / "VERSION").read_text().strip()
        self.assertEqual("v0.4.1", version)

        guide = (ROOT / "docs" / "RULE_AUTHORING.md").read_text()
        self.assertIn("<!-- RULE_CATALOG:START -->", guide)
        self.assertIn("<!-- RULE_CATALOG:END -->", guide)

        result = run_script("scripts/generate-rule-catalog.py", "--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_pr_e_rule_pack_resolver_and_workflow_contract(self):
        script = ROOT / "scripts" / "resolve-rule-packs.py"
        self.assertTrue(script.exists(), f"missing {script}")

        for pack in ("security", "reliability", "style", "infra"):
            self.assertTrue((ROOT / "semgrep" / "packs" / f"{pack}.txt").exists())
        for pack in ("reliability", "style"):
            self.assertTrue((ROOT / "ast-grep" / "packs" / f"{pack}.txt").exists())

        result = run_script(str(script), "--tool", "semgrep", "--packs", "security,infra", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        paths = json.loads(result.stdout)["paths"]
        self.assertIn("semgrep/rules/base.yaml", paths)
        self.assertIn("semgrep/rules/kubernetes.yaml", paths)
        self.assertEqual(len(paths), len(set(paths)), "resolved pack paths must be de-duplicated")

        workflow_text = (ROOT / ".github" / "workflows" / "reusable-lint.yml").read_text()
        self.assertIn("rule_packs:", workflow_text)
        self.assertIn("scripts/resolve-rule-packs.py", workflow_text)

        harness_text = (ROOT / "scripts" / "test-rules.sh").read_text()
        self.assertIn("RULE_PACKS_TO_TEST", harness_text)
        self.assertIn("resolve-rule-packs.py", harness_text)


if __name__ == "__main__":
    unittest.main()
