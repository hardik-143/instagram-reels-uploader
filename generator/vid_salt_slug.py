#!/usr/bin/env python3
"""What if salt touched a slug? Facts: slugs have a vestigial shell, internal in most species (John Innes Centre
'All about slugs'; Univ. of Kentucky Critter Files: shell small and hidden under the skin). Eyespots sit on the tips
of the upper (longer) tentacles and can be regrown if lost (JIC). Slug skin loses water easily, so slugs rely on
mucus to stay moist (UKy). Salt mixes with the water in the mucus, forming a solution saltier than the slug's
interior; water leaves the skin cells by osmosis until the slug dehydrates (Mental Floss; Science Focus / Dr Gordon
Port, Newcastle Univ.: slugs release lots of mucus to clean their skin and die within minutes of dehydration;
scientists don't know how much pain they feel). Salt preserves food: it draws water out and gives microbes osmotic
shock (Science ABC). Seawater is ~3.5% salt (NOAA); kidneys can only make urine less salty than blood, so drinking
seawater dehydrates you (Live Science; USGS). Twist: most marine invertebrates are osmoconformers whose body fluids
are about isotonic with seawater (Univ. of Alabama Animal Physiology pressbook), so sea slugs don't lose water."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, ease_back, ease_out, clamp, text_sprite
from make_reel import grad

TW = 60.0
BODY = (226, 156, 70)
BODY_D = (184, 116, 48)
DRY = (150, 104, 66)
SLIME = (200, 240, 255)
SALT = (250, 250, 255)

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=68):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

def put(frame, txt, cx, y, size=52, col=WHITE):
    l = label(txt, size, col)
    comp(frame, l, cx - l.width / 2, y)

def mix(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

# ---------------------------------------------------------------- backgrounds
_bgc = {}
def garden_bg():
    if "garden" not in _bgc:
        img = grad([(0, (150, 210, 250)), (0.6, (214, 240, 220)), (1, (214, 240, 220))], W, H)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 1180, W, H], fill=(120, 86, 60))
        d.rectangle([0, 1170, W, 1200], fill=(90, 160, 80))
        rng = np.random.default_rng(3)
        for k in range(40):
            x = rng.uniform(0, W); h = rng.uniform(30, 90)
            d.polygon([(x - 10, 1185), (x + 10, 1185), (x + rng.uniform(-15, 15), 1185 - h)], fill=(70, 150, 70))
        for k in range(18):
            x = rng.uniform(0, W); y = rng.uniform(1260, 1900); r = rng.uniform(10, 26)
            d.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=(100, 72, 52))
        _bgc["garden"] = img
    return _bgc["garden"]

def lab_bg():
    if "lab" not in _bgc:
        img = grad([(0, (226, 236, 246)), (1, (196, 210, 228))], W, H)
        _bgc["lab"] = img
    return _bgc["lab"]

def kitchen_bg():
    if "kitchen" not in _bgc:
        img = grad([(0, (255, 232, 196)), (1, (248, 206, 160))], W, H)
        d = ImageDraw.Draw(img)
        for x in range(0, W, 90):
            for y in range(560, 1180, 90):
                d.rectangle([x + 3, y + 3, x + 87, y + 87], outline=(240, 214, 176), width=3)
        d.rectangle([0, 1180, W, H], fill=(170, 110, 70))
        d.rectangle([0, 1170, W, 1196], fill=(120, 76, 46))
        _bgc["kitchen"] = img
    return _bgc["kitchen"]

# ---------------------------------------------------------------- slug
_PS = [0, 0.06, 0.3, 0.55, 0.72, 0.86, 0.95, 1.0]
_PH = [0.02, 0.25, 0.55, 0.92, 0.96, 0.72, 0.45, 0.1]

def slug(frame, cx, cy, L, T, dry=0.0, eyes=1.0, wig=1.0, col=None, spots=None):
    """Side-view slug facing right, foot on y=cy. dry in 0..1 shrinks and darkens it."""
    d = ImageDraw.Draw(frame)
    L = L * (1 - 0.35 * dry)
    Hh = L * 0.24 * (1 - 0.45 * dry)
    base = col or BODY
    c = mix(base, DRY, dry); cd = mix(BODY_D if col is None else tuple(int(v * 0.8) for v in base), (110, 76, 50), dry)
    ow = max(3, int(L / 110))
    ss = np.linspace(0, 1, 60)
    hs = np.interp(ss, _PS, _PH) * Hh
    crawl = wig * 6 * np.sin(ss * 2 * math.pi * 2 - T * 5)
    xs = cx - L / 2 + ss * L
    top = [(x, cy - h - (k if h > 4 else 0)) for x, h, k in zip(xs, hs, crawl)]
    pts = top + [(cx + L / 2, cy), (cx - L / 2, cy)]
    # tentacles (behind body edge)
    hx = cx + L * 0.43; hy = cy - Hh * 0.55
    sway = math.sin(T * 2.5) * 0.1
    for k, (ang, ln, eye) in enumerate(((-1.05 + sway, 0.2, True), (-0.75 + sway, 0.19, True),
                                         (-0.25, 0.07, False), (0.05, 0.065, False))):
        ln = L * ln * (eyes if eye else 1.0) * (1 - 0.5 * dry)
        ex = hx + math.cos(ang) * ln; ey = hy + math.sin(ang) * ln
        d.line([(hx, hy), (ex, ey)], fill=OUTL, width=int(L * 0.032) + 2 * ow)
        d.line([(hx, hy), (ex, ey)], fill=c, width=int(L * 0.032))
        if eye and eyes > 0.3:
            r = L * 0.028
            d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=WHITE, outline=OUTL, width=max(2, ow - 1))
            pr = r * 0.55
            d.ellipse([ex + r * 0.15 - pr, ey - pr, ex + r * 0.15 + pr, ey + pr], fill=OUTL)
    d.polygon(pts, fill=c, outline=OUTL, width=ow)
    # mantle saddle
    m0, m1 = cx - L / 2 + 0.5 * L, cx - L / 2 + 0.86 * L
    mt = cy - Hh * 0.98
    d.chord([m0, mt - Hh * 0.1, m1, cy - Hh * 0.25], 180, 360, fill=cd, outline=OUTL, width=max(2, ow - 1))
    d.ellipse([m0 + L * 0.05, cy - Hh * 0.55, m0 + L * 0.085, cy - Hh * 0.43], fill=OUTL)  # breathing hole
    # foot skirt + smile
    d.line([(cx - L * 0.45, cy - 4), (cx + L * 0.46, cy - 4)], fill=cd, width=max(3, int(Hh * 0.12)))
    d.arc([hx + L * 0.01, cy - Hh * 0.45, hx + L * 0.06, cy - Hh * 0.2], 0, 160, fill=OUTL, width=max(2, ow - 1))
    if spots:
        rng = np.random.default_rng(5)
        for _ in range(spots):
            s = rng.uniform(0.15, 0.85); x = cx - L / 2 + s * L
            y = cy - np.interp(s, _PS, _PH) * Hh * rng.uniform(0.2, 0.75); r = L * 0.018
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255))
    return hx, hy, Hh, L

def slime_trail(d, x0, x1, y, T):
    d.rounded_rectangle([x0, y - 8, x1, y + 10], radius=9, fill=SLIME)
    for k in range(int((x1 - x0) / 60)):
        x = x0 + 30 + k * 60
        a = 0.5 + 0.5 * math.sin(T * 4 + k)
        d.ellipse([x - 5, y - 3, x + 5, y + 5], fill=WHITE if a > 0.5 else SLIME)

def crystals(d, pts, s=14):
    for x, y in pts:
        d.rectangle([x - s / 2, y - s / 2, x + s / 2, y + s / 2], fill=SALT, outline=OUTL, width=2)

def shaker(d, x, y, tilt=0.0):
    c, sn = math.cos(tilt), math.sin(tilt)
    R = lambda px, py: (x + px * c - py * sn, y + px * sn + py * c)
    d.polygon([R(-55, -90), R(55, -90), R(70, 110), R(-70, 110)], fill=(230, 236, 246), outline=OUTL)
    d.polygon([R(-60, 110), R(60, 110), R(50, 160), R(-50, 160)], fill=(170, 176, 190), outline=OUTL)
    for k in (-25, 0, 25):
        px, py = R(k, 148); d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=OUTL)
    px, py = R(0, 10)
    l = "SALT"
    return R(0, 175)

def foam(d, cx, cy, L, T, amt):
    rng = np.random.default_rng(11)
    for k in range(int(amt * 40)):
        s = rng.uniform(0.05, 0.95); x = cx - L / 2 + s * L + rng.uniform(-10, 10)
        y = cy - rng.uniform(0, L * 0.18); r = rng.uniform(8, 20) * (0.8 + 0.2 * math.sin(T * 5 + k))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(245, 250, 255), outline=(170, 190, 210), width=2)

# ---------------------------------------------------------------- props
def meet_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_back(clamp(lt / 0.6))
    x = 470 + 25 * lt
    slime_trail(d, 60, x - 300, 1186, T)
    slug(frame, x, 1186, 640 * p + 2, T)
    if lt > 0.5: top_label(frame, "THE SLUG", 380, YEL, 110)
    if lt > 1.2: put(frame, "a snail with a hidden shell", 540, 535, 54, WHITE)

def eyes_props(frame, d, T, sc):
    lt = T - sc["s"]
    e = 0.2 + 0.8 * ease_out(clamp((lt - 0.6) / 1.2))
    if 3.6 < lt < 4.6: e = 0.2 + 0.8 * abs(math.cos((lt - 3.6) * math.pi))
    hx, hy, Hh, L = slug(frame, 470, 1186, 820, T, eyes=e)
    if lt > 1.6:
        tx, ty = hx + math.cos(-1.05) * L * 0.2, hy + math.sin(-1.05) * L * 0.2
        d.ellipse([tx - 58, ty - 58, tx + 58, ty + 58], outline=YEL, width=8)
    if lt > 0.5: top_label(frame, "EYES ON STALKS", 380, YEL, 96)

def slime_props(frame, d, T, sc):
    lt = T - sc["s"]
    x = 520 + 30 * lt
    slime_trail(d, 40, x - 330, 1186, T)
    slug(frame, x, 1186, 700, T, spots=14)
    rng = np.random.default_rng(2)
    for k in range(6):  # sun drying drops
        a = (T * 0.6 + k / 6) % 1
        dx = 200 + k * 130; dy = 1100 - a * 380
        r = 12 * (1 - a)
        if r > 2: d.ellipse([dx - r, dy - r * 1.3, dx + r, dy + r], fill=(140, 200, 255))
    if lt > 0.5: top_label(frame, "ALWAYS WET", 380, YEL, 110)

def salt_pts(lt, t0, cx, L, n=40, seed=1):
    rng = np.random.default_rng(seed)
    pts = []
    for k in range(n):
        st = t0 + k * 0.05
        if lt < st: continue
        x0 = 600 + rng.uniform(-30, 30)
        x1 = cx - L * 0.35 + rng.uniform(0, L * 0.7)
        p = clamp((lt - st) / 0.7)
        y = 700 + p * (1080 - 700) + rng.uniform(-20, 20) * p
        pts.append((x0 + (x1 - x0) * p, y))
    return pts

def salt_props(frame, d, T, sc):
    lt = T - sc["s"]
    slug(frame, 470, 1186, 700, T, eyes=1.0 if lt < 2.5 else 0.5)
    tilt = 2.6 * ease_out(clamp((lt - 0.6) / 0.5))
    shaker(d, 640, 600, tilt)
    if lt > 1.1: crystals(d, salt_pts(lt, 1.1, 470, 700))
    if lt > 0.5: top_label(frame, "SALT!", 380, YEL, 120)

def osmo_props(frame, d, T, sc):
    lt = T - sc["s"]
    # two chambers with a wavy membrane
    X0, X1, Y0, Y1 = 90, 990, 600, 1300
    d.rounded_rectangle([X0, Y0, X1, Y1], radius=30, fill=(190, 230, 250), outline=OUTL, width=6)
    mx = 540
    d.line([(mx + 10 * math.sin(y / 30), y) for y in range(Y0, Y1, 8)], fill=(200, 140, 80), width=10)
    put(frame, "INSIDE SLUG", 315, Y0 + 30, 48, WHITE)
    put(frame, "SALTY SLIME", 765, Y0 + 30, 48, WHITE)
    rng = np.random.default_rng(4)
    # salt grains on right
    crystals(d, [(rng.uniform(600, 960), rng.uniform(720, 1260)) for _ in range(26)], 18)
    # water drops travelling left -> right
    for k in range(14):
        ph = (lt * 0.35 + k / 14) % 1
        y = 720 + (k * 41) % 520
        x = 150 + ph * 780
        r = 16
        d.ellipse([x - r, y - r, x + r, y + r], fill=(60, 140, 230), outline=OUTL, width=3)
    # big arrow drawn as shapes
    ay = 1380
    d.rectangle([330, ay - 14, 700, ay + 14], fill=YEL, outline=OUTL, width=4)
    d.polygon([(700, ay - 40), (770, ay), (700, ay + 40)], fill=YEL, outline=OUTL)
    if lt > 0.5: top_label(frame, "OSMOSIS", 380, YEL, 120)

def shrivel_props(frame, d, T, sc):
    lt = T - sc["s"]
    dry = clamp((lt - 1.0) / 4.5) * 0.9
    slug(frame, 520, 1186, 760, T, dry=dry, eyes=0.35, wig=0.3)
    foam(d, 520, 1186, 760 * (1 - 0.35 * dry), T, clamp(lt / 1.5) * (1 - 0.5 * dry))
    crystals(d, salt_pts(9, 0, 520, 760 * (1 - 0.35 * dry), n=30, seed=3), 12)
    if lt > 0.5: top_label(frame, "DRYING OUT", 380, YEL, 110)
    if lt > 3.0: put(frame, "PLEASE NEVER DO THIS", 540, 540, 64, WHITE)

def jar(d, cx, cy, s, T):
    d.rounded_rectangle([cx - 150 * s, cy - 220 * s, cx + 150 * s, cy + 200 * s], radius=40 * s,
                        fill=(250, 200, 120), outline=OUTL, width=7)
    d.rectangle([cx - 130 * s, cy - 120 * s, cx + 130 * s, cy + 180 * s], fill=(230, 110, 40))
    rng = np.random.default_rng(8)
    for k in range(12):
        x = cx + rng.uniform(-110, 110) * s; y = cy + rng.uniform(-90, 160) * s
        d.polygon([(x - 26 * s, y), (x, y - 20 * s), (x + 30 * s, y + 4 * s), (x + 4 * s, y + 22 * s)],
                  fill=(250, 210, 90), outline=OUTL)
    d.rounded_rectangle([cx - 165 * s, cy - 270 * s, cx + 165 * s, cy - 210 * s], radius=14 * s,
                        fill=(200, 60, 60), outline=OUTL, width=7)

def microbe(d, x, y, r, T, k, sad):
    w = r * (1 + 0.08 * math.sin(T * 6 + k))
    d.ellipse([x - w, y - r * 0.7, x + w, y + r * 0.7], fill=(120, 200, 110), outline=OUTL, width=4)
    for ex in (-0.35, 0.35):
        d.ellipse([x + ex * r - 6, y - 14, x + ex * r + 6, y - 2], fill=OUTL)
    if sad: d.arc([x - r * 0.3, y + 4, x + r * 0.3, y + 30], 200, 340, fill=OUTL, width=4)
    else: d.arc([x - r * 0.3, y - 10, x + r * 0.3, y + 16], 20, 160, fill=OUTL, width=4)

def achaar_props(frame, d, T, sc):
    lt = T - sc["s"]
    jar(d, 720, 1050, 0.8, T)
    sad = lt > 2.5
    for k, (x, y) in enumerate(((500, 960), (960, 930), (960, 1110))):
        r = 46 * (1 - 0.35 * clamp((lt - 2.5) / 2))
        microbe(d, x + 8 * math.sin(T * 2 + k), y, r, T, k, sad)
        if lt > 1.5:
            crystals(d, [(x + 80 * math.cos(T * 2 + j * 2.1), y + 60 * math.sin(T * 2 + j * 2.1)) for j in range(3)], 14)
    if lt > 0.5: top_label(frame, "ACHAAR POWER", 380, YEL, 100)

def glass(d, cx, cy, s, T):
    d.polygon([(cx - 90 * s, cy - 160 * s), (cx + 90 * s, cy - 160 * s), (cx + 70 * s, cy + 140 * s),
               (cx - 70 * s, cy + 140 * s)], fill=(220, 240, 255), outline=OUTL)
    d.polygon([(cx - 84 * s, cy - 100 * s), (cx + 84 * s, cy - 100 * s), (cx + 70 * s, cy + 134 * s),
               (cx - 70 * s, cy + 134 * s)], fill=(60, 150, 220))
    for k in range(3):
        y = cy - 100 * s + 8 * math.sin(T * 3 + k)
    d.line([(cx - 84 * s, cy - 100 * s), (cx + 84 * s, cy - 100 * s)], fill=WHITE, width=5)

def you_props(frame, d, T, sc):
    lt = T - sc["s"]
    glass(d, 760, 1020, 1.2, T)
    put(frame, "3.5% SALT", 760, 1230, 64, YEL)
    if lt > 0.5: top_label(frame, "SEAWATER?", 380, YEL, 110)

def nudibranch(frame, cx, cy, L, T):
    d = ImageDraw.Draw(frame)
    slug(frame, cx, cy, L, T, col=(140, 80, 220), wig=1.0)
    # frilly orange gills + tips
    for k in range(9):
        s = 0.25 + k * 0.07
        x = cx - L / 2 + s * L
        y = cy - np.interp(s, _PS, _PH) * L * 0.24
        h = L * 0.09 * (1 + 0.15 * math.sin(T * 4 + k))
        d.polygon([(x - 14, y + 6), (x + 14, y + 6), (x, y - h)], fill=(255, 150, 40), outline=OUTL)
        d.ellipse([x - 7, y - h - 7, x + 7, y - h + 7], fill=WHITE, outline=OUTL)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    rng = np.random.default_rng(9)
    for k in range(18):
        x = rng.uniform(0, W); ph = (T * 0.15 + rng.uniform(0, 1)) % 1
        y = 1300 - ph * 900; r = rng.uniform(5, 12)
        d.ellipse([x - r, y - r, x + r, y + r], outline=(170, 220, 255), width=3)
    d.rectangle([0, 1200, W, H], fill=(214, 190, 140))
    for x in (120, 960):
        for k in range(5):
            d.line([(x + k * 12 - 24, 1200), (x + k * 12 - 24 + 20 * math.sin(T + k), 1000 + k * 20)],
                   fill=(60, 160, 90), width=14)
    p = ease_back(clamp(lt / 0.7))
    nudibranch(frame, 500 + 12 * lt, 1205, 620 * p + 2, T)
    if lt > 0.5: top_label(frame, "SEA SLUGS", 380, YEL, 110)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="meet", s=4.0, e=11.0, bg_fn=lambda T: garden_bg(), clock="GARDEN", props=meet_props, char="kid",
         pos=(170, 1330, 230), look=(0.6, -0.3),
         narr="Meet the SLUG: a snail whose tiny SHELL is hidden under its skin.", n_at=4.2,
         narr_y=1580, say="Where's its HOUSE?", say_at=7.6, pitch=440),
    dict(id="eyes", s=11.0, e=18.0, bg_fn=lambda T: garden_bg(), clock="LOOK UP", props=eyes_props,
         narr="Its EYES sit on the tips of its long tentacles. Lose one? It can REGROW it.", n_at=11.2,
         narr_y=1580),
    dict(id="slime", s=18.0, e=25.0, bg_fn=lambda T: garden_bg(), clock="SLIMY", props=slime_props,
         narr="Its skin loses water EASILY, so it stays coated in SLIME to keep wet.", n_at=18.2,
         narr_y=1580),
    dict(id="salt", s=25.0, e=32.0, bg_fn=lambda T: garden_bg(), clock="UH OH", props=salt_props,
         narr="Add SALT and it dissolves in the slime, making it SALTIER than the slug's insides.",
         n_at=25.2, narr_y=1580),
    dict(id="osmo", s=32.0, e=39.0, bg_fn=lambda T: lab_bg(), clock="THE SCIENCE", props=osmo_props,
         narr="Water flows toward the SALTIER side. That's OSMOSIS, and it pulls water OUT of the slug.",
         n_at=32.2, narr_y=1580),
    dict(id="shrivel", s=39.0, e=46.0, bg_fn=lambda T: garden_bg(), clock="MINUTES", props=shrivel_props,
         narr="It pumps out FOAMY slime to wash it off, but enough salt dries it out within MINUTES.",
         n_at=39.2, narr_y=1580),
    dict(id="achaar", s=46.0, e=53.0, bg_fn=lambda T: kitchen_bg(), clock="KITCHEN", props=achaar_props,
         char="uncle", pos=(220, 1130, 340), look=(0.6, -0.2),
         narr="Same trick guards your ACHAAR: salt pulls water out of MICROBES, so they can't grow.",
         n_at=46.2, narr_y=1580, say="Nani knew SCIENCE!", say_at=49.6, pitch=300),
    dict(id="you", s=53.0, e=TW, bg="ocean", clock="AND YOU?", props=you_props, char="kid",
         pos=(300, 1110, 360), look=(0.6, 0.0),
         narr="You can't drink SEAWATER: kidneys can't make urine saltier than BLOOD, so you'd dry out.",
         n_at=53.2, narr_y=1580),
    dict(id="twist", s=TW, e=67.0, bg="sea", clock="PLOT TWIST", props=twist_props, twist=True,
         narr="Twist: SEA SLUGS live in salt water all day. Their insides are about as SALTY as the sea!",
         n_at=TW + 0.2, narr_y=1600),
    dict(id="outro", s=67.0, e=72.0),
]

def intro_extra(frame, d, T):
    if T >= 1.6:
        p = min(ease_back((T - 1.6) / 0.5), 1.15)
        slug(frame, 540, 1450, 560 * p + 2, T)

cfg = dict(
    total=72.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 520, 0.2, "pop"),
        (title([("SALT TOUCHED", WHITE)], 130), 730, 0.75, "right"),
        (title([("A SLUG?", YEL)], 150), 880, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Which salty fact ", WHITE)], 96), 470, 0.15),
                      (title([("surprised ", WHITE), ("YOU?", YEL)], 100), 600, 0.45)],
               row=[("kid", 1), ("fish", 1), ("uncle", 1), ("worm", 1), ("samosa", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=25.0, melody=True),
           dict(t0=25.0, t1=39.0, minor=True), dict(t0=39.0, t1=46.0, drums=False, minor=True),
           dict(t0=46.0, t1=TW - 0.15, melody=True), dict(t0=TW + 2.0, t1=72.0, melody=True)],
    drones=[dict(t0=39.0, dur=7.0, g=0.10), dict(t0=TW, dur=7.0, g=0.12)],
    fx=[("pop", 26.2, 0.25), ("pop", 26.6, 0.2), ("pop", 27.0, 0.2), ("bubbles", 39.5, 0.15, dict(dd=5.0)),
        ("ding", 50.0, 0.2), ("splash", 54.0, 0.3), ("bubbles", TW + 1.0, 0.15, dict(dd=6.0))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_salt_touched_a_slug")
