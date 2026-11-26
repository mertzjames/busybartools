# Hanukkah

A menorah that follows tonight's candle count, with dreidels, latkes, gelt and a countdown to Hanukkah

## Install

Download `busybartools.hanukkah-<version>.tgz` from this app's GitHub Release and upload it to your bar.
See [Installing apps](../../docs/INSTALLING.md).

## Develop

```bash
tools/check.sh hanukkah     # build + typecheck (+ tests/check.sh if present)
tools/deploy.sh hanukkah    # install and launch on the bar in .env
tools/release.sh hanukkah   # (maintainers, on main) tag a release; CI publishes it
```

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
