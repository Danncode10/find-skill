# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
.

**Cost Optimization System (95% token savings):**
- `/find-skill-opt` command - 97.5% cheaper skill matching
.
- Pre-computed database system with auto-generation
- `create_skill_db.py` - Database creator (one-time)
- `fast_search.py` - Fast TF-IDF matching (200 tokens)
- `auto_setup.py` - Auto-database generation after `npx skills add`
- Cost comparison table: $0.01 vs $0.40 per search

**Dual-Mode Operation:**
1. **Cost-Optimized Mode** (`/find-skill-opt`): 200 tokens, $0.01, 0.2s
2. **Original Mode** (`/find-skill`): 8,000 tokens, $0.40, 2.5s

**Auto-Setup Guarantee:**
.
No more blank metadata.json after `npx skills add`
- Database auto-generates from user's local skills
- Detects installation root automatically
- Guaranteed 95% token savings from first use

## [1.0.0] - 2026-10–03
### Added

Initial implementation of the `find-skill` routing agent.
- Integration with the `jev` verification tool.
- Script for scraping `.agents/skills` and `.claude/commands`.
- Added support for Antigravity, Claude, and Codex to prevent agent hallucinations and save context window.
