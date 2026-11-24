#!/usr/bin/env python3
"""What if gravity doubled for a day? Physics (scaling with g, other things equal): weight = m*g, so a scale reads
2x (60 kg -> 120 kg). Jump height h = v^2/(2g): same take-off speed -> half the height. Impact speed v = sqrt(2gh):
sqrt(2) = 1.41 -> ~40% faster. Projectile range R = v^2 sin(2a)/g: roughly half as far (ignoring drag). Deep-water
wave speed c = sqrt(g*lambda/2pi): same wavelength -> ~40% faster. Under +Gz, blood moves from the head toward the
legs and brain/eye blood pressure drops (SKYbrary 'G-induced impairment and the risk of G-LOC'). Relaxed tolerance
'appears to be around 3.5G when unprotected' (SKYbrary); fighter pilots feel about 9g (explainthatstuff), with g-suits
compressing the lower body (SKYbrary). Twist: a typical rollercoaster's biggest force is 'no more than about 2-3.5g'
(explainthatstuff); Helix first drop 3.5g (Physics World)."""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite
from make_reel import grad, paste_c

TW = 53.0
RED = (255, 110, 90)
_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=68):
    l = label(txt, size, col); comp(frame, l, 540 - l.width / 2, y)

def lab_at(frame, txt, x, y, col=WHITE, size=52):
    l = label(txt, size, col); comp(frame, l, x - l.width / 2, y - l.height / 2)

def heavy_pos(T):
    # kid sags lower than normal: gravity is pulling harder
    return (540, 1010 + 6 * math.sin(T * 1.5), 420)

# ---------------------------------------------------------------- props
def scale_props(frame, d, T, sc):
    lt = T - sc["s"]
    # bathroom scale under the kid
    d.rounded_rectangle([360, 1235, 720, 1315], radius=24, fill=(235, 235, 245), outline=OUTL, width=6)
    v = 60 + 60 * ease_out(clamp((lt - 1.0) / 1.6))
    d.rounded_rectangle([450, 1250, 630, 1300], radius=10, fill=(30, 40, 50))
    lab_at(frame, f"{int(v)} KG", 540, 1275, (120, 255, 140) if v < 119 else RED, 40)
    if lt > 0.5: top_label(frame, "GRAVITY x2", 400, YEL, 90)

def blood_props(frame, d, T, sc):
    lt = T - sc["s"]
    top_label(frame, "BLOOD SINKS DOWN", 400, RED, 74)
    # falling blood drops beside the kid
    for k in range(6):
        for side in (250, 830):
            y = 700 + ((lt * 260 + k * 100) % 560)
            d.ellipse([side - 18, y - 18, side + 18, y + 18], fill=(220, 40, 60), outline=OUTL, width=4)
            d.polygon([(side - 14, y - 8), (side + 14, y - 8), (side, y - 40)], fill=(220, 40, 60))
    if lt > 3.4: lab_at(frame, "STAND UP SLOWLY", 540, 590, WHITE, 56)

GROUND = 1330
KID = 380
REST = GROUND - KID // 2 + 10
def jumper(x, t0, hpx, air, rep):
    def pos(T):
        lt = (T - t0) % rep if T > t0 else -1
        y = REST
        if 0 <= lt < air:
            q = lt / air; y = REST - hpx * 4 * q * (1 - q)
        return (x, y, KID)
    return pos

def jump_props(frame, d, T, sc):
    lt = T - sc["s"]
    d.rectangle([0, GROUND, W, GROUND + 8], fill=OUTL)
    # ghost kid (normal gravity) on the left, real kid on the right
    for x, hpx, air, txt, col in ((290, 300, 0.64, "EARTH: 50 CM", WHITE), (790, 150, 0.45, "x2: 25 CM", YEL)):
        cx, cy, B = jumper(x, sc["s"] + 0.6, hpx, air, 1.6)(T)
        spr = draw_char("kid", B, T, 0, False, (0, -0.3), 1)
        if x < 540:
            a = spr.split()[3].point(lambda v: v * 0.55); spr.putalpha(a)
        comp(frame, spr, cx - B / 2, cy - B / 2)
        lab_at(frame, txt, x, 1260 - 520, col, 56)
    top_label(frame, "JUMP HEIGHT", 400, WHITE, 70)

def drop_props(frame, d, T, sc):
    lt = T - sc["s"]
    top_label(frame, "HITS ~40% FASTER", 400, YEL, 74)
    q = ((lt - 0.4) % 1.6) / 1.6
    for x, g, col in ((300, 1.0, WHITE), (780, 2.0, YEL)):
        t = q * 1.6
        y = 620 + min(1.0, 0.5 * g * (t ** 2) / 1.0) * 640
        d.rounded_rectangle([x - 45, y - 80, x + 45, y + 80], radius=16, fill=(40, 44, 60), outline=OUTL, width=6)
        d.rounded_rectangle([x - 33, y - 64, x + 33, y + 58], radius=8, fill=(110, 180, 255))
        if y >= 1259:
            d.line([(x - 30, y - 50), (x + 10, y + 10), (x - 20, y + 50)], fill=WHITE, width=4)
        lab_at(frame, "1G" if g == 1 else "2G", x, 560, col, 60)
    d.rectangle([150, 1345, 930, 1360], fill=(150, 100, 70))

def six_props(frame, d, T, sc):
    lt = T - sc["s"]
    top_label(frame, "SIXES GET RARE", 400, YEL, 80)
    p = clamp((lt - 0.6) / 2.4)
    for R, peak, col, txt in ((780, 420, (255, 255, 255), "80 M"), (390, 210, YEL, "~40 M")):
        pts = []
        for i in range(int(40 * p) + 1):
            s = i / 40
            pts.append((150 + R * s, 1150 - peak * 4 * s * (1 - s)))
        if len(pts) > 1: d.line(pts, fill=col, width=8)
        if p >= 1: lab_at(frame, txt, 150 + R, 1200, col, 56)
    if p < 1:
        s = p
        d.ellipse([150 + 390 * s - 16, 1150 - 210 * 4 * s * (1 - s) - 16, 150 + 390 * s + 16,
                   1150 - 210 * 4 * s * (1 - s) + 16], fill=(200, 30, 40), outline=OUTL, width=4)

def wave_props(frame, d, T, sc):
    lt = T - sc["s"]
    top_label(frame, "WAVES ~40% FASTER", 400, YEL, 72)
    for row, (sp, y0, col) in enumerate(((1.0, 760, (120, 190, 240)), (1.41, 1000, (60, 140, 220)))):
        pts = [(x, y0 + 40 * math.sin(x / 90 - lt * 4 * sp)) for x in range(0, W + 20, 20)]
        d.line(pts, fill=col, width=14)
        lab_at(frame, "1G" if row == 0 else "2G", 110, y0 - 90, WHITE if row == 0 else YEL, 54)

def g_meter(frame, d, x, val, top, col, txt, sub):
    base = 1200
    hgt = max(20, 68 * val)
    d.rounded_rectangle([x - 60, base - 68 * 9.5, x + 60, base], radius=20, fill=(40, 40, 60), outline=OUTL, width=5)
    d.rounded_rectangle([x - 48, base - hgt, x + 48, base - 8], radius=14, fill=col)
    lab_at(frame, txt, x, base - hgt - 40, WHITE, 52)
    lab_at(frame, sub, x, base + 50, col, 40)

def pilot_props(frame, d, T, sc):
    lt = T - sc["s"]
    top_label(frame, "HOW MANY G CAN YOU TAKE?", 400, WHITE, 56)
    k = ease_out(clamp((lt - 0.4) / 2.0))
    g_meter(frame, d, 220, 2 * k, 0, YEL, "2G", "THIS DAY")
    if lt > 1.8: g_meter(frame, d, 540, 3.5 * ease_out(clamp((lt - 1.8) / 1.5)), 0, (120, 220, 255), "~3.5G", "RELAXED")
    if lt > 3.6: g_meter(frame, d, 860, 9 * ease_out(clamp((lt - 3.6) / 1.5)), 0, RED, "9G", "PILOTS")

def coaster_props(frame, d, T, sc):
    lt = T - sc["s"]
    # coaster track hill
    pts = [(x, 1180 - 380 * math.exp(-((x - 380) / 220) ** 2)) for x in range(0, W + 20, 20)]
    d.line(pts, fill=(255, 120, 80), width=14)
    q = clamp((lt - 0.6) / 2.2)
    cx = 200 + 500 * q
    cy = 1180 - 380 * math.exp(-((cx - 380) / 220) ** 2)
    d.rounded_rectangle([cx - 60, cy - 50, cx + 60, cy + 10], radius=14, fill=YEL, outline=OUTL, width=5)
    if lt > 2.4:
        d.rounded_rectangle([200, 600, 880, 720], radius=30, fill=(40, 30, 60), outline=OUTL, width=6)
        lab_at(frame, "UP TO ~3.5G", 540, 660, YEL, 66)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="weigh", s=4.0, e=11.0, bg="bedroom", clock="7:00 AM", props_after=scale_props, char="kid", pos=heavy_pos,
         narr="Gravity DOUBLES overnight. Your 60 KG body now reads 120 KG on the scale.", n_at=4.2,
         say="Who is SITTING on me?!", say_at=7.4, pitch=600, bubble_y=700),
    dict(id="blood", s=11.0, e=18.0, bg="bedroom", clock="7:05 AM", props=blood_props, char="kid", pos=heavy_pos,
         narr="Your BLOOD sinks toward your legs. Stand up too fast and you may feel DIZZY.", n_at=11.2),
    dict(id="jump", s=18.0, e=25.0, bg="day", clock="8:00 AM", props=jump_props,
         narr="Your best JUMP? Only HALF as high. Same push, double the pull.", n_at=18.2),
    dict(id="drop", s=25.0, e=32.0, bg="office", clock="10:00 AM", props=drop_props,
         narr="Drop your PHONE and it hits the floor about 40% FASTER. RIP screen.", n_at=25.2),
    dict(id="six", s=32.0, e=39.0, bg="stadium", clock="4:00 PM", props=six_props,
         narr="A cricket hit that flew 80 METRES lands ROUGHLY HALF as far.", n_at=32.2),
    dict(id="waves", s=39.0, e=46.0, bg="ocean", clock="6:00 PM", props=wave_props,
         narr="OCEAN WAVES of the same size race about 40% FASTER.", n_at=39.2),
    dict(id="pilot", s=46.0, e=TW, bg="night", clock="CAN YOU SURVIVE?", props=pilot_props,
         narr="Relaxed people handle about 3.5 G. Fighter PILOTS in g-suits feel 9 G. You'd survive, TIRED.",
         n_at=46.2),
    dict(id="twist", s=TW, e=60.0, bg="twist", clock="PLOT TWIST", twist=True, props=coaster_props,
         char="kid", pos=(780, 1000, 360),
         narr="Twist: you've felt MORE! A ROLLER COASTER can hit about 3.5 G, just for a few SECONDS.",
         n_at=TW + 0.2),
    dict(id="outro", s=60.0, e=65.0),
]

def intro_extra(frame, d, T):
    if T >= 1.7:
        y = 1400 + 40 * ease_out(clamp((T - 1.7) / 0.5))
        comp(frame, draw_char("kid", 360, T, 0, False, (0, 0.3), 1), 540 - 180, y - 180)

cfg = dict(
    total=65.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 480, 0.2, "pop"),
        (title([("GRAVITY", WHITE)], 170), 690, 0.75, "right"),
        (title([("DOUBLED", YEL)], 190), 870, 1.05, "pop"),
        (title([("FOR A DAY?", WHITE)], 130), 1040, 1.4, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Could ", WHITE), ("YOU", YEL), (" last", WHITE)], 96), 470, 0.15),
                      (title([("a 2G day?", WHITE)], 92), 600, 0.45)],
               row=[("kid", 1), ("uncle", 1), ("cat", 1), ("dog", 1), ("kid", "puff")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=32.0, melody=True),
           dict(t0=32.0, t1=46.0), dict(t0=46.0, t1=TW - 0.15, melody=True),
           dict(t0=TW + 2.0, t1=65.0, melody=True)],
    drones=[dict(t0=TW, dur=7.0, g=0.08)],
    fx=[("boom", 4.4, 0.3), ("tick", 5.2, 0.3), ("pop", 19.0, 0.25), ("crash", 26.6, 0.15), ("crowd", 32.2, 0.15),
        ("waves", 39.2, 0.25), ("heartbeat", 46.2, 0.2), ("whoosh", TW + 1.0, 0.4)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_gravity_doubled")
