# Quality Gates and Standards

## Validation Scripts

### Citation Verification

```bash
python scripts/verify_citations.py --report [path]
```

**Checks:**
- DOI resolution (verifies citation exists)
- Title/year matching (detects mismatched metadata)
- Flags suspicious entries (recent year without DOI, no URL, failed verification)
- Source-diversity: warns when any single domain supplies >20% of cited sources (`--strict` fails). Concentration on a primary/authoritative domain (vendor spec page, standards body, model card host) is acceptable - the smell is concentration on secondary summary sites. Judge by tier, not raw share.

**On suspicious citations:** Review flagged, remove/replace fabricated, re-run until clean.

### Structure & Quality Validation

```bash
python scripts/validate_report.py --report [path] --min-sources <mode-floor>
```

Pass `--min-sources` matching the selected mode: **Quick 10, Standard 25, Deep 50, UltraDeep 80**. A source count below the floor is a blocking error, not a warning. Omitting the flag falls back to a floor of 10.

**Automated checks:**
1. Executive summary length (200-400 words)
2. Required sections present
3. Citations recognized in any key format - numeric `[1]`, prefixed `[S1]`, or namespaced `[GPU-1]`; comma-grouped `[GPU-1, GPU-2]` and list-marker bibliography entries (`- [GPU-1] ...`) supported
4. Bibliography matches citations (body keys resolve to entries and vice versa)
5. No placeholder text (TBD, TODO)
6. Word count reasonable (500-10000)
7. Source count at or above the mode floor (`--min-sources`)
8. Bibliography entries are not bare URLs - each must carry title/author/date text, not just a link
9. Findings nested under a `## Main Analysis` heading (required section)
10. No broken internal links

**Failure handling:**
- Attempt 1: Auto-fix formatting/links
- Attempt 2: Manual review + correction
- After 2 failures: STOP, report issues, ask user

### Validation Loop Protocol

**After generating ANY report, run this loop:**

1. Run `python scripts/validate_report.py --report [path]`
2. Run `python scripts/verify_citations.py --report [path]`
3. If EITHER fails:
   - Read error output carefully
   - Fix the specific issues identified
   - Re-run BOTH validators
4. Maximum 3 retry cycles. If still failing after 3 cycles: STOP and report issues to user.

**Do NOT skip validation.** Every report must pass both scripts before delivery.

---

## Anti-Fatigue Protocol

### Quality Check (Apply to EVERY Section)

Before considering section complete:
- [ ] **Paragraph count:** >=3 paragraphs for major sections
- [ ] **Prose-first:** <20% bullets (>=80% flowing prose)
- [ ] **No placeholders:** Zero "Content continues", "Due to length", "[Sections X-Y]"
- [ ] **Evidence-rich:** Specific data points, statistics, quotes
- [ ] **Citation density:** Major claims cited in same sentence

**If ANY fails:** Regenerate section before continuing.

### Bullet Point Policy

- Use bullets SPARINGLY: Only for distinct lists (product names, company roster, enumerated steps)
- NEVER use bullets as primary content delivery
- Each finding requires substantive prose (3-5+ paragraphs)
- Convert: "* Market size: $2.4B" -> "The global market reached $2.4 billion in 2023, driven by increasing consumer demand [1]."

---

## Bibliography Requirements (ZERO TOLERANCE)

**Report is UNUSABLE without complete bibliography.**

**MUST:**
- Include EVERY citation [N] used in report body
- Format: [N] Author/Org (Year). "Title". Publication. URL (Retrieved: Date)
- Each entry on its own line, complete

**NEVER:**
- Placeholders: "[8-75] Additional citations", "...continue...", "etc."
- Ranges: "[3-50]" instead of individual entries
- Truncation: Stop at 10 when 30 cited
- **Bare URLs**: an entry that is only a link (`[3] https://...`) with no title/author/date. Every entry MUST carry descriptive text - `[N] Title - Publisher - Date - URL` at minimum. A bare-URL bibliography defeats credibility assessment and citation verification, and is a blocking validator error.

## Report Structure (required headings)

Findings are the body of the analysis, but they MUST be nested as `### Finding N` subsections under a single `## Main Analysis` heading - not promoted to top-level `## Finding N`. The validator requires a literal `Main Analysis` section; a report that heads findings at `##` level with no wrapper fails the structure check. Mirror the section order in `report_template.md`: Executive Summary, Introduction, Main Analysis (findings inside), Synthesis & Insights, Limitations & Caveats, Recommendations, Bibliography, Methodology.

---

## Writing Standards

### Core Principles

| Principle | Description |
|-----------|-------------|
| Narrative-driven | Flowing prose, story with beginning/middle/end |
| Precision | Every word deliberately chosen |
| Economy | No fluff, eliminate fancy grammar |
| Clarity | Exact numbers embedded in sentences |
| Directness | State findings without embellishment |
| High signal-to-noise | Dense information, respect reader time |

### Precision Examples

| Bad | Good |
|-----|------|
| "significantly improved outcomes" | "reduced mortality 23% (p<0.01)" |
| "several studies suggest" | "5 RCTs (n=1,847) show" |
| "potentially beneficial" | "increased biomarker X by 15%" |
| "* Market: $2.4B" | "The market reached $2.4 billion in 2023 [1]." |

---

## Source Attribution Standards

**Immediate citation:** Every factual claim followed by [N] in same sentence.

**Quote sources directly:**
- "According to [1]..."
- "[1] reports..."

**Distinguish fact from synthesis:**
- GOOD: "Mortality decreased 23% (p<0.01) in the treatment group [1]."
- BAD: "Studies show mortality improved significantly."

**No vague attributions:**
- NEVER: "Research suggests...", "Studies show...", "Experts believe..."
- ALWAYS: "Smith et al. (2024) found..." [1]

**Label speculation:**
- GOOD: "This suggests a potential mechanism..."
- BAD: "The mechanism is..." (presented as fact)

**Admit uncertainty:**
- GOOD: "No sources found addressing X directly."
- BAD: Fabricating a citation

---

## Source Tier Preference

Prefer **primary artifacts** over secondary summaries for any quantitative or definitional claim. This holds across every discipline:

| Tier | Examples (domain-neutral) |
|------|---------------------------|
| Primary (prefer) | Vendor/standards spec sheets, official documentation, peer-reviewed papers, raw config/data/source files, primary datasets, regulatory filings, court records, original measurements |
| Secondary (use to contextualize) | Review articles, textbooks, reputable journalism that cites primaries |
| Tertiary (avoid as the cited source) | SEO blog roundups, content-farm "best X in YEAR" pages, AI-generated summaries, unsourced aggregators |

**Rules:**
- Any **quantitative or definitional** claim (a spec value, a constant, a measured result, a formal definition) cites the **primary artifact** - e.g. the actual config/spec/dataset/paper - not a blog that restates it. If only a secondary source is available, cite it AND mark the claim for primary-source follow-up.
- When a secondary source asserts a number, attempt to trace it to its primary before citing. Cite the primary if found.
- Tertiary sources may motivate a search but should not be the load-bearing citation for any factual claim.

## Empirically-Checkable Claims

Where a key claim is **empirically verifiable**, state the concrete check that would confirm or refute it - the measurement, query, calculation, experiment, or observation a reader could run. Domain-neutral: a VRAM budget states the load-and-measure test; a performance claim states the benchmark; a market-size figure states the dataset and filter; a derivation states the inputs. This converts assertions into falsifiable, reproducible findings.

## Weak-Claim Containment

A claim the report itself flags as weak, single-source, unverified, or "weakest-sourced" MUST NOT appear inside Recommendations or be stated as actionable fact. Resolve it one of two ways before delivery:
1. Repair it with one additional targeted search that raises it to the 3-independent-source standard, or
2. Demote it to the Limitations & Caveats section, explicitly labeled.

Self-flagged uncertainty in a recommendation is a defect, not honesty - move the hedge out of the action item.

## Anti-Hallucination Protocol

- **Source grounding:** Every factual claim MUST cite specific source immediately [N]
- **Clear boundaries:** Distinguish FACTS (from sources) from SYNTHESIS (your analysis)
- **Explicit markers:** Use "According to [1]..." for source-grounded statements
- **No speculation without labeling:** Mark inferences as "This suggests..."
- **Verify before citing:** If unsure source says X, do NOT fabricate citation
- **When uncertain:** Say "No sources found for X" rather than inventing references

---

## Report Quality Standards

**Every report must have:**
- Sources at or above the mode floor (Quick 10, Standard 25, Deep 50, UltraDeep 80); below-floor is a blocking error, not a footnote
- 3+ sources per major claim
- Primary-tier citation for every quantitative/definitional claim (see Source Tier Preference)
- Executive summary 200-400 words
- Full citations with URLs
- Credibility assessment
- Limitations section
- Methodology documented
- No placeholders

**Priority:** Thoroughness over speed. Quality > speed.

---

## Error Handling

**Stop immediately if:**
- 2 validation failures on same error
- <5 sources after exhaustive search
- User interrupts/changes scope

**Graceful degradation:**
- 5-10 sources: Note in limitations, extra verification
- Time constraint: Package partial, document gaps
- High-priority critique: Address immediately

**Error format:**
```
Issue: [Description]
Context: [What was attempted]
Tried: [Resolution attempts]
Options:
   1. [Option 1]
   2. [Option 2]
```
