# Independence Day

Fireworks, a parade, a cookout and a dusk countdown to the fireworks for the Fourth of July

## Install

Download `busybartools.july4-<version>.tgz` from this app's GitHub Release and upload it to your bar.
See [Installing apps](../../docs/INSTALLING.md).

## Develop

```bash
tools/check.sh independence-day     # build + typecheck (+ tests/check.sh if present)
tools/deploy.sh independence-day    # install and launch on the bar in .env
tools/release.sh independence-day   # (maintainers, on main) tag a release; CI publishes it
```

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
