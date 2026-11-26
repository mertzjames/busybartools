# Veterans Day

A tribute for Veterans Day: flags on Main Street, a parade, a salute, poppies and a thank-you

## Install

Download `busybartools.veteransday-<version>.tgz` from this app's GitHub Release and upload it to your bar.
See [Installing apps](../../docs/INSTALLING.md).

## Develop

```bash
tools/check.sh veterans-day     # build + typecheck (+ tests/check.sh if present)
tools/deploy.sh veterans-day    # install and launch on the bar in .env
tools/release.sh veterans-day   # (maintainers, on main) tag a release; CI publishes it
```

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
