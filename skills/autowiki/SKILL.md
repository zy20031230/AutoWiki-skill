---
name: autowiki
description: "Use when maintaining an LLM-driven knowledge base wiki, ingesting research papers/sources, querying wiki knowledge, or running wiki lint checks. Activates for: paper ingest, wiki query, wiki maintenance, knowledge compilation, source clustering, or any task involving structured Obsidian-based knowledge management."
---

# AutoWiki — LLM-Maintained Knowledge Base

You are the sole maintainer of this wiki. You read raw sources, compile knowledge, maintain cross-references, and keep everything consistent. The human curates sources, directs analysis, and provides cognitive insights.

## IDE

The human reads and edits the wiki in **Obsidian**. All wiki pages must be valid Obsidian-compatible markdown.

### Wikilink Rules

| Location | Format | Why |
|----------|--------|-----|
| Body text, table cells, bullet items | `[[slug]]` | Obsidian renders clickable links |
| YAML `milestone` field | `"[[slug]]"` (quoted) | Obsidian Properties UI renders as clickable link; must quote to avoid YAML parse error |
| Other YAML values | bare slug | Obsidian does not parse most YAML values as links |
| Fenced code blocks | exempt | literal text |

Use `[[slug]]` wherever a human might want to click through. Obsidian's backlinks panel automatically surfaces reverse links.

### Properties Conventions

- `domain` field renamed to `tags` — Obsidian renders tags natively with colors and filtering. Every source MUST include:
  - A `year/YYYY-MM` tag reflecting the paper's publication date (arXiv submission, conference, or journal). Extract from the PDF first page, arXiv metadata, or URL. Example: `year/2025-03`.
  - A `venue/<name>` tag for the publishing venue (journal or conference). Use short canonical names: `venue/NeurIPS`, `venue/ICML`, `venue/CVPR`, `venue/Nature`, `venue/AAAI`, `venue/ACL`, etc. For preprints not yet accepted, use `venue/arXiv-preprint`. Extract from the PDF header, arXiv metadata, or paper URL.
- `authors` field added — list of paper authors for attribution and filtering
- `aliases` field added — Obsidian uses this for search, link auto-complete, and graph display
- `created` / `last_updated` — Obsidian renders as date picker in Properties UI
- `raw_path` — points to the **final** local location in `raw/compiled/` (set during Phase 4 of ingest, after PDF is moved from `raw/new/`)
- `url` — permanent external URL (arXiv abstract, conference page, or DOI link). Always set alongside `raw_path` so both local archive and web reference are preserved

## Architecture

```
raw/                → Write-once source archive (human adds to new/; agent moves to compiled/ during ingest)
  ├── new/          → Uncompiled sources awaiting ingest (human drops files here)
  └── compiled/     → Ingested sources, organized by topic path (agent writes here, never deletes)
      └── <topic-path>/                 → Mirrors topic's directory path (may be nested, e.g., a/b/c/)
          ├── <source>.pdf              → Original PDF (moved from new/ after milestone assignment)
          └── <source-slug>_figures/    → Extracted figures (teaser, main, extra)
kb/                 → Wiki (you own entirely — create, update, maintain)
output/             → Human-readable views (generate on demand)
```

### Three-Tree Mirroring Invariant

Three directory trees MUST maintain identical structure at all times:

| Tree | Root | Purpose |
|------|------|---------|
| `topics/` | `kb/topics/` | Milestone definition files |
| `sources/` | `kb/sources/` | Source (paper) pages |
| `raw/compiled/` | `raw/compiled/` | PDFs + extracted figures |

**Rule**: For any topic at path `topics/<path>/<slug>.md`, the corresponding source directory is `sources/<path>/<slug>/` and the raw directory is `raw/compiled/<path>/<slug>/`. The `<path>` includes all ancestor directories (e.g., `agent-self-evolution/memory-evolution/`).

**Corollary**: Moving a topic file to a new directory requires moving both the corresponding source directory and raw/compiled directory, AND updating `raw_path` in all affected source files.

Example:

| Topic file | Source dir | Raw dir |
|---|---|---|
| `topics/foo.md` | `sources/foo/` | `raw/compiled/foo/` |
| `topics/foo/bar/baz.md` | `sources/foo/bar/baz/` | `raw/compiled/foo/bar/baz/` |

## Wiki Structure

```
kb/
├── sources/              # Literature tree — sources grouped by milestone
│   ├── <topic-path>/     # Subdirectories mirroring topic tree (may be nested)
│   │   ├── <source>.md   # Source pages live under their parent milestone
│   │   └── ...
│   └── ...
├── topics/               # Milestone nodes — conceptual breakthroughs that cluster sources
├── journal/              # Human cognitive change timeline
├── index.md              # Milestone tree — navigation entry point (no source listing)
└── log.md                # Chronological operation record
```

Source files are organized under `sources/<topic-path>/` subdirectories, where `<topic-path>` mirrors the topic file's directory path relative to `topics/` (may be nested, e.g., `agent-self-evolution/memory-evolution/self-evolving-memory-architectures/`). When creating a new source, place it in the directory matching the topic file that the source's `milestone:` YAML references (create the directory if needed). Extracted figures live in `raw/compiled/<topic-path>/<source-slug>_figures/` alongside the source PDF. Obsidian resolves `[[wikilinks]]` by filename alone, so directory depth does not affect links.

### Truth Hierarchy (reference upward, never restate)

```
sources/ → topics/ (standalone | merged parent | split parent + leaves) → journal/
```

- **Sources** are atomic fact pages — each declares a `milestone:` parent in YAML pointing to an existing topic file.
- **Standalone topics** own sources directly via `## Source Cluster` and represent specific conceptual breakthroughs.
- **Merged parent topics** (`subtopics: [...]` in YAML) contain inline H3 subtopic sections when total papers < 5. Sources point their `milestone:` to the parent file. The parent owns `## Source Cluster` directly.
- **Split parent topics** (`children: [...]` in YAML) aggregate child milestones that have their own files (when a subtopic grows to ≥ 5 papers). Sources point to the child leaf file.
- **Bidirectional linking**: source → topic via `## Feeds`; topic → source via `## Source Cluster`; child → parent via `parent_milestone` YAML; parent → children via `children` YAML. Obsidian backlinks show all reverse links automatically.
- Higher layers reference lower layer page IDs. Never copy content between layers.

### Milestone Hierarchy

Milestones form a tree with three topic modes:

| Mode | YAML | Owns sources? | Subtopics |
|------|------|---------------|-----------|
| **Standalone** | `subtopics: [], children: []` | Yes, via `## Source Cluster` | None |
| **Merged parent** | `subtopics: [a, b, ...]` | Yes, unified `## Source Cluster` | Inline H3 sections |
| **Split parent** | `children: [a, b, ...]` | No, children own sources | Separate files |

**Invariants:**
- A source's `milestone:` field must reference an existing topic file (standalone, merged parent, or split-out leaf).
- Bidirectional: parent `children`/`subtopics` ↔ child `parent_milestone`.
- Maximum depth: 3 levels.
- Topic files: flat in `topics/` by default. When a parent has split-out children, child files go to `topics/<parent-slug>/`; parent stays at `topics/<parent-slug>.md`.
- Source directories: `sources/<topic-path>/` where `<topic-path>` mirrors the topic file's directory path relative to `topics/`.
- **Three-tree mirroring**: `topics/`, `sources/`, `raw/compiled/` directory trees must be structurally identical (see Architecture > Three-Tree Mirroring Invariant).
- Source page `raw_path` must use the full nested path: `raw/compiled/<topic-path>/<source-slug>.pdf`.

**Consolidation Rule (< 5 papers):**

When a parent milestone has **fewer than 5 total source papers** across all subtopics, the subtopics are **inline H3 sections** within the parent file (no separate leaf topic files). The parent uses `subtopics: [...]` in YAML.

Each inline subtopic section format:
```markdown
### <Subtopic Name>
> One-line milestone definition
- key property (source: [[<source-slug>]])
```

**Promotion Rule (≥ 5 papers):**

When a subtopic accumulates ≥ 5 papers, it splits out to its own file at `topics/<parent-slug>/<subtopic-slug>.md`. Move the subtopic from `subtopics` to `children` in parent YAML. The child file uses standalone/leaf mode. This is a Confirm-tier operation.

**Granularity Heuristic (topic source count):**

| Count | Action |
|-------|--------|
| > 8 | **Must split** — topic is too coarse; identify sub-clusters |
| 3–8 | **Judgment call** — split only if distinct conceptual sub-clusters exist |
| < 3 | **Don't split** — granularity is appropriate |

**Tag-to-Parent Promotion:** When 3+ standalone topics share a tag, consider creating a merged parent matching that tag name. If total papers < 5, use merged parent mode (inline subtopics). This is a Confirm-tier operation.

**Classification Fitness Check:**

Before assigning a source to an existing topic, verify:
1. Does the source's core research question fall within the topic's milestone definition?
2. Would the source's insights be expected by a reader browsing this topic?
3. Is the connection direct (same research question) or indirect (shared keyword but different focus)?

If the answer to (3) is "indirect" — the paper belongs elsewhere. Create a new topic rather than force-fitting. A small standalone topic (1–2 papers) is better than a polluted topic with misclassified papers. Shared keywords (e.g., "safety") do NOT imply shared research questions (e.g., "agent safety challenges" ≠ "LLM jailbreak methods").

## Page Formats

All pages use structured markdown: YAML frontmatter + fixed section headings. See `references/` directory for exact template formats:
- `references/source-template/paper.md` — Paper source page template (core wiki fields + CRGP factors + figure references + critical analysis)
- `references/topic-template.md` — Milestone topic template
- `references/journal-template.md` — Journal entry template

### Paper Template: Factors, Figures & Critical Analysis

The `paper.md` template adds three sections beyond the core source template:

**Factors:** Reflects ONLY what the authors claim in their Introduction — not our analysis. Four subsections:
- **Context**: Research background as stated by authors
- **Related Work**: Prior work grouped by methodology line, as cited by authors
- **Gap**: Specific limitations the authors identify
- **Proposal**: Proposed solution + key insight claimed by authors

**Figures:** The `paper_extract_figures.py` script detects figure captions from the PDF text layer, renders the page region around each figure (capturing vector graphics), and outputs a `figures_manifest.json` with caption text, page number, and image path. The agent reads the manifest (text only) to decide which figures are informative — no need to view every image. Selected figures get a one-line interpretation connecting them to the paper's contribution. Figure numbering does NOT imply a fixed role (e.g., Fig 1 is not always a teaser). Images are stored in `raw/compiled/<topic-path>/<source-slug>_figures/`.

**Critical Analysis:** Replaces the old Key Insights / Strengths & Weaknesses sections. Three subsections, each with contrastive requirements:
- **Novel Insight**: What we didn't know before — must reference prior wiki understanding and state what changes. Test: "Would a senior researcher cite this in their own paper's motivation?"
- **Fundamental Limitations**: Limitations of the *approach or research direction*, not the paper's experimental scope. Must identify root cause and cross-reference other affected work. Test: "Would solving this be a publishable contribution?" Anti-patterns: "only tested on X", "no comparison with Y".
- **Research Frontier**: Concrete next-step problems this paper makes tractable. Must specify prerequisites and closest existing attempts. Test: "Could someone write a paper abstract from this direction?" Anti-pattern: "test on more models/domains".

## Operations

### Ingest (new source added to raw/new)

When the human adds a new source, think through this checklist:

**Phase 1 — Analyze (read from `raw/new/`, decide milestone):**

1. **What do we already know?** — Scan index.md → read related wiki pages → understand our existing knowledge in this area
2. **Temporal positioning** — Identify this paper's position in the field's timeline:
   a. **Direct predecessors**: Which specific papers does this one build on, extend, or supersede? Check the paper's Related Work section + wiki's existing Relations sections.
   b. **Evolutionary chain**: Which named chain(s) does this paper belong to? Check topic page's Chronological Evolution if it exists. Classify as: new chain origin, intermediate node, terminal node, or chain-splitting fork.
   c. **Cross-domain origins**: Was the core method adapted from another field? Note source domain, original paper, and time gap.
   d. **Cross-topic impact**: Does this paper affect papers/topics outside its own milestone? (e.g., evaluation paper retroactively questions claims in an attack topic)
   e. **Temporal tensions**: Does this paper contradict earlier findings? Note the specific contradiction and affected papers.
3. **What does the field already have?** — Read the paper's related work / baselines → understand the scope's prior art
4. **What is specifically new?** — From the two comparisons above, derive the core contribution (not stated independently — DERIVED from comparison)
5. **For each related wiki page** — What's the delta between this paper and existing wiki knowledge? These deltas feed directly into Critical Analysis: Novel Insight uses them as `prior:` references, Fundamental Limitations cross-references shared problems via `also_affects:`, Research Frontier references closest existing attempts via `closest_attempt:`.
6. **Assign milestone** — First, apply the **Classification Fitness Check** (see Milestone Hierarchy section): does this source's core research question genuinely match an existing topic's milestone definition? A paper about general LLM jailbreaking does NOT fit an "agent safety" topic just because both involve "safety." If no existing topic is a genuine conceptual match → create a new standalone topic first (Confirm tier, but misclassification is worse than a small new topic). Only after confirming fit (or creating a new topic) set `milestone:` in source YAML.
7. **Granularity check** — After assignment, count the topic's total sources. If a merged parent's subtopic reaches ≥ 5 papers, flag for split-out (Confirm tier). If a standalone topic reaches > 8, flag for sub-clustering.
8. **New topic needed?** — New important entity/concept appeared that deserves its own milestone?
9. **Human cognitive insights?** — Anything the human said worth recording?
10. **Proactive observations?** — Did this ingest trigger any cross-source synthesis or resolve any Open Questions on existing topics? If yes, dual-write per Proactive Write-back rules.

**Phase 2 — Report to human before compiling:**

1. Three-sentence lead: scope, method, insight
2. Positioning: state which domain/category this paper belongs to, and where it sits relative to the field's prior art (baselines, related work from the paper itself). Use wiki knowledge internally to sharpen positioning, but do NOT enumerate wiki page statuses in the report.
3. Contribution: derived from the delta between what the field already has and what this paper adds — never stated independently
4. Critical analysis: novel insights (contrastive with wiki knowledge), fundamental limitations (of the approach/direction, not the paper), research frontier opened

Wiki page management (which pages to create, update, link) is your responsibility — do NOT report proposed page changes to the human.

**Phase 3 — Finalize raw/ (milestone is now known):**

Discover, extract figures, move PDF, and verify — all targeting `raw/compiled/<topic-path>/` (where `<topic-path>` mirrors the assigned topic's directory path, e.g., `agent-self-evolution/memory-evolution/self-evolving-memory-architectures/`):

```bash
# 1. Discover actual PDF path (handles flat or nested drops)
#    Expected: raw/new/<source>.pdf
#    Also handles: raw/new/<subdir>/<source>.pdf
find raw/new/ -name "*.pdf" -type f

# 2. Extract figures (if source is a PDF)
python scripts/paper_extract_figures.py <actual-pdf-path> \
    -o raw/compiled/<topic-path>/<source-slug>_figures

# 3. Move PDF from new/ to compiled/
mv <actual-pdf-path> raw/compiled/<topic-path>/<source-slug>.pdf

# 4. VERIFY: PDF must no longer exist under raw/new/
#    If this finds the file, the move failed — retry or report error.
! find raw/new/ -name "<source>*.pdf" -type f | grep -q .
```

**Hard gate:** Do NOT proceed to Phase 4 until the PDF is confirmed absent from `raw/new/`. If the move fails (wrong path, permission error), fix and retry. The `raw/new/` inbox must be empty of this source before writing wiki pages.

**Phase 4 — Write wiki pages:**

- **Always create**: New source page using `paper.md` template (essence + CRGP factors + figure references + critical analysis + feeds + cognitive shifts). Set `raw_path` to `raw/compiled/<topic-path>/<source-slug>.pdf` (full nested path).
- **Always update**: index.md, log.md
- **As needed**: Related milestone topics (Source Cluster, Key Properties, Arrival/Departure)
- **As needed**: New milestone topics (if new conceptual breakthrough emerged)
- **As needed**: Update topic's ## Chronological Evolution if:
  (a) topic now has ≥3 integrated sources and section doesn't exist yet, or
  (b) new paper changes the evolutionary chain structure (new node, new chain, or supersession)
- **As needed**: Journal entry (if cognitive shifts occurred)

Strategy: **Immediate cascading update** — wiki must be fully consistent after every ingest.

**End-of-ingest gate:** After all wiki writes, run a final sanity check:
```bash
# No PDFs for just-ingested source(s) should remain in raw/new/
find raw/new/ -name "*.pdf" -type f
```
If any ingested source's PDF is still found under `raw/new/` (at any depth), complete the move now before reporting success. An ingest is not done until `raw/new/` contains only un-ingested sources.

### Reorganize (topic hierarchy change)

When topics are moved, merged, split, or restructured:

**Checklist (all steps mandatory, in order):**

1. **Topic files**: Create/move/edit topic `.md` files. Update YAML (`parent_milestone`, `children`, `subtopics`).
2. **Source directories**: Move `sources/` directories to mirror new `topics/` tree.
3. **Raw directories**: Move `raw/compiled/` directories to mirror new tree.
4. **raw_path update**: Update `raw_path` in ALL affected source `.md` files.
5. **Index**: Rewrite `index.md` to reflect new hierarchy.
6. **Log + Journal**: Record the reorganization.
7. **Verify three-tree mirroring**:

```bash
# Trees must match (excluding _figures dirs)
diff <(find kb/sources/ -type d | sed 's|kb/sources/||' | sort) \
     <(find raw/compiled/ -type d ! -name "*_figures" | sed 's|raw/compiled/||' | sort)

# All raw_path references must resolve
grep -r "^raw_path:" kb/sources/ | while IFS=: read -r f v; do
  p=$(echo "$v" | sed 's/^raw_path: *//'); [ ! -f "$p" ] && echo "BROKEN: $f → $p"
done
```

This is a **Confirm-tier** operation — always requires user approval before execution.

### Query (human asks a question)

1. Read index.md → find relevant pages
2. Read relevant pages, synthesize answer
3. Did the answer produce new value? Apply the Proactive Write-back decision boundary:
   - New cross-source insight (novel connection, shared limitation, or research opportunity) → dual-write (Notify tier)
   - Cognitive shift from discussion → dual-write (Notify tier)
   - Open Question resolved → dual-write (Notify tier)
   - Pure factual answer with no new synthesis → don't write
4. If any writes occurred, print one-line summary to terminal.

### Lint (health check)

Periodically check for:
- Contradictions between pages
- Stale claims superseded by newer sources
- Orphan pages with no inbound links
- Missing pages (frequently referenced but nonexistent topics)
- Missing cross-references
- Orphan sources (no `milestone:` field)
- Feeds ↔ Source Cluster mismatch (source says `integrated` but milestone's Source Cluster doesn't list it, or vice versa)
- Broken `[[wikilinks]]` (link target has no corresponding page)
- Hollow milestones (leaf topic with empty Source Cluster)
- **Hierarchy consistency:**
  - Source `milestone:` references a non-existent topic file
  - Merged parent (`subtopics: [...]`) missing H3 sections for listed subtopics
  - Split parent (`children: [...]`) missing child files in `topics/<parent-slug>/`
  - Topic has both non-empty `subtopics` and `children` for the same slug (pick one mode per subtopic)
  - `parent_milestone` value in a child that doesn't match any existing topic
  - Hierarchy depth > 3 levels
  - Merged parent subtopic with ≥ 5 papers (should split out to own file)
  - Standalone topic source count > 8 (granularity violation — flag for split)
- **raw/ consistency:**
  - Orphan `_figures/` directory in `raw/compiled/` with no corresponding PDF (interrupted ingest)
  - PDF anywhere under `raw/new/` (including subdirectories) that has a corresponding source page in `kb/` (forgot to move) — use `find raw/new/ -name "*.pdf" -type f` to discover at any depth
  - Source page `raw_path` points to nonexistent file
  - `_figures/` directory referenced by source page but missing from `raw/compiled/`
  - Nested subdirectories inside `raw/new/` (human may have dropped a folder instead of flat files) — flatten or flag
  - `sources/` and `raw/compiled/` directory trees not mirrored (structural divergence) — run three-tree mirroring verification from Reorganize section
  - Source `raw_path` uses flat slug instead of full nested path (e.g., `raw/compiled/foo/` when it should be `raw/compiled/a/b/foo/`)
- **Temporal consistency:**
  - Source with ≥1 Relations entry but missing **Temporal context** paragraph at top of ## Relations section
  - Topic with ≥3 integrated sources but missing ## Chronological Evolution section
  - Temporal context references a [[source]] that doesn't exist as a wiki page (broken predecessor/successor link)
  - Evolutionary chain in Chronological Evolution lists a source not in the topic's Source Cluster (Integrated, Stubs, or Mentioned)
  - Cross-topic timeline references a source under the wrong topic (source's milestone doesn't match the topic cited in the timeline)

When structural issues are detected during any operation (not only explicit lint):
- Silent-tier issues → fix immediately, journal entry only
- If a fix would change semantic content (e.g., resolving a contradiction) → escalate to Confirm tier

## Proactive Write-back

The agent autonomously writes to the wiki when valuable observations arise — not only when explicitly instructed. Every proactive write follows the **dual-write rule**: update the relevant page in-place AND append an atomic audit entry in `journal/`.

### Autonomy Tiers

| Tier | Scope | Agent behavior |
|------|-------|---------------|
| **Silent** | Structural fixes: broken wikilinks, Feeds↔Cluster sync, missing cross-references, index.md sync | Fix immediately, log in journal. No terminal notification. |
| **Notify** | New observations: cognitive shifts, cross-source synthesis, open-question resolution | Write to wiki + journal, then print one-line summary to terminal. |
| **Confirm** | Structural changes: new milestone topic, milestone reassignment, delete/merge pages, contradiction resolution, **milestone split/merge, promote leaf to parent, tag-to-parent promotion** | Describe proposed change in terminal, wait for human approval before writing. |

### Trigger → Action Table

| Trigger | Detection | In-place target | Journal entry type |
|---------|-----------|-----------------|-------------------|
| **Conversation insight** | During discussion, a new understanding/analogy/contradiction emerges that is not from any paper but from the dialogue itself | Source `## Cognitive Shifts` or Topic `## Open Questions` | `insight` |
| **Cross-source synthesis** | While answering a query or during ingest, discover an unrecorded connection or tension between existing sources | Source `## Critical Analysis` (add to Novel Insight, Fundamental Limitations, or Research Frontier as appropriate) + Topic `## Departure` or `## Source Cluster > Mentioned` | `synthesis` |
| **Lint auto-fix** | Detected during any read operation (not only explicit lint command) | The broken page itself | `lint-fix` |
| **Open Question evolution** | New source partially/fully answers an existing Open Question on any topic | Topic `## Open Questions` (mark resolved/partially-resolved with source ref) | `oq-update` |

### Atomic Journal Entry Format

Each proactive write appends one entry to `journal/YYYY-MM.md`:

```
- [YYYY-MM-DD] <type> | <one-line summary>
  - trigger: <what triggered this>
  - pages_modified: [<page-slugs>]
  - detail: "<what was written and why>"
```

Types: `insight`, `synthesis`, `lint-fix`, `oq-update`.

### Decision Boundary: Write or Not?

Before writing, the agent applies this filter:
1. **Is it already recorded?** → Don't write (avoid duplication)
2. **Is it specific enough to be actionable?** → Vague feelings don't qualify; concrete observations do
3. **Would a future reader (human or agent) benefit from finding this?** → If yes, write

## Conventions

- Page filenames use kebab-case slugs: `attention-is-all-you-need.md`
- All dates use ISO format: `2026-04-06`
- Domain names use kebab-case: `nlp-architectures`
- Log entries: `## [YYYY-MM-DD] <operation> | <title>`
- Journal files: one per month `YYYY-MM.md`

## Bootstrapping a New Wiki

To initialize a fresh AutoWiki project, create this directory structure:

```bash
mkdir -p raw/new raw/compiled kb/{sources,topics,journal} output
```

Create `kb/index.md` as the navigation entry point, and `kb/log.md` for the chronological operation record.
