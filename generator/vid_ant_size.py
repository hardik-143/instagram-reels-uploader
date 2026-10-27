#!/usr/bin/env python3
"""What if you shrank to the size of an ant? Terminal velocity of a small/medium ant ~6.4 km/h; 'sufficiently small
animals cannot be hurt in a fall from any height' (M. LaBarbera, via Globe and Mail; Haldane 1926 mouse/mine shaft).
Raindrops can weigh ~50x a mosquito and mosquitoes survive the hits (Dickerson & Hu, PNAS 2012, Georgia Tech).
Haldane: 'An insect going for a drink is in as great danger as a man leaning out over a precipice' (surface tension).
Many ants carry 10-50x their body weight (Terminix; leaf-cutters >50x). ~20 quadrillion ants, ~12 Mt dry carbon, more
than all wild birds and mammals combined (Schultheiss et al., PNAS 2022 / UWA). 20e15 / 8e9 = 2.5 million per human.
Twist: Similipal kai chutney (red weaver ant, Mayurbhanj, Odisha) got a GI tag on 2 Jan 2024 (Down To Earth)."""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, comp, paste_c, ease_back, ease_out, clamp, text_sprite

TW = 53.0

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=68):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

# ---------------------------------------------------------------- new character: a red weaver ant
BODY, SHADE, LEG = (214, 92, 40), (176, 66, 30), (90, 40, 24)

def ant(B, T, talk=0.0, blink=False, look=(0, 0), state=1):
    S = 2 * B
    L = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    u = S / 200.0
    lw = lambda w: max(1, int(round(w * u)))
    def EL(b, fill, w=2.6):
        d.ellipse([v * u for v in b], fill=fill, outline=OUTL if w else None, width=lw(w) if w else 0)
    def LN(pts, w=3.0, fill=LEG):
        d.line([(x * u, y * u) for x, y in pts], fill=fill, width=lw(w), joint="curve")
    # 6 legs from the thorax, walking
    for i, x in enumerate((84, 100, 116)):
        k = 6 * math.sin(T * 10 + i * 2.1)
        LN([(x, 122), (x - 26 + k, 140), (x - 34 + k, 176)], 3.4)
        LN([(x, 122), (x + 26 - k, 140), (x + 34 - k, 176)], 3.4)
    # abdomen (back right), thorax, head (front left)
    EL((112, 92, 192, 156), SHADE)
    d.arc([126 * u, 98 * u, 178 * u, 150 * u], 250, 290, fill=BODY, width=lw(3))
    EL((76, 104, 124, 140), BODY)
    # antennae
    a = 4 * math.sin(T * 6)
    LN([(48, 66), (40, 34 + a), (22, 20 + a)], 3.0, OUTL)
    LN([(72, 62), (82, 30 - a), (100, 18 - a)], 3.0, OUTL)
    EL((8, 50, 112, 140), BODY)
    # face
    for i, x in enumerate((44, 76)):
        r = 12
        if blink or (state == "wink" and i == 1):
            d.arc([(x - r) * u, (86 - r * 0.7) * u, (x + r) * u, (86 + r * 0.7) * u], 200, 340, fill=OUTL, width=lw(3))
            continue
        EL((x - r, 86 - r * 1.1, x + r, 86 + r * 1.1), WHITE, w=2.2)
        px, py = x + look[0] * 5, 86 + look[1] * 5
        EL((px - 6, py - 7, px + 6, py + 7), (25, 20, 30), w=0)
        EL((px - 5, py - 6, px - 1, py - 2), WHITE, w=0)
    EL((22, 104, 36, 112), (255, 150, 140), w=0); EL((84, 104, 98, 112), (255, 150, 140), w=0)
    # mandibles + mouth
    LN([(48, 124), (54, 134), (60, 128)], 2.6, OUTL); LN([(72, 124), (66, 134), (60, 128)], 2.6, OUTL)
    if talk > 0.08:
        o = 3 + 10 * talk
        EL((52, 110, 68, 112 + o), (125, 28, 48), w=2.0)
    else:
        d.arc([50 * u, 104 * u, 70 * u, 118 * u], 20, 160, fill=OUTL, width=lw(2.6))
    return L.reduce(2)

_draw_orig = E.draw_char
def draw_char(kind, B, T, talk=0.0, blink=False, look=(0, 0), state=1):
    if kind == "ant":
        return ant(B, T, talk, blink, look, state)
    return _draw_orig(kind, B, T, talk, blink, look, state)
E.draw_char = draw_char

def mini(frame, kind, x, y, size, T, state=1, look=(0, 0.2), rot=0):
    spr = draw_char(kind, size, T, 0, False, look, state)
    if rot: spr = spr.rotate(rot, resample=Image.BICUBIC, expand=False)
    comp(frame, spr, x - size / 2, y - size / 2)

# ---------------------------------------------------------------- props
def floor(d, y0=1300, col=(196, 150, 104)):
    d.rectangle([0, y0, W, H], fill=col)
    for x in range(-40, W, 160):
        d.line([(x, y0), (x + 120, H)], fill=(176, 132, 90), width=6)

def shrink_pos(T):
    lt = T - 4.0
    s = 520 - 450 * ease_out(clamp((lt - 1.0) / 1.6))
    s = int(s)
    return (420, 1300 - s * 0.45, s)

def shrink_props(frame, d, T, sc):
    floor(d)
    lt = T - sc["s"]
    # a giant sandal appears beside you once you shrink
    q = ease_out(clamp((lt - 2.0) / 1.0))
    if q > 0:
        x0 = 600 + 400 * (1 - q)
        d.rounded_rectangle([x0, 1050, x0 + 520, 1290], radius=110, fill=(70, 110, 200), outline=OUTL, width=8)
        d.rounded_rectangle([x0 + 40, 1230, x0 + 500, 1300], radius=30, fill=(240, 220, 170), outline=OUTL, width=6)
        d.line([(x0 + 120, 1060), (x0 + 260, 1200), (x0 + 400, 1060)], fill=OUTL, width=10)
    if lt > 2.6:
        top_label(frame, "5 MM TALL", 380, YEL, 80)

def fall_pos(T):
    lt = T - 11.0
    return (560 + 40 * math.sin(lt * 2.2), 600 + 95 * lt, 150)

def fall_props(frame, d, T, sc):
    lt = T - sc["s"]
    # a tall tower on the left
    d.rectangle([40, 300, 300, H], fill=(150, 160, 190), outline=OUTL, width=6)
    for yy in range(340, H, 90):
        for xx in (80, 170):
            d.rectangle([xx, yy, xx + 60, yy + 50], fill=(220, 230, 250))
    d.rectangle([0, 1690, W, H], fill=(110, 170, 90))
    # little parachute arms lines
    if lt > 0.5:
        top_label(frame, "TOP SPEED: 6 KM/H", 380, YEL, 66)

def rain_props(frame, d, T, sc):
    lt = T - sc["s"]
    for k in range(9):
        x = (k * 131 + 40) % 1080
        y = ((lt * 700 + k * 230) % 1500) + 300
        r = 34 + (k % 3) * 10
        d.ellipse([x - r, y - r * 1.1, x + r, y + r], fill=(150, 200, 250), outline=OUTL, width=5)
        d.ellipse([x - r * 0.5, y - r * 0.7, x - r * 0.1, y - r * 0.3], fill=WHITE)
    if lt > 0.5:
        top_label(frame, "DROP = 50x A MOSQUITO", 380, YEL, 60)

def drop_props(frame, d, T, sc):
    floor(d, 1320, (230, 222, 206))
    lt = T - sc["s"]
    # tiny you stuck inside a giant water drop
    wob = 10 * math.sin(T * 4)
    mini(frame, "kid", 540, 1130, 230, T, look=(0.3, -0.4), rot=8 * math.sin(T * 3))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.ellipse([330 - wob, 930 + wob, 750 + wob, 1330], fill=(110, 180, 250, 120), outline=(30, 90, 170, 255), width=8)
    od.ellipse([400, 980, 470, 1040], fill=(255, 255, 255, 200))
    frame.alpha_composite(ov)
    if lt > 0.5:
        top_label(frame, "WATER = GLUE", 380, YEL, 80)

def lift_props(frame, d, T, sc):
    floor(d, 1330, (110, 170, 90))
    lt = T - sc["s"]
    # ant holds a big sugar cube overhead, bobbing
    b = 12 * math.sin(T * 5)
    x0, y0 = 380, 885 + b
    d.rectangle([x0, y0, x0 + 280, y0 + 170], fill=WHITE, outline=OUTL, width=8)
    for k in range(5):
        d.ellipse([x0 + 30 + k * 50, y0 + 40 + (k % 3) * 40, x0 + 46 + k * 50, y0 + 56 + (k % 3) * 40],
                  fill=(220, 220, 230))
    if lt > 0.5:
        top_label(frame, "10-50x BODY WEIGHT", 380, YEL, 66)

def crowd_props(frame, d, T, sc):
    floor(d, 1250, (196, 150, 104))
    lt = T - sc["s"]
    n = int(clamp(lt / 3.0) * 18)
    for k in range(n):
        x = (k * 167 + 60 * math.sin(T + k)) % 1140 - 30
        y = 1260 + (k % 3) * 55
        mini(frame, "ant", x, y, 120, T + k * 0.3)
    if lt > 0.5:
        top_label(frame, "20,000,000,000,000,000", 380, YEL, 62)
    if lt > 2.8:
        top_label(frame, "2.5 MILLION PER HUMAN", 470, WHITE, 56)

def scale_props(frame, d, T, sc):
    lt = T - sc["s"]
    tilt = 70 * ease_out(clamp((lt - 1.2) / 1.2))
    cx, cy = 540, 930
    d.polygon([(cx - 60, 1500), (cx + 60, 1500), (cx, cy)], fill=(120, 100, 80), outline=OUTL)
    lx, ly, rx, ry = cx - 330, cy + tilt, cx + 330, cy - tilt
    d.line([(lx, ly), (rx, ry)], fill=OUTL, width=16)
    for px, py in ((lx, ly), (rx, ry)):
        d.line([(px, py), (px - 120, py + 160)], fill=OUTL, width=5)
        d.line([(px, py), (px + 120, py + 160)], fill=OUTL, width=5)
        d.chord([px - 160, py + 100, px + 160, py + 220], 0, 180, fill=(220, 200, 120), outline=OUTL, width=6)
    # left pan: a heap of ants (heavier, goes down); right pan: wild animals
    for k in range(7):
        mini(frame, "ant", lx - 110 + (k % 4) * 70, ly + 120 - (k // 4) * 50, 110, T + k)
    mini(frame, "whale", rx - 50, ry + 110, 170, T)
    mini(frame, "pigeon", rx + 80, ry + 110, 120, T)
    if lt > 0.5:
        l = label("ANTS", 60, YEL); comp(frame, l, lx - l.width / 2, ly + 230)
    if lt > 1.0:
        top_label(frame, "VS WILD BIRDS + MAMMALS", 420, WHITE, 52)

def chutney_props(frame, d, T, sc):
    lt = T - sc["s"]
    d.rectangle([0, 1250, W, H], fill=(170, 110, 70))
    # stone bowl of red chutney
    d.chord([120, 1080, 520, 1360], 0, 180, fill=(120, 120, 130), outline=OUTL, width=8)
    d.ellipse([120, 1160, 520, 1260], fill=(196, 60, 40), outline=OUTL, width=8)
    for k in range(5):
        d.ellipse([180 + k * 60, 1190 + (k % 2) * 20, 200 + k * 60, 1206 + (k % 2) * 20], fill=(250, 120, 60))
    # one worried ant running away
    mini(frame, "ant", 300 - 140 * clamp((lt - 2.0) / 3.0), 1060, 150, T, look=(-0.6, -0.2))
    if lt > 0.5:
        top_label(frame, "KAI CHUTNEY · ODISHA", 380, YEL, 62)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="shrink", s=4.0, e=11.0, bg="living", clock="SHRINKING...", char="kid", pos=shrink_pos,
         props=shrink_props, look=(0.5, -0.5),
         narr="You shrink to about 5 MM tall, the size of a big ANT.", n_at=4.2, narr_y=1500,
         say="Why is my CHAPPAL a building?!", say_at=7.4, pitch=420),
    dict(id="fall", s=11.0, e=18.0, bg="speed", clock="FALL TEST", char="kid", pos=fall_pos,
         props=fall_props, look=(0, 0.6), rot=lambda T: 12 * math.sin(T * 2),
         narr="Fall off a tower? A falling ant tops out near 6 KM/H. You'd walk AWAY.", n_at=11.2, narr_y=1500,
         say="Wheee... very SLOWLY!", say_at=13.6, pitch=420),
    dict(id="rain", s=18.0, e=25.0, bg="storm", clock="MONSOON", char="mosquito", pos=(540, 1100, 420),
         props=rain_props, look=(0, -0.5),
         narr="Raindrops become BOULDERS. Mosquitoes take hits 50 TIMES their weight and SURVIVE.", n_at=18.2,
         narr_y=1500, say="Just go with the FLOW!", say_at=21.4, pitch=520),
    dict(id="drop", s=25.0, e=32.0, bg="office", clock="REAL DANGER", props=drop_props,
         narr="The real danger is WATER. At ant size, one drop can grab you like GLUE.", n_at=25.2, narr_y=1500),
    dict(id="lift", s=32.0, e=39.0, bg="day", clock="SUPER STRENGTH", char="ant", pos=(540, 1180, 420),
         props=lift_props, look=(0.3, -0.6),
         narr="Your new neighbours: many ANTS carry 10 to 50 TIMES their own weight.", n_at=32.2, narr_y=1500,
         say="Leg day, EVERY day!", say_at=35.2, pitch=480),
    dict(id="crowd", s=39.0, e=46.0, bg="day", clock="HEADCOUNT", char="ant", pos=(540, 1010, 300),
         props=crowd_props, look=(0, 0.2),
         narr="And you'd have company: about 20 QUADRILLION ants live on Earth.", n_at=39.2, narr_y=1580,
         say="We're EVERYWHERE!", say_at=42.4, pitch=500),
    dict(id="scale", s=46.0, e=53.0, bg="day", clock="WEIGH-IN", props=scale_props,
         narr="Together, all ants OUTWEIGH every wild BIRD and MAMMAL on Earth combined.", n_at=46.2,
         narr_y=1600),
    dict(id="twist", s=TW, e=60.0, bg="sweetshop", clock="PLOT TWIST", char="uncle", pos=(760, 1080, 400),
         props=chutney_props, twist=True, look=(-0.6, 0.2),
         narr="Twist: in Odisha, red weaver ants become KAI CHUTNEY, with its own GI TAG.", n_at=TW + 0.2,
         narr_y=1500, say="Stay off my PLATE, tiny!", say_at=TW + 3.4, pitch=150),
    dict(id="outro", s=60.0, e=65.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        x = 540 + 40 * math.sin(T * 2); y = 1420 + 8 * math.sin(T * 6)
        paste_c(frame, ant(380, T, 0, False, (0, 0.2)), x, y, ease_back((T - 1.9) / 0.4))

cfg = dict(
    total=65.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU SHRANK TO", WHITE)], 120), 770, 0.75, "right"),
        (title([("ANT SIZE?", YEL)], 150), 915, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" shrink", WHITE)], 100), 470, 0.15),
                      (title([("for one day?", YEL)], 96), 600, 0.45)],
               row=[("ant", 1), ("mosquito", 1), ("kid", 1), ("uncle", 1), ("ant", "wink")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0), dict(t0=18.0, t1=25.0, minor=True),
           dict(t0=25.0, t1=32.0, drums=False, minor=True), dict(t0=32.0, t1=46.0, melody=True),
           dict(t0=46.0, t1=TW - 0.15, drums=False, melody=True), dict(t0=TW + 2.0, t1=65.0, melody=True)],
    fx=[("whoosh", 5.2, 0.5), ("whoosh", 5.8, 0.4), ("wind", 11.2, 0.35, dict(dd=6.0)),
        ("gale", 18.2, 0.3, dict(dd=6.5)), ("splash", 19.5, 0.4), ("splash", 21.0, 0.35),
        ("bubbles", 25.3, 0.3, dict(dd=6.0)), ("pop", 33.0, 0.4), ("pop", 40.0, 0.3), ("pop", 40.6, 0.3),
        ("pop", 41.2, 0.3), ("click", 47.4, 0.5), ("crash", 47.6, 0.3)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_shrank_to_ant_size")
