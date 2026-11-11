#!/usr/bin/env python3
"""What if you had a newborn's body again? (Children's Day week, 14 Nov)
Facts (checked 2026-11-11):
- Newborns have around 300 bones (Healthline; PopSci 'more than 300'); many fuse, adults have 206.
- Kneecaps are cartilage at birth and start turning to bone in the toddler years, from around age 2 (Pampers India).
- Skull bones are not yet joined, leaving soft spots (fontanelles) that close as the bones grow together (Healthline).
- Newborns focus best at 20-30 cm, about the distance to a parent's face during feeding (AAP HealthyChildren.org).
- Louis Robinson 1891: 60 infants under one month held a horizontal rod for at least 10 s; one held 2 min 35 s
  (Lancaster University psychology glossary).
- Newborn heart rate about 120-160 bpm vs adult resting 60-100 (standard newborn vital-sign references).
- Brain at birth about a quarter of adult size, doubles in the first year, ~90% by age 5 (First Things First).
- Newborns cry without visible tears; tears usually start at about 3-4 weeks, some up to 2 months (Mental Floss / Live Science).
"""
import math
from PIL import Image, ImageDraw, ImageFilter
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

TW = 53.0

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=360, col=YEL, size=60):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

def bone(d, x, y, L=70, a=0.0, col=(250, 246, 232)):
    dx, dy = L / 2 * math.cos(a), L / 2 * math.sin(a)
    d.line([(x - dx, y - dy), (x + dx, y + dy)], fill=OUTL, width=22)
    for sx in (-1, 1):
        cx, cy = x + sx * dx, y + sx * dy
        for o in (-1, 1):
            ox, oy = -math.sin(a) * 9 * o, math.cos(a) * 9 * o
            d.ellipse([cx + ox - 13, cy + oy - 13, cx + ox + 13, cy + oy + 13], fill=col, outline=OUTL, width=4)
    d.line([(x - dx, y - dy), (x + dx, y + dy)], fill=col, width=14)

# ---------------------------------------------------------------- props
def bones_props(frame, d, T, sc):
    lt = T - sc["s"]
    top_label(frame, "BIRTH: ~300 BONES")
    if lt > 3.5:
        top_label(frame, "ADULT: 206", 440, WHITE, 56)
    for k in range(8):
        a = T * 1.5 + k * math.pi / 4
        x = 540 + 300 * math.cos(a); y = 1040 + 200 * math.sin(a)
        bone(d, x, y, 60, a + 1.2)

def knee_props(frame, d, T, sc):
    top_label(frame, "KNEECAPS: SOFT CARTILAGE")
    # a cartoon leg with a squishy blue-ish kneecap
    d.rounded_rectangle([700, 880, 820, 1330], 50, fill=(242, 194, 152), outline=OUTL, width=6)
    s = 1 + 0.08 * math.sin(T * 6)
    d.ellipse([760 - 55 * s, 1080 - 50 / s, 760 + 55 * s, 1080 + 50 / s], fill=(170, 210, 240), outline=OUTL, width=5)

def skull_props(frame, d, T, sc):
    top_label(frame, "SOFT SPOTS ON THE HEAD")
    for k, (x, y) in enumerate(((540, 905), (480, 935), (600, 935))):
        r = 18 + 4 * math.sin(T * 4 + k)
        d.ellipse([x - r, y - r, x + r, y + r], outline=YEL, width=6)

_blur = {}
def blur_bg(T):
    if "b" not in _blur:
        _blur["b"] = E.bg("bedroom").convert("RGBA").filter(ImageFilter.GaussianBlur(26))
    return _blur["b"]

def eyes_props(frame, d, T, sc):
    top_label(frame, "SHARP ONLY AT 20-30 CM")
    sharp = E.bg("bedroom").convert("RGBA")
    m = Image.new("L", frame.size, 0); ImageDraw.Draw(m).ellipse([700, 900, 1000, 1200], fill=255)
    frame.paste(sharp, (0, 0), m)
    d.ellipse([700, 900, 1000, 1200], outline=WHITE, width=8)
    comp(frame, draw_char("uncle", 220, T, 0, False, (-0.4, 0), 1), 850 - 110, 1050 - 110)

def grip_props(frame, d, T, sc):
    lt = T - sc["s"]
    sway = 14 * math.sin(T * 2.2)
    d.rounded_rectangle([200, 900, 880, 932], 14, fill=(150, 104, 64), outline=OUTL, width=5)
    for sx in (-1, 1):
        hx = 540 + sx * 90
        d.line([(hx, 916), (540 + sx * 110 + sway, 1030)], fill=OUTL, width=34)
        d.line([(hx, 916), (540 + sx * 110 + sway, 1030)], fill=(242, 194, 152), width=22)
        d.ellipse([hx - 26, 892, hx + 26, 940], fill=(242, 194, 152), outline=OUTL, width=5)
    top_label(frame, "1891 STUDY, 60 NEWBORNS")
    if lt > 3.5:
        top_label(frame, "RECORD: 2 MIN 35 SEC", 440, WHITE, 56)

def grip_pos(T):
    return (540 + 14 * math.sin(T * 2.2), 1150, 360)

def heart_props(frame, d, T, sc):
    top_label(frame, "~120-160 BEATS A MINUTE")
    y0 = 1060; pts = []
    for x in range(40, 1041, 10):
        ph = ((x - T * 900) % 200) / 200
        y = y0
        if 0.40 < ph < 0.46: y = y0 - 140 * math.sin((ph - 0.40) / 0.06 * math.pi)
        elif 0.46 < ph < 0.52: y = y0 + 70 * math.sin((ph - 0.46) / 0.06 * math.pi)
        pts.append((x, y))
    d.line(pts, fill=(255, 120, 140), width=8, joint="curve")

def brain_props(frame, d, T, sc):
    lt = T - sc["s"]
    top_label(frame, "BRAIN SIZE")
    x0, y0, h = 800, 920, 380
    d.rounded_rectangle([x0, y0, x0 + 70, y0 + h], 30, fill=(60, 60, 80), outline=OUTL, width=5)
    f = 0.25 if lt < 3.0 else 0.25 + 0.25 * ease_out(clamp((lt - 3.0) / 1.5))
    d.rounded_rectangle([x0 + 6, y0 + h - 6 - (h - 12) * f, x0 + 64, y0 + h - 6], 24, fill=(120, 220, 140))
    top_label(frame, "BIRTH: 1/4 OF ADULT" if lt < 3.0 else "AGE 1: ABOUT 1/2", 440, WHITE, 56)

def tears_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 3.0:
        top_label(frame, "TEARS AT ~3-4 WEEKS")
    # dry "WAAH" sound lines
    for k in range(3):
        r = 260 + 40 * k + 20 * math.sin(T * 10 + k)
        d.arc([540 - r, 1060 - r, 540 + r, 1060 + r], 200, 250, fill=WHITE, width=8)
        d.arc([540 - r, 1060 - r, 540 + r, 1060 + r], 290, 340, fill=WHITE, width=8)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="bones", s=4.0, e=11.0, bg="bedroom", clock="DAY 1", char="kid", pos=(540, 1060, 440),
         props=bones_props,
         narr="You'd have about 300 BONES. Many fuse as you grow, leaving 206.", n_at=4.2,
         say="More bones than PAPA!", say_at=6.6, pitch=660),
    dict(id="knees", s=11.0, e=18.0, bg="bedroom", clock="KNEES", char="kid", pos=(330, 1080, 400),
         props=knee_props, look=(0.5, 0.3),
         narr="Your kneecaps would be soft CARTILAGE, not bone, for years.", n_at=11.2,
         say="Squishy KNEES!", say_at=13.8, pitch=660),
    dict(id="skull", s=18.0, e=25.0, bg="bedroom", clock="HEAD", char="kid", pos=(540, 1060, 460),
         props_after=skull_props,
         narr="Your skull bones aren't joined yet, leaving soft SPOTS that close later.", n_at=18.2,
         say="Handle with CARE!", say_at=20.8, pitch=660),
    dict(id="eyes", s=25.0, e=32.0, bg_fn=blur_bg, clock="EYES", char="kid", pos=(330, 1080, 420),
         props=eyes_props, look=(0.6, 0),
         narr="Clear vision only up to about 20-30 CM: Mumma's face while feeding.", n_at=25.2,
         say="Everything else is BLURRY!", say_at=27.8, pitch=660),
    dict(id="grip", s=32.0, e=39.0, bg="bedroom", clock="GRIP", char="kid", pos=grip_pos,
         props=grip_props, look=(0, -0.3),
         narr="In 1891, newborns hung from a rod for at least 10 SECONDS.", n_at=32.2,
         say="NEVER try this on a baby!", say_at=34.8, pitch=660),
    dict(id="heart", s=39.0, e=46.0, bg="night", clock="HEART", char="heart", pos=(540, 1060, 420),
         props=heart_props,
         narr="Your heart would race at about 120 to 160 BEATS a minute.", n_at=39.2,
         say="Zoom zoom ZOOM!", say_at=41.8, pitch=560),
    dict(id="brain", s=46.0, e=TW, bg="bedroom", clock="BRAIN", char="kid", pos=(430, 1070, 420),
         props=brain_props, look=(0, -0.2),
         narr="Your brain: a QUARTER of adult size, then it DOUBLES in year one.", n_at=46.2,
         say="Loading... please WAIT!", say_at=48.8, pitch=660),
    dict(id="twist", s=TW, e=61.0, bg="bedroom", clock="PLOT TWIST", char="kid", state="puff", pos=(540, 1060, 440),
         props=tears_props, twist=True,
         narr="You'd cry LOUDLY, but with NO TEARS. Tear ducts aren't fully working yet.", n_at=TW + 0.4,
         say="WAAAH! Where are my TEARS?", say_at=TW + 3.0, pitch=700),
    dict(id="outro", s=61.0, e=66.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.4)
        spr = draw_char("kid", 300, T, 0, False, (0, 0.2), 1)
        paste_c(frame, spr, 540, 1420, p)

cfg = dict(
    total=66.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 520, 0.2, "pop"),
        (title([("YOU HAD A", WHITE)], 130), 720, 0.75, "right"),
        (title([("NEWBORN'S BODY", YEL)], 120), 860, 1.05, "left"),
        (title([("AGAIN?", WHITE)], 120), 1000, 1.4, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Which fact", WHITE)], 96), 470, 0.15),
                      (title([("shocked ", WHITE), ("YOU?", YEL)], 110), 600, 0.45)],
               row=[("kid", 1), ("heart", 1), ("uncle", 1), ("kid", "puff"), ("ladoo", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=TW - 0.15, melody=True),
           dict(t0=61.0, t1=66.0, melody=True)],
    fx=[("heartbeat", 39.2, 0.5, dict(dd=6.0, bpm=140)), ("pop", 16.0, 0.4)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_had_a_newborns_body")
