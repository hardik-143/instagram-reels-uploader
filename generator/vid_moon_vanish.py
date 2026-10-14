#!/usr/bin/env python3
"""What if the Moon disappeared for 5 seconds?"""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

GONE = 12.0      # Moon actually vanishes (seen from space)
SEEN = 19.0      # light delay: you see it vanish from Earth (scene times stretched for storytelling)
BACK = 46.0      # Moon returns (twist)

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def moon_at(frame, T, x, y, size, scale=1.0, look=(-0.4, 0.3)):
    if scale <= 0.02: return
    spr = draw_char("moon", size, T, 0, False, look, 1)
    paste_c(frame, spr, x, y, scale)

def glow(d, x, y, r):
    for k in range(4):
        rr = r + 10 * (4 - k)
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(40 + 10 * k, 40 + 10 * k, 70 + 12 * k))

def far_props(frame, d, T, sc):
    glow(d, 860, 470, 90)
    moon_at(frame, T, 860, 470, 180)
    l = label("LIGHT: 1.3 SEC", 56, YEL)
    comp(frame, l, 90, 360)

def vanish_props(frame, d, T, sc):
    # seen from space: Moon pops out of existence, its last light still travels to Earth
    s = 1.0 if T < GONE else 1.0 - ease_out(clamp((T - GONE) / 0.25))
    moon_at(frame, T, 840, 470, 240, s)
    if T >= GONE:
        q = clamp((T - GONE) / 1.6)
        for k in range(7):
            f = clamp(q - k * 0.06)
            if 0 < f < 1:
                x = 840 + (300 - 840) * f; y = 470 + (1150 - 470) * f
                d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=(255, 245, 190))

def dark_props(frame, d, T, sc):
    q = clamp((T - SEEN) / 0.25)
    if q < 1:
        glow(d, 860, 470, int(90 * (1 - q)))
    moon_at(frame, T, 860, 470, 180, 1.0 - ease_out(q))
    if T >= SEEN:
        # overall night gets darker
        pass

_shade = {}
def dark_bg(T):
    q = round(clamp((T - SEEN) / 0.6) * 12) / 12
    if q not in _shade:
        base = E.bg("night").convert("RGBA")
        _shade[q] = Image.blend(base, Image.new("RGBA", base.size, (0, 0, 8, 255)), 0.4 * q)
    return _shade[q]

def ripples(frame, d, T, sc):
    lt = T - sc["s"]
    for k in range(4):
        r = ((lt * 220) + k * 130) % 520
        a = clamp(1 - r / 520)
        c = (int(140 + 100 * a), int(160 + 80 * a), 255)
        d.ellipse([860 - r, 470 - r, 860 + r, 470 + r], outline=c, width=6)

def tide_props(frame, d, T, sc):
    lt = T - sc["s"]
    for k in range(6):
        x = (k * 210 + lt * 50) % 1300 - 110
        y = 1290 + 10 * math.sin(lt * 2 + k)
        d.arc([x, y - 30, x + 160, y + 30], 200, 340, fill=(255, 255, 255), width=6)
    l = label("NEEDS HOURS", 56, YEL)
    comp(frame, l, 640 - l.width / 2, 360)

def laser_props(frame, d, T, sc):
    lt = T - sc["s"]
    # beam from the uncle's lab up to where the Moon used to be
    x0, y0, x1, y1 = 330, 1000, 860, 430
    on = (lt % 1.6) < 1.1
    if on:
        d.line([(x0, y0), (x1, y1)], fill=(255, 60, 60), width=8)
        d.line([(x0, y0), (x1, y1)], fill=(255, 200, 200), width=3)
    q = label("NO ECHO", 60, YEL)
    comp(frame, q, x1 - q.width / 2, y1 - 40 + 6 * math.sin(T * 5))

def back_props(frame, d, T, sc):
    s = ease_back(clamp((T - BACK - 0.2) / 0.4))
    if s > 0: glow(d, 540, 960, int(180 * s))

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="far", s=4.0, e=11.0, bg="night", clock="384,400 KM AWAY", char="kid", pos=(420, 1080, 500),
         props=far_props, look=(0.5, -0.5),
         narr="The Moon is about 384,400 KM away. Its light takes 1.3 SECONDS to reach you.", n_at=4.2,
         say="So I see it... LATE?", say_at=7.4, pitch=600),
    dict(id="vanish", s=11.0, e=18.0, bg="space", clock="0 SEC · MOON GONE", char="earth", pos=(300, 1150, 380),
         props=vanish_props, look=(0.6, -0.6),
         narr="Poof. But its last light is still flying toward Earth for 1.3 SECONDS.", n_at=12.3,
         say="I can still SEE you!", say_at=14.6, pitch=200),
    dict(id="dark", s=18.0, e=25.0, bg_fn=dark_bg, clock="1.3 SEC", char="kid", pos=(420, 1080, 500),
         props=dark_props, look=(0.5, -0.5),
         narr="NOW you see it vanish. Moonlight is just SUNLIGHT bouncing off it.", n_at=18.2,
         say="Who switched off the NIGHT LIGHT?", say_at=20.6, pitch=620),
    dict(id="gravity", s=25.0, e=32.0, bg="space", clock="2 SEC", char="earth", pos=(420, 1120, 420),
         props=ripples, look=(0.6, -0.5),
         narr="Its PULL vanishes too, but even gravity travels at the speed of LIGHT.", n_at=25.2,
         say="Even the goodbye is LATE!", say_at=27.8, pitch=200),
    dict(id="tides", s=32.0, e=39.0, bg="ocean", clock="3 SEC", char="whale", pos=(540, 1080, 520),
         props=tide_props, look=(0, -0.3),
         narr="The Moon drives most of our TIDES. But oceans need HOURS to respond.", n_at=32.2,
         say="Five seconds? Didn't NOTICE.", say_at=34.8, pitch=160),
    dict(id="laser", s=39.0, e=BACK, bg="night", clock="4 SEC", char="uncle", pos=(300, 1080, 440),
         props=laser_props, look=(0.6, -0.6),
         narr="Scientists bounce LASERS off mirrors that Apollo astronauts left on the Moon.", n_at=39.2,
         say="Hello? Where's my ECHO?!", say_at=41.8, pitch=220),
    dict(id="twist", s=BACK, e=53.0, bg="night", clock="5 SEC · MOON BACK", char="moon", pos=(540, 1000, 440),
         props=back_props, twist=True, look=(0, 0.3),
         narr="It's back, 1.3 SECONDS late again. The oceans never even NOTICED.", n_at=46.3,
         say="Did anyone MISS me?", say_at=48.8, pitch=380),
    dict(id="outro", s=53.0, e=58.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.4)
        blink = 1.0 if (T % 0.8) < 0.55 else 0.0
        spr = draw_char("moon", 300, T, 0, False, (0, 0), 1)
        if blink: paste_c(frame, spr, 540, 1400, p)

cfg = dict(
    total=58.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("THE MOON", WHITE)], 150), 770, 0.75, "right"),
        (title([("DISAPPEARED", WHITE)], 130), 915, 1.05, "left"),
        (title([("...for ", WHITE), ("5 SECONDS?", YEL)], 96), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL)], 110), 470, 0.15),
                      (title([("have noticed?", YEL)], 110), 600, 0.45)],
               row=[("kid", 1), ("earth", 1), ("moon", 1), ("whale", 1), ("uncle", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=11.9, melody=True),
           dict(t0=12.2, t1=BACK - 0.15, minor=True, melody=True), dict(t0=53.0, t1=58.0, melody=True)],
    drones=[dict(t0=11.0, dur=7.0, g=0.06), dict(t0=25.0, dur=7.0, g=0.06)],
    fx=[("pop", GONE, 0.9), ("powerdown", GONE + 0.05, 0.5), ("pop", SEEN, 0.8), ("waves", 32.0, 0.5, dict(dd=7.0)),
        ("click", 39.3, 0.6), ("click", 40.9, 0.6), ("click", 42.5, 0.6), ("click", 44.1, 0.6),
        ("pop", BACK + 0.2, 1.0)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_the_moon_disappeared")
