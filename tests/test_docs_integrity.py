#!/usr/bin/env python3
"""Docs-integrity regression guards for the deep-research-claude skill.

Run: python -m unittest discover -s tests -p 'test_*.py'

These guard the packaging-layer regressions fixed in the html-generation PR:
a doc that invokes a script removed from scripts/, a doc that points at the
pre-rename skill directory, and a {{PLACEHOLDER}} referenced by the HTML step
that is absent from the McKinsey template.
"""
import re
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_ROOT / "scripts"
DOC_FILES = sorted(SKILL_ROOT.glob("*.md")) + sorted((SKILL_ROOT / "reference").glob("*.md"))

SCRIPT_REF = re.compile(r"\bscripts/([A-Za-z0-9_]+\.py)\b")
STALE_SKILL_PATH = re.compile(r"skills/deep-research(?![-\w])")
TEMPLATE_PLACEHOLDER = re.compile(r"\{\{([A-Z_]+)\}\}")
PLACEHOLDER_META_TOKEN = "PLACEHOLDER"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestReferencedScriptsExist(unittest.TestCase):
    def test_every_doc_script_reference_resolves(self) -> None:
        missing = []
        for doc in DOC_FILES:
            for name in SCRIPT_REF.findall(_read(doc)):
                if not (SCRIPTS_DIR / name).exists():
                    missing.append(f"{doc.name} -> scripts/{name}")
        self.assertEqual([], sorted(set(missing)), f"docs reference nonexistent scripts: {missing}")


class TestNoStaleSkillPath(unittest.TestCase):
    def test_no_pre_rename_skill_directory(self) -> None:
        hits = []
        for doc in DOC_FILES:
            for lineno, line in enumerate(_read(doc).splitlines(), 1):
                if STALE_SKILL_PATH.search(line):
                    hits.append(f"{doc.name}:{lineno}: {line.strip()}")
        self.assertEqual([], hits, f"stale pre-rename skill path (use deep-research-claude): {hits}")


class TestTemplatePlaceholdersResolve(unittest.TestCase):
    def test_html_gen_placeholders_exist_in_template(self) -> None:
        doc = SKILL_ROOT / "reference" / "html-generation.md"
        template = SKILL_ROOT / "templates" / "mckinsey_report_template.html"
        if not (doc.exists() and template.exists()):
            self.skipTest("html-generation.md or McKinsey template absent")
        template_text = _read(template)
        used = {p for p in TEMPLATE_PLACEHOLDER.findall(_read(doc)) if p != PLACEHOLDER_META_TOKEN}
        missing = sorted(p for p in used if "{{%s}}" % p not in template_text)
        self.assertEqual([], missing, f"placeholders used in doc but missing from template: {missing}")


if __name__ == "__main__":
    unittest.main()
