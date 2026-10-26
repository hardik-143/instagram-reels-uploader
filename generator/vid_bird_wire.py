#!/usr/bin/env python3
"""What if you were a bird on a power line? Birds on one wire are safe because both feet sit at the same potential, so
almost no current flows (Wikipedia: Live-line working; general physics). Many Indian street (HT distribution) lines run
at 11 kV; home supply is 230 V, 50 Hz (IEEE RO-MAN 2019 India guide); 11,000/230 ~ 48x. Touching two wires, or a wire
and an earthed pole, lets current flow through the body. WWF-India: more than 130 raptors (Himalayan vultures, steppe
eagles) electrocuted 2014-2019 along 4 km of Langha Road near Dehradun; wires insulated April 2025, no raptor
electrocutions recorded there since. India's highest AC transmission level: 765 kV. Twist: bare-hand live-line work,
linemen in Faradays suits of conductive fibre bond to the line and share its potential, like birds (Wikipedia).
Safety: metal-coated manja conducts; never retrieve kites from lines (BSES/Tata Power-DDL advisories via ThePrint)."""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

TW = 51.0      # twist start
PX = 400       # pigeon x on the wire
W1, W2 = 1180, 1290   # wire heights at centre
SAG = 40

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def put_label(frame, txt, cx, y, size=56, col=YEL):
    l = label(txt, size, col)
    comp(frame, l, cx - l.width / 2, y)

def wy(x, base):
    """Height of a sagging wire at x (poles at x=60 and x=1020)."""
    u = (x - 540) / 480.0
    return base - SAG * u * u

def draw_wires(d, cover=False):
    for base in (W1, W2):
        pts = [(x, wy(x, base)) for x in range(40, 1041, 20)]
        if cover:
            d.line(pts, fill=OUTL, width=26)
            d.line(pts, fill=(60, 130, 220), width=18)
        else:
            d.line(pts, fill=OUTL, width=9)
            d.line(pts, fill=(90, 90, 100), width=5)

_bgc = {}
def wire_bg(cover=False, sky="day"):
    k = (cover, sky)
    if k not in _bgc:
        img = E.bg(sky).copy()
        d = ImageDraw.Draw(img)
        for x in (60, 1020):
            d.rectangle([x - 18, 1080, x + 18, 1700], fill=(130, 120, 110), outline=OUTL, width=5)
            d.rectangle([x - 60, wy(x, W1) - 14, x + 60, wy(x, W1) + 8], fill=(120, 100, 80), outline=OUTL, width=4)
            d.rectangle([x - 60, wy(x, W2) - 14, x + 60, wy(x, W2) + 8], fill=(120, 100, 80), outline=OUTL, width=4)
        draw_wires(d, cover)
        _bgc[k] = img
    return _bgc[k]

def feet(d, x, y):
    for dx in (-30, 30):
        d.line([(x + dx, y - 26), (x + dx, y)], fill=OUTL, width=12)
        d.line([(x + dx, y - 26), (x + dx, y)], fill=(240, 140, 60), width=6)
        d.ellipse([x + dx - 16, y - 8, x + dx + 16, y + 8], fill=(240, 140, 60), outline=OUTL, width=3)

def pig_on(x, B):
    return (x, wy(x, W1) - 0.36 * B - 20, B)

def spark(d, x, y, T, r=60):
    for k in range(6):
        a = k * math.pi / 3 + T * 9
        pts = [(x, y)]
        for j in range(1, 4):
            rr = r * j / 3
            pts.append((x + rr * math.cos(a) + (12 if j % 2 else -12) * math.sin(a),
                        y + rr * math.sin(a) + (12 if j % 2 else -12) * math.cos(a)))
        d.line(pts, fill=(255, 240, 90), width=8)

def flash(period=0.9, on=0.12, g=0.55, t0=0.0):
    def ov(frame, T, sc):
        lt = T - sc["s"]
        if lt > t0 and ((lt - t0) % period) < on:
            return Image.blend(frame, Image.new("RGBA", (W, H), (255, 255, 230, 255)), g)
        return frame
    return ov

# ----------------------------------------------------------------- props
def perch_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 1.0: put_label(frame, "11,000 VOLTS", 790, 1020, 50)

def perch_after(frame, d, T, sc):
    feet(d, PX, wy(PX, W1))

def same_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 0.8:
        put_label(frame, "BOTH FEET: 11,000 V", 760, 960, 42, WHITE)
    if lt > 2.0: put_label(frame, "DIFFERENCE: 0", 780, 1040, 54)

def same_after(frame, d, T, sc):
    feet(d, PX, wy(PX, W1))

def home_props(frame, d, T, sc):
    lt = T - sc["s"]
    cx, cy = 700, 950
    d.rounded_rectangle([cx - 110, cy - 110, cx + 110, cy + 110], 24, fill=(250, 250, 250), outline=OUTL, width=6)
    for dx in (-40, 40):
        d.ellipse([cx + dx - 16, cy - 30, cx + dx + 16, cy + 2], fill=(60, 60, 60))
    d.ellipse([cx - 18, cy + 30, cx + 18, cy + 66], fill=(60, 60, 60))
    put_label(frame, "230 V", cx, 1075, 56, WHITE)
    if lt > 2.0: put_label(frame, "WIRE: 48x MORE", cx, 1150, 50)

def two_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_out(clamp((lt - 1.2) / 0.8))
    # wing stretching down to the lower wire
    x0, y0 = PX + 60, 1140
    x1, y1 = x0 + 200 * p, y0 + (wy(x0 + 200, W2) - y0) * p
    d.polygon([(x0 - 10, y0 - 30), (x1, y1), (x0 + 40, y0 + 30)], fill=(150, 160, 200), outline=OUTL)
    if p >= 1:
        spark(d, x1, y1, T, 70)
        put_label(frame, "CURRENT FLOWS!", 770, 980, 46)

def two_after(frame, d, T, sc):
    feet(d, PX, wy(PX, W1))

def vulture(d, cx, cy, T):
    body = (90, 60, 45); wing = (60, 40, 30)
    # left wing up to the top wire, right wing down to the lower wire
    lx, ly = 280, wy(280, W1) - 4
    rx, ry = 860, wy(860, W2) + 4
    d.polygon([(cx - 40, cy - 30), (lx + 40, ly - 50), (lx, ly), (lx + 60, ly + 30), (cx - 30, cy + 30)],
              fill=wing, outline=OUTL)
    d.polygon([(cx + 40, cy - 30), (rx - 60, ry - 40), (rx, ry), (rx - 40, ry + 40), (cx + 30, cy + 30)],
              fill=wing, outline=OUTL)
    d.ellipse([cx - 70, cy - 60, cx + 70, cy + 70], fill=body, outline=OUTL, width=5)
    d.ellipse([cx - 40, cy - 130, cx + 40, cy - 50], fill=(230, 200, 180), outline=OUTL, width=5)  # bare pale head
    d.polygon([(cx + 30, cy - 95), (cx + 70, cy - 85), (cx + 30, cy - 70)], fill=(250, 200, 80), outline=OUTL)
    d.ellipse([cx + 4, cy - 104, cx + 18, cy - 90], fill=OUTL)
    if (T % 0.9) < 0.5:
        spark(d, lx, ly, T, 50); spark(d, rx, ry, T, 50)
    return lx, ly, rx, ry

def vulture_props(frame, d, T, sc):
    vulture(d, 600, 1220, T)
    put_label(frame, "130+ BIRDS, 4 KM", 680, 900, 54)

def fix_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 1.0: put_label(frame, "COVERED WIRES", 790, 1020, 50)

def fix_after(frame, d, T, sc):
    feet(d, PX, wy(PX, W1))

def pylon(d, cx, base, h, w):
    top = base - h
    L = [(cx - w / 2, base), (cx - w / 8, top)]; R = [(cx + w / 2, base), (cx + w / 8, top)]
    col = (150, 155, 165)
    d.line(L, fill=OUTL, width=14); d.line(L, fill=col, width=8)
    d.line(R, fill=OUTL, width=14); d.line(R, fill=col, width=8)
    for k in range(6):
        t1, t2 = k / 6, (k + 1) / 6
        xa = cx - w / 2 + (w / 2 - w / 8) * t1; xb = cx + w / 2 - (w / 2 - w / 8) * t2
        ya = base - h * t1; yb = base - h * t2
        d.line([(xa, ya), (xb, yb)], fill=col, width=5)
        d.line([(2 * cx - xa, ya), (2 * cx - xb, yb)], fill=col, width=5)
    for ay, aw in ((top + 60, w * 0.9), (top + 170, w * 1.1)):
        d.rectangle([cx - aw / 2, ay - 8, cx + aw / 2, ay + 8], fill=col, outline=OUTL, width=4)
        for sx in (cx - aw / 2 + 10, cx + aw / 2 - 10):
            d.line([(sx, ay), (sx, ay + 50)], fill=(240, 240, 250), width=10)

def big_bg(T=0):
    k = "big"
    if k not in _bgc:
        img = E.bg("speed").copy(); d = ImageDraw.Draw(img)
        pylon(d, 720, 1330, 540, 300)
        for ay, aw in ((1330 - 540 + 110, 270), (1330 - 540 + 220, 330)):
            for sx in (720 - aw / 2 + 10, 720 + aw / 2 - 10):
                d.line([(0, ay + 30), (sx, ay + 50), (W, ay + 30)], fill=OUTL, width=5)
        _bgc[k] = img
    return _bgc[k]

def big_props(frame, d, T, sc):
    put_label(frame, "765,000 VOLTS", 560, 1250, 64)

def suit_props(frame, d, T, sc):
    cx = 640
    d.rounded_rectangle([cx - 120, 1110, cx + 120, 1360], 40, fill=(200, 205, 215), outline=OUTL, width=6)
    for k in range(1, 6):
        d.line([(cx - 120 + k * 40, 1115), (cx - 120 + k * 40, 1355)], fill=(160, 165, 180), width=3)
        d.line([(cx - 115, 1110 + k * 42), (cx + 115, 1110 + k * 42)], fill=(160, 165, 180), width=3)
    d.line([(cx + 100, 1150), (cx + 230, wy(cx + 230, W1) - 4)], fill=OUTL, width=30)
    d.line([(cx + 100, 1150), (cx + 230, wy(cx + 230, W1) - 4)], fill=(200, 205, 215), width=20)
    put_label(frame, "SAME VOLTAGE", 870, 950, 40)

def kite_props(frame, d, T, sc):
    lt = T - sc["s"]
    kx, ky = 780, wy(780, W1) - 60
    sw = 6 * math.sin(T * 3)
    d.polygon([(kx, ky - 90), (kx + 70 + sw, ky), (kx, ky + 90), (kx - 70 + sw, ky)], fill=(240, 80, 120), outline=OUTL)
    d.line([(kx, ky - 90), (kx, ky + 90)], fill=OUTL, width=4)
    d.line([(kx - 70 + sw, ky), (kx + 70 + sw, ky)], fill=OUTL, width=4)
    d.line([(kx, ky + 90), (kx - 40, ky + 200), (kx + 10, ky + 300)], fill=(200, 200, 210), width=4)
    if lt > 1.0: put_label(frame, "LEAVE IT!", 780, 860, 64)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="perch", s=4.0, e=11.0, bg_fn=lambda T: wire_bg(), clock="9:00 AM", char="pigeon",
         pos=pig_on(PX, 340), props=perch_props, props_after=perch_after, look=(0, 0.1),
         narr="Many street wires in India carry 11,000 VOLTS. You sit on one. NOTHING happens.", n_at=4.2,
         say="Comfy SEAT!", say_at=7.0, pitch=900),
    dict(id="same", s=11.0, e=18.0, bg_fn=lambda T: wire_bg(), clock="WHY?", char="pigeon",
         pos=pig_on(PX, 340), props=same_props, props_after=same_after, look=(0, 0.3),
         narr="Current flows from HIGH voltage to LOW. Both your feet: the SAME voltage.", n_at=11.2,
         say="No difference, no SHOCK!", say_at=14.0, pitch=900),
    dict(id="home", s=18.0, e=24.5, bg="living", clock="AT HOME", char="kid", pos=(260, 1110, 400),
         props=home_props, look=(0.6, 0.1),
         narr="Your home socket: 230 VOLTS. That street wire: almost 50 TIMES more.", n_at=18.2,
         say="NEVER touch either!", say_at=21.0, pitch=600),
    dict(id="two", s=24.5, e=31.0, bg_fn=lambda T: wire_bg(), clock="DANGER", char="pigeon",
         pos=pig_on(PX, 340), props=two_props, props_after=two_after, look=(0.3, 0.5),
         rot=lambda T: 6 * math.sin(T * 40) if T - 24.5 > 2.0 else 0,
         overlay=flash(0.9, 0.12, 0.5, 2.0),
         narr="But touch a SECOND wire, or the POLE, and current rushes THROUGH you.", n_at=24.7,
         say="ZZZAP!", say_at=27.0, pitch=1000),
    dict(id="vulture", s=31.0, e=38.0, bg_fn=lambda T: wire_bg(), clock="BIG WINGS", props=vulture_props,
         narr="Big wings touch TWO wires. Near Dehradun, 130+ vultures and eagles died on just 4 KM of wire.",
         n_at=31.2),
    dict(id="fix", s=38.0, e=44.5, bg_fn=lambda T: wire_bg(True), clock="THE FIX", char="pigeon",
         pos=pig_on(PX, 340), props=fix_props, props_after=fix_after, look=(0, 0.1),
         narr="The fix: COVER the wires. Since 2025, WWF-India has recorded NO deaths there.", n_at=38.2,
         say="Safe perch for ALL!", say_at=41.0, pitch=900),
    dict(id="big", s=44.5, e=51.0, bg_fn=big_bg, clock="BIGGEST LINES", char="pigeon", pos=(230, 1080, 300),
         props=big_props, look=(0.5, -0.3),
         narr="India's biggest power lines carry 765,000 VOLTS across the country.", n_at=44.7,
         say="Birds sit here TOO!", say_at=47.2, pitch=900),
    dict(id="twist", s=TW, e=58.5, bg_fn=lambda T: wire_bg(sky="speed"), clock="PLOT TWIST", char="uncle",
         state="hat", pos=(640, 1010, 260), props=suit_props, twist=True, look=(0.4, 0),
         narr="Twist: trained linemen in METAL-thread suits touch LIVE lines, just like a BIRD.", n_at=TW + 0.2,
         say="Experts ONLY. Never try!", say_at=TW + 3.2, pitch=300),
    dict(id="kite", s=58.5, e=65.0, bg_fn=lambda T: wire_bg(), clock="SAFETY", char="kid", pos=(260, 1100, 380),
         props=kite_props, look=(0.6, -0.3),
         narr="Kite stuck on a wire? LEAVE it. Metal manja conducts. NEVER touch any wire.", n_at=58.7,
         say="Okay, I'll LEAVE it!", say_at=61.4, pitch=600),
    dict(id="outro", s=65.0, e=70.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_out(clamp((T - 1.9) / 0.5))
        y = 1500
        d.line([(540 - 500 * p, y), (540 + 500 * p, y)], fill=OUTL, width=10)
        d.line([(540 - 500 * p, y), (540 + 500 * p, y)], fill=(120, 120, 130), width=5)
        if p > 0.6:
            spark(d, 540 + 400 * math.sin(T * 2), y, T, 40)

cfg = dict(
    total=70.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("you were a ", WHITE), ("BIRD", YEL)], 120), 770, 0.75, "right"),
        (title([("on a", WHITE)], 110), 905, 1.05, "left"),
        (title([("POWER LINE?", YEL)], 150), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Did", WHITE), (" YOU", YEL), (" know", WHITE)], 92), 470, 0.15),
                      (title([("why birds are safe?", WHITE)], 84), 600, 0.45)],
               row=[("pigeon", 1), ("kid", 1), ("uncle", "hat"), ("sun", 1), ("earth", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=TW - 0.15), dict(t0=65.0, t1=70.0, melody=True)],
    drones=[dict(t0=TW, dur=14.0, g=0.07)],
    fx=[("click", 26.6, 0.8), ("crash", 26.6, 0.5), ("crash", 27.5, 0.4), ("crash", 28.4, 0.4),
        ("crash", 31.4, 0.3), ("wind", 44.7, 0.4, dict(dd=6.0)), ("wind", 58.7, 0.3, dict(dd=6.0))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_bird_wire")
