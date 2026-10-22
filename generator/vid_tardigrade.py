#!/usr/bin/env python3
"""What if you were a tardigrade? Water bears: 8 legs, usually under ~1 mm (EBSCO); live in moss worldwide, found
5,486 m up the Himalayas (EBSCO); dry out into a 'tun'; Antarctic moss frozen at -20 C from 1983 to 2014 (30+ years)
revived and laid eggs (NIPR / Tsujimoto 2016); median lethal dose ~5,000 Gy gamma vs 5-10 Gy for humans (Wikipedia,
Horikawa 2006); FOTON-M3 2007: dried tardigrades 10 days exposed to space, >68% of UV-shielded revived (Jonsson 2008).
Twist: active Ramazzottius varieornatus: 24 h at 37.1 C killed half (Neves et al. 2020, Sci. Reports)."""
import math
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, comp, paste_c, ease_back, ease_out, clamp, text_sprite

_txt = {}
def label(txt, size=56, col=WHITE):
    k = (txt, size, col)
    if k not in _txt: _txt[k] = text_sprite([(txt, col)], size, stroke=8)
    return _txt[k]

def top_label(frame, txt, y=380, col=YEL, size=68):
    l = label(txt, size, col)
    comp(frame, l, 540 - l.width / 2, y)

# ---------------------------------------------------------------- new character: a chubby water bear
BODY, SHADE, CLAW = (236, 200, 176), (206, 160, 138), (90, 60, 50)

def tardi(B, T, talk=0.0, blink=False, look=(0, 0), state=1):
    S = 2 * B
    L = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    u = S / 200.0
    lw = lambda w: max(1, int(round(w * u)))
    def EL(b, fill, w=2.6):
        d.ellipse([v * u for v in b], fill=fill, outline=OUTL if w else None, width=lw(w) if w else 0)
    if state == "tun":
        # dried-out barrel: a wrinkly brown ball, eyes shut
        EL((40, 70, 160, 170), (196, 150, 104))
        for k in range(4):
            y = 92 + k * 20
            d.arc([52 * u, (y - 12) * u, 148 * u, (y + 12) * u], 10, 170, fill=(150, 104, 70), width=lw(2.4))
        for x in (84, 116):
            d.arc([(x - 10) * u, 96 * u, (x + 10) * u, 110 * u], 200, 340, fill=OUTL, width=lw(3))
        if T % 2.0 < 1.0:
            for i, (zx, zy) in enumerate(((150, 60), (166, 40), (180, 22))):
                s = 6 + i * 3
                d.line([((zx - s) * u, (zy - s) * u), ((zx + s) * u, (zy - s) * u), ((zx - s) * u, (zy + s) * u),
                        ((zx + s) * u, (zy + s) * u)], fill=WHITE, width=lw(2.6))
        return L.reduce(2)
    # 4 stubby legs, each with little claws, wiggling
    for i, x in enumerate((50, 82, 118, 150)):
        k = 5 * math.sin(T * 8 + i * 1.7)
        EL((x - 15, 140 + k * 0.3, x + 15, 182 + k), SHADE)
        for c in (-8, 0, 8):
            d.line([((x + c) * u, (180 + k) * u), ((x + c * 1.5) * u, (190 + k) * u)], fill=CLAW, width=lw(2.6))
    # plump segmented body
    EL((22, 44, 178, 168), BODY)
    for x in (62, 100, 138):
        d.arc([(x - 24) * u, 48 * u, (x + 24) * u, 164 * u], 250, 290, fill=SHADE, width=lw(2.4))
    # face
    for i, x in enumerate((80, 120)):
        r = 12
        if blink or (state == "wink" and i == 1):
            d.arc([(x - r) * u, (86 - r * 0.7) * u, (x + r) * u, (86 + r * 0.7) * u], 200, 340, fill=OUTL, width=lw(3))
            continue
        EL((x - r, 86 - r * 1.1, x + r, 86 + r * 1.1), WHITE, w=2.2)
        px, py = x + look[0] * 5, 86 + look[1] * 5
        EL((px - 6, py - 7, px + 6, py + 7), (25, 20, 30), w=0)
        EL((px - 5, py - 6, px - 1, py - 2), WHITE, w=0)
    EL((62, 100, 76, 110), (255, 140, 140), w=0); EL((124, 100, 138, 110), (255, 140, 140), w=0)
    # round tube-like snout
    o = 4 + 10 * talk if talk > 0.08 else 3
    EL((92, 104, 108, 112 + o), (150, 60, 70) if talk > 0.08 else SHADE, w=2.2)
    return L.reduce(2)

_draw_orig = E.draw_char
def draw_char(kind, B, T, talk=0.0, blink=False, look=(0, 0), state=1):
    if kind == "tardi":
        return tardi(B, T, talk, blink, look, state)
    return _draw_orig(kind, B, T, talk, blink, look, state)
E.draw_char = draw_char

def mini(frame, x, y, size, T, state=1, look=(0, 0.2)):
    comp(frame, tardi(size, T, 0, False, look, state), x - size / 2, y - size / 2)

# ---------------------------------------------------------------- props
def moss(d, y0, T):
    d.rectangle([0, y0, W, H], fill=(70, 130, 60))
    for k in range(40):
        x = (k * 61) % 1120 - 20
        h = 40 + (k * 37) % 50 + 6 * math.sin(T * 2 + k)
        d.ellipse([x - 30, y0 - h, x + 30, y0 + 30], fill=(90, 160, 70) if k % 2 else (60, 140, 60))

def meet_props(frame, d, T, sc):
    moss(d, 1250, T)
    lt = T - sc["s"]
    if lt > 0.5:
        top_label(frame, "UNDER 1 MM LONG", 380, YEL, 72)

def mountain_props(frame, d, T, sc):
    lt = T - sc["s"]
    d.polygon([(-100, 1650), (300, 1100), (520, 1250), (800, 920), (1180, 1650)], fill=(120, 130, 160), outline=OUTL)
    d.polygon([(800, 920), (730, 1020), (765, 1005), (800, 1045), (835, 1005), (870, 1020)], fill=WHITE)
    d.polygon([(300, 1100), (250, 1170), (300, 1155), (350, 1170)], fill=WHITE)
    # tiny moss patch with a water bear on the peak
    d.ellipse([730, 890, 870, 940], fill=(80, 150, 60), outline=OUTL, width=4)
    mini(frame, 800, 850, 140, T)
    if lt > 0.5:
        top_label(frame, "5,500 M UP", 380, YEL, 76)

def tun_props(frame, d, T, sc):
    moss(d, 1300, T)
    lt = T - sc["s"]
    if lt > 0.5:
        top_label(frame, "DRY = 'TUN' MODE", 380, YEL, 68)

def ice_props(frame, d, T, sc):
    lt = T - sc["s"]
    d.rectangle([0, 1300, W, H], fill=(225, 240, 252))
    # ice block with a frozen water bear, cracking open at the end
    crack = clamp((lt - 3.4) / 0.6)
    d.rounded_rectangle([140, 900, 460, 1260], radius=24, fill=(190, 225, 250), outline=OUTL, width=6)
    mini(frame, 300, 1080, 210, T if crack > 0 else 0, "tun" if crack < 1 else 1)
    if crack > 0:
        d.line([(180, 940), (260, 1040), (230, 1120), (300, 1240)], fill=WHITE, width=7)
        d.line([(420, 930), (360, 1010), (400, 1090)], fill=WHITE, width=7)
    if crack >= 1:
        for k in range(3):
            ex = 230 + k * 70; ey = 1270 + 4 * math.sin(T * 5 + k)
            d.ellipse([ex - 20, ey - 14, ex + 20, ey + 14], fill=(255, 250, 230), outline=OUTL, width=4)
    if lt > 0.5:
        top_label(frame, "30 YEARS ON ICE", 380, YEL, 72)

def rad_props(frame, d, T, sc):
    lt = T - sc["s"]
    # pulsing glow rings around a water bear
    for k in range(4):
        r = 80 + ((lt * 120 + k * 60) % 240)
        a = int(200 * (1 - (r - 80) / 240))
        d.ellipse([300 - r, 1120 - r, 300 + r, 1120 + r], outline=(140, 255, 120), width=8)
    mini(frame, 300, 1120, 230, T, look=(0.4, 0))
    if lt > 0.5:
        top_label(frame, "HUMAN: ~10 GY", 360, WHITE, 58)
    if lt > 2.6:
        top_label(frame, "WATER BEAR: 5,000 GY", 440, YEL, 66)

def space_props(frame, d, T, sc):
    lt = T - sc["s"]
    for k in range(5):
        x = 200 + k * 170 + 30 * math.sin(T * 0.8 + k)
        y = 1180 + 70 * math.sin(T * 1.1 + k * 1.3)
        mini(frame, x, y, 150, T + k, "tun" if lt < 3.6 else 1)
    if lt > 0.5:
        top_label(frame, "10 DAYS IN SPACE", 380, YEL, 72)

def hot_props(frame, d, T, sc):
    lt = T - sc["s"]
    # sweaty water bear + a thermometer
    mini(frame, 260, 1200, 230, T, look=(0.5, -0.2))
    for k in range(3):
        y = 1080 + ((lt * 160 + k * 50) % 150)
        d.ellipse([340 + k * 18, y, 356 + k * 18, y + 24], fill=(120, 190, 255), outline=OUTL, width=3)
    d.rounded_rectangle([860, 760, 920, 1120], radius=30, fill=WHITE, outline=OUTL, width=6)
    lvl = 1080 - 260 * clamp(lt / 2.0)
    d.rectangle([878, lvl, 902, 1100], fill=(230, 40, 50))
    d.ellipse([845, 1080, 935, 1170], fill=(230, 40, 50), outline=OUTL, width=6)
    if lt > 0.8:
        top_label(frame, "37 °C FOR A DAY", 380, YEL, 72)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="meet", s=4.0, e=11.0, bg="day", clock="MEET THE WATER BEAR", char="tardi", pos=(540, 1060, 520),
         props=meet_props, look=(0.2, 0.2),
         narr="You're now a TARDIGRADE: 8 chubby legs, usually under 1 MILLIMETRE long.", n_at=4.2, narr_y=1500,
         say="Call me WATER BEAR!", say_at=6.8, pitch=440),
    dict(id="himalaya", s=11.0, e=18.0, bg="day", clock="WHERE YOU LIVE", char="kid", pos=(240, 1240, 300),
         props=mountain_props, look=(0.6, -0.6),
         narr="Water bears live in moss almost everywhere, even 5,500 M up the HIMALAYAS.", n_at=11.2, narr_y=1500,
         say="Even up THERE?!", say_at=14.6, pitch=400),
    dict(id="tun", s=18.0, e=25.0, bg="day", clock="YOUR SUPERPOWER", char="tardi", state="tun",
         pos=(540, 1110, 460), props=tun_props,
         narr="Your trick: dry out into a little ball called a TUN, with life almost PAUSED.", n_at=18.2, narr_y=1500,
         say="Wake me up LATER...", say_at=21.4, pitch=380),
    dict(id="ice", s=25.0, e=32.0, bg="pole", clock="ANTARCTICA", char="penguin", pos=(780, 1100, 380),
         props=ice_props, look=(-0.6, 0.2),
         narr="Water bears frozen 30 YEARS in Antarctic moss woke up and laid EGGS.", n_at=25.2, narr_y=1500,
         say="Morning, SLEEPYHEAD!", say_at=28.6, pitch=360),
    dict(id="rad", s=32.0, e=39.0, bg="night", clock="RADIATION TEST", char="kid", pos=(800, 1150, 320),
         props=rad_props, look=(-0.6, 0),
         narr="About 10 GY of radiation can kill a human. Water bears survived 5,000.", n_at=32.2, narr_y=1500,
         say="I'll PASS, thanks!", say_at=35.6, pitch=400),
    dict(id="space", s=39.0, e=46.0, bg="space", clock="2007 · ORBIT", props=space_props,
         narr="In 2007, dried water bears spent 10 DAYS exposed to SPACE. Many came back ALIVE.", n_at=39.2,
         narr_y=1500),
    dict(id="twist", s=46.0, e=53.0, bg="hot", clock="PLOT TWIST", char="uncle", pos=(700, 1110, 400),
         props=hot_props, twist=True, look=(-0.6, 0.1),
         narr="Twist: awake water bears in a lab? A day at 37 °C killed HALF of them.", n_at=46.2, narr_y=1500,
         say="That's just a Delhi SUMMER!", say_at=49.4, pitch=150),
    dict(id="outro", s=53.0, e=58.0),
]

def intro_extra(frame, d, T):
    if T >= 1.9:
        x = 540 + 30 * math.sin(T * 2); y = 1420 + 10 * math.sin(T * 5)
        paste_c(frame, tardi(380, T, 0, False, (0, 0.2)), x, y, ease_back((T - 1.9) / 0.4))

cfg = dict(
    total=58.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("YOU WERE A", WHITE)], 130), 770, 0.75, "right"),
        (title([("TARDIGRADE?", YEL)], 140), 915, 1.05, "left"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" swap", WHITE)], 100), 470, 0.15),
                      (title([("with a water bear?", YEL)], 96), 600, 0.45)],
               row=[("tardi", 1), ("penguin", 1), ("kid", 1), ("uncle", 1), ("tardi", "wink")]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=25.0), dict(t0=25.0, t1=32.0, drums=False),
           dict(t0=32.0, t1=39.0, minor=True), dict(t0=39.0, t1=45.85, drums=False, melody=True),
           dict(t0=48.0, t1=58.0, melody=True)],
    fx=[("wind", 11.2, 0.3, dict(dd=6.0)), ("powerdown", 19.0, 0.4), ("wind", 25.2, 0.25, dict(dd=6.0)),
        ("crash", 28.4, 0.4), ("pop", 29.0, 0.5), ("rumble", 32.3, 0.3, dict(dd=3.0)), ("ding", 35.0, 0.3),
        ("pop", 42.6, 0.4), ("pop", 42.8, 0.4), ("pop", 43.0, 0.4)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_you_were_a_tardigrade")
