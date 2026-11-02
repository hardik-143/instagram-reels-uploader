#!/usr/bin/env python3
"""What if you stacked books off a table? The block-stacking problem (Wikipedia: Block-stacking problem; Scientific
American 'This Block-Stacking Math Problem Has a Preposterous Solution'). With N identical books, one per layer, the
best overhang is (1/2)(1 + 1/2 + ... + 1/N) book lengths. 1 book: 1/2. 2 books: 3/4. 4 books: 25/24, the top book is
fully past the edge. 2 lengths: 31 books; 3: 227; 5: 12,367 (Wikipedia). 10 lengths: 272,400,600 books (computed;
SciAm: 100 million books give only ~9.5 lengths). The harmonic series diverges, so the overhang has no limit in theory.
272,400,600 books x 3 cm ~ 8,170 km tall, ~20x the ISS orbit (~400 km). Twist: with counterweights (Paterson et al.,
2007) 3 books reach a full length: two books side by side on one book, versus 11/12 for a single-wide stack."""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def put_label(frame, txt, cx, y, size=60, col=YEL):
    l = label(txt, size, col)
    comp(frame, l, cx - l.width / 2, y)

COLS = [(232, 80, 80), (80, 150, 230), (250, 190, 60), (90, 190, 120), (170, 110, 220), (250, 140, 60)]
WOOD = (176, 120, 76)
WOOD_D = (130, 86, 54)
EDGE = 380          # x of the table edge
TOP = 1150          # y of the table top

def table(d, edge=EDGE, top=TOP):
    d.rectangle([-20, top, edge, top + 50], fill=WOOD, outline=OUTL, width=6)
    d.rectangle([edge - 70, top + 50, edge - 30, 1310], fill=WOOD_D, outline=OUTL, width=5)
    # dashed edge guide line going up
    for y in range(top - 10, 380, -40):
        d.line([(edge, y), (edge, y - 18)], fill=WHITE, width=4)

def offsets(n):
    """x of the right end of each book (top first), in book lengths from the table edge."""
    out = []
    for i in range(1, n + 1):
        out.append(0.5 * sum(1.0 / k for k in range(i, n + 1)))
    return out

def stack(d, n, L, t, shown=None, edge=EDGE, top=TOP, outline=True):
    """Ideal harmonic stack of n books, length L px, thickness t px. `shown` = how many books (from the bottom) are drawn."""
    offs = offsets(n)
    shown = n if shown is None else shown
    for j in range(shown):            # j = 0 is the bottom book
        i = n - 1 - j                 # index from top
        xr = edge + offs[i] * L
        y1 = top - j * t
        c = COLS[j % len(COLS)]
        if outline:
            d.rectangle([xr - L, y1 - t, xr, y1], fill=c, outline=OUTL, width=max(1, min(5, int(t / 5))))
        else:
            d.rectangle([xr - L, y1 - t, xr, y1], fill=c)

def arrow_bar(frame, d, x0, x1, y, txt, size=46):
    d.line([(x0, y), (x1, y)], fill=YEL, width=7)
    d.line([(x0, y - 18), (x0, y + 18)], fill=YEL, width=7)
    d.line([(x1, y - 18), (x1, y + 18)], fill=YEL, width=7)
    put_label(frame, txt, (x0 + x1) / 2, y - 70, size)

def grow(sc, T, dur=1.6, delay=0.3):
    return ease_out(clamp((T - sc["s"] - delay) / dur))

# ------------------------------------------------------------------ scenes
L1 = 300
def one_props(frame, d, T, sc):
    lt = T - sc["s"]
    table(d)
    slide = 0.5 * ease_out(clamp((lt - 0.4) / 1.4))
    if lt > 3.6:   # push a bit too far, then it tips
        q = clamp((lt - 3.6) / 0.6)
        slide = 0.5 + 0.12 * q
    xr = EDGE + slide * L1
    if lt > 4.2:
        q = clamp((lt - 4.2) / 0.7)
        y = TOP + 600 * q * q
        d.rectangle([xr - L1 + 40 * q, y - 40, xr + 40 * q, y], fill=COLS[0], outline=OUTL, width=5)
        put_label(frame, "FALLS!", 700, 860, 70)
    else:
        d.rectangle([xr - L1, TOP - 40, xr, TOP], fill=COLS[0], outline=OUTL, width=5)
        if lt > 1.8:
            arrow_bar(frame, d, EDGE, EDGE + 0.5 * L1, TOP - 120, "1/2")

def two_props(frame, d, T, sc):
    lt = T - sc["s"]
    table(d)
    stack(d, 2, L1, 40, shown=1 if lt < 1.4 else 2)
    if lt > 2.0:
        arrow_bar(frame, d, EDGE, EDGE + 0.75 * L1, TOP - 170, "3/4")

def four_props(frame, d, T, sc):
    lt = T - sc["s"]
    table(d)
    shown = 1 + int(clamp((lt - 0.3) / 2.0) * 3.99)
    stack(d, 4, L1, 40, shown=shown)
    if shown == 4:
        x_top_left = EDGE + offsets(4)[0] * L1 - L1
        d.line([(x_top_left, TOP - 160 - 30), (x_top_left, TOP - 160 + 70)], fill=YEL, width=6)
        put_label(frame, "FULLY PAST THE EDGE", 540, 880, 52)

def b31_props(frame, d, T, sc):
    lt = T - sc["s"]
    table(d, edge=300)
    shown = 1 + int(clamp((lt - 0.3) / 2.5) * 30.99)
    stack(d, 31, 180, 11, shown=shown, edge=300)
    if shown == 31:
        arrow_bar(frame, d, 300, 300 + 2 * 180, 1250, "2 BOOK LENGTHS")

def b227_props(frame, d, T, sc):
    lt = T - sc["s"]
    table(d, edge=260)
    shown = 1 + int(clamp((lt - 0.3) / 2.5) * 226.99)
    stack(d, 227, 140, 3.0, shown=shown, edge=260, outline=False)
    if shown == 227:
        arrow_bar(frame, d, 260, 260 + 3 * 140, 440, "3 LENGTHS: 227", 44)
    if lt > 3.8:
        put_label(frame, "5 LENGTHS: 12,367", 760, 1000, 46, WHITE)

def infinite_props(frame, d, T, sc):
    lt = T - sc["s"]
    terms = ["1", "+ 1/2", "+ 1/3", "+ 1/4", "+ 1/5", "+ ..."]
    k = int(clamp((lt - 0.3) / 2.4) * len(terms) + 0.999)
    line = " ".join(terms[:k])
    if line:
        put_label(frame, line, 540, 420, 64)
    if lt > 3.2:
        put_label(frame, "NEVER STOPS GROWING", 540, 520, 56, WHITE)

def crore_props(frame, d, T, sc):
    lt = T - sc["s"]
    p = ease_back(clamp((lt - 0.5) / 0.6))
    if p > 0:
        put_label(frame, "27 CRORE BOOKS", 540, 420, int(30 + 50 * min(p, 1.1)))
    if lt > 2.2:
        put_label(frame, "(272 MILLION)", 540, 530, 50, WHITE)

def iss(d, x, y, s=1.0):
    d.rectangle([x - 70 * s, y - 8 * s, x + 70 * s, y + 8 * s], fill=(220, 220, 230), outline=OUTL, width=3)
    for dx in (-60, -30, 30, 60):
        d.rectangle([x + dx * s - 12 * s, y - 50 * s, x + dx * s + 12 * s, y - 12 * s], fill=(70, 110, 200), outline=OUTL, width=3)
        d.rectangle([x + dx * s - 12 * s, y + 12 * s, x + dx * s + 12 * s, y + 50 * s], fill=(70, 110, 200), outline=OUTL, width=3)
    d.rectangle([x - 18 * s, y - 18 * s, x + 18 * s, y + 18 * s], fill=WHITE, outline=OUTL, width=3)

def height_props(frame, d, T, sc):
    lt = T - sc["s"]
    paste_c(frame, draw_char("earth", 300, T, 0, E.blink_at(T, 0.2), (0.3, -0.4), lt * 0.3), 540, 1080)
    p = ease_out(clamp((lt - 0.4) / 2.6))
    top = 935 - 440 * p
    d.rectangle([528, top, 552, 935], fill=COLS[2], outline=OUTL, width=3)
    iss(d, 760, 880, 0.8)
    put_label(frame, "ISS 400 KM", 800, 940, 40, WHITE)
    if p > 0.9:
        put_label(frame, "~8,000 KM", 760, 420, 64)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    table(d, edge=540)
    L = 260; t = 46
    # bottom book centred on the edge, two books side by side on top: one out, one as counterweight
    d.rectangle([540 - L / 2, TOP - t, 540 + L / 2, TOP], fill=COLS[1], outline=OUTL, width=5)
    q = ease_out(clamp((lt - 0.8) / 1.2))
    d.rectangle([540 - L, TOP - 2 * t, 540, TOP - t], fill=COLS[3], outline=OUTL, width=5)
    d.rectangle([540 + L * q - L, TOP - 2 * t, 540 + L * q, TOP - t], fill=COLS[0], outline=OUTL, width=5)
    if q >= 1:
        arrow_bar(frame, d, 540, 540 + L, TOP - 2 * t - 70, "1 FULL LENGTH")
        put_label(frame, "COUNTERWEIGHT", 290, 960, 36, WHITE)

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back((T - 1.9) / 0.4)
        for j in range(4):
            i = 3 - j
            xr = 480 + offsets(4)[i] * 220 * p
            y1 = 1560 - j * 34
            d.rectangle([xr - 220 * max(p, 0.1), y1 - 34, xr, y1], fill=COLS[j], outline=OUTL, width=4)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="one", s=4.0, e=11.0, bg="living", clock="1 BOOK", char="kid", pos=(820, 760, 300),
         props=one_props, look=(-0.6, 0.4),
         narr="One book on a table edge can stick out HALF its length. A bit more? It FALLS.", n_at=4.2,
         say="Physics, you WIN.", say_at=8.6, pitch=600),
    dict(id="two", s=11.0, e=18.0, bg="living", clock="2 BOOKS", char="kid", pos=(820, 760, 300),
         props=two_props, look=(-0.6, 0.4),
         narr="Two books, the RIGHT way: top one out by 1/2, the one below by 1/4.", n_at=11.2,
         say="3/4 of a book OUT!", say_at=14.4, pitch=600),
    dict(id="four", s=18.0, e=25.0, bg="living", clock="4 BOOKS", char="kid", state="puff", pos=(820, 700, 300),
         props=four_props, look=(-0.6, 0.4),
         narr="Add 1/6, then 1/8. With just 4 BOOKS, the top book hangs COMPLETELY past the edge!", n_at=18.2,
         say="It's FLOATING!", say_at=21.6, pitch=620),
    dict(id="b31", s=25.0, e=32.0, bg="living", clock="31 BOOKS", char="uncle", pos=(860, 1000, 280),
         props=b31_props, look=(-0.6, -0.2),
         narr="Want it 2 BOOK LENGTHS out? You need 31 BOOKS.", n_at=25.2,
         say="My whole SHELF!", say_at=28.4, pitch=300),
    dict(id="b227", s=32.0, e=39.0, bg="living", clock="227 BOOKS", props=b227_props,
         narr="3 lengths: 227 BOOKS. 5 lengths: 12,367 BOOKS. It gets HARD, fast.", n_at=32.2),
    dict(id="infinite", s=39.0, e=46.0, bg="night", clock="FOREVER?", char="kid", pos=(540, 1000, 400),
         props=infinite_props, look=(0, -0.4),
         narr="But this sum NEVER stops growing. In theory, your stack can reach out as far as you LIKE.",
         n_at=39.2, say="To INFINITY!", say_at=43.0, pitch=620),
    dict(id="crore", s=46.0, e=53.0, bg="night", clock="10 LENGTHS", char="uncle", state="angry",
         pos=(540, 1000, 400), props=crore_props, look=(0, -0.3),
         narr="The catch: 10 book lengths needs about 27 CRORE books.", n_at=46.2,
         say="Not from MY library!", say_at=49.4, pitch=300),
    dict(id="height", s=53.0, e=60.0, bg="space", clock="HOW TALL?", props=height_props,
         narr="At 3 CM per book, that stack is about 8,000 KM tall. 20x higher than the SPACE STATION.",
         n_at=53.2),
    dict(id="twist", s=60.0, e=67.5, bg="twist", clock="PLOT TWIST", char="kid", 
         pos=(850, 820, 280), props=twist_props, twist=True, look=(-0.6, 0.4),
         narr="Twist: CHEAT with a counterweight! 2 books side by side on 1: a full length out with just 3 BOOKS.",
         n_at=60.2, say="Work SMART!", say_at=63.8, pitch=620),
    dict(id="outro", s=67.5, e=72.5),
]

cfg = dict(
    total=72.5, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("you stacked", WHITE)], 120), 770, 0.75, "right"),
        (title([("BOOKS", YEL)], 170), 910, 1.05, "left"),
        (title([("off a table?", WHITE)], 120), 1080, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("How far can", WHITE)], 96), 470, 0.15),
                      (title([("YOU", YEL), (" stack?", WHITE)], 110), 600, 0.45)],
               row=[("kid", 1), ("uncle", 1), ("earth", 1), ("moon", 1), ("kid", "puff")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=39.0), dict(t0=39.0, t1=59.85, melody=True),
           dict(t0=67.5, t1=72.5, melody=True)],
    drones=[dict(t0=53.0, dur=7.0, g=0.06)],
    fx=[("crash", 8.4, 0.5), ("pop", 12.6, 0.5), ("pop", 18.9, 0.5), ("pop", 19.6, 0.5), ("pop", 20.3, 0.5),
        ("ding", 21.0, 0.4), ("rumble", 32.3, 0.3, dict(dd=2.5)), ("whoosh", 46.6, 0.7), ("boom", 53.4, 0.6),
        ("pop", 61.0, 0.5)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_book_stack")
