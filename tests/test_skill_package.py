import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SKILL_DIR = ROOT / "skills" / "upload-to-pages"


class SkillPackageTests(unittest.TestCase):
    def test_skill_uses_the_portable_agent_skills_manifest(self) -> None:
        source = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---\n", source, re.DOTALL)

        self.assertIsNotNone(match, "SKILL.md must start with YAML frontmatter")
        frontmatter = match.group(1)
        self.assertRegex(frontmatter, r"(?m)^name: upload-to-pages$")
        self.assertRegex(frontmatter, r"(?m)^description: Use when ")
        self.assertIn("license: MIT", frontmatter)
        self.assertNotIn("opencode/", frontmatter)
        self.assertNotIn("claude/", frontmatter)
        self.assertNotIn("qwen/", frontmatter)

    def test_skill_covers_the_agreed_sharing_safeguards(self) -> None:
        source = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8").lower()
        required = [
            "github pages",
            "staticrypt",
            "uuid",
            "sensitive",
            "password",
            "expiry",
            "workflow",
            "github connector",
            "gh",
        ]
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, source)

    def test_expiry_workflow_cleans_then_deploys_daily_and_manually(self) -> None:
        workflow = (SKILL_DIR / "templates" / "pages-expiry.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("schedule:", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("scripts/expire_pages.py", workflow)
        self.assertIn("mkdir -p site/shares", workflow)
        self.assertIn("git add -A -- site/shares", workflow)
        self.assertIn("actions/upload-pages-artifact@v4", workflow)
        self.assertIn("path: site", workflow)
        self.assertIn("actions/deploy-pages@v5", workflow)

    def test_readme_has_install_steps_for_each_requested_runtime(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
        for runtime in ("chatgpt", "claude", "opencode", "qwen"):
            with self.subTest(runtime=runtime):
                self.assertIn(runtime, readme)


if __name__ == "__main__":
    unittest.main()
