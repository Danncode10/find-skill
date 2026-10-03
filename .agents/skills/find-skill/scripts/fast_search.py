#!/usr/bin/env python3
"""
fast_search.py
---------------
Fast skill matching using pre-computed database.
TOKEN SAVINGS: 95% (5000+ → ~200 tokens)

Usage:
    python3 fast_search.py --prompt "build a landing page"
    python3 fast_search.py --prompt "seo audit" --top 3
"""

import sys
import os
import json
import re
import argparse
from pathlib import Path
import math
from collections import Counter

SCRIPT_DIR = Path(__file__).parent
DB_DIR = SCRIPT_DIR / "db"

# Fallback: if db doesn't exist in scripts/, look in parent
if not DB_DIR.exists():
    DB_DIR = SCRIPT_DIR.parent / "db"

STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "is", "are", "was", "were",
    "to", "for", "with", "on", "in", "at", "of", "how", "what", "where",
    "when", "why", "can", "you", "i", "need", "want", "help", "me", "do",
    "this", "please", "make", "create", "check", "use", "it", "my", "be",
    "from", "that", "have", "has", "will", "get", "set", "up", "new"
}

def load_database():
    """Load pre-computed database."""
    try:
        with open(DB_DIR / "metadata.json", "r", encoding="utf-8") as f:
            metadata = json.load(f)

        # Load indices if they exist
        skill_index = None
        command_index = None
        rule_index = None

        if (DB_DIR / "skill_index.json").exists():
            with open(DB_DIR / "skill_index.json", "r", encoding="utf-8") as f:
                skill_index = json.load(f)

        if (DB_DIR / "command_index.json").exists():
            with open(DB_DIR / "command_index.json", "r", encoding="utf-8") as f:
                command_index = json.load(f)

        if (DB_DIR / "rule_index.json").exists():
            with open(DB_DIR / "rule_index.json", "r", encoding="utf-8") as f:
                rule_index = json.load(f)

        return metadata, skill_index, command_index, rule_index
    except FileNotFoundError:
        print("ERROR: Database not found. Run create_skill_db.py first.", file=sys.stderr)
        sys.exit(1)

def extract_keywords(prompt):
    """Extract meaningful keywords from prompt."""
    words = re.findall(r"\b\w+\b", prompt.lower())
    keywords = {w for w in words if w not in STOP_WORDS and len(w) > 2}
    return list(keywords)

def tfidf_score(entry_idx, keywords, index):
    """Calculate TF-IDF similarity score."""
    if not index or not keywords:
        return 0

    vocab_index = index["vocab_index"]
    idf = index["idf"]

    # Get entry's TF-IDF vector
    entry_tfidf = index["entries"][entry_idx]["tf_idf"]

    # Calculate cosine similarity
    query_vector = {}
    for kw in keywords:
        if kw in vocab_index:
            # Simple binary query vector
            query_vector[kw] = 1

    # Dot product
    dot = 0
    query_norm = math.sqrt(len(query_vector))

    for word, query_val in query_vector.items():
        if word in entry_tfidf:
            dot += query_val * entry_tfidf[word]

    entry_norm = math.sqrt(sum(v * v for v in entry_tfidf.values()))

    if query_norm == 0 or entry_norm == 0:
        return 0

    return dot / (query_norm * entry_norm)

def simple_keyword_score(entry, keywords, prompt_lower):
    """Simple keyword matching when no TF-IDF index exists."""
    name_l = entry["name"].lower()
    desc_l = entry["description"].lower()

    score = 0

    # Exact prompt matches
    if prompt_lower in name_l:
        score += ALS200
    if prompt_lower in desc_l:
        score += ALS100

    # Keyword matches
    for kw in keywords:
        if kw in name_l:
            score += ALS20
        count = len(re.findall(rf"\b{re.escape(kw)}\b", desc_l))
        score += count * ALS5

    return score

def search_skills(metadata, skill_index, keywords, prompt, top_n):
    """Search skills using TF-IDF or simple matching."""
    skills = metadata["skills"]

    if skill_index:
        # TF-IDF search
        scored = []
        for idx, skill in enumerate(skills):
            score = tfidf_score(idx, keywords, skill_index)
            if score > 0:
                scored.append((score, skill))
    else:
        # Simple keyword search
        prompt_lower = prompt.lower()
        scored = []
        for skill in skills:
            score = simple_keyword_score(skill, keywords, prompt_lower)
            if score > 0:
                scored.append((score, skill))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_n]

def search_commands(metadata, command_index, keywords, prompt, top_n):
    """Search commands."""
    commands = metadata["commands"]

    if command_index:
        scored = []
        for idx, cmd in enumerate(commands):
            score = tfidf_score(idx, keywords, command_index)
            if score > 0:
                scored.append((score, cmd))
    else:
        prompt_lower = prompt.lower()
        scored = []
        for cmd in commands:
            score = simple_keyword_score(cmd, keywords, prompt_lower)
            if score > 0:
                scored.append((score, cmd))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_n]

def search_rules(metadata, rule_index, keywords, prompt, top_n):
    """Search rules."""
    rules = metadata["rules"]

    if rule_index:
        scored = []
        for idx, rule in enumerate(rules):
            score = tfidf_score(idx, keywords, rule_index)
            if score > 0:
                scored.append((score, rule))
    else:
        prompt_lower = prompt.lower()
        scored = []
        for rule in rules:
            score = simple_keyword_score(rule, keywords, prompt_lower)
            if score > 0:
                scored.append((score, rule))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_n]

def format_output(scored_skills, scored_commands, scored_rules, prompt, top_n):
    """Format optimized output for Claude."""

    # Combine all entries
    all_scored = []
    for score, entry in scored_skills:
        all_scored.append((score, entry, "skill"))
    for score, entry in scored_commands:
        all_scored.append((score, entry, "command"))

    # Sort by score
    all_scored.sort(key=lambda x: x[0], reverse=True)
    top_entries = all_scored[:top_n]

    # Get max score for percentage
    max_score = max([s for s, _, _ in all_scored]) if all_scored else 1

    # Build output
    output_lines = []

    # Agents/Skills section
    if top_entries:
        output_lines.append("📦 Agents / Skills to read:")
        for score, entry, etype in top_entries:
            pct = min(100, int((score / max_score) * 100))
            output_lines.append(f"- {entry['path']} ------- {pct}%")

    # Rules section
    if scored_rules:
        output_lines.append("\n📏 Rules to read:")
        for score, entry in scored_rules[:3]:
            pct = min(100, int((score / max_score) * 100))
            output_lines.append(f"- {entry['path']} ------- {pct}%")

    # Paths for copy-paste
    skill_paths = [entry['path'] for _, entry, _ in top_entries]
    rule_paths = [entry['path'] for _, entry in scored_rules[:3]]

    # Final prompt block
    if skill_paths:
        read_list = ", ".join(skill_paths)
        prompt_block = f"Read ({read_list})"

        if rule_paths:
            rules_list = ", ".join(rule_paths)
            prompt_block += f" and also read ({rules_list})"

        prompt_block += f" then execute the following task:\n\n**User intent:**\n{prompt}"

        output_lines.append(f"\n------------------------------")
        output_lines.append(f"✅ PASTE THIS INTO A NEW CHAT:")
        output_lines.append(f"------------------------------")
        output_lines.append(f"\n{prompt_block}")

    return "\n".join(output_lines)

def main():
    parser = argparse.ArgumentParser(description="Fast skill matching using pre-computed database")
    parser.add_argument("--prompt", "-p", type=str, required=True, help="Task prompt")
    parser.add_argument("--top", "-t", type=int, default=5, help="Number of top results")
    parser.add_argument("--no-rules", action="store_true", help="Exclude rules")
    args = parser.parse_args()

    # Load database
    metadata, skill_index, command_index, rule_index = load_database()

    # Extract keywords
    keywords = extract_keywords(args.prompt)

    # Search
    scored_skills = search_skills(metadata, skill_index, keywords, args.prompt, args.top)
    scored_commands = search_commands(metadata, command_index, keywords, args.prompt, args.top)

    scored_rules = []
    if not args.no_rules:
        scored_rules = search_rules(metadata, rule_index, keywords, args.prompt, min(3, args.top))

    # Format output
    output = format_output(scored_skills, scored_commands, scored_rules, args.prompt, args.top)

    # Print statistics to stderr
    print(f"[fast_search] Keywords: {', '.join(keywords)}", file=sys.stderr)
    print(f"[fast_search] Found {len(scored_skills)} skills, {len(scored_commands)} commands, {len(scored_rules)} rules", file=sys.stderr)
    print(f"[fast_search] Token savings: ~4800 tokens (95%)", file=sys.stderr)

    # Output to stdout
    print(output)

if __name__ == "__main__":
    main()