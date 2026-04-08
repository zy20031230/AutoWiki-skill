---
type: topic
id: <slug>
tags:
  - <domain>
parent_milestone: null
subtopics: []
children: []
created: <YYYY-MM-DD>
last_updated: <YYYY-MM-DD>
aliases:
  - <human-readable milestone name>
---

<!-- TEMPLATE MODES (pick ONE based on paper count and hierarchy):

     1. Standalone / Leaf milestone (subtopics: [], children: [])
        → include Key Properties + Source Cluster; omit Synthesis, subtopic H3s, Child Milestones

     2. Merged parent (subtopics: [a, b, ...], children: [])
        → When total papers < 5: subtopics are inline H3 sections in this file
        → include Synthesis + H3 subtopic sections + unified Source Cluster
        → omit Key Properties, Child Milestones

     3. Split parent (children: [a, b, ...], subtopics may coexist)
        → When a subtopic grows to ≥ 5 papers, it splits to its own file under topics/<parent-slug>/
        → include Child Milestones table + Synthesis; remaining inline subtopics stay as H3s
        → Child files use Standalone/Leaf mode

     All modes share: Arrival, Departure, Open Questions -->

> [!abstract] Milestone Definition
> One sentence: what conceptual breakthrough does this milestone represent?

## Arrival

(What prior work / earlier milestones led to this? Where was the field before this breakthrough?)

<!-- ── CONDITIONAL: include when topic has ≥3 integrated sources ── -->

## Chronological Evolution

<!-- Timeline of how this topic's research developed.
     Structure by temporal phases (2-4 phases typical).
     For each paper: [[source]] (YYYY-MM, venue): 1 sentence role.
     End with named evolutionary chains and optional cross-topic timeline.
     Skip this section for topics with <3 integrated sources. -->

**Phase N — <Phase Name> (YYYY-MM–YYYY-MM):**
- [[source]] (YYYY-MM, venue): <1 sentence role in this phase>

**Evolutionary chains:**
1. **<Chain name>:** source_a(date) → source_b(date) → source_c(date)

<!-- Optional: include when clear attack↔defense or capability↔safety co-evolution exists -->
**Cross-topic timeline:**

| Date | <Topic A> (→) | <Topic B> (←) |
|------|--------------|---------------|
| YYYY-MM | [[source]] event | [[source]] response |

<!-- ── STANDALONE / LEAF-ONLY sections ── -->

## Key Properties

- property (source: [[<source-slug>]])

## Source Cluster

### Integrated

| source | contribution to this milestone |
|--------|-------------------------------|
| [[<source-slug>]] | prose |

### Mentioned

- [[<source-slug>]]: brief note on relevance

<!-- ── MERGED PARENT sections (subtopics: [a, b, ...]) ── -->

## Synthesis

(Cross-subtopic patterns visible only at the aggregate level)

### <Subtopic Name>

> One-line milestone definition for this subtopic

- key property (source: [[<source-slug>]])

<!-- Repeat ### for each subtopic -->

## Source Cluster

<!-- Unified for all subtopics -->

### Integrated

| source | contribution to this milestone |
|--------|-------------------------------|
| [[<source-slug>]] | prose |

### Mentioned

- [[<source-slug>]]: brief note on relevance

<!-- ── SPLIT PARENT sections (children: [a, b, ...]) ── -->

## Child Milestones

| child | one-line definition | source count |
|-------|---------------------|--------------|
| [[<child-slug>]] | what this sub-milestone represents | N |

## Synthesis

(Cross-child patterns visible only at the aggregate level)

<!-- ── SHARED sections ── -->

## Departure

(What open questions did this milestone create? Which later milestones does it seed?)
- seeds: [[<later-milestone-slug>]]
- tension_with: [[<sibling-milestone-slug>]]

## Open Questions

- <question text>
- ~~<resolved question text>~~ → Resolved by [[source-slug]] ([YYYY-MM-DD])
