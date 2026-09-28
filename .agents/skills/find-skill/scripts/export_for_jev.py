#!/usr/bin/env python3
"""
export_for_jev.py
-----------------
Scrapes ALL skill descriptions from .agents/skills/, command descriptions
from .claude/commands/, and rule summaries from .agents/rules/.
Outputs a clean, copy-pasteable text block for jev / external AI selection.

Usage:
    python3 .agents/skills/find-skill/scripts/export_for_jev.py
    python3 .agents/skills/find-skill/scripts/export_for_jev.py --prompt "your task here"
    python3 .agents/skills/find-skill/scripts/export_for_jev.py --prompt "your task" --top 5
    python3 .agents/skills/find-skill/scripts/export_for_jev.py --no-rules  # skip rules section

Output modes:
    (no --prompt)   -> Full catalog dump (skills + commands + rules) for jev paste
    (with --prompt) -> Keyword-filtered candidates + relevant rules + ready-to-use prompt
"""

import sys
import os
import re
import argparse

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../../../"))
SKILLS_DIR = os.path.join(PROJECT_ROOT, ".agents", "skills")
RULES_DIR  = os.path.join(PROJECT_ROOT, ".agents", "rules")
COMMANDS_DIR = os.path.join(PROJECT_ROOT, ".claude", "commands")

STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "is", "are", "was", "were",
    "to", "for", "with", "on", "in", "at", "of", "how", "what", "where",
    "when", "why", "can", "you", "i", "need", "want", "help", "me", "do",
    "this", "please", "make", "create", "check", "use", "it", "my", "be",
    "from", "that", "have", "has", "will", "get", "set", "up", "new"
}


def scrape_skills(skills_dir):
    entries = []
    if not os.path.isdir(skills_dir):
        return entries
    for skill_name in sorted(os.listdir(skills_dir)):
        skill_path = os.path.join(skills_dir, skill_name)
        skill_md = os.path.join(skill_path, "SKILL.md")
        if not os.path.isfile(skill_md):
            continue
        name = skill_name
        description = ""
        with open(skill_md, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if fm_match:
            fm = fm_match.group(1)
            name_m = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
            desc_m = re.search(r"^description:\s*(.+?)(?=\n\w|\Z)", fm, re.MULTILINE | re.DOTALL)
            if name_m:
                name = name_m.group(1).strip().strip('"')
            if desc_m:
                description = desc_m.group(1).strip().replace("\n", " ").strip()
        if description:
            entries.append({
                "type": "skill", "name": name,
                "path": f".agents/skills/{skill_name}/SKILL.md",
                "description": description,
            })
    return entries


def scrape_commands(commands_dir):
    entries = []
    if not os.path.isdir(commands_dir):
        return entries
    for fname in sorted(os.listdir(commands_dir)):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(commands_dir, fname)
        command_name = "/" + fname[:-3]
        description = ""
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if fm_match:
            fm = fm_match.group(1)
            desc_m = re.search(r"^description:\s*(.+?)(?=\n\w|\Z)", fm, re.MULTILINE | re.DOTALL)
            if desc_m:
                description = desc_m.group(1).strip().replace("\n", " ").strip()
        if not description:
            h1 = re.search(r"^# (.+)$", content, re.MULTILINE)
            if h1:
                description = h1.group(1).strip()
        if description:
            entries.append({
                "type": "command", "name": command_name,
                "path": f".claude/commands/{fname}",
                "description": description,
            })
    return entries


def scrape_rules(rules_dir):
    """Reads .agents/rules/*.md — extracts first heading + first paragraph as description."""
    entries = []
    if not os.path.isdir(rules_dir):
        return entries
    for fname in sorted(os.listdir(rules_dir)):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(rules_dir, fname)
        rule_name = fname[:-3]  # strip .md
        description = ""
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        # Extract first H1/H2 heading
        h_match = re.search(r'^#{1,2}\s+(.+)$', content, re.MULTILINE)
        # Extract first non-empty paragraph after heading
        para_match = re.search(r'^#{1,2}[^\n]*\n+([^#\n][^\n]{20,})', content, re.MULTILINE)
        title = h_match.group(1).strip() if h_match else rule_name
        body  = para_match.group(1).strip()[:180] if para_match else ""
        description = f"{title} — {body}" if body else title
        if description:
            entries.append({
                "type": "rule",
                "name": rule_name,
                "path": f".agents/rules/{fname}",
                "description": description,
            })
    return entries


def score_entry(entry, keywords, raw_prompt):
    name_l = entry["name"].lower()
    desc_l = entry["description"].lower()
    score = 0
    if raw_prompt in name_l:
        score += 200
    if raw_prompt in desc_l:
        score += 100
    for kw in keywords:
        if kw in name_l:
            score += 20
        count = len(re.findall(rf"\b{re.escape(kw)}\b", desc_l))
        score += count * 5
    return score


def extract_keywords(prompt):
    words = re.findall(r"\b\w+\b", prompt.lower())
    return {w for w in words if w not in STOP_WORDS and len(w) > 2}


def format_full_catalog(skills, commands, rules):
    lines = [
        "=" * 70,
        "DANNFLOW AGENT & SKILL CATALOG — for jev / external AI selection",
        "=" * 70,
        "",
        "INSTRUCTIONS FOR jev:",
        "  1. Read the user task at the bottom.",
        "  2. Pick the BEST 2-5 agents/skills/commands that should work TOGETHER.",
        "  3. Also pick any RULES files the AI should read before executing.",
        "  4. Return as: Read (skill paths...) + also read (rule paths...) then execute: \"<task>\"",
        "",
        "--- SKILLS (.agents/skills/) ---",
    ]
    for e in skills:
        lines.append(f"[SKILL] {e['name']}")
        lines.append(f"  Path: {e['path']}")
        lines.append(f"  Description: {e['description'][:220]}")
        lines.append("")
    lines.append("--- SLASH COMMANDS (.claude/commands/) ---")
    for e in commands:
        lines.append(f"[COMMAND] {e['name']}")
        lines.append(f"  Path: {e['path']}")
        lines.append(f"  Description: {e['description'][:220]}")
        lines.append("")
    if rules:
        lines.append("--- RULES (.agents/rules/) ---")
        for e in rules:
            lines.append(f"[RULE] {e['name']}")
            lines.append(f"  Path: {e['path']}")
            lines.append(f"  Description: {e['description'][:220]}")
            lines.append("")
    lines += [
        "=" * 70,
        "USER TASK (paste your task below this line, then send to jev):",
        "=" * 70,
    ]
    return "\n".join(lines)


def format_filtered_output(scored_agents, scored_rules, prompt, top_n):
    top = scored_agents[:top_n]
    lines = [
        "=" * 70,
        f"jev-ready skill picker — Top {top_n} candidates",
        "=" * 70,
        f"Task: {prompt}",
        "",
        "--- AGENTS / COMMANDS ---",
    ]
    paths = []
    for score, entry in top:
        tag = entry["type"].upper()
        lines.append(f"[{tag}] {entry['name']}  (relevance: {score})")
        lines.append(f"  {entry['description'][:220]}")
        lines.append(f"  -> {entry['path']}")
        lines.append("")
        paths.append(entry["path"])

    # Show relevant rules
    rule_paths = []
    if scored_rules:
        lines.append("--- RELEVANT RULES TO READ BEFORE EXECUTING ---")
        for score, entry in scored_rules[:3]:
            lines.append(f"[RULE] {entry['name']}  (relevance: {score})")
            lines.append(f"  {entry['description'][:220]}")
            lines.append(f"  -> {entry['path']}")
            lines.append("")
            rule_paths.append(entry["path"])

    read_list  = ", ".join(paths)
    rules_list = ", ".join(rule_paths)

    prompt_block = f'Read ({read_list}) and execute the following task following those\nskill/command instructions strictly:'
    if rules_list:
        prompt_block += f'\n\nAlso read these rules before executing: Read ({rules_list})'
    prompt_block += f'\n\n"{prompt}"'

    lines += [
        "-" * 70,
        "READY-TO-USE ANTIGRAVITY PROMPT (copy & paste):",
        "-" * 70,
        "",
        prompt_block,
        "",
        "-" * 70,
        "JEV VERIFICATION BLOCK (paste after full catalog in jev):",
        "-" * 70,
        "",
        f"My AI suggested agents: {read_list}.",
        f"My AI suggested rules:  {rules_list if rules_list else 'none'}.",
        f"Based on the full catalog, confirm or correct which 2-5 agents + which rules BEST match:",
        f'"{prompt}"',
        "",
        "Return in this format:",
        "Agents: Read (path1, path2, path3)",
        "Rules:  Read (rule_path1, rule_path2)",
        "Then execute the task.",
        "=" * 70,
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Export DannFlow agent catalog for jev AI selection.")
    parser.add_argument("--prompt", "-p", type=str, default="", help="Task prompt to filter by")
    parser.add_argument("--top", "-t", type=int, default=5, help="Number of top results (default 5)")
    parser.add_argument("--full", action="store_true", help="Always output full catalog")
    parser.add_argument("--no-rules", action="store_true", help="Exclude rules from output")
    args = parser.parse_args()

    skills   = scrape_skills(SKILLS_DIR)
    commands = scrape_commands(COMMANDS_DIR)
    rules    = [] if args.no_rules else scrape_rules(RULES_DIR)
    all_entries = skills + commands  # rules scored separately

    print(f"\n[scraped] {len(skills)} skills + {len(commands)} commands + {len(rules)} rules = {len(all_entries)+len(rules)} total\n", file=sys.stderr)

    if not args.prompt or args.full:
        print(format_full_catalog(skills, commands, rules))
        return

    keywords = extract_keywords(args.prompt)
    print(f"[keywords] {', '.join(sorted(keywords))}\n", file=sys.stderr)

    # Score agents
    scored_agents = []
    for entry in all_entries:
        s = score_entry(entry, keywords, args.prompt.lower())
        if s > 0:
            scored_agents.append((s, entry))
    scored_agents.sort(key=lambda x: x[0], reverse=True)

    # Score rules separately
    scored_rules = []
    for entry in rules:
        s = score_entry(entry, keywords, args.prompt.lower())
        if s > 0:
            scored_rules.append((s, entry))
    scored_rules.sort(key=lambda x: x[0], reverse=True)

    if not scored_agents:
        print("No agent matches found. Run without --prompt to get the full catalog for jev.")
        return

    print(format_filtered_output(scored_agents, scored_rules, args.prompt, args.top))


if __name__ == "__main__":
    main()
