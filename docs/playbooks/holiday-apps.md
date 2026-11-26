# Playbook: holiday apps and the Wizarding Thanksgiving feast update

How we build three new holiday apps and update Wizarding Thanksgiving in parallel, without contributors (human or
AI sub-agents) overwriting each other's work. Read this together with [AGENTS.md](../../AGENTS.md),
[CONTRIBUTING.md](../../CONTRIBUTING.md) and [docs/DEVELOPMENT.md](../DEVELOPMENT.md).

## Goals

| # | Workstream | Folder | App id | Summary |
|---|---|---|---|---|
| W1 | **Advent Calendar** | `apps/advent-calendar/` | `busybartools.advent` | A unique animation for each day, Dec 1–24 (plus a Dec 25 finale), and a countdown to Christmas Day |
| W2 | **Christmas Day** | `apps/christmas-day/` | `busybartools.christmas` | A loop of Christmas scenes with a themed clock and date card between them |
| W3 | **New Year's Eve** | `apps/new-years-eve/` | `busybartools.newyear` | Party scenes with a countdown to midnight, a big final-10-seconds countdown, then a celebration with the new year |
| W4 | **Wizarding Thanksgiving 1.1** | `apps/wizard-thanksgiving/` | `wizard.thanksgiving` | A new "feast appears" scene with all four students; the cast becomes 2 wizards + 2 witches, each visually distinct beyond house colors |

All art is original (see `NOTICE.md`): generic holiday imagery, no licensed characters, logos or fonts.

## Phases and gates

```
Phase 0  Orchestrator            playbook PR ──► dev
                                 shared render kit PR ──► dev   (gate: outputs byte-identical, CI green)
Phase 1  4 sub-agents, parallel  W1 │ W2 │ W3 │ W4   each in its own git worktree + branch
                                 (gate per workstream: tools/check.sh green, LED review strips, mockup built)
Phase 2  Orchestrator            review strips ► publish one review artifact per workstream
                                 push branches ► open 4 PRs into dev (artifact link in each PR)
Phase 3  You                     review artifacts, comment ► orchestrator relays fixes to the same branch
                                 approve ► squash-merge into dev
Phase 4  Orchestrator            catalog/README integration PR, device verification, dev ► main, releases
```

**Approval rule:** scene PRs (Phase 2) stay open until you approve the scenes in the review artifact. Infrastructure
PRs in Phase 0 merge into `dev` once CI is green and outputs are verified unchanged. They change no visuals.

## Branches and file ownership

Ownership is exclusive: a branch may only change the paths listed for it. This is what keeps parallel work
conflict-free.

| Branch | Owner | May change | Must not change |
|---|---|---|---|
| `mertzjames/docs-holiday-playbook` | orchestrator | `docs/playbooks/**` | anything else |
| `mertzjames/tool-shared-render-kit` | orchestrator | `lib/**`, `apps/wizard-thanksgiving/**` (imports only, byte-identical output), `docs/DEVELOPMENT.md`, `docs/DECISIONS.md`, `AGENTS.md` | scenes, sprites, app behavior |
| `mertzjames/new-app-advent-calendar` | sub-agent W1 | `apps/advent-calendar/**` | `lib/`, `tools/`, root docs, other apps |
| `mertzjames/new-app-christmas-day` | sub-agent W2 | `apps/christmas-day/**` | same |
| `mertzjames/new-app-new-years-eve` | sub-agent W3 | `apps/new-years-eve/**` | same |
| `mertzjames/feat-wizard-feast-scene` | sub-agent W4 | `apps/wizard-thanksgiving/**` | same |
| `mertzjames/docs-holiday-catalog` | orchestrator | root `README.md` (Apps table), `docs/DECISIONS.md` | apps |

Rules that follow from this:
- **Shared code is frozen during Phase 1.** If a sub-agent needs something more from `lib/` (a glyph, an effect, a
  helper), it builds an app-local version (for example `font.register_font()` for extra glyphs) and reports it. The
  orchestrator decides whether to promote it later.
- **Root docs are orchestrator-only.** Sub-agents report catalog text (name, one-liner, id); the orchestrator adds the
  rows in one integration PR, so four PRs don't all edit the same table.
- **Isolation:** every sub-agent works in its own git worktree, so working directories, `node_modules` and build
  outputs never collide.
- **No device access in Phase 1.** There's one physical bar. Only the orchestrator deploys or captures screens, and
  only after approval.

## The shared render kit (Phase 0)

Promoted from Wizarding Thanksgiving under R2 ("promote when a second app needs it"), now that four apps need it:

| Module | Contents |
|---|---|
| `lib/python/busybar/canvas.py` | 72×16 RGBA frames, `FPS`, color mixing (half-up rounding), blit/put/add/rect, easing, `phase()` |
| `lib/python/busybar/font.py` | `big` 5×7, `tiny` 3×5 and `clock` 7×12 fonts, `draw_text`, `text_width`, `register_font()` for app-local fonts, `export_json()` |
| `lib/python/busybar/fx.py` | seeded `Stars`, `Particles`, `sparkle`, `puff`, `moon`, `hills`, `bricks`, color sets |
| `lib/python/busybar/sprite.py` | `Sprite` (text-grid pixel art, palettes, `flip`, `recolor`) |
| `lib/python/busybar/showbuild.py` | the build pipeline: tone curve, `.anim` encode and round-trip verify, mockup sprite sheets, GIF previews, generated-TS writer, mockup templating |
| `lib/python/busybar/anim.py`, `preview.py` | unchanged: `.anim` writer/reader, LED-style previews |
| `lib/ts/busybar/xpmtext.ts` | pixel-font text → XPM2 bitmap (gradient + shadow), `textWidth` |
| `lib/ts/busybar/walltime.ts` | parse the bar's local ISO timestamp; seconds to midnight; days to a date; minute rollover |
| `lib/ts/busybar/drawqueue.ts` | one-request-in-flight draw queue with per-slot replacement |

Apps import the TypeScript by relative path from `app/shared/` (for example `../../../../lib/ts/busybar/xpmtext`).
Files outside `app/src/` are bundled into `main.js`, so the build still emits a single script.

## Workstream specs

### Common to every workstream

- Follow the Wizarding Thanksgiving pattern:
  - a Python `renderer/` produces full-screen 72×16 `.anim` scenes at 15 fps, the generated `app/shared/generated/show.ts`, icons and a self-contained `mockup/index.html` (LED simulator + storyboards);
  - `app/src/main.ts` sequences scenes and live text cards;
  - `tests/check.sh` runs at least one parity or logic test.
- Required files: `README.md`, `docs/DECISIONS.md` (D1…), `AGENTS.md` + `CLAUDE.md`, `prebuild.sh`. Scaffold with
  `tools/new-app.sh`.
- Pixel-art rules:
  - lit colors for small features (black is an unlit LED);
  - review every scene as LED-style strips before reporting;
  - deterministic seeded randomness, so CI renders byte-identical files;
  - the tone curve applies at build time.
- Live text (times, countdowns, years) is drawn by the app as XPM bitmaps from the shared fonts, using the bar's
  `/api/time`. It must match the mockup pixel-for-pixel (parity test).
- Package size: keep each app under about 4 MB of `.anim` data.
- Version `1.0.0` for new apps. Wizarding Thanksgiving goes to `1.1.0`.

### W1 Advent Calendar

- **The loop:**
  1. A "door opens" intro showing the date (`DEC 7`).
  2. Today's unique animation, about 8–10 s.
  3. A countdown card (`18 DAYS` / `TO CHRISTMAS`). On Dec 24 it shows hours and minutes. On Dec 25 it shows the
     finale and `MERRY CHRISTMAS`.
  4. Repeat.
- **Out of season:** before Dec 1, it counts down to the start of Advent. After Dec 25, it loops the finale.
- **Controls:** the encoder browses already-opened days, and OK returns to today.
- 24 distinct daily vignettes plus the finale, all original: tree, wreath, candles, snowman, gingerbread, reindeer,
  sleigh, stockings, presents, ornaments, cocoa, penguin, polar bear, toy soldier, candy cane, snowflakes, bells,
  carolers, cookies and milk, sledding, and so on.

### W2 Christmas Day

- About 8 scenes of 14–18 s each, plus a Christmas clock and date card after each. Mirrors Wizarding Thanksgiving.
- Scene ideas: a sleigh across the moon, opening presents, building a snowman, decorating the tree with a star on
  top, a toy train around the tree, stockings by the fireplace, carolers in the snow, and a `MERRY CHRISTMAS` finale.

### W3 New Year's Eve

- **Before the final minute:** party scenes alternate with a countdown card to the bar's next local midnight
  (`HH:MM:SS`, or `MM:SS` in the last hour, plus `TO 2027`, with the year computed live).
- **Last 60 s:** a dedicated countdown. **Last 10 s:** huge digits, one per second, aligned to the bar clock.
- **At 00:00:** fireworks, `HAPPY NEW YEAR` and the year, drawn live. Then a celebration loop with the clock.
- **Testing:** a demo mode (START button) jumps to T-15 s, so the countdown can be tested and reviewed without
  waiting for midnight. The mockup has the same control.

### W4 Wizarding Thanksgiving 1.1

- **New scene, "The Feast Appears":** the four students sit at the long table, raise their wands, and the dishes
  appear one by one (turkey, pies, potatoes, gravy, goblets) with sparkles. Then a cheer and a caption.
- **Cast:** 2 wizards + 2 witches, each with distinct hair, build or accessories in addition to their house colors.
  Keep each student's house from D19, and convert one wizard to a witch.
- Update every scene that shows a student. Update the playlist, README, mockup facts and decision log (D27+), and
  bump the manifest to `1.1.0`.
- Keep the clock parity test green.

## Sub-agent brief template

Each sub-agent gets:
- its workstream spec;
- the ownership rules above;
- the shared-kit API and the platform facts from `AGENTS.md`;
- the branch name and commit rules: no personal details or session links, and a `Co-Authored-By` trailer;
- a definition of done.

It reports back:
- the branch and commit list;
- `tools/check.sh` output;
- paths to its LED review strips and `mockup/index.html`;
- catalog text (name, one-liner);
- **discoveries:** anything learned that other workstreams should know, which the orchestrator relays;
- open questions.

## Review and approval

- The orchestrator views every review strip before publishing anything.
- Each workstream gets a **review artifact**: its `mockup/index.html` (simulator + storyboards), published separately.
  W4's review copy is published as a new artifact, so the already-shared showcase page doesn't change before you
  approve.
- PR descriptions link the artifact and list the scenes. Feedback, whether as artifact comments or in chat, is applied
  on the same branch, and the artifact is republished at the same URL.
- After approval: squash-merge into `dev`, then the catalog PR, verification on the bar, promote `dev` → `main`, and
  `tools/release.sh` for each app.

## Risks

| Risk | Mitigation |
|---|---|
| Parallel edits to shared files | Exclusive path ownership; shared code frozen during Phase 1; orchestrator-only root docs |
| Midnight and Christmas logic is hard to test | Logic in pure TS functions with unit tests (`tests/`), demo mode, mockup time controls |
| Package size (W1 has 25 animations) | Short vignettes, static backgrounds (delta frames are cheap), size reported by the build |
| Timezone mistakes | Only the bar's `/api/time` local fields are used; never JS `Date` local methods |
| Visual quality drift between agents | Shared kit, shared fonts and palette guidance; the orchestrator reviews every strip |
