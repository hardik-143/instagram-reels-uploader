#!/usr/bin/env python3
"""Shared engine for @whatif.wala Reels: characters, backgrounds, captions, bubbles, music and SFX.
A video is a config dict (see vid_*.py). render_video(cfg) writes the mp4."""
import os, sys, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_reel as R
import make_sun as SN
from make_reel import (W, H, FPS, SR, YEL, WHITE, RED, OUTL, CPS, F_TITLE, F_CAP, font, clamp, ease_out,
                       ease_back, comp, paste_c, wrap_words, is_emph, text_sprite, make_bubble, make_clock, grad)

HERE = os.path.dirname(os.path.abspath(__file__))
REEL_KINDS = ("dog", "cat", "cow", "pigeon", "mosquito")
SUN_KINDS = ("sun", "flower", "penguin", "fish", "worm")

def fit(spr, maxw=1030):
    if spr.width > maxw:
        s = maxw / spr.width
        spr = spr.resize((int(spr.width * s), int(spr.height * s)), Image.LANCZOS)
    return spr

def title(segments, size, stroke=10):
    return fit(text_sprite(segments, size, stroke=stroke))

# ================================================================ characters
def draw_char(kind, B, T, talk=0.0, blink=False, look=(0, 0), state=1):
    if kind in REEL_KINDS:
        return R.draw_animal(kind, B, T, talk, blink, look, wink=(state == "wink"))
    if kind in SUN_KINDS:
        return SN.draw_char(kind, B, T, talk, blink, look, state if isinstance(state, (int, float)) else 1)

    S = 2 * B
    L = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    u = S / 200.0
    lw = lambda w: max(1, int(round(w * u)))

    def E(b, fill, w=2.6, dd=None):
        dd = dd or d
        x0, y0, x1, y1 = b
        dd.ellipse([x0 * u, y0 * u, x1 * u, y1 * u], fill=fill, outline=OUTL if w else None,
                   width=lw(w) if w else 0)

    def PG(pts, fill, w=2.6):
        d.polygon([(x * u, y * u) for x, y in pts], fill=fill, outline=OUTL if w else None,
                  width=lw(w) if w else 0)

    def LN(pts, w=2.0, fill=OUTL):
        d.line([(x * u, y * u) for x, y in pts], fill=fill, width=lw(w), joint="curve")

    def RR(b, fill, r, w=2.6):
        d.rounded_rectangle([v * u for v in b], radius=r * u, fill=fill, outline=OUTL if w else None,
                            width=lw(w) if w else 0)

    def eyes(lx, rx, y, r, closed=False, squeeze=False):
        for i, x in enumerate((lx, rx)):
            if squeeze:
                s = 1 if i == 0 else -1
                LN([(x - r * s, y - r * 0.7), (x + r * 0.6 * s, y), (x - r * s, y + r * 0.7)], max(2.2, r * 0.3))
                continue
            if blink or closed or (state == "wink" and i == 1):
                d.arc([(x - r) * u, (y - r * 0.7) * u, (x + r) * u, (y + r * 0.7) * u], 200, 340,
                      fill=OUTL, width=lw(max(2.2, r * 0.27)))
                continue
            E((x - r, y - r * 1.12, x + r, y + r * 1.12), WHITE, w=max(1.6, r * 0.22))
            px, py = x + look[0] * r * 0.38, y + look[1] * r * 0.38
            E((px - r * 0.46, py - r * 0.52, px + r * 0.46, py + r * 0.52), (25, 20, 30), w=0)
            E((px - r * 0.42, py - r * 0.5, px - r * 0.06, py - r * 0.14), WHITE, w=0)

    def mouth(x, y, wd, o, flat=False):
        if flat:
            LN([(x - wd / 2, y), (x + wd / 2, y)], 3); return
        if o > 0.08:
            h = wd * 0.15 + wd * 0.62 * o
            E((x - wd / 2, y - h * 0.3, x + wd / 2, y + h), (125, 28, 48), w=max(1.6, wd * 0.1))
            E((x - wd * 0.3, y + h * 0.35, x + wd * 0.3, y + h * 0.95), (245, 115, 135), w=0)
        else:
            d.arc([(x - wd / 2) * u, (y - wd * 0.3) * u, (x + wd / 2) * u, (y + wd * 0.23) * u], 20, 160,
                  fill=OUTL, width=lw(max(2, wd * 0.11)))

    def cheeks(xl, xr, y, r=8, col=(255, 140, 140)):
        E((xl - r, y - r * 0.6, xl + r, y + r * 0.6), col, w=0)
        E((xr - r, y - r * 0.6, xr + r, y + r * 0.6), col, w=0)

    def outlined_union(shapes, fill, grow=2.6):
        """Draw ellipse/polygon union with a single outer outline."""
        for kind_, data in shapes:
            if kind_ == "e":
                x0, y0, x1, y1 = data
                E((x0 - grow, y0 - grow, x1 + grow, y1 + grow), OUTL, w=0)
            else:
                cx = sum(p[0] for p in data) / len(data); cy = sum(p[1] for p in data) / len(data)
                PG([(x + (x - cx) * 0.06, y + (y - cy) * 0.06) for x, y in data], OUTL, w=0)
        for kind_, data in shapes:
            if kind_ == "e": E(data, fill, w=0)
            else: PG(data, fill, w=0)

    if kind == "earth":
        off = state if isinstance(state, (int, float)) else 0.0
        E((30, 30, 170, 170), (70, 150, 240))
        land = Image.new("RGBA", (S, S), (0, 0, 0, 0)); ld = ImageDraw.Draw(land)
        g = (98, 192, 112)
        for bx, by, bw, bh in ((40, 48, 56, 52), (104, 36, 46, 34), (108, 102, 60, 52), (50, 122, 36, 38),
                               (130, 64, 42, 32), (190, 70, 50, 60), (230, 120, 40, 40)):
            x = ((bx + off) % 280) - 40
            ld.ellipse([x * u, by * u, (x + bw) * u, (by + bh) * u], fill=g)
        mask = Image.new("L", (S, S), 0)
        ImageDraw.Draw(mask).ellipse([31 * u, 31 * u, 169 * u, 169 * u], fill=255)
        L.alpha_composite(Image.composite(land, Image.new("RGBA", (S, S), (0, 0, 0, 0)), mask))
        d.ellipse([30 * u, 30 * u, 170 * u, 170 * u], outline=OUTL, width=lw(2.6))
        cheeks(62, 138, 116, 9)
        eyes(78, 122, 92, 12)
        mouth(100, 128, 28, talk)
    elif kind == "bat":
        RR((90, 2, 110, 54), (70, 46, 46), 6)
        for y in (12, 24, 36):
            LN([(91, y), (109, y + 6)], 2, fill=(200, 60, 60))
        RR((54, 44, 146, 198), (238, 204, 150), 20)
        d.rounded_rectangle([126 * u, 52 * u, 140 * u, 190 * u], radius=6 * u, fill=(218, 180, 124))
        cheeks(70, 130, 126, 7)
        eyes(82, 118, 104, 10.5)
        mouth(100, 134, 22, talk)
    elif kind == "hockey":
        LN([(170, 6), (78, 170), (56, 186), (30, 180)], 13)
        LN([(170, 6), (78, 170), (56, 186), (30, 180)], 8, fill=(170, 108, 58))
        E((46, 46, 154, 154), (250, 250, 246))
        for x, y in ((70, 64), (130, 64), (62, 120), (138, 120), (100, 140)):
            E((x - 4, y - 4, x + 4, y + 4), (220, 220, 214), w=0)
        cheeks(70, 130, 116, 8)
        eyes(80, 120, 92, 11)
        mouth(100, 122, 24, talk)
    elif kind == "football":
        E((38, 38, 162, 162), WHITE)
        def pent(cx, cy, r, rot=0):
            PG([(cx + r * math.cos(math.radians(rot + 72 * i - 90)), cy + r * math.sin(math.radians(rot + 72 * i - 90)))
                for i in range(5)], (36, 34, 40), w=0)
        pent(100, 58, 15); pent(56, 100, 13, 36); pent(144, 100, 13, 36); pent(74, 146, 13); pent(126, 146, 13)
        d.ellipse([38 * u, 38 * u, 162 * u, 162 * u], outline=OUTL, width=lw(2.6))
        cheeks(70, 130, 118, 8)
        eyes(82, 118, 94, 11)
        mouth(100, 126, 24, talk)
    elif kind == "cloud":
        outlined_union([("e", (30, 84, 104, 156)), ("e", (70, 48, 146, 124)), ("e", (110, 80, 180, 152)),
                        ("e", (54, 100, 160, 164))], (250, 250, 255))
        cheeks(80, 124, 124, 7)
        eyes(88, 118, 104, 9)
        mouth(103, 128, 20, talk)
    elif kind == "heart":
        outlined_union([("e", (34, 38, 106, 110)), ("e", (94, 38, 166, 110)),
                        ("p", [(38, 90), (162, 90), (100, 172)])], (232, 50, 72))
        E((52, 52, 78, 72), (255, 130, 150), w=0)
        cheeks(70, 130, 108, 8, (255, 120, 140))
        eyes(80, 120, 86, 10.5)
        mouth(100, 112, 22, talk)
    elif kind == "whale":
        PG([(150, 106), (196, 66), (184, 106), (196, 148)], (78, 128, 200))
        E((92, 138, 134, 184), (70, 118, 188))
        E((12, 56, 178, 162), (92, 146, 214))
        d.chord([12 * u, 56 * u, 178 * u, 162 * u], 20, 160, fill=(204, 228, 248))
        for x in (60, 80, 100, 120):
            LN([(x, 140), (x + 4, 158)], 1.4, fill=(150, 186, 220))
        d.ellipse([12 * u, 56 * u, 178 * u, 162 * u], outline=OUTL, width=lw(2.6))
        cheeks(34, 92, 112, 7)
        eyes(46, 78, 94, 9)
        if talk > 0.08:
            E((34, 116, 70, 122 + 14 * talk), (125, 28, 48), w=1.8)
        else:
            d.arc([22 * u, 104 * u, 92 * u, 126 * u], 25, 155, fill=OUTL, width=lw(2.4))
    elif kind in ("uncle", "kid"):
        skin = (226, 168, 118) if kind == "uncle" else (242, 194, 152)
        puff = state == "puff"
        if puff:
            skin = (238, 150, 130)
        E((32, 92, 54, 124), skin); E((146, 92, 168, 124), skin)
        E((44, 34, 156, 172), skin)
        if kind == "uncle":
            E((40, 66, 64, 112), (150, 150, 156), w=0); E((136, 66, 160, 112), (150, 150, 156), w=0)
            E((82, 44, 114, 62), (244, 200, 154), w=0)
            if state == "hat":
                E((22, 40, 178, 66), (196, 160, 104))
                RR((54, 4, 146, 54), (214, 178, 120), 22)
                d.rectangle([56 * u, 38 * u, 144 * u, 48 * u], fill=(120, 84, 50))
            if state in ("crown", "crown_angry"):
                PG([(60, 46), (56, 6), (78, 28), (100, 0), (122, 28), (144, 6), (140, 46)], (255, 200, 40))
                RR((58, 36, 142, 50), (240, 170, 30), 4)
                for gx, gc in ((80, (220, 40, 60)), (100, (40, 140, 220)), (120, (220, 40, 60))):
                    E((gx - 5, 38, gx + 5, 48), gc, w=1.4)
            angry = state in ("angry", "crown_angry")
            if angry:
                LN([(62, 74), (92, 86)], 4); LN([(138, 74), (108, 86)], 4)
                cheeks(64, 136, 124, 10, (240, 90, 90))
            else:
                d.arc([62 * u, 72 * u, 94 * u, 86 * u], 200, 340, fill=OUTL, width=lw(3))
                d.arc([106 * u, 72 * u, 138 * u, 86 * u], 200, 340, fill=OUTL, width=lw(3))
            eyes(80, 120, 96, 8)
            for x0 in (62, 102):
                d.ellipse([x0 * u, 79 * u, (x0 + 36) * u, 113 * u], outline=OUTL, width=lw(3))
            LN([(98, 95), (102, 95)], 3)
            E((92, 100, 108, 124), (206, 142, 98))
            E((64, 120, 100, 140), (70, 52, 44), w=0); E((100, 120, 136, 140), (70, 52, 44), w=0)
            mouth(100, 148, 24, max(talk, 0.6 if angry and talk > 0 else talk))
        else:
            d.chord([44 * u, 34 * u, 156 * u, 172 * u], 180, 360, fill=(46, 34, 34))
            PG([(46, 96), (60, 78), (74, 92), (88, 74), (102, 90), (116, 74), (130, 92), (144, 78), (154, 96),
                (154, 70), (46, 70)], (46, 34, 34), w=0)
            d.ellipse([44 * u, 34 * u, 156 * u, 172 * u], outline=OUTL, width=lw(2.6))
            if puff:
                E((38, 110, 82, 150), (255, 150, 150)); E((118, 110, 162, 150), (255, 150, 150))
                eyes(80, 120, 104, 10, squeeze=True)
                E((92, 134, 108, 146), (125, 28, 48), w=1.8)
            else:
                cheeks(66, 134, 130, 8)
                eyes(80, 120, 106, 11)
                mouth(100, 138, 24, talk)

    elif kind == "samosa":
        tri = [(100, 22), (184, 178), (16, 178)]
        PG(tri, (234, 174, 70))
        PG([(100, 30), (112, 176), (88, 176)], (216, 152, 54), w=0)
        LN([(100, 28), (100, 174)], 1.6, fill=(196, 132, 44))
        for x, y in ((56, 160), (144, 160), (100, 70), (74, 120), (126, 120)):
            E((x - 3, y - 3, x + 3, y + 3), (196, 132, 44), w=0)
        d.polygon([(x * u, y * u) for x, y in tri], outline=OUTL, width=lw(2.6))
        cheeks(74, 126, 146, 7)
        eyes(84, 116, 124, 9)
        mouth(100, 152, 18, talk)
    elif kind == "trex":
        g, dk = (112, 178, 94), (80, 140, 70)
        a = 7 * math.sin(T * 8)
        for s_ in (-1, 1):
            pts = [(100 + s_ * 34, 150), (100 + s_ * 48, 168 + a * s_), (100 + s_ * 54, 160 + a * s_)]
            LN(pts, 7); LN(pts, 4, fill=g)
        E((36, 28, 164, 150), g)
        E((48, 96, 152, 180), g)
        E((60, 44, 78, 60), dk, w=0); E((122, 48, 140, 64), dk, w=0)
        E((86, 102, 94, 110), dk, w=0); E((106, 102, 114, 110), dk, w=0)
        eyes(74, 126, 78, 11)
        LN([(58, 60), (88, 68)], 3.2); LN([(142, 60), (112, 68)], 3.2)
        top = 132
        if talk > 0.08:
            E((62, top - 4, 138, top + 10 + 30 * talk), (125, 28, 48))
            for x in range(68, 132, 12):
                PG([(x, top - 2), (x + 8, top - 2), (x + 4, top + 8)], WHITE, w=1.2)
        else:
            LN([(62, top + 4), (138, top + 4)], 2.4)
            for x in range(66, 134, 12):
                PG([(x, top + 4), (x + 8, top + 4), (x + 4, top + 12)], WHITE, w=1.2)
    elif kind == "trike":
        E((12, 6, 188, 150), (236, 140, 70))
        E((30, 22, 170, 136), (250, 172, 98), w=0)
        for i in range(9):
            ang = math.radians(200 + i * 17.5)
            x, y = 100 + 86 * math.cos(ang), 78 + 70 * math.sin(ang)
            E((x - 7, y - 7, x + 7, y + 7), (200, 110, 50), w=0)
        PG([(66, 72), (56, 10), (82, 64)], (250, 242, 222))
        PG([(134, 72), (144, 10), (118, 64)], (250, 242, 222))
        E((44, 56, 156, 176), (122, 162, 202))
        PG([(90, 120), (100, 92), (110, 120)], (250, 242, 222))
        PG([(76, 146), (124, 146), (100, 186)], (92, 122, 164))
        cheeks(62, 138, 126, 7)
        eyes(76, 124, 104, 10)
        mouth(100, 160, 18, talk)
    elif kind == "diya":
        fl = 1 + 0.08 * math.sin(T * 23) + 0.05 * math.sin(T * 37)
        PG([(100, 128 - 98 * fl), (122, 98), (100, 128), (78, 98)], (255, 176, 40))
        PG([(100, 128 - 70 * fl), (110, 104), (100, 124), (90, 104)], (255, 238, 150), w=0)
        d.chord([18 * u, 70 * u, 182 * u, 198 * u], 0, 180, fill=(212, 102, 46), outline=OUTL, width=lw(2.6))
        E((18, 118, 182, 150), (212, 102, 46))
        E((30, 123, 170, 145), (244, 176, 60), w=0)
        for x in range(36, 170, 18):
            E((x - 3, 166, x + 3, 172), (250, 210, 120), w=0)
        cheeks(62, 138, 176, 7)
        eyes(80, 120, 160, 9)
        mouth(100, 180, 18, talk)
    elif kind == "ladoo":
        E((36, 36, 164, 164), (250, 162, 44))
        for i in range(26):
            x = 46 + (i * 37) % 108; y = 46 + (i * 53) % 108
            if (x - 100) ** 2 + (y - 100) ** 2 < 58 ** 2:
                E((x - 3, y - 3, x + 3, y + 3), (222, 128, 30), w=0)
        E((56, 52, 92, 76), (255, 204, 110), w=0)
        cheeks(68, 132, 118, 8)
        eyes(80, 120, 94, 11)
        mouth(100, 124, 24, talk)
    elif kind == "moon":
        E((32, 32, 168, 168), (216, 216, 226))
        for b in ((48, 50, 78, 78), (118, 120, 148, 146), (122, 44, 142, 62), (54, 122, 72, 138), (140, 82, 156, 98)):
            E(b, (188, 188, 202), w=0)
        cheeks(64, 136, 116, 8)
        eyes(80, 120, 94, 11)
        mouth(100, 126, 24, talk)
    elif kind == "auto":
        yel, grn = (252, 206, 40), (40, 140, 82)
        for b in ((30, 168, 66, 200), (134, 168, 170, 200), (82, 172, 118, 200)):
            E(b, (34, 34, 38))
        RR((24, 16, 176, 96), yel, 28)
        RR((34, 84, 166, 182), grn, 20)
        RR((48, 36, 152, 100), (192, 228, 246), 14)
        eyes(78, 122, 66, 11)
        E((88, 106, 112, 126), (255, 250, 206))
        mouth(100, 152, 26, talk)
        LN([(24, 60), (10, 52)], 3); E((2, 44, 16, 58), (200, 220, 236))
        LN([(176, 60), (190, 52)], 3); E((184, 44, 198, 58), (200, 220, 236))
    elif kind == "train":
        RR((26, 22, 174, 202), (246, 246, 250), 44)
        d.rectangle([28 * u, 132 * u, 172 * u, 148 * u], fill=(40, 92, 196))
        d.rounded_rectangle([26 * u, 22 * u, 174 * u, 202 * u], radius=44 * u, outline=OUTL, width=lw(2.6))
        RR((44, 40, 156, 108), (32, 42, 62), 22)
        eyes(80, 120, 74, 12)
        E((40, 158, 60, 176), (255, 250, 206)); E((140, 158, 160, 176), (255, 250, 206))
        mouth(100, 170, 26, talk)
    elif kind == "rocket":
        fl = 8 * math.sin(T * 30)
        PG([(78, 168), (122, 168), (100, 204 + fl)], (255, 150, 40), w=0)
        PG([(88, 168), (112, 168), (100, 190 + fl * 0.6)], (255, 236, 140), w=0)
        PG([(62, 120), (36, 176), (70, 166)], (222, 52, 62))
        PG([(138, 120), (164, 176), (130, 166)], (222, 52, 62))
        RR((60, 52, 140, 172), (246, 246, 250), 28)
        PG([(60, 66), (100, 2), (140, 66)], (222, 52, 62))
        d.rectangle([62 * u, 148 * u, 138 * u, 158 * u], fill=(222, 52, 62))
        E((76, 70, 124, 118), (150, 210, 250))
        eyes(90, 110, 94, 7.5)
        cheeks(76, 124, 132, 6)
        mouth(100, 134, 18, talk)
    elif kind == "chai":
        wob = 5 * math.sin(T * 5)
        E((32 - wob, 40 + wob, 168 + wob, 170 - wob), (198, 130, 72))
        E((54, 56, 96, 84), (232, 184, 124), w=0)
        cheeks(66, 134, 120, 8)
        eyes(80, 120, 96, 11)
        mouth(100, 128, 24, talk)
    return L.reduce(2)

# ================================================================ backgrounds
_bg_cache = {}
def bg(name):
    if name in _bg_cache:
        return _bg_cache[name]
    if name in ("intro", "outro", "dog", "cat", "cow", "pigeon", "mosquito", "twist"):
        img = R.build_bg(name)
    elif name in SN.BGS:
        img = SN.BGS[name]
    else:
        img = build_bg(name)
    _bg_cache[name] = img
    return img

def build_bg(kind):
    k = 2
    rng = np.random.default_rng(abs(hash(kind)) % 991)
    G = {
        "sea1721": [(0, (255, 186, 132)), (0.55, (255, 222, 170)), (1, (255, 230, 180))],
        "stadium": [(0, (14, 22, 58)), (0.5, (30, 44, 96)), (1, (30, 44, 96))],
        "gully": [(0, (255, 214, 160)), (1, (255, 196, 140))],
        "living": [(0, (230, 214, 250)), (1, (206, 186, 236))],
        "speed": [(0, (90, 170, 250)), (0.7, (196, 232, 255)), (1, (196, 232, 255))],
        "storm": [(0, (60, 70, 92)), (0.7, (120, 128, 140)), (1, (120, 128, 140))],
        "ocean": [(0, (110, 180, 240)), (0.5, (200, 230, 250)), (1, (200, 230, 250))],
        "pole": [(0, (150, 200, 250)), (0.65, (226, 240, 255)), (1, (226, 240, 255))],
        "pool": [(0, (236, 246, 252)), (0.4, (236, 246, 252)), (0.42, (90, 200, 230)), (1, (30, 140, 200))],
        "sea": [(0, (60, 150, 220)), (0.5, (20, 80, 150)), (1, (8, 30, 70))],
        "cinema": [(0, (24, 12, 30)), (1, (44, 18, 40))],
        "diwali": [(0, (16, 10, 44)), (1, (64, 30, 84))],
        "sweetshop": [(0, (255, 226, 178)), (1, (250, 200, 150))],
        "smog": [(0, (150, 140, 122)), (1, (112, 102, 92))],
        "train": [(0, (214, 232, 224)), (1, (196, 218, 210))],
        "cretaceous": [(0, (255, 160, 104)), (0.6, (255, 214, 156)), (1, (255, 214, 156))],
        "digsite": [(0, (120, 190, 250)), (0.6, (214, 236, 252)), (1, (214, 236, 252))],
        "office": [(0, (214, 226, 240)), (1, (190, 206, 226))],
        "hot": [(0, (255, 130, 60)), (0.6, (255, 196, 110)), (1, (255, 206, 120))],
        "bedroom": [(0, (40, 40, 90)), (1, (80, 60, 120))],
    }[kind]
    img = grad(G, W * k, H * k); d = ImageDraw.Draw(img)
    E = lambda b, f: d.ellipse([v * k for v in b], fill=f)
    Rr = lambda b, f, r=0: d.rounded_rectangle([v * k for v in b], radius=r * k, fill=f) if r else d.rectangle([v * k for v in b], fill=f)
    PG = lambda pts, f: d.polygon([(x * k, y * k) for x, y in pts], fill=f)
    LN = lambda pts, f, w: d.line([(x * k, y * k) for x, y in pts], fill=f, width=int(w * k))
    def cloud(cx, cy, s=1.0, col=WHITE):
        for dx, r in ((-60, 50), (0, 70), (60, 50)):
            E((cx + (dx - r) * s, cy - r * s, cx + (dx + r) * s, cy + r * s), col)

    if kind == "sea1721":
        cloud(230, 520, 0.9); cloud(860, 640, 0.7)
        Rr((0, 1080, 1080, 1340), (70, 150, 200))
        for y in range(1110, 1330, 40):
            for x in range(int(rng.uniform(-40, 0)), 1080, 120):
                LN([(x, y), (x + 50, y)], (130, 200, 236), 4)
        # sailing ship (back right)
        PG([(700, 1060), (1020, 1060), (980, 1120), (740, 1120)], (110, 62, 40))
        for x, h in ((800, 300), (900, 340)):
            LN([(x, 1060), (x, 1060 - h)], (80, 50, 34), 8)
            PG([(x - 70, 1060 - h + 30), (x + 70, 1060 - h + 50), (x + 60, 1060 - h * 0.45), (x - 60, 1060 - h * 0.42)], (250, 244, 228))
        PG([(900, 1060 - 340), (960, 1060 - 320), (900, 1060 - 300)], (220, 50, 50))
        Rr((0, 1330, 1080, 1920), (240, 214, 160))
        E((-200, 1290, 500, 1400), (240, 214, 160))
        LN([(130, 1360), (150, 1100), (180, 980)], (120, 80, 50), 22)
        for a in range(0, 360, 60):
            ra = math.radians(a)
            PG([(180, 980), (180 + 150 * math.cos(ra), 980 + 70 * math.sin(ra) + 30), (180 + 120 * math.cos(ra + 0.3), 980 + 60 * math.sin(ra + 0.3))], (60, 150, 80))
    elif kind == "stadium":
        for x in (140, 940):
            LN([(x, 700), (x, 260)], (90, 90, 110), 10)
            Rr((x - 80, 200, x + 80, 270), (60, 60, 80), 10)
            for j in range(4):
                E((x - 70 + j * 38, 210, x - 42 + j * 38, 238), (255, 250, 220))
        Rr((0, 900, 1080, 1180), (40, 40, 70))
        for _ in range(900):
            x, y = rng.uniform(0, W), rng.uniform(910, 1170)
            c = [(240, 90, 90), (90, 160, 240), (250, 220, 90), (250, 250, 250), (120, 220, 140)][rng.integers(0, 5)]
            E((x - 5, y - 5, x + 5, y + 5), c)
        Rr((0, 1180, 1080, 1920), (60, 150, 200))
        for y in range(1180, 1920, 120):
            Rr((0, y, 1080, y + 60), (54, 140, 190))
        LN([(0, 1330), (1080, 1330)], WHITE, 6); LN([(540, 1180), (540, 1920)], WHITE, 6)
    elif kind == "gully":
        Rr((0, 360, 520, 1330), (250, 180, 150)); Rr((560, 300, 1080, 1330), (170, 210, 200))
        for x0, y0, x1 in ((60, 520, 220), (300, 520, 460), (640, 460, 800), (860, 460, 1020),
                           (80, 880, 300), (780, 880, 1000)):
            Rr((x0, y0, x1, y0 + 180), (110, 80, 70), 6); Rr((x0 + 12, y0 + 12, x1 - 12, y0 + 168), (180, 220, 250), 4)
            LN([((x0 + x1) / 2, y0 + 12), ((x0 + x1) / 2, y0 + 168)], (110, 80, 70), 6)
        Rr((40, 1120, 380, 1330), (120, 120, 130))
        for y in range(1140, 1330, 26): LN([(40, y), (380, y)], (100, 100, 110), 3)
        Rr((700, 1140, 1040, 1330), (230, 120, 60)); Rr((720, 1150, 1020, 1200), (250, 230, 120))
        LN([(0, 260), (1080, 320)], (40, 40, 40), 3); LN([(0, 300), (1080, 290)], (40, 40, 40), 3)
        Rr((0, 1330, 1080, 1920), (140, 136, 140))
        for x in range(0, 1080, 200): Rr((x + 40, 1600, x + 140, 1620), (230, 230, 230))
    elif kind == "living":
        Rr((40, 880, 230, 1040), (120, 80, 60), 10); Rr((54, 894, 216, 1026), (250, 240, 220), 6)
        Rr((0, 1240, 1080, 1920), (150, 100, 70))
        Rr((740, 880, 1060, 1110), (40, 40, 50), 16); Rr((758, 898, 1042, 1092), (90, 170, 100), 6)
        Rr((890, 1110, 910, 1180), (40, 40, 50)); Rr((830, 1170, 970, 1190), (40, 40, 50), 6)
        Rr((40, 1060, 700, 1200), (220, 90, 100), 40); Rr((20, 1160, 720, 1400), (200, 70, 80), 50)
    elif kind == "speed":
        cloud(200, 420, 0.8); cloud(820, 560, 0.6)
        x = 0
        while x < 1080:
            bw = rng.integers(80, 160); top = rng.integers(1000, 1200)
            Rr((x, top, x + bw, 1340), (150, 160, 190))
            x += bw + rng.integers(6, 20)
        Rr((0, 1340, 1080, 1920), (110, 110, 120))
    elif kind == "storm":
        for cx, cy, s in ((200, 380, 1.4), (700, 300, 1.6), (950, 520, 1.1)):
            cloud(cx, cy, s, (90, 96, 112))
        Rr((0, 1320, 1080, 1920), (90, 110, 80))
        for x in (120, 960):
            LN([(x, 1330), (x + 60, 1100)], (70, 50, 40), 18)
            E((x + 10, 1000, x + 190, 1140), (70, 120, 70))
    elif kind == "ocean":
        cloud(240, 420, 0.8); cloud(860, 520, 0.7)
        Rr((0, 1250, 1080, 1920), (40, 120, 190))
    elif kind == "pole":
        cloud(250, 520, 0.7, (250, 252, 255))
        E((-300, 1230, 700, 1460), (240, 248, 255)); E((300, 1210, 1400, 1460), (232, 242, 255))
        Rr((0, 1330, 1080, 1920), (244, 250, 255))
        Rr((880, 1000, 904, 1340), (230, 50, 50))
        for y in range(1000, 1340, 40): Rr((880, y, 904, y + 20), WHITE)
        E((866, 980, 918, 1032), (210, 214, 224))
        for _ in range(26):
            x, y = rng.uniform(0, W), rng.uniform(1380, H)
            E((x - 34, y - 6, x + 34, y + 6), (214, 228, 248))
    elif kind == "pool":
        for y in range(0, 760, 70): LN([(0, y), (1080, y)], (210, 226, 236), 3)
        for x in range(0, 1080, 70): LN([(x, 0), (x, 760)], (210, 226, 236), 3)
        Rr((0, 790, 1080, 820), (250, 250, 250))
        for y in (1340, 1700):
            for x in range(0, 1080, 40):
                E((x, y - 12, x + 32, y + 12), (240, 60, 60) if (x // 40) % 2 else WHITE)
        for _ in range(30):
            x, y = rng.uniform(0, W), rng.uniform(840, H)
            LN([(x, y), (x + 60, y + 6)], (140, 220, 245), 4)
    elif kind == "sea":
        for i in range(6):
            x = 80 + i * 190
            PG([(x, 0), (x + 70, 0), (x + 260, 1500), (x + 120, 1500)], (120, 190, 240))
        img2 = grad(G, W * k, H * k)
        img = Image.blend(img2, img, 0.25); d = ImageDraw.Draw(img)
        for _ in range(110):
            x, y = rng.uniform(0, W), rng.uniform(0, H); r = rng.uniform(1.5, 3.5)
            d.ellipse([(x - r) * k, (y - r) * k, (x + r) * k, (y + r) * k], fill=(150, 200, 240))
        PG([(0, 1700), (300, 1660), (700, 1720), (1080, 1670), (1080, 1920), (0, 1920)], (10, 26, 50))
    elif kind == "cinema":
        Rr((90, 140, 990, 640), (240, 236, 220), 10)
        img_glow = Image.new("RGBA", img.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(img_glow)
        gd.polygon([(90 * k, 640 * k), (990 * k, 640 * k), (1080 * k, 1300 * k), (0, 1300 * k)], fill=(255, 250, 220, 28))
        img = Image.alpha_composite(img, img_glow); d = ImageDraw.Draw(img)
        for row, y in enumerate((1340, 1500, 1660, 1820)):
            for x in range(-40 + (row % 2) * 60, 1120, 120):
                d.rounded_rectangle([x * k, y * k, (x + 100) * k, (y + 150) * k], radius=24 * k, fill=(150, 30, 46))
                d.rounded_rectangle([x * k, (y + 60) * k, (x + 100) * k, (y + 150) * k], radius=20 * k, fill=(120, 22, 36))
    elif kind == "diwali":
        for _ in range(80):
            x, y = rng.uniform(0, W), rng.uniform(0, 900); r = rng.uniform(1.5, 3.5)
            E((x - r, y - r, x + r, y + r), (230, 220, 255))
        x = 0
        while x < 1080:
            bw = int(rng.integers(140, 220)); top = int(rng.integers(900, 1060))
            Rr((x, top, x + bw, 1330), (52, 30, 70))
            for wy in range(top + 40, 1300, 90):
                for wx in range(x + 24, x + bw - 40, 60):
                    Rr((wx, wy, wx + 34, wy + 46), (255, 196, 90))
            x += bw + 8
        Rr((0, 1330, 1080, 1920), (70, 40, 60))
        cx, cy = 540, 1720
        for i, (r, c) in enumerate(((190, (240, 60, 110)), (150, (255, 190, 40)), (110, (60, 180, 220)), (70, (150, 220, 90)), (34, (255, 240, 200)))):
            E((cx - r * 1.6, cy - r * 0.55, cx + r * 1.6, cy + r * 0.55), c)
    elif kind == "sweetshop":
        Rr((0, 300, 1080, 330), (150, 96, 60))
        for x in range(40, 1080, 150):
            Rr((x, 180, x + 90, 300), (220, 240, 250), 14)
            E((x + 14, 230, x + 76, 290), [(255, 170, 60), (240, 240, 250), (240, 120, 150), (180, 220, 120)][(x // 150) % 4])
        Rr((0, 1240, 1080, 1920), (190, 140, 100))
        Rr((0, 1240, 1080, 1270), (230, 200, 160))
        for row, y in enumerate((1330, 1520, 1710)):
            for x in range(30 + (row % 2) * 60, 1080, 170):
                Rr((x, y, x + 140, y + 120), (240, 240, 244), 10)
                for k_ in range(6):
                    sx, sy = x + 24 + (k_ % 3) * 40, y + 30 + (k_ // 3) * 46
                    col = [(255, 170, 50), (236, 236, 240), (250, 120, 150), (190, 120, 70)][(row + x // 170) % 4]
                    if (row + x // 170) % 4 == 1:
                        PG([(sx - 16, sy), (sx, sy - 16), (sx + 16, sy), (sx, sy + 16)], (214, 216, 224))
                    else:
                        E((sx - 16, sy - 16, sx + 16, sy + 16), col)
    elif kind == "smog":
        x = 0
        while x < 1080:
            bw = int(rng.integers(90, 170)); top = int(rng.integers(900, 1150))
            Rr((x, top, x + bw, 1330), (122, 112, 104))
            x += bw + 10
        Rr((0, 1330, 1080, 1920), (96, 88, 80))
        for _ in range(40):
            x, y = rng.uniform(-100, W), rng.uniform(200, 1500); r = rng.uniform(80, 200)
            E((x - r, y - r * 0.4, x + r, y + r * 0.4), (160, 150, 134))
    elif kind == "train":
        Rr((0, 200, 1080, 230), (150, 160, 170))
        for x in range(60, 1080, 140):
            LN([(x, 230), (x, 300)], (150, 160, 170), 6)
            E((x - 26, 300, x + 26, 352), (196, 206, 214))
            E((x - 16, 310, x + 16, 342), (214, 232, 224))
        for x0 in (20, 800):
            Rr((x0, 860, x0 + 260, 1120), (120, 140, 150), 20); Rr((x0 + 14, 874, x0 + 246, 1106), (170, 214, 240), 14)
            for yy in range(880, 1110, 30): LN([(x0 + 14, yy), (x0 + 246, yy)], (140, 160, 170), 3)
        Rr((0, 1240, 1080, 1360), (50, 90, 170), 10)
        Rr((0, 1360, 1080, 1920), (150, 150, 156))
        for x in range(0, 1080, 60): LN([(x, 1360), (x - 40, 1920)], (140, 140, 146), 3)
        for (x, y, c) in ((90, 1180, (90, 70, 60)), (190, 1150, (60, 50, 50)), (900, 1170, (80, 60, 50)), (1000, 1150, (50, 40, 40))):
            E((x - 54, y - 54, x + 54, y + 54), c)
            Rr((x - 80, y + 40, x + 80, y + 260), [(200, 90, 90), (90, 120, 200), (230, 200, 90), (120, 180, 120)][x % 4], 30)
    elif kind == "cretaceous":
        PG([(640, 1300), (860, 860), (920, 860), (1120, 1300)], (120, 80, 70))
        PG([(860, 860), (890, 900), (920, 860)], (240, 110, 50))
        for i in range(5):
            E((870 - 40 * i, 760 - 90 * i, 940 + 50 * i, 830 - 80 * i), (150, 130, 130))
        for x, h in ((80, 360), (200, 300), (980, 340)):
            LN([(x, 1330), (x, 1330 - h)], (110, 80, 50), 14)
            for a in range(0, 360, 45):
                ra = math.radians(a)
                PG([(x, 1330 - h), (x + 120 * math.cos(ra), 1330 - h + 50 * math.sin(ra) + 20), (x + 90 * math.cos(ra + 0.35), 1330 - h + 40 * math.sin(ra + 0.35))], (60, 140, 70))
        Rr((0, 1330, 1080, 1920), (156, 124, 74))
        for _ in range(40):
            x, y = rng.uniform(0, W), rng.uniform(1360, H)
            PG([(x, y), (x + 10, y - 40), (x + 20, y)], (90, 150, 70))
    elif kind == "digsite":
        cloud(230, 470, 0.8); cloud(850, 600, 0.7)
        Rr((0, 1200, 1080, 1920), (232, 202, 142))
        Rr((140, 1380, 940, 1800), (196, 160, 104), 10)
        for x in range(140, 941, 160): LN([(x, 1380), (x, 1800)], (250, 250, 250), 3)
        for y in range(1380, 1801, 140): LN([(140, y), (940, y)], (250, 250, 250), 3)
        for x, y in ((140, 1380), (940, 1380), (140, 1800), (940, 1800)):
            Rr((x - 8, y - 40, x + 8, y + 8), (150, 100, 60))
    elif kind == "office":
        Rr((40, 860, 300, 1060), (90, 110, 140), 10); Rr((54, 874, 286, 1046), (170, 214, 240), 6)
        Rr((0, 1240, 1080, 1920), (150, 130, 110))
        Rr((0, 1200, 1080, 1260), (190, 150, 110))
        Rr((760, 980, 1040, 1180), (40, 44, 56), 14); Rr((776, 996, 1024, 1164), (110, 160, 220), 8)
        Rr((880, 1180, 920, 1210), (40, 44, 56))
        for i in range(5):
            Rr((790, 1010 + i * 28, 1000 - i * 30, 1022 + i * 28), (230, 240, 250))
    elif kind == "hot":
        Rr((0, 1330, 1080, 1920), (196, 140, 80))
        for _ in range(30):
            x, y = rng.uniform(0, W), rng.uniform(1360, H)
            LN([(x, y), (x + rng.uniform(-60, 60), y + 40), (x + rng.uniform(-80, 80), y + 90)], (150, 100, 56), 4)
        for x in (120, 960):
            LN([(x, 1330), (x + 10, 1160)], (110, 80, 50), 12)
            for a in (-0.6, 0.6):
                LN([(x + 10, 1180), (x + 10 + 70 * math.sin(a), 1110)], (110, 80, 50), 8)
    elif kind == "bedroom":
        Rr((620, 300, 1000, 640), (30, 30, 60), 12); Rr((636, 316, 984, 624), (20, 24, 54), 8)
        for _ in range(30):
            x, y = rng.uniform(640, 980), rng.uniform(320, 620); r = rng.uniform(1.5, 3)
            E((x - r, y - r, x + r, y + r), (230, 230, 255))
        Rr((0, 1300, 1080, 1920), (60, 50, 80))
        Rr((60, 1180, 1020, 1420), (90, 120, 200), 50)
        E((180, 1110, 560, 1240), (236, 236, 250))
    return img.reduce(k)

# ================================================================ audio
_rng = np.random.default_rng(5)
tarr = lambda dd: np.arange(int(dd * SR)) / SR
def lp(x, k):
    if k <= 1: return x.copy()
    pad = np.concatenate([np.full(k // 2, x[0]), x, np.full(k - k // 2, x[-1])])
    c = np.concatenate([[0.0], np.cumsum(pad)])
    return (c[k:k + len(x)] - c[:len(x)]) / k
osc = lambda f: 2 * np.pi * np.cumsum(f) / SR
mf = lambda m: 440 * 2 ** ((m - 69) / 12)
def fadeout(s, ms=10):
    L = min(len(s), int(ms / 1000 * SR)); s[-L:] *= np.linspace(1, 0, L); return s
noise = lambda n: _rng.standard_normal(n)

def kick():
    t = tarr(0.35); f = 45 + 110 * np.exp(-t * 22); return np.sin(osc(f)) * np.exp(-t * 9)
def clap():
    t = tarr(0.18); n = noise(len(t)); n = n - lp(n, 8); return n * np.exp(-t * 28) * 0.5
def hat():
    t = tarr(0.05); n = noise(len(t)); n = n - lp(n, 3); return n * np.exp(-t * 90) * 0.25
def pluck(f, dd=0.32):
    t = tarr(dd); ph = 2 * np.pi * f * t
    s = np.sin(ph) + 0.5 * np.sin(2 * ph) * np.exp(-t * 6) + 0.25 * np.sin(3 * ph) * np.exp(-t * 10)
    return fadeout(s * np.minimum(1, t / 0.003) * np.exp(-t * 9))
def bassn(f, dd=0.45):
    t = tarr(dd); ph = 2 * np.pi * f * t; tri = 2 / np.pi * np.arcsin(np.sin(ph))
    return fadeout((0.7 * tri + 0.5 * np.sin(ph)) * np.minimum(1, t / 0.004) * np.exp(-t * 4.5))
def bell(f, dd=0.4):
    t = tarr(dd); s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 8)
    return fadeout(s * np.minimum(1, t / 0.002) * np.exp(-t * 7))

SFX = {}
def sfx(fn): SFX[fn.__name__] = fn; return fn
@sfx
def whoosh(dd=0.45):
    t = tarr(dd); n = noise(len(t)); env = np.sin(np.pi * t / dd) ** 2
    return (lp(n, 14) * 1.3 + 0.25 * (n - lp(n, 4)) * (t / dd)) * env * 0.45
@sfx
def boom():
    t = tarr(1.4); f = 38 + 60 * np.exp(-t * 6)
    return (np.sin(osc(f)) * np.exp(-t * 3) + lp(noise(len(t)), 20) * np.exp(-t * 12) * 0.6) * 0.9
@sfx
def pop():
    t = tarr(0.09); f = 500 + 900 * t / 0.09; return np.sin(osc(f)) * np.sin(np.pi * t / 0.09) * 0.45
@sfx
def tick(f=2200):
    t = tarr(0.05); return np.sin(2 * np.pi * f * t) * np.exp(-t * 150) * 0.45
@sfx
def click():
    t = tarr(0.12)
    return (np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 300) + np.sin(2 * np.pi * 120 * t) * np.exp(-t * 40) * 0.8) * 0.7
@sfx
def powerdown(dd=1.3):
    t = tarr(dd); f = 520 * np.exp(-t * 2.6) + 30; ph = osc(f)
    return (np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph)) * np.minimum(1, t / 0.01) * (1 - t / dd) ** 1.5 * 0.45
@sfx
def scratch():
    dd = 0.45; t = tarr(dd)
    f = np.where(t < 0.18, 300 + 900 * t / 0.18, 1200 - 1000 * (t - 0.18) / 0.27); ph = osc(f)
    s = np.sign(np.sin(ph)) * 0.3 + lp(noise(len(t)), 2) * 0.4
    return lp(s * np.minimum(1, t / 0.01) * np.minimum(1, (dd - t) / 0.05), 3) * 0.5
@sfx
def ding(f=1320):
    t = tarr(1.6)
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t * 3) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6)
         + 0.25 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 9))
    return s * np.minimum(1, t / 0.002) * 0.4
@sfx
def crash():
    t = tarr(0.6); n = noise(len(t)); n = n - lp(n, 2)
    s = n * np.exp(-t * 10) * 0.5 + np.sin(2 * np.pi * 170 * t) * np.exp(-t * 30) * 0.6
    for _ in range(14):
        t0 = _rng.uniform(0, 0.35); f = _rng.uniform(2500, 6000); tt = t - t0; m = tt > 0
        s[m] += np.sin(2 * np.pi * f * tt[m]) * np.exp(-tt[m] * 40) * 0.15
    return s * 0.7
@sfx
def screech(dd=0.9):
    t = tarr(dd); f = 1500 - 600 * t / dd + 60 * np.sin(2 * np.pi * 30 * t); ph = osc(f)
    s = np.sin(ph) * 0.6 + np.sin(2 * ph) * 0.3 + (noise(len(t)) - lp(noise(len(t)), 3)) * 0.25
    return s * np.minimum(1, t / 0.02) * np.minimum(1, (dd - t) / 0.2) * 0.35
@sfx
def rumble(dd=4.0):
    t = tarr(dd); return lp(noise(len(t)), 120) * 6 * np.minimum(1, t / 0.4) * np.minimum(1, (dd - t) / 0.6) * 0.5
@sfx
def wind(dd=6.0):
    t = tarr(dd); n = noise(len(t))
    s = lp(n, 30) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.35 * t) ** 2)
    whistle = np.sin(osc(650 + 120 * np.sin(2 * np.pi * 0.3 * t))) * 0.05
    return (s * 2.2 + whistle) * np.minimum(1, t / 0.6) * np.minimum(1, (dd - t) / 0.4) * 0.35
@sfx
def gale(dd=6.0):
    t = tarr(dd); n = noise(len(t))
    s = lp(n, 8) * 1.2 + lp(n, 40) * 3
    return s * np.minimum(1, t / 0.3) * np.minimum(1, (dd - t) / 0.4) * 0.3
@sfx
def waves(dd=6.0):
    t = tarr(dd); n = lp(noise(len(t)), 25) * 2.5
    env = 0.4 + 0.6 * np.sin(np.pi * ((t * 0.45) % 1)) ** 2
    return n * env * np.minimum(1, t / 0.4) * np.minimum(1, (dd - t) / 0.5) * 0.35
@sfx
def splash():
    t = tarr(0.8); n = noise(len(t)); return (n - lp(n, 3)) * np.exp(-t * 6) * 0.35 + lp(n, 20) * np.exp(-t * 4) * 0.8
@sfx
def underwater(dd=6.0):
    t = tarr(dd); return lp(noise(len(t)), 300) * 3.0 * np.minimum(1, t / 0.5) * np.minimum(1, (dd - t) / 0.5)
@sfx
def bubbles(dd=6.0):
    s = np.zeros(int(dd * SR))
    for _ in range(int(dd * 3)):
        t0 = _rng.uniform(0, dd - 0.1); t = tarr(0.07); f = _rng.uniform(300, 600) * (1 + 2 * t / 0.07)
        sig = np.sin(osc(f)) * np.sin(np.pi * t / 0.07) * 0.25; i = int(t0 * SR); s[i:i + len(sig)] += sig
    return s
@sfx
def gasp():
    t = tarr(0.7); n = noise(len(t)); s = (lp(n, 4) - lp(n, 30)) * 2
    env = np.minimum(1, t / 0.05) * np.exp(-t * 3)
    return s * env * 0.5
@sfx
def heartbeat(dd=6.0, bpm=40):
    s = np.zeros(int(dd * SR)); per = 60 / bpm; t = tarr(0.18)
    thump = np.sin(osc(60 + 40 * np.exp(-t * 30))) * np.exp(-t * 18)
    k = 0.0
    while k < dd - 0.5:
        for off, g in ((0, 1.0), (0.22, 0.7)):
            i = int((k + off) * SR); s[i:i + len(thump)] += thump[:len(s) - i] * g
        k += per
    return s * 0.8
@sfx
def crowd(dd=6.0):
    t = tarr(dd); n = noise(len(t))
    s = (lp(n, 6) - lp(n, 60)) * 1.6 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.5 * t))
    return s * np.minimum(1, t / 0.5) * np.minimum(1, (dd - t) / 0.5) * 0.5
@sfx
def cheer():
    t = tarr(1.8); n = noise(len(t)); s = (lp(n, 5) - lp(n, 50)) * 2.2
    return s * np.minimum(1, t / 0.15) * np.exp(-t * 1.2) * 0.6
@sfx
def whistle():
    t = tarr(0.8); f = 2600 + 120 * np.sign(np.sin(2 * np.pi * 26 * t)); s = np.sin(osc(f))
    return s * np.minimum(1, t / 0.02) * np.minimum(1, (0.8 - t) / 0.05) * 0.22
@sfx
def seagulls():
    s = np.zeros(int(2.0 * SR))
    for k in range(3):
        t = tarr(0.35); f = 1400 - 600 * t / 0.35; sig = np.sin(osc(f)) * np.sin(np.pi * t / 0.35) * 0.18
        i = int(k * 0.5 * SR); s[i:i + len(sig)] += sig
    return s
@sfx
def kwak():
    s = np.zeros(int(0.6 * SR))
    for i in range(6):
        b = blip(640 * 2 ** ((i % 3) / 12), 1.1); j = int(i * 0.07 * SR); s[j:j + len(b)] += b
    return s

def blip(f, g=1.0):
    t = tarr(0.055); ff = f * (1 + 0.25 * np.exp(-t * 80)); ph = osc(ff)
    s = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.3 * np.sin(3 * ph) + 0.15 * np.sin(4 * ph)
    return fadeout(s * np.minimum(1, t / 0.004) * np.exp(-t * 30) * 0.26 * g)

MAJ = ([48, 43, 45, 41], [(60, 64, 67), (59, 62, 67), (57, 60, 64), (57, 60, 65)])
MIN = ([45, 41, 48, 43], [(57, 60, 64), (57, 60, 65), (55, 60, 64), (55, 59, 62)])
MEL = [[(0, 76), (1, 79), (1.5, 76), (2.5, 72), (3, 74)], [(0, 74), (1, 71), (1.5, 74), (2.5, 79), (3, 77)],
       [(0, 76), (1, 72), (1.5, 76), (2.5, 81), (3, 79)], [(0, 77), (1, 76), (1.5, 74), (2.5, 72), (3, 71)]]

def build_audio(cfg, path):
    TOTAL = cfg["total"]; scenes = cfg["scenes"]
    N = int(SR * (TOTAL + 1))
    music = np.zeros(N); fx = np.zeros(N)
    def add(buf, sig, t, g=1.0):
        i = int(round(t * SR))
        if i >= N: return
        if i < 0: sig = sig[-i:]; i = 0
        j = min(N, i + len(sig)); buf[i:j] += sig[:j - i] * g
    beat = 60 / cfg.get("bpm", 112)
    for m in cfg["music"]:
        prog = MIN if m.get("minor") else MAJ
        roots, chords = prog; b = 0; g = m.get("g", 1.0)
        while True:
            t = m["t0"] + b * beat
            if t >= m["t1"] - 0.05: break
            bar = (b // 4) % 4; pos = b % 4
            if m.get("drums", True):
                clap_on = m.get("clap", True)
                if pos in (0, 2) and (clap_on or pos == 0): add(music, kick(), t, 0.85 * g)
                if clap_on and pos in (1, 3): add(music, clap(), t, 0.45 * g)
                add(music, hat(), t + beat / 2, 0.6 * g); add(music, hat(), t, 0.3 * g)
            add(music, bassn(mf(roots[bar])), t, 0.5 * g)
            for c in chords[bar]: add(music, pluck(mf(c)), t + beat / 2, 0.13 * g)
            if m.get("melody") and pos == 0:
                for off, n_ in MEL[bar]:
                    if t + off * beat < m["t1"] - 0.05: add(music, bell(mf(n_)), t + off * beat, 0.16 * g)
            b += 1
    for dr in cfg.get("drones", []):
        t = tarr(dr["dur"]); env = np.minimum(1, t / 1.0) * np.minimum(1, (dr["dur"] - t) / 0.6)
        s = sum(np.sin(2 * np.pi * f * t) * a for f, a in dr.get("freqs", ((55, 1), (82.4, 0.6), (110, 0.3))))
        add(music, s * env * dr.get("g", 0.1), dr["t0"])

    def babble(text, t0, base, g=1.0, cps=CPS):
        for i, ch in enumerate(text):
            if ch.isalnum():
                f = base * 2 ** ((((ord(ch.lower()) * 5) % 9) - 4) / 14)
                add(fx, blip(f, 1.3 if ch.isupper() else 1.0), t0 + i * cps, g)

    # automatic sounds
    add(fx, boom(), 0.2)
    for item in cfg["intro"]["lines"]:
        add(fx, pop(), item[2])
    for sc in scenes:
        if sc["id"] == "intro": continue
        add(fx, whoosh(), sc["s"] - 0.2)
        if sc.get("clock"): add(fx, tick(), sc["s"] + 0.25)
        if sc.get("twist"): add(fx, scratch(), sc["s"] - 0.15)
        if "say" in sc:
            babble(sc["say"], sc["say_at"], sc.get("pitch", 400))
            if sc.get("twist"): add(fx, ding(), sc["say_end"] + 0.3)
        if sc.get("char") and sc["id"] != "outro":
            add(fx, pop(), sc.get("enter", sc["s"] + 0.15) + 0.05, 0.7)
    out = scenes[-1]
    add(fx, boom(), out["s"] + 0.05, 0.6)
    for i in range(len(cfg["outro"]["row"])): add(fx, pop(), out["s"] + 0.9 + i * 0.18)
    add(fx, pop(), out["s"] + 2.2, 1.2); add(fx, ding(1760), out["s"] + 3.8, 0.6)
    for ev in cfg.get("fx", []):
        name, t, g = ev[:3]; kw = ev[3] if len(ev) > 3 else {}
        add(fx, SFX[name](**kw), t, g)

    gain = np.full(N, 0.6)
    for sc in scenes:
        if "say" in sc:
            gain[int((sc["say_at"] - 0.2) * SR):int((sc["say_end"] + 0.2) * SR)] = 0.33
    gain = lp(gain, int(0.15 * SR))
    tot = np.arange(N) / SR
    gain *= np.clip((TOTAL - tot) / 0.8, 0, 1)
    mix = music * gain + fx * np.clip((TOTAL + 0.05 - tot) / 0.3, 0, 1)
    mix = np.tanh(mix * 1.2); mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.9
    pcm = (mix[:int(TOTAL * SR)] * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(np.stack([pcm, pcm], 1).reshape(-1).tobytes())

# ================================================================ rendering
T_COMMENT = R.T_COMMENT
T_FOLLOW = text_sprite([("Follow ", WHITE), ("@whatif.wala", YEL)], 58, stroke=7)
_clk, _bub = {}, {}
def clock_spr(label):
    if label not in _clk: _clk[label] = make_clock(label)
    return _clk[label]
def bubble_for(text):
    if text not in _bub: _bub[text] = make_bubble(text)
    return _bub[text]

def blink_at(T, seed): return ((T * 0.37 + seed) % 1.0) < 0.045
def talk_amt(sc, T):
    if "say" in sc and sc["say_at"] <= T < sc["say_end"]:
        return clamp(0.5 + 0.55 * math.sin(T * 27))
    return 0.0
def val(v, *a):
    return v(*a) if callable(v) else v

def draw_narr(frame, sc, T):
    if "narr" not in sc or T < sc["n_at"]: return
    d = ImageDraw.Draw(frame); f = font(66)
    lines = wrap_words(sc["narr"].split(), f, 880)
    n = int((T - sc["n_at"]) / 0.2) + 1
    lh = 86; y0 = sc.get("narr_y", 1470) - len(lines) * lh / 2; idx = 0; GAP = 12
    for li, line in enumerate(lines):
        x = 540 - (f.getlength(" ".join(line)) + GAP * (len(line) - 1)) / 2; y = y0 + li * lh
        for w in line:
            if idx < n:
                age = T - (sc["n_at"] + idx * 0.2)
                dy = -14 * (1 - ease_out(age / 0.15))
                emph = is_emph(w) or (w[:1] in "-+" and len(w) > 1) or any(ch.isdigit() for ch in w)
                d.text((x, y + dy), w, font=f, fill=YEL if emph else WHITE, stroke_width=8, stroke_fill=(0, 0, 0))
            x += f.getlength(w + " ") + GAP; idx += 1

def draw_bubble(frame, sc, T, anchor_y=800):
    if "say" not in sc: return
    t0 = sc["say_at"] - 0.25
    if T < t0: return
    B = bubble_for(sc["say"]); b = B["img"].copy(); bd = ImageDraw.Draw(b); f = font(58)
    nvis = int((T - sc["say_at"]) / CPS) + 1 if T >= sc["say_at"] else 0
    count = 0
    for li, line in enumerate(B["lines"]):
        x = (B["bw"] - f.getlength(" ".join(line))) / 2; y = B["pad"] - 6 + li * B["lh"]
        for w in line:
            vis = w[:max(0, nvis - count)]
            if vis: bd.text((x, y), vis, font=f, fill=RED if is_emph(w) else (36, 26, 46))
            x += f.getlength(w + " "); count += len(w) + 1
    s = 0.35 + 0.65 * ease_back((T - t0) / 0.3)
    bb = b.resize((max(1, int(b.width * s)), max(1, int(b.height * s))), Image.BILINEAR) if abs(s - 1) > 0.01 else b
    comp(frame, bb, 540 - B["bw"] * s / 2, sc.get("bubble_y", anchor_y) + 60 - bb.height)

def draw_clock(frame, sc, T):
    lab = sc.get("clock")
    if not lab: return
    lt = T - sc["s"] - 0.25
    if lt < 0: return
    c = clock_spr(val(lab, T))
    y = 228 - 60 * (1 - ease_back(lt / 0.35))
    comp(frame, c, 540 - c.width / 2, y)

def scene_at(cfg, T):
    for sc in cfg["scenes"]:
        if sc["s"] <= T < sc["e"]: return sc
    return cfg["scenes"][-1]

def anim_in(kind, p):
    if kind == "left": return (-600 * (1 - ease_out(p)), 1.0)
    if kind == "right": return (600 * (1 - ease_out(p)), 1.0)
    return (0, 0.2 + 0.8 * ease_back(p))

def render(cfg, T):
    sc = scene_at(cfg, T); lt = T - sc["s"]; sid = sc["id"]
    frame = (sc["bg_fn"](T) if sc.get("bg_fn") else bg(sc.get("bg", "intro"))).copy()
    d = ImageDraw.Draw(frame)
    if sid == "intro":
        for spr, y, t0, an in cfg["intro"]["lines"]:
            if T >= t0:
                dx, s = anim_in(an, (T - t0) / (0.35 if an == "pop" else 0.3))
                paste_c(frame, spr, 540 + dx, y, s)
        if cfg["intro"].get("extra"): cfg["intro"]["extra"](frame, d, T)
    elif sid == "outro":
        o = cfg["outro"]
        for spr, y, t0 in o["lines"]:
            if lt >= t0:
                paste_c(frame, spr, 540, y, (0.3 + 0.7 * ease_back((lt - t0) / 0.3)) * (1 + 0.025 * math.sin(T * 6)))
        for i, (kd, st) in enumerate(o["row"]):
            s0 = 0.9 + i * 0.18
            if lt < s0: continue
            p = ease_back((lt - s0) / 0.35)
            n = len(o["row"]); x = 540 + (i - (n - 1) / 2) * 205
            y = 940 + 300 * (1 - p) + 10 * math.sin(T * 4 + i)
            talk = clamp(0.5 + 0.6 * math.sin(T * 22 + i * 2)) if 1.8 <= lt < 3.4 else 0
            comp(frame, draw_char(kd, 200, T, talk, blink_at(T, i * 0.2), (0, 0.2), st), x - 100, y - 100)
        if lt >= 2.2:
            paste_c(frame, T_COMMENT, 540, 1235, (0.3 + 0.7 * ease_back((lt - 2.2) / 0.3)) * (1 + 0.04 * math.sin(T * 7)))
            ay = 1360 + 18 * abs(math.sin(T * 5))
            d.polygon([(500, ay), (580, ay), (540, ay + 60)], fill=WHITE, outline=OUTL, width=5)
        if lt >= 2.6:
            paste_c(frame, T_FOLLOW, 540, 1530, 0.3 + 0.7 * ease_back((lt - 2.6) / 0.3))
        if o.get("note") and lt >= 2.9:
            paste_c(frame, o["note"], 540, 1620, 0.3 + 0.7 * ease_back((lt - 2.9) / 0.3))
    else:
        if sc.get("props"): sc["props"](frame, d, T, sc)
        if sc.get("char") and T >= sc.get("enter", sc["s"] + 0.15):
            le = T - sc.get("enter", sc["s"] + 0.15)
            talk = talk_amt(sc, T)
            cx, cy, B = val(sc.get("pos", (540, 1080, 600)), T)
            p = ease_back(le / 0.55)
            bob = 8 * math.sin(T * 3.2) + (6 * math.sin(T * 20) if talk > 0 else 0)
            y = cy + 640 * (1 - p) + bob
            spr = draw_char(sc["char"], B, T, talk, blink_at(T, 0.5), sc.get("look", (0, 0.15)),
                            val(sc.get("state", 1), T))
            rot = val(sc.get("rot", 0), T)
            if rot: spr = spr.rotate(rot, resample=Image.BICUBIC, expand=False)
            comp(frame, spr, cx - B / 2, y - B / 2)
        if sc.get("props_after"): sc["props_after"](frame, ImageDraw.Draw(frame), T, sc)
        draw_bubble(frame, sc, T)
        if sc.get("overlay"): frame = sc["overlay"](frame, T, sc)
    draw_clock(frame, sc, T)
    draw_narr(frame, sc, T)
    if sid != "intro" and lt < 0.2:
        s = 1.0 + 0.07 * (1 - ease_out(lt / 0.2))
        big = frame.resize((int(W * s), int(H * s)), Image.BILINEAR)
        ox, oy = (big.width - W) // 2, (big.height - H) // 2
        frame = big.crop((ox, oy, ox + W, oy + H))
        if lt < 0.12:
            frame = Image.blend(frame, Image.new("RGBA", (W, H), (255, 255, 255, 255)), 0.55 * (1 - lt / 0.12))
    if T < 0.2:
        frame = Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 255)), frame, T / 0.2)
    return frame.convert("RGB")

def finalize(cfg):
    for sc in cfg["scenes"]:
        if "say" in sc: sc["say_end"] = sc["say_at"] + len(sc["say"]) * CPS
    return cfg

def preview(cfg, times, out):
    frames = [render(cfg, t) for t in times]
    tw_, th_ = 270, 480; cols = 4; rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw_, rows * th_))
    for i, fr in enumerate(frames):
        sheet.paste(fr.resize((tw_, th_)), ((i % cols) * tw_, (i // cols) * th_))
    sheet.save(out)

def render_video(cfg, out):
    audio = out.replace(".mp4", ".wav")
    build_audio(cfg, audio)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", audio, "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nf = int(cfg["total"] * FPS)
    for i in range(nf):
        p.stdin.write(render(cfg, i / FPS).tobytes())
    p.stdin.close(); p.wait()
    os.remove(audio)

def main(cfg, name):
    finalize(cfg)
    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        preview(cfg, [float(x) for x in sys.argv[2].split(",")], os.path.join(HERE, f"{name}_preview.png"))
        print("ok")
    else:
        render_video(cfg, os.path.join(HERE, f"{name}.mp4")); print("done")
