---
name: deep-research
description: Conducts enterprise-grade research with multi-source synthesis, citation tracking, and verification. Produces citation-backed reports through a structured pipeline with source credibility scoring. Triggers on "deep research", "comprehensive analysis", "research report", "compare X vs Y", "analyze trends", or "state of the art". Not for simple lookups, debugging, or questions answerable with 1-2 searches.
---

# Deep Research v3 - Multi-Agent Fan-Out Architecture

## Core Purpose

Deliver citation-backed, verified research reports through a **hierarchical multi-agent pipeline** where a lead orchestrator decomposes queries into non-overlapping sub-questions and delegates to independent research agents, each with their own search budget and quality gates.

**Autonomy Principle:** Operate independently. Infer assumptions from context. Only stop for critical errors or incomprehensible queries.

**Architecture Principle:** The lead context is an ORCHESTRATOR, not a researcher. It decomposes, delegates, and synthesizes. It never searches.

---

## Decision Tree

```
Request Analysis
+-- Simple lookup? --> STOP: Use WebSearch directly
+-- Debugging? --> STOP: Use standard tools
+-- Complex analysis needed? --> CONTINUE

Mode Selection (determines agent count + token budget)
+-- Quick exploration --> NO fan-out, lead searches directly (~4x tokens)
+-- Standard research --> 3-5 agents, lead never searches (~10x tokens) [DEFAULT]
+-- Critical decision --> 5-8 agents, lead never searches, follow-up round (~15x tokens)
+-- Comprehensive review --> 8-15 agents, lead never searches, mandatory follow-up (~20x tokens)
```

**Default assumptions:** Technical query = technical audience. Comparison = balanced perspective. Trend = recent 1-2 years.

**Token economics:** UltraDeep = ~20x a single-context call. Only use when the question genuinely requires 8+ independent research angles. Standard (3-5 agents) covers 80% of research queries well.

---

## Workflow Overview

| Phase | Name | Quick | Standard | Deep | UltraDeep |
|-------|------|-------|----------|------|-----------|
| 1 | SCOPE | Y | Y | Y | Y |
| 2 | CLASSIFY | Y | Y | Y | Y |
| 2.5 | DECOMPOSE | - | Y | Y | Y |
| 3 | FAN-OUT (or direct search in Quick) | direct | Y | Y | Y |
| 3.5 | FAN-IN | - | Y | Y | Y |
| 4 | TRIANGULATE | - | Y | Y | Y |
| 4.5 | OUTLINE REFINEMENT | - | Y | Y | Y |
| 5 | SYNTHESIZE | - | Y | Y | Y |
| 6 | CRITIQUE | - | - | Y | Y |
| 7 | REFINE | - | - | Y | Y |
| 8 | PACKAGE | Y | Y | Y | Y |

---

## Execution

**On invocation, load relevant reference files:**

1. **Phase 1-5:** Load [methodology.md](./reference/methodology.md) for detailed phase instructions
2. **Phase 8 (Report):** Load [report-assembly.md](./reference/report-assembly.md) for progressive generation
3. **HTML/PDF output:** Load [html-generation.md](./reference/html-generation.md)
4. **Quality checks:** Load [quality-gates.md](./reference/quality-gates.md)
5. **Long reports (>18K words):** Load [continuation.md](./reference/continuation.md)

**Templates:**
- Report structure: [report_template.md](./templates/report_template.md)
- HTML styling: [mckinsey_report_template.html](./templates/mckinsey_report_template.html)

**Post-production validation:**
- `python scripts/verify_citations.py --report [path]` (URL accessibility + DOI resolution + hallucination detection)

---

## Output Contract

**Required sections:**
- Executive Summary (200-400 words)
- Introduction (scope, methodology, assumptions)
- Main Analysis (4-8 findings, 600-2,000 words each, cited)
- Synthesis & Insights (patterns, implications)
- Limitations & Caveats
- Recommendations
- Bibliography (COMPLETE - every citation, no placeholders)
- Methodology Appendix

**Output files (all to `~/Documents/[Topic]_Research_[YYYYMMDD]/`):**
- Markdown (primary source)
- HTML (McKinsey style, auto-opened)
- PDF (professional print, auto-opened)

**Quality standards:**
- 25+ sources (Standard), 50+ (Deep), 80+ (UltraDeep)
- 3+ independent sources per major claim
- All claims cited immediately [N]
- No placeholders, no fabricated citations
- Prose-first (>=80%), bullets sparingly

---

## When to Use / NOT Use

**Use:** Comprehensive analysis, technology comparisons, state-of-the-art reviews, multi-perspective investigation, market analysis.

**Do NOT use:** Simple lookups, debugging, 1-2 search answers, quick time-sensitive queries.
