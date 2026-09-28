# Skill Search — Architecture Diagram

## Overview

This document explains the full flow from user prompt to agent execution,
including how the jev external AI fits into the system.

---

## Flow 1: `/find-skill` Slash Command (Antigravity)

```
User types in Antigravity
      │
      ▼
┌─────────────────────────────────────┐
│  /find-skill "build payroll system" │
│  (.claude/commands/find-skill.md)   │
└─────────────────────────────────────┘
      │
      │ runs
      ▼
┌──────────────────────────────────────────────────────┐
│  export_for_jev.py --prompt "..." --top 5            │
│  (.agents/skills/find-skill/scripts/)              │
│                                                      │
│  Scrapes live sources:                               │
│  ├── .agents/skills/*/SKILL.md  (frontmatter)        │
│  └── .claude/commands/*.md      (frontmatter)        │
│                                                      │
│  Scores each entry by keyword match                  │
│  Returns top-N candidates                            │
└──────────────────────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────────────────────┐
│  Antigravity presents:                               │
│  ├── Ranked table (skill name, score, path)          │
│  ├── READY-TO-USE ANTIGRAVITY PROMPT                 │
│  └── JEV VERIFICATION BLOCK                         │
└──────────────────────────────────────────────────────┘
      │
      ▼
User copies prompt → pastes into new Antigravity chat
      │
      ▼
┌──────────────────────────────────────────────────────┐
│  Read (.agents/skills/X/SKILL.md,                    │
│        .claude/commands/Y.md, ...)                   │
│  then execute: "build payroll system"                │
└──────────────────────────────────────────────────────┘
```

---

## Flow 2: jev External AI Verification (Anti-Hallucination Layer)

```
User wants external AI (jev/ChatGPT/Gemini) to pick agents
      │
      ▼
┌──────────────────────────────────────────────────────┐
│  Step 1: Generate full catalog                       │
│                                                      │
│  python3 export_for_jev.py --full                    │
│                                                      │
│  Output: 2600+ line text block                       │
│  ├── [SKILL] name → path → description              │
│  └── [COMMAND] name → path → description            │
└──────────────────────────────────────────────────────┘
      │
      │ user copies output
      ▼
┌──────────────────────────────────────────────────────┐
│  jev (external AI — NOT Antigravity)                 │
│                                                      │
│  Input:                                              │
│  ├── Full catalog text (pasted by user)             │
│  └── User task at bottom                            │
│                                                      │
│  jev picks 2-5 agents that WORK TOGETHER:           │
│  ├── Not just one — always a team                    │
│  └── Returns file paths, not just names             │
└──────────────────────────────────────────────────────┘
      │
      │ jev outputs:
      ▼
┌──────────────────────────────────────────────────────┐
│  Read (.agents/skills/A/SKILL.md,                    │
│        .agents/skills/B/SKILL.md,                    │
│        .claude/commands/C.md)                        │
│  then execute: "user's task"                         │
└──────────────────────────────────────────────────────┘
      │
      │ user pastes into Antigravity
      ▼
┌──────────────────────────────────────────────────────┐
│  Antigravity reads the specified SKILL.md files      │
│  and executes the task following those instructions  │
└──────────────────────────────────────────────────────┘
```

---

## Flow 3: Combined (Best of Both — Recommended)

```
User has a task
      │
      ├─── /find-skill "task"   → Antigravity gives scored candidates
      │                           + jev verification block
      │
      └─── Paste jev block into jev → jev confirms/corrects paths
                │
                ▼
            Final prompt → Antigravity executes task
```

---

## Why SKILL_REGISTRY.md Still Matters (but differently)

```
SKILL_REGISTRY.md                    export_for_jev.py
─────────────────                    ─────────────────
Human-curated descriptions           Live-scraped from frontmatter
Can be stale                         Always current
AI reads it for context              Script reads it for scoring
~508 lines, hard to load fully       Output is structured for parsing
Used by: AGENTS.md Rule 1            Used by: /find-skill, find-skill
```

AGENTS.md Rule 1 still points to SKILL_REGISTRY.md as the "phonebook."
`export_for_jev.py` is the machine-readable version that produces
actionable, jev-ready output. They serve different audiences:
- Registry → human-readable, AI-context reference
- export_for_jev → machine output, jev input, slash command output

---

## Data Sources

```
.agents/skills/
├── skill-name/
│   └── SKILL.md          ← frontmatter: name, description
│                            scraped by export_for_jev.py
.claude/commands/
├── command-name.md       ← frontmatter: description
│                            scraped by export_for_jev.py
docs/dannflow_docs/
└── SKILL_REGISTRY.md     ← human-curated, AI phonebook
                             referenced by AGENTS.md Rule 1
```

---

## Files in This Skill

```
.agents/skills/find-skill/
├── SKILL.md                    ← agent instructions + workflow
├── docs/
│   └── architecture.md         ← this file
├── scripts/
│   ├── search.py               ← original keyword search vs SKILL_REGISTRY
│   └── export_for_jev.py       ← live scraper + jev output blocks
└── tests/
    └── test_export_for_jev.py  ← unit tests for the export script
```
