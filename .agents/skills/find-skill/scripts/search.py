#!/usr/bin/env python3
import sys
import re
import os

if len(sys.argv) < 2:
    print("Usage: python3 search.py \"<user prompt>\"")
    sys.exit(1)

prompt = sys.argv[1].lower()

# Basic stop words to ignore
stop_words = {"a", "an", "the", "and", "or", "but", "is", "are", "was", "were", "to", "for", "with", "on", "in", "at", "of", "how", "what", "where", "when", "why", "can", "you", "i", "need", "want", "help", "me", "do", "this", "please", "make", "create", "check"}

words = re.findall(r'\b\w+\b', prompt)
keywords = set(w for w in words if w not in stop_words and len(w) > 2)

# Determine path to SKILL_REGISTRY.md (relative to project root)
registry_path = "docs/dannflow_docs/SKILL_REGISTRY.md"
if not os.path.exists(registry_path):
    # Try looking from the script's directory if run from there
    script_dir = os.path.dirname(os.path.realpath(__file__))
    registry_path = os.path.join(script_dir, "../../../../docs/dannflow_docs/SKILL_REGISTRY.md")

if not os.path.exists(registry_path):
    print(f"Error: Cannot find SKILL_REGISTRY.md at {registry_path}")
    sys.exit(1)

skills = []
with open(registry_path, 'r', encoding='utf-8') as f:
    for line in f:
        # Regex to parse '- **skill-name**: description' OR '- **"skill-name"**: description'
        match = re.match(r'^- \*\*(?:")?([^"]+)(?:")?\*\*: (.*)', line.strip())
        if match:
            skills.append((match.group(1), match.group(2)))

results = []
for name, desc in skills:
    score = 0
    name_lower = name.lower()
    desc_lower = desc.lower()
    
    # Exact phrase matches get massive boosts
    if prompt in name_lower:
        score += 100
    elif prompt in desc_lower:
        score += 50
        
    # Word matches
    for kw in keywords:
        if kw in name_lower:
            # Word match in name is high priority
            score += 15
        if kw in desc_lower:
            # Count occurrences in description
            count = len(re.findall(rf'\b{re.escape(kw)}\b', desc_lower))
            score += (count * 3)
            
    if score > 0:
        results.append((score, name, desc))

# Sort by highest score
results.sort(key=lambda x: x[0], reverse=True)

print(f"🔍 Extracted core keywords: {', '.join(keywords)}\n")

if not results:
    print("No matching skills found in the registry. The prompt might require building a new skill.")
    sys.exit(0)

print("==========================================")
print("📑 Top Ranked Candidates from SKILL_REGISTRY")
print("==========================================\n")

# Return top 15 max to keep context window clean
for i, (score, name, desc) in enumerate(results[:15]):
    print(f"--- Rank {i+1} (Relevance Score: {score}) ---")
    print(f"Name: {name}")
    print(f"Description: {desc}\n")
