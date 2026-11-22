#!/usr/bin/env python3
"""What if every bee vanished? Facts: over 20,000 bee species (FAO pollination page); a worker honey bee makes about
1/12 teaspoon of honey in her life (Kansas DOT / Pollinator Partnership 'Busy as a Bee'); about 75% of global food crop
TYPES depend on pollinators to some extent, ~35% of production by volume (FAO; Our World in Data, Ritchie 2021);
cereals such as wheat, rice and maize do not rely on bees at all (OWID); losing all pollinators would cut crop
production by roughly 5% (high-income) to 8% (low/middle-income) (OWID, citing Aizen et al.); fully dependent crops
include melons, kiwi, Brazil nuts and cocoa (OWID); in Maoxian County, Sichuan, farmers hand-pollinate apple and pear
blossoms ('The Human Pollinators of Fruit Crops in Maoxian County, Sichuan', Mountain Research and Development 2012);
cacao flowers are pollinated by tiny midges no bigger than a pinhead (US National Park Service, 'Chocolate midge').
Twist: no substantive evidence Einstein said 'if bees disappeared man would have 4 years left'; earliest known version
is a May 1965 French magazine, ~10 years after he died in 1955 (Quote Investigator 2013/2024)."""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, comp, ease_back, ease_out, clamp, text_sprite

TW = 60.0
GONE = 9.0     # the bees vanish
BEEY = (255, 200, 40)
HONEY = (240, 160, 30)

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

# ---------------------------------------------------------------- new character: a friendly bee
def bee(B, T, talk=0.0, blink=False, look=(0, 0), state=1):
    S = 2 * B
    L = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    u = S / 200.0
    lw = lambda w: max(1, int(round(w * u)))
    def EL(b, fill, w=2.6):
        d.ellipse([v * u for v in b], fill=fill, outline=OUTL if w else None, width=lw(w) if w else 0)
    def LN(pts, w=2.6, fill=OUTL):
        d.line([(x * u, y * u) for x, y in pts], fill=fill, width=lw(w), joint="curve")
    f = math.sin(T * 40)
    # wings (flutter)
    for sx in (-1, 1):
        cx = 100 + sx * 38
        h = 30 + 10 * f
        EL((cx - 30, 52 - h, cx + 30, 62), (225, 240, 255), 2.2)
    # stinger
    d.polygon([(92 * u, 168 * u), (108 * u, 168 * u), (100 * u, 186 * u)], fill=OUTL)
    # body with stripes
    EL((52, 60, 148, 172), BEEY, 3.0)
    for y in (118, 142):
        LN([(56, y), (144, y)], 9, OUTL)
    # antennae
    LN([(86, 66), (74, 36)], 2.6); LN([(114, 66), (126, 36)], 2.6)
    EL((68, 30, 80, 42), OUTL, 0); EL((120, 30, 132, 42), OUTL, 0)
    # eyes
    for x in (84, 116):
        if blink:
            LN([(x - 9, 88), (x + 9, 88)], 2.6)
            continue
        EL((x - 10, 77, x + 10, 99), WHITE, 2.2)
        px, py = x + look[0] * 4, 88 + look[1] * 4
        EL((px - 5, py - 6, px + 5, py + 6), (25, 20, 30), 0)
        EL((px - 4, py - 5, px - 1, py - 2), WHITE, 0)
    # cheeks + mouth
    EL((66, 96, 76, 104), (255, 140, 140), 0); EL((124, 96, 134, 104), (255, 140, 140), 0)
    if talk > 0.08:
        h = 3 + 9 * talk
        EL((92, 100, 108, 104 + h), (125, 28, 48), 1.8)
    else:
        d.arc([90 * u, 94 * u, 110 * u, 108 * u], 20, 160, fill=OUTL, width=lw(2.6))
    return L.reduce(2)

_draw_orig = E.draw_char
def draw_char(kind, B, T, talk=0.0, blink=False, look=(0, 0), state=1):
    if kind == "bee":
        return bee(B, T, talk, blink, look, state)
    return _draw_orig(kind, B, T, talk, blink, look, state)
E.draw_char = draw_char

def mini_bee(frame, x, y, size, T):
    spr = bee(size, T, 0, False, (0, 0))
    comp(frame, spr, x - size / 2, y - size / 2)

# ---------------------------------------------------------------- props
def swarm_props(frame, d, T, sc):
    lt = T - sc["s"]
    if T < GONE:
        for k in range(14):
            x = 120 + (k * 173) % 840 + 40 * math.sin(T * 2 + k)
            y = 700 + (k * 97) % 560 + 30 * math.cos(T * 3 + k * 1.3)
            if abs(x - 540) < 200 and abs(y - 1080) < 200: continue
            mini_bee(frame, x, y, 90, T + k)
    else:
        p = clamp((T - GONE) / 0.4)
        for k in range(10):  # little puffs where bees were
            x = 120 + (k * 173) % 840; y = 700 + (k * 97) % 560
            r = 30 + 50 * p
            if abs(x - 540) < 200 and abs(y - 1080) < 200: continue
            if p < 1: d.ellipse([x - r, y - r, x + r, y + r], outline=WHITE, width=6)
    if lt > 0.5: top_label(frame, "20,000+ KINDS OF BEES", 380, YEL, 76)

def bee_pos(T):
    if T < GONE: return (540, 1080, 420)
    return (540, 1080, max(1, int(420 * (1 - clamp((T - GONE) / 0.35)))))

def honey_props(frame, d, T, sc):
    lt = T - sc["s"]
    jx, jy = 790, 1150
    lvl = 1 - ease_out(clamp((lt - 2.5) / 2.5))
    d.rounded_rectangle([jx - 140, jy - 220, jx + 140, jy + 140], radius=40, fill=(235, 245, 250), outline=OUTL, width=8)
    if lvl > 0.02:
        top = jy + 120 - 320 * lvl
        d.rounded_rectangle([jx - 118, top, jx + 118, jy + 120], radius=26, fill=HONEY)
    d.rectangle([jx - 150, jy - 260, jx + 150, jy - 215], fill=(200, 80, 60), outline=OUTL, width=7)
    at_label(frame, "HONEY", jx, jy - 40, WHITE, 52)
    # teaspoon
    if lt > 0.8:
        d.ellipse([140, 1290, 260, 1340], fill=(200, 205, 215), outline=OUTL, width=6)
        d.line([(255, 1312), (420, 1300)], fill=OUTL, width=12)
        d.ellipse([185, 1303, 215, 1327], fill=HONEY)
    if lt > 0.5: top_label(frame, "1/12 TEASPOON", 380, YEL, 96)

def fruit(d, x, y, r, col, leaf=True, stripes=None):
    d.ellipse([x - r, y - r, x + r, y + r], fill=col, outline=OUTL, width=6)
    if stripes:
        for k in (-0.5, 0, 0.5):
            d.arc([x - r * (1 - abs(k)) - 4, y - r, x + r * (1 - abs(k)) + 4, y + r], 250, 290, fill=stripes, width=8)
    if leaf:
        d.line([(x, y - r), (x + 6, y - r - 24)], fill=OUTL, width=6)
        d.ellipse([x + 6, y - r - 30, x + 40, y - r - 12], fill=(90, 180, 80), outline=OUTL, width=4)

def crops_props(frame, d, T, sc):
    lt = T - sc["s"]
    items = [(230, 980, 70, (230, 60, 60)), (420, 920, 60, (255, 160, 40)), (640, 940, 65, (150, 90, 190)),
             (850, 990, 80, (90, 170, 70))]
    for i, (x, y, r, c) in enumerate(items):
        if lt > 0.6 + i * 0.3:
            s = min(ease_back(clamp((lt - 0.6 - i * 0.3) / 0.4)), 1.1)
            fruit(d, x, y, r * s, c, leaf=s > 0.9)
    if lt > 0.5: top_label(frame, "75% OF CROP TYPES", 380, YEL, 82)

def staples_props(frame, d, T, sc):
    lt = T - sc["s"]
    # roti stack
    for k in range(3):
        y = 1210 - k * 22
        d.ellipse([560, y - 40, 820, y + 40], fill=(235, 195, 130), outline=OUTL, width=6)
    for (x, y) in ((640, 1150), (720, 1170), (690, 1135)):
        d.ellipse([x - 12, y - 7, x + 12, y + 7], fill=(170, 110, 60))
    # rice bowl
    d.chord([820, 1060, 1040, 1260], 0, 180, fill=(70, 130, 200), outline=OUTL, width=7)
    d.chord([835, 1090, 1025, 1190], 180, 360, fill=WHITE, outline=OUTL, width=6)
    # wheat stalk
    x0 = 920
    d.line([(x0, 1040), (x0, 850)], fill=(200, 160, 60), width=8)
    for k in range(4):
        y = 870 + k * 40
        for sx in (-1, 1):
            d.ellipse([x0 + sx * 10 - 16, y - 14, x0 + sx * 10 + 16, y + 14], fill=(230, 190, 80), outline=OUTL, width=4)
    if lt > 0.5: top_label(frame, "NO BEES NEEDED", 380, YEL, 96)
    if lt > 2.0: at_label(frame, "ROTI", 690, 1290, WHITE, 52)
    if lt > 2.4: at_label(frame, "CHAWAL", 930, 1290, WHITE, 52)

def drop_props(frame, d, T, sc):
    lt = T - sc["s"]
    g = ease_out(clamp((lt - 1.0) / 2.5))
    base = 1300
    for i, (lab, h, col) in enumerate((("BEFORE", 440, (120, 200, 255)), ("AFTER", 440 * (1 - 0.08 * g), (255, 170, 70)))):
        x = 330 + i * 420
        d.rounded_rectangle([x - 110, base - h, x + 110, base], radius=18, fill=col, outline=OUTL, width=7)
        at_label(frame, lab, x, base + 45, WHITE, 50)
    if lt > 3.4: at_label(frame, "ABOUT 5-8% LESS", 540, 780, WHITE, 64)
    if lt > 0.5: top_label(frame, "ALL CROPS, ALL POLLINATORS", 380, YEL, 64)

def melon_props(frame, d, T, sc):
    lt = T - sc["s"]
    s = min(ease_back(clamp((lt - 0.4) / 0.5)), 1.1)
    x, y, r = 760, 1100, 170 * s
    if r > 2:
        d.ellipse([x - r, y - r * 0.85, x + r, y + r * 0.85], fill=(70, 160, 60), outline=OUTL, width=8)
        for k in (-0.55, 0, 0.55):
            d.arc([x - r * (1 - abs(k) * 0.6), y - r * 0.85, x + r * (1 - abs(k) * 0.6), y + r * 0.85], 260, 280,
                  fill=(30, 100, 40), width=10)
            d.line([(x + k * r, y - r * 0.8), (x + k * r * 1.05, y + r * 0.8)], fill=(30, 100, 40), width=10)
    if lt > 2.0:
        bob = 10 * math.sin(T * 5)
        d.rounded_rectangle([600, 820 + bob, 920, 900 + bob], radius=16, fill=WHITE, outline=OUTL, width=6)
        l = label("PRICE UP!", 50, (230, 50, 40))
        comp(frame, l, 760 - l.width / 2, 860 + bob - l.height / 2)
    if lt > 0.5: top_label(frame, "FRUIT GETS RARE", 380, YEL, 96)

def tree(d, x, y, T, lt):
    d.rectangle([x - 22, y - 10, x + 22, y + 260], fill=(130, 85, 50), outline=OUTL, width=6)
    for (dx, dy, r) in ((0, -120, 170), (-130, -40, 120), (130, -40, 120)):
        d.ellipse([x + dx - r, y + dy - r, x + dx + r, y + dy + r], fill=(110, 185, 90), outline=OUTL, width=6)
    for k in range(9):
        bx = x - 200 + (k * 53) % 400; by = y - 220 + (k * 71) % 240
        c = (255, 230, 120) if lt > 1.0 + k * 0.4 else (255, 190, 210)
        d.ellipse([bx - 16, by - 16, bx + 16, by + 16], fill=c, outline=OUTL, width=3)

def brush_props(frame, d, T, sc):
    lt = T - sc["s"]
    tree(d, 700, 1050, T, lt)
    if lt > 0.5: top_label(frame, "HUMAN POLLINATORS", 380, YEL, 82)

def brush_after(frame, d, T, sc):
    # a brush on a stick tapping the blossoms
    lt = T - sc["s"]
    k = int(clamp((lt - 1.0) / 0.4, 0, 8))
    bx = 700 - 200 + (k * 53) % 400; by = 1050 - 220 + (k * 71) % 240
    tx, ty = bx + 8 * math.sin(T * 14), by + 6 * math.cos(T * 14)
    d.line([(330, 1180), (tx, ty)], fill=(150, 100, 60), width=10)
    d.ellipse([tx - 18, ty - 18, tx + 18, ty + 18], fill=(250, 240, 210), outline=OUTL, width=4)

def choc_props(frame, d, T, sc):
    lt = T - sc["s"]
    # chocolate bar
    x0, y0 = 600, 960
    d.rounded_rectangle([x0, y0, x0 + 340, y0 + 220], radius=14, fill=(120, 70, 40), outline=OUTL, width=8)
    for i in range(3):
        for j in range(2):
            cx, cy = x0 + 20 + i * 105, y0 + 20 + j * 95
            d.rounded_rectangle([cx, cy, cx + 90, cy + 80], radius=8, fill=(140, 85, 50), outline=(90, 50, 30), width=4)
    # a tiny midge zipping around
    mx = 770 + 150 * math.cos(T * 3); my = 880 + 50 * math.sin(T * 6)
    d.ellipse([mx - 6, my - 4, mx + 6, my + 4], fill=OUTL)
    d.ellipse([mx - 10, my - 12, mx, my - 2], fill=(220, 235, 255), outline=OUTL, width=2)
    d.ellipse([mx, my - 12, mx + 10, my - 2], fill=(220, 235, 255), outline=OUTL, width=2)
    if lt > 1.5: at_label(frame, "PINHEAD-SIZED MIDGE", 770, 1260, WHITE, 48)
    if lt > 0.5: top_label(frame, "CHOCOLATE SURVIVES", 380, YEL, 82)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    # a forwarded-message card
    d.rounded_rectangle([140, 850, 940, 1100], radius=30, fill=WHITE, outline=OUTL, width=8)
    for k, line in enumerate(("'No bees? Humans have", "4 years left.'  - Einstein?")):
        if ("q", k) not in _txt:
            _txt[("q", k)] = text_sprite([(line, OUTL)], 50, stroke=0, shadow=False)
        sp = _txt[("q", k)]
        comp(frame, sp, 540 - sp.width / 2, 930 + k * 80 - sp.height / 2)
    if lt > 2.2:
        s = min(ease_back(clamp((lt - 2.2) / 0.35)), 1.15)
        st = label("NO PROOF", int(110 * s) + 1, (235, 50, 40))
        st = st.rotate(-12, expand=True, resample=Image.BICUBIC)
        comp(frame, st, 540 - st.width / 2, 975 - st.height / 2)
    if lt > 3.5: at_label(frame, "FIRST SEEN: 1965", 540, 1160, YEL, 62)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="swarm", s=4.0, e=11.0, bg="day", clock="MIDNIGHT", char="bee", pos=bee_pos, props=swarm_props,
         look=(0, 0.2), narr="There are over 20,000 kinds of BEES. Tonight, every single one VANISHES.",
         n_at=4.2, narr_y=1560, say="Bye-bye, BUZZ!", say_at=6.6, pitch=520),
    dict(id="honey", s=11.0, e=18.0, bg="day", clock="MORNING", char="uncle", pos=(320, 1150, 400),
         props=honey_props, look=(0.6, 0),
         narr="One worker bee makes about 1/12 of a TEASPOON of honey in her whole life.", n_at=11.2,
         narr_y=1560, say="My HONEY is gone!", say_at=14.4, pitch=150),
    dict(id="crops", s=18.0, e=25.0, bg="day", clock="MARKET", char="kid", pos=(540, 1230, 300),
         props=crops_props, look=(0, -0.5),
         narr="About 75% of crop TYPES get help from pollinators like bees.", n_at=18.2, narr_y=1560,
         say="My FRUIT bowl?", say_at=21.2, pitch=440),
    dict(id="staples", s=25.0, e=32.0, bg="day", clock="LUNCH", char="uncle", pos=(270, 1150, 400),
         props=staples_props, look=(0.6, 0.1),
         narr="But WHEAT, RICE and maize don't need bees at all. Roti and chawal are SAFE.", n_at=25.2,
         narr_y=1560, say="Dal-chawal ZINDABAD!", say_at=28.4, pitch=150),
    dict(id="drop", s=32.0, e=39.0, bg="day", clock="THE MATHS", props=drop_props,
         narr="Losing ALL pollinators would cut world crop output by about 5 TO 8%.", n_at=32.2, narr_y=1560),
    dict(id="melon", s=39.0, e=46.0, bg="day", clock="SUMMER", char="kid", pos=(300, 1150, 340),
         props=melon_props, look=(0.6, 0),
         narr="Not a famine. But MELONS, kiwis and many nuts would get rare and pricey.", n_at=39.2,
         narr_y=1560, say="No more TARBOOZ?", say_at=42.4, pitch=440),
    dict(id="brush", s=46.0, e=53.0, bg="day", clock="REAL LIFE", char="uncle", state="hat", pos=(260, 1180, 340),
         props=brush_props, props_after=brush_after, look=(0.6, -0.3),
         narr="In parts of Sichuan, China, people already hand-pollinate apple flowers with BRUSHES.",
         n_at=46.2, narr_y=1560, say="Flower by FLOWER?", say_at=49.4, pitch=150),
    dict(id="choc", s=53.0, e=TW, bg="day", clock="GOOD NEWS", char="kid", pos=(300, 1120, 340),
         props=choc_props, look=(0.6, -0.2),
         narr="CHOCOLATE survives. Cacao flowers are pollinated by tiny MIDGES, not bees.", n_at=53.2,
         narr_y=1560, say="Chocolate is SAFE!", say_at=56.0, pitch=440),
    dict(id="twist", s=TW, e=67.0, bg="twist", clock="PLOT TWIST", char="uncle", pos=(540, 1340, 240),
         props=twist_props, twist=True, look=(0, -0.4),
         narr="Twist: that viral EINSTEIN bee quote? NO PROOF. It first showed up 10 years after he died.",
         n_at=TW + 0.2, narr_y=1560, say="FAKE forward!", say_at=TW + 4.2, pitch=150),
    dict(id="outro", s=67.0, e=72.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = min(ease_back((T - 1.9) / 0.4), 1.2)
        B = int(320 * p) + 2
        spr = bee(B, T, 0, False, (0, 0.2))
        comp(frame, spr, 540 - B / 2, 1390 + 12 * math.sin(T * 2) - B / 2)

cfg = dict(
    total=72.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("EVERY BEE", WHITE)], 140), 770, 0.75, "right"),
        (title([("VANISHED?", YEL)], 150), 920, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("What would ", WHITE), ("YOU", YEL)], 96), 470, 0.15),
                      (title([("miss most?", YEL)], 96), 600, 0.45)],
               row=[("bee", 1), ("kid", 1), ("flower", 1), ("cow", 1), ("uncle", "hat")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=GONE - 0.1, melody=True),
           dict(t0=GONE + 0.6, t1=25.0, minor=True), dict(t0=25.0, t1=46.0, melody=True),
           dict(t0=46.0, t1=TW - 0.15, melody=True), dict(t0=TW + 2.0, t1=72.0, melody=True)],
    drones=[dict(t0=GONE, dur=4.0, g=0.2)],
    fx=[("whoosh", 5.0, 0.3), ("pop", GONE, 0.4), ("pop", GONE + 0.1, 0.35), ("pop", GONE + 0.2, 0.3),
        ("powerdown", GONE + 0.3, 0.25), ("click", 14.0, 0.3), ("pop", 18.8, 0.3), ("pop", 19.1, 0.3),
        ("pop", 19.4, 0.3), ("pop", 19.7, 0.3), ("ding", 27.6, 0.25), ("tick", 33.4, 0.3),
        ("crash", 41.2, 0.15), ("click", 47.4, 0.25), ("click", 48.2, 0.25), ("click", 49.0, 0.25),
        ("ding", 55.0, 0.25), ("crash", TW + 2.3, 0.25)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_every_bee_vanished")
