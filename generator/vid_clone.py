#!/usr/bin/env python3
"""What if you could clone yourself? Facts: a clone shares the donor's DNA but is born as a baby and ages normally.
Dolly the sheep, born 5 July 1996 at the Roslin Institute, first mammal cloned from an adult (mammary) cell, the only
live lamb from 277 attempts (University of Edinburgh 'Our History'). Memories are not stored in DNA. Identical twins
share almost all DNA, yet fingerprints differ (womb environment, Live Science). NDRI Karnal cloned buffalo calf
Garima, born 6 June 2009, with the hand-guided cloning technique (ICAR). India's 2017 National Guidelines for Stem Cell
Research prohibit research related to reproductive cloning (Nature India). Twist: CC, the first cloned cat (born 22 Dec
2001, Texas A&M), was genetically identical to donor Rainbow but had a different coat pattern (Texas A&M CVMBS)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 53.0

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=68):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

def mini(frame, kind, x, y, size, T, state=1, look=(0, 0.2), talk=0.0, alpha=None):
    size = max(2, int(size))
    spr = draw_char(kind, size, T, talk, False, look, state)
    if alpha is not None:
        a = spr.getchannel("A").point(lambda v: int(v * alpha)); spr.putalpha(a)
    comp(frame, spr, x - size / 2, y - size / 2)

# ---------------------------------------------------------------- props
def copy_props(frame, d, T, sc):
    lt = T - sc["s"]
    # a dreamy, see-through second uncle on the right
    a = 0.35 + 0.15 * math.sin(T * 4)
    if lt > 1.0:
        mini(frame, "uncle", 760, 1130 + 10 * math.sin(T * 3), 400, T, alpha=a, look=(-0.5, 0.1))
        d.text((900, 860), "?", font=E.font(120), fill=WHITE, stroke_width=8, stroke_fill=OUTL)
    if lt > 0.5:
        top_label(frame, "SAME DNA", 380, YEL, 84)

def crib_props(frame, d, T, sc):
    lt = T - sc["s"]
    # crib behind the baby
    d.rounded_rectangle([290, 1150, 790, 1360], radius=20, fill=(250, 220, 170), outline=OUTL, width=8)
    for x in range(320, 780, 50):
        d.line([(x, 1000), (x, 1160)], fill=(210, 170, 120), width=12)
    d.rounded_rectangle([280, 980, 800, 1010], radius=12, fill=(210, 170, 120), outline=OUTL, width=6)
    if lt > 0.5:
        top_label(frame, "AGE: 0", 380, YEL, 90)

def crib_after(frame, d, T, sc):
    d.rounded_rectangle([290, 1250, 790, 1360], radius=20, fill=(250, 220, 170), outline=OUTL, width=8)

def sheep(d, cx, cy, s, T, talk=0.0):
    """A fluffy cartoon sheep, facing left."""
    bob = 6 * math.sin(T * 3)
    cy = cy + bob
    for dx in (-90, 50):
        d.rounded_rectangle([cx + dx * s, cy + 60 * s, cx + (dx + 34) * s, cy + 170 * s], radius=12 * s,
                            fill=(60, 50, 60), outline=OUTL, width=5)
    for dx, dy, r in ((-110, 0, 80), (-40, -40, 90), (40, -40, 90), (110, 0, 80), (0, 30, 100), (-70, 50, 70),
                      (70, 50, 70)):
        d.ellipse([cx + (dx - r) * s - 5, cy + (dy - r) * s - 5, cx + (dx + r) * s + 5, cy + (dy + r) * s + 5],
                  fill=OUTL)
    for dx, dy, r in ((-110, 0, 80), (-40, -40, 90), (40, -40, 90), (110, 0, 80), (0, 30, 100), (-70, 50, 70),
                      (70, 50, 70)):
        d.ellipse([cx + (dx - r) * s, cy + (dy - r) * s, cx + (dx + r) * s, cy + (dy + r) * s], fill=(250, 248, 240))
    hx, hy = cx - 190 * s, cy - 40 * s
    d.ellipse([hx - 70 * s, hy - 85 * s, hx + 70 * s, hy + 85 * s], fill=(70, 60, 70), outline=OUTL, width=6)
    d.ellipse([hx - 125 * s, hy - 60 * s, hx - 50 * s, hy - 25 * s], fill=(70, 60, 70), outline=OUTL, width=5)
    d.ellipse([hx + 50 * s, hy - 60 * s, hx + 125 * s, hy - 25 * s], fill=(70, 60, 70), outline=OUTL, width=5)
    for ex in (-28, 28):
        d.ellipse([hx + (ex - 18) * s, hy - 30 * s, hx + (ex + 18) * s, hy + 8 * s], fill=WHITE, outline=OUTL, width=4)
        d.ellipse([hx + (ex - 14) * s, hy - 18 * s, hx + (ex + 2) * s, hy + 2 * s], fill=(20, 20, 30))
    o = 10 + 30 * talk
    d.ellipse([hx - 24 * s, hy + 34 * s, hx + 24 * s, hy + (34 + o) * s], fill=(125, 28, 48), outline=OUTL, width=4)
    for dx, dy, r in ((-40, -110, 40), (0, -125, 44), (40, -110, 40)):
        d.ellipse([hx + (dx - r) * s * 0.8, hy + (dy - r) * s * 0.8, hx + (dx + r) * s * 0.8,
                   hy + (dy + r) * s * 0.8], fill=(250, 248, 240), outline=OUTL, width=4)

def dolly_props(frame, d, T, sc):
    lt = T - sc["s"]
    talk = E.talk_amt(sc, T)
    p = ease_back(clamp((lt - 0.2) / 0.5))
    sheep(d, 600, 1200 + 500 * (1 - p), 1.15, T, talk)
    if lt > 0.5:
        n = min(277, int(277 * clamp((lt - 0.5) / 2.5)))
        top_label(frame, f"ATTEMPT #{n}", 380, YEL, 80)

def memory_props(frame, d, T, sc):
    lt = T - sc["s"]
    # thought cloud above-right with a locked password box
    x, y = 780, 980
    for dx, dy, r in ((0, 0, 110), (-90, 30, 70), (90, 30, 70), (0, 70, 80)):
        d.ellipse([x + dx - r - 5, y + dy - r - 5, x + dx + r + 5, y + dy + r + 5], fill=OUTL)
    for dx, dy, r in ((0, 0, 110), (-90, 30, 70), (90, 30, 70), (0, 70, 80)):
        d.ellipse([x + dx - r, y + dy - r, x + dx + r, y + dy + r], fill=WHITE)
    for k, (bx, by, r) in enumerate(((620, 1150, 22), (580, 1200, 14))):
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=WHITE, outline=OUTL, width=4)
    d.rounded_rectangle([x - 130, y - 10, x + 130, y + 60], radius=14, fill=(230, 236, 246), outline=OUTL, width=5)
    stars = "*" * min(6, int(lt * 3))
    d.text((x - 100, y - 18), stars, font=E.font(80), fill=OUTL)
    if lt > 2.2:
        d.text((x - 30, y - 120), "?", font=E.font(110), fill=(230, 40, 50), stroke_width=6, stroke_fill=OUTL)
    if lt > 0.5:
        top_label(frame, "NO MEMORIES COPIED", 380, YEL, 70)

def print_icon(d, cx, cy, r, seed):
    """Fingerprint: loops of concentric arcs, centre offset by seed."""
    d.ellipse([cx - r, cy - r * 1.25, cx + r, cy + r * 1.25], fill=(255, 226, 196), outline=OUTL, width=6)
    ox, oy = (12, -18) if seed == 0 else (-16, 22)
    for k in range(1, 6):
        rr = k * r * 0.16
        a0, a1 = (200, 520) if seed == 0 else (150, 470)
        d.arc([cx + ox - rr, cy + oy - rr * 1.2, cx + ox + rr, cy + oy + rr * 1.2], a0 + k * 12, a1 - k * 8,
              fill=(150, 90, 70), width=6)

def twins_props(frame, d, T, sc):
    lt = T - sc["s"]
    mini(frame, "kid", 300, 1000, 380, T, look=(0.4, 0.2), talk=E.talk_amt(sc, T))
    mini(frame, "kid", 780, 1000, 380, T, look=(-0.4, 0.2))
    if lt > 2.6:
        q = ease_back(clamp((lt - 2.6) / 0.4))
        print_icon(d, 300, 1250, 60 * q, 0)
        print_icon(d, 780, 1250, 60 * q, 1)
        d.text((490, 1200), "=/=", font=E.font(70), fill=WHITE, stroke_width=7, stroke_fill=OUTL)
    if lt > 0.5:
        top_label(frame, "IDENTICAL TWINS", 380, YEL, 76)

def lab_props(frame, d, T, sc):
    lt = T - sc["s"]
    # lab bench with a test tube on the left
    d.rectangle([0, 1300, W, 1380], fill=(150, 160, 180), outline=OUTL, width=6)
    d.rounded_rectangle([90, 1060, 150, 1300], radius=28, fill=(220, 240, 255), outline=OUTL, width=6)
    d.rounded_rectangle([96, 1180, 144, 1294], radius=22, fill=(120, 220, 160))
    if lt > 0.5:
        top_label(frame, "MADE IN KARNAL", 380, YEL, 76)

def law_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 1.0:
        q = ease_back(clamp((lt - 1.0) / 0.4))
        cx, cy, r = 820, 1000, 120 * q
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE, outline=(220, 30, 40), width=max(1, int(22 * q)))
        if q > 0.3:
            mini(frame, "uncle", cx, cy + 10, 170 * q, T, look=(-0.3, 0))
        d.line([(cx - r * 0.7, cy - r * 0.7), (cx + r * 0.7, cy + r * 0.7)], fill=(220, 30, 40),
               width=max(1, int(22 * q)))
    if lt > 0.5:
        top_label(frame, "NOT ALLOWED", 380, YEL, 84)

def cc_props(frame, d, T, sc):
    lt = T - sc["s"]
    # framed photo of the donor cat with calico patches
    fx, fy = 270, 1000
    d.rounded_rectangle([fx - 170, fy - 190, fx + 170, fy + 190], radius=16, fill=(140, 90, 50), outline=OUTL, width=8)
    d.rectangle([fx - 140, fy - 160, fx + 140, fy + 160], fill=(255, 240, 210))
    mini(frame, "cat", fx, fy + 20, 260, T, look=(0.2, 0.2))
    for px, py, r, c in ((-60, -30, 34, (230, 130, 40)), (50, -50, 30, (60, 50, 50)), (-20, 60, 28, (230, 130, 40)),
                         (60, 50, 24, (60, 50, 50))):
        d.ellipse([fx + px - r, fy + py - r * 0.8, fx + px + r, fy + py + r * 0.8], fill=c)
    l = label("DONOR", 46, WHITE); comp(frame, l, fx - l.width / 2, fy + 196)
    if lt > 0.5:
        top_label(frame, "COPY CAT?", 380, YEL, 90)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="copy", s=4.0, e=11.0, bg="office", clock="DAY 1 · THE PLAN", char="uncle", pos=(330, 1120, 440),
         props=copy_props, look=(0.6, 0),
         narr="A clone is a genetic COPY of you, with the same DNA, letter for letter.", n_at=4.2, narr_y=1560,
         say="TWO of me? Double the WORK done!", say_at=7.2, pitch=150),
    dict(id="baby", s=11.0, e=18.0, bg="bedroom", clock="PROBLEM #1", char="kid", pos=(540, 1130, 380),
         props=crib_props, props_after=crib_after, look=(0, 0.3),
         narr="But a clone is born as a BABY. Your copy would be decades YOUNGER.", n_at=11.2, narr_y=1560,
         say="Hi... PAPA?!", say_at=14.6, pitch=480),
    dict(id="dolly", s=18.0, e=25.0, bg="digsite", clock="1996 · SCOTLAND", props=dolly_props,
         narr="Dolly the sheep was cloned from an adult cell. 277 TRIES, one lamb.", n_at=18.2, narr_y=1560,
         say="BAA-sically a COPY.", say_at=21.6, pitch=330),
    dict(id="memory", s=25.0, e=32.0, bg="living", clock="PROBLEM #2", char="kid", pos=(330, 1180, 360),
         props=memory_props, look=(0.6, -0.4),
         narr="Memories aren't in DNA. Your clone won't know your friends or PASSWORDS.", n_at=25.2,
         narr_y=1560, say="Who are YOU, uncle?", say_at=28.4, pitch=480),
    dict(id="twins", s=32.0, e=39.0, bg="gully", clock="NATURE DID IT FIRST", props=twins_props,
         narr="Identical twins are nature's near-clones. Yet even their FINGERPRINTS differ.", n_at=32.2,
         narr_y=1560, say="Same face, DIFFERENT prints!", say_at=35.0, pitch=480),
    dict(id="buffalo", s=39.0, e=46.0, bg="office", clock="2009 · NDRI KARNAL", char="cow", pos=(600, 1110, 460),
         props=lab_props, look=(-0.3, 0.1),
         narr="In 2009, Indian scientists in Karnal cloned a buffalo calf named GARIMA.", n_at=39.2,
         narr_y=1560, say="I'm a BUFFALO, okay?", say_at=42.4, pitch=260),
    dict(id="law", s=46.0, e=TW, bg="office", clock="PROBLEM #3", char="uncle", state="angry",
         pos=(330, 1120, 420), props=law_props, look=(0.5, 0),
         narr="Cloning humans? India's research rules PROHIBIT it, like many countries.", n_at=46.2,
         narr_y=1560, say="No second ME?!", say_at=49.4, pitch=150),
    dict(id="twist", s=TW, e=60.0, bg="living", clock="PLOT TWIST", char="cat", pos=(780, 1080, 420),
         props=cc_props, twist=True, look=(-0.6, 0.1),
         narr="Twist: CC, the first cloned cat, didn't even LOOK like her donor!", n_at=TW + 0.2,
         narr_y=1560, say="Copy... PASTE FAILED.", say_at=TW + 3.4, pitch=520),
    dict(id="outro", s=60.0, e=65.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = min(ease_back((T - 1.9) / 0.4), 1.2)
        mini(frame, "uncle", 400, 1380, 360 * p, T, look=(0.5, 0))
    if T >= 2.4:
        p = min(ease_back((T - 2.4) / 0.4), 1.2)
        mini(frame, "uncle", 680, 1380, 360 * p, T, look=(-0.5, 0))

cfg = dict(
    total=65.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU COULD", WHITE)], 120), 770, 0.75, "right"),
        (title([("CLONE YOURSELF?", YEL)], 130), 915, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" clone", WHITE)], 100), 470, 0.15),
                      (title([("yourself?", YEL)], 96), 600, 0.45)],
               row=[("uncle", 1), ("kid", 1), ("cat", 1), ("cow", 1), ("uncle", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0), dict(t0=18.0, t1=32.0, melody=True),
           dict(t0=32.0, t1=46.0), dict(t0=46.0, t1=TW - 0.15, minor=True),
           dict(t0=TW + 2.0, t1=65.0, melody=True)],
    fx=[("pop", 1.95, 0.4), ("pop", 2.45, 0.4), ("pop", 5.2, 0.3), ("ding", 13.0, 0.3), ("pop", 18.6, 0.4),
        ("tick", 19.0, 0.2), ("tick", 19.6, 0.2), ("tick", 20.2, 0.2), ("ding", 21.0, 0.3), ("click", 25.8, 0.3),
        ("click", 26.2, 0.3), ("click", 26.6, 0.3), ("pop", 34.8, 0.4), ("pop", 47.0, 0.4), ("crash", 47.2, 0.25)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_could_clone_yourself")
