# Memorial Day

A quiet tribute for Memorial Day: the flag at half-staff, poppies, a lone bugler and a flyover

## Install

Download `busybartools.memorialday-<version>.tgz` from this app's GitHub Release and upload it to your bar.
See [Installing apps](../../docs/INSTALLING.md).

## Develop

```bash
tools/check.sh memorial-day     # build + typecheck (+ tests/check.sh if present)
tools/deploy.sh memorial-day    # install and launch on the bar in .env
tools/release.sh memorial-day   # (maintainers, on main) tag a release; CI publishes it
```

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
