#!/usr/bin/env python3
"""Validate deep-research Markdown report structure and citation consistency."""

from __future__ import annotations

import argparse
import logging
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

LOGGER = logging.getLogger(__name__)
REQUIRED_SECTIONS: tuple[str, ...] = (
    "Executive Summary",
    "Introduction",
    "Main Analysis",
    "Synthesis",
    "Limitations",
    "Recommendations",
    "Bibliography",
    "Methodology",
)
PLACEHOLDER_PATTERN = re.compile(
    r"\b(TBD|TODO|FIXME|placeholder|additional sources|content continues|etc\.)\b",
    re.IGNORECASE,
)
CITATION_PATTERN = re.compile(r"\[([A-Za-z]{0,12}[-_ ]?\d+)\]")
CITATION_RANGE_PATTERN = re.compile(r"\[\d+\s*-\s*\d+\]")
BIBLIOGRAPHY_ENTRY_PATTERN = re.compile(
    r"^[-*]?\s*(?:\[([^\]]+)\]|(\d+)\.)\s+(.*)$", re.MULTILINE
)
BODY_KEY_PATTERN = re.compile(r"[A-Za-z]{0,12}[-_ ]?\d+[A-Za-z]?")
URL_PATTERN = re.compile(r"https?://\S+")
HEADING_PATTERN = re.compile(r"^##+\s+(.+?)\s*$", re.MULTILINE)

DEFAULT_MIN_SOURCES = 10
MIN_RICHNESS_CHARS = 4


@dataclass
class ValidationResult:
    """Container for validation findings."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Return true when no blocking errors were found."""
        return not self.errors

    def add_error(self, message: str) -> None:
        """Add a blocking validation error."""
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        """Add a non-blocking validation warning."""
        self.warnings.append(message)


class ReportValidator:
    """Validate one Markdown research report."""

    def __init__(self, report_path: Path, min_sources: int = DEFAULT_MIN_SOURCES) -> None:
        self.report_path = report_path
        self.content = report_path.read_text(encoding="utf-8")
        self.min_sources = min_sources
        self.result = ValidationResult()

    def validate(self) -> ValidationResult:
        """Run all validation checks and return the result."""
        self._check_required_sections()
        self._check_placeholders()
        self._check_citations()
        self._check_summary_length()
        self._check_word_count()
        return self.result

    def _check_required_sections(self) -> None:
        headings = [heading.lower() for heading in HEADING_PATTERN.findall(self.content)]
        for section in REQUIRED_SECTIONS:
            if not any(section.lower() in heading for heading in headings):
                self.result.add_error(f"Missing required section: {section}")

    def _check_placeholders(self) -> None:
        matches = sorted(set(match.group(0) for match in PLACEHOLDER_PATTERN.finditer(self.content)))
        if matches:
            self.result.add_error(f"Placeholder text found: {', '.join(matches)}")

    def _check_citations(self) -> None:
        if CITATION_RANGE_PATTERN.search(self.content):
            self.result.add_error("Citation range found. Use individual citations instead.")

        body, bibliography = self._split_bibliography()
        body_citations = self._body_citation_keys(body)
        entries = self._bibliography_entries(bibliography)
        bibliography_citations = {key for key, _ in entries}

        if not bibliography_citations:
            self.result.add_error("No bibliography entries found")
            return

        missing = sorted(body_citations - bibliography_citations)
        if missing:
            self.result.add_error(f"Citations missing from bibliography: {', '.join(missing)}")

        unused = sorted(bibliography_citations - body_citations)
        if unused:
            self.result.add_warning(f"Bibliography entries not cited in body: {', '.join(unused)}")

        source_count = len(bibliography_citations)
        if source_count < self.min_sources:
            self.result.add_error(
                f"Source count {source_count} below floor of {self.min_sources} "
                "for the selected mode"
            )

        bare = [key for key, content in entries if self._is_bare_url(content)]
        if bare:
            preview = ", ".join(bare[:5]) + (" ..." if len(bare) > 5 else "")
            self.result.add_error(
                f"{len(bare)} bibliography entries are bare URLs with no title/author/date "
                f"({preview}). Format: [N] Author/Org (Year). \"Title\". Publisher. URL"
            )

    @staticmethod
    def _bibliography_entries(bibliography: str) -> list[tuple[str, str]]:
        entries: list[tuple[str, str]] = []
        for match in BIBLIOGRAPHY_ENTRY_PATTERN.finditer(bibliography):
            key = (match.group(1) or match.group(2)).strip()
            content = match.group(3).strip()
            entries.append((key, content))
        return entries

    @staticmethod
    def _is_bare_url(content: str) -> bool:
        residual = URL_PATTERN.sub("", content)
        residual = re.sub(r"[^A-Za-z0-9]", "", residual)
        return len(residual) < MIN_RICHNESS_CHARS

    @staticmethod
    def _body_citation_keys(body: str) -> set[str]:
        keys: set[str] = set()
        for span in re.findall(r"\[([^\]]+)\]", body):
            for token in span.split(","):
                token = token.strip()
                if BODY_KEY_PATTERN.fullmatch(token):
                    keys.add(token)
        return keys

    def _check_summary_length(self) -> None:
        summary = self._section_text("Executive Summary")
        if not summary:
            return
        word_count = len(re.findall(r"\b\w+\b", summary))
        if word_count < 200 or word_count > 400:
            self.result.add_error(
                f"Executive Summary length is {word_count} words; expected 200-400"
            )

    def _check_word_count(self) -> None:
        word_count = len(re.findall(r"\b\w+\b", self.content))
        if word_count < 500:
            self.result.add_error(f"Report is too short: {word_count} words")

    def _split_bibliography(self) -> tuple[str, str]:
        match = re.search(r"^##\s+Bibliography\s*$", self.content, re.MULTILINE | re.IGNORECASE)
        if not match:
            return self.content, ""
        return self.content[: match.start()], self.content[match.end() :]

    def _section_text(self, section_name: str) -> str:
        pattern = re.compile(
            rf"^##\s+{re.escape(section_name)}\s*$\n(?P<body>.*?)(?=^##\s+|\Z)",
            re.MULTILINE | re.DOTALL | re.IGNORECASE,
        )
        match = pattern.search(self.content)
        return match.group("body").strip() if match else ""


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Validate a deep-research Markdown report")
    parser.add_argument("--report", "-r", required=True, type=Path, help="Report path")
    parser.add_argument(
        "--min-sources",
        type=int,
        default=DEFAULT_MIN_SOURCES,
        help=(
            "Minimum distinct bibliography sources required (mode floor: "
            "Quick 10, Standard 25, Deep 50, UltraDeep 80). Below this is a "
            "blocking error."
        ),
    )
    return parser.parse_args()


def configure_logging() -> None:
    """Configure console logging."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")


def main() -> int:
    """Run the validator."""
    configure_logging()
    args = parse_args()

    if not args.report.exists():
        LOGGER.error("ERROR: Report file not found: %s", args.report)
        return 1

    try:
        validator = ReportValidator(args.report, min_sources=args.min_sources)
    except OSError as exc:
        LOGGER.error("ERROR: Cannot read report: %s", exc)
        return 1

    result = validator.validate()

    LOGGER.info("STRUCTURE VALIDATION: %s", args.report)
    for warning in result.warnings:
        LOGGER.warning("WARNING: %s", warning)
    for error in result.errors:
        LOGGER.error("ERROR: %s", error)

    if result.passed:
        LOGGER.info("REPORT VALIDATION PASSED")
        return 0

    LOGGER.error("REPORT VALIDATION FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
