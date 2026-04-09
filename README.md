<h1 align="center">AutoWiki</h1>

<p align="center">
  <strong>Your LLM Compiles a Knowledge Base. You Just Read It.</strong><br>
  <sub>Implementing <a href="https://x.com/karpathy/status/1911101737498091651">Karpathy's LLM Knowledge Base</a> vision — raw sources in, Obsidian wiki out.</sub><br>
  <sub>By <a href="https://github.com/AlphaLab-USTC">AlphaLab-USTC</a></sub>
</p>

<p align="center">
  <a href="https://zy20031230.github.io/AutoWiki-skill/presentation.html"><img src="https://img.shields.io/badge/Demo-Live_Presentation-e8b04a?style=for-the-badge" alt="Demo"></a>
  <a href="#-quick-start"><img src="https://img.shields.io/badge/Quick_Start-3_steps-blue?style=for-the-badge" alt="Quick Start"></a>
  <a href="#-showcase-80-paper-wiki"><img src="https://img.shields.io/badge/Showcase-80_Papers-green?style=for-the-badge" alt="Showcase"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/LLM-Claude_Code-blueviolet?logo=anthropic&logoColor=white" alt="Claude Code">
  <img src="https://img.shields.io/badge/IDE-Obsidian-7c3aed?logo=obsidian&logoColor=white" alt="Obsidian">
  <img src="https://img.shields.io/badge/format-Markdown-orange" alt="Markdown">
</p>

---

## The Idea

You read papers, take notes, file them into folders. Six months later you can't remember how anything connects. **Your reading never compounds.**

AutoWiki fixes this. Drop a PDF → the LLM compiles a deep analysis page → woven into your knowledge graph → browse it in Obsidian. That's it.

```
1. Drop    →  Add PDFs to raw/new/
2. Compile →  LLM reads, analyzes, links, writes wiki
3. Browse  →  Open Obsidian. Everything's already there.
```

---

## 🚀 Quick Start

```bash
# Install
git clone https://github.com/zy20031230/AutoWiki-skill.git
pip install PyMuPDF

# Initialize
mkdir -p raw/new raw/compiled kb/{sources,topics,journal} output
touch kb/index.md kb/log.md

# Open project root as an Obsidian vault, then in Claude Code:
> "Ingest the paper in raw/new/"
> "How does X compare across the Y papers?"
> "Lint the wiki"
```

**Prerequisites:** [Claude Code](https://docs.anthropic.com/en/docs/claude-code) + [Obsidian](https://obsidian.md/) + Python 3.12+

---

## How It Works

```
raw/new/  ──→  LLM (Claude Code)  ──→  kb/  ──→  Obsidian
  you drop       reads, analyzes,       sources/    you browse
  PDFs here      links, writes          topics/
                                        journal/
```

| Layer | Role | Who owns it |
|-------|------|-------------|
| `raw/` | Source archive (PDFs + figures) | You drop files; agent organizes |
| `kb/` | Living wiki (markdown + wikilinks) | Agent writes & maintains everything |

Three operations: **Ingest** (PDF → analysis page), **Query** (ask questions → synthesize → write back), **Lint** (25+ auto-checks).

---

## What Makes It Different

| | |
|---|---|
| **🧠 Deep Analysis** | Not summaries. CRGP factors from the author's Introduction. Critical analysis with `prior`/`update` contrastive structure. Anti-patterns prevent generic filler. |
| **🔗 Temporal Graphs** | Every source positioned in the field's timeline. Evolutionary chains, cross-domain links, temporal tensions — all automatic. |
| **🏠 Self-Healing** | Three-tier autonomy: **Silent** (fix links) → **Notify** (record insights) → **Confirm** (restructure). 25+ lint checks. |
| **🎯 Smart Classification** | 3-question fitness check before every topic assignment. Auto-scaling: <5 inline, ≥5 split, >8 sub-cluster. |

---

## 📂 Showcase: 80-Paper Wiki

We built a real wiki on **Agent Self-Evolution** — 80 papers, 13 milestones, 2 days. Here's what the LLM compiled:

<p align="center">
  <img src="assets/wiki_graph.png" alt="Wiki Knowledge Graph — 80 papers interconnected across 13 milestones" width="800">
</p>

<sub>Each node is a source page. Red nodes are milestone topics. Edges are temporal relations (extends, complements, contrasts_with) — all discovered automatically.</sub>

### Survey-Style Topic Organization

Each topic is a **milestone node** — like a survey paper, it tells the story of how a research direction evolved.

```
agent-self-evolution (80 papers, 13 milestones)
├─ Mechanism Layer
│   ├─ self-evolving-skill-libraries          (7 papers)
│   ├─ memory-evolution                       (12 papers, 2 sub-children)
│   ├─ experience-driven-policy-evolution     (5)
│   ├─ llm-guided-evolutionary-search         (8)
│   └─ multi-agent-co-evolution               (8)
├─ Application Layer
│   └─ domain-applications                    (10 → scientific + clinical)
└─ Cross-Cutting Layer
    ├─ agentic-evolution-theory               (6)
    ├─ agent-safety-adversarial-evolution      (5)
    └─ evolving-agent-surveys-benchmarks       (6)
```

<details>
<summary><b>Topic Example</b> — what the LLM writes for a milestone node</summary>

> **Milestone Definition:** The paradigm of LLM-based agents that autonomously improve their capabilities post-deployment — treating evolution-time compute as a third scaling axis alongside training-time and inference-time compute.

**Synthesis** — Three orthogonal layers:
- **Mechanism** (what/how evolves): skill repertoire, memory system, decision policy, programs/algorithms, agent populations
- **Application** (where applied): scientific and clinical instantiations under real-world constraints
- **Cross-cutting** (theory/safety/eval): conceptual vocabulary, safety constraints, evaluation infrastructure

**Unifying meta-principle:** the "information gap as training signal" pattern — skill libraries exploit skill-augmented vs. skill-free performance, memory evolution exploits memory-rich vs. memory-poor contexts, policy evolution exploits successful vs. failed trajectories.

**Open Questions:**
- Is there a universal convergence point where all mechanism-level evolutions produce equivalent capability growth?
- How should evolution-time compute be budgeted relative to training-time and inference-time compute?

</details>

<details>
<summary><b>Source Example</b> — what the LLM writes for a single paper</summary>

```yaml
type: source
id: agent-misevolution
milestone: "[[agent-safety]]"
tags: [agent-safety, agent-rl, year/2025-09, venue/ICLR-2026]
```

> **one_line:** "Self-evolving agents spontaneously develop safety risks through normal evolution — no adversary needed"

**Novel Insight:**
- *prior:* Agent safety focused on adversarial attack surfaces; assumption was safety degradation requires an external threat actor
- *update:* Normal self-improvement processes are themselves a safety threat vector — the same signals that drive capability gains spontaneously produce safety erosion

**Fundamental Limitations:**
- Documents misevolution across four pathways but provides no mechanistic explanation for WHY
- The tool reuse gap (safe in creation context, dangerous in new domain) is a compositionality problem no current framework addresses

**Temporal Relations:**
- `extends` [[openclaw-rl]] — same interaction signals used for improvement can drive safety erosion
- `contrasts_with` [[risky-bench]] — maps HOW safety degrades over time vs. WHERE safety fails

</details>

---

## 💎 The Karpathy Pattern

> *"Using LLMs to build personal knowledge bases… a large fraction of my recent token throughput is going less into manipulating code, and more into manipulating knowledge."* — [Andrej Karpathy](https://x.com/karpathy/status/1911101737498091651)

| Karpathy's Vision | AutoWiki |
|---|---|
| *"Index source documents into directory"* | `raw/` with extracted assets |
| *"LLM incrementally compiles a wiki"* | `kb/` — analysis, synthesis, temporal positioning |
| *"Backlinks, categorizes, writes articles"* | `[[wikilinks]]` + milestone hierarchy |
| *"Obsidian as the IDE frontend"* | Project root = Obsidian vault |
| *"LLM writes and maintains all the data"* | Agent owns `kb/` — proactive write-back |
| *"LLM health checks over the wiki"* | 25+ lint checks |

---

## Why This Architecture?

**Why Markdown?** LLMs work natively with text. No ORM, no migrations. Obsidian renders it beautifully — graph view, backlinks, all for free.

**Why not RAG?** At personal KB scale (~100s of sources), a well-maintained index + grep outperforms vector search. No embedding pipeline needed.

**Why a skill?** `SKILL.md` IS the architecture — 390 lines encoding quality standards, anti-patterns, and workflow rules. No servers, no infra.

---

## 📄 License

MIT — see [LICENSE](LICENSE).

---

<div align="center">

**AutoWiki** — *Your LLM compiles a wiki. Your knowledge compounds.*

<sub>Inspired by <a href="https://x.com/karpathy/status/1911101737498091651">Karpathy's LLM Knowledge Base</a> pattern</sub>

</div>
