"""The magical items' backgrounds (2026-10-22, the user: "The background created for magical items is too simple, can you
improve them?"; first asked 2026-10-21: "backgrounds with colored effects to represent the magical items (for instance a
pale blue glow for the forstblade)").

One painted effect per element, 128 px, its colours baked in, transparent round its edge (the HUD turns some of them:
nothing reaches past the inscribed circle): flame tongues rising from below, a frost crystal, forked lightning, venom
bubbles in a haze, holy rays and a halo, an arcane rune circle, and drifting sparkles for magic with no element.
Written to MedievalSetting Assets/Game/Resources/UI/ItemGlow/<kind>.png (ItemGlyph.Glow loads and animates them).
Run: py glow_textures.py [preview icons dir]

Not in the game: tried 2026-10-22 and taken out the same day (the user: "these are too much. I was thinking more like a
faint colored outline" -- ItemIconsMenu.Outline and ItemGlyph.Glow do that now). Kept for the record.
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image

S = 128
OUT = r"E:\Unity\Projects\MedievalSetting\Assets\Game\Resources\UI\ItemGlow"
y, x = np.mgrid[0:S, 0:S].astype(np.float32)
U = (x + 0.5) / S * 2 - 1                    # -1 .. 1, left to right
V = 1 - (y + 0.5) / S * 2                    # -1 .. 1, bottom to top
R = np.sqrt(U * U + V * V)
A = np.arctan2(V, U)


def smooth(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def noise(freq, seed, sx=1.0, sy=1.0):
    """value noise at a frequency (cells across the square), bilinear"""
    rnd = np.random.default_rng(seed)
    n = int(freq) + 2
    g = rnd.random((n + 1, n + 1)).astype(np.float32)
    gx = (U * sx * 0.5 + 0.5) * freq
    gy = (V * sy * 0.5 + 0.5) * freq
    gx = np.mod(gx, n - 1)
    gy = np.mod(gy, n - 1)
    x0 = np.floor(gx).astype(int)
    y0 = np.floor(gy).astype(int)
    fx = smooth(gx - x0)
    fy = smooth(gy - y0)
    a = g[y0, x0] * (1 - fx) + g[y0, x0 + 1] * fx
    b = g[y0 + 1, x0] * (1 - fx) + g[y0 + 1, x0 + 1] * fx
    return a * (1 - fy) + b * fy


def fbm(freq, seed, octaves=4, sx=1.0, sy=1.0):
    total, amp, norm = 0, 1.0, 0
    for o in range(octaves):
        total = total + noise(freq * 2 ** o, seed + o * 17, sx, sy) * amp
        norm += amp
        amp *= 0.5
    return total / norm


def ramp(t, stops):
    """colour along t (0..1) through (position, (r, g, b)) stops"""
    t = np.clip(t, 0, 1)
    out = np.zeros(t.shape + (3,), np.float32)
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        m = (t >= p0) & (t <= p1)
        k = ((t - p0) / max(p1 - p0, 1e-6))[..., None]
        out = np.where(m[..., None], np.array(c0) * (1 - k) + np.array(c1) * k, out)
    return out


def seg_dist(ax, ay, bx, by):
    """distance of every pixel to the segment a-b"""
    dx, dy = bx - ax, by - ay
    t = np.clip(((U - ax) * dx + (V - ay) * dy) / max(dx * dx + dy * dy, 1e-9), 0, 1)
    return np.hypot(U - (ax + t * dx), V - (ay + t * dy))


def line(pts, width):
    """a polyline's soft stroke, 0..1"""
    d = np.full(U.shape, 9.0, np.float32)
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        d = np.minimum(d, seg_dist(ax, ay, bx, by))
    return np.exp(-(d / width) ** 2)


def sparkles(n, seed, rmax=0.85, size=(0.04, 0.09)):
    """four-pointed glints scattered inside rmax"""
    rnd = random.Random(seed)
    out = np.zeros(U.shape, np.float32)
    for _ in range(n):
        r, a = rmax * math.sqrt(rnd.random()), rnd.random() * 2 * math.pi
        cx, cy, s = r * math.cos(a), r * math.sin(a), rnd.uniform(*size)
        dx, dy = np.abs(U - cx), np.abs(V - cy)
        star = np.exp(-(dx / (s * 0.12)) ** 2) * np.exp(-(dy / s) ** 2) + np.exp(-(dy / (s * 0.12)) ** 2) * np.exp(-(dx / s) ** 2)
        core = np.exp(-((dx * dx + dy * dy) / (s * 0.25) ** 2))
        out = np.maximum(out, np.clip(star * 0.8 + core, 0, 1) * rnd.uniform(0.5, 1.0))
    return out


def glow(core=0.0, edge=1.0, power=1.6):
    """a soft round light, 1 in the middle (to core), 0 at edge"""
    return smooth(1 - (R - core) / (edge - core)) ** power


def save(name, rgb, alpha):
    alpha = np.clip(alpha, 0, 1) * smooth((1.0 - R) / 0.12)          # nothing past the inscribed circle (it turns)
    img = np.dstack([np.clip(rgb, 0, 1), alpha])
    Image.fromarray((img * 255).astype(np.uint8), "RGBA").save(os.path.join(OUT, name + ".png"))
    return name


def flame():
    n = fbm(3.0, 11, 4, sx=1.6, sy=0.7)                              # stretched up: tongues
    h = (V + 1) / 2                                                  # 0 bottom .. 1 top
    body = (1 - h * 1.25) + (n - 0.5) * 1.1
    body = body * smooth(1 - np.abs(U) * 1.1)                        # narrower to the sides
    f = np.clip(body, 0, 1)
    base = glow(0.0, 1.0, 1.8) * 0.45
    t = np.maximum(f, base * 0.6)
    rgb = ramp(t, [(0, (0.45, 0.05, 0.02)), (0.35, (0.85, 0.2, 0.04)), (0.6, (1.0, 0.5, 0.1)), (0.82, (1.0, 0.82, 0.3)), (1, (1.0, 0.97, 0.75))])
    return save("flame", rgb, np.maximum(smooth(f * 1.6), base))


def frost():
    base = glow(0.0, 1.0, 1.5)
    arms = np.zeros(U.shape, np.float32)
    for k in range(6):                                               # a crystal: six arms, each with two pairs of branches
        a = k * math.pi / 3 + math.pi / 6
        ca, sa = math.cos(a), math.sin(a)
        arms = np.maximum(arms, line([(0, 0), (0.82 * ca, 0.82 * sa)], 0.013))
        for t, ln in ((0.38, 0.2), (0.6, 0.14)):
            px, py = t * ca, t * sa
            for sgn in (-1, 1):
                b = a + sgn * math.pi / 3
                arms = np.maximum(arms, line([(px, py), (px + ln * math.cos(b), py + ln * math.sin(b))], 0.01))
    rime = fbm(6, 21, 3) * base
    sp = sparkles(14, 5, 0.9, (0.03, 0.07))
    t = np.clip(base * 0.55 + arms * 0.75 + sp, 0, 1)
    rgb = ramp(t, [(0, (0.2, 0.45, 0.75)), (0.45, (0.5, 0.8, 1.0)), (0.75, (0.82, 0.95, 1.0)), (1, (1, 1, 1))])
    return save("frost", rgb, np.clip(base * 0.65 + rime * 0.2 + arms * 0.5 + sp * 0.8, 0, 1))


def storm():
    base = glow(0.0, 1.0, 1.7)
    rnd = random.Random(3)
    bolt, halo = np.zeros(U.shape, np.float32), np.zeros(U.shape, np.float32)
    for k in range(4):                                               # forked bolts out from the middle
        a = k * 2 * math.pi / 4 + rnd.uniform(-0.4, 0.4)
        pts, r_ = [(0.0, 0.0)], 0.0
        while r_ < 0.88:
            r_ += rnd.uniform(0.1, 0.18)
            aa = a + rnd.uniform(-0.45, 0.45)
            pts.append((min(r_, 0.9) * math.cos(aa), min(r_, 0.9) * math.sin(aa)))
        bolt = np.maximum(bolt, line(pts, 0.01))
        halo = np.maximum(halo, line(pts, 0.06))
        j = rnd.randrange(1, len(pts) - 1)                           # a fork off it
        fx, fy = pts[j]
        fa = a + rnd.choice((-1, 1)) * 0.8
        bolt = np.maximum(bolt, line([(fx, fy), (fx + 0.22 * math.cos(fa), fy + 0.22 * math.sin(fa))], 0.011))
    t = np.clip(base * 0.5 + halo * 0.4 + bolt, 0, 1)
    rgb = ramp(t, [(0, (0.25, 0.15, 0.55)), (0.45, (0.58, 0.45, 1.0)), (0.75, (0.82, 0.75, 1.0)), (1, (1, 1, 1))])
    return save("storm", rgb, np.clip(base * 0.6 + halo * 0.4 + bolt * 0.75, 0, 1))


def venom():
    base = glow(0.0, 1.0, 1.4)
    haze = fbm(4, 31, 4)
    rnd = random.Random(8)
    rings, hi = np.zeros(U.shape, np.float32), np.zeros(U.shape, np.float32)
    for _ in range(11):                                              # bubbles: a rim and a glint each
        r, a = 0.8 * math.sqrt(rnd.random()), rnd.random() * 2 * math.pi
        cx, cy, s = r * math.cos(a), r * math.sin(a), rnd.uniform(0.04, 0.11)
        d = np.hypot(U - cx, V - cy)
        rings = np.maximum(rings, np.exp(-((d - s) / 0.012) ** 2) + smooth(1 - d / s) * 0.25)
        hi = np.maximum(hi, np.exp(-(np.hypot(U - cx + s * 0.35, V - cy - s * 0.35) / (s * 0.22)) ** 2))
    t = np.clip(base * (0.35 + haze * 0.5) + rings * 0.6 + hi, 0, 1)
    rgb = ramp(t, [(0, (0.1, 0.3, 0.05)), (0.4, (0.3, 0.7, 0.12)), (0.7, (0.55, 0.95, 0.3)), (1, (0.9, 1.0, 0.75))])
    return save("venom", rgb, np.clip(base * (0.45 + haze * 0.5) + rings * 0.6 + hi * 0.8, 0, 1))


def holy():
    base = glow(0.0, 1.0, 1.5)
    n = fbm(2, 41, 2)
    rays = (0.5 + 0.5 * np.cos(A * 12 + n * 2.0)) ** 5 * smooth(1 - R / 0.95) * smooth(R / 0.15)
    rays2 = (0.5 + 0.5 * np.cos(A * 12 + math.pi / 12 * 12 + n)) ** 8 * smooth(1 - R / 0.75) * 0.6
    halo = np.exp(-((R - 0.56) / 0.045) ** 2) * 0.6
    t = np.clip(base * 0.6 + rays * 0.6 + rays2 * 0.4 + halo * 0.7, 0, 1)
    rgb = ramp(t, [(0, (0.6, 0.4, 0.1)), (0.4, (1.0, 0.78, 0.35)), (0.75, (1.0, 0.92, 0.65)), (1, (1, 1, 0.92))])
    return save("holy", rgb, np.clip(base * 0.55 + rays * 0.65 + rays2 * 0.4 + halo * 0.75, 0, 1))


def arcane():
    base = glow(0.0, 1.0, 1.6)
    ring = np.exp(-((R - 0.8) / 0.016) ** 2) + np.exp(-((R - 0.64) / 0.012) ** 2)
    marks = np.zeros(U.shape, np.float32)
    rnd = random.Random(12)
    for k in range(18):                                              # glyphs between the rings: ticks, little arcs, dots
        a = k * 2 * math.pi / 18
        kind = rnd.randrange(3)
        ca, sa = math.cos(a), math.sin(a)
        if kind == 0:
            marks = np.maximum(marks, line([(0.67 * ca, 0.67 * sa), (0.77 * ca, 0.77 * sa)], 0.011))
        elif kind == 1:
            b = a + 0.12
            marks = np.maximum(marks, line([(0.69 * ca, 0.69 * sa), (0.74 * math.cos(b), 0.74 * math.sin(b)), (0.69 * math.cos(b + 0.1), 0.69 * math.sin(b + 0.1))], 0.009))
        else:
            marks = np.maximum(marks, np.exp(-(np.hypot(U - 0.72 * ca, V - 0.72 * sa) / 0.02) ** 2))
    tri = np.zeros(U.shape, np.float32)                              # a star of two triangles inside
    for off in (0, math.pi / 3):
        pts = [(0.6 * math.cos(off + i * 2 * math.pi / 3 + math.pi / 2), 0.6 * math.sin(off + i * 2 * math.pi / 3 + math.pi / 2)) for i in range(4)]
        tri = np.maximum(tri, line(pts, 0.008))
    sp = sparkles(6, 9, 0.5, (0.03, 0.06))
    t = np.clip(base * 0.5 + ring * 0.8 + marks * 0.8 + tri * 0.45 + sp, 0, 1)
    rgb = ramp(t, [(0, (0.2, 0.12, 0.5)), (0.45, (0.5, 0.42, 1.0)), (0.75, (0.78, 0.72, 1.0)), (1, (1, 1, 1))])
    return save("arcane", rgb, np.clip(base * 0.5 + ring * 0.85 + marks * 0.85 + tri * 0.5 + sp, 0, 1))


def magic():
    base = glow(0.0, 1.0, 1.7)
    swirl = 0.5 + 0.5 * np.sin(A * 3 + R * 9 + fbm(3, 51, 2) * 2)
    sp = sparkles(18, 61, 0.88, (0.03, 0.08))
    t = np.clip(base * (0.4 + swirl * 0.25) + sp, 0, 1)
    rgb = ramp(t, [(0, (0.3, 0.18, 0.5)), (0.45, (0.66, 0.5, 1.0)), (0.75, (0.85, 0.78, 1.0)), (1, (1, 1, 1))])
    return save("magic", rgb, np.clip(base * (0.4 + swirl * 0.3) + sp, 0, 1))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    made = [flame(), frost(), storm(), venom(), holy(), arcane(), magic()]
    print("made", made)
    if len(sys.argv) > 1:                                            # a preview: each behind an icon, as in a bag cell
        icons = sys.argv[1]
        pairs = [("flame", "emberbrand"), ("frost", "frostbite"), ("storm", "stormcaller"), ("venom", "serpent_spear"),
                 ("holy", "dawnblade"), ("arcane", "oathkeeper"), ("magic", "silk_venom_cord"), ("frost", "arrows"),
                 ("flame", "scroll_fire_shield"), ("holy", "sunguard"), ("arcane", "archmage_staff"), ("magic", "oak_staff")]
        cell = 128
        sheet = Image.new("RGBA", (len(pairs) // 2 * (cell + 8) + 8, 2 * (cell + 8) + 8), (30, 26, 22, 255))
        for i, (k, ic) in enumerate(pairs):
            c = Image.new("RGBA", (cell, cell), (58, 50, 40, 255))
            g = Image.open(os.path.join(OUT, k + ".png")).convert("RGBA")
            c.alpha_composite(g)
            c.alpha_composite(Image.open(os.path.join(icons, ic + ".png")).convert("RGBA").resize((cell - 4, cell - 4)), (2, 2))
            sheet.alpha_composite(c, (8 + (i % 6) * (cell + 8), 8 + (i // 6) * (cell + 8)))
        out = r"E:\Unity\Projects\GameArtGeneration\Items\renders\glow_v2.png"
        sheet.resize((sheet.width * 3 // 2, sheet.height * 3 // 2), Image.LANCZOS).save(out)
        print("preview", out)
