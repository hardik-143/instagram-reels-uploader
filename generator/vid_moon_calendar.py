#!/usr/bin/env python3
"""What if the calendar followed only the Moon? Facts: one Moon cycle (new moon to new moon) ~29.5 days; 12 lunar
months ~354 days vs solar year ~365 days, ~11 days short; Diwali falls on the new-moon (Amavasya) night of Kartik:
20 Oct 2025, 8 Nov 2026 (Gulf News); 2026 had an extra (adhik) Jyeshtha month, 17 May-15 June 2026 (Gulf News);
adhik maas is added every 32.5 months on average (Wikipedia, Adhika-masa). Without it festivals would slide ~11 days
earlier each year: ~8 years = ~87 days (Diwali ~mid-Aug, monsoon), ~16 years = ~174 days (Diwali ~mid-May, summer).
Real-world example: the Hijri calendar's 354-day year makes Ramadan arrive ~10-11 days earlier each year, taking
~33 years to cycle the whole Gregorian year (Gulf News). Makar Sankranti follows the Sun (Makar rashi), so it stays
around 14 January (LatestLY). Twist: Sanskrit 'mas' means both 'moon' and 'month'; English 'month' comes from Old
English 'monath', from 'mona' (moon) (Wiktionary)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

TW = 62.5
RED = (230, 60, 60)

_txt = {}
def label(txt, size=56, col=WHITE, stroke=8):
    k = (txt, size, col, stroke)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=stroke)
    return _txt[k]

def center_label(frame, txt, x, y, col=YEL, size=64, stroke=8):
    l = label(txt, size, col, stroke)
    comp(frame, l, x - l.width / 2, y - l.height / 2)

_gl = {}
def glow(frame, x, y, r, col=(255, 200, 120), s=0.8):
    k = (int(r), col, round(s, 2))
    if k not in _gl:
        R = max(2, int(r))
        yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
        q = np.clip(1 - np.sqrt(xx ** 2 + yy ** 2) / R, 0, 1) ** 2
        arr = np.zeros((2 * R + 1, 2 * R + 1, 4), np.uint8)
        arr[..., 0], arr[..., 1], arr[..., 2] = col
        arr[..., 3] = (q * 255 * s).astype(np.uint8)
        _gl[k] = Image.fromarray(arr, "RGBA")
    g = _gl[k]
    frame.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))

def calendar(frame, d, x, y, month, day, w=260, rot=0.0):
    """A tear-off calendar page centred at x,y."""
    h = w * 1.1
    d.rounded_rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], 22, fill=(255, 255, 255), outline=OUTL, width=6)
    d.rounded_rectangle([x - w / 2, y - h / 2, x + w / 2, y - h / 2 + h * 0.28], 22, fill=RED, outline=OUTL, width=6)
    for k in (-1, 1):
        d.ellipse([x + k * w * 0.25 - 12, y - h / 2 - 16, x + k * w * 0.25 + 12, y - h / 2 + 8], fill=OUTL)
    m = label(month, int(w * 0.15), WHITE, 4)
    comp(frame, m, x - m.width / 2, y - h / 2 + h * 0.14 - m.height / 2)
    dd = label(day, int(w * 0.42), OUTL, 2)
    comp(frame, dd, x - dd.width / 2, y + h * 0.14 - dd.height / 2)

def phase_moon(d, x, y, r, ph):
    """ph 0..1 (0 new, 0.5 full)."""
    d.ellipse([x - r, y - r, x + r, y + r], fill=(60, 60, 90), outline=OUTL, width=4)
    lit = math.cos(ph * 2 * math.pi)   # 1 new, -1 full
    pts = []
    side = 1 if ph < 0.5 else -1
    for i in range(41):
        a = -math.pi / 2 + math.pi * i / 40
        pts.append((x + side * r * math.cos(a), y + r * math.sin(a)))
    for i in range(41):
        a = math.pi / 2 - math.pi * i / 40
        pts.append((x + side * r * lit * math.cos(a), y + r * math.sin(a)))
    d.polygon(pts, fill=(250, 240, 200))
    d.ellipse([x - r, y - r, x + r, y + r], outline=OUTL, width=4)

# ---------------------------------------------------------------- scene props
def phases(frame, d, T, sc):
    lt = T - sc["s"]
    n = 8
    for k in range(n):
        a = math.pi + k * 2 * math.pi / n
        x = 540 + 360 * math.cos(a); y = 1060 + 330 * math.sin(a)
        if y > 1320: continue
        p = ease_back(clamp((lt - 0.2 - k * 0.12) / 0.3))
        if p > 0: phase_moon(d, x, y, 44 * p, k / n)

def twelve(frame, d, T, sc):
    lt = T - sc["s"]
    for k in range(12):
        p = ease_back(clamp((lt - 0.2 - k * 0.1) / 0.3))
        if p <= 0: continue
        x = 190 + (k % 6) * 140; y = 920 + (k // 6) * 140
        phase_moon(d, x, y, 50 * p, 0.5)
    if lt > 2.0:
        q = ease_out(clamp((lt - 2.0) / 0.8))
        d.rounded_rectangle([140, 1200, 140 + 776 * q, 1250], 12, fill=(120, 170, 255), outline=OUTL, width=4)
        center_label(frame, "354 DAYS", 140 + 776 * q / 2, 1225, WHITE, 34, 5)
    if lt > 3.2:
        d.rounded_rectangle([140, 1270, 940, 1320], 12, fill=(255, 200, 60), outline=OUTL, width=4)
        center_label(frame, "365 DAYS", 540, 1295, WHITE, 34, 5)

def diwali_cals(frame, d, T, sc):
    lt = T - sc["s"]
    calendar(frame, d, 230, 1100, "OCT 2025", "20", 240)
    if lt > 1.6:
        calendar(frame, d, 850, 1100, "NOV 2026", "8", 240)

def adhik(frame, d, T, sc):
    lt = T - sc["s"]
    for k in range(13):
        p = ease_back(clamp((lt - 0.2 - k * 0.08) / 0.3))
        if p <= 0: continue
        x = 150 + (k % 7) * 130; y = 1000 + (k // 7) * 160
        big = (k == 12)
        w = (120 if big else 100) * p
        if w < 12: continue
        col = (255, 200, 60) if big else (255, 255, 255)
        d.rounded_rectangle([x - w / 2, y - w * 0.55, x + w / 2, y + w * 0.55], 12, fill=col, outline=OUTL, width=4)
        d.rectangle([x - w / 2 + 3, y - w * 0.55 + 3, x + w / 2 - 3, y - w * 0.25], fill=RED)
    if lt > 1.8:
        center_label(frame, "+1 MONTH", 860, 1290, YEL, 50)

def slide(frame, d, T, sc):
    lt = T - sc["s"]
    # strip of months; a diya marker slides left by ~11 days a year
    months = ["JUN", "JUL", "AUG", "SEP", "OCT", "NOV"]
    x0, y = 110, 1180
    for i, m in enumerate(months):
        x = x0 + i * 150
        d.rounded_rectangle([x, y - 50, x + 140, y + 50], 14, fill=(90, 120, 220), outline=OUTL, width=4)
        center_label(frame, m, x + 70, y, WHITE, 40, 5)
    years = min(8, int(lt / 0.6))
    dx = 5 * 150 + 40 - years * 11 * 150 / 30.4
    center_label(frame, "YEAR +%d" % years, 540, 1000, YEL, 56)
    dsp = draw_char("diya", 110, T, 0, False, (0, 0), 1)
    paste_c(frame, dsp, x0 + dx, y - 110, 1)

def rain(frame, d, T, sc):
    lt = T - sc["s"]
    for k in range(40):
        ph = (lt * 1.6 + k / 40) % 1.0
        x = (k * 97) % 1080; y = 400 + ph * 950
        d.line([(x, y), (x - 10, y + 40)], fill=(170, 200, 255), width=4)

def heat(frame, d, T, sc):
    lt = T - sc["s"]
    glow(frame, 860, 520, 200, (255, 200, 80), 0.8)
    for k in range(3):
        y = 820 + k * 50
        pts = [(240 + i * 40, y + 10 * math.sin(lt * 6 + i + k)) for i in range(16)]
        d.line(pts, fill=(255, 240, 200), width=5)
    center_label(frame, "MAY", 230, 1200, YEL, 70)

def ramadan(frame, d, T, sc):
    lt = T - sc["s"]
    # crescent drifting leftwards along a year strip
    x = 880 - ((lt / 0.55) % 12) * 60
    glow(frame, x, 980, 110, (255, 240, 180), 0.6)
    d.ellipse([x - 70, 910, x + 70, 1050], fill=(250, 240, 200), outline=OUTL, width=4)
    d.ellipse([x - 40, 890, x + 100, 1030], fill=(30, 30, 70))
    d.rounded_rectangle([120, 1190, 960, 1250], 14, fill=(255, 255, 255), outline=OUTL, width=4)
    for k in range(1, 12):
        xx = 120 + k * 840 / 12
        d.line([(xx, 1195), (xx, 1245)], fill=OUTL, width=3)
    center_label(frame, "-11 DAYS / YEAR", 540, 1130, YEL, 48)

def kites(frame, d, T, sc):
    lt = T - sc["s"]
    for k, (x, y, col) in enumerate([(150, 500, (255, 90, 90)), (940, 520, (90, 200, 120))]):
        yy = y + 20 * math.sin(lt * 2 + k)
        d.polygon([(x, yy - 70), (x + 55, yy), (x, yy + 70), (x - 55, yy)], fill=col, outline=OUTL)
        d.line([(x, yy - 70), (x, yy + 70)], fill=OUTL, width=3)
        d.line([(x, yy + 70), (x - 30 + 20 * math.sin(lt * 3 + k), yy + 160)], fill=OUTL, width=3)
    calendar(frame, d, 230, 1110, "JAN", "14", 220)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 1.0:
        center_label(frame, "MAAS = MOON + MONTH", 540, 1210, YEL, 54)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="cycle", s=4.0, e=10.5, bg="night", clock="29.5 DAYS", char="moon", pos=(540, 1060, 300),
         props=phases, look=(0, 0),
         narr="One Moon cycle, new moon to new moon: about 29.5 DAYS.", n_at=4.2,
         say="I was your FIRST clock!", say_at=7.0, pitch=420),
    dict(id="twelve", s=10.5, e=17.0, bg="night", clock="354 DAYS", props=twelve,
         narr="12 Moons add up to only 354 DAYS. The Sun's year is 365. 11 days SHORT!", n_at=10.7),
    dict(id="diwali", s=17.0, e=23.5, bg="diwali", clock="19 DAYS LATE", char="diya", pos=(540, 1080, 260),
         props=diwali_cals, look=(0, -0.3),
         narr="Diwali is on a NEW MOON night: 20 Oct 2025, but 8 Nov 2026.", n_at=17.2,
         say="Why so LATE this year?", say_at=19.8, pitch=560),
    dict(id="adhik", s=23.5, e=30.0, bg="day", clock="13 MONTHS", char="uncle", pos=(540, 830, 240),
         props=adhik, look=(0, 0.4),
         narr="2026 got an EXTRA month: ADHIK MAAS. It's added about every 32.5 months.", n_at=23.7,
         say="Two Jyeshthas!", say_at=26.6, pitch=300),
    dict(id="slide", s=30.0, e=36.5, bg="night", clock="-11 DAYS A YEAR", props=slide,
         narr="Now DELETE that extra month. Festivals slide about 11 DAYS earlier every year.", n_at=30.2),
    dict(id="monsoon", s=36.5, e=43.0, bg="storm", clock="~8 YEARS", char="diya", pos=(540, 1080, 300),
         props=rain, look=(0, -0.4),
         narr="In about 8 years, Diwali lands in the MONSOON. Diyas versus rain!", n_at=36.7,
         say="Who brought an UMBRELLA?", say_at=39.4, pitch=560),
    dict(id="summer", s=43.0, e=49.5, bg="hot", clock="~16 YEARS", char="kid", pos=(560, 1080, 400),
         props=heat, look=(0, -0.3),
         narr="In about 16 years: Diwali in May's peak SUMMER heat.", n_at=43.2,
         say="Diwali with a COOLER?", say_at=45.8, pitch=640),
    dict(id="real", s=49.5, e=56.0, bg="night", clock="REAL!", props=ramadan,
         narr="It's REAL for Ramadan: no extra month, so it comes ~11 days earlier every year.", n_at=49.7),
    dict(id="sankranti", s=56.0, e=TW, bg="day", clock="14 JANUARY", char="kid", pos=(650, 1080, 360),
         props=kites, look=(0, -0.5),
         narr="But MAKAR SANKRANTI follows the SUN, so it stays near 14 JANUARY.", n_at=56.2,
         say="My kites stay PUT!", say_at=58.8, pitch=640),
    dict(id="twist", s=TW, e=69.5, bg="night", clock="WAIT...", char="moon", pos=(540, 1000, 300),
         twist=True, props=twist_props, look=(0, 0),
         narr="Twist: Sanskrit 'MAAS' meant both MOON and MONTH. English 'month' comes from 'moon' too!", n_at=62.9,
         say="The month was ALWAYS mine!", say_at=65.8, pitch=420),
    dict(id="outro", s=69.5, e=74.5),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.4)
        spr = draw_char("moon", 300, T, 0, False, (0, 0), 1)
        paste_c(frame, spr, 540, 1400, p)

cfg = dict(
    total=74.5, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("THE CALENDAR", WHITE)], 130), 770, 0.75, "right"),
        (title([("FOLLOWED ONLY", WHITE)], 120), 910, 1.05, "left"),
        (title([("the ", WHITE), ("MOON?", YEL)], 110), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Which festival would ", WHITE)], 76), 450, 0.15),
                      (title([("YOU", YEL), (" miss most?", WHITE)], 96), 570, 0.45)],
               row=[("moon", 1), ("diya", 1), ("uncle", 1), ("kid", 1), ("sun", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=TW - 0.15, melody=True),
           dict(t0=69.5, t1=74.5, melody=True)],
    fx=[("pop", 11.0, 0.3), ("ding", 19.0, 0.4), ("click", 31.0, 0.4), ("gale", 36.8, 0.4, dict(dd=5.5)),
        ("wind", 56.3, 0.3, dict(dd=5.0))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_moon_calendar")
