# CLAUDE.md

Project instructions for Claude Code. The shared rules for every AI agent live in AGENTS.md and are imported here:

@AGENTS.md

## Claude Code specifics

- **Plan first for anything non-trivial.** That means a new app, a new scene, or a change to `tools/`, `lib/` or CI.
  Explore the relevant `apps/<app>/docs/DECISIONS.md` before proposing changes: it records what was tried and why.
- **Look at pixel art before shipping it.** Render LED-style previews to a scratch directory and view them. For
  example, `python3 apps/wizard-thanksgiving/renderer/review.py scene <scene> <out_dir> 1.5`, or
  `busybar.preview.led(frame, cell=10)` for any frame. Iterate on what you see, not on the grid text.
- **The device is a shared, physical screen.** Only run `tools/deploy.sh`, POST to `http://<bar>/api/...` or
  simulate input when the user asks. Reading is fine once they have (`/api/version`, `/api/screen`,
  `tools/screens.py`).
- **Network access.** Deploys and screen captures reach the bar on the local network and fetch Node 24 with `npx`.
  If a sandbox blocks LAN or npm access, say so; don't work around it silently.
- **Git:**
  - branch from `dev` as `<github-username>/<topic>`, and open PRs with `gh pr create --base dev`;
  - never push to `main` or `dev`, force-push, or create tags or releases unless asked;
  - commit messages may carry a `Co-Authored-By:` trailer, but **no session links or personal details**
    (the repo is public).
- **Keep the decision logs current.** When you make a meaningful choice, append an entry to the app's
  `docs/DECISIONS.md` (or the repo's `docs/DECISIONS.md` for repo-wide choices) in the same PR.
- **Before you say a change is done,** run `tools/check.sh` and report its result. If it fails, say so and show the
  failing output.
