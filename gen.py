#!/usr/bin/env python3
"""The World in One Day - Friday 20 November 2026 (v4).
One-page broadsheet: serif display headlines, full prose decks with
attributed sources, generated editorial illustrations on every lead
and grid card, a dark world map with numbered pins, and a complete
ALSO wire list. 36 stories, 7 regions, 13 illustrated.
Deterministic: fixed data, fixed fonts, fixed-seed texture, no
network. Illustrations ship in assets/ and are composited, never
drawn, by this program."""
from PIL import Image, ImageDraw, ImageFont
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))

SER = "/usr/share/fonts/truetype/liberation/LiberationSerif-%s.ttf"
SAN = "/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf"

def SF(sz):  return ImageFont.truetype(SER % "Bold", sz)
def SI(sz):  return ImageFont.truetype(SER % "Italic", sz)
def SB(sz):  return ImageFont.truetype(SAN % "Bold", sz)
def NR(sz):  return ImageFont.truetype(SAN % "Regular", sz)
def NB(sz):  return ImageFont.truetype(SAN % "Bold", sz)
def NI(sz):  return ImageFont.truetype(SAN % "Italic", sz)

W, H = 1024, 1024
BG    = (246, 241, 228)
CARD  = (253, 250, 242)
INK   = (26, 24, 20)
RED   = (178, 32, 36)
GREY  = (110, 102, 88)
WHITE = (255, 255, 255)
DARK  = (24, 34, 52)
DECKC = (52, 48, 40)

def tw(d, s, f):
    return d.textlength(s, font=f)

def wrap(d, s, f, maxw):
    out, cur = [], ""
    for word in s.split():
        t = (cur + " " + word).strip()
        if tw(d, t, f) <= maxw or not cur:
            cur = t
        else:
            out.append(cur); cur = word
    if cur:
        out.append(cur)
    return out

def spaced(d, xy, s, f, fill, gap=2):
    x, y = xy
    for ch in s:
        d.text((x, y), ch, font=f, fill=fill)
        x += tw(d, ch, f) + gap
    return x - gap

def fit1(d, s, f, maxw):
    while s and tw(d, s, f) > maxw:
        s = s.rsplit(" ", 1)[0]
    return s

def chip(d, xy, s, fill):
    """Short high-contrast stat chip drawn over an illustration."""
    x, y = xy
    w_ = tw(d, s, NB(10)) + 14
    d.rounded_rectangle([x, y, x + w_, y + 17], 4, fill=fill)
    d.text((x + 7, y + 3), s, font=NB(10), fill=WHITE)

# ------------------------------------------------------------- texture
def grain(img, amp=7, cell=4, seed=20261120):
    """Deterministic blotchy paper texture. A fixed-seed LCG makes a
    coarse noise field; it is upscaled with bicubic smoothing and
    added to the art layer BEFORE any text is drawn, so type stays
    perfectly crisp while paper, paint and sea gain real variation."""
    gw, gh = W // cell, H // cell
    small = Image.new("L", (gw, gh))
    px = small.load()
    state = seed
    for yy in range(gh):
        for xx in range(gw):
            state = (1103515245 * state + 12345) % (2 ** 31)
            px[xx, yy] = 128 + int(((state >> 8) % 1000) / 1000.0 * 2 - 1) * amp * 3
    field = small.resize((W, H), Image.BICUBIC)
    fp = field.load()
    ip = img.load()
    for yy in range(H):
        for xx in range(W):
            delta = fp[xx, yy] - 128
            r, g, b = ip[xx, yy]
            ip[xx, yy] = (max(0, min(255, r + delta)),
                          max(0, min(255, g + delta)),
                          max(0, min(255, b + delta)))
    return img

# --------------------------------------------------------- illustrations
def art_for(name, w_, h_):
    """Load assets/<name>.jpg and cover-crop it to exactly w_ x h_."""
    path = os.path.join(HERE, "assets", name + ".jpg")
    im = Image.open(path).convert("RGB")
    sw, sh = im.size
    scale = max(w_ / sw, h_ / sh)
    nw, nh = int(sw * scale + 0.5), int(sh * scale + 0.5)
    im = im.resize((nw, nh), Image.LANCZOS)
    x0 = (nw - w_) // 2
    y0 = (nh - h_) // 2
    return im.crop((x0, y0, x0 + w_, y0 + h_))

# ------------------------------------------------------------------ map
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70), (-80, 73), (-75, 68), (-65, 60), (-55, 52), (-60, 46), (-70, 44), (-75, 40), (-76, 35), (-80, 32), (-81, 26), (-84, 20), (-90, 21), (-97, 16), (-105, 20), (-110, 24), (-114, 29), (-120, 34), (-124, 40), (-124, 46), (-130, 55), (-150, 60), (-165, 60)],
    [(-79, 9), (-72, 12), (-64, 10), (-55, 6), (-50, 0), (-44, -3), (-35, -8), (-39, -13), (-41, -22), (-48, -27), (-52, -33), (-58, -39), (-62, -41), (-65, -45), (-67, -50), (-68, -54), (-71, -54), (-73, -46), (-73, -37), (-71, -30), (-70, -20), (-75, -15), (-79, -8), (-81, -4), (-80, 1), (-77, 4)],
    [(-17, 15), (-10, 29), (-6, 35), (10, 37), (11, 34), (20, 32), (30, 31), (35, 28), (38, 22), (43, 12), (51, 12), (48, 5), (42, -5), (40, -15), (36, -22), (33, -26), (28, -33), (20, -35), (17, -32), (14, -22), (12, -15), (13, -5), (9, 4), (-8, 4), (-13, 8), (-17, 12)],
    [(-9, 43), (-2, 44), (-1, 46), (-5, 48), (0, 49), (2, 51), (5, 53), (8, 55), (8, 57), (10, 59), (18, 56), (21, 55), (24, 58), (28, 59), (30, 60), (25, 66), (20, 70), (30, 70), (40, 68), (45, 66), (40, 64), (35, 65), (32, 60), (28, 55), (23, 52), (18, 50), (14, 48), (10, 45), (12, 44), (15, 42), (18, 40), (15, 38), (12, 38), (10, 37), (3, 37), (-2, 37), (-6, 36), (-9, 37), (-9, 43)],
    [(-5, 50), (-3, 53), (-5, 55), (-3, 58), (-6, 58), (-8, 55), (-6, 52), (-5, 51)],
    [(40, 68), (60, 69), (80, 73), (100, 77), (120, 73), (140, 72), (160, 70), (178, 66), (178, 62), (160, 55), (142, 50), (140, 40), (135, 35), (127, 40), (122, 38), (120, 32), (115, 23), (108, 15), (105, 9), (100, 7), (98, 12), (95, 16), (92, 16), (89, 22), (86, 20), (80, 15), (77, 8), (72, 20), (66, 25), (61, 25), (57, 27), (52, 28), (48, 30), (44, 29), (40, 31), (36, 36), (36, 42), (40, 45), (40, 50), (38, 55), (40, 68)],
    [(113, -22), (114, -28), (115, -34), (118, -35), (124, -33), (129, -32), (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27), (151, -24), (146, -19), (142, -11), (142, -15), (139, -17), (136, -15), (135, -12), (132, -11), (130, -13), (126, -14), (122, -17), (118, -20)],
    [(167, -45), (171, -41), (174, -39), (176, -38), (174, -41), (172, -43), (169, -46), (167, -45)],
]

def draw_map(img, box, pins):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    # deep-sea vertical gradient, then graticule, then the land
    for yy in range(y0, y1):
        t = (yy - y0) / max(1, (y1 - y0))
        col = (int(28 - 10 * t), int(40 - 10 * t), int(62 - 14 * t))
        d.line([(x0, yy), (x1, yy)], fill=col)
    def proj(lon, lat):
        return (x0 + (lon + 180) / 360 * (x1 - x0), y0 + (90 - lat) / 180 * (y1 - y0))
    for lon in range(-150, 180, 30):
        gx, _ = proj(lon, 0)
        d.line([(gx, y0), (gx, y1)], fill=(36, 52, 76), width=1)
    for lat in range(-60, 90, 30):
        _, gy = proj(0, lat)
        d.line([(x0, gy), (x1, gy)], fill=(36, 52, 76), width=1)
    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=(198, 174, 122))
    for lon, lat in [(100, -2), (110, -3), (120, -2), (131, -3), (141, -4)]:
        px, py = proj(lon, lat)
        d.ellipse([px - 5, py - 2, px + 5, py + 2], fill=(198, 174, 122))
    for lon, lat in [(130, 31), (137, 35), (141, 40), (142, 44)]:
        px, py = proj(lon, lat)
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(198, 174, 122))
    pin_off = {1: (33, 53), 3: (34, 33), 6: (5, 53), 12: (16, 40)}
    for num, lon, lat in pins:
        lon, lat = pin_off.get(num, (lon, lat))
        px, py = proj(lon, lat)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED, outline=WHITE, width=2)
        s = str(num)
        fnt = NB(9 if len(s) < 2 else 8)
        d.text((px - tw(d, s, fnt) / 2, py - 5), s, font=fnt, fill=WHITE)
    d.ellipse([x0 + 10, y1 - 40, x0 + 22, y1 - 28], fill=RED, outline=WHITE, width=1)
    d.text((x0 + 26, y1 - 39), "5 SPACE", font=NB(8), fill=(200, 214, 235))
    d.text((x0 + 26, y1 - 28), "Mercury", font=NB(8), fill=(200, 214, 235))
    lx = x0 + 120
    d.ellipse([lx, y1 - 26, lx + 9, y1 - 17], fill=RED)
    d.text((lx + 13, y1 - 26), "1-3 Lead", font=NB(8), fill=(200, 214, 235))
    d.ellipse([lx + 76, y1 - 26, lx + 85, y1 - 17], fill=RED)
    d.text((lx + 89, y1 - 26), "4-13 Feature", font=NB(8), fill=(200, 214, 235))

# ------------------------------------------------------------------ data
# region codes: EU, AP, AM, OC, ME, AF, WO
LEADS = [
    dict(n=1, place="KYIV, UKRAINE", beat="WAR", scene="missiles", reg="EU",
         chip="~30 MISSILES", chipfill=(70, 16, 16),
         head="Russia fires wave of ~30 ballistic missiles at Kyiv",
         deck="Seven overnight waves hit energy and transport sites across the "
              "capital; fires burn in three districts and two foreign embassies "
              "are damaged. (Kyiv Post, Reuters)"),
    dict(n=2, place="ODISHA, INDIA", beat="CYCLONE", scene="cyclone", reg="AP",
         chip="110 KM/H", chipfill=(16, 44, 74),
         head="Cyclone Akvan makes landfall in eastern India",
         deck="Severe storm crosses the coast near Gopalpur; 300,000+ people "
              "evacuated, winds 90-100 gusting 110 km/h; 423 rescue teams "
              "deployed and schools shut. (IMD, The Hindu)"),
    dict(n=3, place="ANTALYA, TURKIYE", beat="CLIMATE", scene="cop31", reg="EU",
         chip="$120BN GAP", chipfill=(90, 30, 20),
         head="COP31 reaches its final day deadlocked",
         deck="The closing draft omits a fossil-fuel phase-out while $120bn in "
              "adaptation finance stays unresolved; hosts push a '35 by 35' "
              "clean-power goal. (UN News, Reuters)"),
]

GRID = [
    dict(n=4, place="SEOUL/TOKYO", beat="MARKETS", scene="selloff", reg="AP",
         chip="ASIA -7%", chipfill=(70, 16, 16),
         head="AI sell-off sinks Asia to worst week since 2020",
         deck="Nikkei -4.5%, KOSPI -4.7%, SoftBank -16%; MSCI Asia down 7%. (Reuters)"),
    dict(n=5, place="MERCURY", beat="SPACE", scene="mercury", reg="WO",
         chip="6BN MILES", chipfill=(14, 30, 52),
         head="BepiColombo reaches Mercury after 8 years",
         deck="ESA/JAXA probe ends 6bn-mile trip; insertion Saturday. (ESA)"),
    dict(n=6, place="BRUSSELS", beat="EUROPE", scene="eudeal", reg="EU",
         chip="RESET TALKS", chipfill=(16, 34, 62),
         head="Burnham holds first EU-UK reset summit",
         deck="Brussels hosts UK PM; agrifood, carbon links eyed. (EU Council)"),
    dict(n=7, place="TOKYO", beat="ECONOMY", scene="inflation", reg="AP",
         chip="CPI 2.3%", chipfill=(90, 30, 20),
         head="Japan inflation hits 2.3%; BoJ hike eyed",
         deck="Oct CPI rises from 2.1%; core above 2% for second month. (Reuters)"),
    dict(n=8, place="BEIJING", beat="RATES", scene="rates", reg="AP",
         chip="LPR HELD", chipfill=(52, 44, 30),
         head="China holds lending rates for 18th month",
         deck="1-year LPR stays at 3.0%, 5-year at 3.5% as expected. (PBOC)"),
    dict(n=9, place="WELLINGTON", beat="CRICKET", scene="cricket", reg="OC",
         chip="118 RECORD", chipfill=(26, 58, 26),
         head="Phillips makes history with 118 vs India",
         deck="First NZ batter with 3-format centuries in a year; 368. (ICC)"),
    dict(n=10, place="SAN SALVADOR", beat="POLITICS", scene="bukele", reg="AM",
         chip="THIRD TERM", chipfill=(30, 40, 66),
         head="Bukele registers for third-term run",
         deck="Files for Feb 2027 vote; rights groups object. (AP)"),
    dict(n=11, place="SENEGAL", beat="MIGRATION", scene="boat", reg="AF",
         chip="YENNE COAST", chipfill=(70, 30, 16),
         head="Migrant boat capsizes off Yenne: 4 dead",
         deck="Dozens missing from ~50-100 aboard; Canary surge. (Al Jazeera)"),
    dict(n=12, place="ROME", beat="LABOUR", scene="strike", reg="EU",
         chip="100 SQUARES", chipfill=(66, 16, 16),
         head="Italy's CGIL holds 24-hr general strike",
         deck="Unions rally in ~100 squares against 2027 budget. (CGIL, AFP)"),
    dict(n=13, place="BARCELONA", beat="HEALTH", scene="pill", reg="AM",
         chip="60.7% RESPONSE", chipfill=(8, 30, 32),
         head="Pancreatic cancer pill shrinks tumours 60.7%",
         deck="Daraxonrasib + chemo beats chemo alone (23-42%). (Reuters)"),
]

# (n, dateline, brief, source, region) - each brief is a complete wire
# sentence: who, what, the hard detail, and its source.
ALSO = [
    (14, "LONDON", "UK, Norway fund 100m+ for two Ukrainian naval vessels", "BBC", "EU"),
    (15, "COPENHAGEN", "Parliament approves the Greenland defence bill", "AFP", "EU"),
    (16, "WARSAW", "Poland probes objects downed during the strikes", "Reuters", "EU"),
    (17, "BERLIN", "Ukraine's allies meet; Europe 'ready to talk'", "BBC", "EU"),
    (18, "SMOLENSK", "Drone strike reported on a chemical plant", "Kyiv Indep.", "EU"),
    (19, "KHARKIV", "Drone hits a hospital; at least four hurt", "Ukrinform", "EU"),
    (20, "SEOUL", "Ruling party moves to impeach Chief Justice Cho", "SBS", "AP"),
    (21, "SEOUL", "111 students caught cheating in the Suneung exam", "officials", "AP"),
    (22, "COX'S BAZAR", "Rohingya pray in camps after the ICJ ruling", "Al Jazeera", "AP"),
    (23, "JAKARTA", "Parliament passes the asset-forfeiture bill", "Reuters", "AP"),
    (24, "WASHINGTON", "Pentagon puts the US war cost against Iran at $48.3bn", "Reuters", "AM"),
    (25, "NEW YORK", "Mamdani plans to close Rikers Island jail by 2032", "reports", "AM"),
    (26, "PORT-AU-PRINCE", "Forces kill 34 gang suspects in a raid", "Reuters", "AM"),
    (27, "FLORIDA", "St Johns River hits a record 18.3 ft; schools shut", "AP", "AM"),
    (28, "CALIFORNIA", "Attorney general subpoenas Nvidia in chip probe", "CNBC", "AM"),
    (29, "HORMUZ", "Four attacks on vessels in 96 hours, centre says", "UKMTO", "ME"),
    (30, "RIYADH", "Houthi missiles damage PIF tower; Gulf condemns", "Sky", "ME"),
    (31, "GAZA", "Israeli troops cross the Yellow Line; Hamas cries foul", "UPI", "ME"),
    (32, "BLANTYRE", "Fuel crisis: night queues, 20-litre daily cap", "Al Jazeera", "AF"),
    (33, "DAKAR", "President Faye enacts supplementary budget by decree", "AFP", "AF"),
    (34, "BOUGAINVILLE", "Rio Tinto pledges $370m for Panguna mine fleet", "Reuters", "OC"),
    (35, "CANBERRA", "CBO warns AUKUS subs could shrink the US fleet", "Reuters", "OC"),
    (36, "TONGA", "Kingdom declares emergency as El Nino drought bites", "RNZ", "OC"),
]

NUMBERS = [
    ("300,000+", "evacuated ahead of Cyclone Akvan", False),
    ("~30", "ballistic missiles fired at Kyiv", False),
    ("-7%", "Asia shares' worst week since 2020", True),
    ("2.3%", "Japan Oct headline CPI; BoJ eyed", True),
    ("118", "Phillips' historic century vs India", False),
    ("8 yrs", "BepiColombo reaches Mercury", False),
]

REGION_ORDER = [
    ("EU", "EUROPE", (58, 92, 150)),
    ("AP", "ASIA-PACIFIC", (186, 84, 52)),
    ("AM", "AMERICAS", (84, 140, 84)),
    ("OC", "OCEANIA", (110, 84, 140)),
    ("ME", "MIDEAST", (176, 128, 44)),
    ("AF", "AFRICA", (84, 118, 60)),
    ("WO", "WORLD / SPACE", (60, 60, 70)),
]

PINS = [(1, 30, 50), (2, 85, 19), (3, 31, 37), (4, 128, 31), (6, 0, 51),
        (7, 139, 36), (8, 116, 40), (9, 175, -41), (10, -89, 14),
        (11, -17, 15), (12, 12.5, 42), (13, 2, 41)]

DATECHECK = ("First reported Thursday 19 Nov, so NOT shown as Friday's news: the Trump-Xi-Putin "
             "Shenzhen summit itself - Anthropic's $83 IPO pricing & Nasdaq debut - the ICJ Myanmar "
             "Rohingya genocide verdict - GTA VI midnight launch - Senate 48-51 Iran "
             "war-powers vote - Fiona the hippo's death.")

# ---------------------------------------------------------------- layout
L, R = 22, 1002
CW = R - L

def lead_card_text(img, x, y, w_, st):
    d = ImageDraw.Draw(img)
    cy = y + 146
    kick = "%02d - %s - %s" % (st["n"], st["place"], st["beat"])
    d.text((x + 10, cy), kick, font=NB(10), fill=RED)
    cy += 15
    for ln in wrap(d, st["head"], SF(22), w_ - 20)[:2]:
        d.text((x + 10, cy), ln, font=SF(22), fill=INK)
        cy += 25
    cy += 4
    for ln in wrap(d, st["deck"], NR(11), w_ - 20)[:3]:
        d.text((x + 10, cy), ln, font=NR(11), fill=DECKC)
        cy += 13

def grid_card_text(img, x, y, w_, st):
    d = ImageDraw.Draw(img)
    cy = y + 60
    kick = "%02d - %s - %s" % (st["n"], st["place"], st["beat"])
    d.text((x + 8, cy), fit1(d, kick, NB(9), w_ - 16), font=NB(9), fill=RED)
    cy += 13
    for ln in wrap(d, st["head"], SF(14), w_ - 16)[:2]:
        d.text((x + 8, cy), ln, font=SF(14), fill=INK)
        cy += 16
    cy += 1
    for ln in wrap(d, st["deck"], NR(10), w_ - 16)[:2]:
        d.text((x + 8, cy), ln, font=NR(10), fill=DECKC)
        cy += 12

def also_item_lines(d, item, textw):
    """Wrap one ALSO brief as (word, font) tokens with a hanging
    indent: red number, bold dateline, regular brief, italic source."""
    n, place, brief, src, _reg = item
    toks = [(place, NB(9))]
    for w_ in brief.split():
        toks.append((w_, NR(9)))
    toks.append(("(%s)" % src, NI(9)))
    lines, cur, curw = [], [], 0.0
    space = tw(d, " ", NR(9))
    for w_, f in toks:
        ww = tw(d, w_, f)
        add = ww if not cur else ww + space
        if cur and curw + add > textw:
            lines.append(cur); cur, curw = [(w_, f)], ww
        else:
            cur.append((w_, f)); curw += add
    if cur:
        lines.append(cur)
    return lines

def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    counts = {}
    for st in LEADS + GRID:
        counts[st["reg"]] = counts.get(st["reg"], 0) + 1
    for _, _, _, _, reg in ALSO:
        counts[reg] = counts.get(reg, 0) + 1
    total = sum(counts.values())
    assert total == 36, total

    # ---------- art layer: frames, illustrations, map, bars ----------
    lw = (CW - 26) / 3
    lead_xy = []
    for i, st in enumerate(LEADS):
        x, y = L + i * (lw + 13), 196
        lead_xy.append((x, y))
        d.rectangle([x, y, x + lw, y + 258], fill=CARD, outline=(190, 180, 156), width=1)
        img.paste(art_for(st["scene"], int(lw - 16), 132), (int(x + 8), y + 8))
    gw = (CW - 40) / 5
    grid_xy = []
    for r_ in range(2):
        for c_ in range(5):
            x, y = L + c_ * (gw + 10), 460 + r_ * 140
            grid_xy.append((x, y))
            d.rectangle([x, y, x + gw, y + 134], fill=CARD, outline=(190, 180, 156), width=1)
            img.paste(art_for(GRID[r_ * 5 + c_]["scene"], int(gw - 12), 50), (int(x + 6), y + 6))
    # region bar segments (labels come after the grain)
    x = L
    for code, _label, col in REGION_ORDER:
        segw = CW * counts[code] / total
        d.rectangle([x, 168, x + segw - 2, 188], fill=col)
        x += segw
    # masthead rules, numbers dividers, date-check frame, footer rule
    d.rectangle([L, 103, R, 106], fill=INK)
    d.line([(L, 109), (R, 109)], fill=INK, width=1)
    cellw = CW / 6
    for i in range(1, 6):
        d.line([(L + i * cellw, 116), (L + i * cellw, 162)], fill=(190, 180, 156), width=1)
    draw_map(img, [L, 760, L + 288, 962], PINS)
    d.rectangle([L, 966, R, 993], outline=RED, width=2)
    d.line([(L, 999), (R, 999)], fill=INK, width=2)

    # ---------- texture over the art layer only ----------
    img = grain(img)
    d = ImageDraw.Draw(img)

    # ---------- text layer ----------
    spaced(d, (L, 8), "THE WORLD IN ONE DAY", NB(11), RED, gap=2)
    rtxt = "FRIDAY'S NEWS - ONE PAGE - 36 STORIES - 7 REGIONS"
    d.text((R - tw(d, rtxt, NB(10)), 9), rtxt, font=NB(10), fill=GREY)
    d.text((L, 24), "Friday 20 November 2026", font=SF(54), fill=INK)
    sub = ("Cyclone Akvan strikes India - Ballistic missiles hit Kyiv - "
           "COP31 deadlocked on final day - Asian AI sell-off")
    d.text((L, 84), fit1(d, sub, SI(15), CW), font=SI(15), fill=(150, 44, 40))
    # the day in numbers
    for i, (num, cap, isred) in enumerate(NUMBERS):
        x = L + i * cellw
        d.text((x + 8, 114), num, font=SF(25), fill=RED if isred else INK)
        for j, ln in enumerate(wrap(d, cap, NB(8), cellw - 14)[:2]):
            d.text((x + 8, 144 + j * 10), ln, font=NB(8), fill=GREY)
    # region bar labels
    x = L
    for code, label, _col in REGION_ORDER:
        segw = CW * counts[code] / total
        lab = "%s %d" % (label, counts[code])
        if tw(d, lab, NB(9)) <= segw - 8:
            d.text((x + (segw - 2 - tw(d, lab, NB(9))) / 2, 173), lab, font=NB(9), fill=WHITE)
        else:
            s = str(counts[code])
            d.text((x + (segw - 2 - tw(d, s, NB(9))) / 2, 173), s, font=NB(9), fill=WHITE)
        x += segw
    # cards: chips over the illustrations, then type
    for (x, y), st in zip(lead_xy, LEADS):
        chip(d, (x + 14, y + 14), st["chip"], st["chipfill"])
        lead_card_text(img, x, y, lw, st)
    for (x, y), st in zip(grid_xy, GRID):
        chip(d, (x + 10, y + 10), st["chip"], st["chipfill"])
        grid_card_text(img, x, y, gw, st)
    # bottom: map + ALSO
    d.text((L, 742), "WHERE IT HAPPENED", font=SB(12), fill=INK)
    ax = L + 302
    d.text((ax, 742), "ALSO ON FRIDAY 20 NOVEMBER - 23 MORE STORIES", font=SB(12), fill=INK)
    wb = "World Briefs (14-36)"
    d.text((R - tw(d, wb, NI(10)), 743), wb, font=NI(10), fill=GREY)
    colw, textoff, lh, gap = 216, 17, 10, 3
    cols_x = [ax, ax + colw + 15, ax + 2 * (colw + 15)]
    col, cy = 0, 760.0
    for item in ALSO:
        lines = also_item_lines(d, item, colw - textoff)
        need = len(lines) * lh + gap
        if cy + need > 962 and col < 2:
            col += 1; cy = 760.0
        cx = cols_x[col]
        d.text((cx, int(cy)), "%02d" % item[0], font=NB(9), fill=RED)
        for li, line in enumerate(lines):
            xx = cx + textoff
            for w_, f in line:
                d.text((xx, int(cy) + li * lh), w_, font=f,
                       fill=INK if f in (NB(9),) else DECKC)
                xx += tw(d, w_, f) + tw(d, " ", NR(9))
        cy += need
    assert col <= 2 and cy <= 962 + lh, (col, cy)
    # date check
    d.text((L + 8, 973), "DATE CHECK", font=NB(10), fill=RED)
    dx = L + 8 + tw(d, "DATE CHECK", NB(10)) + 8
    lines = wrap(d, DATECHECK, NR(9), R - dx - 8)
    d.text((dx, 969), lines[0], font=NR(9), fill=INK)
    rest = " ".join(lines[1:])
    d.text((L + 8, 980), fit1(d, rest, NR(9), CW - 16), font=NR(9), fill=INK)
    # footer
    foot = "Every story here happened, or was first reported, on Friday 20 November 2026."
    d.text((L, 1003), foot, font=NB(9), fill=INK)
    src = "Sources: Reuters, AP, AFP, BBC, IMD, UN News, Al Jazeera, ICC, EU Council, PBOC"
    d.text((R - tw(d, src, NI(8)), 1004), src, font=NI(8), fill=GREY)
    img.save(os.path.join(HERE, "entry.png"))
    print("wrote entry.png; also ends col", col, "y", cy)

if __name__ == "__main__":
    main()
