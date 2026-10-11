#!/usr/bin/env python3
"""What if Earth stopped spinning for one second?"""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp

STOP = 5.0

def intro_extra(frame, d, T):
    if T < 1.9: return
    s = ease_back((T - 1.9) / 0.4)
    off = min(T, 3.2) * 70
    jx = 10 * math.sin(T * 90) * max(0, 1 - (T - 3.2) / 0.4) if T >= 3.2 else 0
    paste_c(frame, draw_char("earth", 380, T, 0, False, (0, 0), off), 540 + jx, 1390, s)
    if T < 3.2:
        for i in range(3):
            a = T * 4 + i * 2.1
            d.arc([540 - 230, 1390 - 230, 540 + 230, 1390 + 230], math.degrees(a), math.degrees(a) + 40,
                  fill=(255, 230, 120), width=8)

def earth_state(T):
    return min(T, STOP) * 70

def earth_pos(T):
    j = 14 * math.sin(T * 80) * max(0, 1 - (T - STOP) / 0.5) if T >= STOP else 0
    return (540 + j, 1080, 600)

def spin_rings(frame, d, T, sc):
    if T < STOP:
        for i in range(3):
            a = T * 4 + i * 2.1
            d.arc([540 - 360, 1080 - 360, 540 + 360, 1080 + 360], math.degrees(a), math.degrees(a) + 40,
                  fill=(255, 230, 120), width=10)
    elif T < STOP + 0.6:
        p = (T - STOP) / 0.6
        for i in range(8):
            a = i * math.pi / 4; r1 = 330 + 40 * p; r2 = r1 + 80 * (1 - p)
            d.line([(540 + r1 * math.cos(a), 1080 + r1 * math.sin(a)), (540 + r2 * math.cos(a), 1080 + r2 * math.sin(a))],
                   fill=(255, 230, 120), width=10)

def streaks(frame, d, T, sc, col=(255, 255, 255), speed=2400, n=22, slope=0.0):
    for i in range(n):
        y = 380 + (i * 97) % 1300
        x = ((i * 271) - T * speed) % 1500 - 200
        L = 160 + (i % 4) * 60
        d.line([(x, y), (x + L, y + L * slope)], fill=col, width=5 + (i % 3) * 2)

def fly_props(frame, d, T, sc):
    streaks(frame, d, T, sc)

def fly_pos(T):
    return (540 + 30 * math.sin(T * 2.4), 1060 + 20 * math.sin(T * 3.1), 560)

def storm_props(frame, d, T, sc):
    streaks(frame, d, T, sc, col=(200, 206, 216), speed=3000, n=30, slope=0.12)

def cloud_pos(T):
    return (540 + 18 * math.sin(T * 13), 1060 + 10 * math.sin(T * 9), 560)

def wave_props(frame, d, T, sc):
    lt = T - sc["s"]
    rise = ease_out(lt / 1.2)
    base = 1250
    pts = [(0, H)]
    for x in range(0, W + 1, 30):
        crest = 520 * rise * math.exp(-((x - 640 - 40 * math.sin(T)) / 380) ** 2)
        y = base - crest + 18 * math.sin(x / 70 + T * 4)
        pts.append((x, y))
    pts.append((W, H))
    d.polygon(pts, fill=(36, 112, 186))
    d.line(pts[1:-1], fill=(230, 246, 255), width=14, joint="curve")
    for i, (x, y) in enumerate(pts[1:-1]):
        if i % 2 == 0:
            d.ellipse([x - 12, y - 18, x + 12, y + 6], fill=(240, 250, 255))

def fish_pos(T):
    return (520 + 30 * math.sin(T * 1.8), 1000 + 30 * math.sin(T * 2.6), 520)

def fish_rot(T):
    return 8 * math.sin(T * 2.6)

def bonus_state(T):
    return (T - 39.0) * 70

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="stop", s=4.0, e=11.0, bg="space", clock="0.0 SEC", char="earth", state=earth_state, pos=earth_pos,
         props=spin_rings, say="Hold on. Quick BREAK.", say_at=5.6, pitch=260,
         narr="Earth stops spinning. But YOU don't.", n_at=7.0),
    dict(id="fly", s=11.0, e=18.0, bg="speed", clock="0.1 SEC", char="uncle", pos=fly_pos, rot=-12,
         props=fly_props, look=(-0.6, -0.3),
         narr="In India, you'd keep flying east at about 1,500 km/h.", n_at=11.2,
         say="WHY am I FLYING?!", say_at=12.9, pitch=230),
    dict(id="storm", s=18.0, e=25.0, bg="storm", clock="0.5 SEC", char="cloud", pos=cloud_pos,
         props=storm_props, narr="Winds faster than SOUND rip across the planet.", n_at=18.2,
         say="I'm going SUPERSONIC!", say_at=19.8, pitch=520),
    dict(id="ocean", s=25.0, e=32.0, bg="ocean", clock="1.0 SEC", char="fish", pos=fish_pos, rot=fish_rot,
         props=wave_props, look=(0, -0.3),
         narr="Oceans keep sloshing east. Giant tsunamis hit the coasts.", n_at=25.2,
         say="Surf's UP. Way, WAY up.", say_at=26.9, pitch=480),
    dict(id="pole", s=32.0, e=39.0, bg="pole", clock="SOUTH POLE", char="penguin", twist=True,
         narr="But right at the South Pole? You'd barely MOVE.", n_at=32.2,
         say="Wait... did something happen?", say_at=34.2, pitch=560),
    dict(id="bonus", s=39.0, e=45.0, bg="space", clock="+1 SECOND", char="earth", state=bonus_state,
         narr="Bonus: your day just got 1 second LONGER.", n_at=39.2,
         say="You're welcome.", say_at=41.2, pitch=260),
    dict(id="outro", s=45.0, e=50.0),
]

cfg = dict(
    total=50.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("EARTH STOPPED", WHITE)], 112), 770, 0.75, "right"),
        (title([("SPINNING", WHITE)], 140), 905, 1.05, "left"),
        (title([("...for ", WHITE), ("ONE", YEL), (" second?", WHITE)], 90), 1050, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Where would ", WHITE), ("YOU", YEL)], 96), 470, 0.15),
                      (title([("want to be?", YEL)], 116), 600, 0.45)],
               row=[("earth", 0), ("uncle", 1), ("cloud", 1), ("fish", 1), ("penguin", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=31.85, minor=True),
           dict(t0=39.0, t1=45.0, drums=False, g=0.8), dict(t0=45.0, t1=50.0, melody=True)],
    fx=[("screech", 2.7, 0.9, dict(dd=0.5)), ("click", 3.2, 1.0),
        ("screech", STOP - 0.55, 1.0, dict(dd=0.6)), ("boom", STOP, 1.0), ("rumble", STOP, 0.8, dict(dd=2.0)),
        ("gale", 11.0, 0.7, dict(dd=7.0)), ("whoosh", 11.6, 0.8), ("whoosh", 14.5, 0.8),
        ("boom", 18.5, 0.9), ("gale", 18.0, 0.9, dict(dd=7.0)),
        ("waves", 25.0, 1.0, dict(dd=7.0)), ("splash", 25.6, 0.9), ("splash", 28.5, 0.6),
        ("wind", 32.0, 0.5, dict(dd=7.0)), ("kwak", 32.6, 1.0)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_earth_stopped_spinning")
