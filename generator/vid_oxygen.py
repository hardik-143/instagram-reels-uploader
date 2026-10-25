#!/usr/bin/env python3
"""What if all the oxygen gas vanished for 5 seconds? Air is ~21% oxygen, so pressure drops to ~79%, about what you
feel ~2 km up (barometric formula); fire needs oxygen, so flames go out; petrol/diesel engines burn fuel with air,
so they stall; rockets carry their own oxidiser (ISRO's CE20 cryogenic upper stage burns liquid oxygen + liquid
hydrogen); CSB: oxygen-deficient air can cause unconsciousness after only one or two breaths, so hold your breath.
Twist: only the gas vanished. Your body is ~65% oxygen by weight (Live Science)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, comp, paste_c, ease_back, ease_out, clamp, text_sprite

OFF = 4.0      # oxygen vanishes
BACK = 39.0    # oxygen returns (twist)

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=64):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

# ---------------------------------------------------------------- a diya whose flame has gone out
_draw_orig = E.draw_char
def draw_char(kind, B, T, talk=0.0, blink=False, look=(0, 0), state=1):
    if kind == "diyaoff":
        spr = _draw_orig("diya", B, T, talk, blink, look, state)
        a = np.array(spr)
        cut = int(a.shape[0] * 0.56)
        a[:cut, :, 3] = 0
        return Image.fromarray(a)
    return _draw_orig(kind, B, T, talk, blink, look, state)
E.draw_char = draw_char

# ---------------------------------------------------------------- props
def air_bars(frame, d, T, sc):
    lt = T - sc["s"]
    x0, x1, y0, y1 = 140, 940, 400, 470
    n = x0 + (x1 - x0) * 0.78
    o_end = n + (x1 - x0) * 0.21 * (1 - ease_out(clamp((lt - 0.6) / 1.0)))
    d.rounded_rectangle([x0, y0, n, y1], 14, fill=(90, 150, 230), outline=OUTL, width=4)
    if o_end > n + 4:
        d.rounded_rectangle([n, y0, o_end, y1], 14, fill=(230, 70, 70), outline=OUTL, width=4)
    l = label("NITROGEN 78%", 46, WHITE); comp(frame, l, x0 + 20, y0 + 10)
    if lt < 1.4:
        l2 = label("O2 21%", 40, WHITE); comp(frame, l2, n + 6, y1 + 10)
    else:
        l2 = label("O2 GONE", 46, YEL); comp(frame, l2, n - 40, y1 + 14)
    # little pop marks by the ears
    if lt > 3.0:
        for s in (-1, 1):
            cx = 540 + s * 260
            for k in range(3):
                a = (k - 1) * 0.5
                d.line([(cx + s * 30 * math.cos(a), 960 + 30 * math.sin(a)),
                        (cx + s * 70 * math.cos(a), 960 + 70 * math.sin(a))], fill=YEL, width=8)

def smoke(d, x, y, lt, n=4):
    for k in range(n):
        ph = (lt * 0.5 + k / n) % 1.0
        yy = y - ph * 260
        xx = x + 26 * math.sin(ph * 7 + k)
        r = 14 + 26 * ph
        c = int(200 + 40 * ph)
        d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(c, c, c))

def flame_props(frame, d, T, sc):
    lt = T - sc["s"]
    # a row of small diyas, all out, each with a smoke wisp
    for x in (150, 930):
        spr = draw_char("diyaoff", 180, T, 0, False, (0, 0), 1)
        comp(frame, spr, x - 90, 1150)
        smoke(d, x, 1190, lt + x * 0.01, 3)
    smoke(d, 540, 1000, lt, 5)

def gas_stove(frame, d, T, sc):
    pass

def exhaust_props(frame, d, T, sc):
    lt = T - sc["s"]
    # exhaust puffs that stop after a moment
    if lt < 1.2:
        for k in range(4):
            ph = (lt * 2 + k / 4) % 1.0
            x = 260 - ph * 160; y = 1220 - ph * 40
            r = 16 + 24 * ph
            d.ellipse([x - r, y - r, x + r, y + r], fill=(170, 170, 170))
    if lt > 1.4:
        top_label(frame, "ENGINE: STALLED", 380, YEL, 72)
        # a few "dead" cars in the background row
        for i, x in enumerate((130, 950)):
            d.rounded_rectangle([x - 90, 1220, x + 90, 1300], 22, fill=(200, 60, 60) if i else (60, 110, 200),
                                outline=OUTL, width=4)
            d.ellipse([x - 70, 1280, x - 30, 1320], fill=(34, 34, 38)); d.ellipse([x + 30, 1280, x + 70, 1320], fill=(34, 34, 38))

def rocket_pos(T):
    t = T - 25.0
    return (540, 1150 - 260 * ease_out(clamp(t / 6.0)), 460)

def rocket_props(frame, d, T, sc):
    lt = T - sc["s"]
    t = T - 25.0
    y = 1150 - 260 * ease_out(clamp(t / 6.0))
    for k in range(7):
        ph = (lt * 1.6 + k / 7) % 1.0
        x = 540 + (k - 3) * 40 * ph * 2
        yy = y + 230 + ph * 220
        r = 24 + 40 * ph
        d.ellipse([x - r, yy - r, x + r, yy + r], fill=(235, 235, 240))
    if lt > 1.2:
        top_label(frame, "LIQUID OXYGEN ON BOARD", 380, YEL, 60)

def puff_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 1.0:
        top_label(frame, "HOLD YOUR BREATH", 380, YEL, 72)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 2.6:
        p = ease_back(clamp((lt - 2.6) / 0.4))
        l = label("65% OXYGEN", int(40 + 50 * p), YEL)
        comp(frame, l, 540 - l.width / 2, 400)

def back_overlay(frame, T, sc):
    q = clamp((T - BACK) / 0.35)
    if q >= 1: return frame
    white = Image.new("RGBA", frame.size, (255, 255, 255, 255))
    return Image.blend(white, frame, q)

S = [
    dict(id="intro", s=0.0, e=OFF),
    dict(id="thin", s=OFF, e=11.0, bg="day", clock="O2 OFF · 1 SEC", char="kid", pos=(540, 1060, 520),
         props=air_bars, look=(0, -0.4),
         narr="Air is 21% OXYGEN. Lose it and pressure drops like you're 2 KM up.", n_at=4.2,
         say="My EARS just POPPED!", say_at=7.4, pitch=620),
    dict(id="flames", s=11.0, e=18.0, bg="diwali", clock="2 SEC", char="diyaoff", pos=(540, 1080, 460),
         props=flame_props, look=(0, -0.3),
         narr="Fire NEEDS oxygen. Every diya, candle and gas stove goes OUT.", n_at=11.2,
         say="Who blew me OUT?!", say_at=13.8, pitch=560),
    dict(id="engines", s=18.0, e=25.0, bg="gully", clock="3 SEC", char="auto", pos=(540, 1080, 480),
         props=exhaust_props, look=(0.3, 0),
         narr="Petrol and diesel engines burn fuel WITH oxygen. Every auto STALLS.", n_at=18.2,
         say="Engine OFF, bhaiya!", say_at=20.8, pitch=380),
    dict(id="rocket", s=25.0, e=32.0, bg="day", clock="4 SEC", char="rocket", pos=rocket_pos,
         props=rocket_props, look=(0, -0.5),
         narr="But ROCKETS carry their own. ISRO's cryogenic stage burns LIQUID oxygen.", n_at=25.2,
         say="Not my PROBLEM!", say_at=27.8, pitch=520),
    dict(id="breath", s=32.0, e=BACK, bg="day", clock="4.9 SEC", char="kid", state="puff", pos=(540, 1060, 520),
         props=puff_props, look=(0, 0),
         narr="Safety experts warn: 1 or 2 breaths of oxygen-free air can make you FAINT.", n_at=32.2,
         say="Mmmph! NOT breathing!", say_at=34.8, pitch=640),
    dict(id="twist", s=BACK, e=46.0, bg="day", clock="5 SEC · O2 BACK", char="kid", pos=(540, 1060, 520),
         props=twist_props, overlay=back_overlay, twist=True, look=(0, 0.3),
         narr="O2 is back. Plot twist: you never lost YOURS. You are 65% OXYGEN by weight.", n_at=39.4,
         say="I'm mostly OXYGEN?!", say_at=42.0, pitch=640),
    dict(id="outro", s=46.0, e=51.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.4)
        spr = draw_char("diya", 260, T, 0, False, (0, 0), 1)
        paste_c(frame, spr, 540, 1400, p)

cfg = dict(
    total=51.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("ALL OXYGEN", WHITE)], 140), 770, 0.75, "right"),
        (title([("VANISHED", WHITE)], 150), 915, 1.05, "left"),
        (title([("...for ", WHITE), ("5 SECONDS?", YEL)], 96), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("What would ", WHITE), ("YOU", YEL)], 96), 470, 0.15),
                      (title([("miss first?", YEL)], 110), 600, 0.45)],
               row=[("kid", 1), ("diya", 1), ("auto", 1), ("rocket", 1), ("chai", 1)]),
    music=[dict(t0=0.2, t1=OFF, drums=False), dict(t0=OFF, t1=BACK - 0.15, melody=True),
           dict(t0=46.0, t1=51.0, melody=True)],
    fx=[("powerdown", OFF + 0.05, 0.8), ("pop", 7.0, 0.7), ("powerdown", 19.4, 0.6),
        ("rumble", 25.1, 0.6, dict(dd=6.0)), ("gasp", BACK + 0.1, 0.7), ("wind", BACK + 0.1, 0.4, dict(dd=3.0))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_oxygen_vanished")
