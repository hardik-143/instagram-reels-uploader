#!/usr/bin/env python3
"""What if you climbed the chilli ladder? A Scoville ladder: shimla mirch (bell pepper) 0 SHU (MasterClass); jalapeno
up to ~8,000 SHU (NPR / Guinness); Guntur Sannam, Andhra Pradesh, 35,000-40,000 SHU (Chili Pepper Madness);
bhut jolokia ~1 million SHU, Guinness hottest chilli 2007, from Northeast India (ScienceDaily / NMSU 2007); Naga Mircha
GI tag 2008, Nagaland (Wikipedia); Carolina Reaper 1.64 million SHU, Pepper X 2.69 million SHU, Guinness Oct 2023;
pure capsaicin 16 million SHU (Univ. of Bristol). Hornbill Festival 1-10 Dec 2026, Kisama (Time Out / GKToday).
Twist: chilli isn't Indian at all - it came from the Americas, brought by the Portuguese after Vasco da Gama reached
Calicut in 1498 (Alimentarium). Safety line: never dare anyone to eat super-hots."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

TW = 56.0   # twist starts

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=64):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

_gl = {}
def glow(frame, x, y, r, col=(255, 120, 60), s=0.8):
    k = (int(r), col, round(s, 2))
    if k not in _gl:
        R = max(2, int(r))
        yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
        q = np.clip(1 - np.sqrt(xx ** 2 + yy ** 2) / R, 0, 1) ** 2
        arr = np.zeros((2 * R + 1, 2 * R + 1, 4), np.uint8)
        arr[..., 0], arr[..., 1], arr[..., 2] = col
        arr[..., 3] = (q * 255 * s).astype(np.uint8)
        _gl[k] = Image.fromarray(arr, "RGBA")
    g = _gl[k]
    frame.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))

# ---------------------------------------------------------------- chilli drawing
def chilli(d, cx, cy, L, col, ang=0.0, fat=0.18, curve=0.25):
    """A curved chilli pod: tapered body + green stem, pointing down-left to up-right along ang."""
    n = 14
    top, bot = [], []
    ca, sa = math.cos(ang), math.sin(ang)
    for i in range(n + 1):
        u = i / n
        x = (u - 0.5) * L
        y = curve * L * (u - 0.5) ** 2 * 2 - curve * L * 0.25
        wdt = fat * L * (0.25 + 0.75 * math.sin(math.pi * min(1, u * 1.15)) ** 0.7) * (1 - 0.85 * u ** 2)
        for arr, s in ((top, -1), (bot, 1)):
            px, py = x, y + s * wdt / 2
            arr.append((cx + px * ca - py * sa, cy + px * sa + py * ca))
    pts = top + bot[::-1]
    d.polygon(pts, fill=col, outline=OUTL, width=5)
    # shine
    hx, hy = top[3]
    d.line([top[3], top[6]], fill=(255, 255, 255), width=max(3, int(L * 0.02)))
    # stem at u=0 end
    sx, sy = (top[0][0] + bot[0][0]) / 2, (top[0][1] + bot[0][1]) / 2
    ex, ey = sx - 0.12 * L * ca, sy - 0.12 * L * sa - 0.06 * L
    d.line([(sx, sy), (ex, ey)], fill=(60, 150, 60), width=max(6, int(L * 0.05)))
    d.ellipse([sx - L * 0.06, sy - L * 0.05, sx + L * 0.06, sy + L * 0.05], fill=(70, 170, 70), outline=OUTL, width=4)

def bell_pepper(d, cx, cy, r):
    for dx in (-0.45, 0, 0.45):
        d.ellipse([cx + dx * r - r * 0.55, cy - r * 0.8, cx + dx * r + r * 0.55, cy + r * 0.9], fill=(60, 180, 70),
                  outline=OUTL, width=5)
    d.ellipse([cx - r * 0.5, cy - r * 0.75, cx + r * 0.5, cy + r * 0.85], fill=(80, 200, 90))
    d.line([(cx - r * 0.2, cy - r * 0.5), (cx - r * 0.1, cy + r * 0.5)], fill=(200, 255, 200), width=8)
    d.rectangle([cx - 12, cy - r * 1.05, cx + 12, cy - r * 0.75], fill=(60, 130, 50), outline=OUTL, width=4)

# ---------------------------------------------------------------- heat meter on the left edge
LEVELS = {"bell": 0.03, "jalapeno": 0.14, "guntur": 0.27, "bhut": 0.45, "reaper": 0.6, "pepperx": 0.75,
          "capsaicin": 1.0}
ORDER = list(LEVELS)

def meter(frame, d, T, sc):
    lt = T - sc["s"]
    i = ORDER.index(sc["id"])
    prev = LEVELS[ORDER[i - 1]] if i else 0.0
    lv = prev + (LEVELS[sc["id"]] - prev) * ease_out(clamp(lt / 1.2))
    x, top, bot = 80, 480, 1200
    d.rounded_rectangle([x - 26, top, x + 26, bot], 26, fill=(250, 250, 255), outline=OUTL, width=5)
    yl = min(bot - (bot - top - 20) * lv, bot - 40)
    col = (int(120 + 135 * lv), int(200 - 170 * lv), 40)
    d.rounded_rectangle([x - 14, yl, x + 14, bot - 8], 14, fill=col)
    chilli(d, x, bot + 40, 110, (230, 40, 40), ang=-0.3, fat=0.3)

def with_meter(fn=None):
    def p(frame, d, T, sc):
        if fn: fn(frame, d, T, sc)
        meter(frame, d, T, sc)
    return p

def flames(frame, d, T, sc, n=5, y0=820, spread=110, scale=1.0):
    lt = T - sc["s"]
    for k in range(n):
        ph = (lt * 1.3 + k / n) % 1.0
        x = 540 + (k - (n - 1) / 2) * spread + 15 * math.sin(lt * 5 + k)
        y = y0 - ph * 160 * scale
        r = (34 - 20 * ph) * scale
        d.polygon([(x, y - r * 1.8), (x + r, y), (x, y + r * 0.8), (x - r, y)], fill=(255, int(160 - 80 * ph), 30),
                  outline=OUTL)

# ---------------------------------------------------------------- scene props
def p_bell(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_back(clamp(lt / 0.5))
    bell_pepper(d, 760, 1250, 120 * p + 1)

def p_jal(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_back(clamp(lt / 0.5))
    chilli(d, 770, 1240, 300 * p + 1, (50, 150, 50), ang=-0.5, fat=0.3, curve=0.1)

def p_guntur(frame, d, T, sc):
    lt = T - sc["s"]
    for k in range(5):
        p = ease_back(clamp((lt - k * 0.15) / 0.5))
        chilli(d, 700 + k * 50, 1180 + k * 40, 300 * p + 1, (210, 30, 30), ang=-0.6 + k * 0.12, fat=0.13)
    flames(frame, d, T, sc, n=3, y0=800, spread=140, scale=0.7)

def p_bhut(frame, d, T, sc):
    lt = T - sc["s"]
    glow(frame, 540, 1060, 380, (255, 90, 40), 0.55)
    p = ease_back(clamp(lt / 0.6))
    chilli(d, 540, 1080, 520 * p + 1, (220, 40, 30), ang=-0.35, fat=0.22, curve=0.3)
    # wrinkles
    if p > 0.9:
        for k in range(4):
            x = 420 + k * 70
            d.arc([x - 30, 1010 + k * -14, x + 30, 1070 + k * -14], 200, 340, fill=(150, 20, 20), width=6)
    flames(frame, d, T, sc, n=5, y0=850)

def reaper_shape(d, cx, cy, L, col):
    chilli(d, cx, cy, L, col, ang=0.1, fat=0.4, curve=0.05)
    tx, ty = cx + L * 0.5, cy + L * 0.02   # scorpion tail
    d.polygon([(tx - 30, ty - 30), (tx + 50, ty + 10), (tx + 20, ty + 60), (tx - 20, ty + 20)], fill=col,
              outline=OUTL)

def p_reaper(frame, d, T, sc):
    lt = T - sc["s"]
    glow(frame, 540, 1080, 400, (255, 60, 40), 0.6)
    p = ease_back(clamp(lt / 0.6))
    reaper_shape(d, 520, 1080, 400 * p + 1, (200, 20, 30))
    flames(frame, d, T, sc, n=6, y0=840, spread=110, scale=1.2)

def p_px(frame, d, T, sc):
    lt = T - sc["s"]
    glow(frame, 540, 1080, 440, (255, 40, 80), 0.7)
    p = ease_back(clamp(lt / 0.6))
    chilli(d, 540, 1090, 480 * p + 1, (240, 200, 40), ang=-0.2, fat=0.32, curve=0.2)
    flames(frame, d, T, sc, n=7, y0=850, spread=100, scale=1.4)
    if lt > 3.0:
        top_label(frame, "WORLD RECORD", 380, YEL, 60)

def p_caps(frame, d, T, sc):
    lt = T - sc["s"]
    # lab flask with a single glowing drop
    cx, cy = 540, 1080
    d.polygon([(cx - 60, cy - 250), (cx + 60, cy - 250), (cx + 60, cy - 80), (cx + 220, cy + 200),
               (cx - 220, cy + 200), (cx - 60, cy - 80)], fill=(220, 240, 255), outline=OUTL)
    d.line([(cx - 60, cy - 250), (cx - 60, cy - 80), (cx - 220, cy + 200), (cx + 220, cy + 200), (cx + 60, cy - 80),
            (cx + 60, cy - 250)], fill=OUTL, width=6)
    d.polygon([(cx - 140, cy + 90), (cx + 140, cy + 90), (cx + 220, cy + 200), (cx - 220, cy + 200)],
              fill=(255, 120, 60))
    for k in range(4):
        ph = (lt * 0.9 + k / 4) % 1.0
        x = cx + (k - 1.5) * 60; y = cy + 160 - ph * 220
        d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=(255, 200, 120), outline=OUTL, width=3)
    glow(frame, cx, cy + 140, 300, (255, 80, 40), 0.6)
    if lt > 3.2:
        top_label(frame, "DON'T TRY THIS", 380, (255, 90, 90), 66)

def p_twist(frame, d, T, sc):
    lt = T - sc["s"]
    # globe band with a dotted voyage line from the Americas to India
    d.ellipse([140, 760, 940, 1400], fill=(70, 140, 220), outline=OUTL, width=6)
    d.polygon([(250, 900), (360, 880), (380, 1040), (330, 1240), (290, 1250), (300, 1060), (240, 980)],
              fill=(90, 190, 90), outline=OUTL)       # Americas
    d.polygon([(700, 950), (800, 930), (830, 1010), (770, 1140), (740, 1080), (690, 1010)],
              fill=(90, 190, 90), outline=OUTL)       # India
    q = ease_out(clamp((lt - 0.8) / 2.5))
    pts = []
    for i in range(int(40 * q) + 1):
        u = i / 40
        pts.append((360 + 400 * u, 1000 - 220 * math.sin(math.pi * u)))
    for i, (x, y) in enumerate(pts):
        if i % 2 == 0:
            d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=WHITE)
    if pts:
        x, y = pts[-1]
        chilli(d, x, y - 20, 110, (220, 30, 30), ang=-0.3, fat=0.25)
    if lt > 3.2:
        top_label(frame, "MADE IN... AMERICA?!", 380, YEL, 64)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="bell", s=4.0, e=10.5, bg="day", clock="0 SHU", char="kid", pos=(470, 1080, 440),
         props=with_meter(p_bell), look=(0.4, 0.2),
         narr="Chilli heat is measured in SCOVILLE units. SHIMLA MIRCH scores ZERO.", n_at=4.2,
         say="Easy! Next!", say_at=7.4, pitch=620),
    dict(id="jalapeno", s=10.5, e=17.0, bg="day", clock="8,000 SHU", char="kid", pos=(470, 1080, 440),
         props=with_meter(p_jal), look=(0.4, 0.2),
         narr="A JALAPENO: up to about 8,000. The pizza-topping level.", n_at=10.7,
         say="Thoda tikha...", say_at=13.6, pitch=620),
    dict(id="guntur", s=17.0, e=23.5, bg="hot", clock="40,000 SHU", char="kid", state="puff", pos=(430, 1080, 440),
         props=with_meter(p_guntur), look=(0.4, 0),
         narr="GUNTUR chillies from Andhra Pradesh: around 35,000 to 40,000.", n_at=17.2,
         say="PAANI! PAANI!", say_at=20.2, pitch=680),
    dict(id="bhut", s=23.5, e=30.0, bg="night", clock="1 MILLION SHU",
         props=with_meter(p_bhut),
         narr="The BHUT JOLOKIA from Northeast India: about 1 MILLION. Guinness's hottest in 2007!", n_at=23.7),
    dict(id="reaper", s=30.0, e=36.5, bg="storm", clock="1.64 MILLION SHU",
         props=with_meter(p_reaper),
         narr="Then the CAROLINA REAPER took the crown: 1.64 MILLION.", n_at=30.2),
    dict(id="pepperx", s=36.5, e=43.0, bg="storm", clock="2.69 MILLION SHU",
         props=with_meter(p_px),
         narr="Today's champion, since 2023: PEPPER X, 2.69 MILLION.", n_at=36.7),
    dict(id="capsaicin", s=43.0, e=TW, bg="office", clock="16 MILLION SHU", char="uncle", pos=(800, 1180, 360),
         props=with_meter(p_caps), look=(-0.5, -0.2),
         narr="The top of the ladder: PURE CAPSAICIN, the chemical behind the burn, 16 MILLION.", n_at=43.2,
         say="Lab only. NEVER dare anyone!", say_at=48.6, pitch=300),
    dict(id="twist", s=TW, e=63.0, bg="space", clock="WAIT...", props=p_twist, twist=True,
         narr="Twist: chilli isn't even INDIAN! The Portuguese brought it from the AMERICAS after 1498.", n_at=56.4),
    dict(id="outro", s=63.0, e=68.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.4)
        chilli(d, 540, 1400, 340 * p + 1, (220, 30, 30), ang=-0.3, fat=0.22)

cfg = dict(
    total=68.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU CLIMBED", WHITE)], 140), 770, 0.75, "right"),
        (title([("THE CHILLI", WHITE)], 140), 915, 1.05, "left"),
        (title([("LADDER?", YEL)], 130), 1070, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("How high can ", WHITE), ("YOU", YEL)], 96), 470, 0.15),
                      (title([("handle?", YEL)], 110), 600, 0.45)],
               row=[("kid", 1), ("samosa", 1), ("uncle", 1), ("chai", 1), ("cow", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=TW - 0.15, melody=True),
           dict(t0=63.0, t1=68.0, melody=True)],
    fx=[("gasp", 20.0, 0.5), ("boom", 23.6, 0.6), ("rumble", 30.1, 0.5, dict(dd=5.0)), ("crash", 36.6, 0.5),
        ("bubbles", 43.3, 0.4, dict(dd=5.0)), ("seagulls", TW + 0.6, 0.3), ("waves", TW + 0.2, 0.3, dict(dd=5.0))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_chilli_ladder")
