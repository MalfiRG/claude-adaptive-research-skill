# Deep Research Methodology v3: Multi-Agent Fan-Out Pipeline

## Architecture Overview

```
Lead Orchestrator (this context)
    |
    +-- Phase 1: SCOPE (define boundaries)
    +-- Phase 2: CLASSIFY (query type -> agent count)
    +-- Phase 2.5: DECOMPOSE (non-overlapping sub-questions + briefs)
    +-- Phase 3: FAN-OUT (spawn N agents in parallel)
    |       |-- Agent 1: Sub-question A (5-15 searches)
    |       |-- Agent 2: Sub-question B (5-15 searches)
    |       |-- Agent 3: Sub-question C (5-15 searches)
    |       +-- Agent N: Sub-question N (5-15 searches)
    +-- Phase 3.5: FAN-IN (collect + identify gaps + optional follow-up)
    +-- Phase 4: TRIANGULATE (cross-verify across agent reports)
    +-- Phase 4.5: OUTLINE REFINEMENT (adapt structure to evidence)
    +-- Phase 5: SYNTHESIZE (connect insights, generate frameworks)
    +-- Phase 6: CRITIQUE (red-team the analysis)
    +-- Phase 7: REFINE (fill gaps from critique)
    +-- Phase 8: PACKAGE (final report)
```

**CRITICAL CONSTRAINT:** In Phases 2.5-3.5, the lead orchestrator MUST NOT call WebSearch or WebFetch. All information gathering is delegated to subagents via the `Agent` tool. If you find yourself reaching for WebSearch during these phases, STOP and write an Agent brief instead. The only exception is Quick mode, where the lead MAY search directly.

---

## Phase 1: SCOPE - Research Framing

**Objective:** Define research boundaries and success criteria.

**Activities:**
1. Decompose the question into core components
2. Identify stakeholder perspectives
3. Define scope boundaries (what's in/out)
4. Establish success criteria
5. List key assumptions to validate
6. Get the current date: `date +%Y-%m-%d` (use for all recency filtering)

**Output:** Structured scope document with research boundaries.

---

## Phase 2: CLASSIFY - Query Type Determination

**Objective:** Determine query type and agent count.

Explicitly reason about which category fits:

### Query Types

**Depth-first query** - Multiple perspectives on the SAME issue:
- Parallel agents exploring different viewpoints, methodologies, or source types
- Example: "What are the most effective approaches to microservice testing?"
- Agent strategy: Each agent researches from a different methodological angle

**Breadth-first query** - Problem broken into DISTINCT independent sub-questions:
- Parallel agents handling separate sub-topics that together form the answer
- Example: "Compare the economic systems of three Nordic countries"
- Agent strategy: Each agent owns one sub-topic completely

**Straightforward query** - Focused, well-defined, needs only depth not breadth:
- Single focused investigation, possibly with 1-2 agents for verification
- Example: "What is the current state of WebAssembly adoption?"
- Agent strategy: 1-2 agents with clear scope

### Agent Count Decision

| Query Complexity | Agent Count | Token Multiplier |
|---|---|---|
| Straightforward / Quick mode | 1-2 | ~4x |
| Standard depth or breadth | 3-5 | ~10x |
| Multi-faceted, high-stakes | 5-8 | ~15x |
| Comprehensive, many distinct components | 8-15 | ~20x |

**IMPORTANT:** Never spawn more than 15 agents. If a task seems to need more, restructure - consolidate similar sub-topics into fewer, broader briefs.

**Output:** Query type classification + target agent count + reasoning.

---

## Phase 2.5: DECOMPOSE - Sub-Question Generation & Agent Briefing

**Objective:** Produce N non-overlapping sub-questions, each with a complete agent brief.

This is the LOAD-BEARING phase. Fan-out without specific briefs = same duplication problem with more agents.

### Decomposition Rules

1. **Non-overlapping:** Each sub-question must cover territory NO other sub-question covers. If two agents would search the same keywords, merge them or redraw boundaries.
2. **Collectively exhaustive:** The union of all sub-questions must fully cover the original research question.
3. **Independently answerable:** Each sub-question can be researched without results from other agents.
4. **Appropriately scoped:** Each should need 5-15 tool calls to answer well.
5. **Decision-axis coverage:** The sub-questions must collectively cover every decision-relevant axis the query implies. In particular, if the user named a specific candidate, option, hypothesis, or tool, allocate a sub-question to it AND a sub-question to its principal alternatives - never evaluate the named option in isolation. Also cover the dominant trade-off axis of the domain (whatever the question actually turns on: cost, accuracy, latency, risk, reproducibility, feasibility, etc.). This rule is domain-neutral - it applies whether the query is a hardware choice, an algorithm comparison, a scientific question, or a market analysis. A report that answers only the named option without its alternatives and trade-off axis is under-decomposed.

### Agent Brief Template (6 Components - ALL REQUIRED)

For each subagent, produce a brief with ALL six components:

```
1. OBJECTIVE: [One clear research question - what this agent must answer]

2. OUTPUT FORMAT: [What the report should contain and how to structure it.
   Default: "Dense prose report with inline citations. Flag any speculative
   claims. Include exact quotes from key sources. End with a 'Key Findings'
   bullet list (max 10 items)."]

3. BACKGROUND CONTEXT: [What the broader research is about, why this
   sub-question matters, what the lead will do with the results]

4. KEY QUESTIONS TO ANSWER: [3-7 specific sub-sub-questions that together
   answer the objective. These guide the agent's search strategy.]

5. SUGGESTED SOURCES & TOOLS: [Starting points, domains to prioritize,
   tools to use. e.g., "Start with arxiv.org for papers, then check
   industry blogs. Use WebFetch for full content of promising results."]

6. SCOPE BOUNDARIES: [What NOT to research - explicit exclusions that
   prevent overlap with sibling agents. e.g., "Do NOT cover pricing -
   Agent 3 handles that. Do NOT cover history before 2024."]
```

### Worked Example

**Research question:** "What is the current state of WebAssembly outside the browser?"

**Classification:** Breadth-first (distinct domains of WASM usage)

**Decomposition into 4 agents:**

**Agent 1 Brief:**
```
OBJECTIVE: Research WebAssembly usage in server-side/cloud computing as of 2025-2026.

OUTPUT FORMAT: Dense prose report covering current production deployments,
performance benchmarks vs containers, and adoption trajectory. Include
exact version numbers and benchmark figures. Flag speculation. End with
Key Findings (max 10 items).

BACKGROUND: We're writing a comprehensive research report on WASM outside
the browser. Your findings will be synthesized with 3 other agents covering
edge computing, embedded/IoT, and the plugin/extension ecosystem.

KEY QUESTIONS:
- Which cloud providers offer WASM runtimes in production (not preview)?
- What are the measured cold-start and throughput numbers vs Docker?
- Which companies run WASM in production at scale? What workloads?
- What is WASI Preview 2 status and adoption?
- What are the main blockers to broader server-side adoption?

SUGGESTED SOURCES: Start with CNCF landscape, Bytecode Alliance blog,
Fermyon/Cosmonic/Fastly engineering blogs. Use WebFetch on promising
results for full content. Check arxiv for recent benchmarking papers.

SCOPE BOUNDARIES: Do NOT cover browser WASM, edge computing (Agent 2
handles that), IoT/embedded (Agent 3), or plugin systems (Agent 4).
Focus exclusively on traditional server/cloud deployment.
```

---

## Phase 3: FAN-OUT - Parallel Agent Deployment

**Objective:** Spawn all research agents simultaneously.

**FORBIDDEN TOOLS IN THIS PHASE:** WebSearch, WebFetch. All research is delegated.

### Execution Protocol

**Step 1: Launch ALL agents in a single message with parallel tool calls.**

Use the `Agent` tool with `subagent_type="general-purpose"` and `model="sonnet"`:

```
Agent(
  subagent_type="general-purpose",
  model="sonnet",
  description="Research: [brief objective summary]",
  prompt="[FULL AGENT BRIEF - see below]"
)
```

**Model selection:** Subagents MUST use `model="sonnet"`. Their task (search + read + extract + report) is Sonnet-tier work. Opus stays only in the lead context (Phases 2.5, 3.5, 4-8) where cross-agent synthesis and insight generation require it. This matches Anthropic's production architecture (Opus lead + Sonnet workers) which outperforms single-agent Opus by 90%.

**Step 2: Construct each agent's full prompt.**

Each agent receives a self-contained prompt built from:
1. The system instructions (research process + guidelines)
2. Their specific brief from Phase 2.5

### Subagent System Prompt (embed in every agent's prompt)

```
You are a research subagent working as part of a team. The current date is
[INSERT DATE]. You have been given a clear task by a lead researcher.
Use your available tools (WebSearch, WebFetch) to accomplish this task.

RESEARCH PROCESS:

1. PLANNING: Think through the task. Make a research plan. Determine a
   'research budget' - how many tool calls to conduct:
   - Simple tasks: under 5 tool calls
   - Medium tasks: 5-10 tool calls
   - Complex multi-part tasks: 10-15 tool calls
   Stick to this budget. Going over wastes resources.

2. TOOL SELECTION:
   - WebSearch: for discovering sources (keep queries SHORT - under 5 words)
   - WebFetch: ALWAYS use to get full content of promising search results
   The core loop: WebSearch to find sources -> WebFetch to read them fully.
   Never rely solely on search snippets.

3. RESEARCH LOOP (OODA):
   - OBSERVE: What information is gathered? What's still needed?
   - ORIENT: What tools and queries would be best next?
   - DECIDE: Choose the most promising next action
   - ACT: Execute with specific tool use
   Repeat 5-15 times. Never use the exact same query twice.

4. PARALLEL TOOL CALLS: When you need multiple independent searches,
   fire them in a SINGLE message. Do not serialize independent lookups.

5. SOURCE QUALITY: After each result, reason about quality:
   - Is this speculation (future tense, "could", "may") or established fact?
   - Is this an original source or aggregator/SEO farm?
   - Does it have specific data points or just generalities?
   - Flag issues rather than presenting dubious claims as facts.

6. STOPPING RULE: When results show diminishing returns (same info
   repeating, queries returning nothing new), STOP searching and compose
   your report. Do not waste budget on redundant searches.

REPORT FORMAT: Your report goes to a lead researcher who synthesizes
across multiple agents. Be:
- Dense and information-rich (not padded)
- Specific (exact numbers, dates, versions, names)
- Cited (note which URL provided each major fact)
- Honest about uncertainty (flag speculation, single-source claims)

End your report with:
## Key Findings
- [Max 10 bullet points summarizing the most important discoveries]

## Sources Used
- [List of URLs consulted with brief description of each]
```

**Step 3: Wait for all agents to complete.**

Do not begin Phase 3.5 until all agents have returned. If one agent fails or times out, proceed with remaining results and note the gap.

---

## Phase 3.5: FAN-IN - Result Collection & Gap Analysis

**Objective:** Collect all agent reports, identify gaps, optionally spawn follow-up agents.

### Activities

1. **Collect all reports** - Read each agent's full response.

2. **Tally source pool:**
   - Count unique URLs across all agents
   - Quality gate: Standard needs 25+, Deep needs 50+, UltraDeep needs 80+
   - If below threshold, spawn 1-2 targeted follow-up agents

3. **Identify gaps:**
   - Which sub-questions got weak coverage (few sources, low specificity)?
   - Did any agent flag "couldn't find reliable information on X"?
   - Are there contradictions between agents that need resolution?

4. **Optional follow-up round (Deep/UltraDeep only):**
   - Spawn 1-3 targeted agents to fill specific gaps
   - These get VERY narrow briefs: "Resolve the contradiction between
     Agent 2's claim that X and Agent 4's claim that Y" or "Find
     quantitative data on Z - previous agent found only qualitative."
   - Budget: 3-5 tool calls each (surgical, not exploratory)

5. **Merge into unified fact base:**
   - Organize findings by theme/sub-question
   - Note source provenance (which agent found what)
   - Flag contradictions for Phase 4 resolution
   - Track confidence levels

**Output:** Unified fact base organized by theme, with source tracking and gap annotations.

---

## Phase 4: TRIANGULATE - Cross-Reference Verification

**Objective:** Validate information across multiple independent sources.

**Activities:**
1. Identify core claims that drive the analysis
2. Cross-reference each core claim across 3+ sources from DIFFERENT agents
3. Flag contradictions or single-source claims
4. Assess source credibility and recency
5. Note consensus vs. debate areas
6. Document verification status per claim

**Quality Standards:**
- Core claims must have 3+ independent sources (from at least 2 different agents)
- Flag any single-source information prominently
- Prioritize recent sources over older ones for current-state claims
- Identify potential biases (vendor docs vs independent analysis)

**Output:** Verified fact base with confidence levels per claim.

---

## Phase 4.5: OUTLINE REFINEMENT - Dynamic Evolution

**Objective:** Adapt research direction based on evidence discovered.

**When to Execute:** Standard/Deep/UltraDeep modes only, after Phase 4.

**Activities:**

1. **Compare scope vs findings:**
   - Did evidence reveal more important angles than initially scoped?
   - Are there unexpected patterns or contradictions?
   - Did any sub-question prove much richer or emptier than expected?

2. **Evaluate adaptation need:**
   - Major findings contradict initial assumptions -> adapt
   - Critical subtopic emerged that wasn't planned -> add section
   - Original question was too broad/narrow -> adjust scope
   - Evidence aligns with plan, no surprises -> keep structure

3. **Refine outline if needed:**
   - Add sections for unexpected but important findings
   - Demote/remove sections with insufficient evidence
   - Reorder by evidence strength and importance

4. **Targeted gap filling (if major gaps found):**
   - Launch 1-2 targeted agents (narrow brief, 3-5 tool calls each)
   - Time-box: do not restart full Phase 3

**Output:** Refined outline reflecting the actual evidence landscape.

---

## Phase 5: SYNTHESIZE - Deep Analysis

**Objective:** Connect insights and generate novel understanding.

**Activities:**
1. Identify patterns ACROSS agent reports (not visible to any single agent)
2. Map relationships between concepts from different sub-questions
3. Generate insights beyond source material (second-order implications)
4. Create conceptual frameworks that organize the findings
5. Build argument structures with evidence hierarchies
6. Write inline citations [N] for every factual claim

**This is where the lead's value appears.** Individual agents found facts. The lead connects them into understanding that no single agent could produce - because they each only saw their slice.

**Output:** Synthesized understanding with insight generation and full citation trail.

---

## Phase 6: CRITIQUE - Quality Assurance

**Objective:** Rigorously evaluate research quality.

**Activities:**
1. Review for logical consistency across the full analysis
2. Check citation completeness (every factual claim cited?)
3. Identify remaining gaps or weaknesses
4. Assess balance and objectivity
5. Verify claims against the source reports
6. Test alternative interpretations

**Red Team Questions:**
- What's missing that a domain expert would notice?
- What could be wrong? What alternative explanations exist?
- Which claims rest on single-source evidence?
- What biases might be present (vendor, geographic, recency)?
- What counterfactuals should be considered?

**Persona-Based Critique (Deep/UltraDeep only):**
- "Skeptical Practitioner" - Would someone doing this daily trust these findings?
- "Adversarial Reviewer" - What would a peer reviewer reject?
- "Implementation Engineer" - Can these recommendations be executed?

**Critical Gap Loop-Back:**
If critique identifies a critical knowledge gap (not just a writing issue), spawn 1-2 targeted agents with narrow briefs before proceeding to Phase 7. Time-box to 3-5 tool calls per agent.

**Output:** Critique report with improvement recommendations.

---

## Phase 7: REFINE - Iterative Improvement

**Objective:** Address gaps and strengthen weak areas.

**Activities:**
1. Conduct additional targeted research for critical gaps (via Agent tool)
2. Strengthen weak arguments with additional evidence
3. Add missing perspectives
4. Resolve contradictions (with source citations for resolution)
5. Enhance clarity of complex arguments
6. Verify revised content against sources

**Output:** Strengthened research with addressed deficiencies.

---

## Phase 8: PACKAGE - Report Generation

**Objective:** Deliver professional, actionable research.

**Activities:**
1. Structure report with clear hierarchy. Findings go as `### Finding N` subsections under one `## Main Analysis` heading - never as top-level `## Finding N` (the validator requires a literal Main Analysis section).
2. Write executive summary (200-400 words)
3. Develop detailed sections with inline citations
4. Create visualizations (tables, comparison matrices, diagrams)
5. Compile full bibliography (COMPLETE - every source from every agent), each entry `[N] Author/Org (Year). "Title". Publisher. URL` - never a bare URL
6. Add methodology appendix (document agent count, decomposition, gaps)

**Load [report-assembly.md](./report-assembly.md) for progressive generation instructions.**

**Output:** Complete research report.

---

## Mode-Specific Behavior

### Quick Mode
- Phases 2.5, 3, 3.5 are SKIPPED entirely - no fan-out orchestration
- Lead searches directly: 5-10 WebSearch + WebFetch calls (like a focused single-context researcher)
- Optionally spawn 1 verification agent for a second perspective
- Skip Phases 4.5, 6, 7
- Target: 10+ sources, 2-5 minutes
- This is the ONLY mode where the lead calls WebSearch/WebFetch

### Standard Mode (DEFAULT)
- 3-5 agents, lead never searches
- Full Phase 1-5 + **Phase 6-Lite** + 8
- Skip the full Phase 6 persona panel and Phase 7 refine loop
- Target: 25+ sources, 5-10 minutes

**Phase 6-Lite (Standard-mode critique gate, mandatory):** A single self-critique pass by the lead before packaging - no persona panel, no automatic agent fan-out. Run this checklist and fix in place:
1. **Decision-axis coverage:** Does the report cover the named option AND its principal alternatives AND the dominant trade-off axis (per Phase 2.5 rule 5)? If an axis is missing, spawn ONE narrow follow-up agent (time-box 3-5 tool calls) to fill it.
2. **Weak-claim containment:** Scan for any claim flagged weak/single-source/unverified. Each must be repaired with one targeted search or demoted to Limitations - never left inside Recommendations (see quality-gates.md).
3. **Primary-tier check:** Every quantitative/definitional claim cites a primary artifact, not a secondary summary. Re-source the worst offenders.
This gate is what separates a broad-but-soft Standard report from a defensible one; do not skip it.

### Deep Mode
- 5-8 agents, lead never searches
- Full Phase 1-8
- Mandatory follow-up round in Phase 3.5
- Target: 50+ sources, 10-20 minutes

### UltraDeep Mode
- 8-15 agents, lead never searches
- Full Phase 1-8
- Mandatory follow-up round in Phase 3.5
- Persona-based critique in Phase 6
- Target: 80+ sources, 20-45 minutes
