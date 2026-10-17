#!/usr/bin/env python3
"""What if you lived one year in the wettest place on Earth? (Mawsynram, Meghalaya)
Facts: Mawsynram avg ~11,872 mm/yr; Delhi normal 774.4 mm; June ~3,162 mm, July ~3,300 mm, Dec ~4 mm;
Cherrapunji 26,461 mm Aug 1860 - Jul 1861; knup bamboo rain shield (Khasi); living root bridges;
Sohra (Cherrapunji) dry-season water shortages."""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def put_label(frame, txt, cx, y, size=56, col=YEL):
    l = label(txt, size, col)
    comp(frame, l, cx - l.width / 2, y)

def rain(d, T, n=60, speed=1500, col=(200, 220, 255), slant=0.25, ymax=1330):
    for i in range(n):
        x0 = (i * 157) % (W + 200) - 100
        y = (T * speed + i * 263) % (ymax + 200) - 200
        x = x0 + slant * y * 0.3
        d.line([(x, y), (x - 60 * slant, y + 60)], fill=col, width=5)

def umbrella(d, cx, top, s=1.0, broken=False, T=0):
    r = 210 * s
    if broken:
        pts = [(cx - r, top + 40 * s), (cx - r * 0.5, top - 60 * s), (cx - r * 0.1, top + 30 * s),
               (cx + r * 0.3, top - 90 * s), (cx + r * 0.7, top + 10 * s), (cx + r, top - 40 * s), (cx + r * 0.6, top + 70 * s)]
        d.polygon(pts, fill=(220, 60, 90), outline=OUTL)
    else:
        d.pieslice([cx - r, top, cx + r, top + 2 * r * 0.75], 180, 360, fill=(220, 60, 90), outline=OUTL, width=7)
    d.line([(cx, top + r * 0.4), (cx, top + r * 1.5)], fill=OUTL, width=10)

def knup(d, cx, cy, s=1.0):
    # turtle-shell bamboo shield behind/over the head
    w, h = 300 * s, 210 * s
    d.chord([cx - w, cy - h, cx + w, cy + h], 180, 360, fill=(196, 160, 96), outline=OUTL, width=7)
    for k in range(1, 6):
        x = cx - w + k * 2 * w / 6
        d.line([(x, cy - h * math.sqrt(max(0, 1 - ((x - cx) / w) ** 2))), (x, cy)], fill=(140, 104, 56), width=5)
    for k in (0.35, 0.7):
        d.arc([cx - w * k, cy - h * k, cx + w * k, cy + h * k], 180, 360, fill=(140, 104, 56), width=5)

# ------------------------------------------------------------- scene props
def arrive_props(frame, d, T, sc): rain(d, T, 50)
def arrive_after(frame, d, T, sc):
    umbrella(d, 540, 620, 1.1)
    rain(d, T + 0.37, 20, 1700)

def bars_props(frame, d, T, sc):
    rain(d, T, 30)
    lt = T - sc["s"]; p = ease_out(clamp((lt - 0.4) / 2.0))
    base = 1270
    hD = 26 * p; hM = 400 * p
    d.rectangle([540, base - hD, 660, base], fill=(240, 180, 80), outline=OUTL, width=6)
    d.rectangle([780, base - hM, 920, base], fill=(70, 150, 230), outline=OUTL, width=6)
    put_label(frame, "DELHI", 600, base + 2, 36, WHITE)
    put_label(frame, "MAWSYNRAM", 850, base + 2, 30, WHITE)
    if p > 0.5:
        put_label(frame, "774", 600, base - hD - 66, 44)
        put_label(frame, "11,872", 850, base - hM - 66, 44)

def flood_props(frame, d, T, sc):
    lt = T - sc["s"]
    # 4-storey building, water rising to the roof
    x0, x1, base, fh = 560, 900, 1320, 100
    d.rectangle([x0, base - 4 * fh, x1, base], fill=(240, 220, 190), outline=OUTL, width=7)
    for f in range(4):
        for c in range(3):
            wx = x0 + 30 + c * 105; wy = base - (f + 1) * fh + 30
            d.rectangle([wx, wy, wx + 70, wy + 60], fill=(160, 210, 250), outline=OUTL, width=4)
    lvl = 4 * fh * ease_out(clamp(lt / 3.5))
    wave = 8 * math.sin(T * 4)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(img)
    dd.rectangle([0, base - lvl + wave, W, 1380], fill=(60, 130, 210, 150))
    frame.alpha_composite(img)
    put_label(frame, "ABOUT 12 M", 730, base - 4 * fh - 80, 52)
    rain(d, T, 40)

def july_props(frame, d, T, sc): rain(d, T, 110, 2300)
def july_after(frame, d, T, sc):
    umbrella(d, 600, 640, 1.0, broken=True, T=T)
    rain(d, T + 0.21, 40, 2400)

def knup_props(frame, d, T, sc):
    rain(d, T, 60)
    # paddy terrace
    for k in range(3):
        y = 1180 + k * 50
        d.rectangle([0, y, W, y + 50], fill=(110 + k * 20, 170 + k * 10, 90), outline=OUTL, width=3)
def knup_after(frame, d, T, sc):
    cx, cy, B = 540, 1080, 520
    bob = 8 * math.sin(T * 3.2)
    knup(d, cx, cy - B * 0.22 + bob, 1.0)
    rain(d, T + 0.4, 25, 1700)

def loud_props(frame, d, T, sc):
    rain(d, T, 120, 2400, (180, 200, 240))
    # tin roof over the kid
    d.polygon([(160, 760), (920, 760), (1000, 860), (80, 860)], fill=(150, 160, 170), outline=OUTL)
    for k in range(10):
        x = 120 + k * 88
        d.line([(x + 40, 768), (x, 852)], fill=(120, 130, 140), width=4)
    for k in range(6):
        x = 150 + (k * 160 + int(T * 30) * 37) % 800
        d.text((x, 700 + (k % 2) * 20), "TAP", fill=WHITE, stroke_width=4, stroke_fill=OUTL,
               font=E.font(40))

def bridge_props(frame, d, T, sc):
    rain(d, T, 30)
    # stream
    d.rectangle([0, 1250, W, 1330], fill=(70, 150, 210))
    for k in range(5):
        x = (k * 240 + T * 80) % W
        d.arc([x - 40, 1262, x + 40, 1292], 200, 340, fill=WHITE, width=4)
    # two trees and a root bridge
    for tx in (90, 990):
        d.rectangle([tx - 45, 760, tx + 45, 1260], fill=(110, 80, 50), outline=OUTL, width=6)
        d.ellipse([tx - 150, 640, tx + 150, 880], fill=(60, 140, 70), outline=OUTL, width=6)
    for k in range(6):
        off = k * 10
        d.arc([60, 980 + off, 1020, 1300 + off], 200, 340, fill=(130, 96, 60), width=12)
    d.arc([60, 990, 1020, 1300], 200, 340, fill=OUTL, width=4)

def record_props(frame, d, T, sc):
    rain(d, T, 70, 2000)
    lt = T - sc["s"]
    x0, x1, base, fh = 600, 880, 1300, 46
    n = int(9 * ease_out(clamp(lt / 3.0)))
    for f in range(9):
        y = base - (f + 1) * fh
        d.rectangle([x0, y, x1, y + fh], fill=(240, 220, 190), outline=OUTL, width=4)
        if f < n:
            d.rectangle([x0 + 4, y + 4, x1 - 4, y + fh - 4], fill=(60, 130, 210))
    put_label(frame, "26 M", 740, base - 9 * fh - 80, 56)

def dry_props(frame, d, T, sc):
    # cracked dry ground, empty bucket
    d.rectangle([0, 1250, W, 1340], fill=(200, 160, 110))
    for k in range(8):
        x = 60 + k * 130
        d.line([(x, 1260), (x + 30, 1300), (x - 10, 1330)], fill=(140, 100, 60), width=4)
    bx, by = 820, 1250
    d.polygon([(bx - 80, by - 150), (bx + 80, by - 150), (bx + 60, by), (bx - 60, by)], fill=(90, 150, 220), outline=OUTL)
    d.arc([bx - 70, by - 230, bx + 70, by - 90], 200, 340, fill=OUTL, width=6)
    put_label(frame, "DEC: ABOUT 4 mm", 540, 860, 52)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="arrive", s=4.0, e=11.0, bg="storm", clock="DAY 1", char="kid", pos=(540, 1100, 460),
         props=arrive_props, props_after=arrive_after, look=(0, -0.3),
         narr="Meet MAWSYNRAM, Meghalaya: one of Earth's WETTEST places.", n_at=4.2,
         say="Just a LITTLE drizzle, na?", say_at=7.0, pitch=600, bubble_y=520),
    dict(id="bars", s=11.0, e=18.0, bg="storm", clock="1 YEAR OF RAIN", char="cloud", pos=(280, 1060, 420),
         props=bars_props, look=(0.6, 0.2),
         narr="About 11,800 mm of rain a year. Delhi gets about 770. 15x MORE!", n_at=11.2,
         say="I'm working OVERTIME!", say_at=14.2, pitch=420),
    dict(id="flood", s=18.0, e=25.0, bg="storm", clock="IF IT NEVER DRAINED", char="kid", pos=(280, 1100, 400),
         props=flood_props, look=(0.6, -0.2), state="puff",
         narr="If none drained away, a year's rain would stand nearly 12 METRES deep.", n_at=18.2,
         say="That's a 4-STOREY building!", say_at=21.2, pitch=620, bubble_y=640),
    dict(id="july", s=25.0, e=32.0, bg="storm", clock="JUNE + JULY", char="kid", pos=(540, 1110, 440),
         props=july_props, props_after=july_after, look=(0, -0.4),
         narr="June and July EACH bring more than 3 METRES of rain.", n_at=25.2,
         say="My umbrella just RESIGNED.", say_at=27.8, pitch=600, bubble_y=500),
    dict(id="knup", s=32.0, e=39.0, bg="storm", clock="THE LOCAL FIX", char="kid", pos=(540, 1080, 520),
         props=knup_props, props_after=knup_after, look=(0, 0.2),
         narr="Locals wear a KNUP: a bamboo rain shield. Hands stay FREE!", n_at=32.2,
         say="Hands-free UMBRELLA!", say_at=35.0, pitch=620, bubble_y=500),
    dict(id="loud", s=39.0, e=46.0, bg="storm", clock="MONSOON", char="kid", pos=(540, 1110, 440),
         props=loud_props, look=(0, -0.3),
         narr="Rain on roofs gets so LOUD people talk louder. No sunshine for DAYS.", n_at=39.2,
         say="WHAT?! I can't HEAR you!", say_at=42.4, pitch=640, bubble_y=560),
    dict(id="bridge", s=46.0, e=53.0, bg="storm", clock="MEGHALAYA MAGIC", char="kid", pos=(540, 1010, 300),
         props=bridge_props, look=(0, 0.2),
         narr="Khasi villagers GROW bridges from living ROOTS. Some last centuries.", n_at=46.2,
         say="A bridge that GROWS?!", say_at=49.0, pitch=620, bubble_y=520),
    dict(id="record", s=53.0, e=60.0, bg="storm", clock="WORLD RECORD", char="kid", pos=(280, 1100, 400),
         props=record_props, look=(0.6, -0.3), state="puff",
         narr="Nearby CHERRAPUNJI once got 26,461 mm in 12 months. 26 METRES!", n_at=53.2,
         say="That's a 9-STOREY flood!", say_at=56.2, pitch=640, bubble_y=640),
    dict(id="twist", s=60.0, e=67.5, bg="hot", clock="DECEMBER", char="kid", pos=(300, 1100, 420),
         props=dry_props, twist=True, look=(0.6, 0.2),
         narr="But winter is almost DRY. Nearby Sohra even runs SHORT of drinking water.", n_at=60.2,
         say="Wettest place... and THIRSTY?!", say_at=63.2, pitch=620, bubble_y=640),
    dict(id="outro", s=67.5, e=72.5),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        rain(d, T, 40, 1600, (200, 220, 255), 0.25, 1920)

cfg = dict(
    total=72.5, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU LIVED 1 YEAR", WHITE)], 116), 770, 0.75, "right"),
        (title([("in the ", WHITE), ("WETTEST", YEL)], 130), 915, 1.05, "left"),
        (title([("place on ", WHITE), ("EARTH?", YEL)], 100), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Could", WHITE), (" YOU", YEL), (" survive", WHITE)], 92), 470, 0.15),
                      (title([("a year of rain?", WHITE)], 92), 600, 0.45)],
               row=[("kid", 1), ("cloud", 1), ("fish", 1), ("flower", 1), ("chai", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=59.85, minor=True), dict(t0=67.5, t1=72.5, melody=True)],
    drones=[dict(t0=60.0, dur=7.5, g=0.08)],
    fx=[("gale", 4.1, 0.35, dict(dd=21.0)), ("gale", 25.1, 0.5, dict(dd=7.0)), ("crash", 27.0, 0.4),
        ("gale", 32.1, 0.3, dict(dd=21.0)), ("waves", 46.1, 0.4, dict(dd=7.0)), ("gale", 53.1, 0.45, dict(dd=6.5))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_wettest_place")
