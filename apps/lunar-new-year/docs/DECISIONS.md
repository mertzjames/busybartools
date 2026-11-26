# Decision log — Lunar New Year

What was decided, why, and what else was considered. Newest at the bottom.

---

## D1 — Scenes and cards on the shared show runner
*2026-11-26*

**Decision:** Full-screen 72×16 `.anim` scenes at 15 fps, rendered by a Python `renderer/` on the shared render kit.
Playback is the kit's `createShow()` (`lib/ts/busybar/showrunner.ts`), so `app/src/main.ts` is only configuration:
the scenes, a `clock` card, a `count` card and a `steps(t)` playlist picker.

**Why:** The round-2 playbook asks every holiday app to use the runner instead of its own playback loop. The runner
already does one-request-in-flight drawing, page fades, minute rollovers and a playlist re-pick every cycle.

**Alternatives:** Copying Christmas Day's own loop. It works, but it's a second copy of the same code to maintain.

---

## D2 — Seven festival scenes
*2026-11-26*

**Decision:** Red Lanterns Rising, Dragon Dance, Lion Dance, Red Envelopes, Dumplings Steaming, Firecrackers and a
Fireworks Finale, each 12–16 s. Each one has a small story drawn from the festival's own customs:
- **Lanterns:** the full moon of the Lantern Festival, sky lanterns, and palace lanterns hung for the new year.
- **Dragon dance:** the dragon chases a pearl carried ahead of it, and each hoop of its body has a dancer.
- **Lion dance:** "plucking the greens" (cai qing). The lion takes lettuce and a red envelope hung high, then
  scatters the leaves for luck.
- **Red envelopes:** a child bows with a New Year wish, and a grandparent gives an envelope.
- **Dumplings:** a coin is hidden in one dumpling, a New Year's Eve custom in northern China. Finding it means luck.
- **Firecrackers:** the folklore of the Nian, a beast that fears loud noise and the color red. An original,
  friendly design, never a scary one.
- **Finale:** red-and-gold fireworks and `HAPPY` / `NEW YEAR`.

**Why:** These are the brief's ideas. Each gets a beginning, a middle and a punchline, as the Christmas scenes do.

**Alternatives:** A "spring couplets on the door" scene. It was dropped because couplets need Chinese characters,
and invented strokes would be fake writing. A plain red-envelope rain was dropped for the family moment, which
says more about the custom.

---

## D3 — Sprites as text grids, props procedural
*2026-11-26*

**Decision:** The zodiac animals, the dance dragon's head, the lion's head, the Nian, the lettuce and the dumpling
are text-grid sprites in `renderer/sprites.py`. These are drawn procedurally in `renderer/lnyfx.py`:
- lanterns, rooftops with curled eaves, the pagoda and the firecrackers;
- envelopes, coins and steam;
- the papercut border and the simple figures.

**Why:** Grids are easy to review and tweak (`review.py sprites`). Procedural props scale and recolor freely.

---

## D4 — App-local props instead of kit changes
*2026-11-26*

**Decision:** The red-and-gold palette, lanterns, rooftops and other props live in `renderer/lnyfx.py`. Fireworks,
confetti and glitter come from the kit's `busybar.party`.

**Why:** `lib/` is frozen during parallel work. Lanterns and curled-eave rooftops could be promoted later, if
another app wants them (repo R2).

---

## D5 — Twelve short zodiac scenes
*2026-11-26*

**Decision:**
- **Variants:** one 6 s scene per animal (`zodiac_<animal>.anim`, about 30–43 KiB each, 390 KiB for all twelve).
- **Layout:** the animal arrives on the left of a wine-red stage with a gold papercut border. It does its own move:
  - the rabbit hops, the rooster crows and the monkey waves;
  - the tiger pounces, the horse rears, the goat lowers its horns;
  - the dog wags, the rat twitches its nose, the ox stamps, the pig trots;
  - the snake and the dragon undulate.

  `YEAR OF THE` (tiny) and the name (big) wipe in on the right with a glint.
- **Snake and dragon:** both bodies are drawn along a moving wave rather than as grids. The zodiac dragon reuses
  the dance dragon's head.
- **Goat:** the name is `GOAT`, following the brief and the kit's `ZODIAC` list. 羊 is also translated as sheep
  or ram.

**Why:**
- Short and small: the bar plays only one of the twelve in a year, but all twelve ship so the app never needs an
  update.
- A wave reads as "serpent" at 16 px tall. A grid snake looked like a stick.
- Showing every animal in the same style helps recognizability. Each animal has its colors (orange tiger with lit
  brown stripes, white goat with curled horns and a beard, a front-facing monkey with a curled tail).

**Alternatives:** Baking only the animal and drawing its name as live text. Baking the name lets the wipe and glint
animate, and the card already draws it live.

---

## D6 — Two playlists, picked from the date
*2026-11-26*

**Decision:** `steps(t)` picks one of two playlists (`PLAYLISTS` in `renderer/scenes/__init__.py`, exported into
`show.ts`):
- **countdown** (before the holiday, and outside the date table): Lanterns, clock, zodiac, count, Dragon, clock,
  Envelopes, count, Lion, clock, Dumplings, count, Firecrackers, clock, Finale, count;
- **festival** (New Year's Day through day 15): it opens with the zodiac scene and the greeting card, then the same
  scenes in a different order.

**Why:** The default runner playlist (scene, clock, …) has no countdown. Alternating the clock and count cards
follows the playbook. On the day, opening with the year's animal and `YEAR OF THE GOAT` is the strongest first
impression. Both playlists live in one place, so the app and the mockup can't disagree.

---

## D7 — Card design and the shared text styles
*2026-11-26*

**Decision:**
- **Backdrop:** a deep wine wall, two glowing red lanterns in the top corners (rows 0–7, outer 5 columns),
  plum-blossom sprigs in the bottom corners (outer 2 columns) and faint gold glints.
- **Lines:**
  - `N DAYS` in big gold over `TO LUNAR NEW YEAR` in tiny cream. The tiny line is 64 px; at 95 px, big doesn't fit.
  - `YEAR OF THE` in tiny over the animal in big.
  - Greetings as two big lines: `HAPPY` / `NEW YEAR`, `GONG XI` / `FA CAI`, `LANTERN` / `FESTIVAL`.
- **Clock:** the `clock` font time, then the date in big.
- **One table:** every style (font, y, gradient, shadow) and page length lives in `renderer/textstyle.py`. The
  zodiac captions bake with the same styles. The build tone-maps the colors for `show.ts` and the mockup.

**Why:** Gold on wine with a red shadow is the festival's palette and reads well. The lanterns and blossoms stay
clear of every text box. `tests/text_parity.py` checks that the app's XPM text matches the renderer pixel for pixel,
for every style and all twelve animal names.

**Alternatives:** Paging `LUNAR` / `NEW YEAR` after `N DAYS`. Two lines on one page read faster.

---

## D8 — Tone curve GAMMA = 0.8
*2026-11-26*

**Decision:** Use the curve approved on real hardware for Wizarding Thanksgiving, for frames and for the live-text
colors.

**Why:** It keeps the bar, the mockup and the review strips identical. Re-tuning without a device would be guesswork.

---

## D9 — One script: kit re-exports in app/shared
*2026-11-26*

**Decision:** `app/shared/kit.ts` re-exports the kit modules (text, time, holidays, show runner) by relative path.
`app/shared/lny.ts` holds this app's pure date logic. The build output is `scripts: main.js` only.

**Why:** Every `.ts` under `app/src/` becomes its own script entry, which the firmware can't run (repo AGENTS.md).

---

## D10 — Holiday mode: START walks the zodiac
*2026-11-26*

**Decision:**
- **First START:** turns on holiday mode, the festival playlist and cards with the real season's animal.
- **Each further press:** shows the next animal (Goat, Monkey, Rooster, … Horse), so twelve presses review every
  animal's scene and card.
- **Thirteenth press:** returns to the real date.
- **Applying it:** every press calls `show.start()` again, which re-picks the playlist from the top right away. The
  festival playlist begins with the zodiac scene, so each press shows the new animal at once.

**Why:**
- The playbook asks START to preview the holiday. Stepping through the animals also makes it the review tool for
  all twelve zodiac scenes, with no extra button.
- `start()` is the runner's "new cycle" entry, so no kit change is needed.

**Alternatives:** A separate long-press for the animals. It's harder to discover, and the runner passes long presses
through as "ignored" anyway.

---

## D11 — Season rules and the fallback outside the date table
*2026-11-26*

**Decision:**
- **Span:** the festival lasts 15 days, `spanDays = 15`, from New Year's Day through the Lantern Festival (the 15th
  day of the first lunar month).
- **Animal:** before the new year, the cards and the zodiac scene show the upcoming year's animal: `zodiac(year)`
  of the next occurrence. In January 2027 that's GOAT, not the Horse year still in progress.
- **Outside the table:** the kit's `lunarNewYear` table covers 2025–2036 and returns null outside it. From then
  on, the count card shows only `HAPPY` / `NEW YEAR` with no countdown. The playlist still runs, with the zodiac
  scene of the year in progress.
- **Animal without a table:** Lunar New Year always falls between Jan 21 and Feb 20, so the app uses last year's
  animal until Feb 20 and this year's from Feb 21. Only the four weeks in between can be wrong, and only after
  2036.

**Why:** A countdown to an unknown date would be wrong. A generic greeting is always right. Tests cover Jan and
Feb 2027, day 15 (Feb 20, 2027), the day after, and 2036–2037.

---

## D12 — Respectful figures and an accurate greeting
*2026-11-26*

**Decision:**
- **People:** simple figures. A head is a hair pixel over a skin pixel, with no drawn faces. Clothing color tells
  them apart: the dancers' matching gold and red uniforms, the grandparent's jade jacket and silver bun, the
  child's gold jacket.
- **Greeting:** the romanized greeting is `GONG XI FA CAI` (恭喜发财, Mandarin pinyin without tone marks:
  "wishing you prosperity"), split `GONG XI` / `FA CAI` over two big lines.
- **Tone:** respectful and warm, with no caricature. The Nian is a folklore beast drawn as a round, friendly monster.

**Why:**
- The brief asks for no caricature of people.
- Pinyin is the standard romanization, and the phrase is the most common written New Year greeting.
- The app is named "Lunar New Year", and the main greeting is `HAPPY NEW YEAR`, because the festival is also Tết,
  Seollal and more.

**Alternatives:**
- Cantonese `GUNG HEI FAT CHOI`.
- Vietnamese `CHUC MUNG NAM MOI`.
- Both are open for review.
- The zodiac follows the Chinese list from the kit. The Vietnamese zodiac has the Cat in place of the Rabbit and the
  Buffalo in place of the Ox.

---

## D13 — Keep captions and action apart; contrast fixes from review
*2026-11-26*

**Decision:** Changes made while reviewing LED strips:
- **Finale:** the town and fireworks dim to 45% under `HAPPY` / `NEW YEAR`, and the late bursts move to the
  screen edges.
- **Dumplings:** `LUCKY COIN!` sits on the empty wall to the right. The wall lantern moved left, and the coin is a
  3×3 gold ring with a square hole that pops up-left of the chopsticks.
- **Firecrackers:** the rooftops behind the string are lower and darker, so the crackers stand out.
- **Lion dance:** when the lion rears, its body tilts and the front dancer's legs show longer, instead of filling a
  block. The drummer wears a white shirt so it shows on the dark wall.
- **Tiger:** the stripes are a lit brown, because darker stripes read as holes.

**Why:** Round-1 lessons: dim behind captions, check contrast, and look at every scene, not just the grid text.

---

## D14 — The mockup mirrors the app's logic, and a test keeps them equal
*2026-11-26*

**Decision:** `mockup/template.html` has a `// <logic>` block, a plain-JS copy of `lny.ts` and the kit's Lunar
New Year rule. `tests/logic.test.mts` runs that block and checks it against the app every day from 2024 to 2038,
including the season, the card pages, the playlist and holiday mode. The mockup has a "Bar date" picker and a
holiday-mode button that works like START.

**Why:** Reviewers can see any date's show in the browser, and the copy can't drift silently.

**Alternatives:** New Year's Eve strips TypeScript types to share the exact source. That's more machinery for this
small amount of logic.
