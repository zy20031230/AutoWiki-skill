# AutoWiki Skill

LLM-maintained knowledge base skill for **Claude Code** and **OpenClaw**. Turns your coding agent into a structured wiki maintainer powered by Obsidian.

## What It Does

AutoWiki teaches your AI agent to:

- **Ingest** research papers/sources into a structured wiki with milestone-based clustering
- **Query** the wiki with automatic cross-source synthesis and proactive write-back
- **Lint** the wiki for contradictions, orphans, broken links, and stale claims
- **Maintain** bidirectional links, journal entries, and cascading updates

The wiki is fully Obsidian-compatible — the human reads and navigates in Obsidian, the agent maintains consistency.

## Installation

### Claude Code (Plugin Marketplace)

Register the marketplace, then install:

```bash
/plugin marketplace add zhangyi/autowiki-skill
/plugin install autowiki@autowiki-skill
```

Or install directly from the official marketplace if published:

```bash
/plugin install autowiki
```

### Claude Code (Local)

Clone and link:

```bash
git clone https://github.com/zhangyi/autowiki-skill.git
cd autowiki-skill
# Register as a local marketplace
```

### OpenClaw

```bash
openclaw plugins install --marketplace https://github.com/zhangyi/autowiki-skill
```

Or install from a local clone:

```bash
git clone https://github.com/zhangyi/autowiki-skill.git
openclaw plugins install --marketplace ./autowiki-skill -l
```

### Verify Installation

Start a new session in a project that has `kb/` and `raw/` directories. The agent will detect the AutoWiki structure and load the skill automatically.

Or manually invoke:

```
Use the autowiki skill to ingest this paper.
```

## Quick Start

1. Install the skill (see above)
2. Create the wiki structure:

```bash
mkdir -p raw/new raw/compiled kb/{sources,topics,journal,_templates} output
```

3. Copy templates from `skills/autowiki/references/` into `kb/_templates/`
4. Create `kb/index.md` and `kb/log.md`
5. Drop a PDF or paper into `raw/new/` and tell the agent to ingest it

## Wiki Structure

```
raw/new/          → Drop sources here for ingest
raw/compiled/     → Processed sources (moved automatically)
kb/sources/       → Literature tree, grouped by milestone
kb/topics/        → Milestone nodes (conceptual breakthroughs)
kb/journal/       → Cognitive change timeline
kb/index.md       → Navigation entry point
kb/log.md         → Operation log
```

## License

MIT
