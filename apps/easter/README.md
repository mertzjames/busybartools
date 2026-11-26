# Easter

A springtime Easter show: a hopping bunny, an egg hunt, hatching chicks and spring flowers

## Install

Download `busybartools.easter-<version>.tgz` from this app's GitHub Release and upload it to your bar.
See [Installing apps](../../docs/INSTALLING.md).

## Develop

```bash
tools/check.sh easter     # build + typecheck (+ tests/check.sh if present)
tools/deploy.sh easter    # install and launch on the bar in .env
tools/release.sh easter   # (maintainers, on main) tag a release; CI publishes it
```

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
