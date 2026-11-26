# AGENTS.md — New Years Eve

App-specific rules for AI coding agents. The repo-wide rules in [/AGENTS.md](../../AGENTS.md) still apply.

- **What it does:** Party scenes, a countdown to midnight, and a celebration when the new year rings in
- **Entry point:** `app/src/main.ts`. Put helpers and generated data in `app/shared/`, never in `app/src/`.
- **Build and test:** `tools/check.sh new-years-eve` from the repo root.
- **Invariants:** <list what must stay true: frame rate, which files are generated, timings, ...>
- **Decisions:** read [docs/DECISIONS.md](docs/DECISIONS.md) before changing deliberate choices.
