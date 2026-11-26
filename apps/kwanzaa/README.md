# Kwanzaa

A kinara that follows the seven days of Kwanzaa, with the principle of the day and harvest, drums and karamu scenes

## Install

Download `busybartools.kwanzaa-<version>.tgz` from this app's GitHub Release and upload it to your bar.
See [Installing apps](../../docs/INSTALLING.md).

## Develop

```bash
tools/check.sh kwanzaa     # build + typecheck (+ tests/check.sh if present)
tools/deploy.sh kwanzaa    # install and launch on the bar in .env
tools/release.sh kwanzaa   # (maintainers, on main) tag a release; CI publishes it
```

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
