#!/usr/bin/env python3
"""What if the Moon came twice as close? Facts: mean Earth-Moon distance ~384,400 km (NASA ~385,000 km); the
24 Nov 2026 Beaver supermoon is full at 14:53 UTC (20:23 IST) at ~360,768 km, ~6.5% larger and ~13.5% brighter
than at mean distance (Star Walk). Half the distance (~192,000 km) -> twice the apparent width, 4x the disc area,
~4x the light (inverse square). Tidal force scales with 1/d^3 -> 8x the lunar tidal pull (LibreTexts, tidal
force). Kepler's third law P ~ a^1.5: 27.3 d / 2.83 = ~9.7 d sidereal, ~9.9 d synodic -> ~36 full moons a year.
Moon would look ~2x wider than the Sun, so annular ('ring of fire') eclipses would no longer happen and total
eclipses would be longer. Twist: the Moon recedes ~3.8 cm/yr (NASA lunar laser ranging; 3.82 cm/yr, Meyers &
Malinverno 2018, PNAS); 1.4 billion years ago, when it was closer, a day lasted just over 18 hours (same study)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

TW = 56.0

_txt = {}
def label(txt, size=56, col=WHITE, stroke=8):
    k = (txt, size, col, stroke)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=stroke)
    return _txt[k]

def center_label(frame, txt, x, y, col=YEL, size=64, stroke=8):
    l = label(txt, size, col, stroke)
    comp(frame, l, x - l.width / 2, y - l.height / 2)

_gl = {}
def glow(frame, x, y, r, col=(255, 240, 200), s=0.6):
    k = (int(r), col, round(s, 2))
    if k not in _gl:
        R = max(2, int(r))
        yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
        q = np.clip(1 - np.sqrt(xx ** 2 + yy ** 2) / R, 0, 1) ** 2
        arr = np.zeros((2 * R + 1, 2 * R + 1, 4), np.uint8)
        arr[..., 0], arr[..., 1], arr[..., 2] = col
        arr[..., 3] = (q * 255 * s).astype(np.uint8)
        _gl[k] = Image.fromarray(arr, "RGBA")
    g = _gl[k]
    frame.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))

def moon_disc(d, x, y, r):
    d.ellipse([x - r, y - r, x + r, y + r], fill=(222, 222, 230), outline=OUTL, width=max(3, int(r / 25)))
    for fx, fy, fr in ((-0.4, -0.35, 0.2), (0.3, 0.3, 0.24), (0.35, -0.4, 0.12), (-0.35, 0.35, 0.13)):
        d.ellipse([x + fx * r - fr * r, y + fy * r - fr * r, x + fx * r + fr * r, y + fy * r + fr * r],
                  fill=(192, 192, 206))

# ---------------------------------------------------------------- scene props
def distance(frame, d, T, sc):
    lt = T - sc["s"]
    e = draw_char("earth", 260, T, 0, False, (0.3, 0), 0)
    paste_c(frame, e, 170, 1000, 1)
    half = ease_out(clamp((lt - 3.2) / 1.2))
    mx = 930 - 315 * half
    d.line([(300, 1180), (mx, 1180)], fill=YEL, width=8)
    for x in (300, mx): d.line([(x, 1155), (x, 1205)], fill=YEL, width=8)
    center_label(frame, "192,000 KM" if half > 0.5 else "384,400 KM", (300 + mx) / 2, 1250, WHITE, 52)

def supermoon(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_out(clamp((lt - 1.2) / 1.0))
    moon_disc(d, 300, 1030, 150)
    moon_disc(d, 780, 1030, 150 * (1 + 0.065 * p))
    center_label(frame, "AVERAGE", 300, 1240, WHITE, 44)
    center_label(frame, "24 NOV", 780, 1240, YEL, 50)

def grow(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_out(clamp((lt - 0.8) / 1.6))
    r = 110 * (1 + p)
    glow(frame, 540, 560, r * 2.0, (255, 250, 220), 0.35 + 0.3 * p)
    moon_disc(d, 540, 560, r)
    if p > 0.95: center_label(frame, "2x WIDE", 860, 880, YEL, 60)

def bright(frame, d, T, sc):
    lt = T - sc["s"]
    glow(frame, 820, 470, 340, (255, 250, 225), 0.55)
    moon_disc(d, 820, 470, 150)

def tide_pull(frame, d, T, sc):
    lt = T - sc["s"]
    moon_disc(d, 880, 620, 150)
    e = draw_char("earth", 300, T, 0, False, (0.4, 0), 0)
    # tidal bulge: an ocean ellipse stretched toward the Moon
    st = 1 + 0.25 * ease_out(clamp((lt - 1.8) / 1.0))
    d.ellipse([300 - 230 * st, 1040 - 190, 300 + 230 * st, 1040 + 190], fill=(60, 140, 230), outline=OUTL, width=5)
    paste_c(frame, e, 300, 1040, 1)
    if lt > 2.6:
        center_label(frame, "8x PULL", 800, 860, YEL, 72)

def beach(frame, d, T, sc):
    lt = T - sc["s"]
    # sand + a sea that climbs higher up the beach
    d.rectangle([0, 1240, 1080, 1920], fill=(244, 214, 150))
    rise = 140 * (0.5 - 0.5 * math.cos(lt * 1.3))
    y = 1330 - rise
    pts = [(0, y)] + [(x, y + 14 * math.sin(x / 70 + lt * 3)) for x in range(0, 1081, 30)] + [(1080, 1920), (0, 1920)]
    d.polygon(pts, fill=(60, 150, 220))
    d.line([(60, 1180), (60, 1330)], fill=OUTL, width=6)
    for k in range(5):
        yy = 1190 + k * 30
        d.line([(50, yy), (70, yy)], fill=OUTL, width=4)
    moon_disc(d, 860, 470, 130)

def orbit(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy = 540, 1000
    e = draw_char("earth", 200, T, 0, False, (0, 0), 0)
    d.ellipse([cx - 300, cy - 230, cx + 300, cy + 230], outline=(140, 150, 200), width=4)
    paste_c(frame, e, cx, cy, 1)
    a = lt * 2.2
    moon_disc(d, cx + 300 * math.cos(a), cy + 230 * math.sin(a), 46)
    n = min(36, int(lt * 6))
    center_label(frame, "FULL MOON #%d" % max(1, n), 540, 1290, YEL, 48)

def eclipse(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy = 540, 1020
    glow(frame, cx, cy, 380, (255, 220, 120), 0.9)
    d.ellipse([cx - 110, cy - 110, cx + 110, cy + 110], fill=(255, 210, 70), outline=OUTL, width=4)
    p = ease_out(clamp((lt - 0.6) / 2.2))
    mx = cx + 520 * (1 - p)
    d.ellipse([mx - 220, cy - 220, mx + 220, cy + 220], fill=(30, 30, 50), outline=OUTL, width=5)
    if p > 0.95:
        center_label(frame, "TOTAL!", 540, 700, YEL, 72)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    e = draw_char("earth", 220, T, 0, False, (0.3, 0), 0)
    paste_c(frame, e, 190, 960, 1)
    if lt > 3.8:
        center_label(frame, "1.4 BILLION YEARS AGO:", 540, 1170, WHITE, 46)
        center_label(frame, "18-HOUR DAYS", 540, 1240, YEL, 60)

def drift_pos(T):
    lt = T - TW
    return (560 + 240 * ease_out(clamp((lt - 0.5) / 4.0)), 1000, 280)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="now", s=4.0, e=10.5, bg="space", clock="384,400 KM", char="moon", pos=(930, 1000, 260),
         props=distance, look=(-0.4, 0),
         narr="The Moon is about 384,400 KM away. Now cut that in HALF.", n_at=4.2,
         say="Coming CLOSER!", say_at=7.6, pitch=420),
    dict(id="super", s=10.5, e=17.0, bg="night", clock="24 NOVEMBER", props=supermoon,
         narr="This 24 NOVEMBER's SUPERMOON comes only ~6% closer. It looks ~6.5% BIGGER.", n_at=10.7),
    dict(id="grow", s=17.0, e=23.5, bg="night", clock="192,000 KM", char="kid", pos=(540, 1120, 380),
         props=grow, look=(0, -0.6),
         narr="Twice as close: TWICE as wide, and 4x the AREA in the sky.", n_at=17.2),
    dict(id="bright", s=23.5, e=30.0, bg="night", clock="4x BRIGHTER", char="uncle", pos=(400, 1100, 380),
         props=bright, look=(0.5, -0.5),
         narr="Full moon nights about 4x BRIGHTER. Moonlight shadows everywhere!", n_at=23.7,
         say="Who turned the lights UP?", say_at=26.4, pitch=300),
    dict(id="tides", s=30.0, e=36.5, bg="space", clock="8x PULL", props=tide_pull,
         narr="Tidal pull grows with distance CUBED. Half the distance = 8x STRONGER!", n_at=30.2),
    dict(id="beach", s=36.5, e=43.0, bg="day", clock="HIGH TIDE", char="uncle", pos=(560, 1110, 320),
         props=beach, look=(0, 0.4), state="angry",
         narr="High tides would climb way higher up beaches like JUHU, twice a day.", n_at=36.7,
         say="My CHAPPALS!", say_at=39.6, pitch=300),
    dict(id="month", s=43.0, e=49.5, bg="space", clock="~10 DAYS", props=orbit,
         narr="Closer orbits are faster: one lap in about 10 DAYS. ~36 PURNIMAS a year!", n_at=43.2),
    dict(id="eclipse", s=49.5, e=TW, bg="space", clock="ECLIPSE", props=eclipse,
         narr="Looking 2x wider than the SUN: longer total eclipses, no 'RING OF FIRE'.", n_at=49.7),
    dict(id="twist", s=TW, e=64.0, bg="space", clock="WAIT...", char="moon", pos=drift_pos,
         twist=True, props=twist_props, look=(-0.4, 0),
         narr="Twist: the Moon WAS closer! It drifts ~3.8 CM away a YEAR.", n_at=56.9,
         say="I'm LEAVING slowly!", say_at=59.6, pitch=420),
    dict(id="outro", s=64.0, e=69.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.4)
        spr = draw_char("moon", 300, T, 0, False, (0, 0), 1)
        paste_c(frame, spr, 540, 1400, p)

cfg = dict(
    total=69.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("THE MOON CAME", WHITE)], 125), 770, 0.75, "right"),
        (title([("TWICE AS", WHITE)], 130), 910, 1.05, "left"),
        (title([("CLOSE?", YEL)], 130), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" want", WHITE)], 90), 450, 0.15),
                      (title([("a giant Moon?", WHITE)], 90), 570, 0.45)],
               row=[("moon", 1), ("earth", 0), ("uncle", 1), ("kid", 1), ("sun", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=TW - 0.15, melody=True),
           dict(t0=64.0, t1=69.0, melody=True)],
    fx=[("pop", 11.8, 0.3), ("whoosh", 18.0, 0.3), ("rumble", 31.5, 0.3, dict(dd=4.0)),
        ("waves", 36.6, 0.45, dict(dd=6.0)), ("ding", 54.0, 0.35)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_moon_closer")
