#!/usr/bin/env python3
"""What if lightning struck you?
Facts (checked 2026-11-11):
- ~44 (+-5) lightning flashes per second worldwide (NASA OTD, via Wikipedia 'Distribution of lightning').
- Average bolt ~300 million volts, ~30,000 amps (NOAA JetStream lightning FAQ).
- Ground current causes the most lightning deaths and injuries; direct strikes are less common (NWS 'How lightning strikes people').
- ~90% of people struck survive (NOAA 2013-2022 averages: 22 deaths / 220 struck); cardiac arrest is the immediate cause of
  death; victims carry no charge and are safe to touch, start CPR (NWS Dr Lightning victims guide).
- Lichtenberg figures: reddish fern-like marks, fade within hours to ~2 days (TORRO).
- India: 2,558 lightning deaths in 2023, 39.7% of deaths from natural forces (NCRB ADSI 2023 via Down To Earth).
- Damini app, IITM Pune (2020), alerts when lightning is within 20 and 40 km (ThePrint).
- Cars: metal body protects, tyres are a myth; soft-top / no metal roof gives little protection (NWS myths / ScienceNotes).
"""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

TW = 60.0   # twist start

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=360, col=YEL, size=60):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

_gl = {}
def glow(frame, x, y, r, col=(255, 240, 160), s=0.8):
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

def zigzag(x0, y0, x1, y1, seed, n=7, amp=40):
    rng = np.random.default_rng(seed)
    pts = [(x0, y0)]
    for i in range(1, n):
        f = i / n
        pts.append((x0 + (x1 - x0) * f + rng.uniform(-amp, amp), y0 + (y1 - y0) * f))
    pts.append((x1, y1))
    return pts

def bolt(d, pts, w=14):
    d.line(pts, fill=OUTL, width=w + 10, joint="curve")
    d.line(pts, fill=(255, 238, 110), width=w, joint="curve")
    d.line(pts, fill=(255, 255, 230), width=max(2, w // 3), joint="curve")

def flash(period=1.6, on=0.1, g=0.6, t0=0.3):
    def ov(frame, T, sc):
        lt = T - sc["s"] - t0
        if lt < 0: return frame
        ph = lt % period
        if ph < on:
            return Image.blend(frame, Image.new("RGBA", frame.size, (255, 255, 240, 255)), g * (1 - ph / on))
        return frame
    return ov

def is_on(T, sc, period=1.6, on=0.18, t0=0.3):
    lt = T - sc["s"] - t0
    return lt >= 0 and (lt % period) < on

# ---------------------------------------------------------------- props
def earth_props(frame, d, T, sc):
    top_label(frame, "~44 FLASHES EVERY SECOND")
    k = int(T * 8)
    for j in range(3):
        rng = np.random.default_rng(k * 3 + j)
        a = rng.uniform(0, 2 * math.pi); r0 = 175
        x0, y0 = 540 + (r0 + 70) * math.cos(a), 1060 + (r0 + 70) * math.sin(a)
        x1, y1 = 540 + (r0 - 10) * math.cos(a), 1060 + (r0 - 10) * math.sin(a)
        glow(frame, x1, y1, 60, (255, 250, 200), 0.8)
        bolt(d, zigzag(x0, y0, x1, y1, k * 7 + j, 3, 14), 6)

def bolt_props(frame, d, T, sc):
    top_label(frame, "300 MILLION VOLTS", 360, YEL)
    top_label(frame, "30,000 AMPS", 440, WHITE, 56)
    if is_on(T, sc):
        glow(frame, 540, 1310, 260, (255, 255, 220), 0.8)
        bolt(d, zigzag(560, 1080, 520, 1320, int(T / 1.6), 5, 50), 16)

def ground_props(frame, d, T, sc):
    # lone tree on the right gets hit, current spreads through the ground
    tx = 800
    d.rectangle([tx - 22, 1080, tx + 22, 1330], fill=(90, 62, 44), outline=OUTL, width=5)
    d.ellipse([tx - 150, 860, tx + 150, 1120], fill=(70, 130, 70), outline=OUTL, width=6)
    lt = T - sc["s"]
    if is_on(T, sc):
        glow(frame, tx, 900, 200, (255, 255, 220), 0.8)
        bolt(d, zigzag(tx + 30, 300, tx, 900, int(T / 1.6) + 5, 6, 50), 16)
    ph = ((lt - 0.3) % 1.6) / 1.6 if lt > 0.3 else -1
    if ph >= 0:
        for k in range(3):
            q = ph * 1.4 - k * 0.25
            if 0 < q < 1:
                rx = 60 + 700 * q
                d.ellipse([tx - rx, 1330 - rx * 0.09, tx + rx, 1330 + rx * 0.09],
                          outline=(255, 230, 90), width=max(2, int(8 * (1 - q))))
    top_label(frame, "GROUND CURRENT")

def survive_props(frame, d, T, sc):
    top_label(frame, "~9 IN 10 SURVIVE")
    # heartbeat line behind the heart
    y0 = 1060; pts = []
    for x in range(40, 1041, 10):
        ph = ((x - T * 400) % 340) / 340
        y = y0
        if 0.40 < ph < 0.45: y = y0 - 160 * math.sin((ph - 0.40) / 0.05 * math.pi)
        elif 0.45 < ph < 0.50: y = y0 + 80 * math.sin((ph - 0.45) / 0.05 * math.pi)
        pts.append((x, y))
    d.line(pts, fill=(80, 240, 120), width=8, joint="curve")

def fern(d, x, y, a, L, depth, w):
    if depth == 0 or L < 6: return
    x2, y2 = x + L * math.cos(a), y + L * math.sin(a)
    d.line([(x, y), (x2, y2)], fill=(206, 58, 64), width=max(2, w))
    fern(d, x2, y2, a - 0.45, L * 0.66, depth - 1, w - 2)
    fern(d, x2, y2, a + 0.45, L * 0.66, depth - 1, w - 2)
    fern(d, x2, y2, a + 0.05, L * 0.55, depth - 1, w - 2)

def fern_props(frame, d, T, sc):
    lt = T - sc["s"]
    # forearm panel on the right
    d.rounded_rectangle([560, 900, 1000, 1330], 70, fill=(236, 186, 146), outline=OUTL, width=6)
    fade = clamp((lt - 4.5) / 1.5)
    if fade < 1:
        layer = Image.new("RGBA", frame.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
        fern(ld, 780, 1310, -math.pi / 2, 150, 6, 14)
        a = layer.split()[3].point(lambda v: int(v * (1 - fade)))
        layer.putalpha(a)
        frame.alpha_composite(layer)
    top_label(frame, "LICHTENBERG FIGURE")

def india_props(frame, d, T, sc):
    top_label(frame, "~4 IN 10 DEATHS FROM NATURE")
    # paddy field rows
    for i in range(6):
        y = 1340 + i * 30
        for x in range(30 + (i % 2) * 40, W, 80):
            d.line([(x, y), (x - 10, y - 30)], fill=(90, 170, 80), width=6)
            d.line([(x, y), (x + 12, y - 28)], fill=(90, 170, 80), width=6)

def phone_props(frame, d, T, sc):
    lt = T - sc["s"]
    x0, y0 = 590, 900
    d.rounded_rectangle([x0, y0, x0 + 320, y0 + 470], 40, fill=(40, 40, 52), outline=OUTL, width=6)
    d.rounded_rectangle([x0 + 20, y0 + 40, x0 + 300, y0 + 430], 20, fill=(235, 240, 250))
    l = label("DAMINI", 50, (40, 90, 200)); comp(frame, l, x0 + 160 - l.width / 2, y0 + 60)
    if (lt % 1.0) < 0.6:
        d.rounded_rectangle([x0 + 40, y0 + 160, x0 + 280, y0 + 400], 20, fill=(255, 210, 60), outline=OUTL, width=4)
        bolt(d, [(x0 + 170, y0 + 180), (x0 + 140, y0 + 260), (x0 + 175, y0 + 260), (x0 + 145, y0 + 340)], 8)
        l2 = label("20 KM", 44, (200, 40, 40)); comp(frame, l2, x0 + 160 - l2.width / 2, y0 + 340)
    top_label(frame, "FREE APP BY IITM PUNE")

def rules_props(frame, d, T, sc):
    top_label(frame, "HEAR THUNDER? GO INDOORS")
    if is_on(T, sc, 2.0):
        glow(frame, 200, 1300, 200, (255, 255, 220), 0.7)
        bolt(d, zigzag(240, 480, 200, 1320, int(T / 2.0), 7, 50), 14)

def car(d, x, y, s=1.0):
    def P(px, py): return (x + px * s, y + py * s)
    d.polygon([P(-300, 60), P(-300, -20), P(-170, -40), P(-90, -140), P(110, -140), P(200, -40), P(300, -20),
               P(300, 60)], fill=(200, 60, 60), outline=OUTL, width=6)
    d.polygon([P(-70, -120), P(-140, -40), P(-10, -40), P(-10, -120)], fill=(190, 225, 245), outline=OUTL, width=4)
    d.polygon([P(10, -120), P(10, -40), P(170, -40), P(100, -120)], fill=(190, 225, 245), outline=OUTL, width=4)
    for wx in (-180, 180):
        d.ellipse([*P(wx - 60, 0), *P(wx + 60, 120)], fill=(34, 34, 38), outline=OUTL, width=5)
        d.ellipse([*P(wx - 24, 36), *P(wx + 24, 84)], fill=(160, 160, 170))

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy = 600, 1150
    car(d, cx, cy, 1.0)
    if lt > 0.8:
        # current racing over the metal shell, then down to the ground, never through the cabin
        path = [(cx - 300, cy + 60), (cx - 300, cy - 20), (cx - 170, cy - 40), (cx - 90, cy - 140), (cx + 110, cy - 140),
                (cx + 200, cy - 40), (cx + 300, cy - 20), (cx + 300, cy + 60)]
        q = ((lt - 0.8) * 0.9) % 1.0
        n = len(path) - 1
        for k in range(5):
            f = (q + k * 0.2) % 1.0
            i = int(f * n); u = f * n - i
            px = path[i][0] + (path[i + 1][0] - path[i][0]) * u
            py = path[i][1] + (path[i + 1][1] - path[i][1]) * u
            glow(frame, px, py, 50, (255, 250, 170), 0.9)
        if (lt % 1.8) < 0.2:
            bolt(d, zigzag(cx - 20, 300, cx - 10, cy - 140, int(T / 1.8), 6, 40), 14)
    if lt > 3.0:
        l = label("METAL SHELL, NOT TYRES", 54, YEL); comp(frame, l, 540 - l.width / 2, 360)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="earth", s=4.0, e=11.0, bg="space", clock="RIGHT NOW", char="earth", pos=(540, 1060, 520),
         state=0, props=earth_props,
         narr="Lightning hits somewhere on Earth about 44 TIMES every second.", n_at=4.2,
         say="Ouch! Ouch! OUCH!", say_at=6.6, pitch=360),
    dict(id="bolt", s=11.0, e=18.0, bg="storm", clock="1 BOLT", char="cloud", pos=(540, 940, 360),
         props=bolt_props, overlay=flash(), look=(0, 0.4),
         narr="One average bolt carries about 300 MILLION volts, in a blink.", n_at=11.2,
         say="Sorry, couldn't HOLD it in!", say_at=13.6, pitch=480),
    dict(id="ground", s=18.0, e=25.0, bg="storm", clock="HOW IT HITS", char="uncle", state="angry",
         pos=(320, 1090, 420), props=ground_props, overlay=flash(), look=(0.4, 0.2),
         narr="Direct hits are RARE. Most people are hurt by current through the GROUND.", n_at=18.2,
         say="The GROUND bit me?!", say_at=20.8, pitch=220),
    dict(id="survive", s=25.0, e=32.0, bg="night", clock="AFTER A STRIKE", char="heart", pos=(540, 1060, 440),
         props=survive_props,
         narr="About 9 IN 10 people struck SURVIVE. The danger: the heart can STOP.", n_at=25.2,
         say="Victims are SAFE to touch. Start CPR!", say_at=27.8, pitch=520),
    dict(id="fern", s=32.0, e=39.0, bg="living", clock="SKIN MARKS", char="kid", pos=(290, 1110, 380),
         props=fern_props, look=(0.5, 0.3),
         narr="Some survivors get red, fern-shaped marks that fade within a day or TWO.", n_at=32.2,
         say="It's not a TATTOO!", say_at=34.6, pitch=620),
    dict(id="india", s=39.0, e=46.0, bg="storm", clock="INDIA", char="uncle", state="hat", pos=(540, 1080, 460),
         props=india_props, overlay=flash(2.2), look=(0, -0.3),
         narr="In 2023, lightning killed 2,558 people in INDIA.", n_at=39.2,
         say="Not safe in the open FIELD!", say_at=41.8, pitch=220),
    dict(id="damini", s=46.0, e=53.0, bg="living", clock="BE WARNED", char="kid", pos=(300, 1100, 400),
         props=phone_props, look=(0.5, 0.2),
         narr="The DAMINI app alerts you when lightning is within 20 to 40 KM.", n_at=46.2,
         say="Lightning nearby? I'm STAYING in!", say_at=48.6, pitch=620),
    dict(id="rules", s=53.0, e=TW, bg="storm", clock="STAY SAFE", char="cloud", pos=(640, 960, 340),
         props=rules_props, overlay=flash(2.0, 0.1, 0.5), look=(-0.3, 0.3),
         narr="Avoid open fields, lone TREES and water. Nowhere outside is SAFE.", n_at=53.2,
         say="When thunder roars, go INDOORS!", say_at=55.6, pitch=480),
    dict(id="twist", s=TW, e=68.0, bg="storm", clock="PLOT TWIST", char="auto", pos=(150, 1200, 220),
         props=twist_props, twist=True, look=(0.5, 0.3),
         narr="Cars are safe, but NOT because of TYRES. The METAL shell carries the current.",
         n_at=TW + 0.4, narr_y=1500,
         say="My canvas roof won't SAVE me?!", say_at=TW + 3.2, pitch=420),
    dict(id="outro", s=68.0, e=73.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        if (T - 1.9) % 1.2 < 0.15:
            glow(frame, 540, 1450, 260, (255, 255, 220), 0.8)
        p = ease_back((T - 1.9) / 0.4)
        spr = draw_char("cloud", 300, T, 0, False, (0, 0.3), 1)
        paste_c(frame, spr, 540, 1380, p)

cfg = dict(
    total=73.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("LIGHTNING", WHITE)], 150), 780, 0.75, "right"),
        (title([("STRUCK ", WHITE), ("YOU?", YEL)], 140), 940, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Did ", WHITE), ("YOU", YEL), (" know", WHITE)], 96), 470, 0.15),
                      (title([("the car fact?", YEL)], 110), 600, 0.45)],
               row=[("cloud", 1), ("earth", 0), ("heart", 1), ("uncle", "hat"), ("auto", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=TW - 0.15, minor=True),
           dict(t0=68.0, t1=73.0, melody=True)],
    fx=[("boom", 2.0, 0.6), ("rumble", 11.3, 0.5, dict(dd=5.0)), ("boom", 18.35, 0.5), ("rumble", 39.4, 0.4, dict(dd=5.0)),
        ("heartbeat", 25.2, 0.5, dict(dd=6.0, bpm=70)), ("rumble", 53.4, 0.5, dict(dd=5.0)), ("boom", TW + 0.9, 0.6)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_lightning_struck_you")
