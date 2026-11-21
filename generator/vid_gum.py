#!/usr/bin/env python3
"""What if you swallowed chewing gum? Facts: the '7 years in your stomach' idea is a myth (Scientific American,
pediatric gastroenterologist David Milov: endoscopy shows no such thing, swallowed gum seen is usually no more than a
week old; Duke Health, gastroenterologist Nancy McGreal: has yet to see a wad of gum sitting in the stomach in upper
endoscopies; KidsHealth 2026: 'isn't true'). Gum base per the FDA definition: elastomers, softeners, resins,
antioxidants; permitted elastomers include natural chicle and butyl rubber, also used in inner tubes (Scientific
American). Sweeteners are absorbed; the body has no digestive enzymes to break down gum base (Duke Health, Live
Science, KidsHealth). It passes in about 40 hours like food (Cleveland Clinic, Live Science quoting Julia Zumpano RD).
Rare blockages: 1998 Pediatrics report of three children who swallowed gum regularly (Scientific American, Live
Science); swallowing a lot, often, can cause an intestinal blockage (Cleveland Clinic); an occasional piece is harmless
(KidsHealth). Twist: a 5,700-year-old chewed lump of birch pitch from Syltholm, Denmark gave a complete ancient human
genome (Jensen et al. 2019, Nature Communications; University of Copenhagen press release 17 Dec 2019)."""
import math
from PIL import Image
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 46.0
GUM, GUM_D = (255, 140, 190), (220, 90, 150)
PINK, PINK_D = (240, 170, 175), (200, 110, 120)
TAR = (90, 60, 40)

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def lab_at(frame, txt, x, y, col=WHITE, size=52):
    l = label(txt, size, col); comp(frame, l, x - l.width / 2, y - l.height / 2)

def mini(frame, kind, x, y, size, T, state=1, look=(0, 0.2), talk=0.0):
    size = max(2, int(size))
    spr = draw_char(kind, size, T, talk, False, look, state)
    comp(frame, spr, x - size / 2, y - size / 2)

def wad(d, x, y, r, col=GUM, dark=GUM_D):
    d.ellipse([x - r, y - 0.75 * r, x + r, y + 0.75 * r], fill=col, outline=OUTL, width=6)
    d.arc([x - 0.6 * r, y - 0.4 * r, x + 0.2 * r, y + 0.3 * r], 200, 320, fill=dark, width=6)
    d.arc([x - 0.1 * r, y - 0.1 * r, x + 0.7 * r, y + 0.5 * r], 200, 320, fill=dark, width=6)

def stomach(d, cx, cy, s=1.0):
    # J-shaped stomach: big round body + tube in and out
    d.rounded_rectangle([cx - 210 * s, cy - 380 * s, cx - 130 * s, cy - 120 * s], radius=int(40 * s),
                        fill=PINK, outline=OUTL, width=7)
    d.ellipse([cx - 280 * s, cy - 200 * s, cx + 240 * s, cy + 230 * s], fill=PINK, outline=OUTL, width=8)
    d.rounded_rectangle([cx + 140 * s, cy + 80 * s, cx + 330 * s, cy + 160 * s], radius=int(40 * s),
                        fill=PINK, outline=OUTL, width=7)
    d.ellipse([cx - 268 * s, cy - 188 * s, cx + 228 * s, cy + 218 * s], fill=PINK)
    d.rectangle([cx - 198 * s, cy - 230 * s, cx - 142 * s, cy - 150 * s], fill=PINK)
    for k in range(3):
        d.arc([cx - 200 * s + k * 120 * s, cy - 60 * s, cx - 60 * s + k * 120 * s, cy + 120 * s], 20, 160,
              fill=PINK_D, width=6)

# ---------------------------------------------------------------- props
def myth_after(frame, d, T, sc):
    lt = T - sc["s"]
    # bubble grows from the kid's mouth, then pops
    if 0.4 < lt < 3.0:
        r = 15 + 75 * ease_out(clamp((lt - 0.4) / 2.4))
        d.ellipse([540 - r, 1205 - r, 540 + r, 1205 + r], fill=GUM, outline=OUTL, width=7)
        d.ellipse([540 - 0.5 * r, 1205 - 0.6 * r, 540 - 0.2 * r, 1205 - 0.3 * r], fill=(255, 210, 230))
    if lt > 3.0:
        lab_at(frame, "GULP!", 540, 860, (255, 120, 80), 90)
    if lt > 3.6:
        lab_at(frame, "7 YEARS?", 540, 560, YEL, 120)

def scope_props(frame, d, T, sc):
    lt = T - sc["s"]
    stomach(d, 540, 960)
    # camera cable from the top
    p = ease_out(clamp((lt - 0.4) / 1.6))
    ty = 560 + 360 * p
    d.line([(370, 420), (370, 580), (400, ty)], fill=(60, 60, 70), width=12)
    d.ellipse([400 - 26, ty - 26, 400 + 26, ty + 26], fill=(60, 60, 70), outline=OUTL, width=5)
    if lt > 1.8:
        d.polygon([(400, ty), (300 + 60 * math.sin(T * 2), ty + 260), (560 + 60 * math.sin(T * 2), ty + 260)],
                  fill=(255, 250, 200))
        d.ellipse([388, ty - 12, 412, ty + 12], fill=(255, 255, 230))
    if lt > 3.2:
        lab_at(frame, "NO OLD GUM HERE", 540, 1320, YEL, 64)

def made_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = min(ease_back(clamp((lt - 0.3) / 0.5)), 1.15)
    wad(d, 540, 640, max(4, 130 * p))
    for i, (txt, y) in enumerate((("RESINS", 840), ("SOFTENERS", 930), ("BUTYL RUBBER", 1020))):
        if lt > 1.0 + 0.6 * i:
            lab_at(frame, txt, 540, y, YEL if i == 2 else WHITE, 66)
    if lt > 3.6:
        # inner tube ring
        d.ellipse([400, 1110, 680, 1310], fill=(40, 40, 50), outline=OUTL, width=8)
        d.ellipse([480, 1170, 600, 1250], fill=(70, 110, 170), outline=OUTL, width=6)
        d.arc([420, 1125, 560, 1220], 190, 260, fill=(110, 110, 120), width=8)
        lab_at(frame, "ALSO IN INNER TUBES", 540, 470, WHITE, 56)

def digest_props(frame, d, T, sc):
    lt = T - sc["s"]
    stomach(d, 540, 940)
    wad(d, 520, 970, 80)
    # sugar cubes drift out of the gum and fade into the wall
    for k in range(5):
        a = clamp((lt - 0.6 - 0.4 * k) / 2.0)
        if 0 < a < 1:
            ang = -2.4 + k * 0.9
            x = 520 + 200 * a * math.cos(ang); y = 970 + 170 * a * math.sin(ang)
            d.rectangle([x - 22, y - 22, x + 22, y + 22], fill=WHITE, outline=OUTL, width=4)
    if lt > 1.4: lab_at(frame, "SUGAR: ABSORBED", 540, 520, WHITE, 62)
    if lt > 3.6: lab_at(frame, "BASE: NO ENZYMES", 540, 1290, YEL, 64)

# a winding gut path
PATH = [(170, 560), (910, 560), (910, 760), (170, 760), (170, 960), (910, 960), (910, 1160), (170, 1160),
        (170, 1300), (540, 1300)]
def along(f):
    segs = [(PATH[i], PATH[i + 1]) for i in range(len(PATH) - 1)]
    L = [math.dist(a, b) for a, b in segs]; tot = sum(L); t = f * tot
    for (a, b), l in zip(segs, L):
        if t <= l:
            u = t / l; return a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u
        t -= l
    return PATH[-1]

def journey_props(frame, d, T, sc):
    lt = T - sc["s"]
    d.line(PATH, fill=OUTL, width=74, joint="curve")
    d.line(PATH, fill=PINK, width=58, joint="curve")
    f = ease_out(clamp((lt - 0.4) / 5.0))
    x, y = along(f)
    for k in range(1, 4):  # food bits riding along
        fx, fy = along(max(0, f - 0.05 * k))
        d.ellipse([fx - 16, fy - 16, fx + 16, fy + 16], fill=(200, 160, 90), outline=OUTL, width=4)
    wad(d, x, y, 34)

def journey_clock(T):
    sc_s = 32.0
    h = int(round(40 * ease_out(clamp((T - sc_s - 0.4) / 5.0))))
    return f"HOUR {h}"

def warn_props(frame, d, T, sc):
    lt = T - sc["s"]
    n = min(9, int(max(0, lt - 0.3) / 0.3) + 1)
    pts = [(540, 900), (470, 870), (610, 870), (500, 950), (590, 950), (440, 920), (640, 920), (540, 830),
           (540, 990)]
    for i in range(n):
        wad(d, pts[i][0], pts[i][1], 70)
    if lt > 2.0: lab_at(frame, "RARE, BUT REAL", 540, 560, (255, 120, 80), 76)
    if lt > 3.8:
        # bin
        d.polygon([(420, 1120), (660, 1120), (630, 1330), (450, 1330)], fill=(70, 160, 110), outline=OUTL)
        d.rounded_rectangle([400, 1090, 680, 1130], radius=12, fill=(60, 140, 95), outline=OUTL, width=6)
        lab_at(frame, "BIN IT", 540, 1225, WHITE, 60)

def helix(d, cx, cy, h, T):
    for k in range(14):
        y = cy - h / 2 + k * h / 13
        a = T * 2 + k * 0.6
        x1 = cx + 70 * math.sin(a); x2 = cx - 70 * math.sin(a)
        d.line([(x1, y), (x2, y)], fill=(200, 200, 220), width=5)
        d.ellipse([x1 - 11, y - 11, x1 + 11, y + 11], fill=(90, 180, 255), outline=OUTL, width=3)
        d.ellipse([x2 - 11, y - 11, x2 + 11, y + 11], fill=(255, 120, 150), outline=OUTL, width=3)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    wad(d, 330, 960, 130, TAR, (60, 40, 25))
    for k in range(4):  # tooth marks
        d.arc([250 + 40 * k, 900, 290 + 40 * k, 940], 0, 180, fill=(50, 30, 20), width=6)
    if lt > 0.8: lab_at(frame, "5,700 YEARS OLD", 540, 520, YEL, 74)
    if lt > 1.8: helix(d, 760, 960, 380, T)
    if lt > 2.6: lab_at(frame, "WHOLE GENOME", 760, 1240, WHITE, 60)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="myth", s=4.0, e=11.0, bg="living", clock="THE MYTH", char="kid", pos=(540, 1080, 520),
         props_after=myth_after,
         narr="They say swallowed GUM stays in your stomach for 7 YEARS. Does it?", n_at=4.2, narr_y=1530),
    dict(id="scope", s=11.0, e=18.0, bg="night", clock="CAMERA CHECK", props=scope_props,
         narr="Doctors who look inside stomachs with CAMERAS don't find years-old gum.", n_at=11.2,
         narr_y=1530),
    dict(id="made", s=18.0, e=25.0, bg="night", clock="WHAT'S IN GUM?", props=made_props,
         narr="Gum BASE is rubbery stuff: resins, softeners, even BUTYL RUBBER.", n_at=18.2, narr_y=1530),
    dict(id="digest", s=25.0, e=32.0, bg="night", clock="INSIDE YOU", props=digest_props,
         narr="Your body absorbs the SUGAR, but has NO ENZYMES to break down the base.", n_at=25.2,
         narr_y=1530),
    dict(id="journey", s=32.0, e=39.0, bg="night", clock=journey_clock, props=journey_props,
         narr="So it just rides along with your food and leaves in about 40 HOURS.", n_at=32.2,
         narr_y=1530),
    dict(id="warn", s=39.0, e=TW, bg="night", clock="BUT...", props=warn_props,
         narr="Swallow LOTS of gum, often? It can rarely clump into a BLOCKAGE. Use the BIN!",
         n_at=39.2, narr_y=1530),
    dict(id="twist", s=TW, e=53.0, bg="twist", clock="PLOT TWIST", twist=True, props=twist_props,
         narr="Twist: a 5,700-YEAR-OLD chewed lump of birch tar gave scientists a WHOLE HUMAN GENOME!",
         n_at=TW + 0.2, narr_y=1530, say="Gum with DNA?!", say_at=TW + 3.6, pitch=620),
    dict(id="outro", s=53.0, e=58.0),
]

def intro_extra(frame, d, T):
    if T >= 1.6:
        p = min(ease_back((T - 1.6) / 0.5), 1.15)
        wad(d, 540, 1300, max(4, 150 * p))

cfg = dict(
    total=58.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 480, 0.2, "pop"),
        (title([("YOU SWALLOWED", WHITE)], 110), 690, 0.75, "right"),
        (title([("CHEWING", YEL)], 150), 830, 1.05, "left"),
        (title([("GUM?", YEL)], 150), 990, 1.35, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Did ", WHITE), ("YOU", YEL), (" believe", WHITE)], 84), 470, 0.15),
                      (title([("the 7-year myth?", WHITE)], 90), 600, 0.45)],
               row=[("kid", 1), ("uncle", 1), ("cat", 1), ("dog", 1), ("kid", "puff")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=25.0, melody=True),
           dict(t0=25.0, t1=39.0), dict(t0=39.0, t1=TW - 0.15, drums=False, minor=True),
           dict(t0=TW + 2.0, t1=58.0, melody=True)],
    drones=[dict(t0=39.2, dur=6.5, g=0.05), dict(t0=TW, dur=7.0, g=0.08)],
    fx=[("pop", 7.0, 0.4), ("gasp", 7.1, 0.25), ("ding", 7.6, 0.2), ("click", 12.0, 0.2), ("ding", 14.2, 0.2),
        ("pop", 18.4, 0.3), ("pop", 19.0, 0.25), ("pop", 19.6, 0.25), ("pop", 20.2, 0.25),
        ("bubbles", 25.6, 0.15, dict(dd=3.0)), ("tick", 33.0, 0.2), ("tick", 35.0, 0.2), ("ding", 37.4, 0.25),
        ("pop", 42.8, 0.3), ("pop", TW + 1.0, 0.25)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_swallowed_chewing_gum")
