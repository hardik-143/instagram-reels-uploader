#!/usr/bin/env python3
"""What if a day lasted 100 hours? (~88 s)"""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, RED, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp

SUNGLOW = E.SN.SUNGLOW

def spin_offset(T):
    """Earth's land offset: fast spin, slowing down between 6 s and 9 s, then slow."""
    off, t, dt = 0.0, 4.0, 0.05
    while t < T:
        v = 140 if t < 6 else (140 - 105 * clamp((t - 6) / 3))
        off += v * dt; t += dt
    return off

@E.sfx
def crickets(dd=8.0):
    t = E.tarr(dd); s = np.zeros(len(t)); L = int(0.03 * E.SR)
    for k in range(int(dd / 0.85) + 1):
        for j in range(3):
            i = int((k * 0.85 + j * 0.045 + (0.15 if k % 2 else 0)) * E.SR)
            if i + L < len(t): s[i:i + L] += np.sin(np.linspace(0, np.pi, L))
    return np.sin(2 * np.pi * 4300 * t) * s * 0.06

@E.sfx
def alarm():
    t = E.tarr(1.2); s = np.sin(2 * np.pi * 2600 * t) * (np.sin(2 * np.pi * 14 * t) > 0)
    return s * np.minimum(1, (1.2 - t) / 0.05) * 0.18

@E.sfx
def cicadas(dd=8.0):
    t = E.tarr(dd); n = E.noise(len(t)); s = (n - E.lp(n, 2)) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * t))
    return s * np.minimum(1, t / 0.5) * np.minimum(1, (dd - t) / 0.5) * 0.08

def intro_extra(frame, d, T):
    if T < 1.9: return
    paste_c(frame, draw_char("earth", 380, T, 0, False, (0, 0), T * 140), 540, 1390, ease_back((T - 1.9) / 0.4))

def gauge(frame, d, T, sc):
    lt = T - sc["s"]
    v = 1670 - (1670 - 400) * ease_out(clamp((lt - 1.0) / 3.0))
    cx, cy, r = 540, 1150, 330
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=(30, 26, 60), outline=OUTL, width=10)
    d.arc([cx - r + 30, cy - r + 30, cx + r - 30, cy + r - 30], 180, 360, fill=(80, 70, 140), width=24)
    for k in range(11):
        a = math.radians(180 + k * 18)
        d.line([(cx + (r - 70) * math.cos(a), cy + (r - 70) * math.sin(a)), (cx + (r - 30) * math.cos(a), cy + (r - 30) * math.sin(a))], fill=WHITE, width=6)
    a = math.radians(180 + 180 * v / 2000)
    d.line([(cx, cy), (cx + (r - 60) * math.cos(a), cy + (r - 60) * math.sin(a))], fill=(255, 80, 90), width=14)
    d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=YEL, outline=OUTL, width=6)
    f = E.font(96, E.F_TITLE)
    txt = f"{int(round(v / 10) * 10):,} km/h"
    d.text((cx, cy - 120), txt, font=f, fill=YEL, anchor="mm", stroke_width=8, stroke_fill=OUTL)

def sun_in_sky(frame, d, T, sc, x=860, y=520, s=0.6):
    paste_c(frame, SUNGLOW, x, y, s)

def day_props(frame, d, T, sc):
    sun_in_sky(frame, d, T, sc, 880, 360, 0.55)

def hot_props(frame, d, T, sc):
    sun_in_sky(frame, d, T, sc, 860, 360, 0.75)
    for k in range(6):
        x = 120 + k * 170; ph = T * 2 + k
        pts = [(x + 14 * math.sin(ph + j * 0.9), 1300 - j * 40) for j in range(8)]
        d.line(pts, fill=(255, 226, 170), width=5, joint="curve")

def wall_clock(frame, d, T, sc):
    cx, cy, r = 900, 420, 110
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE, outline=OUTL, width=10)
    for k in range(12):
        a = math.radians(k * 30)
        d.line([(cx + (r - 26) * math.cos(a), cy + (r - 26) * math.sin(a)), (cx + (r - 10) * math.cos(a), cy + (r - 10) * math.sin(a))], fill=OUTL, width=5)
    a1 = T * 0.4; a2 = T * 4.8
    d.line([(cx, cy), (cx + 50 * math.sin(a1), cy - 50 * math.cos(a1))], fill=OUTL, width=10)
    d.line([(cx, cy), (cx + 82 * math.sin(a2), cy - 82 * math.cos(a2))], fill=RED, width=6)
    f = E.font(30)
    d.text((cx, cy + r + 30), "1 of 100 hrs", font=f, fill=(60, 60, 80), anchor="mm")

def storm_props(frame, d, T, sc):
    for i in range(18):
        y = 380 + (i * 97) % 1300
        x = ((i * 271) - T * 900) % 1500 - 200
        d.line([(x, y), (x + 140, y + 30)], fill=(200, 206, 216), width=5)

def uncle_state(T):
    return "angry" if T >= 53.6 else 1

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="slow", s=4.0, e=12.0, bg="space", clock="FROM 24 TO 100 HRS", char="earth", state=spin_offset,
         pos=(540, 1080, 600), narr="Earth spins once every 24 hours. Now slow it down, 4 times slower.", n_at=4.2,
         say="Ahh... finally, a SLOW life.", say_at=7.4, pitch=260),
    dict(id="speed", s=12.0, e=20.0, bg="space", clock="THE SPEED", props=gauge,
         narr="At the equator, the ground would move at about 400 km/h instead of 1,670.", n_at=12.2, narr_y=1600),
    dict(id="day", s=20.0, e=28.0, bg="day", clock="HOUR 30", char="flower", pos=(540, 1100, 560), props=day_props,
         look=(0.6, -0.6), narr="You'd get about 50 hours of sunlight in a row.", n_at=20.2,
         say="Sunscreen. I need MORE sunscreen.", say_at=21.9, pitch=700),
    dict(id="heat", s=28.0, e=36.0, bg="hot", clock="HOUR 45", char="dog", pos=(540, 1080, 600), props=hot_props,
         narr="Days that long would bake the ground far hotter than a normal afternoon.", n_at=28.2,
         say="It's been daytime for 45 HOURS.", say_at=30.3, pitch=320),
    dict(id="night", s=36.0, e=44.0, bg="night", clock="HOUR 75", char="moon", pos=(540, 1060, 560),
         narr="Then about 50 hours of darkness. Nights would turn freezing cold.", n_at=36.2,
         say="Double shift AGAIN? Seriously?", say_at=38.3, pitch=380),
    dict(id="sleep", s=44.0, e=52.0, bg="bedroom", clock="YOUR BODY", char="kid", pos=(400, 1110, 560),
         narr="Your body clock runs on about 24 hours. You might sleep 4 times a day.", n_at=44.2,
         say="Good morning... good night... good MORNING?", say_at=46.3, pitch=600),
    dict(id="monday", s=52.0, e=60.0, bg="office", clock="MONDAY", char="uncle", pos=(560, 1080, 560),
         state=uncle_state, props=wall_clock, look=(-0.6, -0.2),
         narr="And Monday? It would last 100 HOURS.", n_at=52.2,
         say="Meeting at hour 87. Don't be LATE!", say_at=54.0, pitch=230),
    dict(id="weather", s=60.0, e=68.0, bg="storm", clock="THE WEATHER", char="cloud", pos=(540, 1060, 560),
         props=storm_props, narr="A slower spin means a weaker Coriolis effect. Cyclones could lose their spin.", n_at=60.2,
         say="No spin? I'm just a regular CLOUD now.", say_at=62.5, pitch=500),
    dict(id="truth", s=68.0, e=76.0, bg="space", clock="PLOT TWIST", char="moon", pos=(540, 1060, 560), twist=True,
         narr="Plot twist: Earth IS slowing down. The Moon's tides work like brakes.", n_at=68.2,
         say="Guilty. About 2 milliseconds per century.", say_at=70.4, pitch=380),
    dict(id="future", s=76.0, e=83.0, bg="space", clock="10+ BILLION YEARS", char="sun", pos=(540, 1060, 600),
         narr="At that rate, 100-hour days are over 10 billion years away.", n_at=76.2,
         say="Sorry... I won't last THAT long.", say_at=78.2, pitch=420),
    dict(id="outro", s=83.0, e=88.0),
]

cfg = dict(
    total=88.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("A DAY LASTED", WHITE)], 124), 770, 0.75, "right"),
        (title([("100 HOURS?", YEL)], 150), 915, 1.05, "left"),
        (title([("...instead of ", WHITE), ("24", YEL)], 90), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("What would ", WHITE), ("YOU", YEL), (" do", WHITE)], 96), 470, 0.15),
                      (title([("with 100 hours?", YEL)], 110), 600, 0.45)],
               row=[("earth", 1), ("sun", 1), ("moon", 1), ("kid", 1), ("uncle", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=36.0), dict(t0=36.0, t1=67.85, minor=True),
           dict(t0=76.0, t1=83.0, drums=False, g=0.8), dict(t0=83.0, t1=88.0, melody=True)],
    drones=[dict(t0=68.0, dur=8.0, g=0.09)],
    fx=[("powerdown", 6.0, 0.8, dict(dd=2.5)), ("whoosh", 6.0, 0.5)]
       + [("tick", 13.0 + k * 0.1, 0.5, dict(f=2600)) for k in range(30)]
       + [("cicadas", 28.0, 1.0, dict(dd=8.0)), ("crickets", 36.0, 1.0, dict(dd=8.0)),
          ("alarm", 44.6, 1.0), ("alarm", 48.6, 0.8), ("gale", 60.0, 0.8, dict(dd=8.0))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_a_day_lasted_100_hours")
