---
name: upload-to-pages
description: Use when someone wants to share existing reports, data exports, HTML pages, or static files through GitHub Pages with a random link, password-protected HTML, or an expiry date.
license: MIT
---

# Upload to Pages

## Principle

Keep it simple: one share repository, one random folder per share, one daily expiry workflow, and one small cleanup script. Keep one canonical skill for every host. Do not add a server, database, custom encryption, or host-specific variants.

GitHub Pages serves public content. A UUID link is unlisted, not private. Use UUID-only links for content approved for public access. A private source repository does not by itself make its Pages site private.

## Before publishing

1. Share only files the user already supplied or created. Do not generate or convert reports.
2. Check filenames and readable contents for personal, financial, health, employment, business-confidential, credential, and identifying information. If anything is sensitive or unreadable, pause and explain the exposure before publishing. Never use UUID-only sharing for sensitive content.
3. Password protection is for HTML only. StatiCrypt encrypts HTML; non-HTML files are copied unchanged. Do not upload sensitive CSV, PDF, image, or other assets. Check external scripts and assets; pause and ask whether to embed them or allow them to remain public.
4. Treat the skill repository and the share repository as separate. Use a configured default share repository when the host provides one; accept a per-share repository override. If no target is configured, ask for `OWNER/REPO`.
5. Use the connected GitHub connector/plugin for operations it supports. Use authenticated `gh` for missing operations, including repository creation or Pages settings. If neither is available, stop and explain what is needed.

## Share a page

1. Confirm the chosen mode: UUID-only for non-sensitive content, or StatiCrypt for HTML. If the user requests an expiry date, make sure the target repository has the workflow and script from `templates/pages-expiry.yml` and `scripts/expire_pages.py`. Configure Pages to publish with GitHub Actions.
2. Work on a copy in a temporary staging folder. Keep plaintext out of the GitHub repository. Create `site/shares/<UUID>/` using a cryptographically random UUID. Do not make a public index of share folders; use `templates/site-index.html` only when the site has no root page.
3. For an HTML page with an expiry, add a visible “Available until YYYY-MM-DD (TIMEZONE)” notice to the staged copy. Leave the user's original untouched. If a safe insertion point is unclear, pause and ask.
4. For password mode, require a working HTTPS Pages URL before publishing. StatiCrypt v3 uses WebCrypto, which needs a secure browser context; if the Pages URL is HTTP or its certificate is not ready, stop and explain. Encrypt every HTML file before upload with StatiCrypt. Review every non-HTML asset because it stays readable. If the user chose their own password, open a masked local window with this skill's `scripts/prompt_password.py`; use hidden terminal input only when a window is unavailable. Pass the result to StatiCrypt through a temporary environment variable using shell command substitution, never as a command-line argument. Never ask for a password in chat or put it in a URL, repository file, or workflow secret. If the host cannot collect it privately, ask the user to run encryption locally or choose another mode. A generated password must come from a cryptographic random source; give it to the owner once, separately from the URL, to share out of band.
5. If an expiry is requested, add a public `expiry.json` beside the page with only:

   ```json
   {"expires_on":"YYYY-MM-DD","timezone":"Area/Location"}
   ```

   The expiry date lasts through the end of that local date. The daily workflow removes the whole share folder after that date, commits the deletion, and redeploys Pages. Non-HTML files stay byte-for-byte unchanged; include their expiry in the share details.
6. Publish the staged files. Wait for a successful Pages workflow and verify the exact page URL before returning it. Use the deployment's Pages base URL plus the share path; do not guess the repository URL or claim success from a commit alone.

## Expiry limits

GitHub Pages has no built-in per-page expiry. The supplied workflow runs daily at 04:17 UTC and can also be started manually. GitHub may delay or drop scheduled runs, and can disable schedules for inactive public repositories. The page may remain available until the next successful run. Deleting it from the current site does not remove Git history, cached copies, downloads, or copies of the link. Expiry is cleanup, not access control.

## Common mistakes

- Publishing sensitive content because it is “only a UUID link.”
- Encrypting HTML but leaving linked data files or scripts public.
- Committing plaintext before encrypting it; history keeps old commits.
- Promising that a date immediately revokes access or deletes downloaded copies.
- Using a guessed Pages URL instead of verifying the deployment result.
