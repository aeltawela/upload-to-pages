# Upload to Pages

**Share ready-made reports, HTML, data, and static files on GitHub Pages.** Choose an unlisted UUID link, password-protected HTML, or a date-based cleanup.

[![CI](https://github.com/aeltawela/upload-to-pages/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/aeltawela/upload-to-pages/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Agent Skill](https://img.shields.io/badge/Agent-Skill-6f42c1.svg)](https://agentskills.io/)

## Pick a sharing mode

| Mode | What the recipient gets | Use it for |
| --- | --- | --- |
| UUID link | A hard-to-guess URL to a public page | Non-sensitive content that is okay to publish |
| Password | StatiCrypt-encrypted HTML and a password shared separately | An HTML page when the host can collect a password privately |
| Expiry date | A page folder removed by the daily cleanup workflow after its date | Temporary links where delayed removal is acceptable |

GitHub Pages is public hosting. A UUID link is unlisted, not private. StatiCrypt protects HTML only; linked CSV, PDF, image, or script files remain public. Expiry is cleanup, not immediate revocation: GitHub may delay scheduled jobs, and deletion cannot remove Git history, cached copies, or downloads.

## Quick start

Install the skill for your user account with [Vercel Skills CLI](https://github.com/vercel-labs/skills). These commands install the same `SKILL.md` for each harness:

| Harness | Install command |
| --- | --- |
| ChatGPT desktop / Codex | `npx skills add aeltawela/upload-to-pages --skill upload-to-pages --agent codex --global --copy --yes` |
| OpenCode | `npx skills add aeltawela/upload-to-pages --skill upload-to-pages --agent opencode --global --copy --yes` |
| Claude Code | `npx skills add aeltawela/upload-to-pages --skill upload-to-pages --agent claude-code --global --copy --yes` |
| Qwen Code | `npx skills add aeltawela/upload-to-pages --skill upload-to-pages --agent qwen-code --global --copy --yes` |

Or ask the chosen harness to install it for you:

> Install the `upload-to-pages` skill from `aeltawela/upload-to-pages` for this harness using the install command in this README. Install it for my user account, keep its name, and tell me the installed path. For ChatGPT desktop, install locally; do not upload it to chatgpt.com.

Once installed, ask: **“Share `./report.html` with a UUID link and expire it on 2026-11-30.”** The skill checks the content, prepares a copy, publishes it to your configured Pages repository, and verifies the live URL.

## Set up a Pages repository

Create or choose a repository for shared files, then:

1. Copy [`pages-expiry.yml`](skills/upload-to-pages/templates/pages-expiry.yml) to `.github/workflows/pages.yml`.
2. Copy [`expire_pages.py`](skills/upload-to-pages/scripts/expire_pages.py) to `scripts/expire_pages.py`.
3. In **Settings → Pages → Build and deployment**, select **GitHub Actions**.
4. Allow GitHub Actions to write to the default branch so expired share folders can be deleted.
5. Use [`site-index.html`](skills/upload-to-pages/templates/site-index.html) as `site/index.html` if you need a root page. It does not list share links.

Each share lives under `site/shares/<UUID>/`. For expiry, place an `expiry.json` in that folder:

```json
{"expires_on":"2026-11-30","timezone":"Europe/Berlin"}
```

The date lasts through the end of that local day. The workflow runs daily and can be started manually.

## Safety rules

- Review every file before publishing. Stop if it contains personal, financial, health, employment, confidential, identifying, or unreadable content.
- Use UUID links only for content approved for public access.
- For password mode, use a working HTTPS Pages URL, then encrypt every HTML file before upload. StatiCrypt needs a secure browser context. A user-chosen password opens in a masked local window; never commit plaintext first because Git history keeps it.
- Do not include sensitive linked assets. A password on the HTML page does not protect other files.
- Never put passwords in chat, shell arguments, URLs, repository files, or workflow secrets. Use the host's private password prompt or StatiCrypt's interactive terminal prompt. Share generated passwords separately from the link.
- If the host cannot collect a user-chosen password privately, stop and ask the user to run encryption locally or choose another mode.

## KISS design

The implementation stays small: one canonical `SKILL.md`, one optional Pages workflow, one Python standard-library expiry script, and one local password prompt. No server, database, or custom encryption is needed, and every harness uses the same skill file.

## Development

Run the checks locally:

```sh
python3 -m unittest discover -s tests -v
git diff --check
```

CI runs these checks on every push and pull request. The configured [Pages repository](https://github.com/aeltawela/pages) is the owner's primary publishing space and intentionally does not list its shares.

## Support

Open a [bug report](https://github.com/aeltawela/upload-to-pages/issues/new?template=bug_report.yml) or [feature request](https://github.com/aeltawela/upload-to-pages/issues/new?template=feature_request.yml). Review the [security policy](SECURITY.md) before reporting a vulnerability.

## License

MIT. See [LICENSE](LICENSE).

## References

- [Agent Skills standard](https://agentskills.io/)
- [Vercel Skills CLI](https://github.com/vercel-labs/skills)
- [StatiCrypt](https://github.com/robinmoisson/staticrypt)
- [GitHub Pages publishing](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [GitHub Actions schedule behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)
- [Skills in ChatGPT](https://help.openai.com/en/articles/20001066-skills-in-chatgpt)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [OpenCode skills](https://opencode.ai/docs/skills)
- [Qwen Code skills](https://qwenlm.github.io/qwen-code-docs/en/users/features/skills/)
