#!/usr/bin/env python3
"""What if a whale swallowed you? Sources: National Geographic (2021) 'Most whales can't really swallow a human':
humpback mouth ~10 ft (~3 m), throat about fist-sized, stretching to ~15 in (~38 cm); sperm whales are the only one of
~90 whale species with a throat big enough to swallow a human; ~65 ft (~20 m) long; dive >10,000 ft (~3 km); colossal
squid found in their stomachs; 2021 Cape Cod lobster diver engulfed by a humpback, ~30 s, spat out, survived.
Whale stomachs: multi-chambered, main stomach secretes hydrochloric acid (Baleines en direct, GREMM).
Squid beaks accumulate in sperm whale stomachs (Inside Science/AIP; Smithsonian Ocean). Ambergris forms in the
intestine around indigestible squid beaks, usually passed with faeces, fresh it smells of faeces, prized as a perfume
fixative, ~1-5% of sperm whales (ScienceABC). India: sperm whale protected under the Wildlife (Protection) Act,
ambergris seizures by police (ThePrint 2022)."""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def put_label(frame, txt, cx, y, size=60, col=YEL):
    l = label(txt, size, col)
    comp(frame, l, cx - l.width / 2, y)

GREY = (120, 132, 150)
GREY_D = (92, 102, 120)
GREY_L = (170, 180, 196)

def sperm_whale(d, x, y, s, T, flip=False):
    """Sperm whale facing left (or right if flip): big boxy head, narrow lower jaw. (x, y) = head front centre."""
    f = -1 if flip else 1
    wob = 6 * s * math.sin(T * 2.2)
    def X(v): return x + f * v * s
    # tail flukes
    tx = X(820)
    d.polygon([(X(700), y - 20 * s), (tx, y - 90 * s + wob), (X(760), y), (tx, y + 90 * s + wob), (X(700), y + 20 * s)],
              fill=GREY_D, outline=OUTL)
    # body taper
    d.polygon([(X(260), y - 120 * s), (X(720), y - 26 * s), (X(720), y + 26 * s), (X(260), y + 110 * s)],
              fill=GREY, outline=OUTL)
    # boxy head
    x0, x1 = sorted([X(0), X(320)])
    d.rounded_rectangle([x0, y - 130 * s, x1, y + 110 * s], radius=int(70 * s), fill=GREY, outline=OUTL, width=max(3, int(6 * s)))
    # lower jaw
    j0, j1 = sorted([X(40), X(280)])
    d.rounded_rectangle([j0, y + 96 * s, j1, y + 128 * s], radius=int(14 * s), fill=GREY_L, outline=OUTL, width=max(2, int(4 * s)))
    # wrinkles
    for k in range(3):
        xx = X(380 + 80 * k)
        d.line([(xx, y - 70 * s), (xx + f * 20 * s, y + 40 * s)], fill=GREY_D, width=max(2, int(4 * s)))
    # eye
    ex = X(250)
    d.ellipse([ex - 12 * s, y + 40 * s, ex + 12 * s, y + 64 * s], fill=WHITE, outline=OUTL, width=max(2, int(3 * s)))
    d.ellipse([ex - 6 * s, y + 46 * s, ex + 6 * s, y + 58 * s], fill=OUTL)

def squid(d, x, y, s, T, col=(230, 110, 90)):
    """Squid pointing up, tentacles trailing down."""
    for k in range(8):
        dx = (k - 3.5) * 14 * s
        pts = []
        for i in range(8):
            t = i / 7
            pts.append((x + dx * (1 + t) + 18 * s * math.sin(T * 3 + k + t * 4), y + 60 * s + t * 170 * s))
        d.line(pts, fill=OUTL, width=max(4, int(11 * s)))
        d.line(pts, fill=col, width=max(2, int(6 * s)))
    d.polygon([(x, y - 170 * s), (x - 60 * s, y - 90 * s), (x + 60 * s, y - 90 * s)], fill=col, outline=OUTL)
    d.ellipse([x - 52 * s, y - 120 * s, x + 52 * s, y + 70 * s], fill=col, outline=OUTL, width=max(3, int(5 * s)))
    for sx in (-22, 22):
        d.ellipse([x + sx * s - 13 * s, y + 20 * s, x + sx * s + 13 * s, y + 46 * s], fill=WHITE, outline=OUTL, width=3)
        d.ellipse([x + sx * s - 6 * s, y + 27 * s, x + sx * s + 6 * s, y + 41 * s], fill=OUTL)

def beak(d, x, y, s, rot=0.0):
    pts = [(0, -1), (0.8, 0.2), (0.2, 0.9), (-0.5, 0.4)]
    c, si = math.cos(rot), math.sin(rot)
    P = [(x + s * (px * c - py * si), y + s * (px * si + py * c)) for px, py in pts]
    d.polygon(P, fill=(60, 40, 30), outline=OUTL)

def lump(d, x, y, s, col=(190, 182, 160)):
    d.polygon([(x - 90 * s, y + 10 * s), (x - 60 * s, y - 50 * s), (x + 10 * s, y - 70 * s), (x + 80 * s, y - 30 * s),
               (x + 95 * s, y + 30 * s), (x + 30 * s, y + 70 * s), (x - 60 * s, y + 55 * s)], fill=col, outline=OUTL)
    for k in range(6):
        a = k * 1.7
        d.ellipse([x + 50 * s * math.cos(a) - 7 * s, y + 30 * s * math.sin(a) - 7 * s,
                   x + 50 * s * math.cos(a) + 7 * s, y + 30 * s * math.sin(a) + 7 * s], fill=(150, 140, 118))

def bubbles(d, T, n=10, x0=150, x1=950, y0=500, y1=1300):
    for k in range(n):
        ph = (T * 0.25 + k / n) % 1.0
        x = x0 + (k * 263) % (x1 - x0) + 15 * math.sin(T * 2 + k)
        y = y1 - (y1 - y0) * ph
        r = 10 + 5 * (k % 3)
        d.ellipse([x - r, y - r, x + r, y + r], outline=(220, 245, 255), width=4)

def kid_small(frame, T, x, y, size=200, look=(0, 0), state=1, talk=0.0):
    paste_c(frame, draw_char("kid", size, T, talk, E.blink_at(T, 0.4), look, state), x, y)

# ------------------------------------------------------------------ scene props
def mouth_props(frame, d, T, sc):
    bubbles(d, T, 8)
    lt = T - sc["s"]
    p = ease_out(clamp((lt - 0.4) / 1.0))
    d.line([(120, 1230), (120 + 840 * p, 1230)], fill=WHITE, width=8)
    d.line([(120, 1205), (120, 1255)], fill=WHITE, width=8)
    if p >= 1:
        d.line([(960, 1205), (960, 1255)], fill=WHITE, width=8)
        put_label(frame, "MOUTH ~3 M", 540, 1250, 44, WHITE)

def mouth_after(frame, d, T, sc):
    kid_small(frame, T, 860, 880, 180, (-0.6, 0.4))

def throat_props(frame, d, T, sc):
    bubbles(d, T, 8)
    lt = T - sc["s"]
    r = 60 + 50 * ease_out(clamp((lt - 1.0) / 1.2))
    cx, cy = 800, 1000
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(125, 28, 48), outline=OUTL, width=7)
    put_label(frame, "THROAT ~38 CM", cx - 30, 1150, 44)

def diver_props(frame, d, T, sc):
    lt = T - sc["s"]
    bubbles(d, T, 10)

def diver_after(frame, d, T, sc):
    lt = T - sc["s"]
    kid_small(frame, T, 540, 820, 200, (0, -0.4))
    # whale jaws closing over the diver: upper jaw from above, lower jaw from below
    q = ease_out(clamp((lt - 2.0) / 0.9))
    if q > 0:
        top = 380 + 440 * q
        bot = 1330 - 510 * q
        d.rectangle([0, 340, W, top], fill=(92, 146, 214), outline=OUTL, width=8)
        d.rectangle([0, bot, W, 1340], fill=(204, 228, 248), outline=OUTL, width=8)
        for x in range(60, W, 90):
            d.line([(x, bot + 20), (x + 10, 1330)], fill=(150, 186, 220), width=6)
        ey = top - 110
        d.ellipse([110, ey - 45, 200, ey + 45], fill=WHITE, outline=OUTL, width=6)
        d.ellipse([140, ey - 20, 180, ey + 20], fill=OUTL)
    if lt > 3.2:
        put_label(frame, "LIGHTS OUT!", 540, 760, 74)

def spit_props(frame, d, T, sc):
    lt = T - sc["s"]
    bubbles(d, T, 12)
    put_label(frame, "~30 SECONDS", 540, 380, 70)

def spit_after(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_out(clamp((lt - 0.6) / 0.8))
    kid_small(frame, T, 380 + 400 * p, 1150 - 420 * p + 80 * p * p, 190, (-0.4, 0), "puff" if lt < 3 else 1)

def sperm_props(frame, d, T, sc):
    lt = T - sc["s"]
    x = 1200 - 900 * ease_out(clamp((lt - 0.2) / 2.0))
    sperm_whale(d, x, 1010, 0.62, T)
    put_label(frame, "1 OF ~90 SPECIES", 540, 380, 60)

def dive_props(frame, d, T, sc):
    lt = T - sc["s"]
    # depth gauge on the left
    p = ease_out(clamp((lt - 0.3) / 3.0))
    d.rectangle([70, 420, 100, 1300], fill=(20, 40, 80), outline=WHITE, width=4)
    d.rectangle([74, 424, 96, 424 + 872 * p], fill=YEL)
    sperm_whale(d, 240, 640 + 420 * p, 0.42, T)
    squid(d, 800, 1050, 0.75, T)
    if p > 0.8:
        put_label(frame, "3 KM DEEP", 330, 440, 56)

def inside_props(frame, d, T, sc):
    lt = T - sc["s"]
    # dark stomach walls with acid puddle
    d.rectangle([0, 360, W, 1340], fill=(60, 18, 34))
    d.ellipse([-200, 300, 1280, 1460], fill=(110, 32, 52), outline=OUTL, width=10)
    for k in range(9):
        x = 120 + k * 110
        d.arc([x - 60, 360, x + 60, 520], 0, 180, fill=(150, 50, 70), width=10)
    d.ellipse([140, 1180, 940, 1320], fill=(170, 220, 70), outline=OUTL, width=6)
    for k in range(7):
        ph = (lt * 0.6 + k / 7) % 1.0
        x = 200 + k * 100
        y = 1240 - 160 * ph
        d.ellipse([x - 10, y - 10, x + 10, y + 10], outline=(210, 250, 120), width=4)
    put_label(frame, "NO AIR + ACID", 540, 380, 64)

def beaks_props(frame, d, T, sc):
    lt = T - sc["s"]
    n = int(clamp((lt - 0.3) / 2.5) * 24)
    for k in range(n):
        beak(d, 300 + (k * 97) % 480, 1250 - (k // 6) * 40 - (k * 13) % 30, 26, k * 0.9)
    if lt > 3.3:
        p = ease_back(clamp((lt - 3.3) / 0.5))
        lump(d, 540, 1000, 1.2 * p)
        put_label(frame, "AMBERGRIS", 540, 380, 70)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    lump(d, 800, 1220, 0.9, (70, 60, 50))
    put_label(frame, "NOT VOMIT", 540, 380, 74)
    if lt > 2.4:
        for k in range(3):   # stink lines
            x = 760 + k * 40
            pts = [(x + 12 * math.sin(lt * 4 + i + k), 1140 - i * 22) for i in range(8)]
            d.line(pts, fill=(150, 190, 90), width=6)

def india_props(frame, d, T, sc):
    lt = T - sc["s"]
    lump(d, 810, 1240, 0.8)
    # perfume bottle
    d.rounded_rectangle([210, 1150, 330, 1300], radius=20, fill=(250, 210, 230), outline=OUTL, width=6)
    d.rectangle([250, 1110, 290, 1150], fill=(220, 180, 90), outline=OUTL, width=5)
    put_label(frame, "PROTECTED IN INDIA", 540, 380, 58)

def intro_extra(frame, d, T):
    if T >= 1.9:
        x = 540 + 30 * math.sin(T * 2); y = 1440 + 16 * math.sin(T * 3)
        paste_c(frame, draw_char("whale", 360, T, 0, False, (0, 0), 1), x, y, ease_back((T - 1.9) / 0.4))

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="mouth", s=4.0, e=11.0, bg="sea", clock="HUMPBACK", char="whale", pos=(500, 1000, 600),
         props=mouth_props, props_after=mouth_after, look=(0.4, -0.2),
         narr="A humpback whale's mouth is HUGE: about 3 M across.", n_at=4.2, narr_y=1500,
         say="Room for ONE more?", say_at=6.6, pitch=160),
    dict(id="throat", s=11.0, e=18.0, bg="sea", clock="THE THROAT", char="whale", pos=(330, 1040, 440),
         props=throat_props, look=(0.6, 0),
         narr="But its throat is about FIST-sized. Even stretched: only about 38 CM.", n_at=11.2, narr_y=1500,
         say="You won't FIT, buddy.", say_at=14.0, pitch=160),
    dict(id="diver", s=18.0, e=25.0, bg="sea", clock="2021, USA", props=diver_props, props_after=diver_after,
         narr="It really HAPPENED: in 2021 a humpback scooped up a diver by ACCIDENT.", n_at=18.2, narr_y=1500),
    dict(id="spit", s=25.0, e=32.0, bg="sea", clock="SPAT OUT", char="whale", pos=(330, 1180, 480),
         props=spit_props, props_after=spit_after, look=(0.6, -0.3),
         narr="About 30 SECONDS in the dark... then it surfaced and SPAT him out. He SURVIVED.", n_at=25.2,
         narr_y=1500, say="PTOO! Not FOOD!", say_at=27.8, pitch=170),
    dict(id="sperm", s=32.0, e=39.0, bg="deep", clock="THE ONE", props=sperm_props,
         narr="Of about 90 whale species, only ONE has a throat big enough: the SPERM WHALE.", n_at=32.2,
         narr_y=1500),
    dict(id="dive", s=39.0, e=46.0, bg="deep", clock="20 M LONG", props=dive_props,
         narr="About 20 M long, it dives more than 3 KM deep to hunt GIANT SQUID.", n_at=39.2, narr_y=1500),
    dict(id="inside", s=46.0, e=53.0, bg="deep", clock="INSIDE", props=inside_props,
         narr="Swallowed? Total DARKNESS, NO AIR, and a stomach that makes ACID.", n_at=46.2, narr_y=1500),
    dict(id="beaks", s=53.0, e=60.5, bg="deep", clock="SQUID BEAKS", props=beaks_props,
         narr="Squid BEAKS can't be digested. In the gut, they get coated in wax: AMBERGRIS.", n_at=53.2,
         narr_y=1500),
    dict(id="twist", s=60.5, e=68.0, bg="twist", clock="PLOT TWIST", char="kid", state="puff",
         pos=(320, 1080, 400), props=twist_props, twist=True, look=(0.6, 0.3),
         narr="They call it 'whale VOMIT'. It mostly comes out the OTHER END. Fresh, it smells like POOP.",
         n_at=60.7, narr_y=1500, say="Wait... it's POOP?!", say_at=63.6, pitch=600),
    dict(id="india", s=68.0, e=75.0, bg="ocean", clock="INDIA", char="uncle", pos=(540, 1070, 400),
         props=india_props, look=(0.3, 0.2),
         narr="Perfumers PRIZE it. But sperm whales are PROTECTED in India: selling ambergris is ILLEGAL.",
         n_at=68.2, narr_y=1500, say="Found a lump? Tell the POLICE!", say_at=71.0, pitch=300),
    dict(id="outro", s=75.0, e=80.0),
]

cfg = dict(
    total=80.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("a WHALE", WHITE)], 140), 770, 0.75, "right"),
        (title([("SWALLOWED", WHITE)], 140), 915, 1.05, "left"),
        (title([("YOU?", YEL)], 150), 1070, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" swim", WHITE)], 100), 470, 0.15),
                      (title([("near a whale?", YEL)], 104), 600, 0.45)],
               row=[("whale", 1), ("kid", 1), ("fish", 1), ("uncle", 1), ("whale", "wink")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=32.0), dict(t0=32.0, t1=53.0, drums=False, minor=True),
           dict(t0=53.0, t1=60.35, minor=True), dict(t0=68.0, t1=80.0, melody=True)],
    drones=[dict(t0=32.0, dur=21.0, g=0.06)],
    fx=[("waves", 0.3, 0.3, dict(dd=4.0)), ("splash", 4.4, 0.7), ("bubbles", 11.2, 0.5, dict(dd=6.0)),
        ("underwater", 18.0, 0.4, dict(dd=7.0)), ("crash", 20.3, 0.4), ("splash", 25.7, 0.8),
        ("underwater", 32.0, 0.4, dict(dd=14.0)), ("heartbeat", 46.2, 0.5, dict(dd=6.5)),
        ("pop", 56.4, 0.6), ("waves", 68.2, 0.3, dict(dd=6.5))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_whale_swallowed_you")
