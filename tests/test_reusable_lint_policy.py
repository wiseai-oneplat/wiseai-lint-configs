import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "reusable-lint.yml"


class ReusableLintPolicyTest(unittest.TestCase):
    def test_workflow_declares_reporting_and_blocking_inputs(self):
        text = WORKFLOW.read_text()
        for needle in (
            "reporter_mode:",
            "reviewdog_level:",
            "lint_mode:",
            "fail_on_error:",
            "REVIEWDOG_REPORTER",
            "REVIEWDOG_LEVEL",
            "REVIEWDOG_FAIL_ON_ERROR",
        ):
            self.assertIn(needle, text)

    def test_reviewdog_commands_use_shared_policy_env(self):
        text = WORKFLOW.read_text()
        self.assertIn('-reporter="${REVIEWDOG_REPORTER}"', text)
        self.assertIn('-level="${REVIEWDOG_LEVEL}"', text)
        self.assertIn('-fail-on-error="${REVIEWDOG_FAIL_ON_ERROR}"', text)
        self.assertNotIn("-reporter=github-pr-review", text)
        self.assertNotIn("-level=warning", text)

    def test_reviewdog_actions_receive_shared_policy_inputs(self):
        text = WORKFLOW.read_text()
        for action in (
            "reviewdog/action-shellcheck",
            "reviewdog/action-hadolint",
            "reviewdog/action-yamllint",
            "reviewdog/action-tfsec",
        ):
            with self.subTest(action=action):
                index = text.find(action)
                self.assertNotEqual(index, -1, f"missing {action}")
                block = text[index : index + 350]
                self.assertIn("reporter: ${{ inputs.reporter_mode }}", block)
                self.assertIn("level: ${{ inputs.reviewdog_level }}", block)
                self.assertIn("fail_on_error: ${{ inputs.fail_on_error || inputs.lint_mode == 'blocking' }}", block)

    def test_summary_only_tools_write_step_summary_and_respect_blocking(self):
        text = WORKFLOW.read_text()
        for job in ("helm-lint", "kubeconform"):
            with self.subTest(job=job):
                index = text.find(f"{job}:")
                self.assertNotEqual(index, -1, f"missing {job}")
                block = text[index : index + 1400]
                self.assertIn("GITHUB_STEP_SUMMARY", block)
                self.assertIn('REVIEWDOG_FAIL_ON_ERROR" = "true"', block)

    def test_docs_explain_reporting_and_lint_modes(self):
        text = (ROOT / "docs" / "INTEGRATION.md").read_text()
        for needle in (
            "reporter_mode",
            "reviewdog_level",
            "lint_mode",
            "advisory",
            "blocking",
            "fail_on_error",
        ):
            self.assertIn(needle, text)
        self.assertNotIn("-reporter=github-pr-review", text)


if __name__ == "__main__":
    unittest.main()
