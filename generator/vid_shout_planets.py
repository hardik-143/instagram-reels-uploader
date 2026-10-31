#!/usr/bin/env python3
"""What if you shouted on other planets?
Facts: sound in Earth air ~343 m/s at 20 C (~1 km in 3 s). Moon: no air, no sound; astronauts used radio.
Mars (Perseverance microphones, Maurice et al., Nature 2022, CNRS release): surface pressure ~170x lower than Earth,
96% CO2; speed of sound ~240 m/s, ~250 m/s above 240 Hz, so high pitches arrive slightly earlier; high pitches fade
fast; two people ~5 m apart would struggle to hold a conversation.
Venus: surface pressure ~90x Earth, >470 C (NASA Venus lithograph); voice would sound deeper (Leighton, Univ. of
Southampton 2012). India's Venus Orbiter Mission approved Sept 2024, launch planned March 2028 (ISRO / Wikipedia).
Twist: Chandra X-ray Observatory (2003) found pressure (sound) waves in hot gas around the black hole in the Perseus
cluster, ~250 million light-years away: a B-flat ~57 octaves below middle C, the deepest note known."""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite
from vid_jump_worlds import wbg, GROUND

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=64):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

KID = 400
REST = GROUND - KID // 2 + 10

def rings(d, T, x0, y0, x1, speed, t0, col=(255, 255, 255), width=8, fade=None, period=0.35, spread=60):
    """Sound arcs travelling right from (x0, y0) toward x1. fade = distance (px) over which they vanish."""
    if T < t0: return
    for k in range(12):
        age = T - t0 - k * period
        if age < 0: continue
        x = x0 + speed * age
        if x > x1: continue
        dist = x - x0
        a = 1.0 if fade is None else max(0.0, 1 - dist / fade)
        if a <= 0.02: continue
        c = tuple(int(col[i] * a + 60 * (1 - a)) for i in range(3))
        r = spread + dist * 0.25
        d.arc([x - r, y0 - r, x + r, y0 + r], -40, 40, fill=c, width=max(2, int(width * (0.4 + 0.6 * a))))

# ---------------------------------------------------------------- scene props
def earth_props(frame, d, T, sc):
    lt = T - sc["s"]
    rings(d, T, 380, 1000, 760, 260, sc["s"] + 0.8)
    if lt > 1.0: top_label(frame, "343 M/S", 380, YEL, 80)

def friend(frame, T, x, y, size=300, look=(-0.6, 0), talk=0.0, kind="dog"):
    comp(frame, draw_char(kind, size, T, talk, E.blink_at(T, 0.9), look, 1), x - size / 2, y - size / 2)

def earth_after(frame, d, T, sc):
    friend(frame, T, 860, 1120, 300)

def moon_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 3.0:
        l = label("HELLO?", 64, (150, 150, 170)); comp(frame, l, 560, 900)
        d.line([(550, 900 + l.height / 2), (570 + l.width, 900 + l.height / 2)], fill=(230, 80, 80), width=8)
    if lt > 1.0: top_label(frame, "NO AIR = NO SOUND", 380, YEL, 66)

def mars_props(frame, d, T, sc):
    lt = T - sc["s"]
    rings(d, T, 380, 1050, 780, 220, sc["s"] + 3.0, fade=260)
    if lt > 1.0: top_label(frame, "5 METRES = TOO FAR", 380, YEL, 64)

def mars_after(frame, d, T, sc):
    friend(frame, T, 870, REST + 40, 280, look=(-0.6, 0))
    lt = T - sc["s"]
    if lt > 4.6:
        l = label("??", 70, WHITE); comp(frame, l, 870 - l.width / 2, REST - 230 - 6 * math.sin(T * 4))

def mars2_props(frame, d, T, sc):
    lt = T - sc["s"]
    # high notes (thin, yellow) run slightly ahead of low notes (thick, blue)
    rings(d, T, 300, 920, 980, 250, sc["s"] + 1.2, col=(255, 230, 90), width=6, period=0.6, spread=40)
    rings(d, T, 300, 1060, 980, 240, sc["s"] + 1.2, col=(120, 200, 255), width=12, period=0.6, spread=40)
    if lt > 1.0: top_label(frame, "HIGH 250 / LOW 240 M/S", 380, YEL, 58)

def venus_props(frame, d, T, sc):
    lt = T - sc["s"]
    rings(d, T, 640, 1000, 1000, 330, sc["s"] + 3.2, col=(150, 70, 30), width=14, period=0.5)
    if lt > 1.0: top_label(frame, "90x THICKER AIR", 380, YEL, 66)

def orbit_pos(T):
    lt = T - 39.0
    a = lt * 1.1
    return (540 + 330 * math.cos(a), 900 + 120 * math.sin(a), 260)

def venus2_props(frame, d, T, sc):
    lt = T - sc["s"]
    # Venus disc seen from orbit
    d.ellipse([290, 650, 790, 1150], fill=(236, 186, 110), outline=OUTL, width=8)
    for k in range(4):
        y = 740 + k * 100
        d.arc([300, y - 40, 780, y + 40], 10, 170, fill=(255, 216, 150), width=14)
    if lt > 1.0: top_label(frame, "SHUKRAYAAN: 2028", 380, YEL, 66)

def space_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 1.0: top_label(frame, "SPACE = SILENT?", 380, YEL, 70)
    if lt > 3.0:
        l = label("HELLO?", 64, (150, 150, 170)); comp(frame, l, 540 - l.width / 2, 650)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy = 540, 920
    for k in range(7):
        r = 120 + ((T * 70 + k * 70) % 490)
        a = max(0.0, 1 - (r - 120) / 490)
        c = (int(255 * a + 30 * (1 - a)), int(150 * a + 20 * (1 - a)), int(60 * a + 50 * (1 - a)))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c, width=10)
    d.ellipse([cx - 150, cy - 40, cx + 150, cy + 40], outline=(255, 190, 90), width=14)
    d.ellipse([cx - 90, cy - 90, cx + 90, cy + 90], fill=(0, 0, 0), outline=(255, 140, 60), width=6)
    if lt > 1.0: top_label(frame, "DEEPEST NOTE EVER FOUND", 380, YEL, 56)
    if lt > 4.2:
        l = label("B-FLAT", 80, WHITE); comp(frame, l, 540 - l.width / 2, 1110)

def float_pos(T):
    return (540, 1000 + 30 * math.sin(T * 1.4), 460)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="earth", s=4.0, e=11.0, bg="day", clock="EARTH", char="kid", pos=(260, 1060, 420),
         props=earth_props, props_after=earth_after, look=(0.6, 0),
         narr="On Earth, your shout flies at about 343 M/S. That's 1 KM in 3 SECONDS.", n_at=4.2,
         say="OYE, come HERE!", say_at=7.4, pitch=620, bubble_y=760),
    dict(id="moon", s=11.0, e=18.0, bg_fn=wbg("moon"), clock="MOON", char="kid", pos=(380, REST, KID),
         props=moon_props, look=(0.4, -0.2),
         narr="On the MOON there's no air, so NO sound at all. Astronauts talked by RADIO.", n_at=11.2,
         ),
    dict(id="mars", s=18.0, e=25.0, bg_fn=wbg("mars"), clock="MARS", char="kid", pos=(280, REST, 380),
         props=mars_props, props_after=mars_after, look=(0.6, 0),
         narr="MARS air is about 170x THINNER. A friend just 5 M away could barely hear you.", n_at=18.2,
         say="CHAI is READY!", say_at=20.6, pitch=640, bubble_y=700),
    dict(id="mars2", s=25.0, e=32.0, bg_fn=wbg("mars"), clock="MARS: 2 SPEEDS", char="kid", pos=(200, REST, 360),
         props=mars2_props, look=(0.6, 0),
         narr="Sound is slower there, about 240 M/S. And HIGH notes arrive a bit before LOW notes.", n_at=25.2),
    dict(id="venus", s=32.0, e=39.0, bg_fn=wbg("venus"), clock="VENUS", char="kid", pos=(460, REST, KID),
         props=venus_props, look=(0.5, 0),
         narr="VENUS air is about 90x THICKER. Your voice would sound DEEPER, like a tiny BASS singer.",
         n_at=32.2, say="Namaste... in BASS.", say_at=35.2, pitch=170, bubble_y=700),
    dict(id="venus2", s=39.0, e=46.0, bg="space", clock="VENUS ORBIT", char="rocket", pos=orbit_pos,
         rot=lambda T: -math.degrees((T - 39.0) * 1.1) - 90, props=venus2_props, look=(0, 0),
         narr="But it's also over 470°C down there. India's VENUS ORBITER is planned for 2028. It'll stay in ORBIT.",
         n_at=39.2),
    dict(id="space", s=46.0, e=53.0, bg="space", clock="DEEP SPACE", char="kid", pos=float_pos,
         rot=lambda T: 10 * math.sin(T * 0.9), props=space_props, look=(0, -0.3),
         narr="And out in SPACE? No air, so nothing carries your voice. Total SILENCE... right?", n_at=46.2,
         ),
    dict(id="twist", s=53.0, e=61.0, bg="twist", clock="PLOT TWIST", props=twist_props, twist=True,
         narr="Twist: a faraway BLACK HOLE hums real SOUND waves through hot gas. A B-flat 57 OCTAVES below middle C.",
         n_at=53.2),
    dict(id="outro", s=61.0, e=66.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back(clamp((T - 1.9) / 0.4))
        paste_c(frame, draw_char("kid", 260, T, clamp(0.5 + 0.6 * math.sin(T * 20)), False, (0, -0.3), 1), 540, 1440, p)

cfg = dict(
    total=66.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU SHOUTED", WHITE)], 130), 770, 0.75, "right"),
        (title([("ON OTHER", WHITE)], 140), 915, 1.05, "left"),
        (title([("PLANETS?", YEL)], 130), 1065, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Where would ", WHITE), ("YOU", YEL)], 96), 470, 0.15),
                      (title([("shout first?", YEL)], 116), 600, 0.45)],
               row=[("kid", 1), ("earth", 1), ("moon", 1), ("rocket", 1), ("dog", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=11.0, melody=True),
           dict(t0=18.0, t1=32.0, melody=True), dict(t0=32.0, t1=39.0, drums=False, minor=True),
           dict(t0=39.0, t1=46.0, melody=True), dict(t0=61.0, t1=66.0, melody=True)],
    drones=[dict(t0=11.2, dur=6.5, g=0.03), dict(t0=46.2, dur=6.5, g=0.03), dict(t0=53.2, dur=7.5, g=0.07)],
    fx=[("whoosh", 5.0, 0.4), ("pop", 7.0, 0.3), ("wind", 18.4, 0.15, dict(dd=6.0)), ("pop", 23.0, 0.4),
        ("ding", 27.0, 0.25), ("ding", 27.6, 0.18), ("rumble", 34.5, 0.3, dict(dd=3.0)), ("whoosh", 40.0, 0.4),
        ("whoosh", 43.0, 0.4), ("powerdown", 47.0, 0.25)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_shouted_on_other_planets")
