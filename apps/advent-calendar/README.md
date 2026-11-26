# Advent Calendar

A unique animation for every day of Advent, with a countdown to Christmas

## Install

Download `busybartools.advent-<version>.tgz` from this app's GitHub Release and upload it to your bar.
See [Installing apps](../../docs/INSTALLING.md).

## Develop

```bash
tools/check.sh advent-calendar     # build + typecheck (+ tests/check.sh if present)
tools/deploy.sh advent-calendar    # install and launch on the bar in .env
tools/release.sh advent-calendar   # (maintainers, on main) tag a release; CI publishes it
```

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
