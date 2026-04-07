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

- `domain` field renamed to `tags` — Obsidian renders tags natively with colors and filtering
- `aliases` field added — Obsidian uses this for search, link auto-complete, and graph display
- `created` / `last_updated` — Obsidian renders as date picker in Properties UI

## Architecture

```
raw/                → Immutable source documents (you read, never modify)
  ├── new/          → Uncompiled sources awaiting ingest
  └── compiled/     → Compiled sources, mirrors kb/sources/ milestone structure
kb/                 → Wiki (you own entirely — create, update, maintain)
output/             → Human-readable views (generate on demand)
```

## Wiki Structure

```
kb/
├── sources/              # Literature tree — sources grouped by milestone
│   ├── <milestone-slug>/ # One subdirectory per milestone topic
│   │   ├── <source>.md   # Source pages live under their parent milestone
│   │   └── ...
│   └── ...
├── topics/               # Milestone nodes — conceptual breakthroughs that cluster sources
├── journal/              # Human cognitive change timeline
├── _templates/           # Page templates (reference, do not modify)
├── index.md              # Your navigation entry point
└── log.md                # Chronological operation record
```

Source files are organized under `sources/<milestone-slug>/` subdirectories. The directory name is the bare slug extracted from the source's `milestone:` YAML value (strip `[[` and `]]`). When creating a new source, place it in the corresponding milestone directory (create the directory if needed). Obsidian resolves `[[wikilinks]]` by filename alone, so directory depth does not affect links.

### Truth Hierarchy (reference upward, never restate)

```
sources/ (leaves) → topics/ (milestone nodes) → journal/
```

- **Sources** are atomic fact pages — each declares a `milestone:` parent in YAML
- **Topics** are milestone nodes — each represents a conceptual breakthrough and owns a cluster of sources via `## Source Cluster`
- **Bidirectional linking**: source → milestone via `## Feeds`; milestone → source via `## Source Cluster`. Obsidian backlinks show the reverse automatically.
- Higher layers reference lower layer page IDs. Never copy content between layers. Updates happen at the source, then cascade up.

## Page Formats

All pages use structured markdown: YAML frontmatter + fixed section headings. See `references/` directory for exact template formats:
- `references/source-template.md` — Source page template
- `references/topic-template.md` — Milestone topic template
- `references/journal-template.md` — Journal entry template

### Relation Types

| Type | Meaning |
|------|---------|
| `builds_on` | Extends, improves, inherits |
| `contradicts` | Challenges, conflicts with |
| `applies` | Applies to new domain/scenario |
| `related` | Connected but relationship unclear |

## Operations

### Ingest (new source added to raw/)

When the human adds a new source, think through this checklist:

**Compare first, then derive contribution:**

1. **What do we already know?** — Scan index.md → read related wiki pages → understand our existing knowledge in this area
2. **What does the field already have?** — Read the paper's related work / baselines → understand the scope's prior art
3. **What is specifically new?** — From the two comparisons above, derive the core contribution (not stated independently — DERIVED from comparison)
4. **For each related wiki page** — Is this builds_on, contradicts, or applies? What's the delta?
5. **Assign milestone** — Does this source belong to an existing milestone? If it opens a new direction → create new milestone topic. Set `milestone:` in source YAML.
6. **New topic needed?** — New important entity/concept appeared that deserves its own milestone?
7. **Human cognitive insights?** — Anything the human said worth recording?
8. **Proactive observations?** — Did this ingest trigger any cross-source synthesis or resolve any Open Questions on existing topics? If yes, dual-write per Proactive Write-back rules.

**Report to human before compiling:**

1. Three-sentence lead: scope, method, insight
2. Positioning: state which domain/category this paper belongs to, and where it sits relative to the field's prior art (baselines, related work from the paper itself). Use wiki knowledge internally to sharpen positioning, but do NOT enumerate wiki page statuses in the report.
3. Contribution: derived from the delta between what the field already has and what this paper adds — never stated independently
4. Key insights, strengths & weaknesses

Wiki relation management (which pages to create, update, link) is your responsibility — do NOT report proposed relations to the human.

Then write:
- **Always create**: New source page (essence + relations + feeds + cognitive shifts)
- **Always update**: index.md, log.md
- **As needed**: Related milestone topics (Source Cluster, Key Properties, Arrival/Departure)
- **As needed**: New milestone topics (if new conceptual breakthrough emerged)
- **As needed**: Journal entry (if cognitive shifts occurred)

After compile, move the raw file from `raw/new/` to `raw/compiled/<milestone-slug>/`.

Strategy: **Immediate cascading update** — wiki must be fully consistent after every ingest.

### Query (human asks a question)

1. Read index.md → find relevant pages
2. Read relevant pages, synthesize answer
3. Did the answer produce new value? Apply the Proactive Write-back decision boundary:
   - New cross-source relation → dual-write (Notify tier)
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
- Hollow milestones (topic with empty Source Cluster)

When structural issues are detected during any operation (not only explicit lint):
- Silent-tier issues → fix immediately, journal entry only
- If a fix would change semantic content (e.g., resolving a contradiction) → escalate to Confirm tier

## Proactive Write-back

The agent autonomously writes to the wiki when valuable observations arise — not only when explicitly instructed. Every proactive write follows the **dual-write rule**: update the relevant page in-place AND append an atomic audit entry in `journal/`.

### Autonomy Tiers

| Tier | Scope | Agent behavior |
|------|-------|---------------|
| **Silent** | Structural fixes: broken wikilinks, Feeds↔Cluster sync, missing cross-references, index.md sync | Fix immediately, log in journal. No terminal notification. |
| **Notify** | New observations: cognitive shifts, cross-source synthesis, open-question resolution, new relations discovered | Write to wiki + journal, then print one-line summary to terminal. |
| **Confirm** | Structural changes: new milestone topic, milestone reassignment, delete/merge pages, contradiction resolution | Describe proposed change in terminal, wait for human approval before writing. |

### Trigger → Action Table

| Trigger | Detection | In-place target | Journal entry type |
|---------|-----------|-----------------|-------------------|
| **Conversation insight** | During discussion, a new understanding/analogy/contradiction emerges that is not from any paper but from the dialogue itself | Source `## Cognitive Shifts` or Topic `## Open Questions` | `insight` |
| **Cross-source synthesis** | While answering a query or during ingest, discover an unrecorded relation or tension between existing sources | Source `## Relations` + Topic `## Departure` or `## Source Cluster > Mentioned` | `synthesis` |
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
mkdir -p raw/new raw/compiled kb/{sources,topics,journal,_templates} output
```

Then copy the three template files from `references/` into `kb/_templates/`:
- `source.md`, `topic.md`, `journal.md`

Create `kb/index.md` as the navigation entry point, and `kb/log.md` for the chronological operation record.
