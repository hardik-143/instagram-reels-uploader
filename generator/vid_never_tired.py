#!/usr/bin/env python3
"""What if you never got tired? Facts: marathon runners 'hit the wall' around km 30 (mile 20) when muscle and liver
glycogen run low; a typical person stores ~380 g glycogen, ~1,500 kcal, up to ~3,600 kcal with carb loading
(Wikipedia: Hitting the wall). Jogging 10 km/h for 24 h = 240 km. Running costs ~1 kcal per kg per km (Margaria rule
of thumb, ale-santuz blog / scite); 60 kg x 240 km = 14,400 kcal ~ 55-60 samosas at ~250-262 kcal each (Bajaj Finserv
Markets 262 kcal; DocIndia 174 kcal for a small 40 g one) -> narration says 'about 60'. Humans have nearly 4 million
sweat glands and cool by sweating; persistence hunting: early humans trotted after animals for hours until they tired
(Particle / Scitech 'Particle 101: running'). Delhi-Mumbai by road ~1,400 km -> ~6 days at 240 km/day. Sleep is still
needed by the brain regardless of muscle fatigue (general physiology; no numbers claimed). Twist: Amur falcon
'Apapang', ~150 g, satellite-tagged in Manipur on 11 Nov 2025 (Wildlife Institute of India project), flew ~3,100 km
non-stop across central India, Gujarat and the Arabian Sea in ~76 hours, reaching Somalia (National Herald, OdishaTV,
Deccan Herald). A cricket ball weighs 155.9-163 g, so 150 g is lighter. Safety line: tiredness is a warning signal."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 53.0
SLATE = (96, 104, 122)
SLATE_D = (70, 76, 92)
ORANGE = (240, 128, 50)

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=68):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

def put(frame, txt, cx, y, size=52, col=WHITE):
    l = label(txt, size, col)
    comp(frame, l, cx - l.width / 2, y)

def mini(frame, kind, x, y, size, T, state=1, look=(0, 0.2), talk=0.0):
    size = max(2, int(size))
    spr = draw_char(kind, size, T, talk, False, look, state)
    comp(frame, spr, x - size / 2, y - size / 2)

def road(d, y=1240):
    d.rectangle([0, y, W, y + 150], fill=(90, 92, 104), outline=OUTL, width=6)
    return y

def dashes(d, T, y, speed=600):
    for k in range(9):
        x = (k * 160 - T * speed) % 1440 - 200
        d.rectangle([x, y - 6, x + 90, y + 6], fill=(250, 240, 200))

def streaks(d, T, n=14, speed=1400, seed=2, ymin=600, ymax=1200):
    rng = np.random.default_rng(seed)
    for k in range(n):
        y = rng.uniform(ymin, ymax)
        ln = rng.uniform(60, 200)
        x = (rng.uniform(0, 1500) - T * speed) % 1500 - 200
        d.line([(x, y), (x + ln, y)], fill=(255, 255, 255), width=4)

def falcon(d, x, y, s, T):
    """Flying Amur falcon facing right; (x, y) = body centre."""
    flap = math.sin(T * 9)
    lw = max(2, int(5 * s))
    # far wing
    d.polygon([(x - 10 * s, y - 10 * s), (x - 70 * s, y - 120 * s * flap - 20 * s), (x + 30 * s, y - 15 * s)],
              fill=SLATE_D, outline=OUTL)
    # tail
    d.polygon([(x - 80 * s, y - 5 * s), (x - 150 * s, y - 20 * s), (x - 150 * s, y + 20 * s), (x - 80 * s, y + 12 * s)],
              fill=SLATE_D, outline=OUTL)
    # body
    d.ellipse([x - 95 * s, y - 32 * s, x + 70 * s, y + 32 * s], fill=SLATE, outline=OUTL, width=lw)
    # orange thighs
    d.ellipse([x - 40 * s, y + 8 * s, x + 5 * s, y + 38 * s], fill=ORANGE, outline=OUTL, width=max(1, lw - 2))
    d.line([(x - 20 * s, y + 36 * s), (x - 40 * s, y + 52 * s)], fill=ORANGE, width=max(2, int(6 * s)))
    # head
    hx, hy = x + 80 * s, y - 18 * s
    d.ellipse([hx - 32 * s, hy - 30 * s, hx + 32 * s, hy + 30 * s], fill=SLATE_D, outline=OUTL, width=lw)
    d.polygon([(hx + 26 * s, hy - 8 * s), (hx + 52 * s, hy + 2 * s), (hx + 34 * s, hy + 16 * s)], fill=(250, 200, 80),
              outline=OUTL)
    d.ellipse([hx + 2 * s, hy - 14 * s, hx + 22 * s, hy + 6 * s], fill=ORANGE, outline=OUTL)
    d.ellipse([hx + 8 * s, hy - 8 * s, hx + 16 * s, hy], fill=OUTL)
    # near wing
    d.polygon([(x - 20 * s, y - 5 * s), (x - 40 * s, y - 150 * s * flap - 10 * s), (x + 50 * s, y - 10 * s)],
              fill=SLATE, outline=OUTL)

def antelope(d, x, y, s, T):
    """Simple running antelope; (x, y) = ground point under the body."""
    b = y - 120 * s
    lw = max(2, int(5 * s))
    ph = math.sin(T * 10)
    col = (200, 150, 90)
    for dx, sg in ((-50, 1), (-30, -1), (40, 1), (60, -1)):
        d.line([(x + dx * s, b + 20 * s), (x + dx * s + 25 * s * ph * sg, y)], fill=OUTL, width=max(3, int(9 * s)))
        d.line([(x + dx * s, b + 20 * s), (x + dx * s + 25 * s * ph * sg, y)], fill=col, width=max(2, int(5 * s)))
    d.ellipse([x - 80 * s, b - 30 * s, x + 80 * s, b + 35 * s], fill=col, outline=OUTL, width=lw)
    d.polygon([(x + 55 * s, b - 15 * s), (x + 95 * s, b - 80 * s), (x + 115 * s, b - 70 * s), (x + 75 * s, b + 5 * s)],
              fill=col, outline=OUTL)
    d.ellipse([x + 85 * s, b - 105 * s, x + 145 * s, b - 65 * s], fill=col, outline=OUTL, width=lw)
    d.line([(x + 100 * s, b - 100 * s), (x + 85 * s, b - 160 * s)], fill=OUTL, width=max(2, int(6 * s)))
    d.line([(x + 115 * s, b - 102 * s), (x + 110 * s, b - 165 * s)], fill=OUTL, width=max(2, int(6 * s)))
    d.ellipse([x + 118 * s, b - 95 * s, x + 128 * s, b - 85 * s], fill=OUTL)

# ---------------------------------------------------------------- props
def wall_props(frame, d, T, sc):
    lt = T - sc["s"]
    y = road(d, 1250)
    # brick wall on the right
    for r in range(8):
        for c in range(3):
            off = 40 if r % 2 else 0
            x0 = 800 + c * 90 - off
            y0 = 870 + r * 48
            d.rectangle([x0, y0, x0 + 86, y0 + 44], fill=(190, 80, 60), outline=OUTL, width=4)
    d.rectangle([700, 830, 1080, 870], fill=(150, 60, 45), outline=OUTL, width=4)
    put(frame, "KM 30", 920, 740, 60, YEL)
    if lt > 0.5: top_label(frame, "THE WALL", 380, YEL, 100)

def kid_pos_wall(T):
    return (380, 1080, 380)

def run_clock(T):
    h = int(clamp((T - 11.0) / 6.5) * 24)
    return f"HOUR {h}"

def run_props(frame, d, T, sc):
    lt = T - sc["s"]
    y = road(d, 1250)
    dashes(d, T, y + 75, 700)
    streaks(d, T)
    km = int(clamp(lt / 6.5) * 240)
    put(frame, f"{km} KM", 540, 600, 110, YEL)
    if lt > 0.5: top_label(frame, "10 KM/H, NO STOPS", 380, YEL, 80)

def fuel_props(frame, d, T, sc):
    lt = T - sc["s"]
    n = int(clamp((lt - 0.3) / 4.5) * 60)
    for i in range(n):
        row, col = divmod(i, 10)
        x = 135 + col * 90
        yy = 1290 - row * 58
        mini(frame, "samosa", x, yy, 92, T, look=(0, 0.2))
    put(frame, f"{n} SAMOSAS", 540, 820, 80, YEL)
    if lt > 0.5: top_label(frame, "14,400 CALORIES A DAY", 380, YEL, 72)

def sweat_props(frame, d, T, sc):
    lt = T - sc["s"]
    rng = np.random.default_rng(5)
    for k in range(10):
        ph = (lt * 0.9 + k * 0.1) % 1.0
        x = 540 + rng.uniform(-200, 200)
        yy = 860 + rng.uniform(0, 120) + 380 * ph
        d.polygon([(x, yy - 26), (x - 14, yy), (x + 14, yy)], fill=(120, 200, 255), outline=OUTL)
        d.ellipse([x - 14, yy - 12, x + 14, yy + 14], fill=(120, 200, 255), outline=OUTL, width=3)
    # water bottle
    bx, by = 880, 1080
    d.rounded_rectangle([bx - 50, by - 120, bx + 50, by + 140], radius=26, fill=(170, 220, 255), outline=OUTL, width=6)
    d.rectangle([bx - 26, by - 160, bx + 26, by - 120], fill=(60, 140, 230), outline=OUTL, width=5)
    put(frame, "2 L/HOUR", bx, by + 160, 52, YEL)
    if lt > 0.5: top_label(frame, "~4 MILLION SWEAT GLANDS", 380, YEL, 68)

def hunt_props(frame, d, T, sc):
    lt = T - sc["s"]
    d.rectangle([0, 1290, W, 1420], fill=(214, 170, 100), outline=OUTL, width=6)
    ax = 820 + 30 * math.sin(T * 0.8)
    antelope(d, ax, 1300, 1.0, T)
    if lt > 3.0:
        for k in range(3):
            d.ellipse([ax + 60 + k * 26, 1080 - k * 40, ax + 80 + k * 26, 1100 - k * 40], fill=(150, 200, 255),
                      outline=OUTL)
    if lt > 0.5: top_label(frame, "BUILT TO GO LONG", 380, YEL, 86)

def map_props(frame, d, T, sc):
    lt = T - sc["s"]
    p1, p2 = (300, 640), (330, 1260)
    for k in range(18):
        t = k / 17
        x = p1[0] + (p2[0] - p1[0]) * t + 140 * math.sin(t * math.pi)
        y = p1[1] + (p2[1] - p1[1]) * t
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=WHITE)
    for (x, y), name in ((p1, "DELHI"), (p2, "MUMBAI")):
        d.ellipse([x - 26, y - 26, x + 26, y + 26], fill=(230, 60, 60), outline=OUTL, width=6)
        put(frame, name, x + 200, y - 30, 60, WHITE)
    g = clamp((lt - 0.3) / 5.5)
    x = p1[0] + (p2[0] - p1[0]) * g + 140 * math.sin(g * math.pi)
    y = p1[1] + (p2[1] - p1[1]) * g
    mini(frame, "kid", x, y - 10, 150, T, look=(0, 0.6))
    day = 1 + int(g * 5.8)
    put(frame, f"DAY {min(day, 6)}", 780, 950, 80, YEL)
    if lt > 0.5: top_label(frame, "~1,400 KM", 380, YEL, 100)

def sleep_props(frame, d, T, sc):
    lt = T - sc["s"]
    for k in range(3):
        ph = (lt * 0.6 + k * 0.33) % 1.0
        put(frame, "Z", 700 + 60 * k + 40 * ph, 900 - 220 * ph, 60 + 20 * k, WHITE)
    if lt > 0.5: top_label(frame, "BRAIN NEEDS SLEEP", 380, YEL, 80)

def falcon_props(frame, d, T, sc):
    lt = T - sc["s"]
    d.rectangle([0, 1200, W, 1420], fill=(50, 120, 190), outline=OUTL, width=6)
    for k in range(7):
        x = (k * 170 - lt * 120) % 1200 - 60
        d.arc([x, 1230, x + 90, 1270], 200, 340, fill=WHITE, width=5)
    fx = 640 + 30 * math.sin(T * 1.2)
    fy = 1020 + 25 * math.sin(T * 2.0)
    falcon(d, fx, fy, 1.6, T)
    if lt > 0.5: top_label(frame, "3,100 KM IN 76 HOURS", 380, YEL, 76)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="wall", s=4.0, e=11.0, bg="speed", clock="NORMAL YOU", props=wall_props, char="kid",
         pos=kid_pos_wall, look=(0.6, 0.2),
         narr="Normally your muscles run low on fuel around 30 KM. Runners call it 'the WALL'.", n_at=4.2,
         narr_y=1580, say="My legs are JELLY!", say_at=7.6, pitch=440),
    dict(id="run", s=11.0, e=18.0, bg="speed", clock=run_clock, props=run_props, char="kid",
         pos=lambda T: (540, 1090 + 10 * abs(math.sin(T * 8)), 340), look=(0.6, 0),
         narr="No tiredness? Jog at 10 KM/H all day and night: 240 KM every 24 hours.", n_at=11.2,
         narr_y=1580),
    dict(id="fuel", s=18.0, e=25.0, bg="sweetshop", clock="FUEL CHECK", props=fuel_props, char="uncle",
         pos=(540, 640, 280), look=(0, 0.5), enter=18.15,
         narr="But fuel runs out! 240 KM burns about 14,400 calories: roughly 60 SAMOSAS.",
         n_at=18.2, narr_y=1580),
    dict(id="sweat", s=25.0, e=32.0, bg="hot", clock="COOLING", props=sweat_props, char="kid",
         pos=(470, 1060, 360), look=(0.3, 0),
         narr="You'd cool down with nearly 4 MILLION sweat glands, losing up to 2 LITRES an hour.",
         n_at=25.2, narr_y=1580, say="Pass the PAANI!", say_at=28.4, pitch=440),
    dict(id="hunt", s=32.0, e=39.0, bg="digsite", clock="2 MILLION YEARS AGO", props=hunt_props, char="kid",
         pos=(300, 1170, 300), look=(0.7, 0),
         narr="Humans ARE built for distance: early hunters jogged after animals for HOURS until THEY tired.",
         n_at=32.2, narr_y=1580),
    dict(id="map", s=39.0, e=46.0, bg="space", clock="ROAD TRIP", props=map_props,
         narr="So DELHI to MUMBAI, about 1,400 km on foot, would take about 6 DAYS, nonstop.",
         n_at=39.2, narr_y=1580),
    dict(id="sleep", s=46.0, e=TW, bg="bedroom", clock="BUT...", props=sleep_props, char="uncle",
         pos=(470, 1080, 380), look=(0.3, 0),
         narr="But your BRAIN still needs SLEEP. And real tiredness is a SAFETY alarm: don't ignore it.",
         n_at=46.2, narr_y=1580, say="Legs ready, BRAIN offline.", say_at=49.4, pitch=150),
    dict(id="twist", s=TW, e=60.0, bg="ocean", clock="PLOT TWIST", char="kid", pos=(220, 1300, 260),
         props=falcon_props, twist=True, look=(0.6, -0.4),
         narr="Twist: a 150 g AMUR FALCON tagged in India flew 3,100 KM nonstop over the sea in 76 HOURS.",
         n_at=TW + 0.2, narr_y=1600, say="Lighter than a CRICKET BALL!", say_at=TW + 3.4, pitch=440),
    dict(id="outro", s=60.0, e=65.0),
]

def intro_extra(frame, d, T):
    streaks(d, T, 12, 1600, 9, 1250, 1600)
    if T >= 1.9:
        p = min(ease_back((T - 1.9) / 0.4), 1.2)
        mini(frame, "kid", 540, 1400 + 14 * abs(math.sin(T * 8)), 300 * p, T, look=(0.6, 0))

cfg = dict(
    total=65.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU NEVER", WHITE)], 120), 770, 0.75, "right"),
        (title([("GOT TIRED?", YEL)], 160), 910, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("What would ", WHITE), ("YOU", YEL), (" do", WHITE)], 100), 470, 0.15),
                      (title([("with endless energy?", YEL)], 92), 600, 0.45)],
               row=[("kid", 1), ("samosa", 1), ("uncle", 1), ("chai", 1), ("sun", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0, melody=True),
           dict(t0=18.0, t1=32.0), dict(t0=32.0, t1=46.0, melody=True),
           dict(t0=46.0, t1=TW - 0.15, drums=False, minor=True), dict(t0=TW + 2.0, t1=65.0, melody=True)],
    drones=[dict(t0=46.0, dur=7.0, g=0.15)],
    fx=[("whoosh", 4.5, 0.3), ("crash", 6.0, 0.2), ("whoosh", 11.5, 0.3), ("pop", 19.0, 0.2), ("pop", 20.0, 0.2),
        ("pop", 21.0, 0.2), ("pop", 22.0, 0.2), ("heartbeat", 25.3, 0.25, dict(dd=6.0, bpm=110)),
        ("wind", 32.4, 0.2, dict(dd=6.0)), ("whoosh", 39.5, 0.3), ("waves", TW + 0.2, 0.25, dict(dd=6.5))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_never_got_tired")
