import importlib.util
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).parents[1]
    / "source"
    / "orchestration"
    / "skill"
    / "scripts"
    / "bundle_lint.py"
)
SPEC = importlib.util.spec_from_file_location("bundle_lint", SCRIPT)
assert SPEC and SPEC.loader
bundle_lint = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = bundle_lint
SPEC.loader.exec_module(bundle_lint)


class ReviewFindingStatusTests(unittest.TestCase):
    def lint_review(self, content: str):
        with tempfile.TemporaryDirectory() as directory:
            review = Path(directory) / "task-01-review.md"
            normalized = "\n".join(line.strip() for line in textwrap.dedent(content).splitlines())
            review.write_text(normalized, encoding="utf-8")
            report = bundle_lint.Report()
            bundle_lint.check_reports_and_reviews(Path(directory), report)
            return report.findings

    def test_wrapped_required_change_status_is_current(self):
        findings = self.lint_review(
            """## Required Changes
            - `RC-01` | Problem: a real issue
              Required change: fixed in the follow-up.
              Status: resolved in Round 1.

            ## Remediation History
            ### Round 0
            - `RC-01` was open before the fix.
            """
        )
        self.assertEqual(findings, [])

    def test_latest_remediation_result_is_used_when_item_has_no_status(self):
        findings = self.lint_review(
            """## Required Changes
            - `RC-01` | Problem: a real issue

            ## Remediation History
            ### Round 1
            - IDs checked: `RC-01`
            - Result: unresolved.
            ### Round 2
            - IDs checked: `RC-01`
            - Result: resolved.
            """
        )
        self.assertEqual(findings, [])

    def test_current_open_status_remains_a_blocker(self):
        findings = self.lint_review(
            """## Required Changes
            - `RC-01` | Problem: still broken | Status: open

            ## Remediation History
            ### Round 1
            - IDs checked: `RC-01`
            - Result: resolved.
            """
        )
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].severity, "blocker")
        self.assertIn("RC-01", findings[0].message)

    def test_accepted_current_status_overrides_historical_open_sentence(self):
        findings = self.lint_review(
            """## Required Changes
            - `RC-01` | Problem: accepted product decision | Status: accepted — reason recorded.

            ## Remediation History
            ### Original review
            - `RC-01` quedó abierto antes de la decisión del parent.
            """
        )
        self.assertEqual(findings, [])

    def test_missing_status_is_a_warning_not_a_false_blocker(self):
        findings = self.lint_review(
            """## Required Changes
            - `RC-01` | Problem: a finding without a current status
            """
        )
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].severity, "warn")


if __name__ == "__main__":
    unittest.main()
