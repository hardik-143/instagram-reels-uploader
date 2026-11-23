#!/usr/bin/env python3
"""What if Earth had no tilt? Earth's axis is tilted 23.4 deg (US Naval Observatory; ~23.5 deg per The Conversation);
"if the Earth's axis were perpendicular to its orbital plane, there would be no seasons at all" (USNO). With no tilt the
day/night line always runs through both poles, so every place gets ~12 h of day and ~12 h of night all year, and the
Sun sits on the horizon at the poles (geometry). India's summer monsoon is driven by seasonal land heating, so it is
framed as "could vanish as we know it" (hypothetical).
Twist: perihelion is 3 Jan 2027, 147,104,598 km from the Sun, in India's winter (EarthSky); distance is only ~3% less
than at aphelion, too weak to cause seasons (USNO / EarthSky)."""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

TW = 46.0   # twist starts

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=64):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

def axis(d, cx, cy, ang_deg, L=330):
    a = math.radians(ang_deg)
    dx, dy = L * math.sin(a), -L * math.cos(a)
    d.line([(cx - dx, cy - dy), (cx + dx, cy + dy)], fill=OUTL, width=16)
    d.line([(cx - dx, cy - dy), (cx + dx, cy + dy)], fill=(255, 230, 120), width=8)

# ---------------------------------------------------------------- scene 1: tilted Earth
def p_tilt(frame, d, T, sc):
    axis(d, 540, 1080, 23.4)
    lt = T - sc["s"]
    if lt > 1.5:
        top_label(frame, "TILT: 23.4°", 380, YEL, 70)

# ---------------------------------------------------------------- scene 2: straighten up
def straight_ang(T):
    lt = T - 11.0
    return 23.4 * (1 - ease_out(clamp((lt - 0.8) / 1.6)))

def p_straight(frame, d, T, sc):
    axis(d, 540, 1080, straight_ang(T))
    if T - sc["s"] > 2.6:
        top_label(frame, "TILT: 0°", 380, YEL, 70)

# ---------------------------------------------------------------- scene 3: 12 + 12 hours
def p_daynight(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy, r = 540, 520, 150
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 90, 270, fill=(255, 210, 60), outline=OUTL, width=6)
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 270, 90, fill=(40, 50, 110), outline=OUTL, width=6)
    for k in range(3):
        sx, sy = cx + 50 + k * 30, cy - 60 + k * 50
        d.ellipse([sx - 8, sy - 8, sx + 8, sy + 8], fill=WHITE)
    l1, l2 = label("12 h", 56, WHITE), label("12 h", 56, YEL)
    comp(frame, l1, cx - r - l1.width - 20, cy - l1.height / 2); comp(frame, l2, cx + r + 20, cy - l2.height / 2)

# ---------------------------------------------------------------- scene 4: one season forever
def p_delhi(frame, d, T, sc):
    lt = T - sc["s"]
    for i, (txt, col) in enumerate((("WINTER", (150, 210, 255)), ("SUMMER", (255, 140, 80)))):
        x = 270 + i * 540
        l = label(txt, 52, col)
        comp(frame, l, x - l.width / 2, 420)
        if lt > 1.2 + i * 0.4:
            q = ease_back(clamp((lt - 1.2 - i * 0.4) / 0.4))
            d.line([(x - 120 * q, 400), (x + 120 * q, 500)], fill=(230, 40, 40), width=14)
            d.line([(x - 120 * q, 500), (x + 120 * q, 400)], fill=(230, 40, 40), width=14)

# ---------------------------------------------------------------- scene 5: endless sunrise at the pole
def p_pole(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy, r = 680, 1300, 120
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=(255, 170, 60), outline=OUTL, width=6)
    for k in range(7):
        a = math.radians(190 + k * 26)
        rr = r + 30 + 10 * math.sin(lt * 4 + k)
        d.line([(cx + (r + 10) * math.cos(a), cy + (r + 10) * math.sin(a)),
                (cx + rr * math.cos(a), cy + rr * math.sin(a))], fill=(255, 200, 80), width=10)

def pole_overlay(frame, T, sc):
    o = Image.new("RGBA", frame.size, (255, 140, 60, 50))
    frame.alpha_composite(o)
    return frame

# ---------------------------------------------------------------- scene 6: monsoon
def p_monsoon(frame, d, T, sc):
    lt = T - sc["s"]
    fade = 1 - ease_out(clamp((lt - 3.0) / 1.5))
    if fade > 0.02:
        for k in range(18):
            ph = (lt * 1.6 + k / 18) % 1.0
            x = 230 + (k * 97) % 640; y = 1000 + ph * 300
            d.line([(x, y), (x - 12, y + 40 * fade)], fill=(140, 190, 255), width=6)
    if lt > 3.4:
        top_label(frame, "NO SUMMER = NO MONSOON?", 380, YEL, 58)

# ---------------------------------------------------------------- twist: closest in January
def p_twist(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy = 540, 1080
    d.ellipse([cx - 400, cy - 200, cx + 400, cy + 200], outline=(200, 200, 255), width=5)
    a = lt * 0.5 + 3.3
    ex, ey = cx + 400 * math.cos(a), cy + 200 * math.sin(a)
    spr = draw_char("earth", 150, T, 0, False, (0, 0), lt * 20)
    comp(frame, spr, ex - 75, ey - 75)
    if lt > 2.6:
        top_label(frame, "3 JAN 2027: CLOSEST TO THE SUN", 380, YEL, 54)
        top_label(frame, "147.1 MILLION km", 460, WHITE, 60)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="tilt", s=4.0, e=11.0, bg="space", clock="TODAY", char="earth", pos=(540, 1080, 460), rot=-23.4,
         props=p_tilt, look=(0, 0),
         narr="Earth spins TILTED, by about 23.4°. That tilt is why we get SEASONS.", n_at=4.2,
         say="I'm LEANING, not falling!", say_at=8.0, pitch=420),
    dict(id="straight", s=11.0, e=18.0, bg="space", clock="TILT = 0", char="earth", pos=(540, 1080, 460),
         rot=lambda T: -straight_ang(T), state=lambda T: (T - 11) * 15, props=p_straight, look=(0, 0),
         narr="Now stand it perfectly STRAIGHT. Result? NO SEASONS at all.", n_at=11.2,
         say="Ahh, good posture!", say_at=14.6, pitch=420),
    dict(id="daynight", s=18.0, e=25.0, bg="night", clock="EVERY DAY", char="kid", pos=(540, 1100, 420),
         props=p_daynight, look=(0, -0.4),
         narr="Day and night would be about 12 HOURS each, everywhere, every day of the year.", n_at=18.2),
    dict(id="delhi", s=25.0, e=32.0, bg="day", clock="DELHI", char="uncle", pos=(540, 1080, 440),
         props=p_delhi, look=(0, 0),
         narr="Delhi: no foggy December, no scorching May. ONE in-between season, FOREVER.", n_at=25.2,
         say="Where do I keep my RAZAI?", say_at=28.6, pitch=300),
    dict(id="pole", s=32.0, e=39.0, bg="pole", clock="NORTH POLE", char="penguin", pos=(330, 1080, 380),
         props=p_pole, overlay=pole_overlay, look=(0.5, 0.2),
         narr="At the POLES, the Sun would sit on the horizon forever. An endless SUNRISE.", n_at=32.2,
         say="Golden hour, ALL day!", say_at=35.6, pitch=560),
    dict(id="monsoon", s=39.0, e=TW, bg="storm", clock="MONSOON", char="cloud", pos=(540, 920, 380),
         props=p_monsoon, look=(0, 0.4),
         narr="India's MONSOON runs on summer heat. With no summer, it could vanish as we know it.", n_at=39.2),
    dict(id="twist", s=TW, e=54.0, bg="space", clock="WAIT...", char="sun", pos=(540, 1080, 300),
         props=p_twist, twist=True, look=(0, 0),
         narr="Twist: Earth is CLOSEST to the Sun in early JANUARY, India's winter. DISTANCE isn't the reason!",
         n_at=46.4, say="It was the TILT all along!", say_at=50.0, pitch=300),
    dict(id="outro", s=54.0, e=59.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.4)
        spr = draw_char("earth", 300, T, 0, False, (0, 0), T * 20)
        spr = spr.rotate(-23.4, resample=Image.BICUBIC)
        paste_c(frame, spr, 540, 1400, p)

cfg = dict(
    total=59.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("EARTH HAD", WHITE)], 140), 770, 0.75, "right"),
        (title([("NO TILT?", YEL)], 150), 930, 1.1, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" pick", WHITE)], 96), 470, 0.15),
                      (title([("one season?", YEL)], 110), 600, 0.45)],
               row=[("earth", 1), ("kid", 1), ("uncle", 1), ("penguin", 1), ("cloud", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=TW - 0.15, melody=True),
           dict(t0=54.0, t1=59.0, melody=True)],
    fx=[("whoosh", 11.9, 0.5), ("wind", 32.1, 0.4, dict(dd=5.0)), ("gale", 39.1, 0.4, dict(dd=4.0)),
        ("powerdown", 42.4, 0.4)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_no_tilt")
