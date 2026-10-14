#!/usr/bin/env python3
"""What if the atmosphere disappeared for 5 seconds?"""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

OFF = 11.0     # air vanishes
BACK = 45.0    # air returns (twist)

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

# ---------------------------------------------------------------- black-sky version of the "day" background
_black = None
def black_day():
    global _black
    if _black is None:
        a = np.array(E.bg("day").convert("RGBA")).copy()
        r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
        ys = np.arange(a.shape[0])[:, None]
        sky = (b > r + 25) & (b > g) & (ys < a.shape[0] * 0.72)
        rng = np.random.default_rng(7)
        a[sky] = (6, 6, 16, 255)
        for _ in range(260):
            y = rng.integers(0, int(H * 0.6)); x = rng.integers(0, W)
            if sky[y, x]: a[y, x] = a[y, min(W - 1, x + 1)] = (220, 220, 240, 255)
        _black = Image.fromarray(a)
    return _black

def blacken_fn(T):
    # sky drains from blue to black during the first 0.5 s after the air goes
    q = clamp((T - OFF) / 0.5)
    if q >= 1: return black_day()
    return Image.blend(E.bg("day").convert("RGBA"), black_day(), q)

def sun_small(frame, d, T, sc):
    spr = draw_char("sun", 200, T, 0, False, (0, 0.3), 1)
    comp(frame, spr, 830, 440)

def pressure_props(frame, d, T, sc):
    # arrows-free pressure hint: dots of air pressing down on the kid
    lt = T - sc["s"]
    for k in range(18):
        x = 120 + (k * 53) % 840; y = 460 + ((k * 97 + lt * 160) % 360)
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(255, 255, 255))
    l = label("~10 TONNES PER SQ METRE", 60, YEL)
    comp(frame, l, 540 - l.width / 2, 360)

def black_props(frame, d, T, sc):
    sun_small(frame, d, T, sc)

def silent_props(frame, d, T, sc):
    sun_small(frame, d, T, sc)
    # sound rings that freeze and fade, going nowhere
    lt = T - sc["s"]
    for k in range(3):
        r = 40 + k * 40
        a = int(200 * clamp(1 - lt / 3))
        if a > 0:
            d.arc([760 - r, 980 - r, 760 + r, 980 + r], -40, 40, fill=(255, 255, 255), width=8)
    m = label("MUTE", 64, YEL)
    comp(frame, m, 540 - m.width / 2, 360)

def pig_pos(T):
    t = T - 25.0
    y = 620 + 420 * clamp(t / 2.4) ** 2
    return (540, y, 420)

def pig_rot(T):
    return 25 * math.sin((T - 25.0) * 7)

def feathers(frame, d, T, sc):
    sun_small(frame, d, T, sc)
    lt = T - sc["s"]
    for k in range(5):
        x = 300 + k * 120 + 20 * math.sin(lt * 3 + k); y = 520 + (k * 37) % 90 + lt * 40
        d.ellipse([x - 26, y - 10, x + 26, y + 10], fill=(200, 205, 225), outline=OUTL, width=3)

def chai_bubbles(frame, d, T, sc):
    sun_small(frame, d, T, sc)
    lt = T - sc["s"]
    for k in range(14):
        ph = (lt * 0.9 + k / 14) % 1.0
        x = 430 + (k * 61) % 220 + 10 * math.sin(lt * 5 + k)
        y = 900 - ph * 260
        r = 8 + (k % 3) * 5
        d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 255, 255), width=5)

def fizz_props(frame, d, T, sc):
    sun_small(frame, d, T, sc)
    lt = T - sc["s"]
    for k in range(10):
        ph = (lt * 1.4 + k / 10) % 1.0
        x = 520 + (k * 23) % 80 - 40; y = 1210 - ph * 140
        d.ellipse([x - 6, y - 6, x + 6, y + 6], outline=(255, 255, 255), width=4)
    l = label("~10 SEC AWAKE", 58, YEL)
    comp(frame, l, 540 - l.width / 2, 360)

def boom_overlay(frame, T, sc):
    q = clamp((T - BACK) / 0.35)
    if q >= 1: return frame
    white = Image.new("RGBA", frame.size, (255, 255, 255, 255))
    return Image.blend(white, frame, q)

def cold_chai(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 2.0:
        x = 830; y = 1180
        spr = draw_char("chai", 230, T, 0, False, (-0.5, 0), 1)
        comp(frame, spr, x - 115, y - 115)
        for k in range(3):
            fx = x - 60 + k * 60; fy = y - 160 - 10 * math.sin(T * 4 + k)
            d.line([(fx, fy - 30), (fx, fy + 30)], fill=(150, 210, 255), width=8)
            d.line([(fx - 26, fy - 15), (fx + 26, fy + 15)], fill=(150, 210, 255), width=8)
            d.line([(fx - 26, fy + 15), (fx + 26, fy - 15)], fill=(150, 210, 255), width=8)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="air", s=4.0, e=OFF, bg="day", clock="AIR: ON", char="kid", pos=(540, 1000, 520), props=pressure_props,
         look=(0, -0.5),
         narr="Air presses on EVERY square metre of you like 10 TONNES.", n_at=4.2,
         say="I don't feel ANYTHING.", say_at=6.6, pitch=600),
    dict(id="black", s=OFF, e=18.0, bg_fn=blacken_fn, clock="AIR OFF · 1 SEC", char="kid", pos=(540, 1080, 520),
         props=black_props, look=(0.3, -0.6),
         narr="The sky turns BLACK at noon. No air, nothing to scatter sunlight.", n_at=11.2,
         say="Who switched off the SKY?!", say_at=13.6, pitch=620),
    dict(id="silent", s=18.0, e=25.0, bg_fn=lambda T: black_day(), clock="2 SEC", char="uncle", state="angry",
         pos=(540, 1060, 540), props=silent_props, look=(0.3, 0),
         narr="Total SILENCE. Sound needs air to travel, so nothing can be heard.", n_at=18.2,
         say="OYE! ...OYE?! Why so QUIET?", say_at=20.6, pitch=220),
    dict(id="pigeon", s=25.0, e=32.0, bg_fn=lambda T: black_day(), clock="3 SEC", char="pigeon", pos=pig_pos,
         rot=pig_rot, props=feathers, look=(0, 0.5),
         narr="Wings work by pushing on AIR. Nothing to push, so birds just DROP.", n_at=25.2,
         say="Flap flap... NOTHING!", say_at=27.6, pitch=520),
    dict(id="chai", s=32.0, e=39.0, bg_fn=lambda T: black_day(), clock="4 SEC", char="chai", pos=(540, 1080, 460),
         props=chai_bubbles, look=(0, -0.3),
         narr="Without air pressure, water starts BOILING, even without a stove.", n_at=32.2,
         say="I'm boiling with NO GAS on!", say_at=34.6, pitch=480),
    dict(id="fizz", s=39.0, e=BACK, bg_fn=lambda T: black_day(), clock="4.9 SEC", char="kid", pos=(540, 1000, 480),
         props=fizz_props, look=(0, 0.2),
         narr="Air rushes out of your lungs. The spit on your tongue FIZZES.", n_at=39.2,
         say="My tongue is a SODA!", say_at=41.6, pitch=620),
    dict(id="twist", s=BACK, e=52.0, bg="day", clock="5 SEC · AIR BACK", char="uncle", state="angry",
         pos=(420, 1060, 520), props_after=cold_chai, overlay=boom_overlay, twist=True, look=(0.5, 0.2),
         narr="Air rushes back with a BOOM. And the chai? Boiling made it COLD.", n_at=45.4,
         say="Who made my chai COLD?!", say_at=47.8, pitch=220),
    dict(id="outro", s=52.0, e=57.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.4)
        spr = draw_char("cloud", 300, T, 0, False, (0, 0), 1)
        paste_c(frame, spr, 540 + 200 * math.sin((T - 1.9) * 2), 1400, p)

cfg = dict(
    total=57.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("THE AIR", WHITE)], 150), 770, 0.75, "right"),
        (title([("DISAPPEARED", WHITE)], 130), 915, 1.05, "left"),
        (title([("...for ", WHITE), ("5 SECONDS?", YEL)], 96), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("What would ", WHITE), ("YOU", YEL)], 96), 470, 0.15),
                      (title([("notice first?", YEL)], 110), 600, 0.45)],
               row=[("kid", 1), ("sun", 1), ("pigeon", 1), ("chai", 1), ("uncle", "angry")]),
    # music plays while air exists; the airless seconds get only a low drone (no air, no sound)
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=OFF - 0.1, melody=True),
           dict(t0=52.0, t1=57.0, melody=True)],
    drones=[dict(t0=OFF, dur=BACK - OFF - 0.15, g=0.07)],
    fx=[("powerdown", OFF + 0.05, 0.8), ("gasp", 39.4, 0.6), ("bubbles", 32.2, 0.5, dict(dd=6.0)),
        ("boom", BACK + 0.05, 1.2), ("gale", BACK + 0.1, 0.5, dict(dd=3.0))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_the_atmosphere_disappeared")
