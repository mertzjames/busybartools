# Contributing

Thanks for building on busybartools. This page covers how work flows from a branch to a published release. For
toolchain setup and platform details, see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## Branches

| Branch | Role | How it changes |
|---|---|---|
| `main` | **Released code.** Every app release is tagged from here. | Only by pull request from `dev` (or a hotfix branch). Protected: PR plus a passing CI `check` required, no force pushes. |
| `dev` | **Integration.** The next release, kept working at all times. | Only by pull request from work branches. Protected the same way. |
| `<contributor>/<topic>` | **Your work.** One feature, fix, new app or tool per branch. | Branch from `dev`, open a PR back into `dev`. |

Name work branches with your GitHub username and a short, dash-separated topic that says what kind of change it is:

```
alice/feat-snow-scene          a feature in an existing app
alice/fix-clock-rollover       a bug fix
alice/new-app-fireplace        a new app
alice/tool-gif-to-anim         a new or improved tool / shared library
alice/docs-install-guide       documentation only
alice/hotfix-dragon-crash      urgent fix for released code (branches from main; see below)
```

## Workflow

```bash
git switch dev && git pull
git switch -c alice/feat-snow-scene

# ...make changes...
tools/check.sh                  # must pass: builds, typechecks and tests every app
tools/deploy.sh <app>           # try it on a real bar when the change is visible

git add -A && git commit -m "Add a snowfall scene to Wizarding Thanksgiving"
git push -u origin HEAD
gh pr create --base dev --fill  # or open the PR on GitHub
```

Keep a PR to one topic. Rebase on `dev` (or merge `dev` in) if it falls behind. CI must be green before merging.

### Pull request checklist

The PR template repeats this list:

- [ ] `tools/check.sh` passes locally, and CI is green.
- [ ] Visible changes were tried on a real bar (attach a `tools/screens.py` capture or a photo if you can).
- [ ] Regenerated assets are committed (`.anim`, generated TypeScript, mockups).
- [ ] The app's `README.md` is updated, and a `docs/DECISIONS.md` entry covers any meaningful choice.
- [ ] No personal or network details: home IPs, subnets, time zones, local paths, names, photos of homes, tokens.
      Use `<bar-ip>`, and keep real addresses in your git-ignored `.env`.

### Merging

- **Work branch → `dev`:** squash merge, so each topic lands as one clear commit. GitHub deletes the branch.
- **`dev` → `main`:** merge commit, titled "Release: …", so `main`'s history reads as a list of releases.

## Releasing

Each app is versioned independently with [semantic versioning](https://semver.org): `MAJOR.MINOR.PATCH` in
`apps/<app>/app/src/appmeta/manifest.json`. The **Release** workflow turns a version tag into a GitHub Release
with the uploadable `.tgz` attached.

1. **Bump the version in a PR to `dev`.** Change `"version"` in the app's manifest and note the change in the app's
   `docs/DECISIONS.md` or README.
2. **Promote to `main`** with a PR from `dev` to `main` titled `Release: <app> <version>`, and merge it once CI passes.
3. **Tag from `main`:**
   ```bash
   git switch main && git pull
   tools/release.sh <app>        # checks main is clean and current, builds and tests, then pushes <app>-v<version>
   ```
4. The workflow checks that the tag matches the manifest version and is on `main`. It builds from the committed
   assets, runs the app's tests, and publishes **"<App name> <version>"** with `<app-id>-<version>.tgz`, install
   steps and a SHA-256. Watch it with `gh run watch`.

Tags look like `<app-folder>-v<version>`, for example `wizard-thanksgiving-v1.0.0`. Never move or delete a published
tag: bump the version instead.

### Hotfixes

For an urgent fix to released code, branch from `main` (`alice/hotfix-…`), bump the patch version, and open a PR into
`main`. After it merges and is released, merge `main` back into `dev` so the fix isn't lost.

## Commit messages

- Write an imperative summary of 72 characters or fewer ("Fix clock rollover at midnight"), then a blank line and the
  why if it's not obvious.
- Don't put personal details in commit messages either. The repo is public and history is permanent.

## License

By contributing, you agree that your contributions are licensed under the repo's [MIT License](LICENSE). Keep art
original; don't add copyrighted characters, logos or fonts.
