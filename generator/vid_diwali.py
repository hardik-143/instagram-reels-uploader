#!/usr/bin/env python3
"""What if Diwali lasted 365 days?"""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import YEL, WHITE, OUTL, W, H, title, draw_char, comp, paste_c, ease_back, ease_out, clamp

@E.sfx
def firework():
    t = E.tarr(1.6); s = np.zeros(len(t))
    up = t < 0.55
    s[up] = np.sin(E.osc(np.where(up, 900 + 1400 * t / 0.55, 0))[up]) * 0.12
    tb = t - 0.55; m = tb > 0
    n = E.noise(len(t))
    s[m] += (E.lp(n, 6)[m] * 3) * np.exp(-tb[m] * 6) * 0.7
    for _ in range(25):
        t0 = 0.6 + E._rng.uniform(0, 0.9); i = int(t0 * E.SR)
        if i + 300 < len(s): s[i:i + 300] += E.noise(300) * np.exp(-np.arange(300) / 60) * 0.35
    return s * 0.8

@E.sfx
def cough():
    s = np.zeros(int(1.0 * E.SR))
    for k, t0 in enumerate((0.0, 0.32, 0.6)):
        t = E.tarr(0.22); n = E.noise(len(t))
        sig = (E.lp(n, 3) - E.lp(n, 40)) * 2.5 * np.minimum(1, t / 0.01) * np.exp(-t * 14)
        i = int(t0 * E.SR); s[i:i + len(sig)] += sig * (1 - 0.2 * k)
    return s * 0.5

@E.sfx
def kaching():
    return E.ding(2093) * 0.7 + np.concatenate([np.zeros(int(0.08 * E.SR)), E.ding(2637)[:-int(0.08 * E.SR)]]) * 0.6

@E.sfx
def whimper():
    t = E.tarr(0.9); f = 900 - 350 * t / 0.9 + 30 * np.sin(2 * np.pi * 7 * t)
    return np.sin(E.osc(f)) * np.sin(np.pi * t / 0.9) * 0.25

BURSTS = [(0.6, 1.5), (1.9, 2.7)]
def fireworks(d, T, bursts, seed=0):
    cols = [(255, 214, 10), (255, 90, 140), (90, 200, 255), (140, 255, 140), (255, 160, 60)]
    for i, (t0, cx, cy) in enumerate(bursts):
        age = T - t0
        if 0 <= age < 1.3:
            p = ease_out(age / 1.0); col = cols[(i + seed) % 5]
            r_ = 30 + 170 * p
            for k in range(16):
                a = k * math.pi / 8
                x, y = cx + r_ * math.cos(a), cy + r_ * math.sin(a) + 60 * age * age
                rr = max(1, 9 * (1 - age / 1.3))
                d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col)
        elif -0.55 <= age < 0:
            q = (age + 0.55) / 0.55
            y = 1300 - (1300 - cy) * q
            d.ellipse([cx - 5, y - 5, cx + 5, y + 5], fill=(255, 236, 180))

def lights(d, T, y=360):
    for i in range(18):
        x = 30 + i * 60
        yy = y + 30 * math.sin(math.pi * (i % 9) / 8)
        on = (int(T * 3) + i) % 3 != 0
        c = [(255, 214, 10), (255, 90, 140), (90, 200, 255)][i % 3] if on else (90, 80, 100)
        d.ellipse([x - 10, yy - 10, x + 10, yy + 10], fill=c)

def intro_extra(frame, d, T):
    fireworks(d, T, [(0.5, 200, 320), (1.1, 880, 260), (2.3, 260, 1700), (2.9, 820, 1640)])
    if T >= 1.9:
        paste_c(frame, draw_char("diya", 360, T, 0, False, (0, 0), 1), 540, 1380, ease_back((T - 1.9) / 0.4))

S1_BURSTS = [(4.4, 180, 300), (5.0, 900, 360), (6.2, 300, 1000), (7.4, 820, 980), (8.6, 160, 1050), (9.8, 900, 320)]
def day1_props(frame, d, T, sc):
    lights(d, T, 160)
    fireworks(d, T, S1_BURSTS)

def smog_props(frame, d, T, sc):
    for i in range(14):
        x = (i * 157 + T * 40 * (1 + i % 3)) % 1300 - 110
        y = 300 + (i * 211) % 1100
        r = 70 + (i % 4) * 30
        d.ellipse([x - r, y - r * 0.4, x + r, y + r * 0.4], fill=(170, 160, 142))

def uncle_state(T):
    return "angry" if T >= 26.6 else 1

def bill_after(frame, d, T, sc):
    if T < 26.0: return
    p = ease_back((T - 26.0) / 0.4)
    w, h = int(250 * p), int(300 * p)
    if w < 10: return
    x0, y0 = 760, 1000
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=WHITE, outline=OUTL, width=5)
    if p > 0.9:
        f = E.font(30); f2 = E.font(38)
        d.text((x0 + 20, y0 + 20), "ELECTRICITY", font=f, fill=(40, 40, 50))
        d.text((x0 + 20, y0 + 56), "BILL", font=f, fill=(40, 40, 50))
        for k in range(4): d.line([(x0 + 20, y0 + 110 + k * 28), (x0 + w - 20, y0 + 110 + k * 28)], fill=(200, 200, 210), width=4)
        d.text((x0 + 20, y0 + 226), "TOTAL: ???", font=f2, fill=(225, 45, 75))

def night_props(frame, d, T, sc):
    lights(d, T, 160)

S = [
    dict(id="intro", s=0.0, e=4.0),
    dict(id="day1", s=4.0, e=11.0, bg="diwali", clock="DAY 1", char="diya", pos=(540, 1080, 560),
         props=day1_props, narr="Day 1: lights, sweets, new clothes. PERFECT.", n_at=4.2,
         say="Best. Day. EVER!", say_at=5.8, pitch=560),
    dict(id="day30", s=11.0, e=18.0, bg="sweetshop", clock="DAY 30", char="ladoo", pos=(540, 1060, 560),
         narr="Day 30: even your mithai is begging for a break.", n_at=11.2,
         say="Please... eat a SALAD today.", say_at=12.9, pitch=500),
    dict(id="day90", s=18.0, e=25.0, bg="smog", clock="DAY 90", char="cloud", pos=(540, 1060, 560),
         props=smog_props, narr="Day 90: crackers every night. The air turns TOXIC.", n_at=18.2,
         say="Cough... I can't see my OWN face.", say_at=19.9, pitch=480),
    dict(id="day180", s=25.0, e=32.0, bg="living", clock="DAY 180", char="uncle", pos=(380, 1080, 560),
         state=uncle_state, look=(0.9, 0.2), props_after=bill_after,
         narr="Day 180: lights on 24/7. Now open the electricity bill.", n_at=25.2,
         say="This bill is BIGGER than my salary!", say_at=27.0, pitch=230),
    dict(id="day365", s=32.0, e=39.0, bg="diwali", clock="DAY 365", char="dog", pos=(540, 1080, 600),
         props=night_props, twist=True, look=(0, 0.3),
         narr="But someone would suffer the most... your PET.", n_at=32.2,
         say="365 days of crackers? I'm moving OUT.", say_at=34.2, pitch=320),
    dict(id="outro", s=39.0, e=44.0),
]

cfg = dict(
    total=44.0, scenes=S,
    intro=dict(lines=[
        (title([("WHAT IF", YEL)], 220), 560, 0.2, "pop"),
        (title([("DIWALI LASTED", WHITE)], 116), 770, 0.75, "right"),
        (title([("365 DAYS?", YEL)], 150), 915, 1.05, "left"),
        (title([("...yes, ", WHITE), ("EVERY", YEL), (" day", WHITE)], 86), 1060, 1.5, "pop"),
    ], extra=intro_extra),
    outro=dict(lines=[(title([("Would ", WHITE), ("YOU", YEL), (" survive", WHITE)], 96), 470, 0.15),
                      (title([("365 days of Diwali?", YEL)], 96), 600, 0.45)],
               row=[("diya", 1), ("ladoo", 1), ("cloud", 1), ("uncle", 1), ("dog", 1)]),
    music=[dict(t0=0.2, t1=4.0, drums=False), dict(t0=4.0, t1=31.85), dict(t0=39.0, t1=44.0, melody=True)],
    fx=[("firework", 0.0, 0.6), ("firework", 0.6, 0.5), ("firework", 1.8, 0.4), ("firework", 2.4, 0.4)]
       + [("firework", t - 0.6, 0.55) for t, _, _ in S1_BURSTS]
       + [("cough", 19.3, 1.0), ("cough", 22.4, 0.7), ("kaching", 26.1, 1.0),
          ("firework", 32.6, 0.25), ("whimper", 33.4, 1.0), ("whimper", 36.6, 0.8)],
)

if __name__ == "__main__":
    E.main(cfg, "what_if_diwali_lasted_365_days")
