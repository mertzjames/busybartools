# Playbook: holiday apps, round 2 (a year of holidays)

Sixteen more holiday apps are built in four waves, soonest holiday first, by parallel contributors (human or AI
sub-agents) who never overwrite each other's work. This round reuses the process, ownership rules and review flow of
[round 1](holiday-apps.md). Read that first, along with [AGENTS.md](../../AGENTS.md) and
[docs/DEVELOPMENT.md](../DEVELOPMENT.md). This page covers only what is new or different.

## The waves

Dates are the next occurrence from late November 2026.

| Wave | # | App | Folder | App id | Next date |
|---|---|---|---|---|---|
| A | A1 | Hanukkah | `apps/hanukkah/` | `busybartools.hanukkah` | Dec 4–12, 2026 |
| A | A2 | Kwanzaa | `apps/kwanzaa/` | `busybartools.kwanzaa` | Dec 26 – Jan 1 |
| A | A3 | MLK Day | `apps/mlk-day/` | `busybartools.mlkday` | Jan 18, 2027 |
| A | A4 | Lunar New Year | `apps/lunar-new-year/` | `busybartools.lunarnewyear` | Feb 6, 2027 |
| B | B1 | Valentine's Day | `apps/valentines-day/` | `busybartools.valentines` | Feb 14 |
| B | B2 | Presidents' Day | `apps/presidents-day/` | `busybartools.presidents` | Feb 15, 2027 |
| B | B3 | St. Patrick's Day | `apps/st-patricks-day/` | `busybartools.stpatricks` | Mar 17 |
| B | B4 | Easter | `apps/easter/` | `busybartools.easter` | Mar 28, 2027 |
| C | C1 | Mother's Day | `apps/mothers-day/` | `busybartools.mothersday` | May 9, 2027 |
| C | C2 | Memorial Day | `apps/memorial-day/` | `busybartools.memorialday` | May 31, 2027 |
| C | C3 | Juneteenth | `apps/juneteenth/` | `busybartools.juneteenth` | Jun 19 |
| C | C4 | Father's Day | `apps/fathers-day/` | `busybartools.fathersday` | Jun 20, 2027 |
| D | D1 | Independence Day | `apps/independence-day/` | `busybartools.july4` | Jul 4 |
| D | D2 | Labor Day | `apps/labor-day/` | `busybartools.laborday` | Sep 6, 2027 |
| D | D3 | Halloween | `apps/halloween/` | `busybartools.halloween` | Oct 31 |
| D | D4 | Veterans Day | `apps/veterans-day/` | `busybartools.veteransday` | Nov 11 |

Left out on purpose: minor observances (Groundhog Day, April Fools' Day, Earth Day, Cinco de Mayo), and Diwali,
whose date needs its own table. Any of them can be added later with this playbook.

## Phases and gates

```
Phase 0  Orchestrator            kit PR (R10: holidays.ts, showrunner.ts, party.py) + this playbook ──► dev
Phase 1  per wave: 4 sub-agents   one worktree + branch each; gate: tools/check.sh green, review strips, mockup
Phase 2  Orchestrator            look at every strip ► one review artifact per app ► one PR per app into dev
Phase 3  You                     review, comment ► fixes on the same branch ► approve
Phase 4  Orchestrator            squash-merge ► catalog PR ► verify on the bar ► dev ► main ► releases
```

- **Waves overlap.** The next wave's agents start as soon as the previous wave's agents report back, while you
  review. At most four app agents work at once.
- **Release per wave.** The soonest holidays ship first. Hanukkah starts Dec 4, so wave A is the priority.
- **Approval rule (unchanged):** an app PR stays open until you approve its scenes.

## Ownership (unchanged rules, new names)

| Branch | Owner | May change |
|---|---|---|
| `mertzjames/new-app-<folder>` | that app's sub-agent | `apps/<folder>/**` only |
| `mertzjames/docs-holiday-catalog-<wave>` | orchestrator | root `README.md` Apps table, `docs/DECISIONS.md` |
| kit or tool fixes | orchestrator | `lib/**`, `tools/**`, root docs, in their own PRs |

`lib/`, `tools/`, root docs and CI are frozen for sub-agents. Agents report kit ideas as discoveries; they don't
edit shared files.

## Common spec (every app)

**Structure.** Scaffold with `tools/new-app.sh`. Copy the shape of `apps/christmas-day/`:
- `renderer/` holds `build.py`, `review.py`, `sprites.py`, and `scenes/` with a `PLAYLIST` and card backdrops;
- `app/shared/` holds the device client, kit re-exports and the generated `show.ts`;
- `mockup/template.html` is the LED simulator and storyboards;
- `tests/check.sh` runs the parity test and the logic tests.

**Playback uses the kit runner** (`lib/ts/busybar/showrunner.ts`). Don't write a new playback loop.
- `main.ts` is configuration: scenes from the generated `show.ts`, plus at least two cards:
  - **`clock`**: the time (`clock` font) and then the date;
  - **`count`**: before the holiday, `18 DAYS` / `TO HANUKKAH`; on the day, a greeting such as `HAPPY` / `HANUKKAH`
    (or the day's own card, see the specs below); after it, the count to the next one.
- The default playlist alternates `scene, clock, scene, count, …`.
- Use `steps(t)` when the show depends on the date (Hanukkah's candles, Kwanzaa's principle of the day, Memorial
  Day's half-staff until noon).

**Dates come from the kit** (`lib/ts/busybar/holidays.ts`): `nextOccurrence(t, HOLIDAYS.<key>, spanDays)` and
`daysLabel`. Never hard-code a year.

**Holiday mode for review.** START toggles a preview of the holiday itself (the on-the-day cards and playlist) on
any date, so you can review it without waiting. Press it again to go back. The mockup has the same toggle.

**Scenes:**
- Five to eight scenes of 12–18 s, plus card backdrops. Total `.anim` data under about 3 MB.
- 15 fps, deterministic, `GAMMA = 0.8`, original art only.
- Use `busybar.party` for fireworks, confetti, snow and glitter.

**Live text and parity:**
- Card text must match the mockup and the Python renderer pixel for pixel. Add a parity test, as
  `apps/christmas-day/tests/clock_parity.py` does.
- Test app logic that depends on the date (which playlist, which card text) with `node --test`, against the dates
  in the spec.

**Docs:** `README.md` (scenes, cards, controls), `docs/DECISIONS.md` (D1…), `AGENTS.md` and `CLAUDE.md`. Use
version `1.0.0`.

### Tone and respect

Four of these days honor sacrifice or a civil-rights struggle: **MLK Day, Memorial Day, Juneteenth and Veterans
Day**. Treat them as tributes:
- slow pacing and calm color;
- no confetti, no jokes, no party horns. Juneteenth may end in celebration, which is how it is observed;
- **no likenesses of real people.** Use silhouettes, symbols and places;
- **no long quotations.** The King estate enforces copyright on Dr. King's speeches. Short words like `DREAM` or
  `EQUALITY`, or the MLK Day of Service motto, are fine;
- **no official insignia.** Service-branch seals and emblems are protected; use flags, poppies, salutes and
  generic uniforms.

Religious and cultural holidays (Hanukkah, Kwanzaa, Lunar New Year, Easter) use their own symbols correctly: candle
counts and order, colors and greetings. Keep them warm and celebratory, without caricature.

## App specs

Scene lists are starting points: the agent proposes the final list in its review artifact.

### Wave A

**A1 Hanukkah** (span 9 calendar days from the first evening).
- **The menorah scene follows tonight's count.** Pre-render nine variants: 0–8 candles plus the shamash.
  `steps(t)` picks tonight's from the date. Treat 17:00 local as sundown and record that choice in D-notes.
  - Candles are added from right to left and lit from left to right (newest first). The shamash is raised or set
    apart.
- Other scenes: spinning dreidel (the letters can be simplified shapes), latkes in a sizzling pan, sufganiyot
  with powdered sugar, a gelt coin cascade, a menorah glowing in a snowy window, and a blue-and-silver finale.
- **Cards:**
  - before: `N DAYS` / `TO HANUKKAH`;
  - during: `NIGHT 3` / `HAPPY HANUKKAH`, or `CHAG SAMEACH`;
  - after: the count to next year.

**A2 Kwanzaa** (span 7 days, Dec 26 – Jan 1).
- **The kinara:** three red candles on the left, one black in the middle and three green on the right.
  - Day 1 lights the black candle. Later days add red and green candles alternately, starting with red. Which
    end the lighting starts from varies between sources: follow the official Kwanzaa website and record the choice
    in the D-notes.
  - Pre-render seven lit states, and `steps(t)` picks the day's.
  - **Black is an unlit LED:** draw the black candle as a lit charcoal with a highlight.
- **Principle of the day card:** the Swahili word (`big` font, up to 12 characters, so `KUJICHAGULIA` just fits)
  over the English (`tiny`). The seven are Umoja (unity), Kujichagulia (self-determination), Ujima (collective
  work and responsibility), Ujamaa (cooperative economics), Nia (purpose), Kuumba (creativity) and Imani (faith).
- Scenes: lighting the kinara, the harvest basket (mazao and corn), the unity cup, drums and dance, a kente-pattern
  weave, and the karamu feast (Dec 31).
- **Cards:** before: `N DAYS` / `TO KWANZAA`; during: the principle card and `HABARI GANI?`.

**A3 MLK Day** (tribute; third Monday of January).
- Scenes: sunrise over a long march of varied silhouettes, a dove over a city, many hands joining, a day of
  service (planting a tree, a food drive, painting a mural), freedom bells ringing, and a dawn on a mountaintop.
- **Cards:**
  - before: `N DAYS` / `TO MLK DAY`;
  - on the day: `MLK DAY`, then words such as `DREAM`, `EQUALITY`, `SERVICE`, and `A DAY ON` / `NOT A DAY OFF`.

**A4 Lunar New Year** (table-based date; `zodiac(year)`).
- **The zodiac scene:** pre-render a short scene for each of the 12 animals (5–6 s, small). `steps(t)` picks the
  year's animal.
- Other scenes: a dragon dance, a lion dance, red lanterns rising, firecrackers (`busybar.party`), red envelopes,
  dumplings, and a fireworks finale.
- **Cards:**
  - before: `N DAYS` / `TO LUNAR NEW YEAR`, which may need `tiny` or two lines;
  - on the day and through the Lantern Festival (15 days): `YEAR OF THE` / `GOAT`.
- **If the date table runs out:** cards fall back to a generic `HAPPY NEW YEAR` with no countdown.

### Wave B

- **B1 Valentine's Day:** floating hearts, a generic cherub with a bow, a love letter delivered, two birds on a wire,
  a box of chocolates, a rose blooming.
- **B2 Presidents' Day:** light and patriotic, with no faces. A stovepipe hat and log cabin, a cherry tree, a
  monument skyline, a bald eagle, a waving flag.
- **B3 St. Patrick's Day:** a folklore leprechaun (green coat, buckled hat), a rainbow to a pot of gold, a shamrock
  field, a parade with bagpipes, a river dyed green, Celtic knots.
- **B4 Easter:** a bunny hopping through an egg hunt, chicks hatching, painting eggs, spring flowers opening, a
  basket. The date comes from `HOLIDAYS.easter`.

### Wave C

- **C1 Mother's Day:** a bouquet assembling, breakfast in bed, a parent and child gardening, a handmade card.
- **C2 Memorial Day (tribute):**
  - the flag at half-staff until noon on the day, then full staff (`steps(t)`), following the custom;
  - poppies, rows of white headstones with small flags, a lone bugler at dusk, a respectful flyover.
- **C3 Juneteenth:**
  - **opens solemn:** dawn over Galveston Bay, and the news arriving (`JUNE 19, 1865`);
  - **then joyful:** the Juneteenth flag (star and burst), a family cookout, red drinks, music, and fireworks.
- **C4 Father's Day:** a grill, fishing at dawn, playing catch, a tie as a gift.

### Wave D

- **D1 Independence Day:** fireworks over a skyline (`busybar.party`), a parade, a cookout, sparklers, the Liberty
  Bell, an eagle. On Jul 4, the count is to dusk (21:00): `FIREWORKS IN` / `HH:MM`.
- **D2 Labor Day:** a tribute to workers building a skyline, then the end of summer: a cookout, a last swim, a beach
  sunset.
- **D3 Halloween:** jack-o'-lanterns carved and lit, a haunted house with lit windows, bats across the moon,
  trick-or-treaters, a classic Halloween witch on a broom, a ghost, a skeleton dance, a black cat.
  - **Black is unlit:** draw the cat in deep violet-grey with lit eyes.
  - Cards: `N NIGHTS` / `TO HALLOWEEN`.
- **D4 Veterans Day (tribute):** flags along a street, a salute, poppies, and branch-neutral uniforms (no
  insignia). At 11:00 on Nov 11, the 11th hour of the 11th day, show a quiet moment card. `THANK YOU` / `VETERANS`.

## Sub-agent brief and report

The brief is the same as round 1: the app spec, the common spec, the ownership rules, the platform facts, the branch
name and commit rules (no personal details or session links, and a `Co-Authored-By` trailer), and the definition of
done. Every agent also gets the **discoveries so far** from the agents before it.

The report is also the same: the branch and commits, `tools/check.sh` output, review strip paths, the
`mockup/index.html` path, catalog text, discoveries, and open questions.

## Risks (new in this round)

| Risk | Mitigation |
|---|---|
| Hanukkah starts in 8 days | Wave A first; Hanukkah is reviewed and released as soon as it's ready, without waiting for the rest of its wave |
| Moving dates (Easter, Hanukkah, floating Mondays, Lunar New Year) | Kit rules with tests against published dates (R10); apps never hard-code a year |
| Insensitive treatment of tributes or faiths | Tone rules above; you review every scene before merge |
| Sixteen apps drifting apart in quality | The shared runner, effects and fonts; the orchestrator views every strip; discoveries relayed between waves |
| Black candles, black cats, black flags | Lit dark colors with highlights (AGENTS.md: black is an unlit LED) |
