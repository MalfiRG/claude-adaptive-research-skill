#!/usr/bin/env python3
"""Unit tests for scripts/validate_report.py against the shipped fixtures.

Run: python -m unittest discover -s tests -p 'test_*.py'

Wires up the previously-orphaned tests/fixtures/{valid,invalid}_report.md so the
structural validator has coverage. Imports the script by path (scripts/ is not a
package) and exercises the offline ReportValidator API; no network is used.
"""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = SKILL_ROOT / "tests" / "fixtures"


def _load_validator_module():
    path = SKILL_ROOT / "scripts" / "validate_report.py"
    spec = importlib.util.spec_from_file_location("validate_report", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


validate_report = _load_validator_module()
ReportValidator = validate_report.ReportValidator


class TestValidFixture(unittest.TestCase):
    def test_valid_report_passes(self) -> None:
        result = ReportValidator(FIXTURES / "valid_report.md").validate()
        self.assertTrue(result.passed, f"valid fixture should pass; errors={result.errors}")


class TestInvalidFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.result = ReportValidator(FIXTURES / "invalid_report.md").validate()

    def test_invalid_report_fails(self) -> None:
        self.assertFalse(self.result.passed)

    def test_reports_missing_required_sections(self) -> None:
        self.assertTrue(any("Missing required section" in e for e in self.result.errors))

    def test_flags_placeholder_text(self) -> None:
        self.assertTrue(any("Placeholder text" in e for e in self.result.errors))

    def test_flags_missing_bibliography(self) -> None:
        self.assertTrue(any("bibliography" in e.lower() for e in self.result.errors))


class TestCitationConsistencyChecks(unittest.TestCase):
    def _validate_text(self, text: str):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as fh:
            fh.write(text)
            tmp = Path(fh.name)
        try:
            return ReportValidator(tmp).validate()
        finally:
            tmp.unlink()

    def test_citation_range_is_rejected(self) -> None:
        result = self._validate_text("# R\n\n## Bibliography\n[1] a\n[2] b\n\nSee [1-2].\n")
        self.assertTrue(any("Citation range" in e for e in result.errors))

    def test_body_citation_absent_from_bibliography_is_flagged(self) -> None:
        result = self._validate_text("# R\n\nBody cites [9].\n\n## Bibliography\n[1] only entry\n")
        self.assertTrue(any("missing from bibliography" in e.lower() for e in result.errors))


class TestSourceFloorAndKeyFormats(unittest.TestCase):
    def _validator(self, text: str, **kwargs):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as fh:
            fh.write(text)
            tmp = Path(fh.name)
        try:
            validator = ReportValidator(tmp, **kwargs)
            validator.validate()
            return validator
        finally:
            tmp.unlink()

    def test_source_count_below_floor_is_error(self) -> None:
        bib = "\n".join(f"[{i}] source {i} https://x{i}.com" for i in range(1, 6))
        validator = self._validator(f"# R\n\n## Bibliography\n{bib}\n", min_sources=10)
        self.assertTrue(any("below floor" in e for e in validator.result.errors))

    def test_source_count_at_floor_passes_count_check(self) -> None:
        bib = "\n".join(f"[{i}] source {i} https://x{i}.com" for i in range(1, 13))
        validator = self._validator(f"# R\n\n## Bibliography\n{bib}\n", min_sources=10)
        self.assertFalse(any("below floor" in e for e in validator.result.errors))

    def test_prefixed_and_list_marker_bibliography_entries_counted(self) -> None:
        bib = "- [GPU-1] alpha https://a.com\n- [COST-2] beta https://b.com\n[S3] gamma https://c.com"
        validator = self._validator(f"# R\n\nUses [GPU-1] and [S3].\n\n## Bibliography\n{bib}\n", min_sources=3)
        self.assertFalse(any("below floor" in e for e in validator.result.errors))
        self.assertFalse(any("No bibliography entries" in e for e in validator.result.errors))

    def test_comma_grouped_body_keys_resolve_against_bibliography(self) -> None:
        bib = "- [GPU-1] alpha https://a.com\n- [GPU-2] beta https://b.com"
        validator = self._validator(f"# R\n\nClaim [GPU-1, GPU-2].\n\n## Bibliography\n{bib}\n", min_sources=2)
        self.assertFalse(any("missing from bibliography" in e.lower() for e in validator.result.errors))


if __name__ == "__main__":
    unittest.main()
