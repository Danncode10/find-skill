#!/usr/bin/env python3
"""
Tests for export_for_jev.py

Run from project root:
    python3 -m pytest .agents/skills/find-skill/tests/ -v
    python3 .agents/skills/find-skill/tests/test_export_for_jev.py
"""

import sys
import os
import unittest
import tempfile
import shutil

# Add script directory to path
SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts"))
sys.path.insert(0, SCRIPT_DIR)

import importlib.util
spec = importlib.util.spec_from_file_location("export_for_jev", os.path.join(SCRIPT_DIR, "export_for_jev.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

scrape_skills     = mod.scrape_skills
scrape_commands   = mod.scrape_commands
score_entry       = mod.score_entry
extract_keywords  = mod.extract_keywords
format_full_catalog    = mod.format_full_catalog
format_filtered_output = mod.format_filtered_output


class TestExtractKeywords(unittest.TestCase):
    def test_removes_stop_words(self):
        kws = extract_keywords("I want to build a payroll system")
        self.assertNotIn("i", kws)
        self.assertNotIn("to", kws)
        self.assertNotIn("a", kws)
        self.assertIn("build", kws)
        self.assertIn("payroll", kws)
        self.assertIn("system", kws)

    def test_ignores_short_words(self):
        kws = extract_keywords("do an UI fix")
        # "do" is stop word, "an" is stop word, "UI" is 2 chars so filtered
        self.assertIn("fix", kws)

    def test_empty_prompt(self):
        kws = extract_keywords("")
        self.assertEqual(kws, set())

    def test_returns_lowercase(self):
        kws = extract_keywords("Build SUPABASE Auth")
        self.assertIn("build", kws)
        self.assertIn("supabase", kws)
        self.assertIn("auth", kws)


class TestScrapeSkills(unittest.TestCase):
    def setUp(self):
        # Create a temporary fake skills directory
        self.tmp = tempfile.mkdtemp()

        # Skill WITH valid frontmatter
        skill_dir = os.path.join(self.tmp, "my-skill")
        os.makedirs(skill_dir)
        with open(os.path.join(skill_dir, "SKILL.md"), "w") as f:
            f.write('---\nname: my-skill\ndescription: Does payroll and supabase stuff.\n---\n\n# Body')

        # Skill WITHOUT frontmatter (fallback)
        skill_dir2 = os.path.join(self.tmp, "bare-skill")
        os.makedirs(skill_dir2)
        with open(os.path.join(skill_dir2, "SKILL.md"), "w") as f:
            f.write('# Bare Skill\nJust a body, no frontmatter.')

        # Directory with no SKILL.md (should be skipped)
        os.makedirs(os.path.join(self.tmp, "empty-dir"))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_scrapes_valid_skill(self):
        entries = scrape_skills(self.tmp)
        names = [e["name"] for e in entries]
        self.assertIn("my-skill", names)

    def test_skips_dir_without_skill_md(self):
        entries = scrape_skills(self.tmp)
        names = [e["name"] for e in entries]
        self.assertNotIn("empty-dir", names)

    def test_entry_has_required_keys(self):
        entries = scrape_skills(self.tmp)
        for e in entries:
            self.assertIn("type", e)
            self.assertIn("name", e)
            self.assertIn("path", e)
            self.assertIn("description", e)

    def test_type_is_skill(self):
        entries = scrape_skills(self.tmp)
        for e in entries:
            self.assertEqual(e["type"], "skill")

    def test_path_contains_skill_name(self):
        entries = scrape_skills(self.tmp)
        for e in entries:
            self.assertIn(e["name"], e["path"])

    def test_nonexistent_dir_returns_empty(self):
        entries = scrape_skills("/nonexistent/path/xyz")
        self.assertEqual(entries, [])


class TestScrapeCommands(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

        # Command with frontmatter
        with open(os.path.join(self.tmp, "find-skill.md"), "w") as f:
            f.write('---\ndescription: Finds the best skills for your task.\n---\n\n# /find-skill')

        # Command with H1 fallback (no frontmatter description)
        with open(os.path.join(self.tmp, "my-cmd.md"), "w") as f:
            f.write('# My Command Title\nBody text here.')

        # Non-.md file (should be skipped)
        with open(os.path.join(self.tmp, "ignore.txt"), "w") as f:
            f.write("skip me")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_scrapes_frontmatter_description(self):
        entries = scrape_commands(self.tmp)
        found = next((e for e in entries if e["name"] == "/find-skill"), None)
        self.assertIsNotNone(found)
        self.assertIn("Finds", found["description"])

    def test_h1_fallback(self):
        entries = scrape_commands(self.tmp)
        found = next((e for e in entries if e["name"] == "/my-cmd"), None)
        self.assertIsNotNone(found)
        self.assertEqual(found["description"], "My Command Title")

    def test_skips_non_md(self):
        entries = scrape_commands(self.tmp)
        names = [e["name"] for e in entries]
        self.assertNotIn("/ignore", names)

    def test_type_is_command(self):
        entries = scrape_commands(self.tmp)
        for e in entries:
            self.assertEqual(e["type"], "command")

    def test_nonexistent_dir_returns_empty(self):
        entries = scrape_commands("/nonexistent/path/xyz")
        self.assertEqual(entries, [])


class TestScoreEntry(unittest.TestCase):
    def _make_entry(self, name, description, etype="skill"):
        return {"type": etype, "name": name, "description": description}

    def test_exact_name_match_scores_high(self):
        # "payroll-system" in name: keyword "payroll" hits name (+20) and keyword "system" hits name (+20)
        # exact phrase "payroll system" does NOT match "payroll-system" (hyphen vs space) → no 200 bonus
        entry = self._make_entry("payroll-system", "Handles payroll")
        score = score_entry(entry, {"payroll", "system"}, "payroll system")
        # keyword "payroll" in name (+20) + in desc (+5) + keyword "system" in name (+20) = 45 min
        self.assertGreater(score, 30)

    def test_exact_phrase_in_name_scores_200(self):
        # Exact phrase match when name contains phrase with same separator
        entry = self._make_entry("payroll system builder", "Tool for payroll")
        score = score_entry(entry, {"payroll", "system"}, "payroll system")
        # "payroll system" in "payroll system builder" → +200
        self.assertGreaterEqual(score, 200)


    def test_keyword_in_description_scores(self):
        entry = self._make_entry("some-skill", "Does payroll processing and supabase queries")
        score = score_entry(entry, {"payroll", "supabase"}, "payroll supabase")
        self.assertGreater(score, 0)

    def test_no_match_scores_zero(self):
        entry = self._make_entry("unrelated-skill", "Handles C++ build errors")
        score = score_entry(entry, {"payroll", "supabase"}, "payroll supabase")
        self.assertEqual(score, 0)

    def test_multiple_keyword_occurrences_score_higher(self):
        entry1 = self._make_entry("a", "payroll payroll payroll")
        entry2 = self._make_entry("b", "payroll once")
        kw = {"payroll"}
        s1 = score_entry(entry1, kw, "payroll")
        s2 = score_entry(entry2, kw, "payroll")
        self.assertGreater(s1, s2)


class TestFormatOutput(unittest.TestCase):
    MOCK_SKILLS = [
        {"type": "skill", "name": "skill-a", "path": ".agents/skills/skill-a/SKILL.md",
         "description": "Does things A"},
    ]
    MOCK_COMMANDS = [
        {"type": "command", "name": "/cmd-b", "path": ".claude/commands/cmd-b.md",
         "description": "Does things B"},
    ]
    MOCK_RULES = [
        {"type": "rule", "name": "diagram_rules_drawio", "path": ".agents/rules/diagram_rules_drawio.md",
         "description": "Draw.io diagram rules — dark mode color rules"},
    ]

    def test_full_catalog_contains_header(self):
        out = format_full_catalog(self.MOCK_SKILLS, self.MOCK_COMMANDS, [])
        self.assertIn("DANNFLOW AGENT & SKILL CATALOG", out)
        self.assertIn("jev", out)

    def test_full_catalog_lists_skills(self):
        out = format_full_catalog(self.MOCK_SKILLS, self.MOCK_COMMANDS, [])
        self.assertIn("[SKILL] skill-a", out)

    def test_full_catalog_lists_commands(self):
        out = format_full_catalog(self.MOCK_SKILLS, self.MOCK_COMMANDS, [])
        self.assertIn("[COMMAND] /cmd-b", out)

    def test_full_catalog_lists_rules(self):
        out = format_full_catalog(self.MOCK_SKILLS, self.MOCK_COMMANDS, self.MOCK_RULES)
        self.assertIn("[RULE] diagram_rules_drawio", out)

    def test_filtered_output_contains_prompt_block(self):
        scored = [(50, self.MOCK_SKILLS[0]), (30, self.MOCK_COMMANDS[0])]
        out = format_filtered_output(scored, [], "build payroll", 2)
        self.assertIn("READY-TO-USE ANTIGRAVITY PROMPT", out)
        self.assertIn("JEV VERIFICATION BLOCK", out)

    def test_filtered_output_includes_paths(self):
        scored = [(50, self.MOCK_SKILLS[0])]
        out = format_filtered_output(scored, [], "build payroll", 1)
        self.assertIn(".agents/skills/skill-a/SKILL.md", out)

    def test_filtered_output_includes_task(self):
        scored = [(50, self.MOCK_SKILLS[0])]
        out = format_filtered_output(scored, [], "build payroll system", 1)
        self.assertIn("build payroll system", out)

    def test_filtered_output_includes_relevant_rules(self):
        scored_agents = [(50, self.MOCK_SKILLS[0])]
        scored_rules  = [(40, self.MOCK_RULES[0])]
        out = format_filtered_output(scored_agents, scored_rules, "create drawio diagram", 1)
        self.assertIn("RELEVANT RULES TO READ", out)
        self.assertIn(".agents/rules/diagram_rules_drawio.md", out)
        self.assertIn("Rules:", out)


class TestLiveScrapeSanity(unittest.TestCase):
    """Sanity check against the real project directory (if available)."""

    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
    SKILLS_DIR = os.path.join(PROJECT_ROOT, ".agents", "skills")
    COMMANDS_DIR = os.path.join(PROJECT_ROOT, ".claude", "commands")

    def test_live_skills_scrapes_more_than_100(self):
        if not os.path.isdir(self.SKILLS_DIR):
            self.skipTest("Not in project root")
        entries = scrape_skills(self.SKILLS_DIR)
        self.assertGreater(len(entries), 100, "Expected 100+ skills from live project")

    def test_live_commands_scrapes_more_than_50(self):
        if not os.path.isdir(self.COMMANDS_DIR):
            self.skipTest("Not in project root")
        entries = scrape_commands(self.COMMANDS_DIR)
        self.assertGreater(len(entries), 50, "Expected 50+ commands from live project")

    def test_live_all_entries_have_descriptions(self):
        if not os.path.isdir(self.SKILLS_DIR):
            self.skipTest("Not in project root")
        entries = scrape_skills(self.SKILLS_DIR) + scrape_commands(self.COMMANDS_DIR)
        missing = [e["name"] for e in entries if not e.get("description")]
        self.assertEqual(missing, [], f"These entries have no description: {missing[:10]}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
