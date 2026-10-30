#!/usr/bin/env python3
"""What if you could walk through walls? Facts: an atom is almost entirely empty space; the nucleus has a diameter
about 1/100,000 of the atom's (Flinn Scientific). Scaled to a ~150 m cricket ground, that is ~1.5 mm, about a mustard
seed. Solid things push back because electrons repel electrons (standard electromagnetism). Removing the empty space
from all humans leaves roughly a sugar cube of matter weighing billions of tonnes (ScienceABC; check: 8e9 x ~60 kg /
nuclear density 2.3e17 kg/m^3 = ~2 cm^3). Quantum tunnelling: particles can cross barriers they classically could not;
stars need it for fusion at their core temperatures (RevisionDojo/Leicester PST). Flash memory depends on electrons
tunnelling through an oxide layer (Physics Forums; NAND flash). For a whole human the odds are absurdly small,
framed here as a hypothetical. Twist: about 100 trillion neutrinos pass through your body each second (IceCube,
University of Wisconsin); ~100 billion solar neutrinos through a thumbnail each second (Fermilab)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 53.0
BRICK = (196, 92, 70)

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=68):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

def mini(frame, kind, x, y, size, T, state=1, look=(0, 0.2), talk=0.0):
    size = max(2, int(size))
    spr = draw_char(kind, size, T, talk, False, look, state)
    comp(frame, spr, x - size / 2, y - size / 2)

def wall(d, x0, x1, y0=860, y1=1380, ghost=False):
    d.rectangle([x0, y0, x1, y1], fill=(170, 80, 64), outline=OUTL, width=8)
    bh, bw = 52, 120
    for r, y in enumerate(range(y0 + 4, y1 - 4, bh)):
        off = 0 if r % 2 == 0 else bw // 2
        for x in range(x0 - off, x1, bw):
            a, b = max(x + 4, x0 + 4), min(x + bw - 4, x1 - 4)
            if b > a:
                d.rectangle([a, y + 4, b, min(y + bh - 4, y1 - 4)], fill=BRICK if not ghost else (210, 150, 140))

def stars(d, cx, cy, T, n=4, r=90):
    for k in range(n):
        a = T * 4 + k * 2 * math.pi / n
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r * 0.4
        pts = []
        for j in range(10):
            rr = 22 if j % 2 == 0 else 9
            aa = j * math.pi / 5 - math.pi / 2
            pts.append((x + math.cos(aa) * rr, y + math.sin(aa) * rr))
        d.polygon(pts, fill=(255, 220, 60), outline=OUTL)

def atom(d, cx, cy, R, T, nuc=10):
    for k in range(3):
        ang = k * math.pi / 3
        box = [cx - R, cy - R * 0.36, cx + R, cy + R * 0.36]
        # rotated ellipse as a polyline
        pts = []
        for j in range(61):
            t = j / 60 * 2 * math.pi
            x, y = R * math.cos(t), R * 0.36 * math.sin(t)
            pts.append((cx + x * math.cos(ang) - y * math.sin(ang), cy + x * math.sin(ang) + y * math.cos(ang)))
        d.line(pts, fill=(140, 200, 255), width=5)
        t = T * 2.5 + k * 2.1
        x, y = R * math.cos(t), R * 0.36 * math.sin(t)
        ex, ey = cx + x * math.cos(ang) - y * math.sin(ang), cy + x * math.sin(ang) + y * math.cos(ang)
        d.ellipse([ex - 16, ey - 16, ex + 16, ey + 16], fill=(90, 170, 255), outline=OUTL, width=4)
    d.ellipse([cx - nuc, cy - nuc, cx + nuc, cy + nuc], fill=(240, 70, 70), outline=OUTL, width=3)

# ---------------------------------------------------------------- props
def empty_props(frame, d, T, sc):
    lt = T - sc["s"]
    wall(d, 700, 1080)
    if lt > 1.0:
        q = ease_back(clamp((lt - 1.0) / 0.5))
        d.ellipse([760 - 150 * q, 1080 - 150 * q, 760 + 150 * q, 1080 + 150 * q], fill=(20, 24, 50), outline=OUTL,
                  width=8)
        if q > 0.5: atom(d, 760, 1080, 120 * q, T, nuc=6)
    if lt > 0.5:
        top_label(frame, "ATOMS = EMPTY?", 380, YEL, 84)

def stadium_props(frame, d, T, sc):
    lt = T - sc["s"]
    # a big oval ground with a pitch and a zoom circle on its centre
    d.ellipse([60, 820, 1020, 1330], fill=(70, 160, 80), outline=WHITE, width=10)
    d.ellipse([200, 900, 880, 1250], outline=(120, 200, 120), width=6)
    d.rectangle([515, 1000, 565, 1150], fill=(214, 190, 140))
    if lt > 1.5:
        q = ease_back(clamp((lt - 1.5) / 0.5))
        d.ellipse([540 - 5, 1075 - 5, 540 + 5, 1075 + 5], fill=(230, 180, 40), outline=OUTL)
        d.line([(548, 1068), (720, 960)], fill=WHITE, width=5)
        r = 90 * q
        d.ellipse([780 - r, 900 - r, 780 + r, 900 + r], fill=WHITE, outline=OUTL, width=6)
        s = 28 * q
        d.ellipse([780 - s, 900 - s, 780 + s, 900 + s], fill=(230, 180, 40), outline=OUTL, width=4)
    if lt > 0.5:
        top_label(frame, "NUCLEUS = MUSTARD SEED", 380, YEL, 70)

def bonk_props(frame, d, T, sc):
    lt = T - sc["s"]
    wall(d, 700, 1080)
    if lt > 1.2:
        for k in range(3):
            y = 960 + k * 110
            for x0, sgn in ((630, -1), (760, 1)):
                d.ellipse([x0 - 22, y - 22, x0 + 22, y + 22], fill=(90, 170, 255), outline=OUTL, width=4)
                d.text((x0 - 12, y - 30), "-", font=E.font(46), fill=WHITE)
        stars(d, 470, 860, T)
    if lt > 0.5:
        top_label(frame, "ELECTRONS PUSH BACK", 380, YEL, 72)

def cube_props(frame, d, T, sc):
    lt = T - sc["s"]
    # crowd of tiny heads collapsing into one sugar cube
    p = ease_out(clamp((lt - 1.2) / 1.6))
    rng = np.random.default_rng(3)
    for i in range(28):
        x0, y0 = rng.uniform(560, 1020), rng.uniform(860, 1300)
        x = x0 + (790 - x0) * p; y = y0 + (1100 - y0) * p
        r = 26 * (1 - p)
        if r > 2:
            d.ellipse([x - r, y - r, x + r, y + r], fill=(240, 190, 150), outline=OUTL, width=3)
    if p > 0.85:
        s = 70
        d.polygon([(790 - s, 1100 - s * 0.6), (790, 1100 - s), (790 + s, 1100 - s * 0.6), (790, 1100 - s * 0.2)],
                  fill=WHITE, outline=OUTL)
        d.polygon([(790 - s, 1100 - s * 0.6), (790, 1100 - s * 0.2), (790, 1100 + s * 0.8), (790 - s, 1100 + s * 0.4)],
                  fill=(230, 230, 240), outline=OUTL)
        d.polygon([(790 + s, 1100 - s * 0.6), (790, 1100 - s * 0.2), (790, 1100 + s * 0.8), (790 + s, 1100 + s * 0.4)],
                  fill=(205, 205, 220), outline=OUTL)
        l = label("BILLIONS OF TONNES", 46, WHITE); comp(frame, l, 790 - l.width / 2, 1230)
    if lt > 0.5:
        top_label(frame, "8 BILLION HUMANS", 380, YEL, 80)

def tunnel_props(frame, d, T, sc):
    lt = T - sc["s"]
    # a barrier with a little ball slipping through
    d.rectangle([690, 860, 770, 1320], fill=(150, 150, 180), outline=OUTL, width=6)
    ph = (lt * 0.5) % 1.0
    x = 600 + ph * 340
    y = 1100 - 60 * abs(math.sin(ph * math.pi * 3)) if x < 700 else 1100
    a = 0.4 if 690 < x < 770 else 1.0
    col = (90, 170, 255) if a == 1.0 else (180, 210, 255)
    d.ellipse([x - 38, y - 38, x + 38, y + 38], fill=col, outline=OUTL, width=5)
    if lt > 0.5:
        top_label(frame, "QUANTUM TUNNELLING", 380, YEL, 76)

def phone(d, cx, cy, s=1.0, T=0.0):
    d.rounded_rectangle([cx - 110 * s, cy - 200 * s, cx + 110 * s, cy + 200 * s], radius=30 * s, fill=(40, 40, 50),
                        outline=OUTL, width=6)
    d.rounded_rectangle([cx - 94 * s, cy - 176 * s, cx + 94 * s, cy + 170 * s], radius=16 * s, fill=(170, 220, 255))
    for i in range(3):
        for j in range(4):
            x = cx - 80 * s + i * 56 * s; y = cy - 160 * s + j * 80 * s
            on = ((i + j + int(T * 3)) % 3) != 0
            d.rounded_rectangle([x, y, x + 48 * s, y + 68 * s], radius=6, fill=(255, 200, 120) if on else (250, 250, 255))

def phone_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_back(clamp((lt - 0.3) / 0.5))
    phone(d, 790, 1080 + 400 * (1 - p), 1.0, T)
    if lt > 0.5:
        top_label(frame, "YOUR PHONE DOES IT", 380, YEL, 74)

def odds_props(frame, d, T, sc):
    lt = T - sc["s"]
    wall(d, 700, 1080)
    stars(d, 470, 860, T, n=3)
    if lt > 0.5:
        n = int(10 ** min(9.0, 1 + lt * 2.2))
        top_label(frame, f"BONK #{n:,}", 380, YEL, 80)

def neutrino_wall(frame, d, T, sc):
    wall(d, 0, 260)

def neutrino_props(frame, d, T, sc):
    lt = T - sc["s"]
    rng = np.random.default_rng(7)
    for i in range(40):
        y = rng.uniform(860, 1360)
        sp = rng.uniform(500, 900)
        x = (rng.uniform(0, W) + T * sp) % (W + 100) - 50
        d.line([(x - 50, y), (x, y)], fill=(255, 255, 160), width=3)
        d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(255, 250, 120))
    if lt > 0.5:
        n = int(100 * clamp((lt - 0.5) / 2.0))
        top_label(frame, f"{n} TRILLION / SEC", 380, YEL, 80)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="empty", s=4.0, e=11.0, bg="office", clock="THE DREAM", char="uncle", pos=(330, 1100, 420),
         props=empty_props, look=(0.6, 0),
         narr="Good news: every ATOM in that wall is almost entirely EMPTY space.", n_at=4.2, narr_y=1560,
         say="So walls are... NOTHING?", say_at=7.4, pitch=150),
    dict(id="stadium", s=11.0, e=18.0, bg="stadium", clock="ATOM SIZED STADIUM", props=stadium_props,
         narr="If an atom were a cricket STADIUM, its nucleus would be a MUSTARD SEED.", n_at=11.2,
         narr_y=1560),
    dict(id="bonk", s=18.0, e=25.0, bg="office", clock="ATTEMPT #1", char="uncle", state="angry",
         pos=(470, 1090, 420), props=bonk_props, look=(0.6, 0.1),
         narr="So why the BONK? Electrons in you PUSH AWAY electrons in the wall.", n_at=18.2, narr_y=1560,
         say="OUCH! Physics!", say_at=21.8, pitch=150),
    dict(id="cube", s=25.0, e=32.0, bg="space", clock="SQUEEZE EVERYONE", char="kid", pos=(290, 1110, 380),
         props=cube_props, look=(0.6, 0.1),
         narr="Squeeze the empty space out of ALL humans: about one SUGAR CUBE.", n_at=25.2, narr_y=1560,
         say="Very HEAVY sugar!", say_at=28.6, pitch=480),
    dict(id="tunnel", s=32.0, e=39.0, bg="space", clock="THE LOOPHOLE", char="sun", pos=(300, 1080, 420),
         props=tunnel_props, look=(0.6, 0.1),
         narr="Tiny particles really CAN slip through barriers. The Sun needs it to SHINE.", n_at=32.2,
         narr_y=1560, say="I do it all DAY!", say_at=35.6, pitch=260),
    dict(id="phone", s=39.0, e=46.0, bg="bedroom", clock="IN YOUR POCKET", char="kid", pos=(300, 1110, 380),
         props=phone_props, look=(0.6, 0),
         narr="Your phone's memory uses tunnelling ELECTRONS to save your photos.", n_at=39.2, narr_y=1560,
         say="My selfies are QUANTUM?", say_at=42.4, pitch=480),
    dict(id="odds", s=46.0, e=TW, bg="office", clock="WHOLE HUMAN?", char="uncle", state="angry",
         pos=(470, 1090, 420), props=odds_props, look=(0.6, 0.1),
         narr="A whole human? Odds so tiny you'd bonk for longer than the UNIVERSE has existed.", n_at=46.2,
         narr_y=1560, say="Still... TRYING!", say_at=49.8, pitch=150),
    dict(id="twist", s=TW, e=60.0, bg="living", clock="PLOT TWIST", char="kid", pos=(640, 1100, 400),
         props=neutrino_wall, props_after=neutrino_props, twist=True, look=(-0.4, 0.1),
         narr="Twist: about 100 TRILLION neutrinos pass through YOUR body every second.", n_at=TW + 0.2,
         narr_y=1560, say="Wait, THEY can do it?!", say_at=TW + 3.4, pitch=480),
    dict(id="outro", s=60.0, e=65.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = min(ease_back((T - 1.9) / 0.4), 1.2)
        d.rectangle([640, 1260, 640 + 300 * p, 1620], fill=(170, 80, 64), outline=OUTL, width=6)
    if T >= 2.3:
        x = 300 + 260 * clamp((T - 2.3) / 1.4)
        mini(frame, "uncle", x, 1420, 300, T, look=(0.6, 0))

cfg = dict(
    total=65.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU COULD WALK", WHITE)], 112), 770, 0.75, "right"),
        (title([("THROUGH WALLS?", YEL)], 124), 905, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Which wall would ", WHITE)], 92), 470, 0.15),
                      (title([("YOU", YEL), (" walk through?", WHITE)], 92), 590, 0.45)],
               row=[("uncle", "angry"), ("kid", 1), ("sun", 1), ("kid", 1), ("uncle", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0), dict(t0=18.0, t1=32.0, melody=True),
           dict(t0=32.0, t1=46.0), dict(t0=46.0, t1=TW - 0.15, minor=True),
           dict(t0=TW + 2.0, t1=65.0, melody=True)],
    fx=[("pop", 1.95, 0.4), ("pop", 5.1, 0.3), ("ding", 13.0, 0.3), ("crash", 19.1, 0.3), ("boom", 19.15, 0.25),
        ("whoosh", 26.4, 0.3), ("pop", 28.0, 0.4), ("whoosh", 33.0, 0.25), ("whoosh", 35.0, 0.25),
        ("click", 40.0, 0.3), ("click", 40.4, 0.3), ("crash", 47.0, 0.25), ("crash", 48.4, 0.25),
        ("crash", 49.6, 0.25), ("whoosh", TW + 1.0, 0.3), ("whoosh", TW + 2.0, 0.3)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_could_walk_through_walls")
