#!/usr/bin/env python3
"""What if you were a chipkali (house gecko) for a day?
Facts: toes carry millions of microscopic hairs (setae), each ending in hundreds to thousands of tiny pads (spatulae);
grip by van der Waals forces, no glue; geckos peel toes to let go and attach/detach ~15 times a second while running
(UC Berkeley 2000, Autumn et al., Nature). Setae could in theory hold two 60 kg humans (RoundGlass Sustain, common
house gecko). Geckos struggle to stick to dry Teflon (University of Akron, Stark et al. 2012). No eyelids, they lick
their eyes clean (RoundGlass; Wikipedia Gecko). Up to 50 insects a day, gather at lights (RoundGlass). Drop tail,
it keeps wriggling, regrows in 6-12 months (RoundGlass); regrown lizard tails have a cartilage tube, not bone (ASU 2012).
Geckskin: index-card-sized pad holds ~700 lb (~318 kg) on smooth glass (UMass Amherst 2012).
Twist: house geckos are non-venomous (Animal Diversity Web via Africa Check), but geckos can carry Salmonella germs
even if they look clean (CDC), so food a gecko fell into should still be thrown out."""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, comp, paste_c, ease_back, ease_out, clamp, text_sprite

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=64):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

# ---------------------------------------------------------------- new character: a friendly house gecko (top view)
SKIN, SPOT, PAD, BELLY = (214, 198, 158), (178, 156, 116), (236, 222, 190), (232, 220, 186)

def gecko(B, T, talk=0.0, blink=False, look=(0, 0), state=1):
    """Top-down cartoon gecko, head up. state: 1 normal, "notail" tail dropped, "lick" tongue over the eye."""
    S = 2 * B
    L = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    u = S / 200.0
    lw = lambda w: max(1, int(round(w * u)))
    def EL(b, fill, w=2.6):
        d.ellipse([v * u for v in b], fill=fill, outline=OUTL if w else None, width=lw(w) if w else 0)
    def PG(pts, fill, w=2.6):
        d.polygon([(x * u, y * u) for x, y in pts], fill=fill, outline=OUTL if w else None, width=lw(w) if w else 0)
    def LN(pts, w=2.6, fill=OUTL):
        d.line([(x * u, y * u) for x, y in pts], fill=fill, width=lw(w), joint="curve")
    wig = math.sin(T * 5)
    # tail
    if state != "notail":
        pts_l, pts_r = [], []
        for i in range(9):
            q = i / 8
            y = 128 + 66 * q
            x = 100 + 14 * wig * q * q + 8 * math.sin(q * 3)
            wd = 11 * (1 - q) + 1.5
            pts_l.append((x - wd, y)); pts_r.append((x + wd, y))
        PG(pts_l + pts_r[::-1], SKIN)
        for q in (0.25, 0.5, 0.72):
            y = 128 + 66 * q; x = 100 + 14 * wig * q * q + 8 * math.sin(q * 3)
            EL((x - 4, y - 3, x + 4, y + 3), SPOT, w=0)
    else:
        PG([(90, 126), (110, 126), (104, 140), (96, 140)], SKIN)
    # legs with toe pads
    step = math.sin(T * 6)
    for sx, sy, fx, fy in ((-1, 82, 46, 64), (1, 82, 154, 64), (-1, 124, 46, 148), (1, 124, 154, 148)):
        ph = step * (1 if (sx * (1 if sy < 100 else -1)) > 0 else -1)
        fy2 = fy + 4 * ph
        kx = 100 + sx * 30
        LN([(100 + sx * 12, sy), (kx, sy + (-12 if sy < 100 else 10)), (fx, fy2)], 9.5, OUTL)
        LN([(100 + sx * 12, sy), (kx, sy + (-12 if sy < 100 else 10)), (fx, fy2)], 6.5, SKIN)
        for k in range(5):
            a = (-70 + 35 * k) * math.pi / 180
            base = -90 if sy < 100 else 90
            ang = math.radians(base) + a * 0.8 + (0 if sx < 0 else 0)
            ang = ang + (-0.5 if sx < 0 else 0.5)
            tx, ty = fx + 11 * math.cos(ang) * (1 if sx > 0 or True else -1), fy2 + 11 * math.sin(ang)
            LN([(fx, fy2), (tx, ty)], 4.0, OUTL); LN([(fx, fy2), (tx, ty)], 2.0, SKIN)
            EL((tx - 3.6, ty - 3.6, tx + 3.6, ty + 3.6), PAD, w=1.4)
    # body
    EL((78, 66, 122, 138), SKIN)
    EL((88, 78, 112, 130), BELLY, w=0)
    for x, y in ((84, 88), (114, 100), (86, 116), (113, 126)):
        EL((x - 4, y - 3, x + 4, y + 3), SPOT, w=0)
    # head
    EL((70, 18, 130, 80), SKIN)
    for x in (80, 120):
        r = 13
        if blink:
            d.arc([(x - r) * u, (40 - r * 0.6) * u, (x + r) * u, (40 + r * 0.6) * u], 20, 160, fill=OUTL, width=lw(3))
            continue
        EL((x - r, 40 - r, x + r, 40 + r), (238, 222, 120), w=2.4)
        px, py = x + look[0] * 4, 40 + look[1] * 4
        EL((px - 2.8, py - 9, px + 2.8, py + 9), (25, 20, 30), w=0)     # slit pupil
        EL((px - 6, py - 8, px - 2.5, py - 4), WHITE, w=0)
    EL((84, 60, 92, 66), (255, 150, 150), w=0); EL((108, 60, 116, 66), (255, 150, 150), w=0)
    if talk > 0.08:
        h = 3 + 9 * talk
        EL((92, 62, 108, 66 + h), (125, 28, 48), w=1.8)
    else:
        d.arc([88 * u, 56 * u, 112 * u, 70 * u], 20, 160, fill=OUTL, width=lw(2.6))
    if state == "lick":
        ph = clamp(0.5 + 0.8 * math.sin(T * 7))
        tip = (100 + 20 * ph, 64 - 30 * ph)
        LN([(100, 66), (104 + 10 * ph, 66 - 6 * ph), tip], 6.5, (230, 90, 110))
        EL((tip[0] - 4.5, tip[1] - 4.5, tip[0] + 4.5, tip[1] + 4.5), (230, 90, 110), w=1.2)
    return L.reduce(2)

_draw_orig = E.draw_char
def draw_char(kind, B, T, talk=0.0, blink=False, look=(0, 0), state=1):
    if kind == "gecko":
        return gecko(B, T, talk, blink, look, state)
    return _draw_orig(kind, B, T, talk, blink, look, state)
E.draw_char = draw_char

# ---------------------------------------------------------------- props
def wall_deco(d):
    # picture frame and a light switch board on the living-room wall
    d.rounded_rectangle([90, 520, 330, 700], radius=10, fill=(250, 240, 220), outline=OUTL, width=6)
    d.polygon([(110, 680), (180, 590), (240, 650), (280, 610), (310, 680)], fill=(110, 170, 110))
    d.ellipse([260, 545, 300, 585], fill=(255, 200, 80))
    d.rounded_rectangle([800, 980, 940, 1120], radius=10, fill=WHITE, outline=OUTL, width=5)
    for x in (830, 870, 910):
        d.rectangle([x - 8, 1020, x + 8, 1060], fill=(200, 200, 210), outline=OUTL, width=3)

def climb_pos(T):
    lt = T - 4.0
    return (540, 1230 - 45 * lt, 520)

def wall_props(frame, d, T, sc):
    if T - sc["s"] > 1.0: top_label(frame, "NO GLUE. NO SUCTION.", 380, YEL, 62)

def hairs_props(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy, r = 730, 900, 240
    g = ease_back(clamp((lt - 0.6) / 0.5))
    if g <= 0: return
    r = r * g
    d.line([(400, 1060), (cx - r * 0.7, cy + r * 0.7)], fill=OUTL, width=8)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(250, 238, 214), outline=OUTL, width=10)
    if g > 0.9:
        # rows of hairs, each splitting into tiny tips
        for row in range(4):
            y0 = cy - 150 + row * 85
            d.rectangle([cx - 200, y0 + 52, cx + 200, y0 + 64], fill=SKIN)
            for k in range(13):
                x = cx - 180 + k * 30
                if (x - cx) ** 2 + (y0 + 20 - cy) ** 2 > (r - 30) ** 2: continue
                sway = 3 * math.sin(T * 4 + k + row)
                d.line([(x, y0 + 54), (x + sway, y0 + 14)], fill=(150, 120, 90), width=4)
                for j in (-8, 0, 8):
                    d.line([(x + sway, y0 + 14), (x + sway + j, y0 + 2)], fill=(150, 120, 90), width=2)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=OUTL, width=10)
    if lt > 1.0: top_label(frame, "MILLIONS OF TINY HAIRS", 380, YEL, 60)

def ceiling(d, y=500):
    d.rectangle([0, y - 40, W, y], fill=(240, 232, 250))
    d.line([(0, y), (W, y)], fill=OUTL, width=6)

def hold_props(frame, d, T, sc):
    ceiling(d, 500)
    lt = T - sc["s"]
    if lt > 1.0: top_label(frame, "IN THEORY: 2 ADULTS", 380, YEL, 62)

def hold_after(frame, d, T, sc):
    lt = T - sc["s"]
    g = ease_out(clamp((lt - 2.2) / 0.6))
    if g <= 0: return
    for i, x in enumerate((400, 680)):
        y = 1150 + 300 * (1 - g) + 8 * math.sin(T * 2 + i)
        d.line([(540, 760), (x, y - 120)], fill=(120, 90, 60), width=7)
        comp(frame, _draw_orig("uncle", 280, T, 0, E.blink_at(T, i * 0.3), (0, -0.5),
             "hat" if i else 1), x - 140, y - 140)

def peel_pos(T):
    lt = T - 25.0
    x = -120 + (lt * 520) % 1320
    return (x, 1080, 440)

def peel_props(frame, d, T, sc):
    lt = T - sc["s"]
    # little sticky footprints blinking on and off behind the runner
    x0 = -120 + (lt * 520) % 1320
    for k in range(1, 7):
        x = x0 - k * 70
        if x < 0: continue
        a = max(0, 1 - k / 7)
        col = tuple(int(c * (1 - 0.4 * a) + 255 * 0.4 * a) for c in (206, 186, 236))
        y = 1080 + (40 if k % 2 else -40)
        d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=(250, 240, 200))
    if lt > 1.0: top_label(frame, "STICK + UNSTICK: 15x A SECOND", 380, YEL, 50)

def pan(d, x=540, y=1050, r=330):
    d.line([(x + r - 20, y + 40), (x + r + 260, y + 120)], fill=(60, 50, 50), width=46)
    d.ellipse([x - r, y - r, x + r, y + r], fill=(56, 56, 66), outline=OUTL, width=10)
    d.ellipse([x - r + 40, y - r + 40, x + r - 40, y + r - 40], fill=(40, 40, 48))
    d.arc([x - r + 80, y - r + 80, x + r - 80, y + r - 80], 200, 250, fill=(110, 110, 130), width=10)

def slide_pos(T):
    lt = T - 32.0
    y = 900 + 260 * ((lt * 0.55) % 1.0)
    return (540, y, 420)

def teflon_props(frame, d, T, sc):
    pan(d, 540, 1040, 330)
    lt = T - sc["s"]
    if lt > 1.0: top_label(frame, "DRY TEFLON = NO GRIP", 380, YEL, 62)

def eyes_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 1.0: top_label(frame, "NO EYELIDS", 380, YEL, 72)

def tubelight(d, T):
    d.rounded_rectangle([250, 470, 830, 520], radius=25, fill=(255, 255, 230), outline=OUTL, width=5)
    for k in range(3):
        rr = 30 + 20 * k
        d.rounded_rectangle([250 - rr, 470 - rr * 0.5, 830 + rr, 520 + rr * 0.5], radius=40, outline=(255, 255, 200), width=3)

def bugs(d, T, n, alive=1.0):
    for k in range(n):
        if k / n >= alive: continue
        x = 540 + 360 * math.sin(T * (0.8 + k * 0.11) + k * 1.9)
        y = 640 + 90 * math.sin(T * (1.2 + k * 0.07) + k)
        fl = 6 * math.sin(T * 40 + k)
        d.ellipse([x - 22, y - 34 - fl, x + 2, y - 4], fill=(220, 230, 255), outline=OUTL, width=3)
        d.ellipse([x - 2, y - 34 + fl, x + 22, y - 4], fill=(220, 230, 255), outline=OUTL, width=3)
        d.line([(x - 24, y), (x + 24, y)], fill=OUTL, width=10)

def bulb_props(frame, d, T, sc):
    lt = T - sc["s"]
    tubelight(d, T)
    bugs(d, T, 10, 1.0 - clamp((lt - 2.0) / 4.5))
    if lt > 1.0: top_label(frame, "UP TO 50 INSECTS A DAY", 380, YEL, 58)

def run_away(T):
    lt = T - 53.0
    if lt < 2.0: return (540, 1080, 520)
    return (540 + 260 * ease_out((lt - 2.0) / 1.2), 1080, 520)

def tail_state(T): return 1 if T - 53.0 < 2.0 else "notail"

def tail_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt >= 2.0:
        # the dropped tail, wriggling on its own
        x0, y0 = 300, 1190
        pts = []
        for i in range(12):
            q = i / 11
            pts.append((x0 - 90 + 180 * q, y0 + 26 * math.sin(T * 16 + q * 6) * (0.4 + q)))
        d.line(pts, fill=OUTL, width=34, joint="curve")
        d.line(pts, fill=SKIN, width=24, joint="curve")
        if lt > 2.3:
            for k in range(3):
                a = (T * 3 + k) % 1.0
                d.arc([x0 - 140 - 30 * a, y0 - 90 - 30 * a, x0 + 140 + 30 * a, y0 + 90 + 30 * a], 200 + k * 50,
                      230 + k * 50, fill=WHITE, width=5)
    if lt > 1.0 and lt < 4.0: top_label(frame, "DANGER? DROP IT!", 380, YEL, 66)
    if lt >= 4.0: top_label(frame, "REGROWS: 6-12 MONTHS", 380, YEL, 62)

def glass_props(frame, d, T, sc):
    lt = T - sc["s"]
    # a glass window with a small pad holding a big weight
    d.rectangle([140, 470, 940, 1300], fill=(200, 230, 250))
    d.rectangle([140, 470, 940, 1300], outline=OUTL, width=8)
    for k in range(3):
        d.line([(220 + k * 90, 520), (160 + k * 90, 640)], fill=WHITE, width=10)
    d.rectangle([470, 600, 610, 690], fill=(250, 230, 120), outline=OUTL, width=5)
    sw = 6 * math.sin(T * 1.5)
    d.line([(540, 690), (540 + sw, 900)], fill=(90, 70, 50), width=8)
    d.rounded_rectangle([400 + sw, 900, 680 + sw, 1120], radius=14, fill=(110, 110, 124), outline=OUTL, width=6)
    l = label("~300 KG", 64, WHITE); comp(frame, l, 540 + sw - l.width / 2, 975)
    if lt > 1.0: top_label(frame, "GECKSKIN (2012)", 380, YEL, 64)

def dal_props(frame, d, T, sc):
    x, y = 540, 1150
    d.ellipse([x - 300, y - 70, x + 300, y + 70], fill=(250, 196, 60), outline=OUTL, width=8)
    d.chord([x - 300, y - 200, x + 300, y + 200], 0, 180, fill=(236, 236, 244), outline=OUTL, width=8)
    d.ellipse([x - 260, y - 52, x + 260, y + 52], fill=(250, 196, 60))
    for dx in (-150, -40, 90, 180):
        d.ellipse([x + dx - 10, y - 18, x + dx + 10, y + 2], fill=(210, 140, 40))
    lt = T - sc["s"]
    if lt > 1.0: top_label(frame, "NOT POISON. STILL GERMS.", 380, YEL, 56)

def dal_after(frame, d, T, sc):
    # rim drawn again so the gecko peeks out from the bowl
    x, y = 540, 1150
    d.chord([x - 300, y - 200, x + 300, y + 200], 0, 180, fill=(236, 236, 244), outline=OUTL, width=8)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="wall", s=4.0, e=11.0, bg="living", clock="9 PM: WAKE UP", char="gecko", pos=climb_pos,
         props=wall_props, look=(0, -0.6),
         narr="You'd walk straight up WALLS and across the CEILING. No glue needed.", n_at=4.2,
         say="Floor is so BORING.", say_at=7.4, pitch=760, bubble_y=760),
    dict(id="hairs", s=11.0, e=18.0, bg="living", clock="ZOOM IN", char="gecko", pos=(300, 1080, 440),
         props=hairs_props, look=(0.8, -0.2),
         narr="Your toes carry MILLIONS of tiny HAIRS. Each splits into HUNDREDS of even tinier tips.",
         n_at=11.2),
    dict(id="hold", s=18.0, e=25.0, bg="living", clock="SUPER GRIP", char="gecko", pos=(540, 630, 300), rot=180,
         props=hold_props, props_after=hold_after, look=(0, 0.6),
         narr="They grip with weak ATOM-level forces. In theory, all of them could hold TWO adults.",
         n_at=18.2),
    dict(id="peel", s=25.0, e=32.0, bg="living", clock="RUN!", char="gecko", pos=peel_pos, rot=-90,
         props=peel_props, look=(0, -0.6),
         narr="To let go, you PEEL your toes like tape. Running, you stick and unstick 15 TIMES a second.",
         n_at=25.2),
    dict(id="teflon", s=32.0, e=39.0, bg="living", clock="KITCHEN", char="gecko", pos=slide_pos,
         rot=lambda T: 8 * math.sin(T * 5), props=teflon_props, look=(0, 0.5),
         narr="Your one enemy: a dry TEFLON non-stick pan. Geckos can barely grip it.", n_at=32.2,
         say="I'm SLIDING!", say_at=35.4, pitch=800, bubble_y=740),
    dict(id="eyes", s=39.0, e=46.0, bg="living", clock="NO BLINKING", char="gecko", pos=(540, 1060, 600),
         state=lambda T: "lick" if (T - 39.0) > 3.4 else 1, props=eyes_props, look=(0, 0),
         narr="No EYELIDS either. To clean your eyes, you just LICK them.", n_at=39.2,
         say="Slurp! All CLEAN.", say_at=42.6, pitch=760, bubble_y=740),
    dict(id="bulb", s=46.0, e=53.0, bg="bedroom", clock="NIGHT SHIFT", char="gecko", pos=(540, 1080, 500),
         props=bulb_props, look=(0, -0.7),
         narr="Your night job: guard the TUBELIGHT. One gecko can eat up to 50 INSECTS a day.", n_at=46.2),
    dict(id="tail", s=53.0, e=60.0, bg="living", clock="EMERGENCY", char="gecko", pos=run_away, state=tail_state,
         props=tail_props, look=(0.6, 0),
         narr="Danger? DROP your tail. It keeps WRIGGLING while you escape, and grows back in MONTHS.",
         n_at=53.2),
    dict(id="glass", s=60.0, e=67.0, bg="office", clock="COPIED BY HUMANS", char="gecko", pos=(860, 1150, 300),
         props=glass_props, look=(-0.7, -0.3),
         narr="Scientists copied your feet: an index-card pad that held about 300 KG on GLASS.", n_at=60.2,
         say="My IDEA!", say_at=63.6, pitch=780, bubble_y=760),
    dict(id="twist", s=67.0, e=75.0, bg="twist", clock="PLOT TWIST", char="gecko", pos=(540, 1040, 420),
         props=dal_props, props_after=dal_after, twist=True, look=(0, -0.3),
         narr="Twist: a chipkali in your DAL is NOT poison. But it can carry SALMONELLA germs. Throw it out!",
         n_at=67.2, say="Not POISON. Still YUCK.", say_at=70.8, pitch=760, bubble_y=700),
    dict(id="outro", s=75.0, e=80.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back(clamp((T - 1.9) / 0.4))
        if p > 0.05: paste_c(frame, gecko(420, T, 0, False, (0, -0.2)), 540, 1470, p)

cfg = dict(
    total=80.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 520, 0.2, "pop"),
        (title([("YOU WERE A", WHITE)], 140), 720, 0.75, "right"),
        (title([("CHIPKALI", YEL)], 190), 880, 1.05, "pop"),
        (title([("FOR A DAY?", WHITE)], 130), 1040, 1.5, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" swap", WHITE)], 100), 470, 0.15),
                      (title([("with a chipkali?", YEL)], 96), 600, 0.45)],
               row=[("gecko", 1), ("mosquito", 1), ("kid", 1), ("uncle", 1), ("gecko", 1)],
               note=text_sprite([("If a lizard falls in food, ", WHITE), ("throw the food away.", YEL)], 40, stroke=6)),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=32.0, melody=True),
           dict(t0=32.0, t1=39.0, drums=False, minor=True), dict(t0=39.0, t1=53.0, melody=True),
           dict(t0=53.0, t1=60.0, drums=False, minor=True), dict(t0=60.0, t1=66.85, melody=True),
           dict(t0=75.0, t1=80.0, melody=True)],
    drones=[dict(t0=67.2, dur=7.5, g=0.05)],
    fx=[("pop", 5.0, 0.4), ("whoosh", 11.8, 0.4), ("ding", 13.0, 0.3), ("pop", 20.4, 0.5), ("pop", 20.7, 0.5),
        ("click", 26.0, 0.6), ("click", 26.4, 0.6), ("click", 26.8, 0.6), ("click", 27.2, 0.6),
        ("screech", 33.0, 0.3), ("whoosh", 34.8, 0.4), ("pop", 43.0, 0.5),
        ("click", 48.6, 0.7), ("click", 49.4, 0.7), ("click", 50.3, 0.7), ("click", 51.2, 0.7),
        ("pop", 55.0, 0.7), ("whoosh", 55.2, 0.6), ("ding", 64.0, 0.3), ("splash", 67.6, 0.4)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_were_a_chipkali_for_a_day")
