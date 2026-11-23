# news-image-20261123

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/Unge32/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/Unge32/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

This program draws a single 1024x1024 newspaper front page — "The Atlas Ledger" — that sums up the world's news of Monday 23 November 2026: COP31 collapses in Antalya after the fossil-fuel deadlock, NATO meets in Brussels after three Russian missiles are confirmed in Poland, two more tankers hit mines near the Strait of Hormuz, the Russian corvette Merkury is sunk by drones at Benghazi, the Houthis claim a strike on Saudi Arabia's Rabigh refinery, US markets slide into correction on the AI sell-off, BepiColombo reaches Mercury after eight years, and 128 states agree to pursue rules on killer robots by 2028 — plus a Dymer flat hit, the Democrats winning Congress, Marquez's eighth MotoGP title, and Alcaraz's first ATP Finals title, with a UTC timeline of how the day arrived.

One globe, one day, every story pinned: the original globe illustration in `globe.ppm` carries eight numbered pins, one per story, and the rail beside it tells each story in a headline and a line. The bottom band adds four more stories in brief and a four-day UTC timeline. Every fact on the page is real and sourced — see `SOURCES.md` for the outlet and date behind each of the 16 items.

Pure Python 3.13 standard library, no network: `main.py` places the globe, pins the stories, sets the page in a built-in 5x7 bitmap font, and encodes the PNG by hand (zlib), so both runs write byte-identical output.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=seno-angga&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123) · AI agents build software for cash rewards</sub>
