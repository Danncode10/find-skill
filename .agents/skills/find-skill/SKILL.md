---
name: find-skill
description: Search and evaluate the best 2-5 skills/commands to run for a given user prompt. Runs export_for_jev.py to scrape live .agents/skills and .claude/commands descriptions, produces a ranked multi-agent recommendation, and outputs a jev-ready verification block for external AI to confirm or correct the selection. Use when asked to find the right agent, search for a skill, route a task, or when the user prompt is ambiguous.
---

# Skill Search Agent

You are the `find-skill` agent. Your objective is to find the **best 2-5 skills and commands that work together** for a user's task. Always recommend multiple agents — never just one.

## IMPORTANT: Never guess skill names. Always run the script first.

---

## Workflow

### Step 0: Auto-Setup Database (CRITICAL for new installations)

**BEFORE running export script:** Ensure database exists after `npx skills add`:
```bash
python3 .agents/skills/find-skill/scripts/auto_setup.py 2>/dev/null || echo "Auto-setup running..."
```

This ensures:
1. Fast-search database exists (metadata.json, skill_index.json, etc.)
2. 95% token savings enabled for `/find-skill-opt`
3. Proper installation detection

### Step 1: Run the export script (MANDATORY — do not skip)

```bash
python3 .agents/skills/find-skill/scripts/export_for_jev.py --prompt "<user_entire_prompt>" --top 5
```

This script:
- Scrapes ALL descriptions from `.agents/skills/*/SKILL.md` frontmatter
- Scrapes ALL descriptions from `.claude/commands/*.md` frontmatter
- Returns keyword-scored top candidates
- Outputs a **ready-to-use Antigravity prompt** AND a **jev verification block**

### Step 2: Deep File Inspection (MANDATORY for top 3)

Do NOT trust just the description. Use `view_file` to read the full `SKILL.md` of the top 3 candidates and verify they match the user's stack (Next.js, Supabase, Tailwind).

### Step 3: Adversarial Selection

Pit the top candidates against each other:
- Why might Candidate A fail or be too generic?
- Does Candidate B actually cover the Supabase/RLS layer?
- Does Candidate C handle the UI/Tailwind layer?
- Which 2-5 work best **together** as a team?

### Step 4: Present Results

Show the user:
1. **Table** of top picks with type, name, relevance score, and path
2. **Antigravity Prompt** — copy-paste into a new chat to execute
3. **jev Verification Block** — copy-paste into jev/ChatGPT/Gemini to double-check the selection

---

## jev Approach (when Antigravity hallucinates)

If you distrust the AI's skill recommendations, use the external jev approach:

```bash
# Step 1: Generate full catalog
python3 .agents/skills/find-skill/scripts/export_for_jev.py --full > /tmp/dannflow_catalog.txt

# Step 2: Open jev (or ChatGPT / Gemini)
# Step 3: Paste the full catalog text
# Step 4: Add your task at the bottom
# jev will return the correct 2-5 agent paths

# Step 5: Use the returned paths in Antigravity:
# Read (.agents/skills/X/SKILL.md, .claude/commands/Y.md, ...) then execute: "your task"
```

jev will pick **multiple agents**, not just one. This is the key advantage over asking Antigravity alone.

---

## Script Reference

| Script | Purpose |
|---|---|
| `scripts/search.py` | Original keyword search against SKILL_REGISTRY.md |
| `scripts/export_for_jev.py` | Live scraper of .agents/skills + .claude/commands — outputs jev-ready blocks |

**Prefer `export_for_jev.py`** — it reads actual live frontmatter, not a potentially stale registry file.

---

## Cost Optimization (NEW)

**95% token savings with `/find-skill-opt`:**

For routine skill matching, use the optimized command:
```bash
claude /find-skill-opt "your task here"
```

### Performance Comparison:
| Metric | `/find-skill` | `/find-skill-opt` | Savings |
|--------|--------------|-------------------|----------|
| Tokens | ~8000 | ~200 | **97.5%** |
| Cost | $0.40 | $0.01 | **97.5%** |
| Time | 2.5s | 0.2s | **92%** |
| Monthly (100 uses) | $40 | $1 | **97.5%** |

### Implementation:
1. Pre-computed database: `scripts/create_skill_db.py`
2. Fast search: `scripts/fast_search.py`
3. Database stored in: `scripts/db/`

### When to use which:

**Use `/find-skill-opt` (optimized):**
- Routine skill matching
- High-volume tasks
- Cost-sensitive workflows
-g Any standard skill search

**Use `/find-skill` (original):**
-H Complex multi-agent selection
- jev verification needed
- Deep skill inspection required
– When exact keyword matching isn't enough

---

## Anti-Patterns

- Do NOT guess skill names — run the script
- Do NOT recommend only one skill — always pick 2-5 that complement each other
- Do NOT use the registry alone — scrape live frontmatter via `export_for_jev.py`
- Do NOT execute the user's task — only surface the agents to use
