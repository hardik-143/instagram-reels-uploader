#!/usr/bin/env python3
"""What if every mosquito on Earth vanished?"""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp

PRESS = 15.0   # the kid presses the button

@E.sfx
def buzz(dd=2.5):
    t = E.tarr(dd); f = 560 + 40 * np.sin(2 * np.pi * 3 * t)
    s = np.sign(np.sin(E.osc(f))) * 0.25 + np.sin(E.osc(f * 2)) * 0.1
    return E.lp(s, 4) * np.minimum(1, t / 0.2) * np.minimum(1, (dd - t) / 0.4) * 0.35

def button(frame, d, T, cx=820, cy=1290, pressed=False):
    d.rounded_rectangle([cx - 110, cy - 10, cx + 110, cy + 130], radius=18, fill=(70, 70, 90), outline=OUTL, width=6)
    top = cy - (10 if pressed else 50)
    if top + 30 < cy: d.rectangle([cx - 80, top + 30, cx + 80, cy], fill=(170, 20, 30))
    d.ellipse([cx - 80, top, cx + 80, top + 60], fill=(235, 45, 55), outline=OUTL, width=6)
    d.ellipse([cx - 40, top + 12, cx + 5, top + 30], fill=(255, 150, 150))

def tiny_mosquitoes(frame, d, T, n=9, alive=1.0):
    for k in range(n):
        if k / n >= alive: continue
        x = 540 + 380 * math.sin(T * (0.7 + k * 0.13) + k * 1.7)
        y = 520 + 140 * math.sin(T * (1.1 + k * 0.09) + k)
        fl = 6 * math.sin(T * 40 + k)
        d.ellipse([x - 20, y - 34 - fl, x + 2, y - 4], fill=(220, 230, 255), outline=OUTL, width=3)
        d.ellipse([x - 2, y - 34 + fl, x + 20, y - 4], fill=(220, 230, 255), outline=OUTL, width=3)
        d.line([(x - 26, y), (x + 26, y)], fill=OUTL, width=9)
        d.ellipse([x - 34, y - 8, x - 18, y + 8], fill=OUTL)
        d.line([(x - 34, y), (x - 50, y + 6)], fill=OUTL, width=3)

def button_props(frame, d, T, sc):
    alive = 1.0 if T < PRESS else max(0.0, 1 - (T - PRESS) / 1.2)
    tiny_mosquitoes(frame, d, T, alive=alive)
    button(frame, d, T, pressed=(PRESS <= T < PRESS + 0.5))

def kid_pos(T):
    reach = 0.0
    if PRESS - 0.5 <= T < PRESS + 0.6:
        reach = math.sin(math.pi * (T - PRESS + 0.5) / 1.1)
    return (380 + 120 * reach, 1100, 560)

def flash(frame, T, sc):
    t = T - PRESS
    if 0 <= t < 0.5:
        a = int(200 * (1 - t / 0.5))
        frame = Image.alpha_composite(frame, Image.new("RGBA", (W, H), (255, 255, 255, a)))
    return frame

def larvae(frame, d, T, sc):
    for k in range(7):
        x = 150 + k * 130 + 20 * math.sin(T * 2 + k)
        y = 1330 + 30 * math.sin(T * 1.5 + k * 2)
        pts = [(x + 6 * math.sin(T * 6 + k + j * 0.8), y + j * 9) for j in range(6)]
        d.line(pts, fill=(230, 230, 210), width=7, joint="curve")

def snow(frame, d, T, sc):
    for k in range(26):
        x = (k * 97 + 40 * math.sin(T + k)) % W
        y = (k * 173 + T * (60 + k % 5 * 15)) % H
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(255, 255, 255))
    if sc["id"] == "birds":
        tiny_mosquitoes(frame, d, T, n=12)

def pollen(frame, d, T, sc):
    for k in range(10):
        ph = (T * 0.4 + k / 10) % 1.0
        x = 540 + 300 * math.sin(k * 2.3) * ph
        y = 1000 - 500 * ph
        r = 7 + 3 * (k % 3)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 220, 60), outline=(200, 150, 20), width=2)

def moths(frame, d, T, sc):
    for k in range(4):
        x = 540 + 400 * math.sin(T * 0.9 + k * 1.6)
        y = 560 + 120 * math.sin(T * 1.3 + k * 2.1)
        fl = 0.6 + 0.4 * abs(math.sin(T * 12 + k))
        d.ellipse([x - 34 * fl, y - 22, x, y + 18], fill=(200, 170, 120), outline=OUTL, width=3)
        d.ellipse([x, y - 22, x + 34 * fl, y + 18], fill=(200, 170, 120), outline=OUTL, width=3)
        d.ellipse([x - 5, y - 20, x + 5, y + 22], fill=(90, 70, 50))

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="family", s=4.0, e=11.0, bg="mosquito", clock="3,500 SPECIES", char="mosquito", pos=(540, 1080, 600),
         look=(0.3, 0),
         narr="There are about 3,500 kinds of mosquitoes on Earth.", n_at=4.2,
         say="We're a BIG family.", say_at=6.3, pitch=700),
    dict(id="button", s=11.0, e=18.0, bg="bedroom", clock="ONE BUTTON", char="kid", pos=kid_pos,
         props=button_props, overlay=flash, look=(0.6, 0.1),
         narr="Press one button, and every single mosquito VANISHES.", n_at=11.2,
         say="No more BZZZ at night!", say_at=15.8, pitch=600),
    dict(id="lives", s=18.0, e=25.0, bg="day", clock="LIVES SAVED", char="heart", pos=(540, 1080, 520),
         look=(0, 0.2),
         narr="Malaria, spread by mosquitoes, killed about 610,000 people in 2024.", n_at=18.2,
         say="That's a LOT of lives saved.", say_at=21.0, pitch=220),
    dict(id="fish", s=25.0, e=32.0, bg="sea", clock="UNDERWATER", char="fish", pos=(540, 1060, 560),
         props=larvae, look=(0, 0.4),
         narr="But fish like the mosquitofish eat their larvae for LUNCH.", n_at=25.2,
         say="Hey! Where's my LUNCH?", say_at=27.8, pitch=520),
    dict(id="birds", s=32.0, e=39.0, bg="pole", clock="ARCTIC SUMMER", char="pigeon", pos=(540, 1100, 560),
         props=snow, look=(0, -0.4),
         narr="In the Arctic, birds feast on HUGE summer mosquito swarms.", n_at=32.2,
         say="My BUFFET is gone?!", say_at=34.8, pitch=480),
    dict(id="flower", s=39.0, e=46.0, bg="day", clock="POLLINATION", char="flower", pos=(540, 1100, 580),
         props=pollen, look=(0, -0.2),
         narr="Some orchids even depend on mosquitoes to carry their POLLEN.", n_at=39.2,
         say="Who's my DELIVERY guy now?", say_at=41.9, pitch=560),
    dict(id="gap", s=46.0, e=53.0, bg="night", clock="NATURE ADAPTS", char="earth", pos=(540, 1080, 520),
         props=moths, look=(0.4, -0.3),
         narr="Many scientists think other insects would quickly fill the GAP.", n_at=46.2,
         say="Nature always finds a WAY.", say_at=48.9, pitch=220),
    dict(id="twist", s=53.0, e=60.0, bg="mosquito", clock="PLOT TWIST", char="mosquito", state="wink",
         pos=(540, 1080, 600), twist=True, look=(0, 0),
         narr="Plot twist: only FEMALES bite. Male mosquitoes just drink NECTAR.", n_at=53.2,
         say="I'm basically a VEGETARIAN.", say_at=55.9, pitch=700),
    dict(id="outro", s=60.0, e=65.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        x = 540 + 60 * math.sin(T * 4); y = 1400 + 30 * math.sin(T * 7)
        paste_c(frame, draw_char("mosquito", 360, T, 0, False, (0, 0), 1), x, y, ease_back((T - 1.9) / 0.4))

cfg = dict(
    total=65.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("EVERY MOSQUITO", WHITE)], 116), 770, 0.75, "right"),
        (title([("ON EARTH", WHITE)], 140), 915, 1.05, "left"),
        (title([("...", WHITE), ("VANISHED?", YEL)], 100), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" press", WHITE)], 100), 470, 0.15),
                      (title([("the button?", YEL)], 116), 600, 0.45)],
               row=[("mosquito", 1), ("fish", 1), ("pigeon", 1), ("flower", 1), ("earth", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0), dict(t0=18.0, t1=25.0, drums=False, minor=True),
           dict(t0=25.0, t1=52.85, melody=True), dict(t0=60.0, t1=65.0, melody=True)],
    fx=[("buzz", 2.0, 0.8, dict(dd=2.0)), ("buzz", 4.3, 0.7, dict(dd=2.5)), ("buzz", 11.2, 0.6, dict(dd=3.5)),
        ("click", PRESS, 1.2), ("boom", PRESS + 0.05, 0.5), ("ding", PRESS + 0.3, 0.6),
        ("underwater", 25.0, 0.4, dict(dd=7.0)), ("bubbles", 25.3, 0.6, dict(dd=6.0)),
        ("wind", 32.0, 0.5, dict(dd=7.0)), ("buzz", 32.4, 0.5, dict(dd=3.0)),
        ("buzz", 53.4, 0.5, dict(dd=1.5))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_every_mosquito_vanished")
