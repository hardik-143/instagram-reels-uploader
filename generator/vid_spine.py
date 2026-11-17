#!/usr/bin/env python3
"""What if gravity stopped squashing you?
Facts (checked 2026-11-17):
- People are about 1 cm (usually 1-2 cm) taller in the morning than in the evening (Jamaica Hospital Medical Center
  via Grunge; inkl summary of Journal of Spinal Disorders: up to ~19 mm a day).
- 23 intervertebral discs (6 cervical, 12 thoracic, 5 lumbar); together up to a third of the spine's length; the
  nucleus is a highly hydrated gel (Kenhub).
- Loading through the day pushes fluid out of the discs; lying down at rest lets them take it back (inkl summary of a
  2020 Scientific Reports MRI study).
- Astronauts can grow up to 3% taller in microgravity, about 5 cm for a 1.8 m person, and return to normal height
  within a few months back on Earth (Space.com).
- Low back pain in spaceflight: pooled prevalence 77% (Journal of Pain Research 2024 systematic review/meta-analysis).
Trend: 1.2M-view Indian IG 'subah pass, shaam fail' height-change reel (782x median, 2026-11-14, vidIQ).
"""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

TW = 53.0
GROUND = 1330
SHIRT = (90, 180, 140)
JEANS = (60, 90, 170)
SKIN = (242, 194, 152)
BONE = (250, 244, 226)
DISC = (120, 190, 240)

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def put_label(frame, txt, cx, y, size=60, col=YEL):
    l = label(txt, size, col)
    comp(frame, l, cx - l.width / 2, y)

def head(B, T, look=(0, -0.1)):
    return draw_char("kid", int(B), T, 0, E.blink_at(T, 0.3), look, 1)

def person(frame, d, T, cx, ground, h, hb=150, ache=False):
    body = h - hb * 0.85
    w = body * 0.34
    leg = body * 0.5
    torso = body - leg
    top = ground - body
    d.rounded_rectangle([cx - w / 2, ground - leg, cx - 3, ground], 8, fill=JEANS, outline=OUTL, width=4)
    d.rounded_rectangle([cx + 3, ground - leg, cx + w / 2, ground], 8, fill=JEANS, outline=OUTL, width=4)
    aw = w * 0.24
    d.rounded_rectangle([cx - w / 2 - aw, top + 6, cx - w / 2 + 2, top + torso * 0.95], 8, fill=SKIN, outline=OUTL, width=4)
    d.rounded_rectangle([cx + w / 2 - 2, top + 6, cx + w / 2 + aw, top + torso * 0.95], 8, fill=SKIN, outline=OUTL, width=4)
    d.rounded_rectangle([cx - w / 2, top, cx + w / 2, top + torso + 10], 12, fill=SHIRT, outline=OUTL, width=5)
    if ache:
        r = 26 + 10 * abs(math.sin(T * 6))
        y = top + torso * 0.8
        d.ellipse([cx - r, y - r, cx + r, y + r], outline=(240, 60, 60), width=7)
        d.ellipse([cx - 10, y - 10, cx + 10, y + 10], fill=(240, 60, 60))
    comp(frame, head(hb, T), cx - hb / 2, top - hb * 0.85)
    return top - hb * 0.85

def floor(d, col=(150, 110, 80)):
    d.rectangle([0, GROUND, W, H], fill=col)
    d.line([(0, GROUND), (W, GROUND)], fill=OUTL, width=6)

def ruler(d, x, top, bottom):
    d.rectangle([x - 40, top, x + 40, bottom], fill=(250, 230, 150), outline=OUTL, width=5)
    for k, y in enumerate(range(int(bottom), int(top), -20)):
        L = 40 if k % 5 == 0 else 20
        d.line([(x - 40, y), (x - 40 + L, y)], fill=OUTL, width=3)

def mark(d, x0, x1, y, col):
    d.line([(x0, y), (x1, y)], fill=col, width=8)

def spine(d, cx, top, squash=0.0, n=7, wb=150, hv=62, hd=26):
    """Vertebra stack from `top`; squash 0..1 flattens and widens the discs."""
    y = top
    dh = hd * (1 - 0.45 * squash)
    dw = (wb - 16) * (1 + 0.12 * squash)
    for k in range(n):
        d.rounded_rectangle([cx - wb / 2, y, cx + wb / 2, y + hv], 16, fill=BONE, outline=OUTL, width=5)
        d.polygon([(cx + wb / 2, y + 14), (cx + wb / 2 + 50, y + hv / 2), (cx + wb / 2, y + hv - 14)], fill=BONE, outline=OUTL)
        y += hv
        if k < n - 1:
            d.rounded_rectangle([cx - dw / 2, y, cx + dw / 2, y + dh], int(dh / 2), fill=DISC, outline=OUTL, width=4)
            y += dh
    return y

def drop(d, x, y, s=1.0):
    d.ellipse([x - 12 * s, y - 4 * s, x + 12 * s, y + 20 * s], fill=DISC, outline=OUTL, width=3)
    d.polygon([(x - 10 * s, y + 2 * s), (x, y - 20 * s), (x + 10 * s, y + 2 * s)], fill=DISC)

# ---------------------------------------------------------------- scenes
def morning_props(frame, d, T, sc):
    floor(d)
    ruler(d, 780, 700, GROUND)
    top = person(frame, d, T, 470, GROUND, 600)
    mark(d, 700, 860, top + 6, (90, 220, 120))
    put_label(frame, "7 AM HEIGHT", 780, top - 70, 48, (120, 240, 150))

def spine_props(frame, d, T, sc):
    put_label(frame, "23 DISCS", 540, 335, 64)
    bot = spine(d, 470, 760, 0.0)
    put_label(frame, "BONE", 790, 790, 54, WHITE)
    put_label(frame, "DISC", 790, 870, 54, (150, 210, 255))
    d.line([(700, 825), (580, 792)], fill=WHITE, width=5)
    d.line([(700, 905), (545, 840)], fill=(150, 210, 255), width=5)

def squeeze_props(frame, d, T, sc):
    lt = T - sc["s"]
    sq = 0.5 + 0.5 * math.sin(lt * 2.4 - 1.57)
    sq = clamp(lt / 3.0) * 0.6 + 0.4 * sq * clamp(lt / 3.0)
    put_label(frame, "GRAVITY PUSHES DOWN", 540, 335, 60, (255, 130, 130))
    # arrow down
    for ax in (200, 880):
        d.polygon([(ax - 30, 820), (ax + 30, 820), (ax + 30, 940), (ax + 60, 940), (ax, 1010), (ax - 60, 940), (ax - 30, 940)],
                  fill=(255, 130, 130), outline=OUTL)
    spine(d, 470, 760 + 60 * sq, sq)
    for k in range(5):
        ph = (lt * 0.8 + k * 0.2) % 1.0
        side = -1 if k % 2 else 1
        drop(d, 470 + side * (110 + 140 * ph), 830 + k * 88 + 40 * ph, 1.0)

def night_props(frame, d, T, sc):
    lt = T - sc["s"]
    floor(d, (90, 70, 60))
    ruler(d, 780, 700, GROUND)
    shrink = 26 * ease_out(clamp((lt - 0.5) / 1.6))
    morning_top = GROUND - 600 + 150 * 0.0
    top = person(frame, d, T, 470, GROUND, 600 - shrink)
    mark(d, 700, 860, GROUND - 600 + 6, (90, 220, 120))
    mark(d, 700, 860, top + 6, (255, 110, 110))
    put_label(frame, "9 PM: ~1 CM LESS", 540, 335, 60, (255, 140, 140))

def sleep_props(frame, d, T, sc):
    lt = T - sc["s"]
    # bed
    d.rounded_rectangle([110, 1150, 980, 1250], 20, fill=(200, 120, 160), outline=OUTL, width=6)
    d.rectangle([110, 1250, 140, 1330], fill=(120, 80, 60), outline=OUTL, width=4)
    d.rectangle([950, 1250, 980, 1330], fill=(120, 80, 60), outline=OUTL, width=4)
    d.rounded_rectangle([140, 1040, 960, 1160], 40, fill=(250, 250, 255), outline=OUTL, width=5)  # blanket
    spr = head(190, T, (0, 0)).rotate(90, resample=Image.BICUBIC, expand=False)
    comp(frame, spr, 120, 950)
    for k in range(3):
        ph = (lt * 0.5 + k / 3) % 1.0
        put_label(frame, "z", 330 + 60 * k + 40 * ph, int(900 - 200 * ph), int(50 + 30 * ph), WHITE)
    # discs refilling icon
    for k in range(3):
        f = clamp(lt / 3.0)
        y = 1060 + k * 0
    put_label(frame, "DISCS REFILL", 540, 335, 60, (150, 210, 255))

def space_props(frame, d, T, sc):
    lt = T - sc["s"]
    bob = 14 * math.sin(T * 1.6)
    grow = 40 * ease_out(clamp((lt - 0.6) / 1.8))
    ruler(d, 800, 760, 1330)
    base = 1300 + bob
    top = person(frame, d, T, 480, base, 520 + grow, 140)
    mark(d, 720, 880, base - 520 + 6 + 140 * 0, (120, 180, 255))
    mark(d, 720, 880, top + 6, (90, 220, 120))
    put_label(frame, "UP TO +3%", 540, 335, 64)

def back_props(frame, d, T, sc):
    bob = 14 * math.sin(T * 1.6)
    person(frame, d, T, 540, 1300 + bob, 560, 140, ache=True)
    put_label(frame, "MOST REPORT BACK PAIN", 540, 335, 60, (255, 140, 140))

def twist_props(frame, d, T, sc):
    floor(d)
    ruler(d, 780, 700, GROUND)
    top = person(frame, d, T, 470, GROUND, 600)
    mark(d, 700, 860, top + 6, YEL)
    # sunrise in the window
    d.rectangle([80, 760, 300, 960], fill=(255, 210, 140), outline=OUTL, width=6)
    d.pieslice([130, 860, 250, 980], 180, 360, fill=(255, 170, 60), outline=OUTL)
    d.line([(190, 760), (190, 960)], fill=OUTL, width=5)
    d.line([(80, 860), (300, 860)], fill=OUTL, width=5)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="morning", s=4.0, e=11.0, bg="day", clock="7 AM", props=morning_props,
         narr="Fact: you're about 1-2 CM taller when you WAKE up.", n_at=4.2,
         say="Morning me is TALLER!", say_at=6.8, pitch=640, bubble_y=600),
    dict(id="spine", s=11.0, e=18.0, bg="night", clock="YOUR SPINE", props=spine_props,
         narr="Between your spine's bones sit 23 squishy DISCS, full of WATER.", n_at=11.2,
         say="Built-in SHOCK absorbers!", say_at=13.8, pitch=620, bubble_y=600),
    dict(id="squeeze", s=18.0, e=25.0, bg="night", clock="ALL DAY", props=squeeze_props,
         narr="Standing, walking, sitting: gravity SQUEEZES water out of them.", n_at=18.2,
         say="Squish... SQUISH...", say_at=21.8, pitch=620, bubble_y=700),
    dict(id="night", s=25.0, e=32.0, bg="night", clock="9 PM", props=night_props,
         narr="By night you're around 1 CM SHORTER. Same you, same day!", n_at=25.2,
         say="Who STOLE my centimetre?", say_at=27.8, pitch=640, bubble_y=600),
    dict(id="sleep", s=32.0, e=39.0, bg="night", clock="SLEEP", props=sleep_props,
         narr="Lie down, and the discs SOAK the water back up overnight.", n_at=32.2,
         say="Zzz... RECHARGING", say_at=34.8, pitch=560, bubble_y=600),
    dict(id="space", s=39.0, e=46.0, bg="space", clock="NO GRAVITY", props=space_props,
         narr="No gravity at all? Astronauts grow up to 3% TALLER, about 5 CM.", n_at=39.2,
         say="Finally TALL!", say_at=41.8, pitch=660, bubble_y=600),
    dict(id="back", s=46.0, e=TW, bg="space", clock="THE CATCH", props=back_props,
         narr="Most astronauts get BACK PAIN up there, and shrink back on Earth.", n_at=46.2,
         say="Ouch, my BACK!", say_at=48.8, pitch=600, bubble_y=600),
    dict(id="twist", s=TW, e=61.0, bg="day", clock="PLOT TWIST", props=twist_props, twist=True,
         narr="Your tallest moment of the day? The second you get out of BED.", n_at=TW + 0.4,
         say="Measure me at 7 AM!", say_at=TW + 3.4, pitch=660, bubble_y=600),
    dict(id="outro", s=61.0, e=66.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.4)
        paste_c(frame, head(260, T, (0, 0.2)), 540, 1440, p)

cfg = dict(
    total=66.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 470, 0.2, "pop"),
        (title([("GRAVITY", WHITE)], 150), 670, 0.75, "right"),
        (title([("STOPPED SQUASHING", YEL)], 110), 830, 1.05, "left"),
        (title([("YOU?", WHITE)], 150), 980, 1.4, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Morning or night:", WHITE)], 90), 470, 0.15),
                      (title([("when are ", WHITE), ("YOU", YEL), (" tallest?", WHITE)], 90), 600, 0.45)],
               row=[("kid", 1), ("moon", 1), ("earth", 0), ("sun", 1), ("uncle", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=TW - 0.15, melody=True),
           dict(t0=61.0, t1=66.0, melody=True)],
    fx=[("bubbles", 18.4, 0.25, dict(dd=5.0)), ("pop", 46.6, 0.4)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_gravity_stopped_squashing_you")
