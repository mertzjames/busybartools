# St. Patrick's Day

St. Patrick's Day folklore: a jigging leprechaun, a rainbow to gold, shamrocks, a parade and green fireworks

## Install

Download `busybartools.stpatricks-<version>.tgz` from this app's GitHub Release and upload it to your bar.
See [Installing apps](../../docs/INSTALLING.md).

## Develop

```bash
tools/check.sh st-patricks-day     # build + typecheck (+ tests/check.sh if present)
tools/deploy.sh st-patricks-day    # install and launch on the bar in .env
tools/release.sh st-patricks-day   # (maintainers, on main) tag a release; CI publishes it
```

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
