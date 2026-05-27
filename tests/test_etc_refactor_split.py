import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class EtcRefactorSplitTest(unittest.TestCase):
    def test_etc_refactors_are_split_into_small_prs(self):
        path = ROOT / "docs" / "ETC_REFACTOR_PR_SPLIT.md"
        self.assertTrue(path.exists(), f"missing {path}")
        text = path.read_text()

        for needle in (
            "PR-A: Workflow Language Matrix",
            "PR-B: Tool Version Pinning",
            "PR-C: pre-commit Packaging",
            "PR-D: Version Sync and Catalog Generation",
            "PR-E: Rule Pack Split",
            "Do not bundle",
        ):
            self.assertIn(needle, text)

    def test_each_etc_pr_has_scope_and_verification(self):
        text = (ROOT / "docs" / "ETC_REFACTOR_PR_SPLIT.md").read_text()
        for section in ("PR-A", "PR-B", "PR-C", "PR-D", "PR-E"):
            with self.subTest(section=section):
                start = text.index(section)
                next_start = len(text)
                for marker in ("PR-A", "PR-B", "PR-C", "PR-D", "PR-E"):
                    if marker == section:
                        continue
                    pos = text.find(marker, start + 1)
                    if pos != -1:
                        next_start = min(next_start, pos)
                block = text[start:next_start]
                self.assertIn("Scope:", block)
                self.assertIn("Files:", block)
                self.assertIn("Verification:", block)


if __name__ == "__main__":
    unittest.main()
