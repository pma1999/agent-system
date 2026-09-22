import importlib.util
import os
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


class BriefPathTests(unittest.TestCase):
    def test_normalizes_line_ranges_and_rejects_code_or_prose_as_paths(self):
        candidates = bundle_lint.candidate_paths(
            "`lib/orchestrator.ts:10-20` `../lib/db` "
            '`vi.mock("../lib/db")` `todayISO/yesterdayISO/fetch` `X/20` `clubelo-raw/ok`'
        )
        self.assertIn("lib/orchestrator.ts", candidates)
        self.assertIn("../lib/db", candidates)
        self.assertNotIn('vi.mock("../lib/db")', candidates)
        self.assertNotIn("todayISO/yesterdayISO/fetch", candidates)
        self.assertNotIn("X/20", candidates)
        self.assertNotIn("clubelo-raw/ok", candidates)

    def test_extensionless_relative_module_import_resolves_to_typescript_file(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            (repo / "lib").mkdir()
            (repo / "lib" / "db.ts").write_text("export {};", encoding="utf-8")
            self.assertTrue(bundle_lint.path_exists(repo, "../lib/db"))

    def test_new_file_marker_skips_existence_gate_and_test_command_check(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            bundle = repo / "plans" / "example"
            bundle.mkdir(parents=True)
            brief = bundle / "task-01-brief.md"
            brief.write_text(
                """## Goal
Create a resilience test.

## Acceptance Criteria
- red before, green after

## Scope
Touch:
- `tests/new-resilience.test.ts` (nuevo; test to create)

## Interfaces
Consumes:
- existing code

Produces:
- regression coverage

## Context Pack
- no existing path required

## Tests
Nuevo `npx vitest run tests/new-resilience.test.ts` — red before, green after.

## Report Path
`plans/example/task-01-report.md`
""",
                encoding="utf-8",
            )
            report = bundle_lint.Report()
            bundle_lint.check_brief(repo, bundle, brief, report)
            self.assertFalse([f for f in report.findings if f.severity == "blocker"])

    def test_unmarked_missing_source_file_still_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            bundle = repo / "plans" / "example"
            bundle.mkdir(parents=True)
            brief = bundle / "task-01-brief.md"
            brief.write_text(
                """## Goal
Check a source path.

## Acceptance Criteria
- red before, green after

## Scope
Touch:
- `lib/missing.ts`

## Interfaces
Consumes:
- existing code

Produces:
- regression coverage

## Context Pack
- `lib/missing.ts:10-20`

## Tests
`npx vitest run tests/existing.test.ts` — red before, green after.

## Report Path
`plans/example/task-01-report.md`
""",
                encoding="utf-8",
            )
            report = bundle_lint.Report()
            bundle_lint.check_brief(repo, bundle, brief, report)
            blockers = [f for f in report.findings if f.severity == "blocker"]
            self.assertTrue(any("lib/missing.ts" in f.message for f in blockers))


class SuffixWalkTests(unittest.TestCase):
    def setUp(self):
        bundle_lint.clear_path_cache()

    def tearDown(self):
        bundle_lint.clear_path_cache()

    def test_suffix_search_skips_node_modules_and_git(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            (repo / "src" / "deep").mkdir(parents=True)
            (repo / "src" / "deep" / "thing.ts").write_text("export {};", encoding="utf-8")
            for skipped in ("node_modules", ".git"):
                vendored = repo / skipped / "pkg"
                vendored.mkdir(parents=True)
                (vendored / "lonely-skipme.ts").write_text("export {};", encoding="utf-8")
            # The only copies live under skipped trees: absence is provable
            # without ever descending into them.
            self.assertFalse(bundle_lint.path_exists(repo, "pkg/lonely-skipme.ts"))
            # The suffix fallback still works outside the skipped trees.
            self.assertTrue(bundle_lint.path_exists(repo, "deep/thing.ts"))

    def test_suffix_cache_avoids_second_full_walk(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            (repo / "src").mkdir()
            self.assertFalse(bundle_lint.path_exists(repo, "missing/ghost.ts"))
            self.assertTrue(
                any(key[1] == "missing/ghost.ts"
                    for key in bundle_lint._PATH_SUFFIX_CACHE)
            )
            calls = []
            real_scandir = os.scandir

            def counting(path):
                calls.append(str(path))
                return real_scandir(path)

            os.scandir = counting
            try:
                self.assertFalse(bundle_lint.path_exists(repo, "missing/ghost.ts"))
            finally:
                os.scandir = real_scandir
            self.assertEqual(calls, [])

    def test_truncated_walk_degrades_to_warn_not_hang(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            (repo / "src").mkdir()
            for i in range(20):
                (repo / "src" / f"f{i:02d}.ts").write_text("x", encoding="utf-8")
            old_budget = bundle_lint._MAX_SUFFIX_WALK_ENTRIES
            bundle_lint._MAX_SUFFIX_WALK_ENTRIES = 3
            try:
                # Absence unproven under the tiny budget: never a blocker.
                self.assertTrue(bundle_lint.path_exists(repo, "missing/ghost.ts"))
                self.assertTrue(bundle_lint._SUFFIX_WALK_DEGRADED)
                bundle = repo / "plans" / "demo"
                bundle.mkdir(parents=True)
                (bundle / "plan.md").write_text("# plan\n\nWave 1: task-01\n",
                                                encoding="utf-8")
                (bundle / "progress.md").write_text("Baseline: x\n", encoding="utf-8")
                (bundle / "task-01-brief.md").write_text(
                    "## Goal\nx\n\n## Acceptance Criteria\nx\n\n"
                    "## Scope\nTouch:\n- `lib/missing-ghost.ts`\n\n"
                    "## Interfaces\nConsumes:\n- existing code\n\nProduces:\n- coverage\n\n"
                    "## Context Pack\n- `lib/missing-ghost.ts`\n\n"
                    "## Tests\n`true` — red before, green after.\n\n"
                    "## Report Path\n`plans/demo/task-01-report.md`\n",
                    encoding="utf-8",
                )
                rep = bundle_lint.run(bundle, repo, "pre-approval")
                warns = [f for f in rep.findings if f.severity == "warn"]
                self.assertTrue(any("truncada" in f.message for f in warns))
                self.assertFalse(rep.blockers)
            finally:
                bundle_lint._MAX_SUFFIX_WALK_ENTRIES = old_budget

    def test_naming_check_skips_vendored_dirs(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory)
            (bundle / "plan.md").write_text("# plan\n", encoding="utf-8")
            for skipped, name in (("node_modules", "report-vendored.md"),
                                  (".git", "summary-vendored.md")):
                vendored = bundle / skipped / "pkg"
                vendored.mkdir(parents=True)
                (vendored / name).write_text("# vendored\n", encoding="utf-8")
            report = bundle_lint.Report()
            bundle_lint.check_naming_and_leftovers(bundle, report)
            # Forbidden prefixes inside skipped trees must not flag.
            self.assertEqual(report.findings, [])


if __name__ == "__main__":
    unittest.main()
