# MLK Day

A quiet tribute for Martin Luther King Jr. Day: dawn, a march, a dove, many hands and a day of service

## Install

Download `busybartools.mlkday-<version>.tgz` from this app's GitHub Release and upload it to your bar.
See [Installing apps](../../docs/INSTALLING.md).

## Develop

```bash
tools/check.sh mlk-day     # build + typecheck (+ tests/check.sh if present)
tools/deploy.sh mlk-day    # install and launch on the bar in .env
tools/release.sh mlk-day   # (maintainers, on main) tag a release; CI publishes it
```

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
