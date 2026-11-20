#!/usr/bin/env python3
"""What if you were a cheetah for a day? Facts: cheetahs hunt mainly by day, early morning and late afternoon, unlike
most cats (Smithsonian National Zoo; Cheetah Conservation Fund). Top speed: popular estimates ~100-110 km/h (CCF,
Smithsonian); fastest measured in the wild 25.9 m/s = 93 km/h over 367 runs by 5 wild cheetahs in Botswana (Wilson
et al. 2013, Nature 498:185). Can gain up to ~3 m/s (~10 km/h) in a single stride (Wilson et al. 2013 via UPI /
ScienceDaily). Stride about 6-7 m, up to 4 strides a second (CCF). Average hunting run 173 m; longest runs 407-559 m
(Wilson et al. 2013, ScienceDaily). Semi-retractable blunt claws grip "like track spikes"; long tail works as a
rudder/counterbalance (CCF, Smithsonian). Black tear marks may reduce sun glare (CCF). Cheetahs can't roar; they purr,
chirp, bark, growl and hiss (Smithsonian, CCF). Lose about 1 in 10 kills to lions and hyenas (Scantlebury et al. 2014,
Science, via National Geographic). India declared the cheetah extinct in 1952; 8 cheetahs from Namibia were released
in Kuno National Park on 17 Sept 2022 (PIB). Twist: severe genetic bottleneck in the last Ice Age (CCF); O'Brien et
al. 1985 (Science): all skin grafts swapped between unrelated cheetahs were accepted (CCF resource library)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, comp, ease_back, ease_out, clamp, text_sprite
from make_reel import grad, paste_c

TW = 53.0
FUR, FUR_L, SPOT = (238, 186, 92), (252, 236, 196), (60, 40, 32)

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

BODY_SPOTS = [(58, 100), (74, 92), (92, 98), (110, 92), (128, 100), (66, 118), (84, 112), (102, 120), (120, 114),
              (138, 118), (52, 126), (96, 106), (116, 130), (78, 132), (144, 104)]
HEAD_SPOTS = [(146, 56), (158, 52), (170, 56), (140, 66)]

def cheetah(B, T, talk=0.0, blink=False, look=(0, 0), state=1):
    """Side-view cartoon cheetah facing right. state: 1 = standing, "run" = galloping, "sit" = sitting purr."""
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
    run = state == "run"
    ph = T * 16
    # tail
    wag = 8 * math.sin(T * 3)
    tail = [(46, 108), (28, 104), (14, 92 + wag * 0.5), (8, 76 + wag)] if not run else \
           [(46, 104), (26, 98), (10, 96 + 6 * math.sin(ph)), (-2, 92 + 8 * math.sin(ph + 1))]
    tail = [(x + 6, y) for x, y in tail]
    LN(tail, 12); LN(tail, 7.5, FUR)
    tx, ty = tail[-1]
    for k in range(3):
        px = tail[-1][0] + (tail[-2][0] - tail[-1][0]) * k * 0.28
        py = tail[-1][1] + (tail[-2][1] - tail[-1][1]) * k * 0.28
        EL((px - 3.4, py - 3.4, px + 3.4, py + 3.4), SPOT, w=0)
    # legs (back pair drawn darker, behind)
    hips = [(68, 126, 0.0, True), (138, 124, 2.4, True), (82, 128, 3.14, False), (150, 126, 5.5, False)]
    for hx, hy, off, back in hips:
        if run:
            fx = hx + 22 * math.sin(ph + off); fy = 182 - 10 * max(0.0, math.cos(ph + off))
        elif state == "sit" and hx < 100:
            fx, fy = hx + 18, 182
        else:
            fx, fy = hx + (2 if back else -2), 184
        col = (214, 160, 74) if back else FUR
        LN([(hx, hy), ((hx + fx) / 2, (hy + fy) / 2 + 2), (fx, fy)], 12)
        LN([(hx, hy), ((hx + fx) / 2, (hy + fy) / 2 + 2), (fx, fy)], 7.5, col)
        EL((fx - 6, fy - 4, fx + 7, fy + 5), col, w=2.0)
    # body
    if state == "sit":
        PG([(46, 150), (60, 102), (150, 80), (166, 112), (150, 150)], FUR)
    else:
        EL((40, 84, 162, 142), FUR)
    EL((70, 120, 140, 142), FUR_L, w=0)
    for x, y in BODY_SPOTS:
        if state == "sit" and x < 60: continue
        EL((x - 3.6, y - 3.2, x + 3.6, y + 3.2), SPOT, w=0)
    # head
    hb = -6 if state == "sit" else 0
    EL((132, 42 + hb, 190, 100 + hb), FUR)
    for ex, ey in ((142, 46 + hb), (174, 42 + hb)):
        EL((ex - 9, ey - 9, ex + 9, ey + 9), FUR)
        EL((ex - 4.5, ey - 4.5, ex + 4.5, ey + 4.5), SPOT, w=0)
    for x, y in HEAD_SPOTS:
        EL((x - 2.4, y + hb - 2.4, x + 2.4, y + hb + 2.4), SPOT, w=0)
    EL((156, 74 + hb, 196, 100 + hb), FUR_L, w=2.0)
    EL((186, 72 + hb, 196, 81 + hb), SPOT, w=0)   # nose
    for x in (152, 174):
        r = 7.5; y = 68 + hb
        if blink:
            d.arc([(x - r) * u, (y - r * 0.7) * u, (x + r) * u, (y + r * 0.7) * u], 200, 340, fill=OUTL,
                  width=lw(2.6))
        else:
            EL((x - r, y - r * 1.1, x + r, y + r * 1.1), WHITE, w=2.0)
            px, py = x + 2.5 + look[0] * 3, y + look[1] * 3
            EL((px - 3.6, py - 4.2, px + 3.6, py + 4.2), (25, 20, 30), w=0)
            EL((px - 3, py - 3.6, px - 0.6, py - 1.4), WHITE, w=0)
        # tear marks
        LN([(x - 1, y + 8), (x + 3, y + 18), (x + 8, y + 26)], 3.2, SPOT)
    if talk > 0.08:
        h = 3 + 10 * talk
        EL((176, 88 + hb, 194, 92 + hb + h), (125, 28, 48), w=1.8)
    else:
        d.arc([174 * u, 84 * u + hb * u, 194 * u, 98 * u + hb * u], 20, 160, fill=OUTL, width=lw(2.4))
    EL((150, 84 + hb, 160, 90 + hb), (255, 150, 150), w=0)
    return L.reduce(2)

_draw_orig = E.draw_char
def draw_char(kind, B, T, talk=0.0, blink=False, look=(0, 0), state=1):
    if kind == "cheetah":
        return cheetah(B, T, talk, blink, look, state)
    return _draw_orig(kind, B, T, talk, blink, look, state)
E.draw_char = draw_char

def mini(frame, kind, x, y, size, T, state=1, look=(0, 0.2), talk=0.0, flip=False):
    size = max(2, int(size))
    spr = draw_char(kind, size, T, talk, False, look, state)
    if flip: spr = spr.transpose(Image.FLIP_LEFT_RIGHT)
    comp(frame, spr, x - size / 2, y - size / 2)

# ---------------------------------------------------------------- backgrounds
_bgc = {}
def savanna(kind="day"):
    if kind in _bgc: return _bgc[kind]
    sky = {"day": [(0, (110, 190, 250)), (0.62, (255, 226, 160)), (1, (255, 226, 160))],
           "dawn": [(0, (120, 110, 200)), (0.45, (255, 150, 120)), (0.62, (255, 210, 140)), (1, (255, 210, 140))]}[kind]
    img = grad(sky, W, H); d = ImageDraw.Draw(img)
    sx, sy = (800, 560) if kind == "day" else (300, 1120)
    d.ellipse([sx - 90, sy - 90, sx + 90, sy + 90], fill=(255, 236, 150))
    d.rectangle([0, 1180, W, H], fill=(214, 170, 92))
    d.polygon([(0, 1180), (300, 1150), (620, 1175), (1080, 1140), (1080, 1200), (0, 1200)], fill=(196, 150, 78))
    # acacia tree
    d.line([(150, 1180), (170, 1000), (120, 900)], fill=(110, 76, 50), width=22)
    d.line([(170, 1000), (230, 910)], fill=(110, 76, 50), width=16)
    d.ellipse([20, 840, 330, 940], fill=(98, 140, 70))
    rng = np.random.default_rng(3)
    for x, y in zip(rng.uniform(0, W, 60), rng.uniform(1200, H, 60)):
        d.line([(x, y), (x - 6, y - 24)], fill=(180, 136, 66), width=4)
        d.line([(x, y), (x + 8, y - 20)], fill=(180, 136, 66), width=4)
    _bgc[kind] = img
    return img

def bg_day(T): return savanna("day")
def bg_dawn(T): return savanna("dawn")

def speed_lines(d, T, y0=820, y1=1300):
    for k in range(9):
        y = y0 + (y1 - y0) * k / 8
        x = (1300 - (T * 2400 + k * 377) % 1600)
        d.line([(x, y), (x + 220, y)], fill=WHITE, width=8)

def gauge(d, frame, cx, cy, r, frac, txt):
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=(40, 40, 60), outline=OUTL, width=6)
    for k in range(11):
        a = math.pi + math.pi * k / 10
        d.line([(cx + 0.8 * r * math.cos(a), cy + 0.8 * r * math.sin(a)),
                (cx + 0.95 * r * math.cos(a), cy + 0.95 * r * math.sin(a))], fill=WHITE, width=5)
    a = math.pi + math.pi * clamp(frac)
    d.line([(cx, cy), (cx + 0.8 * r * math.cos(a), cy + 0.8 * r * math.sin(a))], fill=(255, 90, 80), width=12)
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=WHITE, outline=OUTL, width=4)
    lab_at(frame, txt, cx, cy + 50, YEL, 64)

# ---------------------------------------------------------------- props
def wake_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 1.0: top_label(frame, "HUNT BY DAY", 400, YEL, 80)
    if lt > 2.6: lab_at(frame, "MORNING + LATE AFTERNOON", 540, 600, WHITE, 50)

def run_pos(T):
    return (540 + 20 * math.sin(T * 2), 1060, 640)

def speed_props(frame, d, T, sc):
    lt = T - sc["s"]
    speed_lines(d, T)
    v = 93 * ease_out(clamp((lt - 0.4) / 2.6))
    gauge(d, frame, 540, 720, 190, v / 120, f"{int(v)} KM/H")
    if lt > 3.4: top_label(frame, "MEASURED IN THE WILD", 370, WHITE, 54)

def stride_props(frame, d, T, sc):
    lt = T - sc["s"]
    speed_lines(d, T)
    if lt > 0.5: top_label(frame, "+10 KM/H IN ONE STRIDE", 400, YEL, 64)
    if lt > 2.6: lab_at(frame, "STRIDE: UP TO 7 M", 540, 590, WHITE, 58)
    if lt > 4.2: lab_at(frame, "4 STRIDES A SECOND", 540, 700, WHITE, 58)

def gear_props(frame, d, T, sc):
    lt = T - sc["s"]
    top_label(frame, "BUILT FOR SPEED", 400, WHITE, 68)
    items = [(0.6, "SPIKE CLAWS", 800, 1335), (2.0, "TAIL = RUDDER", 270, 700), (3.4, "TEAR MARKS", 820, 640)]
    for t0, txt, x, y in items:
        if lt > t0:
            p = ease_back(clamp((lt - t0) / 0.35))
            l = label(txt, 52, YEL)
            paste_c(frame, l, x, y, 0.3 + 0.7 * p)

def chase_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_out(clamp((lt - 0.3) / 3.0))
    # track
    d.rounded_rectangle([120, 640, 960, 700], radius=30, fill=(40, 40, 60), outline=OUTL, width=6)
    d.rounded_rectangle([128, 648, 128 + 824 * p, 692], radius=22, fill=YEL)
    lab_at(frame, f"{int(173 * p)} M", 540, 580, YEL, 72)
    top_label(frame, "AVERAGE CHASE", 400, WHITE, 64)
    if lt > 3.6: lab_at(frame, "PHEW... REST TIME", 540, 800, WHITE, 56)

def chase_state(T):
    return "run" if T - 32.0 < 3.4 else 1

def voice_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 0.6: top_label(frame, "NO ROAR!", 400, (255, 120, 80), 90)
    if lt > 4.6: lab_at(frame, "purrrr", 300, 900, WHITE, 52)

def india_props(frame, d, T, sc):
    lt = T - sc["s"]
    top_label(frame, "BACK IN INDIA", 400, WHITE, 70)
    if lt > 0.6: lab_at(frame, "1952: GONE", 540, 610, (255, 120, 80), 72)
    if lt > 2.8: lab_at(frame, "2022: 8 ARRIVE AT KUNO", 540, 730, YEL, 62)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 1.2:
        d.rounded_rectangle([170, 1230, 910, 1340], radius=30, fill=(40, 30, 60), outline=OUTL, width=6)
        lab_at(frame, "ALMOST LIKE TWINS", 540, 1285, YEL, 60)

def twist_extra(frame, d, T, sc):
    twist_props(frame, d, T, sc)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="wake", s=4.0, e=11.0, bg_fn=bg_dawn, clock="6:30 AM", props=wake_props, char="cheetah",
         pos=(540, 1060, 600), narr="You wake up as a CHEETAH. Unlike most cats, you hunt by DAY.", n_at=4.2,
         narr_y=1530),
    dict(id="speed", s=11.0, e=18.0, bg_fn=bg_day, clock="TOP SPEED", props=speed_props, char="cheetah",
         state="run", pos=run_pos, narr="Your top speed is about 100 KM/H. In the wild, 93 KM/H was measured.",
         n_at=11.2, narr_y=1530),
    dict(id="stride", s=18.0, e=25.0, bg_fn=bg_day, clock="ACCELERATION", props=stride_props, char="cheetah",
         state="run", pos=run_pos, narr="One STRIDE can add about 10 KM/H. Each one is up to 7 METRES long.",
         n_at=18.2, narr_y=1530),
    dict(id="gear", s=25.0, e=32.0, bg_fn=bg_day, clock="YOUR GEAR", props=gear_props, char="cheetah",
         pos=(540, 1000, 640), narr="CLAWS grip like spikes, your TAIL steers, TEAR MARKS may cut glare.",
         n_at=25.2, narr_y=1530),
    dict(id="chase", s=32.0, e=39.0, bg_fn=bg_day, clock="THE CHASE", props=chase_props, char="cheetah",
         state=chase_state, pos=(540, 1060, 560),
         narr="But chases are SHORT: on average just 173 METRES. Then you need a REST.", n_at=32.2,
         narr_y=1530),
    dict(id="voice", s=39.0, e=46.0, bg_fn=bg_dawn, clock="SAY SOMETHING", props=voice_props, char="cheetah",
         state="sit", pos=(540, 1060, 600), narr="And you CAN'T ROAR. You PURR and CHIRP like a bird!", n_at=39.2,
         narr_y=1530, say="chirp chirp!", say_at=42.6, pitch=900, bubble_y=760),
    dict(id="india", s=46.0, e=TW, bg_fn=bg_day, clock="INDIA", props=india_props, char="cheetah",
         pos=(540, 1060, 560), narr="India lost its cheetahs by 1952. In 2022, 8 came from NAMIBIA to KUNO.",
         n_at=46.2, narr_y=1530),
    dict(id="twist", s=TW, e=60.0, bg="twist", clock="PLOT TWIST", twist=True, char="cheetah", state="sit",
         pos=(540, 980, 520), props_after=twist_extra,
         narr="Twist: cheetahs are so alike, skin grafts between UNRELATED cheetahs were all ACCEPTED!",
         n_at=TW + 0.2, narr_y=1530),
    dict(id="outro", s=60.0, e=65.0),
]

def intro_extra(frame, d, T):
    if T >= 1.7:
        x = 1300 - 760 * ease_out(clamp((T - 1.7) / 0.8))
        st = "run" if T < 2.6 else 1
        mini(frame, "cheetah", x, 1430, 460, T, st)
        if T < 2.6: speed_lines(d, T, 1300, 1560)

cfg = dict(
    total=65.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 480, 0.2, "pop"),
        (title([("YOU WERE A", WHITE)], 130), 690, 0.75, "right"),
        (title([("CHEETAH", YEL)], 190), 860, 1.05, "pop"),
        (title([("FOR A DAY?", WHITE)], 130), 1030, 1.4, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" trade", WHITE)], 96), 470, 0.15),
                      (title([("a roar for speed?", WHITE)], 92), 600, 0.45)],
               row=[("cheetah", 1), ("cat", 1), ("kid", 1), ("dog", 1), ("cheetah", "sit")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=32.0, melody=True),
           dict(t0=32.0, t1=46.0), dict(t0=46.0, t1=TW - 0.15, melody=True),
           dict(t0=TW + 2.0, t1=65.0, melody=True)],
    drones=[dict(t0=TW, dur=7.0, g=0.08)],
    fx=[("whoosh", 1.8, 0.4), ("whoosh", 11.3, 0.4), ("whoosh", 18.5, 0.35), ("pop", 25.8, 0.3),
        ("pop", 27.2, 0.3), ("pop", 28.6, 0.3), ("screech", 35.6, 0.15), ("pop", 40.0, 0.3),
        ("ding", 49.2, 0.2), ("pop", TW + 1.4, 0.25)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_were_a_cheetah")
