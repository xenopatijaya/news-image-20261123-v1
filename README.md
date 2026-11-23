# The World in One Day — Monday 23 November 2026

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/xenopatijaya/news-image-20261123-v1/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/xenopatijaya/news-image-20261123-v1/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

**Sum up 23 November's world news in one image** — a make.fun bounty
([news-image-20261123](https://make.fun/c/news-image-20261123), $100, top 50).

## The image

`entry.png` (1024×1024) is a broadsheet of **30 date-checked stories across
5 regions** (Europe 9, South Asia 6, Asia-Pacific 4, Oceania 7, Americas 4),
every one dated to Monday 23 November 2026 at its source. No Middle East or
African story could be verified as Monday news, so none is printed — the page
carries five regions honestly rather than padding with weekend stories.

- Giant serif date masthead, red top-3 deck, big-numbers strip, segmented
  region tally, UTC timeline, 3 large illustrated leads with certainty tags
  (REPORTED / CLAIM) and named sources, 10 illustrated cards, a numbered
  pin map, numbered briefs with source tags, and a red **DATE CHECK** box.
- The three leads: Nepal–India talks in Delhi, the NATO council meeting on
  Poland's airspace, and the resumed search at the Cikande candy factory.

## How it was built

`draw.py` renders the image with Pillow (standard library + PIL, no network,
no randomness, no clock reads — two runs of the same file are byte-identical).
`main.py` copies the bundled `entry.png` to the output directory.

## Fact audit

Every story was verified live against its source on the morning of 23 Nov
2026. The day's headlines were mostly weekend news in disguise, so the
following were **deliberately left out** and are named in the image's DATE
CHECK box (real day in brackets):

COP31 collapsed with no pact (Sun) · Democrats clinch 258 House seats (Sun) ·
Russian corvette Merkury sunk at Benghazi (Sun) · Sparta II towed out of
Finnish waters (Sun) · Hong Kong Election Committee vote (Sun) · Korea's
education minister quits (Sun) · UKMTO Chabahar tanker incident (Sun) · WHO
Congo Ebola warning (Sun) · Saudi–Houthi exchange (Sun) · UN
lethal-autonomous-weapons talks end (Sat) · Australia's AUKUS rebuke (Sun) ·
Warrap cattle-camp raid (Sat night) · Kota pilgrim crash (Sat night) · Ohio
baby-shower shooting (Sat) · Delta Atlanta glitch (Sun) · Tom Jackson died
(Fri, announced Sun) · Anupama's snooker title (Sat) · Liverpool–Man Utd
(Sun) · Verstappen wins Las Vegas GP (Sat) · Miley Cyrus wedding (Sat) · FBI
database breach confirmed (Sat) · 'El Chapo Isidro' captured (Fri) · Bayelsa
boat capsized (Fri) · Peru M6.7 quake (Fri) · Khasab tanker hits (Sat) · EU
budget proposal (Sat) · Poland rapper-plot reveal (Sun) · Eisenkot condemns
settler attacks (Sun) · Bahrain: 2 hurt in Saturday strikes (Sun) · Lisbon
cost-of-living march (Sun).

A second audit wave caught more weekend stories dressed as Monday news and
they were rebuilt out of the page: Myanmar–ASEAN rebuke (Sat) · Pakistan FM's
US–Iran interview (Sat) · UK–Ukraine drone deal signed (Sat) · Amit Shah's
Arunachal push (Sun) · Tata Steel–APL Apollo deal (Sun) · BJP MP Wadkute's
death (Sat; his lying-in-state on Monday is covered) · IFFI BRICS roundtable
(Sun) · Yemen's 149-claim (Sat) · Araghchi's uranium interview (Fri) ·
COP32 Addis Ababa priorities (Sat) · Kashmir saffron protest (Sat) · Mumbai
assault (Fri) · Modi's IIT Patna AI centre (Sat) · Myanmar draft-graft
statement (Sun) · CSAT cheating review, 111 cases (Fri) · Gaza: two killed
in Sunday shelling (Sun) · EU sanctions package (adopted 16 Nov) · Trump's
contractor order (Fri) · Lewis Pugh's Hormuz swim (16–18 Nov) · Washington
ICE arrests (Sat) · Hyderabad fee-hike protest (17–18 Nov). The Cikande
"24 body bags" figure in an early draft was unsupported and was replaced
with the rescue agency's figure of 36 workers still missing; Japan's markets
were closed on Monday for Labor Thanksgiving Day, not open.

## License

MIT — see [LICENSE](LICENSE).
