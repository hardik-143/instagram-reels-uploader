#!/usr/bin/env python3
"""What if you could stop time? Thought experiment as physicists describe it (Discovery, citing Sean Carroll):
frozen light means no light reaches your eyes; sound is moving air, so silence; air molecules frozen in place make
a 'prison' you can't move through. ~2.5e25 molecules per cubic metre of air (Loschmidt). Twist: time really does
run at different speeds; GPS satellite clocks gain ~38 microseconds a day (+45 GR, -7 SR); uncorrected that is
~10 km of position error per day (techforspace / ESA Galileo)."""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

SNAP = 6.2

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=68):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

def ball(d, x, y, r):
    d.ellipse([x - r, y - r, x + r, y + r], fill=(200, 30, 40), outline=OUTL, width=max(2, int(r / 6)))
    d.arc([x - r * 0.9, y - r * 1.4, x + r * 0.9, y + r * 0.6], 20, 160, fill=WHITE, width=max(2, int(r / 8)))

def frozen_ball(d, T, sc):
    # the ball flies until the snap, then hangs in the air
    t = min(T, SNAP) - sc["s"] if sc["id"] == "snap" else SNAP - 4.0
    x = 900 - 120 * t; y = 900 - 40 * math.sin(t * 1.2)
    for k in range(3):
        d.line([(x + 50 + k * 30, y - 20 + k * 20), (x + 110 + k * 30, y - 20 + k * 20)], fill=WHITE, width=6)
    ball(d, x, y, 40)

# ---------------------------------------------------------------- props
def snap_props(frame, d, T, sc):
    frozen_ball(d, T, sc)
    if T > SNAP:
        top_label(frame, "TIME: STOPPED", 380, YEL, 76)

def snap_overlay(frame, T, sc):
    lt = T - SNAP
    if 0 <= lt < 0.35:
        return Image.blend(frame, Image.new("RGBA", (W, H), (200, 230, 255, 255)), 0.6 * (1 - lt / 0.35))
    if T > SNAP:   # slight blue "frozen" tint
        return Image.blend(frame, Image.new("RGBA", (W, H), (120, 170, 255, 255)), 0.12)
    return frame

def dark_props(frame, d, T, sc):
    # darken the world behind the kid and the bubble so the bubble stays readable
    frozen_ball(d, T, sc)
    lt = T - sc["s"]
    a = int(255 * (0.12 + 0.8 * clamp((lt - 1.2) / 1.8)))
    frame.alpha_composite(Image.new("RGBA", (W, H), (6, 8, 20, a)))

def speaker(d, x, y):
    d.rounded_rectangle([x - 70, y - 110, x + 70, y + 110], radius=18, fill=(60, 60, 76), outline=OUTL, width=6)
    d.ellipse([x - 45, y - 75, x + 45, y + 15], fill=(30, 30, 40), outline=OUTL, width=5)
    d.ellipse([x - 25, y + 35, x + 25, y + 85], fill=(30, 30, 40), outline=OUTL, width=5)

def silence_props(frame, d, T, sc):
    lt = T - sc["s"]
    speaker(d, 260, 1100)
    # sound waves stuck mid-air, never moving
    for k in range(3):
        r = 120 + k * 70
        d.arc([260 - r, 1070 - r, 260 + r, 1070 + r], -40, 40, fill=(140, 200, 255), width=10)
    if lt > 0.6:
        top_label(frame, "0 DECIBELS", 380, YEL, 76)

def air_props(frame, d, T, sc):
    lt = T - sc["s"]
    n = int(clamp(lt / 2.0) * 120)
    for k in range(n):
        x = 60 + (k * 97) % 960 + (k % 3) * 9
        y = 520 + ((k * 53) % 760)
        d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=(140, 200, 255), outline=OUTL, width=3)
    if lt > 0.6:
        top_label(frame, "IN 1 CUBIC METRE:", 350, WHITE, 56)
        top_label(frame, "25 TRILLION TRILLION", 425, YEL, 64)

def wall_props(frame, d, T, sc):
    for k in range(120):
        x = 60 + (k * 97) % 960 + (k % 3) * 9
        y = 520 + ((k * 53) % 760)
        d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=(140, 200, 255), outline=OUTL, width=3)

def satellite(d, x, y, s=1.0):
    c = lambda v: v * s
    d.rectangle([x - c(150), y - c(30), x - c(50), y + c(30)], fill=(60, 90, 200), outline=OUTL, width=5)
    d.rectangle([x + c(50), y - c(30), x + c(150), y + c(30)], fill=(60, 90, 200), outline=OUTL, width=5)
    for xx in (-120, -85, 85, 120):
        d.line([(x + c(xx), y - c(30)), (x + c(xx), y + c(30))], fill=(150, 180, 255), width=3)
    d.rounded_rectangle([x - c(50), y - c(50), x + c(50), y + c(50)], radius=10, fill=(230, 190, 80),
                        outline=OUTL, width=5)
    d.line([(x, y - c(50)), (x, y - c(90))], fill=OUTL, width=5)
    d.ellipse([x - c(12), y - c(102), x + c(12), y - c(78)], fill=WHITE, outline=OUTL, width=3)

def clock_face(d, x, y, r, T, speed):
    d.ellipse([x - r, y - r, x + r, y + r], fill=WHITE, outline=OUTL, width=6)
    a = T * speed
    d.line([(x, y), (x + r * 0.8 * math.sin(a), y - r * 0.8 * math.cos(a))], fill=(230, 40, 50), width=6)
    d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=OUTL)

def gps_props(frame, d, T, sc):
    lt = T - sc["s"]
    sx = 540 + 280 * math.cos(T * 0.6); sy = 640 + 60 * math.sin(T * 0.6)
    satellite(d, sx, sy, 1.0)
    clock_face(d, sx + 170, sy + 90, 50, T, 6.6)
    clock_face(d, 320, 1150, 50, T, 6.0)
    comp(frame, label("EARTH", 44, WHITE), 320 - label("EARTH", 44, WHITE).width / 2, 1210)
    if lt > 3.0:
        top_label(frame, "+38 MICROSECONDS / DAY", 380, YEL, 58)

def city(d):
    for k, (x, h) in enumerate(((60, 380), (200, 300), (330, 450), (760, 420), (900, 330), (1030, 400))):
        d.rectangle([x - 60, 1320 - h, x + 60, 1320], fill=(150, 160, 190) if k % 2 else (130, 140, 175),
                    outline=OUTL, width=4)
        for wy in range(1320 - h + 30, 1300, 60):
            d.rectangle([x - 30, wy, x - 10, wy + 25], fill=(255, 230, 140))
            d.rectangle([x + 10, wy, x + 30, wy + 25], fill=(255, 230, 140))

def map_props(frame, d, T, sc):
    lt = T - sc["s"]
    city(d)
    # phone with a map pin that keeps sliding away
    x, y = 270, 1000
    d.rounded_rectangle([x - 120, y - 210, x + 120, y + 210], radius=28, fill=(40, 40, 50), outline=OUTL, width=6)
    d.rounded_rectangle([x - 100, y - 180, x + 100, y + 180], radius=10, fill=(214, 236, 200))
    d.line([(x - 100, y - 40), (x + 100, y + 30)], fill=WHITE, width=14)
    d.line([(x - 20, y - 180), (x + 30, y + 180)], fill=WHITE, width=14)
    d.ellipse([x - 10, y - 15, x + 10, y + 5], fill=(60, 120, 240))
    drift = 90 * clamp((lt - 1.0) / 4.5)
    px, py = x + drift * 0.6, y - 10 - drift
    d.polygon([(px - 22, py - 30), (px + 22, py - 30), (px, py + 10)], fill=(230, 40, 50), outline=OUTL)
    d.ellipse([px - 26, py - 66, px + 26, py - 14], fill=(230, 40, 50), outline=OUTL, width=4)
    d.ellipse([px - 9, py - 49, px + 9, py - 31], fill=WHITE)
    if lt > 0.6:
        top_label(frame, "~10 KM OFF PER DAY", 380, YEL, 70)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="snap", s=4.0, e=11.0, bg="gully", clock="GULLY CRICKET", char="kid", pos=(330, 1110, 440),
         props=snap_props, overlay=snap_overlay, look=(0.6, -0.4),
         narr="You snap your fingers. The whole world FREEZES... except YOU.", n_at=4.2, narr_y=1500,
         say="Now I can't LOSE!", say_at=7.6, pitch=400),
    dict(id="dark", s=11.0, e=18.0, bg="gully", clock="PROBLEM 1", char="kid", pos=(330, 1110, 440),
         props=dark_props, look=(0, -0.3),
         narr="Physicists say light would freeze too. Nothing reaches your eyes. DARKNESS.", n_at=11.2,
         narr_y=1500, say="Who turned OFF the Sun?!", say_at=14.4, pitch=400),
    dict(id="silence", s=18.0, e=25.0, bg="living", clock="PROBLEM 2", char="uncle", pos=(760, 1100, 420),
         props=silence_props, look=(-0.5, 0),
         narr="Sound is just air moving. Frozen air means total SILENCE.", n_at=18.2, narr_y=1500,
         say="My bhajans... GONE?", say_at=21.4, pitch=150),
    dict(id="air", s=25.0, e=32.0, bg="day", clock="PROBLEM 3", props=air_props,
         narr="Every cubic metre of air holds about 25 TRILLION TRILLION molecules. All STUCK.", n_at=25.2,
         narr_y=1500),
    dict(id="wall", s=32.0, e=39.0, bg="day", clock="AIR = CONCRETE", char="kid", state="puff",
         pos=(540, 1080, 460), props=wall_props, rot=lambda T: 4 * math.sin(T * 9),
         narr="Stuck air acts like a WALL. You couldn't walk, or even BREATHE in.", n_at=32.2, narr_y=1500,
         say="I'm STUCK!", say_at=35.4, pitch=400),
    dict(id="twist", s=39.0, e=46.0, bg="space", clock="PLOT TWIST", props=gps_props, twist=True,
         char="earth", pos=(760, 1230, 280),
         narr="Twist: time REALLY ticks at different speeds. GPS satellite clocks run FAST.", n_at=39.2,
         narr_y=1500),
    dict(id="map", s=46.0, e=53.0, bg="day", clock="WITHOUT EINSTEIN", char="auto", pos=(760, 1180, 380),
         props=map_props, look=(-0.5, 0),
         narr="Without Einstein's fix, your phone's map would drift about 10 KM a DAY.", n_at=46.2,
         narr_y=1530, say="Bhaiya, WHICH way?!", say_at=49.4, pitch=260),
    dict(id="outro", s=53.0, e=58.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        clock_face(d, 540, 1420, 110, 0 if T > 2.6 else T, 8)

cfg = dict(
    total=58.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU COULD", WHITE)], 140), 770, 0.75, "right"),
        (title([("STOP TIME?", YEL)], 150), 920, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("What would ", WHITE), ("YOU", YEL)], 100), 470, 0.15),
                      (title([("do first?", YEL)], 116), 600, 0.45)],
               row=[("kid", 1), ("uncle", 1), ("auto", 1), ("earth", 1), ("kid", "puff")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=SNAP), dict(t0=11.0, t1=18.0, drums=False, minor=True),
           dict(t0=25.0, t1=38.85, drums=False, minor=True), dict(t0=46.0, t1=58.0, melody=True)],
    drones=[dict(t0=18.2, dur=6.6, g=0.3)],
    fx=[("crowd", 4.2, 0.3, dict(dd=2.0)), ("click", SNAP - 0.05, 0.9), ("powerdown", SNAP, 0.6),
        ("powerdown", 12.4, 0.5), ("heartbeat", 32.2, 0.4, dict(dd=6.5, bpm=80)), ("ding", 43.2, 0.25),
        ("ding", 43.6, 0.25), ("screech", 49.0, 0.4)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_could_stop_time")
