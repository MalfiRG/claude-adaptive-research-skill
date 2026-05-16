# Claude Adaptive Research Skill

Multi-agent fan-out research skill for Claude Code. A lead orchestrator (Opus) decomposes queries into non-overlapping sub-questions, delegates to N independent Sonnet researchers (each with 5-15 searches), then synthesizes cross-agent insights into citation-backed reports.

**Origin:** Forked from [199-biotechnologies/claude-deep-research-skill](https://github.com/199-biotechnologies/claude-deep-research-skill) (v2.3.2). Architecture rewritten to multi-agent fan-out pattern based on [Anthropic's multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system).

## Architecture

```
Lead Orchestrator (Opus, this context - NEVER searches)
    |
    +-- SCOPE (define boundaries)
    +-- CLASSIFY (depth-first / breadth-first / straightforward)
    +-- DECOMPOSE (N non-overlapping sub-questions + 6-component briefs)
    +-- FAN-OUT (spawn N Sonnet agents in parallel)
    |       |-- Agent 1: Sub-question A (5-15 searches, OODA loop)
    |       |-- Agent 2: Sub-question B (5-15 searches, OODA loop)
    |       +-- Agent N: Sub-question N (5-15 searches, OODA loop)
    +-- FAN-IN (collect reports, gap analysis, optional follow-up agents)
    +-- TRIANGULATE (cross-verify across agent reports)
    +-- SYNTHESIZE (cross-agent insights no single agent could produce)
    +-- CRITIQUE + REFINE (red-team, fill gaps)
    +-- PACKAGE (final report with full bibliography)
```

## Key Differences from Upstream

| Aspect | Upstream (v2.x) | This Fork (v3) |
|---|---|---|
| Who searches | Main context fires WebSearch | Lead NEVER searches (except Quick mode) |
| Decomposition | None - overlapping thematic cuts | Explicit classify + decompose into non-overlapping sub-questions |
| Agent briefing | Vague: "Analyze X papers" | 6-component brief: objective, format, context, questions, sources, scope boundaries |
| Agent model | Unspecified | Enforced: `model="sonnet"` (Opus wasted on search+extract) |
| Source pool | 10-30 total (heavily duplicated) | 25-80+ unique (non-overlapping by construction) |
| Agent budget | Undefined | 5-15 tool calls per agent, OODA loop, stopping rule |
| Quality gate | FFS threshold | Per-agent source quality reasoning + lead cross-verification |

## Installation

```bash
git clone https://github.com/MalfiRG/claude-adaptive-research-skill.git ~/.claude/skills/deep-research
```

## Usage

```
deep research on the current state of WebAssembly outside the browser
```

```
deep research in ultradeep mode: compare SDET observability across fintech vs big tech
```

## Research Modes

| Mode | Agents | Sources | Token Cost | Best For |
|------|--------|---------|------------|----------|
| Quick | 0 (lead searches directly) | 10+ | ~4x | Fast exploration |
| Standard | 3-5 Sonnet | 25+ | ~10x | Most research questions |
| Deep | 5-8 Sonnet | 50+ | ~15x | Complex topics, critical decisions |
| UltraDeep | 8-15 Sonnet | 80+ | ~20x | Comprehensive reports, maximum rigor |

## Output

Reports saved to `~/Documents/[Topic]_Research_[Date]/`:
- Markdown (primary source of truth)
- HTML (McKinsey-style, auto-opened in browser)
- PDF (professional print via WeasyPrint)

## Quality Standards

- 25+ sources (Standard), 50+ (Deep), 80+ (UltraDeep)
- 3+ independent sources per major claim (from at least 2 different agents)
- Executive summary 200-400 words
- Findings 600-2,000 words each, prose-first (>=80%)
- Full bibliography with URLs from all agents
- Automated validation: `validate_report.py` + `verify_citations.py`

## File Structure

```
claude-adaptive-research-skill/
+-- SKILL.md                          # Skill entry point
+-- reference/
|   +-- methodology.md                # Fan-out pipeline (the core)
|   +-- report-assembly.md            # Progressive generation
|   +-- quality-gates.md              # Validation standards
|   +-- html-generation.md            # McKinsey HTML conversion
|   +-- continuation.md               # Auto-continuation for long reports
|   +-- weasyprint_guidelines.md      # PDF generation
+-- templates/
|   +-- report_template.md            # Report structure template
|   +-- mckinsey_report_template.html # HTML styling
+-- scripts/
|   +-- validate_report.py            # Structure validator
|   +-- verify_citations.py           # Citation checker
|   +-- citation_manager.py           # Citation tracking
|   +-- md_to_html.py                 # Markdown to HTML
|   +-- verify_html.py                # HTML verification
+-- tests/
    +-- fixtures/                     # Test report fixtures
```

## Version History

| Version | Date | Changes |
|---|---|---|
| 3.0 | 2026-05-16 | Multi-agent fan-out architecture. Lead never searches. Sonnet subagents with 6-component briefs. Non-overlapping decomposition. 25-80+ source targets. |
| 2.3.2 | 2026-03-19 | Last upstream-compatible version (snapshot before rewrite) |

## License

MIT
