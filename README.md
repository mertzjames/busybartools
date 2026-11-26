# busybartools

Custom apps, animations and developer tools for the [BUSY Bar](https://busy.app), the desk and wall display with a
72×16 RGB LED front panel.

<p>
  <img src="apps/wizard-thanksgiving/docs/media/dragon_roast.gif" alt="A winged serpent dragon torches a turkey" width="49%">
  <img src="apps/wizard-thanksgiving/docs/media/owl_post.gif" alt="A snowy owl delivers a Happy Thanksgiving letter" width="49%">
</p>

## Apps

| App | What it does | Get it |
|---|---|---|
| [Wizarding Thanksgiving](apps/wizard-thanksgiving/) | Nine wizard-themed Thanksgiving scenes (owls, broomsticks, a talking hat, a winged serpent dragon, and a feast conjured by an old wizard) with a 24-hour clock and the date between them | [Latest release](https://github.com/mertzjames/busybartools/releases?q=wizard-thanksgiving) |
| [Advent Calendar](apps/advent-calendar/) | A new animation behind every door from Dec 1 to Christmas, with a live countdown to Christmas | [Latest release](https://github.com/mertzjames/busybartools/releases?q=advent-calendar) |
| [Hanukkah](apps/hanukkah/) | A menorah lit for tonight's night (at sunset, or a time you pick in the app's settings), with dreidels, latkes, sufganiyot, gelt and a countdown to Hanukkah | [Latest release](https://github.com/mertzjames/busybartools/releases?q=hanukkah) |
| [Christmas Day](apps/christmas-day/) | Eight little Christmas stories, from trimming the tree to fireworks, with a candy-cane clock and the date between scenes | [Latest release](https://github.com/mertzjames/busybartools/releases?q=christmas-day) |
| [Kwanzaa](apps/kwanzaa/) | A kinara lit for the day, with the day's principle in Swahili and English, plus harvest, unity cup, drums and karamu scenes (the candle order is a setting) | [Latest release](https://github.com/mertzjames/busybartools/releases?q=kwanzaa) |
| [New Year's Eve](apps/new-years-eve/) | Party scenes with a countdown to midnight, huge digits for the last ten seconds, then fireworks and HAPPY NEW YEAR (START runs a demo any day) | [Latest release](https://github.com/mertzjames/busybartools/releases?q=new-years-eve) |
| [MLK Day](apps/mlk-day/) | A quiet tribute: dawn, a march, a dove and a day of service, with a countdown to the day | [Latest release](https://github.com/mertzjames/busybartools/releases?q=mlk-day) |
| [Lunar New Year](apps/lunar-new-year/) | Lanterns, dragon and lion dances, red envelopes and the year's zodiac animal, with a countdown and a greeting in Mandarin, Cantonese, Vietnamese or Korean | [Latest release](https://github.com/mertzjames/busybartools/releases?q=lunar-new-year) |
| [Valentine's Day](apps/valentines-day/) | Sweet scenes with hearts, a cherub, lovebirds, chocolates and a rose, with a countdown | [Latest release](https://github.com/mertzjames/busybartools/releases?q=valentines-day) |
| [Presidents' Day](apps/presidents-day/) | Stars, stripes and landmarks: a flag, a cherry tree, monuments at sunset and fireworks | [Latest release](https://github.com/mertzjames/busybartools/releases?q=presidents-day) |
| [St. Patrick's Day](apps/st-patricks-day/) | Folklore and heritage: a jigging leprechaun, a rainbow to a pot of gold, a shamrock field, a parade and green, white and orange fireworks | [Latest release](https://github.com/mertzjames/busybartools/releases?q=st-patricks-day) |
| [Easter](apps/easter/) | A hopping bunny hides eggs, kids hunt them, chicks hatch and spring flowers bloom, ending with a sunrise and Easter lilies | [Latest release](https://github.com/mertzjames/busybartools/releases?q=easter) |
| [Mother's Day](apps/mothers-day/) | Bouquets, breakfast in bed, a garden, a handmade card and hugs, with a countdown to the day | [Latest release](https://github.com/mertzjames/busybartools/releases?q=mothers-day) |
| [Memorial Day](apps/memorial-day/) | A quiet tribute: the flag at half-staff until noon, the armed services, poppies, a lone bugler, a flyover and the Tomb of the Unknown Soldier | [Latest release](https://github.com/mertzjames/busybartools/releases?q=memorial-day) |
| [Juneteenth](apps/juneteenth/) | From a quiet Galveston dawn and the news of freedom to the Juneteenth flag, a cookout, music and fireworks | [Latest release](https://github.com/mertzjames/busybartools/releases?q=juneteenth) |
| [Father's Day](apps/fathers-day/) | A summer day with Dad: fishing at dawn, playing catch, a first bike ride, the grill, a wild tie and fireworks | [Latest release](https://github.com/mertzjames/busybartools/releases?q=fathers-day) |
| [Independence Day](apps/independence-day/) | A hometown parade, the Liberty Bell, an eagle and flag, sparklers and fireworks, with a countdown to the fireworks on the day | [Latest release](https://github.com/mertzjames/busybartools/releases?q=independence-day) |
| [Labor Day](apps/labor-day/) | A tribute to workers that opens into the end of summer: a crane topping out, a parade of trades, the harvest, a cookout and a beach sunset | [Latest release](https://github.com/mertzjames/busybartools/releases?q=labor-day) |
| [Halloween](apps/halloween/) | Spooky-fun and family-friendly: carved pumpkins, a haunted house in a lightning storm, trick-or-treaters, bats, a witch, a black cat and dancing skeletons | [Latest release](https://github.com/mertzjames/busybartools/releases?q=halloween) |
| [Veterans Day](apps/veterans-day/) | A tribute: flags on Main Street, a parade, the armed services, a salute, poppies and a thank-you, with a quiet card at 11:00 on Nov 11 | [Latest release](https://github.com/mertzjames/busybartools/releases?q=veterans-day) |

More apps and tools will be added over time. Want to build one? See [Adding a new app](docs/DEVELOPMENT.md#adding-a-new-app).

## Install an app

Each app ships as a single `.tgz` file on the [Releases page](https://github.com/mertzjames/busybartools/releases):

1. Download the app's `.tgz` from its release. Don't unpack it.
2. Open your bar's web page: **http://10.0.4.20** over USB, or `http://<bar-ip>` on Wi-Fi.
3. Go to **Apps → + Add app**, choose the file, and click **Install app**.
4. On the bar, open the **Apps** menu and start it.

The full guide, including how to enable the HTTP API over Wi-Fi and fix common problems, is in
[docs/INSTALLING.md](docs/INSTALLING.md).

## Repository layout

```
apps/<app>/          one folder per app: the BUSY JS app (app/), its generators, docs and tests
lib/python/busybar/  shared Python: .anim writer/reader, LED-style previews
tools/               shared scripts: check, deploy, release, new-app, screen capture
docs/                installing, development guide, repo-level decisions
.github/             CI, release automation, PR template
```

## For developers

```bash
python3 -m pip install -r requirements.txt   # Pillow (pinned)
tools/check.sh                               # build, typecheck and test every app (no device needed)
cp .env.example .env                         # set BUSYBAR_ADDR to your bar's IP (or leave unset for USB)
tools/deploy.sh wizard-thanksgiving          # install and launch on your bar
```

- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md): toolchain, app anatomy, adding an app, making `.anim` animations,
  BUSY Bar platform notes and testing on the device.
- [CONTRIBUTING.md](CONTRIBUTING.md): branch model (`main` for releases, `dev` for integration,
  `<you>/<topic>` for work), pull requests and how releases are cut.
- [AGENTS.md](AGENTS.md) and [CLAUDE.md](CLAUDE.md): instructions for AI coding agents (Codex, Cursor, Copilot,
  Claude Code and others) working in this repo.

## License

[MIT](LICENSE). This is an unofficial community project, not affiliated with BUSY / Flipper Devices. Themed apps are
fan projects with original art. See [NOTICE.md](NOTICE.md).
