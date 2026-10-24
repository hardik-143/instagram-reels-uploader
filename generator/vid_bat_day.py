#!/usr/bin/env python3
"""What if you were a bat for a day? (Halloween week)
Bats are the only mammals capable of true flight; wings are stretched skin over long finger bones; over 1,400 species
(~1 in 5 mammals) (Ontario Parks); hanging: body weight locks the talons, almost no energy (LiveScience);
echolocation at frequencies higher than humans can hear; bats are not blind (NPS via Forest Preserve of Will County);
a single bat can eat thousands of insects a night; India ~135 species (State of India's Bats Report 2024-25);
Indian flying fox wingspan 1.2-1.5 m, eats guava, mango, fig, disperses seeds (Animal Diversity Web);
only 3 vampire bat species, all in Latin America.
Twist: none in India; India's greater false vampire bat (Lyroderma/Megaderma lyra) is carnivorous - insects, fish,
lizards, frogs, even other bats - but does not drink blood.
Safety: never touch a wild bat."""
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

# ---------------------------------------------------------------- new character: a friendly fruit bat
FUR, DARKF, WING, BELLY = (120, 84, 70), (84, 56, 48), (96, 70, 92), (176, 136, 112)

def batty(B, T, talk=0.0, blink=False, look=(0, 0), state=1):
    """state: 1 = flying (flapping wings), "fold" = wings wrapped (for hanging), "big" = flying fox colours."""
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
    fur, wing = (FUR, WING) if state != "big" else ((176, 110, 60), (90, 62, 52))
    if state == "fold":
        PG([(62, 92), (100, 80), (138, 92), (146, 150), (128, 186), (100, 194), (72, 186), (54, 150)], wing)
        LN([(100, 96), (100, 190)], 2.0)
        EL((76, 96, 124, 168), BELLY, w=0)
    else:
        f = math.sin(T * 9)
        tip = 70 - 46 * f          # wing-tip height
        for s in (-1, 1):
            xo = lambda x: 100 + s * x
            pts = [(xo(30), 96), (xo(66), tip + 20), (xo(96), tip), (xo(92), tip + 40), (xo(78), tip + 52),
                   (xo(66), tip + 48), (xo(56), 140), (xo(38), 150), (xo(28), 140)]
            PG(pts, wing)
            LN([(xo(30), 104), (xo(66), tip + 22), (xo(96), tip + 2)], 2.0)
            LN([(xo(66), tip + 22), (xo(66), tip + 46)], 1.8)
        EL((62, 92, 138, 172), fur)
        EL((80, 112, 120, 164), BELLY, w=0)
    # head + ears
    for s in (-1, 1):
        PG([(100 + s * 18, 52), (100 + s * 40, 12), (100 + s * 44, 58)], fur)
        PG([(100 + s * 24, 50), (100 + s * 38, 24), (100 + s * 39, 54)], (236, 160, 160), w=0)
    EL((62, 38, 138, 110), fur)
    EL((70, 84, 82, 92), (255, 140, 140), w=0); EL((118, 84, 130, 92), (255, 140, 140), w=0)
    for x in (84, 116):
        r = 11
        if blink:
            d.arc([(x - r) * u, (68 - r * 0.7) * u, (x + r) * u, (68 + r * 0.7) * u], 200, 340, fill=OUTL, width=lw(3))
            continue
        EL((x - r, 68 - r * 1.1, x + r, 68 + r * 1.1), WHITE, w=2.2)
        px, py = x + look[0] * 4.5, 68 + look[1] * 4.5
        EL((px - 5.5, py - 6.5, px + 5.5, py + 6.5), (25, 20, 30), w=0)
        EL((px - 4.5, py - 5.5, px - 1, py - 2), WHITE, w=0)
    EL((95, 76, 105, 82), DARKF, w=0)    # nose
    if talk > 0.08:
        h = 4 + 12 * talk
        EL((89, 88, 111, 92 + h), (125, 28, 48), w=1.8)
    else:
        d.arc([88 * u, 82 * u, 112 * u, 98 * u], 20, 160, fill=OUTL, width=lw(2.6))
    PG([(93, 95), (97, 95), (95, 101)], WHITE, w=1.0)   # tiny cute fangs
    PG([(103, 95), (107, 95), (105, 101)], WHITE, w=1.0)
    return L.reduce(2)

_draw_orig = E.draw_char
def draw_char(kind, B, T, talk=0.0, blink=False, look=(0, 0), state=1):
    if kind == "batty":
        return batty(B, T, talk, blink, look, state)
    return _draw_orig(kind, B, T, talk, blink, look, state)
E.draw_char = draw_char

# ---------------------------------------------------------------- props
def moon_disc(d, x=840, y=520, r=90):
    d.ellipse([x - r, y - r, x + r, y + r], fill=(250, 240, 200))
    for dx, dy, rr in ((-30, -20, 18), (25, 30, 14), (20, -35, 10)):
        d.ellipse([x + dx - rr, y + dy - rr, x + dx + rr, y + dy + rr], fill=(230, 218, 176))

def fly_pos(T):
    return (540 + 140 * math.sin(T * 0.9), 1080 + 40 * math.sin(T * 1.8), 640)

def fly_props(frame, d, T, sc):
    moon_disc(d, 860, 620, 80)
    lt = T - sc["s"]
    if lt > 1.0: top_label(frame, "THE ONLY FLYING MAMMAL", 380, YEL, 58)

def branch(d, y=700):
    d.line([(0, y), (1080, y - 30)], fill=(110, 76, 50), width=34)
    for x, dy in ((220, -1), (760, 1)):
        d.line([(x, y - 10), (x + 60, y - 80 * dy - 20)], fill=(110, 76, 50), width=16)
        d.ellipse([x + 40, y - 80 * dy - 60, x + 120, y - 80 * dy], fill=(70, 130, 70))

def hang_props(frame, d, T, sc):
    branch(d, 690)
    for x in (500, 580):    # feet gripping the branch
        d.line([(x, 676), (x, 780)], fill=OUTL, width=8)
        d.arc([x - 16, 664, x + 16, 696], 180, 360, fill=OUTL, width=6)
    lt = T - sc["s"]
    if lt > 1.0: top_label(frame, "UPSIDE DOWN = BEDTIME", 380, YEL, 58)
    if lt > 3.5:
        for i, ch in enumerate("zzz"):
            l = label(ch, 50 + 10 * i, WHITE)
            comp(frame, l, 720 + 40 * i, 1180 - 50 * i - 10 * math.sin(T * 3 + i))

def echo_props(frame, d, T, sc):
    lt = T - sc["s"]
    # sound rings going right, echo rings coming back from a moth
    mx, my = 880, 960
    d.ellipse([mx - 26, my - 18, mx + 26, my + 18], fill=(230, 220, 170), outline=OUTL, width=4)
    d.ellipse([mx - 50, my - 40, mx - 6, my + 6], fill=(240, 236, 210), outline=OUTL, width=3)
    d.ellipse([mx + 6, my - 40, mx + 50, my + 6], fill=(240, 236, 210), outline=OUTL, width=3)
    if lt > 1.0:
        for k in range(4):
            ph = ((T * 0.9 + k * 0.25) % 1.0)
            r = 60 + 380 * ph
            a = int(255 * (1 - ph))
            d.arc([400 - r, 1020 - r, 400 + r, 1020 + r], 300, 350, fill=(120, 220, 255), width=8)
            r2 = 40 + 300 * ((ph + 0.5) % 1.0)
            d.arc([mx - r2, my - r2, mx + r2, my + r2], 150, 200, fill=(255, 200, 90), width=6)
        top_label(frame, "ECHOLOCATION", 380, YEL, 72)

def eyes_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 1.0: top_label(frame, "BATS ARE NOT BLIND", 380, YEL, 64)
    # a samosa on the right
    x, y = 830, 1200
    d.polygon([(x - 90, y + 60), (x + 90, y + 60), (x, y - 90)], fill=(232, 168, 80), outline=OUTL, width=6)
    d.line([(x - 40, y + 10), (x + 20, y - 30)], fill=(200, 130, 60), width=5)

def bugs(d, T, n, alive=1.0):
    for k in range(n):
        if k / n >= alive: continue
        x = 540 + 400 * math.sin(T * (0.8 + k * 0.11) + k * 1.9)
        y = 620 + 110 * math.sin(T * (1.2 + k * 0.07) + k)
        fl = 6 * math.sin(T * 40 + k)
        d.ellipse([x - 18, y - 30 - fl, x + 2, y - 4], fill=(220, 230, 255), outline=OUTL, width=3)
        d.ellipse([x - 2, y - 30 + fl, x + 18, y - 4], fill=(220, 230, 255), outline=OUTL, width=3)
        d.line([(x - 22, y), (x + 22, y)], fill=OUTL, width=8)

def dinner_props(frame, d, T, sc):
    lt = T - sc["s"]
    bugs(d, T, 10, 1.0 - clamp((lt - 2.0) / 4.0))
    if lt > 1.0: top_label(frame, "THOUSANDS OF INSECTS A NIGHT", 380, YEL, 50)

def india_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 1.0: top_label(frame, "INDIA: ~135 BAT SPECIES", 380, YEL, 60)
    if lt > 3.4:
        l = label("WINGSPAN: UP TO 1.5 M", 52, WHITE); comp(frame, l, 540 - l.width / 2, 480)

def fruit(d, x, y, kind):
    if kind == "mango":
        d.ellipse([x - 40, y - 52, x + 40, y + 52], fill=(250, 186, 50), outline=OUTL, width=5)
        d.ellipse([x - 28, y - 44, x - 2, y - 10], fill=(255, 120, 60))
    elif kind == "guava":
        d.ellipse([x - 44, y - 44, x + 44, y + 44], fill=(150, 210, 90), outline=OUTL, width=5)
    else:
        d.ellipse([x - 34, y - 38, x + 34, y + 38], fill=(150, 70, 120), outline=OUTL, width=5)
    d.line([(x, y - 50), (x + 6, y - 70)], fill=(90, 60, 40), width=6)

def seeds_props(frame, d, T, sc):
    lt = T - sc["s"]
    branch(d, 640)
    for x, k in ((180, "mango"), (540, "guava"), (900, "fig")):
        fruit(d, x, 730, k)
    if lt > 3.0:   # seeds fall and sprout
        for i, x in enumerate((240, 470, 700, 880)):
            q = clamp((lt - 3.0 - i * 0.3) / 1.0)
            y = 840 + 450 * q
            if q < 1:
                d.ellipse([x - 10, y - 14, x + 10, y + 14], fill=(90, 60, 40))
            else:
                g = clamp((lt - 4.0 - i * 0.3) / 0.8)
                d.line([(x, 1290), (x, 1290 - 60 * g)], fill=(60, 150, 60), width=7)
                d.ellipse([x - 26 * g, 1290 - 60 * g - 14, x, 1290 - 60 * g + 6], fill=(90, 190, 90))
                d.ellipse([x, 1290 - 60 * g - 14, x + 26 * g, 1290 - 60 * g + 6], fill=(90, 190, 90))

def pumpkin(d, x, y, r=90):
    for dx in (-0.55, 0.55, 0):
        d.ellipse([x + dx * r - r * 0.6, y - r * 0.8, x + dx * r + r * 0.6, y + r * 0.8], fill=(240, 130, 30),
                  outline=OUTL, width=5)
    d.rectangle([x - 10, y - r * 0.8 - 30, x + 10, y - r * 0.8 + 4], fill=(80, 130, 50), outline=OUTL, width=4)
    d.polygon([(x - 45, y - 20), (x - 20, y - 20), (x - 32, y - 45)], fill=(255, 230, 100))
    d.polygon([(x + 20, y - 20), (x + 45, y - 20), (x + 32, y - 45)], fill=(255, 230, 100))
    d.chord([x - 50, y - 10, x + 50, y + 40], 0, 180, fill=(255, 230, 100))

def vamp_props(frame, d, T, sc):
    lt = T - sc["s"]
    pumpkin(d, 830, 1180, 95)
    if lt > 1.0: top_label(frame, "ONLY 3 OF 1,400+", 380, YEL, 70)

def twist_props(frame, d, T, sc):
    lt = T - sc["s"]
    if lt > 1.0: top_label(frame, "0 VAMPIRE BATS IN INDIA", 380, YEL, 58)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="fly", s=4.0, e=11.0, bg="night", clock="SUNSET: WAKE UP", char="batty", pos=fly_pos,
         props=fly_props, look=(0.4, 0),
         narr="You'd be the only MAMMAL that can truly FLY. Your wings are skin stretched over long FINGERS.",
         n_at=4.2, say="Look, no FEATHERS!", say_at=7.6, pitch=700, bubble_y=760),
    dict(id="hang", s=11.0, e=18.0, bg="night", clock="SUNRISE: SLEEP", char="batty", state="fold",
         pos=(540, 1000, 600), rot=lambda T: 180 + 4 * math.sin(T * 1.5), props=hang_props, look=(0, 0),
         narr="Bedtime is UPSIDE DOWN. Your body weight LOCKS your claws, so hanging takes almost no effort.",
         n_at=11.2),
    dict(id="echo", s=18.0, e=25.0, bg="night", clock="NIGHT VISION", char="batty", pos=(330, 1080, 560),
         props=echo_props, look=(0.7, -0.3),
         narr="To find food in the dark, you SHOUT. The ECHOES are too high-pitched for HUMANS to hear.",
         n_at=18.2, say="HELLO? Moth?", say_at=21.6, pitch=760, bubble_y=780),
    dict(id="eyes", s=25.0, e=32.0, bg="night", clock="MYTH BUSTED", char="batty", pos=(380, 1080, 600),
         props=eyes_props, look=(0.8, 0.4),
         narr="And no, you wouldn't be BLIND. All bats can SEE, and many see quite well.", n_at=25.2,
         say="I can see your SAMOSA.", say_at=28.4, pitch=700, bubble_y=760),
    dict(id="dinner", s=32.0, e=39.0, bg="night", clock="DINNER TIME", char="batty", pos=fly_pos,
         props=dinner_props, look=(0.3, -0.5),
         narr="One bat can eat THOUSANDS of insects in a single night. MOSQUITOES, beware.", n_at=32.2,
         say="Crunchy SNACKS!", say_at=35.6, pitch=700, bubble_y=780),
    dict(id="india", s=39.0, e=46.0, bg="night", clock="INDIAN FLYING FOX", char="batty", state="big",
         pos=(540, 1100, 680), props=india_props, look=(0, 0.3),
         narr="India has about 135 bat SPECIES. The INDIAN FLYING FOX has wings up to 1.5 M wide.", n_at=39.2,
         say="I'm the BIG one!", say_at=42.8, pitch=420, bubble_y=760),
    dict(id="seeds", s=46.0, e=53.0, bg="night", clock="NIGHT GARDENER", char="batty", state="big",
         pos=(540, 1080, 460), props=seeds_props, look=(0.3, -0.3),
         narr="Fruit bats eat MANGO, GUAVA and FIGS, then drop the SEEDS that grow new trees.", n_at=46.2,
         say="Free GARDENING!", say_at=49.6, pitch=440, bubble_y=470),
    dict(id="vamp", s=53.0, e=60.0, bg="night", clock="HALLOWEEN WEEK", char="batty", pos=(360, 1080, 600),
         props=vamp_props, look=(0.6, 0),
         narr="Halloween's big fear: VAMPIRES. But only 3 of 1,400+ bat species drink BLOOD.", n_at=53.2,
         say="Ew, no THANKS.", say_at=56.6, pitch=700, bubble_y=760),
    dict(id="twist", s=60.0, e=67.0, bg="twist", clock="PLOT TWIST", char="batty", pos=(540, 1080, 640),
         props=twist_props, twist=True, look=(0, 0.2),
         narr="Twist: none live in India. Our 'FALSE VAMPIRE' bat hunts insects, fish and lizards. No BLOOD!",
         n_at=60.2, say="Wrong NAME, yaar!", say_at=63.6, pitch=700, bubble_y=700),
    dict(id="outro", s=67.0, e=72.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        p = ease_back(clamp((T - 1.9) / 0.4))
        if p > 0.05: paste_c(frame, batty(420, T, 0, False, (0, 0.2)), 540, 1470, p)

cfg = dict(
    total=72.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 520, 0.2, "pop"),
        (title([("YOU WERE A", WHITE)], 140), 720, 0.75, "right"),
        (title([("BAT", YEL)], 200), 880, 1.05, "pop"),
        (title([("FOR A DAY?", WHITE)], 130), 1040, 1.5, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" swap", WHITE)], 100), 470, 0.15),
                      (title([("for one night?", YEL)], 100), 600, 0.45)],
               row=[("batty", 1), ("moon", 1), ("kid", 1), ("mosquito", 1), ("batty", "big")],
               note=text_sprite([("Bats are friends, but ", WHITE), ("never touch a wild bat.", YEL)], 40, stroke=6)),
    music=[dict(t0=0.2, t1=4.0, drums=False, minor=True), dict(t0=4.0, t1=18.0, melody=True),
           dict(t0=18.0, t1=25.0, drums=False, minor=True), dict(t0=25.0, t1=53.0, melody=True),
           dict(t0=53.0, t1=59.85, drums=False, minor=True), dict(t0=67.0, t1=72.0, melody=True)],
    drones=[dict(t0=53.2, dur=6.5, g=0.04), dict(t0=60.2, dur=6.5, g=0.05)],
    fx=[("whoosh", 4.8, 0.5), ("whoosh", 7.0, 0.4), ("wind", 11.2, 0.2, dict(dd=6.5)), ("tick", 19.4, 0.5, dict(f=3400)),
        ("tick", 20.2, 0.5, dict(f=3400)), ("tick", 21.0, 0.5, dict(f=3400)), ("ding", 26.4, 0.3),
        ("click", 34.6, 0.8), ("click", 35.2, 0.8), ("click", 36.0, 0.8), ("pop", 40.4, 0.6),
        ("pop", 49.4, 0.4), ("pop", 49.8, 0.4), ("pop", 50.2, 0.4), ("powerdown", 54.0, 0.4)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_were_a_bat_for_a_day")
