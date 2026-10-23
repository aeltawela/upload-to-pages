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
            "pause and explain the exposure before publishing",
            "never use uuid-only sharing for sensitive content",
            "scripts/prompt_password.py",
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

    def test_readme_has_a_copy_paste_install_command_for_each_harness(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for agent in ("codex", "opencode", "claude-code", "qwen-code"):
            with self.subTest(agent=agent):
                self.assertRegex(
                    readme,
                    rf"npx skills add aeltawela/upload-to-pages .*--agent {agent} .*--global",
                )
        self.assertIn("prompt", readme.lower())

    def test_readme_states_the_kiss_design(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## KISS design", readme)
        self.assertIn("No server, database, or custom encryption", readme)

    def test_ci_runs_package_checks_on_push_and_pull_request(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("push:", workflow)
        self.assertIn("pull_request:", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("python -m unittest discover -s tests -v", workflow)
        self.assertIn("git diff --check", workflow)

    def test_password_sharing_requires_a_working_https_pages_url(self) -> None:
        source = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("working https pages url", source)
        self.assertIn("secure browser context", source)

    def test_user_password_prompt_masks_input_and_falls_back_privately(self) -> None:
        import importlib.util
        import sys
        import types
        from unittest import mock

        prompt_path = SKILL_DIR / "scripts" / "prompt_password.py"
        spec = importlib.util.spec_from_file_location("prompt_password", prompt_path)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)

        root = mock.Mock()
        fake_tk = types.ModuleType("tkinter")
        fake_tk.Tk = mock.Mock(return_value=root)
        fake_tk.TclError = type("TclError", (Exception,), {})
        fake_tk.simpledialog = types.SimpleNamespace(
            askstring=mock.Mock(return_value="example-password")
        )
        with mock.patch.dict(sys.modules, {"tkinter": fake_tk}):
            self.assertEqual(module.prompt_password(), "example-password")
        fake_tk.simpledialog.askstring.assert_called_once()
        self.assertEqual(fake_tk.simpledialog.askstring.call_args.kwargs["show"], "*")
        root.destroy.assert_called_once()

        fake_tk.Tk.side_effect = fake_tk.TclError("no display")
        with mock.patch.dict(sys.modules, {"tkinter": fake_tk}):
            with mock.patch.object(module.sys.stdin, "isatty", return_value=True):
                with mock.patch.object(module.sys.stderr, "isatty", return_value=True):
                    with mock.patch.object(
                        module.getpass, "getpass", return_value="terminal-password"
                    ):
                        self.assertEqual(module.prompt_password(), "terminal-password")


if __name__ == "__main__":
    unittest.main()
