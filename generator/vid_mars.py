#!/usr/bin/env python3
"""What if you lived on Mars? Facts (NASA JPL 'Mars at a glance', InSight press kit): air is 95.3% carbon dioxide and
surface pressure is less than 1/100th of Earth's; average surface temperature about -53 to -63 C (JPL / NASA Science),
polar night down to -128 C; gravity 38% of Earth's; a solar day is 24 h 39 min 35 s; a year is 687 Earth days;
Olympus Mons is about 22-26 km high (over 2.5x Everest's 8,849 m). India's Mars Orbiter Mission (Mangalyaan) entered
Mars orbit on 24 Sep 2014 on the first attempt, first Asian nation, cost about Rs 450 crore / ~$74M (Al Jazeera,
23 Sep 2014). Twist: Mars sunsets look blue because fine dust lets blue light through more efficiently; NASA's
Curiosity rover filmed one on 15 Apr 2015 (NASA SVS 11875)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 53.0
RUST = (200, 90, 50)
DUST = (232, 170, 120)
GROUND = 1330

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=68):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

def at_label(frame, txt, x, y, col=WHITE, size=56):
    l = label(txt, size, col)
    comp(frame, l, x - l.width / 2, y - l.height / 2)

def mars(frame, cx, cy, r, T, face=True):
    S = int(r * 2.4)
    L = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    c = S / 2
    d.ellipse([c - r - 6, c - r - 6, c + r + 6, c + r + 6], fill=OUTL)
    d.ellipse([c - r, c - r, c + r, c + r], fill=RUST)
    for dx, dy, rr in ((-0.4, 0.35, 0.22), (0.45, -0.1, 0.15), (0.1, 0.55, 0.12), (-0.2, -0.5, 0.1)):
        d.ellipse([c + dx * r - rr * r, c + dy * r - rr * r * 0.7, c + dx * r + rr * r, c + dy * r + rr * r * 0.7],
                  fill=(160, 66, 38))
    d.chord([c - r * 0.5, c - r * 1.02, c + r * 0.5, c - r * 0.7], 0, 180, fill=(250, 245, 240))
    if face:
        ex = r * 0.32; ey = c - r * 0.05; er = r * 0.13
        for sx in (-1, 1):
            d.ellipse([c + sx * ex - er, ey - er * 1.1, c + sx * ex + er, ey + er * 1.1], fill=WHITE, outline=OUTL,
                      width=max(2, int(r * 0.03)))
            d.ellipse([c + sx * ex - er * 0.5, ey - er * 0.4, c + sx * ex + er * 0.3, ey + er * 0.6], fill=(25, 20, 30))
        d.arc([c - r * 0.25, c + r * 0.15, c + r * 0.25, c + r * 0.45], 20, 160, fill=OUTL, width=max(2, int(r * 0.05)))
    comp(frame, L, cx - S / 2, cy - S / 2)

# ---------------------------------------------------------------- backgrounds
_cache = {}
def surface_bg(T):
    if "surf" not in _cache:
        img = E.grad([(0, (214, 150, 104)), (1, (244, 200, 150))], W, H).convert("RGBA")
        d = ImageDraw.Draw(img)
        d.ellipse([820, 470, 866, 516], fill=(255, 250, 220))
        d.ellipse([-200, GROUND - 160, 520, GROUND + 160], fill=(176, 80, 46))
        d.ellipse([600, GROUND - 110, 1300, GROUND + 140], fill=(186, 86, 50))
        d.rectangle([0, GROUND, W, H], fill=(196, 92, 52))
        d.line([(0, GROUND), (W, GROUND)], fill=(150, 66, 40), width=6)
        rng = np.random.default_rng(11)
        for k in range(22):
            x = rng.uniform(0, W); y = rng.uniform(GROUND + 40, H - 40); r = rng.uniform(12, 40)
            d.ellipse([x - r, y - r * 0.55, x + r, y + r * 0.55], fill=(150, 66, 40))
        _cache["surf"] = img
    img = _cache["surf"].copy(); d = ImageDraw.Draw(img)
    for k in range(10):  # blowing dust
        x = (k * 173 + T * 160) % (W + 200) - 100
        y = 1180 + (k * 57) % 140
        d.ellipse([x - 30, y - 6, x + 30, y + 6], fill=(236, 186, 140))
    return img

def sunset_bg(T):
    if "sunset" not in _cache:
        img = E.grad([(0, (60, 50, 70)), (0.5, (150, 120, 110)), (1, (190, 150, 120))], W, H).convert("RGBA")
        _cache["sunset"] = img
    img = _cache["sunset"].copy()
    lt = T - TW
    g = ease_out(clamp((lt - 0.4) / 2.5))
    # blue glow around a small setting Sun
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    sx, sy = 540, 1040 + 60 * clamp(lt / 7.0)
    for k in range(10, 0, -1):
        r = 40 + k * 38
        a = int(85 * g)
        gd.ellipse([sx - r, sy - r * 0.8, sx + r, sy + r * 0.8], fill=(60, 140, 255, a))
    img.alpha_composite(glow)
    d = ImageDraw.Draw(img)
    d.ellipse([sx - 40, sy - 40, sx + 40, sy + 40], fill=(240, 250, 255), outline=(150, 200, 255), width=6)
    d.polygon([(0, 1150), (260, 1080), (520, 1140), (800, 1070), (1080, 1130), (1080, H), (0, H)], fill=(70, 40, 34))
    d.rectangle([0, GROUND, W, H], fill=(84, 46, 36))
    return img

# ---------------------------------------------------------------- props
def helmet(frame, d, T, sc):
    """Glass bubble helmet over the kid's head."""
    p = sc["pos"](T) if callable(sc["pos"]) else sc["pos"]
    cx, cy, s = p
    hx, hy, r = cx, cy - s * 0.17, s * 0.36
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
    ld.ellipse([hx - r, hy - r, hx + r, hy + r], fill=(200, 230, 255, 50), outline=(255, 255, 255, 230), width=8)
    ld.ellipse([hx - r * 0.65, hy - r * 0.75, hx - r * 0.35, hy - r * 0.45], fill=(255, 255, 255, 170))
    frame.alpha_composite(L)

def trip_props(frame, d, T, sc):
    lt = T - sc["s"]
    mars(frame, 830, 820, 140, T, face=True)
    if lt > 0.5:
        top_label(frame, "MANGALYAAN, 2014", 380, YEL, 86)
    if lt > 2.2:
        at_label(frame, "FIRST TRY!", 830, 1020, WHITE, 60)

def rocket_pos(T):
    lt = T - 4.0
    g = ease_out(clamp((lt - 0.3) / 4.5))
    return (200 + 240 * g, 1250 - 150 * g, 300)

def air_props(frame, d, T, sc):
    lt = T - sc["s"]
    # CO2 bubbles drifting
    for k in range(9):
        x = 700 + (k % 3) * 120 + 15 * math.sin(T * 2 + k)
        y = 1200 - ((lt * 70 + k * 90) % 520)
        d.ellipse([x - 44, y - 44, x + 44, y + 44], fill=(255, 235, 215), outline=OUTL, width=4)
        if y < 1150:
            at_label(frame, "CO2", x, y, (200, 80, 50), 30)
    if lt > 0.5:
        top_label(frame, "95% CARBON DIOXIDE", 380, YEL, 76)

def therm(d, x, frac, col=(120, 190, 255), top=820):
    d.rounded_rectangle([x - 36, top, x + 36, 1220], radius=36, fill=WHITE, outline=OUTL, width=8)
    d.ellipse([x - 66, 1180, x + 66, 1310], fill=col, outline=OUTL, width=8)
    lvl = 1210 - (1210 - top - 30) * frac
    d.rectangle([x - 18, lvl, x + 18, 1210], fill=col)

def cold_props(frame, d, T, sc):
    lt = T - sc["s"]
    g = ease_out(clamp((lt - 0.6) / 2.4))
    therm(d, 850, 0.85 * (1 - g) + 0.05)
    if lt > 0.5:
        top_label(frame, f"{-int(60 * g)} °C", 380, YEL, 110)
    if lt > 3.5:
        at_label(frame, "POLES: -128 °C", 430, 860, (150, 210, 255), 52)

def scale_props(frame, d, T, sc):
    lt = T - sc["s"]
    # bathroom scale under the kid
    d.rounded_rectangle([340, 1290, 740, 1370], radius=20, fill=WHITE, outline=OUTL, width=7)
    d.rounded_rectangle([470, 1300, 610, 1350], radius=8, fill=(40, 50, 70))
    g = ease_out(clamp((lt - 0.8) / 2.0))
    kg = int(round(60 - 37 * g))
    at_label(frame, f"{kg} KG", 540, 1325, (120, 255, 160), 38)
    if lt > 0.5:
        top_label(frame, "38% GRAVITY", 380, YEL, 96)

def kid_scale_pos(T):
    return (540, 1130, 360)

def day_props(frame, d, T, sc):
    lt = T - sc["s"]
    # clock face
    cx, cy, r = 800, 980, 170
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE, outline=OUTL, width=10)
    for k in range(12):
        a = math.radians(90 - k * 30)
        d.line([(cx + math.cos(a) * r * 0.78, cy - math.sin(a) * r * 0.78),
                (cx + math.cos(a) * r * 0.9, cy - math.sin(a) * r * 0.9)], fill=OUTL, width=6)
    g = ease_out(clamp((lt - 0.8) / 3.0))
    ang = math.radians(90 - 240 * g)
    d.line([(cx, cy), (cx + math.cos(ang) * r * 0.75, cy - math.sin(ang) * r * 0.75)], fill=(220, 60, 50), width=10)
    d.line([(cx, cy), (cx, cy - r * 0.5)], fill=OUTL, width=12)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=OUTL)
    if lt > 1.0:
        at_label(frame, f"+{int(40 * g)} MIN", cx, cy + r + 60, YEL, 66)
    if lt > 0.5:
        top_label(frame, "1 DAY = 24 H 40 MIN", 380, YEL, 80)

def year_props(frame, d, T, sc):
    lt = T - sc["s"]
    # Sun with two orbits
    cx, cy = 540, 960
    d.ellipse([cx - 70, cy - 70, cx + 70, cy + 70], fill=(255, 220, 90), outline=OUTL, width=6)
    for rr, col in ((190, (120, 180, 255)), (330, (230, 120, 80))):
        d.ellipse([cx - rr, cy - rr * 0.45, cx + rr, cy + rr * 0.45], outline=col, width=5)
    ae = T * 2.2; am = T * 2.2 * 365.25 / 687
    ex, ey = cx + 190 * math.cos(ae), cy + 190 * 0.45 * math.sin(ae)
    mx, my = cx + 330 * math.cos(am), cy + 330 * 0.45 * math.sin(am)
    d.ellipse([ex - 26, ey - 26, ex + 26, ey + 26], fill=(70, 140, 230), outline=OUTL, width=4)
    d.ellipse([mx - 30, my - 30, mx + 30, my + 30], fill=RUST, outline=OUTL, width=4)
    if lt > 0.5:
        top_label(frame, "1 YEAR = 687 DAYS", 380, YEL, 84)

def mountain_props(frame, d, T, sc):
    lt = T - sc["s"]
    g1 = ease_out(clamp((lt - 0.4) / 1.2))
    g2 = ease_out(clamp((lt - 1.6) / 2.2))
    base = 1330
    eh = 230 * g1; oh = 600 * g2
    d.polygon([(230, base), (350, base - eh), (470, base)], fill=(200, 210, 225), outline=OUTL)
    d.polygon([(315, base - eh * 0.75), (350, base - eh), (385, base - eh * 0.75)], fill=WHITE)
    d.polygon([(500, base), (640, base - oh), (820, base - oh), (1070, base)], fill=(176, 80, 46), outline=OUTL)
    d.ellipse([660, base - oh - 14, 800, base - oh + 18], fill=(130, 56, 34))
    if lt > 1.0: at_label(frame, "EVEREST", 350, base + 50, WHITE, 46)
    if lt > 2.0: at_label(frame, "OLYMPUS MONS", 790, base + 50, YEL, 46)
    if lt > 0.5:
        top_label(frame, "OVER 2.5x EVEREST", 380, YEL, 84)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 0.5:
        top_label(frame, "RED PLANET, BLUE SUNSET", 380, YEL, 70)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="trip", s=4.0, e=11.0, bg="space", clock="GETTING THERE", char="rocket", pos=rocket_pos,
         props=trip_props, look=(0.6, -0.4),
         narr="In 2014, India's MANGALYAAN reached Mars on its FIRST try.", n_at=4.2, narr_y=1560,
         say="Mars, here I COME!", say_at=7.4, pitch=300),
    dict(id="air", s=11.0, e=18.0, bg_fn=surface_bg, clock="STEP OUTSIDE", char="kid", pos=(380, 1130, 380),
         props=air_props, props_after=helmet, look=(0.6, -0.2),
         narr="The air is 95% CARBON DIOXIDE and over 100x THINNER. Helmet ON.", n_at=11.2, narr_y=1560,
         say="No OXYGEN on the menu!", say_at=14.4, pitch=440),
    dict(id="cold", s=18.0, e=25.0, bg_fn=surface_bg, clock="WEATHER CHECK", char="kid", state="puff",
         pos=(400, 1130, 380), props=cold_props, props_after=helmet, look=(0.6, -0.3),
         narr="Average: about -60 °C. Polar nights: -128 °C.", n_at=18.2, narr_y=1560,
         say="My CHAI is an ice cube!", say_at=21.4, pitch=440),
    dict(id="weight", s=25.0, e=32.0, bg_fn=surface_bg, clock="WEIGH-IN", char="kid", pos=kid_scale_pos,
         props=scale_props, props_after=helmet, look=(0, 0.4),
         narr="Gravity is just 38%. A 60 KG person reads about 23 KG on a scale.", n_at=25.2, narr_y=1560,
         say="Best DIET ever!", say_at=28.6, pitch=440),
    dict(id="day", s=32.0, e=39.0, bg_fn=surface_bg, clock="ALARM CLOCK", char="kid", pos=(300, 1130, 360),
         props=day_props, props_after=helmet, look=(0.6, -0.2),
         narr="A Mars day lasts about 24 HOURS 40 MIN. Bonus SLEEP, every day.", n_at=32.2, narr_y=1560,
         say="Five more MINUTES... x8!", say_at=35.4, pitch=440),
    dict(id="year", s=39.0, e=46.0, bg="space", clock="BIRTHDAYS", char="kid", pos=(880, 1340, 220),
         props=year_props, look=(-0.4, -0.5),
         narr="A Mars year is 687 DAYS. If you're 20 on Earth, you're about 10 on Mars.",
         n_at=39.2, narr_y=1560, say="Cake every 2 YEARS?!", say_at=42.4, pitch=440),
    dict(id="mount", s=46.0, e=TW, bg_fn=surface_bg, clock="WEEKEND TREK", char="uncle", state="hat",
         pos=(140, 1180, 200), props=mountain_props, look=(0.6, -0.4),
         narr="OLYMPUS MONS, a giant volcano, stands over 2.5 TIMES as tall as Everest.", n_at=46.2,
         narr_y=1560, say="Trek CANCELLED!", say_at=49.6, pitch=150),
    dict(id="twist", s=TW, e=61.0, bg_fn=sunset_bg, clock="PLOT TWIST", char="kid", pos=(300, 1250, 260),
         props=twist_props, twist=True, look=(0.6, -0.3),
         narr="Twist: the RED planet has BLUE sunsets. Its dust lets blue light through.",
         n_at=TW + 0.2, narr_y=1560, say="Who painted it BLUE?!", say_at=TW + 3.6, pitch=440),
    dict(id="outro", s=61.0, e=66.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = min(ease_back((T - 1.9) / 0.4), 1.2)
        mars(frame, 540, 1390 + 12 * math.sin(T * 2), 170 * p, T, face=True)

cfg = dict(
    total=66.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU LIVED ON", WHITE)], 120), 770, 0.75, "right"),
        (title([("MARS?", YEL)], 150), 915, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" move", WHITE)], 100), 470, 0.15),
                      (title([("to Mars?", YEL)], 96), 600, 0.45)],
               row=[("rocket", 1), ("earth", 1), ("kid", 1), ("sun", 1), ("uncle", "hat")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=11.0, melody=True),
           dict(t0=11.0, t1=25.0, drums=False, minor=True), dict(t0=25.0, t1=46.0, melody=True),
           dict(t0=46.0, t1=TW - 0.15, melody=True), dict(t0=TW + 2.0, t1=66.0, melody=True)],
    drones=[dict(t0=11.0, dur=14.0, g=0.2)],
    fx=[("rumble", 4.4, 0.3, dict(dd=3.0)), ("whoosh", 6.0, 0.3), ("wind", 11.4, 0.3, dict(dd=6.0)),
        ("wind", 18.4, 0.3, dict(dd=6.0)), ("tick", 26.0, 0.3), ("ding", 27.6, 0.25), ("tick", 33.0, 0.3),
        ("tick", 34.0, 0.3), ("tick", 35.0, 0.3), ("pop", 40.0, 0.25), ("rumble", 47.8, 0.3, dict(dd=3.0)),
        ("wind", TW + 0.5, 0.2, dict(dd=7.0))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_lived_on_mars")
