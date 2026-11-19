#!/usr/bin/env python3
"""What if you could tickle yourself? Facts: Blakemore, Wolpert & Frith (UCL; robot study J. Cogn. Neurosci. 1999,
NeuroImage 10:448-459, 1999): self-produced touch on the right palm was rated less tickly, intense and pleasant than
the same touch made by a robot; adding delays of 0, 100, 200, 300 ms between the left-hand movement and the touch made
it progressively more tickly from 0 to 200 ms; the cerebellum predicts the sensory consequences of your own movement
and the brain dampens them (ScienceAlert, quoting Sarah-Jayne Blakemore). Knismesis = light, crawly tickle; gargalesis
= heavy, laughter tickle (ScienceAlert 2016). Rats: Ishiyama & Brecht, Science 2016 (ScienceDaily): rats make 50 kHz
ultrasonic 'laughter' calls when tickled (humans hear to about 20 kHz), are most ticklish on belly and the soles of
their feet, jump for joy and chase the hand; anxious rats are less ticklish."""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite

TW = 53.0
PINK = (240, 150, 180)

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=68):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

def lab_at(frame, txt, x, y, col=WHITE, size=52):
    l = label(txt, size, col); comp(frame, l, x - l.width / 2, y - l.height / 2)

def mini(frame, kind, x, y, size, T, state=1, look=(0, 0.2), talk=0.0):
    size = max(2, int(size))
    spr = draw_char(kind, size, T, talk, False, look, state)
    comp(frame, spr, x - size / 2, y - size / 2)

def feather(d, x, y, s, ang):
    """A feather: a quill line with a soft vane, rotated by ang (radians)."""
    ca, sa = math.cos(ang), math.sin(ang)
    def P(u, v): return (x + (u * ca - v * sa) * s, y + (u * sa + v * ca) * s)
    vane = [P(0.15, 0)] + [P(0.15 + 0.85 * k / 10, 0.22 * math.sin(math.pi * k / 10)) for k in range(11)] + \
           [P(0.15 + 0.85 * k / 10, -0.22 * math.sin(math.pi * k / 10)) for k in range(10, -1, -1)]
    d.polygon(vane, fill=(250, 245, 255), outline=OUTL)
    d.line([P(-0.15, 0), P(1.0, 0)], fill=OUTL, width=5)

def foot(d, x, y, s):
    d.rounded_rectangle([x - 0.9 * s, y - 0.35 * s, x + 0.9 * s, y + 0.35 * s], radius=int(0.35 * s),
                        fill=(242, 194, 152), outline=OUTL, width=6)
    for k in range(5):
        tx = x + 0.95 * s; ty = y - 0.28 * s + k * 0.14 * s; r = 0.09 * s * (1.15 - 0.08 * k)
        d.ellipse([tx - r, ty - r, tx + r, ty + r], fill=(242, 194, 152), outline=OUTL, width=4)

def wiggles(frame, x, y, T, col=YEL, n=3):
    for k in range(n):
        a = -0.8 + 0.8 * k + 0.2 * math.sin(T * 9 + k)
        lab_at(frame, "HA", x - 130 + 130 * k, y - 30 * k % 60 - 12 * math.sin(T * 12 + k * 2), col, 52)

def rat(d, x, y, s, T, jump=0.0):
    y = y - jump
    d.line([(x + 0.8 * s, y + 0.2 * s), (x + 1.3 * s, y + 0.1 * s + 0.15 * s * math.sin(T * 6)),
            (x + 1.7 * s, y + 0.25 * s)], fill=(230, 160, 170), width=8)
    d.ellipse([x - 0.9 * s, y - 0.5 * s, x + 0.9 * s, y + 0.5 * s], fill=(170, 170, 185), outline=OUTL, width=6)
    d.ellipse([x - 0.4 * s, y - 0.1 * s, x + 0.4 * s, y + 0.45 * s], fill=(235, 225, 235))
    hx = x - 0.95 * s
    d.ellipse([hx - 0.45 * s, y - 0.55 * s, hx + 0.45 * s, y + 0.25 * s], fill=(170, 170, 185), outline=OUTL, width=6)
    for ex in (-0.3, 0.25):
        d.ellipse([hx + ex * s - 0.2 * s, y - 0.85 * s, hx + ex * s + 0.2 * s, y - 0.4 * s], fill=(230, 160, 170),
                  outline=OUTL, width=5)
    for ex in (-0.15, 0.12):
        d.ellipse([hx + ex * s - 0.06 * s, y - 0.25 * s, hx + ex * s + 0.06 * s, y - 0.12 * s], fill=OUTL)
    d.ellipse([hx - 0.55 * s, y - 0.05 * s, hx - 0.38 * s, y + 0.1 * s], fill=(230, 120, 140))
    d.arc([hx - 0.25 * s, y - 0.1 * s, hx + 0.15 * s, y + 0.15 * s], 20, 160, fill=OUTL, width=4)

def brain(d, cx, cy, r, glow):
    d.ellipse([cx - r, cy - 0.72 * r, cx + r, cy + 0.72 * r], fill=(240, 170, 190), outline=OUTL, width=7)
    for k in range(3):
        d.arc([cx - 0.7 * r + k * 0.35 * r, cy - 0.5 * r, cx - 0.2 * r + k * 0.35 * r, cy + 0.1 * r], 200, 340,
              fill=(200, 110, 140), width=6)
    cr = 0.36 * r
    col = (255, 210, 60) if glow else (210, 120, 150)
    d.ellipse([cx + 0.35 * r - cr, cy + 0.35 * r - 0.7 * cr, cx + 0.35 * r + cr, cy + 0.35 * r + 0.7 * cr],
              fill=col, outline=OUTL, width=6)
    for k in range(3):
        yy = cy + 0.25 * r + k * 0.1 * r
        d.line([(cx + 0.12 * r, yy), (cx + 0.58 * r, yy)], fill=OUTL, width=3)

def meter(d, frame, x, y, w, h, frac, lab):
    d.rounded_rectangle([x, y, x + w, y + h], radius=20, fill=(40, 40, 60), outline=OUTL, width=6)
    d.rounded_rectangle([x + 8, y + 8, x + 8 + max(4, (w - 16) * frac), y + h - 8], radius=14, fill=YEL)
    lab_at(frame, lab, x + w / 2, y - 50, WHITE, 48)

# ---------------------------------------------------------------- props
def try_props(frame, d, T, sc):
    lt = T - sc["s"]
    mini(frame, "kid", 360, 960, 420, T, 1, (0.5, 0.4))
    foot(d, 760, 1220, 110)
    if lt > 0.8:
        feather(d, 700 + 40 * math.sin(T * 10), 1080 + 20 * math.cos(T * 10), 170, -2.1)
    if lt > 2.8: top_label(frame, "...NOTHING?", 400, YEL, 90)

def brain_props(frame, d, T, sc):
    lt = T - sc["s"]
    glow = lt > 1.8 and int(T * 4) % 2 == 0
    brain(d, 540, 980, 300, glow)
    if lt > 1.8: lab_at(frame, "CEREBELLUM", 700, 1290, YEL, 56)
    if lt > 3.2: top_label(frame, "PREDICTED. TURNED DOWN.", 400, WHITE, 60)

def other_props(frame, d, T, sc):
    lt = T - sc["s"]
    talk = clamp(0.5 + 0.6 * math.sin(T * 22)) if lt > 1.4 else 0
    mini(frame, "kid", 380, 1060, 380, T, 1, (0.2, 0.0), talk)
    mini(frame, "uncle", 790, 1000, 400, T, 1, (-0.5, 0.2))
    if lt > 0.6:
        feather(d, 560 + 40 * math.sin(T * 12), 1100 + 25 * math.cos(T * 12), 160, math.pi + 0.4)
    if lt > 1.4:
        wiggles(frame, 380, 860, T)
        top_label(frame, "HA HA HA!", 400, YEL, 100)

def robot_arm(d, frame, lt, T, delay_txt):
    # base + two-segment arm ending in a feather, over a palm
    d.rounded_rectangle([110, 1180, 330, 1300], radius=16, fill=(120, 130, 150), outline=OUTL, width=6)
    j1 = (220, 1180); j2 = (420, 900 + 20 * math.sin(T * 2))
    tip = (650 + 50 * math.sin(T * 7), 1030)
    d.line([j1, j2], fill=(160, 170, 190), width=40); d.line([j2, tip], fill=(160, 170, 190), width=32)
    for p in (j1, j2):
        d.ellipse([p[0] - 30, p[1] - 30, p[0] + 30, p[1] + 30], fill=(90, 100, 120), outline=OUTL, width=5)
    feather(d, tip[0], tip[1], 150, 0.9)
    # palm
    d.rounded_rectangle([620, 1150, 920, 1290], radius=60, fill=(242, 194, 152), outline=OUTL, width=6)
    lab_at(frame, "PALM", 770, 1220, WHITE, 44)
    if delay_txt: lab_at(frame, delay_txt, 770, 760, YEL, 64)

def robot_props(frame, d, T, sc):
    lt = T - sc["s"]
    robot_arm(d, frame, lt, T, "DELAY ADDED" if lt > 2.0 else "")
    if lt > 0.4: top_label(frame, "UCL ROBOT TEST, 1999", 400, WHITE, 62)

def delay_props(frame, d, T, sc):
    lt = T - sc["s"]
    steps = [("0 s", 0.12), ("0.1 s", 0.45), ("0.2 s", 0.9)]
    k = min(2, int(max(0, lt - 0.6) / 1.4))
    txt, frac = steps[k]
    p = ease_out(clamp((lt - 0.6 - 1.4 * k) / 0.6))
    prev = steps[k - 1][1] if k else 0.0
    meter(d, frame, 140, 1000, 800, 120, prev + (frac - prev) * p, "TICKLY-METER")
    lab_at(frame, "DELAY: " + txt, 540, 800, YEL, 80)
    if k == 2 and lt > 4.0:
        mini(frame, "kid", 540, 1260, 200, T, 1, (0, 0), clamp(0.5 + 0.6 * math.sin(T * 22)))

def types_props(frame, d, T, sc):
    lt = T - sc["s"]
    mini(frame, "kid", 270, 980, 280, T, 1, (0.3, 0.3))
    feather(d, 270 + 30 * math.sin(T * 6), 1150, 110, -0.4)
    lab_at(frame, "KNISMESIS", 270, 1290, WHITE, 50)
    if lt > 2.0:
        talk = clamp(0.5 + 0.6 * math.sin(T * 22))
        mini(frame, "kid", 790, 980, 280, T, 1, (0, 0), talk)
        wiggles(frame, 790, 850, T)
        lab_at(frame, "GARGALESIS", 790, 1290, YEL, 50)
    top_label(frame, "2 KINDS OF TICKLE", 400, WHITE, 66)

def rat_props(frame, d, T, sc):
    lt = T - sc["s"]
    jump = 110 * abs(math.sin(T * 5)) if lt > 3.2 else 0
    rat(d, 560, 1120, 150, T, jump)
    if lt > 0.8:
        r0 = (lt * 260) % 260
        for k in range(3):
            r = 60 + r0 + 90 * k
            if r < 340:
                d.arc([380 - r, 1050 - r, 380 + r, 1050 + r], 200, 260, fill=YEL, width=7)
        lab_at(frame, "50 kHz SQUEAKS", 540, 760, YEL, 64)
    if lt > 3.2: top_label(frame, "JUMPS FOR JOY", 400, WHITE, 70)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    talk = clamp(0.5 + 0.6 * math.sin(T * 22)) if lt > 1.0 else 0
    mini(frame, "kid", 540, 980, 380, T, 1, (0, 0), talk)
    if lt > 1.0:
        wiggles(frame, 540, 780, T)
        lab_at(frame, "SOCKS!", 230, 900, YEL, 64)
        lab_at(frame, "COMB!", 860, 900, YEL, 64)
        lab_at(frame, "SCRATCH!", 540, 1260, YEL, 64)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="try", s=4.0, e=11.0, bg="bedroom", clock="TRY IT NOW", props=try_props,
         narr="Try it right now: TICKLE your own foot. Almost NOTHING happens.", n_at=4.2, narr_y=1530),
    dict(id="brain", s=11.0, e=18.0, bg="night", clock="INSIDE YOUR HEAD", props=brain_props,
         narr="Your CEREBELLUM predicts the touch from your own hand, and your brain TURNS IT DOWN.",
         n_at=11.2, narr_y=1530),
    dict(id="other", s=18.0, e=25.0, bg="living", clock="SURPRISE ATTACK", props=other_props,
         narr="When SOMEONE ELSE does it, your brain can't predict it, so it TICKLES.", n_at=18.2,
         narr_y=1530),
    dict(id="robot", s=25.0, e=32.0, bg="office", clock="THE TRICK", props=robot_props,
         narr="So scientists in LONDON let people tickle their own palm through a ROBOT ARM.", n_at=25.2,
         narr_y=1530),
    dict(id="delay", s=32.0, e=39.0, bg="office", clock="TINY LAG", props=delay_props,
         narr="The longer the robot's DELAY, up to 0.2 SECONDS, the more TICKLY it felt.", n_at=32.2,
         narr_y=1530),
    dict(id="types", s=39.0, e=46.0, bg="living", clock="TICKLE SCIENCE", props=types_props,
         narr="A light, crawly tickle is KNISMESIS. The laugh-out-loud one is GARGALESIS.", n_at=39.2,
         narr_y=1530),
    dict(id="rat", s=46.0, e=TW, bg="day", clock="NOT JUST US", props=rat_props,
         narr="Even RATS laugh when tickled, with squeaks too HIGH for us to hear.", n_at=46.2,
         narr_y=1530),
    dict(id="twist", s=TW, e=60.0, bg="twist", clock="PLOT TWIST", twist=True, props=twist_props,
         narr="Twist: if that brain filter broke, every SOCK, comb and SCRATCH might tickle you all day!",
         n_at=TW + 0.2, narr_y=1530),
    dict(id="outro", s=60.0, e=65.0),
]

def intro_extra(frame, d, T):
    if T >= 1.6:
        p = min(ease_back((T - 1.6) / 0.5), 1.15)
        mini(frame, "kid", 540, 1240, 300 * p + 2, T, 1, (0, 0))
        if T > 2.0: feather(d, 680 + 30 * math.sin(T * 9), 1260, 140 * p, -2.4)

cfg = dict(
    total=65.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 480, 0.2, "pop"),
        (title([("YOU COULD", WHITE)], 130), 690, 0.75, "right"),
        (title([("TICKLE YOURSELF?", YEL)], 130), 830, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Where are ", WHITE), ("YOU", YEL)], 96), 470, 0.15),
                      (title([("most ticklish?", WHITE)], 96), 600, 0.45)],
               row=[("kid", 1), ("uncle", 1), ("dog", 1), ("cat", 1), ("kid", "puff")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=25.0, melody=True),
           dict(t0=25.0, t1=39.0), dict(t0=39.0, t1=TW - 0.15, melody=True),
           dict(t0=TW + 2.0, t1=65.0, melody=True)],
    drones=[dict(t0=TW, dur=7.0, g=0.12)],
    fx=[("pop", 6.8, 0.3), ("ding", 13.0, 0.2), ("pop", 19.5, 0.3), ("click", 27.0, 0.2),
        ("tick", 33.0, 0.2), ("tick", 34.4, 0.2), ("tick", 35.8, 0.2), ("ding", 36.5, 0.2),
        ("pop", 41.0, 0.3), ("pop", 49.2, 0.25), ("pop", TW + 1.0, 0.25)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_could_tickle_yourself")
