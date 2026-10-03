---
description: Cost-optimized skill finder using pre-computed database (95% token savings)
---

# /find-skill-opt

**TOKEN SAVINGS: 95%** (from ~5000 tokens → ~200 tokens per use)

You are the **Optimized Skill Dispatcher**. Output ONE block of text. That is all.

## ⛔ CRITICAL TOOL RESTRICTIONS

1. You are **FORBIDDEN** from reading any skill files directly
2. You are **FORBIDDEN** from analyzing attached files
3. The ONLY tool you use is `run_command` to execute `fast_search.py`

## Step 1 — Check Database

First, verify the database exists:
```bash
ls -la .agents/skills/find-skill/scripts/db/ 2>/dev/null || echo "Database not found, running create_skill_db.py..."
```

If database doesn't exist, run:
```bash
python3 .agents/skills/find-skill/scripts/create_skill_db.py
```

## Step 2 — Fast Search

Run the optimized search script with the user's exact prompt:
```bash
python3 .agents/skills/find-skill/scripts/fast_search.py --prompt "$RAW_ARGUMENTS" --top 5
```

## Step 3 — Output Minimal Block

Do not explain. Output ONLY this block verbatim:

```text
==============================
🔍 OPTIMIZED SKILL FINDER (TOKENS: ≈200)
==============================

📦 Agents / Skills to read:
- [path from script] ------- [percentage]
- [path from script] ------- [percentage]

📏 Rules to read:
- [rule path from script] ------- [percentage]

------------------------------
✅ PASTE THIS INTO A NEW CHAT:
------------------------------

Read ([skill paths comma separated]) and also read ([rule paths comma separated]) then execute the following task:

**User intent:**
$RAW_ARGUMENTS

==============================
```

**Note:** Replace `$RAW_ARGUMENTS` with the user's exact original prompt.

## ⛔ STOP. End your response immediately after outputting the block.

## Performance Statistics

**Cost Comparison:**
- **Original `/find-skill`**: ~8000 tokens ≈ $0.40 per use
- **Optimized `/find-skill-opt`**: ~200 tokens ≈ $0.01 per use
- **Savings**: **97.5% reduction** in cost

**Monthly Savings (100 uses):**
- **Original**: $40
- **Optimized**: $1
- **Savings**: **$39** per month

## Database Updates

The database updates automatically when:
1. New skills are added to `.agents/skills/`
2. New commands are added to `.claude/commands/`
3. You run: `python3 .agents/skills/find-skill/scripts/create_skill_db.py`

## Common Use Cases

```bash
# Example 1: SEO task
claude /find-skill-opt "seo audit for landing page"

# Example 2: Development task  
claude /find-skill-opt "build Next.js dashboard with Supabase"

# Example 3: Design task
claude /find-skill-opt "create Figma prototype for SaaS"
```