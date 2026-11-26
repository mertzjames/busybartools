# AGENTS.md — Kwanzaa

App-specific rules for AI coding agents. The repo-wide rules in [/AGENTS.md](../../AGENTS.md) still apply.

- **What it does:** A kinara that follows the seven days of Kwanzaa, with the principle of the day and harvest, drums and karamu scenes
- **Entry point:** `app/src/main.ts`. Put helpers and generated data in `app/shared/`, never in `app/src/`.
- **Build and test:** `tools/check.sh kwanzaa` from the repo root.
- **Invariants:** <list what must stay true: frame rate, which files are generated, timings, ...>
- **Decisions:** read [docs/DECISIONS.md](docs/DECISIONS.md) before changing deliberate choices.
