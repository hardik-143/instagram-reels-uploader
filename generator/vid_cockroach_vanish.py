#!/usr/bin/env python3
"""What if every cockroach vanished? ~4,600 species, only ~30 live around humans, ~4 real pests; roach-like insects
~320 million years old (before dinosaurs); forest leaf recycling returns nitrogen to soil; birds and rodents eat
them; wasps that lay eggs only in roach eggs would almost certainly go extinct (LiveScience / Kambhampati).
Twist: termites are now classified as cockroaches (Blattodea), so they would vanish too; one Macrotermes colony
can hold up to 3 million."""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, comp, paste_c, ease_back, ease_out, clamp, text_sprite

GONE = 25.6   # the last roach scuttles away

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=64):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

# ---------------------------------------------------------------- new character: a friendly cockroach
BROWN, DARK, PALE = (150, 84, 44), (104, 58, 30), (196, 128, 80)

def roach(B, T, talk=0.0, blink=False, look=(0, 0), state=1):
    S = 2 * B
    L = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    u = S / 200.0
    lw = lambda w: max(1, int(round(w * u)))
    def EL(b, fill, w=2.6):
        d.ellipse([v * u for v in b], fill=fill, outline=OUTL if w else None, width=lw(w) if w else 0)
    def LN(pts, w=2.6, fill=OUTL):
        d.line([(x * u, y * u) for x, y in pts], fill=fill, width=lw(w), joint="curve")
    wig = math.sin(T * 9)
    # legs: three per side, scuttling
    for i, yy in enumerate((112, 136, 160)):
        k = 6 * math.sin(T * 14 + i * 2.1)
        LN([(62, yy), (34, yy - 8 + k), (20, yy + 14 + k)], 3.4)
        LN([(138, yy), (166, yy - 8 - k), (180, yy + 14 - k)], 3.4)
    # antennae
    for s in (-1, 1):
        x0 = 100 + 16 * s
        pts = [(x0, 48)]
        for j in range(1, 7):
            pts.append((x0 + s * (6 * j + 4 * math.sin(T * 4 + j * 0.6 + wig * 0.3)), 48 - 7 * j - j * j * 0.6))
        LN(pts, 2.6)
    # body + wing cases
    EL((52, 78, 148, 194), BROWN)
    d.line([(100 * u, 92 * u), (100 * u, 192 * u)], fill=DARK, width=lw(2.4))
    EL((64, 96, 90, 128), PALE, w=0)
    # head
    EL((56, 36, 144, 108), DARK)
    EL((70, 82, 84, 92), (255, 140, 140), w=0); EL((116, 82, 130, 92), (255, 140, 140), w=0)
    for i, x in enumerate((84, 116)):
        r = 13
        if blink or (state == "wink" and i == 1):
            d.arc([(x - r) * u, (66 - r * 0.7) * u, (x + r) * u, (66 + r * 0.7) * u], 200, 340, fill=OUTL, width=lw(3))
            continue
        EL((x - r, 66 - r * 1.1, x + r, 66 + r * 1.1), WHITE, w=2.2)
        px, py = x + look[0] * 5, 66 + look[1] * 5
        EL((px - 6, py - 7, px + 6, py + 7), (25, 20, 30), w=0)
        EL((px - 5, py - 6, px - 1, py - 2), WHITE, w=0)
    if talk > 0.08:
        h = 4 + 12 * talk
        EL((90, 88, 110, 92 + h), (125, 28, 48), w=1.8)
    else:
        d.arc([88 * u, 82 * u, 112 * u, 98 * u], 20, 160, fill=OUTL, width=lw(2.6))
    return L.reduce(2)

_draw_orig = E.draw_char
def draw_char(kind, B, T, talk=0.0, blink=False, look=(0, 0), state=1):
    if kind == "roach":
        return roach(B, T, talk, blink, look, state)
    return _draw_orig(kind, B, T, talk, blink, look, state)
E.draw_char = draw_char   # the engine looks the name up at render time

# ---------------------------------------------------------------- props
def mini_roach(frame, x, y, size, T, look=(0, 0)):
    spr = roach(size, T, 0, False, look)
    comp(frame, spr, x - size / 2, y - size / 2)

def species_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 0.6:
        top_label(frame, "~4,600 SPECIES", 380, YEL, 76)

def pests_props(frame, d, T, sc):
    lt = T - sc["s"]
    # 30 small roaches; only 4 get a red "pest" ring
    for k in range(30):
        if lt < 0.4 + k * 0.05: continue
        x = 120 + (k % 10) * 93; y = 400 + (k // 10) * 92
        mini_roach(frame, x, y, 78, T + k)
        if k in (3, 12, 17, 26) and lt > 2.6:
            d.ellipse([x - 44, y - 44, x + 44, y + 44], outline=(230, 40, 50), width=7)

def ancient_props(frame, d, T, sc):
    lt = T - sc["s"]
    x = 250 + 40 * math.sin(T * 1.5)
    mini_roach(frame, x, 1240, 200, T, look=(0.6, -0.2))
    if lt > 0.6:
        top_label(frame, "~320 MILLION YEARS", 380, YEL, 68)

def gone_props(frame, d, T, sc):
    if T < GONE + 1.2:
        q = clamp((T - GONE) / 1.1)
        mini_roach(frame, 300 - 900 * q * q, 1230, 220, T * 2, look=(-0.8, 0))
    else:
        top_label(frame, "0 COCKROACHES", 380, YEL, 70)

def tree(d, x, y, s=1.0):
    d.rectangle([x - 18 * s, y - 40 * s, x + 18 * s, y + 220 * s], fill=(120, 80, 50))
    for dx, dy, r in ((0, -120, 110), (-80, -40, 90), (80, -40, 90), (0, -20, 100)):
        d.ellipse([x + (dx - r) * s, y + (dy - r) * s, x + (dx + r) * s, y + (dy + r) * s], fill=(70, 150, 70))

def forest_props(frame, d, T, sc):
    lt = T - sc["s"]
    tree(d, 140, 700, 0.9); tree(d, 950, 680, 1.0)
    # leaves keep falling and piling up
    for k in range(14):
        ph = (lt * 0.25 + k / 14) % 1.0
        x = 120 + (k * 173) % 860 + 30 * math.sin(T * 2 + k)
        y = 600 + 700 * ph
        d.ellipse([x - 18, y - 9, x + 18, y + 9], fill=(196, 130, 50) if k % 2 else (170, 100, 40))
    pile = 30 + 60 * clamp(lt / 6)
    d.ellipse([60, 1300 - pile, 1020, 1300 + pile], fill=(160, 104, 46))
    if lt > 3.0:
        top_label(frame, "NITROGEN", 380, YEL, 72)

def rat(d, x, y, s=1.0):
    d.ellipse([x - 50 * s, y - 28 * s, x + 50 * s, y + 28 * s], fill=(150, 150, 160), outline=OUTL, width=4)
    d.ellipse([x + 30 * s, y - 40 * s, x + 60 * s, y - 10 * s], fill=(190, 170, 180), outline=OUTL, width=4)
    d.ellipse([x + 52 * s, y - 8 * s, x + 64 * s, y + 4 * s], fill=OUTL)
    d.line([(x - 50 * s, y), (x - 100 * s, y - 20 * s)], fill=OUTL, width=5)

def food_props(frame, d, T, sc):
    lt = T - sc["s"]
    n = 3 if lt < 3.0 else (2 if lt < 4.0 else (1 if lt < 5.0 else 0))
    for k in range(n):
        rat(d, 200 + k * 330, 1250, 0.9)

def wasp(frame, x, y, s, T, alive=1.0):
    L = Image.new("RGBA", (int(320 * s), int(240 * s)), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    c = lambda v: v * s
    flap = 10 * math.sin(T * 40)
    d.ellipse([c(90), c(10 - flap), c(170), c(100)], fill=(220, 240, 255, 200), outline=OUTL, width=3)
    d.ellipse([c(150), c(10 + flap), c(230), c(100)], fill=(220, 240, 255, 200), outline=OUTL, width=3)
    d.ellipse([c(150), c(90), c(300), c(170)], fill=(40, 150, 120), outline=OUTL, width=4)
    d.ellipse([c(100), c(100), c(170), c(160)], fill=(40, 120, 150), outline=OUTL, width=4)
    d.ellipse([c(30), c(90), c(110), c(170)], fill=(30, 110, 140), outline=OUTL, width=4)
    d.ellipse([c(48), c(108), c(78), c(140)], fill=WHITE, outline=OUTL, width=3)
    d.ellipse([c(56), c(116), c(70), c(132)], fill=OUTL)
    d.line([(c(50), c(96)), (c(20), c(40))], fill=OUTL, width=4)
    d.line([(c(80), c(92)), (c(80), c(30))], fill=OUTL, width=4)
    if alive < 1:
        L.putalpha(L.getchannel("A").point(lambda a: int(a * alive)))
    comp(frame, L, x - L.width / 2, y - L.height / 2)

def wasp_props(frame, d, T, sc):
    lt = T - sc["s"]
    # roach egg case (ootheca) on the ground
    d.rounded_rectangle([420, 1210, 660, 1290], radius=30, fill=(120, 66, 34), outline=OUTL, width=5)
    for k in range(7):
        d.line([(450 + k * 30, 1218), (450 + k * 30, 1282)], fill=(90, 48, 24), width=4)

def wasp_after(frame, d, T, sc):
    lt = T - sc["s"]
    alive = 1.0 - clamp((lt - 4.6) / 1.6)
    wasp(frame, 540 + 140 * math.sin(T * 1.7), 1010 + 30 * math.sin(T * 3), 1.6, T, alive)
    if lt > 5.2:
        top_label(frame, "GONE TOO?", 380, YEL, 72)

def termite(d, x, y, s=1.0):
    for i, (dx, r) in enumerate(((0, 22), (34, 16), (62, 18))):
        d.ellipse([x + dx * s - r * s, y - r * 0.8 * s, x + dx * s + r * s, y + r * 0.8 * s],
                  fill=(246, 230, 196) if i < 2 else (210, 130, 60), outline=OUTL, width=3)
    for k in (-1, 1):
        d.line([(x + 20 * s, y), (x + 20 * s, y + k * 24 * s)], fill=OUTL, width=3)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    for k in range(12):
        if lt < 1.0 + k * 0.12: continue
        x = (k * 97 + T * 60) % 1200 - 80
        y = 1275 + (k % 2) * 40
        termite(d, x, y, 1.1)

def colony_props(frame, d, T, sc):
    lt = T - sc["s"]
    # big termite mound
    d.polygon([(560, 600), (620, 610), (700, 1000), (760, 1320), (300, 1320), (400, 980), (500, 620)],
              fill=(178, 104, 56), outline=OUTL)
    for k in range(6):
        y = 700 + k * 100
        d.ellipse([520 - k * 20, y, 548 - k * 20, y + 20], fill=(90, 50, 24))
    for k in range(10):
        x = (k * 131 + T * 80) % 1180 - 60
        termite(d, x, 1340 + (k % 2) * 30, 0.9)
    if lt > 0.6:
        top_label(frame, "UP TO 3 MILLION", 380, YEL, 72)

def flash(frame, T, sc):
    lt = T - GONE
    if 0 <= lt < 0.3:
        return Image.blend(frame, Image.new("RGBA", (W, H), (255, 255, 255, 255)), 0.6 * (1 - lt / 0.3))
    return frame

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="species", s=4.0, e=11.0, bg="cat", clock="MEET THE ROACHES", char="roach", pos=(540, 1060, 520),
         props=species_props, look=(0.2, 0.2),
         narr="Scientists know about 4,600 COCKROACH species on Earth.", n_at=4.2, narr_y=1500,
         say="We're a BIG family!", say_at=6.6, pitch=420),
    dict(id="pests", s=11.0, e=18.0, bg="cat", clock="ONLY A FEW PESTS", char="roach", pos=(540, 1110, 420),
         props=pests_props, look=(0, -0.5),
         narr="Only about 30 live around humans. Just 4 are real kitchen PESTS.", n_at=11.2, narr_y=1500,
         say="Don't judge us ALL!", say_at=14.6, pitch=420),
    dict(id="ancient", s=18.0, e=25.0, bg="cretaceous", clock="BEFORE DINOSAURS", char="trex", pos=(720, 1080, 460),
         props=ancient_props, look=(-0.6, 0.3),
         narr="Roach-like insects showed up about 320 MILLION years ago, before DINOSAURS.", n_at=18.2, narr_y=1500,
         say="You were here FIRST?!", say_at=21.6, pitch=180),
    dict(id="gone", s=25.0, e=32.0, bg="cat", clock="ALL GONE", char="uncle", pos=(620, 1090, 460), enter=GONE + 0.6,
         props=gone_props, overlay=flash, look=(-0.4, 0),
         narr="Now imagine every cockroach on Earth... GONE. Forever.", n_at=25.2, narr_y=1500,
         say="FINALLY! Peace in my KITCHEN!", say_at=27.6, pitch=150),
    dict(id="forest", s=32.0, e=39.0, bg="day", clock="MEANWHILE, IN FORESTS", char="flower", pos=(540, 1080, 400),
         props=forest_props, look=(0, 0.5),
         narr="In forests, roaches eat dead leaves. Their poop returns NITROGEN to soil.", n_at=32.2, narr_y=1500,
         say="Hey, I NEEDED that!", say_at=35.4, pitch=380),
    dict(id="food", s=39.0, e=46.0, bg="cow", clock="LUNCH IS CANCELLED", char="cat", pos=(540, 1060, 460),
         props=food_props, look=(-0.3, 0.5),
         narr="Birds and rats eat roaches. Fewer rats? Hungry cats, snakes and HAWKS.", n_at=39.2, narr_y=1500,
         say="Where's my DINNER?!", say_at=42.6, pitch=330),
    dict(id="wasp", s=46.0, e=53.0, bg="day", clock="TINY WASPS", props=wasp_props, props_after=wasp_after,
         narr="Some wasps lay eggs ONLY in roach eggs. They'd almost surely vanish.", n_at=46.2, narr_y=1500,
         say="My babies NEED roaches!", say_at=48.8, pitch=620),
    dict(id="twist", s=53.0, e=60.0, bg="twist", clock="PLOT TWIST", char="roach", state="wink",
         pos=(540, 1030, 460), props=twist_props, twist=True, look=(0.3, 0.3),
         narr="Twist: scientists now classify TERMITES as cockroaches. They'd vanish TOO!", n_at=53.2, narr_y=1500,
         say="Termites are FAMILY!", say_at=56.6, pitch=420),
    dict(id="colony", s=60.0, e=67.0, bg="digsite", clock="ONE COLONY", char="kid", pos=(880, 1110, 300),
         props=colony_props, look=(-0.6, -0.2),
         narr="One termite colony can hold up to 3 MILLION, all recycling dead WOOD.", n_at=60.2, narr_y=1530,
         say="That's a LOT of cousins!", say_at=63.4, pitch=400),
    dict(id="outro", s=67.0, e=72.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        x = 540 + 40 * math.sin(T * 2); y = 1420 + 12 * math.sin(T * 5)
        paste_c(frame, roach(380, T, 0, False, (0, 0.2)), x, y, ease_back((T - 1.9) / 0.4))

cfg = dict(
    total=72.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("EVERY", WHITE)], 140), 770, 0.75, "right"),
        (title([("COCKROACH", WHITE)], 140), 915, 1.05, "left"),
        (title([("...", WHITE), ("VANISHED?", YEL)], 100), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" miss", WHITE)], 100), 470, 0.15),
                      (title([("the roaches?", YEL)], 116), 600, 0.45)],
               row=[("roach", 1), ("cat", 1), ("flower", 1), ("kid", 1), ("roach", "wink")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=25.0), dict(t0=25.0, t1=32.0, melody=True),
           dict(t0=32.0, t1=46.0, drums=False, minor=True), dict(t0=46.0, t1=52.85, drums=False, minor=True),
           dict(t0=60.0, t1=72.0, melody=True)],
    fx=[("click", 4.5, 0.4), ("rumble", 18.2, 0.4, dict(dd=3.0)), ("whoosh", GONE, 1.0), ("cheer", GONE + 2.4, 0.5),
        ("wind", 32.2, 0.3, dict(dd=6.5)), ("pop", 42.0, 0.5), ("pop", 43.0, 0.5), ("pop", 44.0, 0.5),
        ("powerdown", 50.8, 0.5), ("ding", 64.0, 0.3)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_every_cockroach_vanished")
