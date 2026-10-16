#!/usr/bin/env python3
"""What if blue whales vanished forever? Krill, whale poop, phytoplankton, and the real-world krill crash."""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp, text_sprite

GONE = 20.5   # the whales swim away for good

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def krill(d, T, n=22, y0=880, y1=1300, alive=1.0, scale=1.0):
    for k in range(n):
        if k / n >= alive: continue
        x = (k * 157 + T * (30 + k % 4 * 12)) % 1180 - 50
        y = y0 + (k * 97) % (y1 - y0) + 14 * math.sin(T * 2 + k)
        s = scale * (1 + 0.3 * (k % 3))
        d.ellipse([x - 16 * s, y - 6 * s, x + 16 * s, y + 6 * s], fill=(255, 120, 110), outline=OUTL, width=2)
        d.ellipse([x + 8 * s, y - 4 * s, x + 13 * s, y + 1 * s], fill=OUTL)

def size_props(frame, d, T, sc):
    # ruler under the whale
    q = clamp((T - sc["s"] - 0.5) / 1.2)
    x1 = 90 + 900 * q
    d.line([(90, 1290), (x1, 1290)], fill=WHITE, width=8)
    d.line([(90, 1265), (90, 1315)], fill=WHITE, width=8)
    if q >= 1:
        d.line([(990, 1265), (990, 1315)], fill=WHITE, width=8)

def food_props(frame, d, T, sc):
    krill(d, T, n=26, y0=420, y1=880)

def vanish_pos(T):
    q = clamp((T - GONE) / 1.4)
    return (540 + 1100 * q * q, 1010 - 120 * q, 520)

def vanish_props(frame, d, T, sc):
    if T >= GONE + 1.2:
        l = label("0 BLUE WHALES", 64, YEL)
        comp(frame, l, 540 - l.width / 2, 400)

def boom_props(frame, d, T, sc):
    lt = T - sc["s"]
    krill(d, T, n=34, y0=420, y1=880, alive=0.3 + 0.7 * clamp(lt / 3))

def poop_props(frame, d, T, sc):
    lt = T - sc["s"]
    # brown plume rising toward the surface, green phytoplankton blooming around it
    for k in range(9):
        ph = (lt * 0.35 + k / 9) % 1.0
        x = 300 + 40 * math.sin(k * 2.1 + lt) - 60 * ph
        y = 1240 - 820 * ph
        r = 18 + 10 * (k % 3)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(150, 104, 60))
    g = clamp((lt - 2.5) / 3)
    for k in range(18):
        if k / 18 >= g: continue
        x = 120 + (k * 211) % 860 + 12 * math.sin(T * 2 + k)
        y = 380 + (k * 67) % 260
        d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=(90, 200, 110), outline=(30, 110, 50), width=3)

def oxygen_props(frame, d, T, sc):
    for k in range(12):
        ph = (T * 0.3 + k / 12) % 1.0
        x = 540 + 380 * math.sin(k * 1.9)
        y = 1300 - 900 * ph
        r = 14 + 6 * (k % 3)
        d.ellipse([x - r, y - r, x + r, y + r], outline=(230, 250, 255), width=5)

def whaling_props(frame, d, T, sc):
    l = label("~360,000", 92, YEL)
    comp(frame, l, 540 - l.width / 2, 380)

def crash_props(frame, d, T, sc):
    lt = T - sc["s"]
    krill(d, T, n=30, y0=500, y1=880, alive=1.0 - 0.8 * ease_out(clamp((lt - 1.0) / 2.5)))
    if lt > 3.5:
        l = label("KRILL -80%", 72, YEL)
        comp(frame, l, 540 - l.width / 2, 390)

def song_props(frame, d, T, sc):
    lt = T - sc["s"]
    for k in range(3):
        r = ((lt * 160) + k * 120) % 360
        a = clamp(1 - r / 360)
        c = (int(160 + 90 * a), int(210 + 40 * a), 255)
        d.arc([300 - r, 1000 - r, 300 + r, 1000 + r], 200, 340, fill=c, width=6)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="size", s=4.0, e=11.0, bg="sea", clock="UP TO 33 M", char="whale", pos=(540, 1010, 560),
         props=size_props, look=(0.3, 0),
         narr="Blue whales are the BIGGEST animals ever known: up to 33 M long.", n_at=4.2, narr_y=1500,
         say="I'm kind of a BIG deal.", say_at=6.8, pitch=160),
    dict(id="food", s=11.0, e=18.0, bg="sea", clock="16 TONNES A DAY", char="whale", pos=(540, 1020, 520),
         props=food_props, look=(0.4, -0.4),
         narr="One blue whale can gulp about 16 TONNES of krill in a day.", n_at=11.2, narr_y=1500,
         say="Just a light SNACK.", say_at=13.8, pitch=160),
    dict(id="vanish", s=18.0, e=25.0, bg="sea", clock="GONE FOREVER", char="whale", pos=vanish_pos,
         props=vanish_props, look=(0.6, 0),
         narr="Now imagine every blue whale on Earth... GONE. Forever.", n_at=18.2, narr_y=1500,
         say="Bye, OCEAN!", say_at=19.0, pitch=160),
    dict(id="boom", s=25.0, e=32.0, bg="sea", clock="MORE KRILL?", char="fish", pos=(540, 1030, 480),
         props=boom_props, look=(0, -0.4),
         narr="You'd think krill would BOOM with no giants eating them.", n_at=25.2, narr_y=1500,
         say="Free BUFFET for everyone!", say_at=27.8, pitch=520),
    dict(id="poop", s=32.0, e=39.0, bg="sea", clock="WHALE POOP", char="whale", pos=(700, 1030, 440),
         props=poop_props, look=(-0.4, -0.4),
         narr="But whale POOP brings iron up, feeding tiny ocean plants: PHYTOPLANKTON.", n_at=32.2, narr_y=1500,
         say="Gross... but IMPORTANT.", say_at=35.0, pitch=160),
    dict(id="oxygen", s=39.0, e=46.0, bg="ocean", clock="ABOUT HALF", char="earth", pos=(540, 1020, 480),
         props=oxygen_props, look=(0, -0.3),
         narr="Ocean plankton make roughly HALF of the oxygen produced on Earth.", n_at=39.2, narr_y=1500,
         say="Thank you, PLANKTON!", say_at=41.9, pitch=300),
    dict(id="whaling", s=46.0, e=53.0, bg="sea", clock="THE 1900s", char="whale", pos=(540, 1030, 480),
         props=whaling_props, look=(0, 0.4),
         narr="This almost HAPPENED. Whaling killed about 360,000 blue whales in the 1900s.", n_at=46.2, narr_y=1500,
         say="We nearly VANISHED.", say_at=49.4, pitch=140),
    dict(id="twist", s=53.0, e=60.0, bg="sea", clock="PLOT TWIST", char="fish", pos=(540, 1040, 440),
         props=crash_props, twist=True, look=(0, -0.3),
         narr="Twist: krill didn't boom. In hunted waters they CRASHED by over 80%.", n_at=53.2, narr_y=1500,
         say="No whales... LESS food?!", say_at=56.6, pitch=520),
    dict(id="hope", s=60.0, e=67.0, bg="sea", clock="PROTECTED 1966", char="whale", state="wink",
         pos=(560, 1010, 520), props=song_props, look=(0, 0),
         narr="Protected since 1966, they're returning. Their songs were recorded off LAKSHADWEEP!", n_at=60.2, narr_y=1500,
         say="Singing near INDIA!", say_at=63.6, pitch=170),
    dict(id="outro", s=67.0, e=72.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        x = 540 + 30 * math.sin(T * 2); y = 1420 + 16 * math.sin(T * 3)
        paste_c(frame, draw_char("whale", 380, T, 0, False, (0, 0), 1), x, y, ease_back((T - 1.9) / 0.4))

cfg = dict(
    total=72.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("BLUE WHALES", WHITE)], 140), 770, 0.75, "right"),
        (title([("VANISHED", WHITE)], 140), 915, 1.05, "left"),
        (title([("...", WHITE), ("FOREVER?", YEL)], 100), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Should ", WHITE), ("WE", YEL), (" save", WHITE)], 100), 470, 0.15),
                      (title([("the giants?", YEL)], 116), 600, 0.45)],
               row=[("whale", 1), ("fish", 1), ("earth", 1), ("cloud", 1), ("whale", "wink")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=18.0), dict(t0=18.0, t1=25.0, drums=False, minor=True),
           dict(t0=25.0, t1=46.0, melody=True), dict(t0=46.0, t1=52.85, drums=False, minor=True),
           dict(t0=60.0, t1=72.0, melody=True)],
    fx=[("waves", 0.3, 0.3, dict(dd=4.0)), ("splash", 4.4, 0.7), ("underwater", 11.0, 0.4, dict(dd=7.0)),
        ("bubbles", 11.3, 0.5, dict(dd=6.0)), ("whoosh", GONE, 1.0), ("splash", GONE + 0.6, 0.6),
        ("underwater", 25.0, 0.4, dict(dd=14.0)), ("bubbles", 32.3, 0.6, dict(dd=6.0)),
        ("bubbles", 39.2, 0.4, dict(dd=6.0)), ("gale", 46.0, 0.3, dict(dd=7.0)),
        ("powerdown", 54.2, 0.6), ("waves", 60.2, 0.4, dict(dd=6.5))],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_blue_whales_vanished")
