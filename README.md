# find-skill

Eliminate AI hallucinations and achieve up to **30x less context usage**! **find-skill** uses **jev** for ultimate context optimization, perfectly routing your prompts to the exact skill, rule, or command in massive registries. The essential routing agent for **Antigravity**, **Claude**, and **Codex** developers to save tokens, execute faster, and stop guess-work.

---

## The Problem

Imagine your repository has 200 or more skills installed. When you simply ask the AI to do something, it often takes shortcuts and hallucinates trying to find the correct agent, skill, command, or rule to use. 

For example, in Antigravity, the AI might hallucinate paths and take shortcuts. In Claude and Codex, it still hallucinates and consumes a massive amount of tokens trying to scan through everything. Providing the AI with the entire registry wastes significant token bandwidth and degrades the context window.

## The Solution

**find-skill** addresses this by utilizing **jev** (an external verification tool). Instead of requiring the AI to blindly guess or read every file in the registry, it:
1. Runs a script to search and gather descriptions from all your `.agents/skills` and `.claude/commands`.
2. Uses **jev** to evaluate and choose which agent, skill, or rule has the highest probability of successfully completing your request.
3. Outputs a single, ready-to-use routing prompt.

This provides highly accurate agent routing without hallucination or polluting the active context window.

## Installation

### Install with `skills` (Recommended)

Install globally for your user:
```bash
npx skills add danncode10/find-skill --global
```

Install only for the current project by omitting `--global`:
```bash
npx skills add danncode10/find-skill
```

To target specific agents, add `--agent` followed by one or more agent IDs:
```bash
npx skills add danncode10/find-skill --agent claude-code cursor
```

## Usage

1. Open your AI chat interface (Claude Code, Antigravity, or Codex).
2. Execute the slash command `/find-skill` followed by your objective.

**Example:**
```text
/find-skill I need to build a new React component for user login
```

## Expected Output

The dispatcher executes the `export_for_jev.py` script, evaluates your prompt against all available skills, and provides a single block of text for you to copy.

It will format exactly as follows:

```text
==============================
SKILL FINDER RESULT
==============================

Agents / Skills to read:
- .agents/skills/react-reviewer/SKILL.md
- .agents/skills/ui-to-vue/SKILL.md

Rules to read:
- .agents/rules/ui_preferences.md

------------------------------
PASTE THIS INTO A NEW CHAT:
------------------------------

Read (.agents/skills/react-reviewer/SKILL.md, .agents/skills/ui-to-vue/SKILL.md) and also read (.agents/rules/ui_preferences.md) then execute the following task:

**User intent:**
I need to build a new React component for user login

==============================
```

### Next Steps:
Copy the block under "PASTE THIS INTO A NEW CHAT" and paste it into a fresh session. By offloading the discovery phase to a script in the first session, the second session begins with fully focused context, preserving tokens and reducing the risk of hallucination.
