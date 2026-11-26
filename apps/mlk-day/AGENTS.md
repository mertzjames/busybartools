# AGENTS.md — MLK Day

App-specific rules for AI coding agents. The repo-wide rules in [/AGENTS.md](../../AGENTS.md) still apply.

- **What it does:** A quiet tribute for Martin Luther King Jr. Day: dawn, a march, a dove, many hands and a day of service
- **Entry point:** `app/src/main.ts`. Put helpers and generated data in `app/shared/`, never in `app/src/`.
- **Build and test:** `tools/check.sh mlk-day` from the repo root.
- **Invariants:** <list what must stay true: frame rate, which files are generated, timings, ...>
- **Decisions:** read [docs/DECISIONS.md](docs/DECISIONS.md) before changing deliberate choices.
