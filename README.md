# Upload to Pages

A small, portable Agent Skill for publishing ready-made HTML, reports, data, and static files with GitHub Pages. It supports unlisted UUID links for non-sensitive content, StatiCrypt-protected HTML, and date-based cleanup with one daily GitHub Actions workflow.

## KISS design

- One canonical `SKILL.md`, installed unchanged for each supported agent.
- One Pages workflow and one Python standard-library cleanup script.
- No extra hosting service, database, custom encryption, or platform-specific wrappers.

GitHub Pages is public hosting. UUID links are unlisted, not private. Expiry removes the current site folder after the scheduled job succeeds; it cannot remove Git history, cached copies, or downloads.

## Install the skill

Copy or unzip the `skills/upload-to-pages` folder into the runtime's skill directory. Keep the folder name `upload-to-pages`.

### ChatGPT

In ChatGPT, open **Plugins → Skills → Create → Upload from your computer** and select a ZIP containing the top-level `upload-to-pages/` folder. Skills are available only on eligible ChatGPT plans and workspaces; workspace settings can disable uploads. If the session has no private password input or local terminal, use generated-password mode or run encryption locally.

### OpenCode

Copy the folder to `~/.config/opencode/skills/upload-to-pages/`. OpenCode also recognizes `.agents/skills/` and `.claude/skills/` locations.

### Claude

For Claude Code, copy the folder to `~/.claude/skills/upload-to-pages/`. Claude.ai also supports uploading or syncing skills when the feature is available to the account.

### Qwen Code

Copy the folder to `~/.qwen/skills/upload-to-pages/`. Qwen Code can also load skills from configured skill paths.

The skill uses only the common `name`, `description`, and `license` frontmatter. It needs a GitHub connection or authenticated GitHub CLI for publishing; the available tools differ by host.

## Set up a share repository once

1. Add `skills/upload-to-pages/templates/pages-expiry.yml` as `.github/workflows/pages.yml`.
2. Add `skills/upload-to-pages/scripts/expire_pages.py` as `scripts/expire_pages.py`.
3. Configure **Settings → Pages → Build and deployment → Source → GitHub Actions**.
4. Allow the workflow to write to the default branch so expired folders can be removed.
5. If the site has no root page, copy `templates/site-index.html` to `site/index.html`. It does not list share links.

Each share goes under `site/shares/<UUID>/`. An optional `expiry.json` in that folder contains only an expiry date and time zone. Run the cleanup workflow manually to check it before relying on the next daily run.

## Run checks

```sh
python3 -m unittest discover -s tests -v
```

## References

- [Agent Skills standard](https://agentskills.io/)
- [Skills in ChatGPT](https://help.openai.com/en/articles/20001066-skills-in-chatgpt)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [OpenCode skills](https://opencode.ai/docs/skills)
- [Qwen Code skills](https://qwenlm.github.io/qwen-code-docs/en/users/features/skills/)
- [StatiCrypt](https://github.com/robinmoisson/staticrypt)
- [GitHub Pages publishing](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [GitHub Actions schedule behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)
