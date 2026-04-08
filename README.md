<h1 align="center">AutoWiki</h1>

<p align="center">
  <strong>Your LLM Compiles a Knowledge Base. You Just Read It.</strong><br>
  <sub>Implementing <a href="https://x.com/karpathy/status/1911101737498091651">Karpathy's LLM Knowledge Base</a> vision — raw sources in, Obsidian wiki out.</sub><br>
  <sub>By <a href="https://github.com/AlphaLab-USTC">AlphaLab-USTC</a></sub>
</p>

<p align="center">
  📺 <strong><a href="https://zy20031230.github.io/AutoWiki-skill/presentation.html">Live Demo → Design Philosophy Presentation</a></strong>
</p>

<p align="center">
  <a href="https://zy20031230.github.io/AutoWiki-skill/presentation.html"><img src="https://img.shields.io/badge/Demo-Live_Presentation-e8b04a?style=for-the-badge" alt="Demo"></a>
  <a href="#-quick-start"><img src="https://img.shields.io/badge/Quick_Start-5_min-blue?style=for-the-badge" alt="Quick Start"></a>
  <a href="#-how-it-works"><img src="https://img.shields.io/badge/How_It_Works-Architecture-green?style=for-the-badge" alt="Architecture"></a>
  <a href="#-the-karpathy-pattern"><img src="https://img.shields.io/badge/Karpathy-LLM_Wiki-ff69b4?style=for-the-badge" alt="Karpathy Pattern"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-≥3.12-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/LLM-Claude_Code-blueviolet?logo=anthropic&logoColor=white" alt="Claude Code">
  <img src="https://img.shields.io/badge/IDE-Obsidian-7c3aed?logo=obsidian&logoColor=white" alt="Obsidian">
  <img src="https://img.shields.io/badge/format-Markdown_+_Wikilinks-orange" alt="Markdown">
  <img src="https://img.shields.io/badge/domain-Knowledge_Base-brightgreen" alt="Knowledge Base">
</p>

---

## The Problem

You consume dozens of sources a week — papers, articles, reports, threads. You take notes, highlight key results, maybe file them into folders. But six months later, you can't remember how Source A's method relates to Source B's limitation. You re-derive context every time you revisit a topic. **Your reading never compounds.**

Most tools make this worse, not better. RAG systems re-discover knowledge from scratch on every query. Note-taking apps give you a graveyard of disconnected files. Summarizers produce shallow bullet points that miss what actually matters.

## The Solution

AutoWiki is a **Claude Code skill** that turns raw sources into a living, interconnected wiki. The first fully developed domain is **academic papers** — drop a PDF, get a deep analysis page woven into your knowledge graph:

1. **Drop** — Add PDFs to `raw/new/`
2. **Compile** — The LLM reads the paper, extracts factors from the author's Introduction, positions it in the field's timeline, writes critical analysis, and links it into the wiki
3. **Browse** — Open Obsidian. The wiki is already updated — summaries, cross-references, topic pages, evolutionary chains, all maintained automatically

**You browse it in Obsidian. The LLM writes and maintains everything. Your knowledge compounds.**

---

## What Makes AutoWiki Different

<table>
<tr>
<td width="50%">

### 🧠 Cognitive Depth, Not Shallow Summaries

The LLM doesn't just summarize — it **analyzes**. CRGP factors (Context, Related Work, Gap, Proposal) are extracted from the author's own Introduction. Critical Analysis follows a contrastive structure: Novel Insight states what we didn't know before (with `prior` / `update`), Fundamental Limitations target the *approach* (not "tested on too few datasets"), Research Frontier specifies concrete next steps with prerequisites. Built-in anti-patterns prevent the agent from producing generic filler.

</td>
<td width="50%">

### 🔗 Temporal Knowledge Graphs

Every source is positioned in the field's timeline. The agent identifies direct predecessors, evolutionary chains, cross-domain origins, and temporal tensions (where new findings contradict earlier work). Topics with ≥3 integrated sources auto-generate **Chronological Evolution** sections — showing how the field developed, phase by phase, with named evolutionary chains linking individual contributions.

</td>
</tr>
<tr>
<td width="50%">

### 🏠 Self-Maintaining Wiki

The wiki doesn't just grow — it **heals itself**. Proactive Write-back operates on three tiers: **Silent** (fix broken links automatically), **Notify** (record new insights, tell you), **Confirm** (structural changes, wait for approval). 25+ lint checks continuously catch hierarchy violations, missing cross-references, stale data, and orphan pages. The more you use it, the more consistent it gets.

</td>
<td width="50%">

### 🎯 Classification That Thinks

Before assigning any source to a topic, the agent runs a **3-question fitness check**: Does the source's core question match the topic's definition? Would a reader expect to find it here? Is the connection direct or just a shared keyword? Milestone hierarchy manages scale with consolidation (< 5 sources = inline subtopics) and promotion (≥ 5 = split to own file). No misorganization.

</td>
</tr>
</table>

---

## 💎 The Karpathy Pattern

AutoWiki implements [Andrej Karpathy's LLM Knowledge Base](https://x.com/karpathy/status/1911101737498091651) concept:

> *"Using LLMs to build personal knowledge bases... a large fraction of my recent token throughput is going less into manipulating code, and more into manipulating knowledge (stored as markdown and images)."*

| Karpathy's Vision | AutoWiki's Implementation |
|---|---|
| *"Index source documents into directory"* | `raw/` — source documents (PDFs, articles, clippings) with extracted assets |
| *"LLM incrementally compiles a wiki (.md files)"* | `kb/` — structured analysis, critical synthesis, temporal positioning, all in markdown |
| *"Backlinks, categorizes into concepts, writes articles, links them"* | Three-level index + `[[wikilinks]]` + topic aggregation with milestone hierarchy |
| *"Use Obsidian as the IDE frontend"* | Entire project root is an Obsidian vault |
| *"LLM writes and maintains all the data, I rarely touch it"* | Agent owns `kb/` — proactive write-back keeps everything consistent |
| *"Ask complex questions against the wiki"* | Query: index.md → relevant pages → synthesize → optional write-back |
| *"Explorations and queries always add up"* | Every query can produce journal entries, updated cross-references, resolved open questions |
| *"LLM health checks over the wiki"* | 25+ lint checks: hierarchy, temporal consistency, broken links, orphan pages |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** with [PyMuPDF](https://pymupdf.readthedocs.io/) (`pip install PyMuPDF`)
- **[Claude Code](https://docs.anthropic.com/en/docs/claude-code)** (the LLM agent that maintains the wiki)
- **[Obsidian](https://obsidian.md/)** (your reading interface)

### Setup

```bash
# 1. Install the skill
git clone https://github.com/zhangyi/autowiki-skill.git
# Register as a Claude Code plugin (see .claude-plugin/)

# 2. Initialize wiki structure (in your project directory)
mkdir -p raw/new raw/compiled kb/{sources,topics,journal,_templates} output

# 3. Copy templates
cp autowiki-skill/skills/autowiki/references/source-template/paper.md kb/_templates/
cp autowiki-skill/skills/autowiki/references/topic-template.md kb/_templates/
cp autowiki-skill/skills/autowiki/references/journal-template.md kb/_templates/

# 4. Create entry-point files
touch kb/index.md kb/log.md

# 5. Open in Obsidian
# Point Obsidian at your project root as a vault
```

### Daily Workflow (Paper Domain)

```bash
# Add a paper
# Drop a PDF into raw/new/, then in Claude Code:
> "Ingest the paper in raw/new/"

# The agent will:
#   1. Read the PDF, extract CRGP factors, position temporally
#   2. Report key findings to you for discussion
#   3. Extract figures, move PDF to raw/compiled/
#   4. Write source page, update index, topics, journal

# Ask questions
> "How does adversarial training compare across the safety papers?"
> "What are the open problems in jailbreak evaluation?"

# Health check
> "Lint the wiki"
```

---

## 🏗 How It Works

```
    ┌──────────────────────────────────────────────┐
    │              Obsidian Vault                    │
    │            (Your Reading UI)                   │
    └──────┬──────────────┬───────────────┬─────────┘
           │              │               │
     ┌─────▼────┐  ┌──────▼──────┐  ┌────▼─────┐
     │  kb/      │  │  kb/topics/ │  │  kb/      │
     │  sources/ │  │  (milestone │  │  journal/ │
     │           │  │   nodes)    │  │           │
     └─────▲────┘  └──────▲──────┘  └────▲─────┘
           │              │               │
    ┌──────┴──────────────┴───────────────┴─────────┐
    │              LLM (Claude Code)                  │
    │   Reads Source → Extracts Factors → Positions     │
    │   Temporally → Links → Writes → Self-Lints      │
    └──────────────────────▲────────────────────────┘
                           │
                    ┌──────┴──────┐
                    │   raw/new/   │
                    │ (Your Sources)│
                    └─────────────┘
```

### Two Decoupled Layers

| Layer | What It Does | How |
|-------|-------------|-----|
| **Raw Archive** (`raw/`) | Stores source documents + extracted assets | Human drops sources into `raw/new/`; agent moves to `raw/compiled/` after ingest |
| **Knowledge Base** (`kb/`) | Structured wiki compiled from sources | LLM reads sources → writes `kb/` directly via Claude Code tools (zero Python write code) |

The two layers are fully decoupled. You can re-compile the wiki from raw sources at any time. The raw archive is immutable — the agent never deletes or modifies source documents.

---

## 📁 Directory Structure

```
project-root/                    # Also your Obsidian vault
├── raw/
│   ├── new/                     # 📥 Drop sources here for ingest
│   └── compiled/                # 📦 Processed sources + extracted assets
│       └── <topic-slug>/
│           ├── paper.pdf
│           └── paper_figures/
│               ├── fig_*.png
│               └── figures_manifest.json
│
├── kb/                          # 🤖 Agent's domain — fully LLM-maintained
│   ├── index.md                 # Milestone tree — navigation entry point
│   ├── log.md                   # Chronological operation record
│   ├── sources/                 # Source pages, grouped by milestone topic
│   │   └── <topic-slug>/
│   │       └── paper-name.md
│   ├── topics/                  # Milestone nodes — conceptual breakthroughs
│   │   └── topic-name.md
│   ├── journal/                 # Cognitive change timeline + audit trail
│   │   └── YYYY-MM.md
│   └── _templates/              # Page templates (reference only)
│
└── skills/
    └── autowiki/
        ├── SKILL.md             # The skill definition (the brain)
        ├── references/          # Templates and reference files
        └── scripts/             # Figure extraction tooling
```

### Ownership Model

| Zone | Agent | Human |
|------|-------|-------|
| `kb/**` | Creates, updates, maintains | Read-only (browse in Obsidian) |
| `raw/new/` | Reads, then moves sources out | Drops sources here |
| `raw/compiled/` | Writes (moved sources + assets) | Read-only archive |
| `kb/journal/` | Appends entries | Read-only (your intellectual history) |

---

## 🔍 Agent Interaction

AutoWiki's agent doesn't just compile — it **interacts**:

### Real-Time Write-Back

| When You... | The Agent... |
|---|---|
| Drop a source in `raw/new/` | Runs 4-phase ingest: analyze → report → move files → write wiki |
| Ask a question about the wiki | Searches index → reads pages → synthesizes → writes back new insights |
| Express a new insight in conversation | Records it as a Cognitive Shift on the relevant source page + journal |
| Discover a connection between sources | Updates Relations sections, topic pages, and cross-references |
| Say "this contradicts Source X" | Flags the temporal tension, updates both source pages |

### Three Operations

| Operation | What It Does |
|---|---|
| **Ingest** | 4-phase pipeline: Analyze (read source, position temporally, assign milestone) → Report (3-sentence lead + critical analysis) → Finalize raw/ (extract assets, move source) → Write wiki (source page, index, topics, journal) |
| **Query** | Read index → find relevant pages → synthesize answer → optionally write back new insights to wiki + journal |
| **Lint** | 25+ checks across hierarchy, temporal, and raw/ consistency → auto-fix silent issues, escalate semantic conflicts |

---

## 📖 Why This Architecture?

**Why Markdown, not a database?**
LLMs work natively with text files. No ORM, no schema migrations, no query language. `grep` is the only search tool needed at personal KB scale. And Obsidian renders it beautifully — graph view, backlinks, Properties UI, all for free.

**Why Claude Code as the compiler?**
The knowledge base layer has **zero Python write code**. The LLM uses Claude Code's built-in `Write`, `Edit`, `Grep`, and `Glob` tools to directly manipulate markdown files. This means the "compiler" is the LLM itself — it can adapt its analysis, tagging, and linking strategies without code changes.

**Why not RAG?**
At the scale of a personal knowledge base (~100s of sources, ~dozens of topic pages), a well-maintained index file + grep outperforms vector search. The LLM auto-maintains these indexes, so retrieval stays fast without embedding pipelines. This matches Karpathy's experience: *"I thought I had to reach for fancy RAG, but the LLM has been pretty good about auto-maintaining index files."*

**Why a skill, not a standalone app?**
The skill definition (`SKILL.md`) IS the architecture — 343 lines encoding domain knowledge, quality standards, anti-patterns, and workflow rules. Any Claude Code user can install it and immediately have a sophisticated knowledge base workflow. No infrastructure to deploy, no servers to run.

---

## 🧰 Tech Stack

| Component | Technology |
|---|---|
| LLM agent | [Claude Code](https://docs.anthropic.com/en/docs/claude-code) |
| Reading UI | [Obsidian](https://obsidian.md/) |
| Knowledge base format | Markdown + YAML frontmatter + `[[wikilinks]]` |
| Figure extraction | [PyMuPDF](https://pymupdf.readthedocs.io/) (`fitz`) |
| Skill framework | Claude Code Skills ([`.claude-plugin`](https://docs.anthropic.com/en/docs/claude-code/skills)) |

---

## 🗺 What's Built

- ✅ LLM-compiled wiki with three-level indexing
- ✅ CRGP factors + Critical Analysis with anti-patterns and test criteria
- ✅ Temporal positioning and evolutionary chains
- ✅ Proactive write-back with three-tier autonomy (Silent / Notify / Confirm)
- ✅ 25+ lint checks (hierarchy, temporal, raw/ consistency)
- ✅ Figure extraction pipeline with manifest
- ✅ Classification Fitness Check + milestone hierarchy (consolidation / promotion)
- ✅ Claude Code plugin packaging

The **paper domain** is fully developed — CRGP factor extraction, figure analysis, temporal evolutionary chains. The architecture is domain-agnostic: the same ingest → compile → lint pipeline, milestone hierarchy, and write-back system can power any knowledge domain where reading compounds.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**AutoWiki** — *Your LLM compiles a wiki. Your knowledge compounds.*

<sub>Inspired by <a href="https://x.com/karpathy/status/1911101737498091651">Karpathy's LLM Knowledge Base</a> pattern</sub>

</div>
