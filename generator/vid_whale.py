#!/usr/bin/env python3
"""What if you held your breath as long as a whale?"""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

GASP = 9.7

@E.sfx
def whalecall(dd=1.8):
    t = E.tarr(dd); x = t / dd
    f = 160 + 260 * np.sin(np.pi * x) ** 1.5 + 8 * np.sin(2 * np.pi * 6 * t)
    ph = E.osc(f); s = np.sin(ph) + 0.4 * np.sin(2 * ph)
    return s * np.minimum(1, t / 0.2) * np.minimum(1, (dd - t) / 0.4) * 0.35

def intro_extra(frame, d, T):
    if T < 1.9: return
    s = ease_back((T - 1.9) / 0.4) * (1 + 0.06 * min(1, (T - 1.9) / 2))
    paste_c(frame, draw_char("kid", 380, T, 0, False, (0, 0), "puff"), 540, 1390, s)

def rising_bubbles(frame, d, T, x0, y0, spread=80, n=7, top=840):
    for j in range(n):
        ph = (T * 0.55 + j / n) % 1.0
        bx = x0 + spread * math.sin(j * 1.9) + 10 * math.sin(T * 3 + j)
        by = y0 - 700 * ph; r = 8 + 12 * ph
        if by > top:
            d.ellipse([bx - r, by - r, bx + r, by + r], outline=(220, 245, 255), width=4)

def pool_props(frame, d, T, sc):
    if T < GASP:
        rising_bubbles(frame, d, T, 540, 1300, n=6)

def kid_state(T):
    return "puff" if T < GASP else 1

def kid_pos(T):
    if T < GASP:
        return (540 + 4 * math.sin(T * 30) * max(0, (T - 7.5) / 2), 1120, 580)
    return (540, 1120 - 260 * ease_out((T - GASP) / 0.4), 580)

def sea_props(frame, d, T, sc):
    rising_bubbles(frame, d, T, 300, 1300, spread=40, n=5, top=200)

def whale_pos(T):
    return (540 + 30 * math.sin(T * 0.8), 1080 + 20 * math.sin(T * 1.4), 660)

POP = Image.new("RGBA", (260, 300), (0, 0, 0, 0))
_d = ImageDraw.Draw(POP)
for i in range(18):
    x = 40 + (i * 53) % 180; y = 20 + (i * 37) % 70
    _d.ellipse([x, y, x + 50, y + 46], fill=(255, 246, 214), outline=OUTL, width=4)
_d.polygon([(20, 90), (240, 90), (210, 296), (50, 296)], fill=WHITE, outline=OUTL, width=6)
for x0 in (52, 120, 188):
    _d.polygon([(x0 - 8, 92), (x0 + 22, 92), (x0 + 12, 294), (x0 - 2, 294)], fill=(225, 50, 60))

def cinema_props(frame, d, T, sc):
    g = 220 + int(30 * math.sin(T * 7) * math.sin(T * 1.9))
    d.rounded_rectangle([90, 140, 990, 640], radius=10, fill=(g, g, g - 20))

def cinema_after(frame, d, T, sc):
    comp(frame, POP, 790, 1080 + 6 * math.sin(T * 3))

def heart_pos(T):
    ph = (T * 0.75) % 1.0
    pulse = 1 + 0.08 * math.exp(-ph * 10) + 0.05 * math.exp(-max(0, ph - 0.15) * 10) * (ph > 0.15)
    return (540, 1080, int(560 * pulse))

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="you", s=4.0, e=11.0, bg="pool", clock="YOU", char="kid", state=kid_state, pos=kid_pos,
         props=pool_props, narr="Most people tap out in about a minute.", n_at=4.3,
         say="Mmmph! MMMPH!", say_at=5.8, pitch=600),
    dict(id="whale", s=11.0, e=18.0, bg="sea", clock="3 HRS 42 MIN", char="whale", pos=whale_pos,
         props=sea_props, narr="A Cuvier's beaked whale once held one dive for 3 hours 42 minutes.", n_at=11.2,
         say="Amateurs.", say_at=14.0, pitch=150),
    dict(id="movie", s=18.0, e=25.0, bg="cinema", clock="MOVIE NIGHT", char="uncle", pos=(500, 1110, 560),
         look=(0, -0.6), props=cinema_props, props_after=cinema_after,
         narr="That's one breath for TWO full movies.", n_at=18.2,
         say="Interval? Don't NEED one.", say_at=19.9, pitch=230),
    dict(id="secret", s=25.0, e=32.0, bg="sea", clock="THE SECRET", char="heart", pos=heart_pos,
         props=sea_props, narr="Oxygen-packed muscles, and a heart that slows WAY down.", n_at=25.2,
         say="I slow down to save oxygen.", say_at=27.2, pitch=440),
    dict(id="catch", s=32.0, e=39.0, bg="pool", clock="THE CATCH", char="kid", pos=(540, 1120, 580), twist=True,
         narr="The catch? Whales breathe on PURPOSE. Every single breath.", n_at=32.2,
         say="Wait... I'd have to REMEMBER to breathe?", say_at=34.4, pitch=600),
    dict(id="outro", s=39.0, e=44.5),
]

cfg = dict(
    total=44.5, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU HELD", WHITE)], 140), 770, 0.75, "right"),
        (title([("YOUR BREATH", WHITE)], 128), 910, 1.05, "left"),
        (title([("...like a ", WHITE), ("WHALE?", YEL)], 92), 1055, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("How long can ", WHITE), ("YOU", YEL)], 96), 470, 0.15),
                      (title([("hold yours?", YEL)], 116), 600, 0.45)],
               row=[("kid", 1), ("whale", 1), ("uncle", 1), ("heart", 1), ("fish", 1)],
               note=text_sprite([("Try it on land only. ", WHITE), ("Never underwater.", YEL)], 40, stroke=6)),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=31.85), dict(t0=39.0, t1=44.5, melody=True)],
    fx=[("underwater", 4.0, 0.5, dict(dd=5.8)), ("bubbles", 4.2, 0.9, dict(dd=5.4)),
        ("gasp", GASP, 1.2), ("splash", GASP, 0.8),
        ("underwater", 11.0, 0.5, dict(dd=7.0)), ("whalecall", 11.4, 1.0), ("whalecall", 15.5, 0.7),
        ("heartbeat", 25.0, 0.9, dict(dd=7.0, bpm=45)), ("underwater", 25.0, 0.4, dict(dd=7.0)),
        ("underwater", 32.0, 0.35, dict(dd=7.0))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_held_your_breath_like_a_whale")
