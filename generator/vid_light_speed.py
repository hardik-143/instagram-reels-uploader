#!/usr/bin/env python3
"""What if you travelled near light speed? Facts: light ~299,792 km/s; Earth circumference 40,075 km -> ~7.5 laps a
second. Parker Solar Probe, fastest human-made object, ~692,000 km/h (430,000 mph) at its Dec 2024 perihelion, about
0.064% of light speed (NASA via earth.com, scienceblog). Time dilation gamma = 1/sqrt(1 - v^2/c^2): 90% -> 2.29,
99% -> 7.09, 99.9999% -> 707. Proxima Centauri is 4.24 light-years away: round trip at 0.99c = 8.57 Earth years,
8.57/7.09 = 1.21 years on board (ignoring acceleration). LHC protons reach 99.9999991% of light speed (CERN Bulletin
'The LHC in numbers'); reaching c would need infinite energy. Muons form ~15 km up, live ~2.2 microseconds, would
travel only ~660 m without time dilation, yet reach the ground (CERN HST muon lifetime notes; Frisch-Smith 1963 via
Wikipedia 'Experimental testing of time dilation'). Twist: special relativity allows travel into the future but gives
no way back to the past."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 53.0
BEAM = (255, 245, 170)

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=68):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

def mini(frame, kind, x, y, size, T, state=1, look=(0, 0.2), talk=0.0, rot=0):
    size = max(2, int(size))
    spr = draw_char(kind, size, T, talk, False, look, state)
    if rot: spr = spr.rotate(rot, resample=Image.BICUBIC, expand=False)
    comp(frame, spr, x - size / 2, y - size / 2)

def clock(d, cx, cy, r, ang, col=WHITE):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col, outline=OUTL, width=8)
    for k in range(12):
        a = k * math.pi / 6
        d.line([(cx + 0.8 * r * math.sin(a), cy - 0.8 * r * math.cos(a)),
                (cx + 0.92 * r * math.sin(a), cy - 0.92 * r * math.cos(a))], fill=OUTL, width=5)
    d.line([(cx, cy), (cx + 0.75 * r * math.sin(ang), cy - 0.75 * r * math.cos(ang))], fill=(230, 60, 60), width=9)
    d.line([(cx, cy), (cx + 0.45 * r * math.sin(ang / 12), cy - 0.45 * r * math.cos(ang / 12))], fill=OUTL, width=11)
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=OUTL)

def streaks(d, T, n=40, speed=2600, seed=2, ymin=450, ymax=1450):
    rng = np.random.default_rng(seed)
    for k in range(n):
        y = rng.uniform(ymin, ymax)
        ln = rng.uniform(80, 300)
        x = (rng.uniform(0, 1500) - T * speed) % 1500 - 200
        d.line([(x, y), (x + ln, y)], fill=(200, 220, 255), width=4)

# ---------------------------------------------------------------- props
def light_props(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy, R = 540, 1100, 260
    mini(frame, "earth", cx, cy, 340, T, state=T * 0.2)
    a = lt * 2 * math.pi * 1.3
    for j in range(14):
        aa = a - j * 0.09
        x, y = cx + R * math.cos(aa), cy + R * 0.9 * math.sin(aa)
        r = 16 - j
        d.ellipse([x - r, y - r, x + r, y + r], fill=BEAM)
    if lt > 0.5:
        top_label(frame, "300,000 KM/S", 380, YEL, 96)

def probe_pos(T):
    return (300 + 40 * math.sin(T * 2), 1080, 300)

def probe_props(frame, d, T, sc):
    lt = T - sc["s"]
    streaks(d, T, 20, 900)
    # progress bar to light speed
    x0, x1, y = 120, 960, 1300
    d.rounded_rectangle([x0, y, x1, y + 60], radius=30, fill=(40, 50, 90), outline=OUTL, width=6)
    d.rounded_rectangle([x0, y, x0 + 26, y + 60], radius=30, fill=YEL, outline=OUTL, width=4)
    l = label("LIGHT", 48, BEAM); comp(frame, l, x1 - l.width, y - 70)
    l = label("US", 48, YEL); comp(frame, l, x0, y - 70)
    if lt > 0.5:
        top_label(frame, "0.064% OF LIGHT", 380, YEL, 84)

def clocks_props(frame, d, T, sc, slow=2.29, tag="90% = 2.3x SLOWER"):
    lt = T - sc["s"]
    a = lt * 2 * math.pi * 0.6
    clock(d, 270, 1060, 150, a)
    clock(d, 810, 1060, 150, a / slow, col=(220, 235, 255))
    l = label("EARTH", 56, WHITE); comp(frame, l, 270 - l.width / 2, 1240)
    l = label("YOU", 56, YEL); comp(frame, l, 810 - l.width / 2, 1240)
    streaks(d, T, 12, 2200, 5)
    if lt > 0.5:
        top_label(frame, tag, 380, YEL, 80)

def twins_props(frame, d, T, sc):
    lt = T - sc["s"]
    mini(frame, "earth", 200, 1300, 160, T, state=T * 0.2)
    l = label("TWIN: +8.6 YEARS", 52, WHITE); comp(frame, l, 120, 1000)
    l = label("YOU: +1.2", 52, YEL); comp(frame, l, 640, 1000)
    # star on the far right
    sx, sy = 960, 1260
    for k in range(8):
        a = k * math.pi / 4 + T
        d.line([(sx, sy), (sx + 50 * math.cos(a), sy + 50 * math.sin(a))], fill=(255, 200, 120), width=5)
    d.ellipse([sx - 28, sy - 28, sx + 28, sy + 28], fill=(255, 150, 90), outline=OUTL, width=5)
    if lt > 0.5:
        top_label(frame, "TRIP TO PROXIMA", 380, YEL, 84)

def far_props(frame, d, T, sc):
    lt = T - sc["s"]
    streaks(d, T, 40, 3200, 7)
    if lt > 0.5:
        top_label(frame, "1 YEAR = 707 YEARS", 380, YEL, 80)

def wall_props(frame, d, T, sc):
    lt = T - sc["s"]
    # a glowing wall the rocket can never reach
    x = 860
    for k in range(6):
        d.rectangle([x + k * 8, 920, x + k * 8 + 6, 1420], fill=(255, 245 - k * 20, 170 - k * 20))
    l = label("100%", 64, BEAM); comp(frame, l, x + 24 - l.width / 2, 830)
    # energy meter
    g = clamp((lt - 0.5) / 5.5)
    hgt = 500 * (g ** 4)
    d.rounded_rectangle([110, 900, 190, 1420], radius=20, fill=(40, 50, 90), outline=OUTL, width=6)
    d.rectangle([120, 1410 - hgt, 180, 1410], fill=(255, 90, 60))
    l = label("ENERGY", 44, WHITE); comp(frame, l, 150 - l.width / 2, 840)
    if lt > 0.5:
        top_label(frame, "CERN: 99.9999991%", 380, YEL, 80)

def wall_pos(T):
    return (640 + 30 * math.sin(T * 3), 1100, 300)

def muon_props(frame, d, T, sc):
    lt = T - sc["s"]
    d.rectangle([0, 1340, W, 1420], fill=(90, 150, 90), outline=OUTL, width=6)
    l = label("15 KM UP", 48, WHITE); comp(frame, l, 560, 830)
    for k in range(9):
        x = 600 + k * 50
        ph = (lt * 0.8 + k * 0.13) % 1.0
        y = 920 + 420 * ph
        d.line([(x, y - 60), (x, y)], fill=(255, 140, 220), width=6)
        d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=(255, 120, 210), outline=OUTL, width=3)
    if lt > 0.5:
        top_label(frame, "PROOF: MUONS", 380, YEL, 90)

def ticket_props(frame, d, T, sc):
    lt = T - sc["s"]
    tx, ty = 760, 1180
    rot = 6 * math.sin(T * 2)
    L = Image.new("RGBA", (420, 240), (0, 0, 0, 0)); td = ImageDraw.Draw(L)
    td.rounded_rectangle([6, 6, 414, 234], radius=24, fill=(255, 225, 120), outline=OUTL, width=7)
    td.line([(300, 20), (300, 220)], fill=OUTL, width=4)
    s1 = label("FUTURE", 54, (200, 50, 50)); L.alpha_composite(s1, (int(150 - s1.width / 2), 50))
    s2 = label("ONE WAY", 44, WHITE); L.alpha_composite(s2, (int(150 - s2.width / 2), 130))
    L = L.rotate(rot, resample=Image.BICUBIC, expand=True)
    comp(frame, L, tx - L.width / 2, ty - L.height / 2)
    if lt > 0.5:
        top_label(frame, "NO RETURN TICKET", 380, YEL, 84)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="light", s=4.0, e=11.0, bg="space", clock="SPEED CHECK", props=light_props,
         narr="Light covers 300,000 KM every second: 7.5 laps around EARTH.", n_at=4.2, narr_y=1560),
    dict(id="probe", s=11.0, e=18.0, bg="space", clock="OUR BEST", props=probe_props, char="rocket", pos=probe_pos,
         look=(0.6, 0),
         narr="Our fastest probe hit about 690,000 KM/H. That's under 0.1% of light speed.",
         n_at=11.2, narr_y=1560, say="I'm SO slow?!", say_at=14.4, pitch=260),
    dict(id="ninety", s=18.0, e=25.0, bg="space", clock="90% SPEED", props=clocks_props,
         narr="At 90% of light speed, your clock ticks LESS than half as fast as Earth's.", n_at=18.2,
         narr_y=1560),
    dict(id="twins", s=25.0, e=32.0, bg="space", clock="99% SPEED", props=twins_props, char="kid",
         pos=(760, 1220, 260), look=(-0.5, 0),
         narr="At 99%, fly to the nearest star and back: Earth waits 8.6 YEARS, you age 1.2.", n_at=25.2,
         narr_y=1560, say="Why is my TWIN older now?!", say_at=28.2, pitch=440),
    dict(id="far", s=32.0, e=39.0, bg="space", clock="99.9999% SPEED", props=far_props, char="uncle", state="hat",
         pos=(540, 1100, 380), look=(0.3, 0),
         narr="At 99.9999%, ONE year on board = about 707 YEARS on Earth.", n_at=32.2, narr_y=1560,
         say="Is CHAI still 10 rupees?", say_at=35.2, pitch=150),
    dict(id="wall", s=39.0, e=46.0, bg="space", clock="100%?", props=wall_props, char="rocket", pos=wall_pos,
         look=(0.6, 0),
         narr="CERN pushes protons to 99.9999991%. But 100% would need INFINITE energy.", n_at=39.2,
         narr_y=1560, say="Almost... ALMOST...", say_at=42.4, pitch=260),
    dict(id="muon", s=46.0, e=TW, bg="day", clock="IS IT REAL?", props=muon_props, char="kid",
         pos=(280, 1180, 320), look=(0.6, -0.5),
         narr="Yes! MUONS made 15 km up should die in 660 m. Slow clocks let them reach the GROUND.", n_at=46.2,
         narr_y=1560, say="They're hitting ME?!", say_at=49.2, pitch=440),
    dict(id="twist", s=TW, e=60.0, bg="space", clock="PLOT TWIST", char="uncle", state="hat", pos=(300, 1150, 360),
         props=ticket_props, twist=True, look=(0.6, 0),
         narr="Twist: it's ONE-WAY. Speed can skip you into the FUTURE, but physics has no road back.",
         n_at=TW + 0.2, narr_y=1560, say="Wait, I wanted a RETURN ticket!", say_at=TW + 3.2, pitch=150),
    dict(id="outro", s=60.0, e=65.0),
]

def intro_extra(frame, d, T):
    streaks(d, T, 18, 2400, 9, 1150, 1700)
    if T >= 1.9:
        p = min(ease_back((T - 1.9) / 0.4), 1.2)
        mini(frame, "rocket", 540, 1390 + 12 * math.sin(T * 2), 300 * p, T, look=(0.6, 0))

cfg = dict(
    total=65.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU TRAVELLED NEAR", WHITE)], 100), 770, 0.75, "right"),
        (title([("LIGHT SPEED?", YEL)], 150), 900, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" take the", WHITE)], 100), 470, 0.15),
                      (title([("one-way trip?", YEL)], 96), 600, 0.45)],
               row=[("rocket", 1), ("earth", 1), ("kid", 1), ("sun", 1), ("uncle", "hat")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0, melody=True),
           dict(t0=18.0, t1=32.0), dict(t0=32.0, t1=46.0, melody=True),
           dict(t0=46.0, t1=TW - 0.15, drums=False, minor=True), dict(t0=TW + 2.0, t1=65.0, melody=True)],
    drones=[dict(t0=18.0, dur=7.0, g=0.2)],
    fx=[("whoosh", 4.5, 0.3), ("whoosh", 11.5, 0.3), ("tick", 19.0, 0.2), ("tick", 20.0, 0.2), ("tick", 21.0, 0.2),
        ("whoosh", 25.5, 0.3), ("rumble", 32.4, 0.25, dict(dd=6.0)), ("rumble", 39.4, 0.3, dict(dd=6.0)),
        ("pop", 47.0, 0.25), ("pop", 48.0, 0.25)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_travelled_near_light_speed")
