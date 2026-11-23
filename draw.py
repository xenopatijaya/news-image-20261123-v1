#!/usr/bin/env python3
"""Render the Monday 23 November 2026 world-news broadsheet (1024x1024).

Drawn fresh in-session with PIL. No network, no randomness, no clock reads:
every string on the page is a constant in this file, so two runs of the same
file write byte-identical PNGs. Story facts were verified live against their
sources on the morning of 23 Nov 2026; anything that happened on another day
is named in the red DATE CHECK box instead of being printed as Monday news.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

NAVY = (20, 33, 61)
NAVY2 = (38, 58, 96)
CREAM = (251, 246, 233)
PAPER = (255, 252, 244)
RED = (193, 39, 45)
RED_DK = (150, 24, 30)
INK = (24, 24, 22)
MUTE = (96, 90, 78)
GOLD = (176, 132, 52)
TEAL = (31, 110, 110)
LINE = (20, 33, 61)

FDIR = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(FDIR, "DejaVuSerif.ttf")
SERIFB = os.path.join(FDIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FDIR, "DejaVuSans.ttf")
SANSB = os.path.join(FDIR, "DejaVuSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(draw, text, path, size, max_w):
    """Largest font size <= size whose rendered width fits max_w."""
    s = size
    while s > 6:
        f = font(path, s)
        if draw.textlength(text, font=f) <= max_w:
            return f
        s -= 1
    return font(path, 6)


def wrap(draw, text, f, max_w):
    """Greedy word wrap; returns list of lines."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text(draw, xy, s, f, fill, anchor="la"):
    draw.text(xy, s, font=f, fill=fill, anchor=anchor)


def block(draw, x, y, w, lines, f, fill, leading=None):
    """Draw wrapped lines; returns y after the last line."""
    lh = leading or int(f.size * 1.28)
    for ln in lines:
        text(draw, (x, y), ln, f, fill)
        y += lh
    return y


def chip(draw, x, y, label, fg, bg):
    """Small rounded tag; returns width used."""
    f = font(SANSB, 10)
    w = int(draw.textlength(label, font=f)) + 12
    draw.rounded_rectangle([x, y, x + w, y + 16], radius=8, fill=bg)
    text(draw, (x + 6, y + 2), label, f, fg)
    return w


# ---------------------------------------------------------------- story data
# certainty: REPORTED = confirmed by the named source; CLAIM = one side's
# claim, never printed as fact; SCHEDULED = set for Monday, reported as such.
# Every item happened, or was first reported, on Monday 23 November 2026,
# or is a Monday development of an ongoing story (framed that way in the deck).
LEADS = [
    dict(n=1, region="SOUTH ASIA", place="NEW DELHI", lon=77.2, lat=28.6,
         scene="talks",
         head="NEPAL AND INDIA TALK",
         deck="PM Balendra Shah meets PM Modi in Delhi on his first "
              "bilateral trip abroad since taking office in March. "
              "A 34-member delegation; MoUs on health, education and "
              "farming on the table; joint press conference after.",
         src="MEA / IANS", cert="REPORTED"),
    dict(n=2, region="EUROPE", place="BRUSSELS", lon=4.35, lat=50.85,
         scene="council",
         head="NATO COUNCIL MEETS ON POLAND",
         deck="The North Atlantic Council sits in Brussels today over "
              "Friday's violation of Polish airspace by Russian "
              "missiles and a jet drone. Debris fell in three villages; "
              "one object was a Kh-101 cruise missile.",
         src="NATO / AnewZ", cert="REPORTED"),
    dict(n=3, region="ASIA-PACIFIC", place="CIKANDE, INDONESIA", lon=106.3, lat=-6.2,
         scene="factory",
         head="SEARCH RESUMES AT THE CANDY PLANT",
         deck="Rescuers go back in at 07:00 today at the Milkita candy "
              "factory in Cikande, Banten. The fire broke out Saturday; "
              "three are confirmed dead, dozens are still missing, and "
              "DNA identification will take two to three weeks.",
         src="REUTERS", cert="REPORTED"),
]

CARDS = [
    dict(n=4, region="EUROPE", place="KYIV REGION", lon=30.3, lat=50.8,
         scene="rescue",
         head="14 STILL MISSING IN DYMER",
         deck="Search goes on for 14 people under a block hit by a Russian drone on Sunday.",
         src="REUTERS", cert="REPORTED"),
    dict(n=5, region="OCEANIA", place="WELLINGTON", lon=174.8, lat=-41.3,
         scene="cricket",
         head="TEST DECIDER: DAY FIVE",
         deck="NZ open day five on 119/2, 233 behind India's 720/9. Conway 59 not out.",
         src="ESPNCRICINFO", cert="REPORTED"),
    dict(n=6, region="SOUTH ASIA", place="DHAKA", lon=90.4, lat=23.8,
         scene="podium",
         head="GARMENT PAY TALKS OPEN IN DHAKA",
         deck="Owners table a pay offer today; workers want Tk32,000 a month, up from 12,500.",
         src="BUSINESS STANDARD", cert="REPORTED"),
    dict(n=7, region="EUROPE", place="LONDON", lon=-0.1, lat=51.5,
         scene="bridge",
         head="BRITAIN TO TAKE MORE CONTROL OF UTILITIES",
         deck="Labour sets out its plan for public control of water and energy at the CBI.",
         src="REUTERS", cert="SCHEDULED"),
    dict(n=8, region="ASIA-PACIFIC", place="SINGAPORE", lon=103.8, lat=1.35,
         scene="council",
         head="CHINA–SINGAPORE: 20 DEALS DUE",
         deck="Vice Premier Ding co-chairs the council in Singapore; 20+ deals are expected.",
         src="XINHUA", cert="SCHEDULED"),
    dict(n=9, region="ASIA-PACIFIC", place="JAVA SEA", lon=110.0, lat=-6.0,
         scene="ship",
         head="NAVY SEIZES ROCKET-CHEMICAL SHIP",
         deck="Indonesia's navy seizes a ship carrying 405 tonnes of rocket chemical.",
         src="BUSINESS STANDARD", cert="REPORTED"),
    dict(n=10, region="SOUTH ASIA", place="PARBHANI", lon=76.8, lat=19.3,
         scene="parliament",
         head="WADKUTE'S LAST RESPECTS IN PARBHANI",
         deck="The BJP MP's body lies in Parbhani today for last respects; rites in Hingoli.",
         src="NEWSNATION", cert="REPORTED"),
    dict(n=11, region="OCEANIA", place="CANBERRA", lon=149.1, lat=-35.3,
         scene="council",
         head="CANBERRA'S LAST SITTING WEEK OPENS",
         deck="Parliament opens its final sitting week; gas reservation is on the agenda.",
         src="THE SQUIZ", cert="SCHEDULED"),
    dict(n=12, region="AMERICAS", place="NEW YORK", lon=-74.0, lat=40.7,
         scene="podium",
         head="UN TAKES ON ORGANISED CRIME",
         deck="The UN holds a high-level event in New York on organised crime today.",
         src="UN NEWS", cert="SCHEDULED"),
    dict(n=13, region="OCEANIA", place="MELBOURNE", lon=145.0, lat=-37.8,
         scene="cricket2",
         head="AUSTRALIA HOST ENGLAND IN T20 TONIGHT",
         deck="Australia face England at the MCG tonight, with two players set to debut.",
         src="CRICKET.COM.AU", cert="SCHEDULED"),
]

BRIEFS = [
    dict(n=14, region="EUROPE", place="COPENHAGEN", lon=12.6, lat=55.7,
         fact="Denmark puts its plan to EU envoys today: halt tourist visas for Russians.",
         src="REUTERS"),
    dict(n=15, region="ASIA-PACIFIC", place="TOKYO", lon=139.7, lat=35.7,
         fact="Japan's markets stay shut for Labor Thanksgiving Day; the Nikkei reopens Tuesday.",
         src="JPX"),
    dict(n=16, region="OCEANIA", place="CANBERRA", lon=149.1, lat=-35.3,
         fact="Australia counts the cost of the COP31 collapse it co-ran.",
         src="THE SQUIZ"),
    dict(n=17, region="AMERICAS", place="NEW YORK", lon=-74.0, lat=40.7,
         fact="Wall Street reopens after Nvidia slid about $2.7 trillion from its 6 October peak.",
         src="FINNHUB"),
    dict(n=18, region="AMERICAS", place="NEW YORK", lon=-74.0, lat=40.7,
         fact="Bitcoin holds above $60,000 after sliding to about $55,100 on Saturday.",
         src="FINNHUB"),
    dict(n=19, region="SOUTH ASIA", place="HYDERABAD", lon=78.5, lat=17.4,
         fact="University of Hyderabad students continue a sit-in, demanding a faculty member's removal.",
         src="HYDERABAD MAIL"),
    dict(n=20, region="EUROPE", place="LONDON", lon=-0.1, lat=51.5,
         fact="MPs debate the Finance Bill, putting the 28 October Budget's tax measures into law.",
         src="HANSARD SOCIETY"),
    dict(n=21, region="EUROPE", place="LONDON", lon=-0.1, lat=51.5,
         fact="The government introduces the EU Partnership Bill after Friday's EU-UK reset summit.",
         src="PRESS DATA"),
    dict(n=22, region="SOUTH ASIA", place="NEW DELHI", lon=77.2, lat=28.6,
         fact="Nepal's PM also calls on President Murmu and lays a wreath at Rajghat before talks.",
         src="MEA"),
    dict(n=23, region="AMERICAS", place="HOUSTON", lon=-95.4, lat=29.8,
         fact="NASA holds a press conference ahead of its next space station supply mission.",
         src="PRESS DATA"),
    dict(n=24, region="OCEANIA", place="SYDNEY", lon=151.2, lat=-33.9,
         fact="National Asbestos Awareness Week opens; 11 Australians die each day from asbestos disease.",
         src="MEDIANET"),
    dict(n=25, region="EUROPE", place="LONDON", lon=-0.1, lat=51.5,
         fact="MPs debate a petition calling for changes to bereavement support.",
         src="BBC"),
    dict(n=26, region="OCEANIA", place="WELLINGTON", lon=174.8, lat=-41.3,
         fact="New Zealand releases third-quarter retail sales today, with a recovery expected.",
         src="FINWIRE"),
    dict(n=27, region="EUROPE", place="LONDON", lon=-0.1, lat=51.5,
         fact="Thirty-one NHS trusts warn that cost-cutting demands threaten their ability to function.",
         src="THE GUARDIAN"),
    dict(n=28, region="EUROPE", place="LONDON", lon=-0.1, lat=51.5,
         fact="A disability benefits review will call for an overhaul, not scrapping it for under-25s.",
         src="THE GUARDIAN"),
    dict(n=29, region="OCEANIA", place="CANBERRA", lon=149.1, lat=-35.3,
         fact="UNSW launches a Graduate School of Public Policy for the nation's future leaders today.",
         src="MEDIANET"),
    dict(n=30, region="SOUTH ASIA", place="NEW DELHI", lon=77.2, lat=28.6,
         fact="Nepal's PM flies home this evening after the Delhi talks, ending a visit of little over 24 hours.",
         src="IANS"),
]

ALL = LEADS + CARDS + BRIEFS
REGIONS = ["EUROPE", "SOUTH ASIA", "ASIA-PACIFIC", "OCEANIA", "AMERICAS"]
RCOL = {"EUROPE": NAVY2, "SOUTH ASIA": GOLD, "ASIA-PACIFIC": TEAL,
        "OCEANIA": (20, 90, 70), "AMERICAS": (90, 60, 120)}

BIG = [
    ("720/9", "INDIA'S RECORD TEST TOTAL (SUN) — DECIDER TODAY"),
    ("36", "WORKERS STILL MISSING AT CIKANDE (SUN)"),
    ("34", "MEMBERS OF NEPAL'S DELEGATION IN DELHI"),
    ("14", "STILL MISSING IN KYIV REGION — RESCUE GOES ON"),
    ("32,000", "TAKA A MONTH SOUGHT BY DHAKA GARMENT WORKERS"),
    ("233", "RUNS NZ TRAIL BY AS DAY FIVE OPENS"),
]

TIMELINE = [
    ("07:00 WIB", "CIKANDE SEARCH RESUMES"),
    ("MORNING IST", "SHAH–MODI TALKS, DELHI"),
    ("MORNING CET", "NATO COUNCIL, BRUSSELS"),
    ("DAY FIVE", "WELLINGTON TEST DECIDER"),
    ("AFTER TALKS", "NEPAL JOINT PRESS CONFERENCE"),
]

# Other-day stories deliberately left out (real day in brackets).
EXCLUDED = [
    ("COP31 COLLAPSED, NO PACT", "SUN"),
    ("DEMOCRATS CLINCH 258 SEATS", "SUN"),
    ("MERKURY SUNK AT BENGHAZI", "SUN"),
    ("SPARTA II TOWED OUT", "SUN"),
    ("HONG KONG EC VOTE", "SUN"),
    ("KOREA MINISTER QUITS", "SUN"),
    ("UKMTO CHABAHAR INCIDENT", "SUN"),
    ("WHO EBOLA WARNING", "SUN"),
    ("SAUDI–HOUTHI EXCHANGE", "SUN"),
    ("UN ROBOT-WEAPONS TALKS", "SAT"),
    ("AUKUS REBUKE", "SUN"),
    ("MYANMAR–ASEAN REBUKE", "SAT"),
    ("UK DRONE DEAL SIGNED", "SAT"),
    ("TATA STEEL–APL DEAL", "SUN"),
    ("YEMEN 149 CLAIM", "SAT"),
    ("HORMUZ SWIM ENDS", "SUN"),
]

PRESS_TIME = "PRESS TIME 00:38 UTC"


# ------------------------------------------------------------------- scenes
def _sky(d, x, y, w, h, top=(214, 230, 240), bot=(250, 246, 233)):
    for i in range(h):
        r = int(top[0] + (bot[0] - top[0]) * i / max(h - 1, 1))
        g = int(top[1] + (bot[1] - top[1]) * i / max(h - 1, 1))
        b = int(top[2] + (bot[2] - top[2]) * i / max(h - 1, 1))
        d.line([(x, y + i), (x + w, y + i)], fill=(r, g, b))


def _flag(d, x, y, w, h, stripes):
    """Vertical-pole flag with horizontal stripes."""
    d.line([(x, y - 6), (x, y + h)], fill=INK, width=2)
    for i, c in enumerate(stripes):
        d.rectangle([x + 1, y + i * h / len(stripes), x + w, y + (i + 1) * h / len(stripes)], fill=c)


def _person(d, x, y, s, shirt, pants):
    """Simple standing figure, s = height in px."""
    d.ellipse([x - s * 0.14, y, x + s * 0.14, y + s * 0.28], fill=(222, 184, 150))
    d.rectangle([x - s * 0.16, y + s * 0.28, x + s * 0.16, y + s * 0.62], fill=shirt)
    d.rectangle([x - s * 0.14, y + s * 0.62, x - s * 0.02, y + s], fill=pants)
    d.rectangle([x + s * 0.02, y + s * 0.62, x + s * 0.14, y + s], fill=pants)


def scene_talks(d, x, y, w, h):
    _sky(d, x, y, w, h)
    gy = y + h - 22
    d.rectangle([x, gy, x + w, y + h], fill=(196, 178, 140))          # ground
    cx, cy = x + w // 2, gy - 6
    d.rectangle([x + 18, cy - 26, x + w - 18, cy + 6], fill=(232, 222, 198))  # hall
    d.pieslice([cx - 30, cy - 52, cx + 30, cy + 8], 180, 360, fill=(176, 132, 52))  # dome
    d.rectangle([cx - 2, cy - 62, cx + 2, cy - 52], fill=GOLD)
    for fx in (x + 30, x + w - 52):
        d.rectangle([fx, cy - 22, fx + 6, cy + 6], fill=NAVY)
    _flag(d, x + 12, y + 12, 20, 12, [(255, 153, 51), (255, 255, 255), (19, 136, 8)])
    _flag(d, x + w - 34, y + 12, 20, 12, [(220, 20, 60), (0, 56, 147)])
    _person(d, cx - 26, gy - 34, 30, NAVY, INK)
    _person(d, cx + 26, gy - 34, 30, RED_DK, INK)
    d.line([(cx - 14, gy - 22), (cx + 14, gy - 22)], fill=(222, 184, 150), width=3)
    d.rectangle([cx - 34, gy - 8, cx + 34, gy - 2], fill=(120, 84, 40))  # table
    d.rectangle([cx - 20, gy - 14, cx - 6, gy - 8], fill=(255, 255, 255))
    d.rectangle([cx + 6, gy - 14, cx + 20, gy - 8], fill=(255, 255, 255))


def scene_council(d, x, y, w, h):
    _sky(d, x, y, w, h, top=(30, 48, 88), bot=(70, 95, 140))
    d.ellipse([x + w // 2 - 46, y + 8, x + w // 2 + 46, y + 52], outline=GOLD, width=3)
    for k in range(12):
        import math
        a = k * math.pi / 6
        px = x + w // 2 + 38 * math.cos(a)
        py = y + 30 + 20 * math.sin(a)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=GOLD)
    d.ellipse([x + w // 2 - 34, y + 58, x + w // 2 + 34, y + 78], fill=(120, 84, 40))
    d.rectangle([x + w // 2 - 34, y + 66, x + w // 2 + 34, y + 70], fill=(90, 60, 30))
    for i, fx in enumerate(range(x + 14, x + w - 10, 26)):
        d.rectangle([fx, y + h - 26, fx + 16, y + h - 12], fill=NAVY2 if i % 2 else RED_DK)
    _person(d, x + 26, y + h - 40, 26, NAVY, INK)
    _person(d, x + w - 26, y + h - 40, 26, TEAL, INK)
    d.rectangle([x + 8, y + h - 10, x + w - 8, y + h - 6], fill=(200, 190, 160))


def scene_factory(d, x, y, w, h):
    _sky(d, x, y, w, h, top=(120, 110, 100), bot=(230, 220, 200))
    gy = y + h - 18
    d.rectangle([x, gy, x + w, y + h], fill=(120, 110, 95))
    bx, by = x + w // 2 - 52, gy - 52
    d.rectangle([bx, by, bx + 104, gy], fill=(210, 196, 170))
    d.rectangle([bx, by + 18, bx + 104, by + 20], fill=INK)
    d.rectangle([bx, by + 36, bx + 104, by + 38], fill=INK)
    for wx in range(bx + 8, bx + 100, 18):
        d.rectangle([wx, by + 6, wx + 10, by + 14], fill=(60, 50, 40))
    d.polygon([(bx + 20, by), (bx + 34, by - 26), (bx + 48, by)], fill=(90, 80, 70))
    d.ellipse([bx + 26, by - 44, bx + 44, by - 26], fill=(90, 85, 80))
    d.ellipse([bx + 40, by - 58, bx + 62, by - 36], fill=(110, 105, 100))
    d.ellipse([bx + 58, by - 72, bx + 84, by - 48], fill=(130, 125, 120))
    d.polygon([(x + 14, gy - 30), (x + 60, gy - 30), (x + 40, gy)], fill=(255, 240, 180))
    _person(d, x + 22, gy - 24, 22, RED, INK)
    _person(d, x + w - 22, gy - 24, 22, NAVY, INK)
    d.rectangle([x + w - 60, gy - 6, x + w - 8, gy], fill=(255, 255, 255))
    d.text((x + w - 56, gy - 5), "07:00", font=font(SANSB, 8), fill=RED_DK)


def scene_rescue(d, x, y, w, h):
    _sky(d, x, y, w, h, top=(150, 160, 175), bot=(235, 230, 215))
    gy = y + h - 14
    d.rectangle([x, gy, x + w, y + h], fill=(150, 140, 125))
    d.polygon([(x + 8, gy), (x + w // 2 - 10, y + 26), (x + w - 8, gy)], fill=(120, 110, 95))
    d.polygon([(x + 30, gy), (x + w // 2 + 6, y + 44), (x + w - 30, gy)], fill=(100, 92, 80))
    for rx, ry, rw in ((x + 24, y + 52, 22), (x + w // 2 - 8, y + 40, 18), (x + w - 52, y + 56, 24)):
        d.rectangle([rx, ry, rx + rw, ry + 8], fill=(80, 72, 62))
    d.line([(x + w - 12, y + 6), (x + w // 2, y + 34)], fill=GOLD, width=3)
    d.polygon([(x + w // 2 - 22, y + 30), (x + w - 8, y + 4), (x + w - 2, y + 12)], fill=(255, 244, 190))
    _person(d, x + 22, gy - 22, 20, RED, INK)
    _person(d, x + 40, gy - 22, 20, NAVY, INK)
    d.rectangle([x + 52, gy - 10, x + 84, gy - 4], fill=(230, 220, 200))


def scene_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(46, 125, 60))
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(30, 95, 45))
    d.rectangle([x + w // 2 - 26, y + 12, x + w // 2 + 26, y + h - 26], fill=(205, 178, 120))
    for sx in (x + w // 2 - 8, x + w // 2 - 2, x + w // 2 + 4):
        d.rectangle([sx, y + 16, sx + 3, y + 30], fill=(240, 220, 150))
    d.rectangle([x + w // 2 - 9, y + 14, x + w // 2 + 8, y + 16], fill=(240, 220, 150))
    d.line([(x + w // 2 + 30, y + 34), (x + w // 2 + 52, y + 52)], fill=(150, 100, 50), width=4)
    d.ellipse([x + w // 2 + 48, y + 50, x + w // 2 + 56, y + 58], fill=RED)
    d.rectangle([x + w - 74, y + 6, x + w - 8, y + 26], fill=NAVY)
    d.text((x + w - 70, y + 9), "720/9", font=font(SANSB, 13), fill=(255, 255, 255))
    _person(d, x + w - 24, y + h - 34, 24, (255, 255, 255), (30, 60, 30))
    d.ellipse([x + 14, y + h - 18, x + 22, y + h - 10], fill=(255, 255, 255))


def scene_podium(d, x, y, w, h):
    _sky(d, x, y, w, h, top=(200, 210, 225), bot=(245, 242, 232))
    for i, fx in enumerate(range(x + 10, x + w - 8, 24)):
        d.rectangle([fx, y + 8, fx + 16, y + 30], fill=NAVY2 if i % 2 else RED_DK)
    gy = y + h - 12
    d.rectangle([x, gy, x + w, y + h], fill=(180, 165, 135))
    d.polygon([(x + w // 2 - 34, gy), (x + w // 2 + 34, gy), (x + w // 2 + 24, gy - 34),
               (x + w // 2 - 24, gy - 34)], fill=(90, 60, 30))
    d.rectangle([x + w // 2 - 24, gy - 44, x + w // 2 + 24, gy - 34], fill=(120, 84, 40))
    _person(d, x + w // 2, gy - 62, 26, NAVY, INK)
    d.line([(x + w // 2 + 8, gy - 44), (x + w // 2 + 16, gy - 56)], fill=INK, width=2)
    d.ellipse([x + w // 2 + 14, gy - 60, x + w // 2 + 20, gy - 54], fill=INK)


def scene_drone(d, x, y, w, h):
    _sky(d, x, y, w, h, top=(90, 120, 160), bot=(210, 225, 235))
    d.ellipse([x + w - 30, y + 8, x + w - 8, y + 30], fill=(255, 240, 180))
    gy = y + h - 16
    d.rectangle([x, gy, x + w, y + h], fill=(140, 135, 120))
    for bx in range(x + 8, x + w - 8, 30):
        d.rectangle([bx, gy - 14, bx + 22, gy], fill=(90, 85, 75))
    cx, cy = x + w // 2, y + h // 2 - 6
    d.rectangle([cx - 16, cy - 5, cx + 16, cy + 5], fill=INK)
    for dx, dy in ((-22, -10), (22, -10), (-22, 10), (22, 10)):
        d.ellipse([cx + dx - 6, cy + dy - 3, cx + dx + 6, cy + dy + 3], fill=(60, 60, 60))
        d.line([(cx, cy), (cx + dx, cy + dy)], fill=INK, width=2)
    d.line([(cx, cy + 6), (cx + 26, gy - 16)], fill=RED_DK, width=2)
    d.ellipse([cx + 22, gy - 20, cx + 30, gy - 12], fill=RED_DK)
    d.rectangle([x + 8, y + 8, x + 30, y + 24], fill=(255, 255, 255))
    d.rectangle([x + 8, y + 8, x + 30, y + 24], outline=RED_DK, width=1)
    d.line([(x + 8, y + 8), (x + 30, y + 24)], fill=RED_DK, width=2)
    d.line([(x + 30, y + 8), (x + 8, y + 24)], fill=RED_DK, width=2)


def scene_bridge(d, x, y, w, h):
    _sky(d, x, y, w, h, top=(200, 225, 235), bot=(245, 240, 225))
    d.ellipse([x + w - 34, y + 6, x + w - 10, y + 30], fill=(255, 220, 120))
    gy = y + h - 20
    d.rectangle([x, gy, x + w, y + h], fill=(90, 140, 160))
    d.polygon([(x, gy), (x + w, gy), (x + w, gy - 26), (x, gy - 26)], fill=(120, 150, 110))
    d.polygon([(x + 8, gy - 26), (x + w // 2, gy - 52), (x + w - 8, gy - 26),
               (x + w - 8, gy - 18), (x + 8, gy - 18)], fill=(150, 60, 50))
    for px in range(x + 16, x + w - 10, 18):
        d.line([(px, gy - 30), (px, gy - 44)], fill=(150, 60, 50), width=2)
    d.rectangle([x + w // 2 - 30, gy - 62, x + w // 2 + 30, gy - 52], fill=(255, 255, 255))
    d.text((x + w // 2 - 26, gy - 61), "Rs 4,000 cr", font=font(SANSB, 8), fill=NAVY)


def scene_steel(d, x, y, w, h):
    _sky(d, x, y, w, h, top=(70, 70, 80), bot=(150, 120, 90))
    gy = y + h - 14
    d.rectangle([x, gy, x + w, y + h], fill=(60, 55, 50))
    d.ellipse([x + w // 2 - 26, gy - 44, x + w // 2 + 26, gy + 8], fill=(255, 140, 40))
    d.ellipse([x + w // 2 - 16, gy - 34, x + w // 2 + 16, gy - 2], fill=(255, 190, 90))
    for cx in (x + 22, x + w - 22):
        d.ellipse([cx - 14, gy - 26, cx + 14, gy + 2], fill=(160, 165, 170))
        d.ellipse([cx - 6, gy - 18, cx + 6, gy - 6], fill=(90, 95, 100))
    d.line([(x + 10, y + 8), (x + w - 10, y + 8)], fill=GOLD, width=3)
    d.line([(x + w // 2, y + 8), (x + w // 2, y + 26)], fill=GOLD, width=2)
    d.polygon([(x + w // 2 - 6, y + 26), (x + w // 2 + 6, y + 26), (x + w // 2, y + 36)], fill=GOLD)


def scene_parliament(d, x, y, w, h):
    _sky(d, x, y, w, h, top=(210, 220, 235), bot=(245, 242, 232))
    gy = y + h - 14
    d.rectangle([x, gy, x + w, y + h], fill=(170, 160, 140))
    cx = x + w // 2
    d.rectangle([x + 14, gy - 34, x + w - 14, gy], fill=(225, 215, 190))
    d.pieslice([cx - 22, gy - 56, cx + 22, gy - 12], 180, 360, fill=(176, 132, 52))
    for px in range(x + 22, x + w - 14, 16):
        d.rectangle([px, gy - 30, px + 7, gy], fill=(200, 190, 165))
    d.rectangle([cx - 4, gy - 40, cx + 4, gy - 34], fill=INK)
    d.rectangle([x + 8, gy - 12, x + 26, gy - 4], fill=INK)
    d.ellipse([x + 30, y + 8, x + 44, y + 22], fill=(255, 240, 180))


def scene_film(d, x, y, w, h):
    _sky(d, x, y, w, h, top=(40, 40, 55), bot=(90, 80, 110))
    d.ellipse([x + 18, y + 12, x + 58, y + 52], outline=(230, 220, 200), width=4)
    d.ellipse([x + 30, y + 24, x + 46, y + 40], outline=(230, 220, 200), width=3)
    d.ellipse([x + w - 58, y + 12, x + w - 18, y + 52], outline=(230, 220, 200), width=4)
    d.ellipse([x + w - 46, y + 24, x + w - 30, y + 40], outline=(230, 220, 200), width=3)
    d.polygon([(x + w // 2 - 30, y + h - 34), (x + w // 2 + 30, y + h - 34),
               (x + w // 2 + 30, y + h - 8), (x + w // 2 - 30, y + h - 8)], fill=(20, 20, 20))
    d.polygon([(x + w // 2 - 30, y + h - 34), (x + w // 2 + 30, y + h - 34),
               (x + w // 2 + 24, y + h - 46), (x + w // 2 - 24, y + h - 46)], fill=(240, 240, 240))
    for i in range(5):
        sx = x + w // 2 - 24 + i * 10
        d.line([(sx, y + h - 46), (sx + 5, y + h - 34)], fill=INK, width=2)
    d.polygon([(x + 8, y + h - 20), (x + 40, y + h - 40), (x + 40, y + h - 8)], fill=GOLD)
    d.polygon([(x + w - 8, y + h - 20), (x + w - 40, y + h - 40), (x + w - 40, y + h - 8)], fill=RED_DK)


def scene_claim(d, x, y, w, h):
    _sky(d, x, y, w, h, top=(235, 225, 205), bot=(250, 244, 228))
    d.ellipse([x + w // 2 - 34, y + 6, x + w // 2 + 34, y + 66], outline=RED_DK, width=3)
    d.ellipse([x + w // 2 - 26, y + 14, x + w // 2 + 26, y + 58], fill=(250, 230, 200))
    d.polygon([(x + w // 2, y + 66), (x + w // 2 - 10, y + 52), (x + w // 2 + 10, y + 52)], fill=RED_DK)
    d.text((x + w // 2 - 22, y + 16), "149", font=font(SANSB, 22), fill=RED_DK)
    d.line([(x + 12, y + h - 12), (x + w - 12, y + h - 12)], fill=RED_DK, width=2)
    for lx in range(x + 12, x + w - 12, 12):
        d.line([(lx, y + h - 12), (lx + 6, y + h - 12)], fill=CREAM, width=2)
    d.text((x + 10, y + h - 30), "CLAIM — UNVERIFIED", font=font(SANSB, 8), fill=RED_DK)


SCENES = {"talks": scene_talks, "council": scene_council, "factory": scene_factory,
          "rescue": scene_rescue, "cricket": scene_cricket, "podium": scene_podium,
          "drone": scene_drone, "bridge": scene_bridge, "steel": scene_steel,
          "parliament": scene_parliament, "film": scene_film, "claim": scene_claim}


# ------------------------------------------------------------------- pin map
LAND = [(-100, 48, 55, 22), (-155, 64, 18, 8), (-90, 15, 12, 8), (-60, -12, 22, 28),
        (12, 52, 28, 14), (18, 4, 26, 30), (85, 48, 55, 22), (102, 12, 18, 14),
        (78, 21, 12, 12), (45, 24, 12, 10), (134, -25, 20, 10), (172, -41, 6, 6),
        (-40, 70, 20, 8), (60, 62, 20, 10)]


def _in_land(lon, lat):
    for cx, cy, rx, ry in LAND:
        if ((lon - cx) / rx) ** 2 + ((lat - cy) / ry) ** 2 <= 1:
            return True
    return False


# Label offsets for the crowded clusters (dx, dy from the pin).
# London x6, Delhi x3, New York x3, Canberra x3, Wellington x2, plus
# custom offsets for the South Asia / SE Australia corners.
PIN_OFF = {1: (-13, -36), 22: (13, -36), 30: (33, -19),
           7: (-36, 13), 20: (-36, -13), 21: (-19, -33), 25: (7, -37),
           27: (29, -24), 28: (-19, 33),
           12: (-31, -18), 17: (0, -36), 18: (31, -18),
           11: (-28, -10), 16: (-19, -23), 29: (20, -24),
           5: (-22, 13), 26: (-22, -13), 24: (0, -30), 13: (-14, 24),
           2: (4, 30), 4: (14, 8), 3: (-26, -14), 19: (-28, 4), 10: (20, 14)}


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 240, 232))
    d.rectangle([x, y, x + w, y + h], outline=NAVY, width=1)
    lon = -180
    while lon <= 180:
        lat = 75
        while lat >= -60:
            if _in_land(lon, lat):
                px = x + (lon + 180) / 360 * w
                py = y + (75 - lat) / 135 * h
                d.ellipse([px - 1.6, py - 1.6, px + 1.6, py + 1.6], fill=(120, 140, 165))
            lat -= 5
        lon += 5
    for s in ALL:
        px = x + (s["lon"] + 180) / 360 * w
        py = y + (75 - s["lat"]) / 135 * h
        d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=RED, outline=(255, 255, 255), width=1)
        ox, oy = PIN_OFF.get(s["n"], (7, -7))
        lx, ly = px + ox, py + oy
        if (ox, oy) != (7, -7):
            d.line([(px, py), (lx, ly)], fill=RED_DK, width=1)
        f = font(SANSB, 8)
        tw = d.textlength(str(s["n"]), font=f)
        d.rectangle([lx - 1, ly - 6, lx + tw + 1, ly + 4], fill=NAVY)
        d.text((lx, ly - 6), str(s["n"]), font=f, fill=(255, 255, 255))
    d.text((x + 4, y + h - 12), "EQUIRECTANGULAR • DOTS = LAND", font=font(SANS, 7), fill=MUTE)



# ------------------------------------------------------------------- layout
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W - 1, H - 1], outline=NAVY, width=6)
    mx = 36
    cw = W - 2 * mx  # 952

    # kicker band
    d.rectangle([mx, 10, mx + cw, 34], fill=NAVY)
    text(d, (mx + cw // 2, 15), "THE WORLD IN ONE DAY", font(SERIFB, 15), CREAM, anchor="ma")

    # masthead
    f = fit_font(d, "MONDAY 23 NOVEMBER 2026", SERIFB, 58, cw)
    text(d, (mx + cw // 2, 38), "MONDAY 23 NOVEMBER 2026", f, NAVY, anchor="ma")

    # count line
    counts = {r: sum(1 for s in ALL if s["region"] == r) for r in REGIONS}
    total = len(ALL)
    left = ("%d DATE-CHECKED STORIES  •  %d REGIONS  •  EVERY ONE DATED AT ITS SOURCE"
            % (total, len(REGIONS)))
    text(d, (mx, 98), left, font(SANSB, 13), NAVY)
    text(d, (mx + cw, 99), PRESS_TIME, font(SANS, 11), MUTE, anchor="ra")
    d.line([(mx, 116), (mx + cw, 116)], fill=RED, width=2)

    # red deck (one line)
    deck = ("Nepal–India talks open in Delhi  •  NATO council meets on Poland's "
            "airspace  •  Cikande search resumes at dawn")
    f = fit_font(d, deck, SERIF, 17, cw)
    text(d, (mx, 122), deck, f, RED)

    # big-numbers strip
    y0 = 150
    cell = cw // 6
    for i, (num, lab) in enumerate(BIG):
        x = mx + i * cell
        d.line([(x, y0), (x + cell - 6, y0)], fill=NAVY, width=2)
        fn = fit_font(d, num, SERIFB, 28, cell - 10)
        text(d, (x + (cell - 6) // 2, y0 + 5), num, fn, NAVY, anchor="ma")
        fl = font(SANS, 8)
        block(d, x, y0 + 36, cell - 8, wrap(d, lab, fl, cell - 8)[:2], fl, MUTE, leading=10)
    # region bar
    y0 = 204
    bx = mx
    for r in REGIONS:
        wseg = max(18, int(cw * counts[r] / total))
        d.rectangle([bx, y0, bx + wseg - 2, y0 + 18], fill=RCOL[r])
        fc = font(SANSB, 11)
        text(d, (bx + (wseg - 2) // 2, y0 + 3), str(counts[r]), fc, (255, 255, 255), anchor="ma")
        bx += wseg
    leg = "  •  ".join("%s %d" % (r, counts[r]) for r in REGIONS)
    text(d, (mx, y0 + 22), leg, font(SANSB, 10), NAVY)
    # timeline strip
    y0 = 242
    d.rectangle([mx, y0, mx + cw, y0 + 26], fill=NAVY)
    t = "MONDAY, AROUND THE CLOCK   " + "   •   ".join("%s — %s" % (a, b) for a, b in TIMELINE)
    ft = fit_font(d, t, SANSB, 11, cw - 16)
    text(d, (mx + 8, y0 + 7), t, ft, (255, 255, 255))

    # leads
    ly, lh = 272, 190
    lw = (cw - 16) // 3
    for i, s in enumerate(LEADS):
        x = mx + i * (lw + 8)
        d.rectangle([x, ly, x + lw, ly + lh], fill=(255, 255, 255), outline=NAVY, width=1)
        SCENES[s["scene"]](d, x + 2, ly + 2, lw - 4, 104)
        chip(d, x + 6, ly + 8, s["cert"], (255, 255, 255),
             RED_DK if s["cert"] == "CLAIM" else NAVY)
        sw = d.textlength(s["src"], font=font(SANSB, 8))
        d.rectangle([x + lw - sw - 12, ly + 96, x + lw - 4, ly + 108], fill=(255, 255, 255))
        text(d, (x + lw - 8, ly + 97), s["src"], font(SANSB, 8), NAVY, anchor="ra")
        fh = font(SANSB, 14)
        hy = block(d, x + 8, ly + 112, lw - 16, wrap(d, s["head"], fh, lw - 16), fh, NAVY, leading=16)
        fd = font(SANS, 9)
        block(d, x + 8, hy + 2, lw - 16, wrap(d, s["deck"], fd, lw - 16)[:4], fd, INK, leading=11)

    # cards: 2 rows x 5
    cy, chh, cwid = 466, 88, 186
    for i, s in enumerate(CARDS):
        row, col = divmod(i, 5)
        x = mx + col * (cwid + 5)
        y = cy + row * (chh + 4)
        d.rectangle([x, y, x + cwid, y + chh], fill=(255, 255, 255), outline=NAVY, width=1)
        _m(d, x + 1, y + 1, cwid - 2, 34, s["scene"])
        d.ellipse([x + 4, y + 4, x + 18, y + 18], fill=NAVY)
        text(d, (x + 11, y + 5), str(s["n"]), font(SANSB, 9), (255, 255, 255), anchor="ma")
        chip(d, x + cwid - 62, y + 5, s["cert"], (255, 255, 255),
             RED_DK if s["cert"] == "CLAIM" else NAVY)
        fh = font(SANSB, 10)
        hy = block(d, x + 6, y + 38, cwid - 12, wrap(d, s["head"], fh, cwid - 12)[:2], fh, NAVY, leading=12)
        fd = font(SANS, 8)
        block(d, x + 6, hy + 1, cwid - 12, wrap(d, s["deck"], fd, cwid - 12)[:2], fd, MUTE, leading=10)

    # map + briefs
    my = 650
    text(d, (mx, my), "WHERE IT HAPPENED — EVERY STORY PINNED, NUMBERED AS IN THE TEXT",
         font(SANSB, 11), NAVY)
    draw_map(d, mx, my + 18, 316, 222)
    bx0 = mx + 328
    bw = (cw - 328) // 2 - 4
    fbf = font(SANS, 9)
    fb = font(SANSB, 9)
    for i, s in enumerate(BRIEFS):
        col, row = divmod(i, 9)
        x = bx0 + col * (bw + 8)
        y = my + 18 + row * 25
        num = "%d" % s["n"]
        text(d, (x, y), num, fb, RED_DK)
        nx = x + d.textlength(num + " ", font=fb)
        line1 = "%s — %s (%s)" % (s["place"], s["fact"], s["src"])
        lines = wrap(d, line1, fbf, bw - (nx - x))[:2]
        block(d, nx, y, bw - (nx - x), lines, fbf, INK, leading=11)

    # DATE CHECK (3 columns x 6 rows)
    dy = 896
    d.rectangle([mx, dy, mx + cw, dy + 86], outline=RED, width=2)
    d.rectangle([mx, dy, mx + cw, dy + 20], fill=RED)
    text(d, (mx + 8, dy + 4), "DATE CHECK — NOT MONDAY, LEFT OUT ON PURPOSE",
         font(SANSB, 12), (255, 255, 255))
    fe = font(SANS, 8)
    for i, (item, day) in enumerate(EXCLUDED):
        col, row = divmod(i, 6)
        x = mx + 8 + col * (cw // 3)
        y = dy + 24 + row * 10
        text(d, (x, y), "× %s — %s" % (item, day), fe, RED_DK)

    # footer
    fy = 990
    text(d, (mx + cw // 2, fy), "SOURCES: REUTERS • AP • MEA • ESPNCRICINFO • UN NEWS • IANS • "
         "XINHUA • THE GUARDIAN • BUSINESS STANDARD • FINNHUB • HANSARD SOCIETY",
         font(SANS, 8), MUTE, anchor="ma")
    text(d, (mx + cw // 2, fy + 11), "REPORTED = confirmed by the named source  •  CLAIM = one "
         "side's claim, never printed as fact  •  SCHEDULED = set for Monday",
         font(SANS, 8), MUTE, anchor="ma")

    img.save(OUT, "PNG", optimize=True)
    return OUT



# ------------------------------------------------- mini scenes (cards, 34px)
def _m(d, x, y, w, h, kind):
    """Simplified multi-element scene scaled to a short card strip."""
    if kind == "talks":
        _sky(d, x, y, w, h)
        d.rectangle([x + w * 0.15, y + h * 0.45, x + w * 0.85, y + h], fill=(232, 222, 198))
        d.pieslice([x + w * 0.4, y + h * 0.1, x + w * 0.6, y + h * 0.55], 180, 360, fill=GOLD)
        _flag(d, x + w * 0.08, y + h * 0.25, w * 0.1, h * 0.3,
              [(255, 153, 51), (255, 255, 255), (19, 136, 8)])
        _flag(d, x + w * 0.82, y + h * 0.25, w * 0.1, h * 0.3, [(220, 20, 60), (0, 56, 147)])
        _person(d, x + w * 0.42, y + h * 0.55, h * 0.45, NAVY, INK)
        _person(d, x + w * 0.58, y + h * 0.55, h * 0.45, RED_DK, INK)
    elif kind == "council":
        d.rectangle([x, y, x + w, y + h], fill=(30, 48, 88))
        d.ellipse([x + w * 0.42, y + h * 0.08, x + w * 0.58, y + h * 0.62], outline=GOLD, width=2)
        for k in range(8):
            import math
            a = k * math.pi / 4
            px = x + w * 0.5 + w * 0.07 * math.cos(a)
            py = y + h * 0.35 + h * 0.25 * math.sin(a)
            d.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5], fill=GOLD)
        d.ellipse([x + w * 0.3, y + h * 0.68, x + w * 0.7, y + h * 0.9], fill=(120, 84, 40))
        for i, fx in enumerate(range(4)):
            d.rectangle([x + w * (0.08 + i * 0.22), y + h * 0.82, x + w * (0.2 + i * 0.22), y + h * 0.95],
                        fill=NAVY2 if i % 2 else RED_DK)
    elif kind == "factory":
        _sky(d, x, y, w, h, top=(120, 110, 100), bot=(230, 220, 200))
        d.rectangle([x + w * 0.3, y + h * 0.4, x + w * 0.7, y + h], fill=(210, 196, 170))
        d.ellipse([x + w * 0.38, y + h * 0.02, x + w * 0.52, y + h * 0.4], fill=(90, 85, 80))
        d.ellipse([x + w * 0.52, y - h * 0.1, x + w * 0.68, y + h * 0.3], fill=(120, 115, 110))
        d.polygon([(x + w * 0.08, y + h * 0.75), (x + w * 0.3, y + h * 0.75), (x + w * 0.2, y + h)], fill=(255, 240, 180))
        _person(d, x + w * 0.85, y + h * 0.55, h * 0.45, RED, INK)
    elif kind == "rescue":
        _sky(d, x, y, w, h, top=(150, 160, 175), bot=(235, 230, 215))
        d.polygon([(x + w * 0.1, y + h), (x + w * 0.5, y + h * 0.2), (x + w * 0.9, y + h)], fill=(110, 100, 85))
        d.polygon([(x + w * 0.72, y + h * 0.3), (x + w * 0.98, y + h * 0.05), (x + w, y + h * 0.2)], fill=(255, 244, 190))
        d.rectangle([x + w * 0.3, y + h * 0.6, x + w * 0.45, y + h * 0.75], fill=(80, 72, 62))
        _person(d, x + w * 0.15, y + h * 0.55, h * 0.45, RED, INK)
    elif kind in ("cricket", "cricket2"):
        d.rectangle([x, y, x + w, y + h], fill=(46, 125, 60))
        d.rectangle([x + w * 0.4, y + h * 0.1, x + w * 0.6, y + h], fill=(205, 178, 120))
        for sx in (0.47, 0.5, 0.53):
            d.rectangle([x + w * sx, y + h * 0.15, x + w * sx + 2, y + h * 0.45], fill=(240, 220, 150))
        if kind == "cricket":
            d.rectangle([x + w * 0.66, y + h * 0.08, x + w * 0.95, y + h * 0.4], fill=NAVY)
            d.text((x + w * 0.68, y + h * 0.1), "720/9", font=font(SANSB, 11), fill=(255, 255, 255))
        d.ellipse([x + w * 0.7, y + h * 0.6, x + w * 0.74, y + h * 0.75], fill=RED)
    elif kind == "podium":
        _sky(d, x, y, w, h, top=(200, 210, 225), bot=(245, 242, 232))
        for i, fx in enumerate(range(5)):
            d.rectangle([x + w * (0.08 + i * 0.18), y + h * 0.1, x + w * (0.2 + i * 0.18), y + h * 0.35],
                        fill=NAVY2 if i % 2 else RED_DK)
        d.polygon([(x + w * 0.38, y + h), (x + w * 0.62, y + h), (x + w * 0.56, y + h * 0.5),
                   (x + w * 0.44, y + h * 0.5)], fill=(90, 60, 30))
        _person(d, x + w * 0.5, y + h * 0.25, h * 0.5, NAVY, INK)
    elif kind == "drone":
        _sky(d, x, y, w, h, top=(90, 120, 160), bot=(210, 225, 235))
        d.rectangle([x, y + h * 0.8, x + w, y + h], fill=(140, 135, 120))
        cx, cy = x + w * 0.5, y + h * 0.45
        d.rectangle([cx - 12, cy - 4, cx + 12, cy + 4], fill=INK)
        for dx, dy in ((-18, -8), (18, -8), (-18, 8), (18, 8)):
            d.ellipse([cx + dx - 5, cy + dy - 2, cx + dx + 5, cy + dy + 2], fill=(60, 60, 60))
        d.line([(cx, cy + 4), (cx + 22, y + h * 0.8)], fill=RED_DK, width=2)
        d.ellipse([cx + 18, y + h * 0.68, cx + 26, y + h * 0.88], fill=RED_DK)
    elif kind == "bridge":
        _sky(d, x, y, w, h, top=(200, 225, 235), bot=(245, 240, 225))
        d.rectangle([x, y + h * 0.7, x + w, y + h], fill=(90, 140, 160))
        d.polygon([(x, y + h * 0.7), (x + w, y + h * 0.7), (x + w, y + h * 0.5), (x, y + h * 0.5)], fill=(120, 150, 110))
        d.polygon([(x + w * 0.05, y + h * 0.5), (x + w * 0.5, y + h * 0.15), (x + w * 0.95, y + h * 0.5),
                   (x + w * 0.95, y + h * 0.62), (x + w * 0.05, y + h * 0.62)], fill=(150, 60, 50))
        d.ellipse([x + w * 0.85, y + h * 0.05, x + w * 0.95, y + h * 0.3], fill=(255, 220, 120))
    elif kind == "steel":
        d.rectangle([x, y, x + w, y + h], fill=(70, 70, 80))
        d.ellipse([x + w * 0.42, y + h * 0.1, x + w * 0.58, y + h * 0.95], fill=(255, 140, 40))
        d.ellipse([x + w * 0.46, y + h * 0.3, x + w * 0.54, y + h * 0.75], fill=(255, 190, 90))
        for cx in (0.12, 0.88):
            d.ellipse([x + w * cx - 10, y + h * 0.45, x + w * cx + 10, y + h * 0.95], fill=(160, 165, 170))
            d.ellipse([x + w * cx - 4, y + h * 0.6, x + w * cx + 4, y + h * 0.8], fill=(90, 95, 100))
    elif kind == "parliament":
        _sky(d, x, y, w, h, top=(210, 220, 235), bot=(245, 242, 232))
        d.rectangle([x + w * 0.1, y + h * 0.45, x + w * 0.9, y + h], fill=(225, 215, 190))
        d.pieslice([x + w * 0.42, y + h * 0.05, x + w * 0.58, y + h * 0.5], 180, 360, fill=GOLD)
        for i in range(5):
            d.rectangle([x + w * (0.16 + i * 0.15), y + h * 0.5, x + w * (0.2 + i * 0.15), y + h], fill=(200, 190, 165))
        d.rectangle([x + w * 0.06, y + h * 0.6, x + w * 0.14, y + h * 0.8], fill=INK)
    elif kind == "film":
        d.rectangle([x, y, x + w, y + h], fill=(40, 40, 55))
        d.ellipse([x + w * 0.1, y + h * 0.15, x + w * 0.3, y + h * 0.85], outline=(230, 220, 200), width=3)
        d.ellipse([x + w * 0.7, y + h * 0.15, x + w * 0.9, y + h * 0.85], outline=(230, 220, 200), width=3)
        d.polygon([(x + w * 0.38, y + h * 0.75), (x + w * 0.62, y + h * 0.75), (x + w * 0.62, y + h * 0.95),
                   (x + w * 0.38, y + h * 0.95)], fill=(20, 20, 20))
        d.polygon([(x + w * 0.38, y + h * 0.75), (x + w * 0.62, y + h * 0.75), (x + w * 0.58, y + h * 0.6),
                   (x + w * 0.42, y + h * 0.6)], fill=(240, 240, 240))
    elif kind == "claim":
        d.rectangle([x, y, x + w, y + h], fill=(250, 230, 200))
        d.ellipse([x + w * 0.42, y + h * 0.08, x + w * 0.58, y + h * 0.92], outline=RED_DK, width=3)
        d.text((x + w * 0.44, y + h * 0.18), "?", font=font(SANSB, 18), fill=RED_DK)
        d.line([(x + w * 0.1, y + h * 0.92), (x + w * 0.9, y + h * 0.92)], fill=RED_DK, width=2)
    elif kind == "ship":
        _sky(d, x, y, w, h, top=(190, 215, 230), bot=(240, 238, 228))
        d.rectangle([x, y + h * 0.7, x + w, y + h], fill=(40, 90, 120))
        d.rectangle([x + w * 0.7, y + h * 0.12, x + w * 0.78, y + h * 0.28], fill=(240, 240, 240))
        d.rectangle([x + w * 0.12, y + h * 0.28, x + w * 0.88, y + h * 0.42], fill=(200, 60, 40))
        for cx in (0.2, 0.38, 0.56, 0.74):
            d.rectangle([x + w * cx, y + h * 0.3, x + w * (cx + 0.12), y + h * 0.42], fill=(240, 200, 60))
        d.rectangle([x + w * 0.08, y + h * 0.42, x + w * 0.92, y + h * 0.72], fill=(60, 60, 70))
        d.line([(x, y + h * 0.78), (x + w, y + h * 0.78)], fill=(255, 255, 255), width=1)


if __name__ == "__main__":
    print(render())
