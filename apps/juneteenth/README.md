# Juneteenth

Juneteenth, from a quiet Galveston dawn to a cookout and fireworks, with a countdown

## Install

Download `busybartools.juneteenth-<version>.tgz` from this app's GitHub Release and upload it to your bar.
See [Installing apps](../../docs/INSTALLING.md).

## Develop

```bash
tools/check.sh juneteenth     # build + typecheck (+ tests/check.sh if present)
tools/deploy.sh juneteenth    # install and launch on the bar in .env
tools/release.sh juneteenth   # (maintainers, on main) tag a release; CI publishes it
```

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
