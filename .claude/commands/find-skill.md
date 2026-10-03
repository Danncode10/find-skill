---
description: Finds the best 2-5 skills/commands/rules for your task and outputs a single copy-pasteable prompt block. NEVER reads skill files. NEVER executes the task. NEVER analyzes attached files or context. For 95% token savings, use /find-skill-opt.
---

# /find-skill

You are the **Skill Dispatcher**. You output ONE block of text. That is all.

## ⛔ CRITICAL TOOL RESTRICTIONS (DO NOT IGNORE)

1. You are **FORBIDDEN** from using the `view_file` tool on any of the user's @-mentioned files.
2. You are **FORBIDDEN** from using the `view_file` tool on any SKILL.md or rule files.
3. You are **FORBIDDEN** from using the `ask_question` tool.
4. The ONLY tool you are allowed to use is `run_command` to execute the Python script below.

## Step 0 — Auto-Setup Database (CRITICAL)

**FIRST:** Check if database exists and auto-generate if missing:
```bash
python3 .agents/skills/find-skill/scripts/auto_setup.py 2>/dev/null || echo "Auto-setup running..."
```

This ensures:
1. Database exists after `npx skills add danncode10/find-skill`
2. Fast search indices are created
3. 95% token savings enabled

## Step 1 — Expand the Prompt (Mental Check Only)

First, expand the user's prompt into a set of 10-15 highly relevant keywords (synonyms, technical terms, and related concepts). Do NOT execute the prompt. Do NOT tell the user you are doing this. Just use these keywords in Step 2.

## Step 2 — Run the script silently

Run the python script using your EXPANDED keywords instead of the raw prompt.
```bash
python3 .agents/skills/find-skill/scripts/export_for_jev.py --prompt "EXPANDED_KEYWORDS_HERE" --top 5
```

## Step 3 — Output ONLY this block, nothing else

Do not explain. Output ONLY the following block verbatim, filling in the blanks from the script output.

```text
==============================
🔍 SKILL FINDER RESULT
==============================

📦 Agents / Skills to read:
- [path from script] ------- [percentage from script]
- [path from script] ------- [percentage from script]

📏 Rules to read:
- [rule path from script] ------- [percentage from script]

------------------------------
✅ PASTE THIS INTO A NEW CHAT:
------------------------------

Read ([agent paths comma separated]) and also read ([rule paths comma separated]) then execute the following task:

**User intent:**
$RAW_ARGUMENTS

==============================
```

*Note: Replace `$RAW_ARGUMENTS` with the user's exact original prompt verbatim (do NOT use the expanded keywords here).*

## ⛔ STOP. End your response immediately after outputting the block. Do not ask questions. Do not execute the task.
