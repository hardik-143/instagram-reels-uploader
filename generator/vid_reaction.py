#!/usr/bin/env python3
"""What if your reaction time were 10x faster? Phone catch, 150 km/h bouncer, auto brakes, false-start twist."""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

TWIST = 39.0

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=360, col=YEL, size=60):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

def phone(d, x, y, rot_crack=False):
    d.rounded_rectangle([x - 42, y - 78, x + 42, y + 78], radius=14, fill=(40, 40, 50), outline=OUTL, width=5)
    d.rounded_rectangle([x - 32, y - 64, x + 32, y + 60], radius=6, fill=(120, 190, 250))
    if rot_crack:
        d.line([(x - 30, y - 50), (x + 4, y - 4), (x - 10, y + 20), (x + 28, y + 56)], fill=WHITE, width=5)
        d.line([(x + 4, y - 4), (x + 30, y - 30)], fill=WHITE, width=4)

def ball(d, x, y, r):
    d.ellipse([x - r, y - r, x + r, y + r], fill=(200, 30, 40), outline=OUTL, width=max(2, int(r / 6)))
    d.arc([x - r * 0.9, y - r * 1.4, x + r * 0.9, y + r * 0.6], 20, 160, fill=WHITE, width=max(2, int(r / 8)))

# ---------------------------------------------------------------- props
def normal_props(frame, d, T, sc):
    top_label(frame, "TYPICAL: ~0.25 SEC")
    lt = T - sc["s"]
    # phone slips at 3.6 s and hits the floor before the kid reacts
    t = lt - 3.6
    if t < 0:
        phone(d, 690, 1010)
    else:
        y = 1010 + 1600 * min(t, 0.4) ** 2
        phone(d, 690, min(y, 1260), rot_crack=t > 0.4)

def phone_props(frame, d, T, sc):
    lt = T - sc["s"]
    top_label(frame, "NORMAL: 31 CM DROP", 340, WHITE, 52)
    top_label(frame, "YOU: 3 MM DROP", 410, YEL, 60)
    wob = 4 * math.sin(T * 9) if 1.0 < lt < 2.0 else 0
    phone(d, 690 + wob, 1010)
    if lt > 1.0:
        for k in range(5):
            a = math.radians(-60 + k * 30)
            d.line([(690 + 110 * math.cos(a), 1010 + 110 * math.sin(a)),
                    (690 + 150 * math.cos(a), 1010 + 150 * math.sin(a))], fill=YEL, width=7)

def bouncer_after(frame, d, T, sc):
    lt = T - sc["s"]
    p = (lt % 2.2) / 2.2   # ball flies toward camera on a loop
    x = 540 + 260 * p; y = 560 + 620 * p - 160 * math.sin(math.pi * min(1, p * 1.6))
    ball(d, x, y, 14 + 70 * p ** 2)
    top_label(frame, "~0.5 SEC TO REACT")

def onemetre_props(frame, d, T, sc):
    # ball frozen just after release, near the far end
    bx, by = 540, 560
    ball(d, bx, by, 18)
    d.line([(400, 620), (680, 620)], fill=YEL, width=6)
    d.line([(400, 600), (400, 640)], fill=YEL, width=6); d.line([(680, 600), (680, 640)], fill=YEL, width=6)
    top_label(frame, "BALL MOVED: 1 M")

def auto_pos(T):
    lt = T - 32.0
    x = 300 + 240 * ease_out(clamp(lt / 1.6))
    return (x, 1120, 460)

def auto_props(frame, d, T, sc):
    top_label(frame, "IN 0.25 SEC: 4 M", 340, WHITE, 52)
    top_label(frame, "IN 0.025 SEC: 40 CM", 410, YEL, 60)
    lt = T - sc["s"]
    if lt > 1.6:
        for k in range(3):
            y = 1250 + k * 18
            d.line([(140, y), (300, y)], fill=(70, 70, 70), width=6)

def lanes_props(frame, d, T, sc):
    for y in (1230, 1330):
        d.line([(0, y), (W, y)], fill=WHITE, width=6)
    d.line([(150, 1130), (150, 1330)], fill=WHITE, width=8)
    lt = T - sc["s"]
    # the kid already off the blocks
    x = 200 + 120 * ease_out(clamp(lt / 0.6))
    comp(frame, draw_char("kid", 300, T, 0, False, (0.6, 0), 1), x - 150, 960)
    if lt > 1.0:
        top_label(frame, "FALSE START!", 360, (255, 80, 80), 72)

def flag_after(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 0.8:
        fx, fy = 940, 800
        d.line([(fx, fy), (fx, fy + 220)], fill=(60, 60, 60), width=10)
        d.rectangle([fx, fy, fx + 110, fy + 70], fill=(230, 40, 40), outline=OUTL, width=4)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="normal", s=4.0, e=11.0, bg="living", clock="REACTION · NORMAL", char="kid", pos=(400, 1080, 520),
         props=normal_props, look=(0.4, 0.1),
         narr="Right now, your brain needs about 0.25 SECONDS to react to what you see.", n_at=4.2,
         say="Nobody is faster than ME.", say_at=6.3, pitch=620),
    dict(id="phone", s=11.0, e=18.0, bg="living", clock="REACTION · 10x", char="kid", pos=(400, 1080, 520),
         props=phone_props, look=(0.5, 0),
         narr="Make it 10x faster: 0.025 SEC. A falling phone drops just 3 MM.", n_at=11.2,
         say="Caught it. ZERO cracks!", say_at=13.6, pitch=640),
    dict(id="bouncer", s=18.0, e=25.0, bg="stadium", clock="REACTION · NORMAL", char="bat", pos=(540, 1130, 480),
         props_after=bouncer_after, look=(0, -0.4),
         narr="A 150 KM/H bouncer reaches the batter in about HALF A SECOND.", n_at=18.2,
         say="Normally? Pure PANIC.", say_at=20.6, pitch=420),
    dict(id="onemetre", s=25.0, e=32.0, bg="stadium", clock="REACTION · 10x", char="bat", pos=(540, 1130, 480),
         props=onemetre_props, look=(0, -0.4),
         narr="With 10x reflexes, you react when the ball has moved just 1 METRE.", n_at=25.2,
         say="Plenty of time. CHAI first?", say_at=27.6, pitch=440),
    dict(id="auto", s=32.0, e=TWIST, bg="gully", clock="60 KM/H", char="auto", pos=auto_pos,
         props=auto_props, look=(0.4, 0),
         narr="At 60 KM/H, an auto moves 4 METRES in 0.25 SEC. In 0.025: just 40 CM.", n_at=32.2,
         say="Brakes already ON, boss!", say_at=34.6, pitch=360),
    dict(id="twist", s=TWIST, e=46.0, bg="stadium", clock="100 M RACE", char="uncle", state="angry",
         pos=(700, 1000, 460), props=lanes_props, props_after=flag_after, twist=True, look=(-0.5, 0.1),
         narr="Plot twist: react in under 0.1 SEC in a sprint and it's a FALSE START.", n_at=39.2,
         say="Too FAST! DISQUALIFIED!", say_at=41.8, pitch=220),
    dict(id="outro", s=46.0, e=51.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.4)
        y = 1420 + 30 * math.sin(T * 5)
        r = 46 * p
        if r > 1: ball(d, 540 + 220 * math.sin((T - 1.9) * 2.4), y, r)

cfg = dict(
    total=51.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOUR REFLEXES", WHITE)], 120), 770, 0.75, "right"),
        (title([("WERE", WHITE)], 130), 905, 1.05, "left"),
        (title([("10x ", YEL), ("FASTER?", WHITE)], 140), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" want", WHITE)], 96), 470, 0.15),
                      (title([("10x reflexes?", YEL)], 110), 600, 0.45)],
               row=[("kid", 1), ("bat", 1), ("auto", 1), ("chai", 1), ("uncle", "angry")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=TWIST - 0.15, melody=True),
           dict(t0=46.0, t1=51.0, melody=True)],
    fx=[("crash", 4.0 + 3.6 + 0.4, 0.7), ("click", 12.1, 0.8), ("crowd", 18.2, 0.35, dict(dd=13.0)),
        ("screech", 33.0, 0.6), ("whistle", TWIST + 1.0, 0.8)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_your_reaction_time_was_10x_faster")
