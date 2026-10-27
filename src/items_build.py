"""Small item models for icons (2026-10-21, the user: "new icons ... for the armors, and the plants"; "You might need to
create models for some items, like the necklaces"; "For wild berries, however, it is not the bush, but the berry that
is the item").

The nine neck items of MedievalSetting (none has a model: a necklace is not drawn on the character) and a handful of
wild berries. Each is one object named after its item id (IT_<id>), built at real size and laid in the XZ plane
(front to -Y), its materials named IT_<Metal> so Unity remaps them to its own (ItemIconsMenu). Run in Blender:
exec(open(r"E:/Unity/Projects/GameArtGeneration/Items/src/items_build.py").read()); build(); export()
"""
import math
import random

import bmesh
import bpy
from mathutils import Matrix, Quaternion, Vector

ROOT = "E:/Unity/Projects/GameArtGeneration/Items"
OUT = "E:/Unity/Projects/MedievalSetting/Assets/Game/Items/Models"

# base colour, metallic, roughness -- for the Blender preview; Unity keeps its own by the same names
MATS = {
    "Silver": ((0.80, 0.81, 0.84), 0.9, 0.3),
    "Gold": ((0.92, 0.70, 0.28), 0.9, 0.3),
    "Bronze": ((0.62, 0.42, 0.22), 0.85, 0.4),
    "Pewter": ((0.58, 0.60, 0.62), 0.7, 0.5),
    "Leather": ((0.30, 0.18, 0.10), 0.0, 0.8),
    "Cord": ((0.16, 0.12, 0.08), 0.0, 0.9),
    "Silk": ((0.88, 0.86, 0.78), 0.0, 0.6),
    "Venom": ((0.45, 0.62, 0.18), 0.0, 0.35),
    "Bone": ((0.86, 0.82, 0.68), 0.0, 0.6),
    "Horn": ((0.22, 0.17, 0.13), 0.0, 0.5),
    "Ivory": ((0.90, 0.86, 0.72), 0.0, 0.45),
    "BerryRed": ((0.62, 0.05, 0.07), 0.0, 0.3),
    "BerryDark": ((0.18, 0.04, 0.16), 0.0, 0.3),
    "Leaf": ((0.18, 0.36, 0.10), 0.0, 0.7),
    "Stem": ((0.32, 0.22, 0.12), 0.0, 0.8),
    "Tint": ((0.8, 0.2, 0.2), 0.0, 0.25),        # the item's own colour in Unity (a potion, a scroll's seal, a gem)
    "Glass": ((0.75, 0.85, 0.85), 0.0, 0.1), "Cork": ((0.55, 0.40, 0.25), 0.0, 0.9),
    "Egg": ((0.92, 0.86, 0.74), 0.0, 0.5), "Honey": ((0.85, 0.55, 0.10), 0.0, 0.2), "Glaze": ((0.42, 0.2, 0.09), 0.0, 0.25), "Onion": ((0.72, 0.48, 0.22), 0.0, 0.5),
    "Chitin": ((0.16, 0.14, 0.10), 0.0, 0.3), "RatTail": ((0.78, 0.55, 0.52), 0.0, 0.6), "Plague": ((0.55, 0.52, 0.22), 0.0, 0.4),
    "CheesePaste": ((0.97, 0.88, 0.55), 0.0, 0.6), "CheeseHole": ((0.72, 0.58, 0.28), 0.0, 0.9),
    "Ink": ((0.06, 0.04, 0.03), 0.0, 0.7), "Scorch": ((0.42, 0.26, 0.12), 0.0, 0.9), "Char": ((0.05, 0.04, 0.035), 0.0, 0.95),
    "StemGreen": ((0.24, 0.36, 0.12), 0.0, 0.7), "Ghost": ((0.93, 0.93, 0.95), 0.0, 0.35), "GhostTip": ((0.2, 0.17, 0.2), 0.0, 0.5),
    "Husk": ((0.36, 0.24, 0.13), 0.0, 0.85), "Cotton": ((0.97, 0.96, 0.93), 0.0, 0.95),
    "Ash": ((0.74, 0.6, 0.42), 0.0, 0.7), "Oak": ((0.48, 0.33, 0.2), 0.0, 0.7), "Steel": ((0.6, 0.61, 0.64), 0.85, 0.35), "Rime": ((0.45, 0.75, 1.0), 0.4, 0.15), "Frost": ((0.85, 0.94, 1.0), 0.0, 0.6),
    "Fletch": ((0.8, 0.78, 0.72), 0.0, 0.8), "FletchRed": ((0.62, 0.12, 0.08), 0.0, 0.8), "FletchIce": ((0.62, 0.84, 1.0), 0.0, 0.6),
    "Padding": ((0.55, 0.48, 0.38), 0.0, 0.9), "PaddingDark": ((0.36, 0.3, 0.23), 0.0, 0.9), "Mail": ((0.36, 0.37, 0.4), 0.8, 0.55),
    "RobeUndyed": ((0.62, 0.56, 0.45), 0.0, 0.9), "RobeBlue": ((0.14, 0.2, 0.45), 0.0, 0.85), "RobeCream": ((0.86, 0.8, 0.66), 0.0, 0.85),
    "RobeViolet": ((0.3, 0.14, 0.4), 0.0, 0.85), "Felt": ((0.42, 0.35, 0.26), 0.0, 0.95), "BootDark": ((0.17, 0.15, 0.14), 0.0, 0.7),
    "Wool": ((0.90, 0.88, 0.82), 0.0, 0.9), "ChitinEdge": ((0.5, 0.33, 0.12), 0.0, 0.4), "Fat": ((0.93, 0.87, 0.74), 0.0, 0.5), "Marrow": ((0.6, 0.24, 0.18), 0.0, 0.6), "HornDark": ((0.2, 0.16, 0.13), 0.0, 0.6),
    "Heart": ((0.42, 0.2, 0.09), 0.0, 0.8), "HeartDark": ((0.3, 0.13, 0.06), 0.0, 0.8),
    "IvoryRoot": ((0.5, 0.36, 0.2), 0.0, 0.6), "IvoryOld": ((0.84, 0.76, 0.56), 0.0, 0.5), "RatEnamel": ((0.85, 0.52, 0.16), 0.0, 0.4),
    "CoverFighter": ((0.48, 0.09, 0.07), 0.0, 0.6), "CoverRogue": ((0.15, 0.14, 0.16), 0.0, 0.6),
    "CoverWizard": ((0.13, 0.16, 0.48), 0.0, 0.6), "CoverRanger": ((0.19, 0.32, 0.14), 0.0, 0.6),
    "CoverCleric": ((0.88, 0.85, 0.76), 0.0, 0.6), "CoverGeneral": ((0.4, 0.25, 0.13), 0.0, 0.6),
    "CoverShade": ((0.16, 0.1, 0.06), 0.0, 0.7), "Pages": ((0.9, 0.85, 0.7), 0.0, 0.9), "IronTrim": ((0.42, 0.42, 0.45), 0.8, 0.4), "WoodEnd": ((0.80, 0.63, 0.42), 0.0, 0.8),
    "WoodRing": ((0.66, 0.48, 0.30), 0.0, 0.8), "WoodPith": ((0.35, 0.22, 0.12), 0.0, 0.8), "Rope": ((0.62, 0.52, 0.34), 0.0, 0.9), "WoolCream": ((0.86, 0.80, 0.64), 0.0, 0.9),
    "SilkSheen": ((0.96, 0.96, 0.98), 0.0, 0.25), "WoolDark": ((0.26, 0.15, 0.08), 0.0, 0.9),
    "WoolRed": ((0.48, 0.28, 0.15), 0.0, 0.9), "Linen": ((0.90, 0.85, 0.72), 0.0, 0.9), "WoolBrown": ((0.42, 0.26, 0.16), 0.0, 0.9), "LeatherCured": ((0.50, 0.30, 0.15), 0.0, 0.6),
}


# the kit's own materials, by their names in MedievalVillageKit (VK_X: Unity remaps it to the kit's M_VK_X); the
# colours here only for the Blender preview. The goods atlas (T_VK_Goods: food, hides, furs) is mapped cell by cell.
KIT = {
    "Goods": (0.62, 0.48, 0.30), "Paper": (0.86, 0.80, 0.64), "Wood": (0.42, 0.30, 0.18), "EndGrain": (0.62, 0.48, 0.30),
    "BarkOak": (0.30, 0.24, 0.18), "Burlap": (0.58, 0.48, 0.32), "Clay": (0.62, 0.36, 0.22), "Iron": (0.30, 0.30, 0.32),
    "Coal": (0.08, 0.08, 0.09), "OreIronChunk": (0.42, 0.26, 0.18), "OreSilverChunk": (0.55, 0.56, 0.60),
    "Rock": (0.45, 0.44, 0.42), "StoneFresh": (0.70, 0.66, 0.58), "Cloth_Cream": (0.86, 0.82, 0.70), "Hide": (0.55, 0.40, 0.26),
    "Pigskin": (0.70, 0.52, 0.38), "GoblinHerb": (0.36, 0.38, 0.18), "WildGarlic": (0.22, 0.45, 0.16), "Yarrow": (0.4, 0.48, 0.3),
    "Fireweed": (0.62, 0.26, 0.48),
}
GOODS_CELLS = ("cabbage", "pumpkin", "carrot", "apple", "bread", "cheese", "fish", "fish_smoked",
               "hide", "fur", "meat", "ham", "sausage", "turnip", "herbs", "pomace")   # (the kit's vk_helpers order)
GOODS_PAD = 14 / 512


def goods_uv(cell, u, v):
    """cell-local (u, v) in 0..1 -> the goods atlas (4 x 4 cells, row 0 at the top; as the kit's vk_helpers.goods_uv)"""
    i = GOODS_CELLS.index(cell)
    c_, r_ = i % 4, i // 4
    s_ = 1 - 2 * GOODS_PAD
    return ((c_ + GOODS_PAD + min(max(u, 0.0), 1.0) * s_) / 4, (3 - r_ + GOODS_PAD + min(max(v, 0.0), 1.0) * s_) / 4)


def mat(name):
    full = name if name.startswith("VK_") else "IT_" + name
    m = bpy.data.materials.get(full)
    if m is None:
        m = bpy.data.materials.new(full)
        m.use_nodes = True
    col, metal, rough = (KIT[name[3:]], 0.0, 0.7) if name.startswith("VK_") else MATS[name]
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*col, 1.0)
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Roughness"].default_value = rough
    m.diffuse_color = (*col, 1.0)
    return m


# ------------------------------------------------------------------ meshes


def goods_map(bm, lay, cell, axis=(0, 0, 1), mode="wrap"):
    """a part on the goods atlas (as the kit's goods_map): v along axis over its extent, u the unsigned angle round it
    (mirrored: no seam); mode "caps" maps a cylinder's flat ends top-down, "plane" maps it flat (u along x, v along the
    axis's other side)"""
    vs = list(bm.verts)
    if not vs:
        return
    c = sum((v.co for v in vs), Vector()) / len(vs)
    ax = Vector(axis).normalized()
    ref = Vector((1, 0, 0)) if abs(ax.x) < 0.9 else Vector((0, 1, 0))
    ref = (ref - ax * ref.dot(ax)).normalized()
    side = ax.cross(ref)
    t = [(v.co - c).dot(ax) for v in vs]
    t0, t1 = min(t), max(t)
    rmax = max(((v.co - c) - ax * (v.co - c).dot(ax)).length for v in vs) or 1.0
    if mode == "plane":
        a = [(v.co - c).dot(ref) for v in vs]
        b = [(v.co - c).dot(side) for v in vs]
        a0, a1, b0, b1 = min(a), max(a), min(b), max(b)
        for f in bm.faces:
            for l in f.loops:
                p = l.vert.co - c
                l[lay].uv = goods_uv(cell, (p.dot(ref) - a0) / max(a1 - a0, 1e-6), (p.dot(side) - b0) / max(b1 - b0, 1e-6))
        return
    for f in bm.faces:
        if mode == "caps" and abs(f.normal.dot(ax)) > 0.85:
            for l in f.loops:
                p = l.vert.co - c
                l[lay].uv = goods_uv(cell, 0.5 + 0.45 * p.dot(ref) / rmax, 0.5 + 0.45 * p.dot(side) / rmax)
            continue
        for l in f.loops:
            p = l.vert.co - c
            hh = p.dot(ax)
            r = p - ax * hh
            u = 0.5 if r.length < 1e-7 else math.acos(max(-1.0, min(1.0, r.normalized().dot(ref)))) / math.pi
            l[lay].uv = goods_uv(cell, u, (hh - t0) / max(t1 - t0, 1e-6))


class Builder:
    """one item's mesh, put together from parts, each part on a material slot"""

    def __init__(self, name):
        self.bm = bmesh.new()
        self.bm.loops.layers.uv.new("UVMap")
        self.mats = []
        self.name = name

    def slot(self, m):
        if m not in self.mats:
            self.mats.append(m)
        return self.mats.index(m)

    def add(self, part_bm, m, matrix=Matrix(), uv=None, flat=False):
        """a part on material m; uv: None a box projection (2 per metre), "keep" the part's own (a kit sheet's region), or
        ("goods", cell, axis | "plane" | "caps");
        flat: shaded flat (a thin plate: smoothed, its sharp edges smear)"""
        idx = self.slot(m)
        part_bm.transform(matrix)
        for f in part_bm.faces:
            f.material_index = idx
            f.smooth = not flat
        part_bm.normal_update()                                     # (new faces have no normals yet: the UVs need them)
        lay = part_bm.loops.layers.uv.get("UVMap") or part_bm.loops.layers.uv.new("UVMap")
        if uv is None:
            for f in part_bm.faces:
                n = f.normal
                ax = max(range(3), key=lambda i: abs(n[i]))
                a, b = [(1, 2), (0, 2), (0, 1)][ax]
                for l in f.loops:
                    l[lay].uv = (l.vert.co[a] * 2.0, l.vert.co[b] * 2.0)
        elif uv == "keep":
            pass
        elif uv[0] == "wrap":                                       # ("wrap", axis, tiles round, tiles a metre along)
            ax = Vector(uv[1]).normalized()
            ref = Vector((1, 0, 0)) if abs(ax.x) < 0.9 else Vector((0, 0, 1))
            ref = (ref - ax * ref.dot(ax)).normalized()
            side = ax.cross(ref)
            for f in part_bm.faces:
                us = []
                for l in f.loops:
                    p_ = l.vert.co
                    us.append((math.atan2(p_.dot(side), p_.dot(ref)) / (2 * math.pi) + 0.5) * uv[2])
                if max(us) - min(us) > uv[2] * 0.5:                 # (a face across the seam: its low side round once more)
                    us = [u + uv[2] if u < uv[2] * 0.5 else u for u in us]
                for l, u in zip(f.loops, us):
                    l[lay].uv = (u, l.vert.co.dot(ax) * uv[3])
        else:
            goods_map(part_bm, lay, uv[1], *uv[2:])
        tmp = bpy.data.meshes.new("tmp")
        part_bm.to_mesh(tmp)
        part_bm.free()
        self.bm.from_mesh(tmp)
        bpy.data.meshes.remove(tmp)

    def finish(self, coll, flat=False):
        me = bpy.data.meshes.new("IT_" + self.name)
        self.bm.normal_update()
        self.bm.to_mesh(me)
        self.bm.free()
        for m in self.mats:
            me.materials.append(mat(m))
        if flat:
            for p in me.polygons:
                p.use_smooth = False
        ob = bpy.data.objects.new("IT_" + self.name, me)
        coll.objects.link(ob)
        return ob


def torus(R, r, seg=10, ring=6):
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=False, radius=1, segments=seg)   # placeholder, replaced below
    bm.clear()
    verts = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        c = Vector((math.cos(a), math.sin(a), 0))
        row = []
        for j in range(ring):
            b = 2 * math.pi * j / ring
            row.append(bm.verts.new(c * (R + r * math.cos(b)) + Vector((0, 0, r * math.sin(b)))))
        verts.append(row)
    for i in range(seg):
        for j in range(ring):
            bm.faces.new((verts[i][j], verts[(i + 1) % seg][j], verts[(i + 1) % seg][(j + 1) % ring], verts[i][(j + 1) % ring]))
    return bm


def tube(points, radius, ring=6, closed=True, taper=None):
    """a round tube along points (a cord, a thong); taper(t) scales its radius"""
    bm = bmesh.new()
    n = len(points)
    rows = []
    for i, p in enumerate(points):
        a, b = points[(i - 1) % n] if closed or i > 0 else points[0], points[(i + 1) % n] if closed or i < n - 1 else points[-1]
        t = (b - a).normalized()
        side = t.cross(Vector((0, 1, 0)))
        if side.length < 1e-4:
            side = t.cross(Vector((1, 0, 0)))
        side.normalize()
        up = side.cross(t)
        rr = radius * (taper(i / max(1, n - 1)) if taper else 1.0)
        rows.append([bm.verts.new(p + (side * math.cos(2 * math.pi * j / ring) + up * math.sin(2 * math.pi * j / ring)) * rr)
                     for j in range(ring)])
    for i in range(n if closed else n - 1):
        r0, r1 = rows[i], rows[(i + 1) % n]
        for j in range(ring):
            bm.faces.new((r0[j], r1[j], r1[(j + 1) % ring], r0[(j + 1) % ring]))
    if not closed:
        bm.faces.new(list(reversed(rows[0])))
        bm.faces.new(rows[-1])
    return bm


def sphere(r, sx=1.0, sy=1.0, sz=1.0, seg=12, rings=8):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=r)
    bmesh.ops.scale(bm, vec=Vector((sx, sy, sz)), verts=bm.verts)
    return bm


def cyl(r, depth, seg=16):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=depth)
    return bm


def box(x, y, z):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector((x, y, z)), verts=bm.verts)
    return bm


def horn(length, base, bend, seg=10, ring=8):
    """a curved tapering cone (a claw, a tusk, a tooth): from its root at the origin down -Z, bent toward +X"""
    pts = []
    for i in range(seg + 1):
        t = i / seg
        a = bend * t
        pts.append(Vector((length / max(bend, 1e-3) * (1 - math.cos(a)) if bend > 1e-3 else 0, 0,
                           -(length / max(bend, 1e-3) * math.sin(a)) if bend > 1e-3 else -length * t)))
    return tube(pts, base, ring=ring, closed=False, taper=lambda t: max(0.08, 1 - t ** 0.9))


# ------------------------------------------------------------------ the loop a necklace hangs in


def loop_points(width=0.15, depth=0.19, n=72):
    """the chain's path laid flat, hanging to a point at the bottom (the pendant's): the XZ plane, top at z 0"""
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        h = (1 - math.cos(a)) / 2                                   # 0 at the top, 1 at the bottom
        x = width / 2 * math.sin(a) * (1 - 0.45 * h)               # narrowing as it hangs
        z = -depth * h - 0.12 * depth * h ** 6                     # drawn down to a point at the pendant
        pts.append(Vector((x, 0, z)))
    return pts


def resample(pts, pitch, closed=True):
    seq = pts + ([pts[0]] if closed else [])
    out, carry = [seq[0].copy()], 0.0
    for a, b in zip(seq, seq[1:]):
        seg = (b - a).length
        d = pitch - carry
        while d <= seg:
            out.append(a.lerp(b, d / seg))
            d += pitch
        carry = seg - (d - pitch)
    return out[:-1] if closed else out


def chain(b, m, pts, link=0.009, wire=0.0016, skip_bottom=0.0):
    """links along the path, each a stretched ring, every other one turned a quarter about the path"""
    path = resample(pts, link * 1.55)
    bottom = min(p.z for p in path)
    for i, p in enumerate(path):
        if skip_bottom and p.z < bottom + skip_bottom:
            continue
        q = path[(i + 1) % len(path)]
        t = (q - p).normalized()
        part = torus(link * 0.5, wire, seg=10, ring=5)
        bmesh.ops.scale(part, vec=Vector((1.45, 1.0, 1.0)), verts=part.verts)    # long along its own x
        rot = Vector((1, 0, 0)).rotation_difference(t).to_matrix().to_4x4()
        spin = Matrix.Rotation(math.pi / 2 if i % 2 else 0.0, 4, "X")
        b.add(part, m, Matrix.Translation(p.lerp(q, 0.5)) @ rot @ spin)


def cord(b, m, pts, radius=0.0022, twist=False):
    if not twist:
        b.add(tube(pts, radius, ring=6), m)
        return
    for k in range(2):                                             # two strands twisted round each other
        n = len(pts)
        tw = []
        for i, p in enumerate(pts):
            t = (pts[(i + 1) % n] - pts[i - 1]).normalized()
            side = t.cross(Vector((0, 1, 0))).normalized()
            up = side.cross(t)
            a = i * 0.9 + k * math.pi
            tw.append(p + (side * math.cos(a) + up * math.sin(a)) * radius * 0.9)
        b.add(tube(tw, radius * 0.8, ring=5), m)


def bottom(pts):
    return min(pts, key=lambda p: p.z)


# ------------------------------------------------------------------ the necklaces


def silver_necklace(coll):
    b = Builder("silver_necklace")
    pts = loop_points(0.14, 0.17)
    chain(b, "Silver", pts)
    lo = bottom(pts)
    b.add(torus(0.004, 0.0013), "Silver", Matrix.Translation(lo + Vector((0, 0, -0.004))) @ Matrix.Rotation(math.pi / 2, 4, "X"))
    drop = sphere(0.012, 1.0, 0.45, 1.5)                            # a plain teardrop
    b.add(drop, "Silver", Matrix.Translation(lo + Vector((0, 0, -0.024))))
    return b.finish(coll)


def gold_necklace(coll):
    b = Builder("gold_necklace")
    pts = loop_points(0.15, 0.18)
    chain(b, "Gold", pts, link=0.012, wire=0.0024)
    lo = bottom(pts)
    b.add(torus(0.005, 0.0018), "Gold", Matrix.Translation(lo + Vector((0, 0, -0.005))) @ Matrix.Rotation(math.pi / 2, 4, "X"))
    at = lo + Vector((0, 0, -0.024))
    b.add(torus(0.012, 0.0025, seg=20, ring=6), "Gold", Matrix.Translation(at) @ Matrix.Rotation(math.pi / 2, 4, "X"))   # the empty setting's bezel
    b.add(cyl(0.011, 0.002, seg=20), "Gold", Matrix.Translation(at + Vector((0, 0.002, 0))) @ Matrix.Rotation(math.pi / 2, 4, "X"))
    for k in range(4):                                             # its prongs, waiting for a stone
        a = math.pi / 4 + k * math.pi / 2
        p = at + Vector((math.cos(a) * 0.012, -0.004, math.sin(a) * 0.012))
        b.add(box(0.002, 0.006, 0.002), "Gold", Matrix.Translation(p))
    return b.finish(coll)


def bear_claw_necklace(coll):
    b = Builder("bear_claw_necklace")
    pts = loop_points(0.16, 0.18)
    cord(b, "Leather", pts, 0.0025)
    lo = bottom(pts)
    for k, dx in enumerate((-0.036, -0.018, 0.0, 0.018, 0.036)):
        p = min(pts, key=lambda q: abs(q.x - dx) + (0 if q.z < lo.z + 0.05 else 1))
        ln = 0.045 if k == 2 else 0.038 if k in (1, 3) else 0.03
        tilt = Matrix.Rotation(-dx * 4.0, 4, "Y")                  # fanned out round the loop
        b.add(cyl(0.006, 0.006, seg=10), "Leather", Matrix.Translation(p + Vector((0, 0, -0.003))) @ Matrix.Rotation(math.pi / 2, 4, "X"))
        b.add(horn(ln, 0.0065, 1.1), "Horn", Matrix.Translation(p + Vector((0, 0, -0.005))) @ tilt)
    return b.finish(coll)


def silk_venom_cord(coll):
    b = Builder("silk_venom_cord")
    pts = loop_points(0.14, 0.17)
    cord(b, "Silk", pts, 0.0026, twist=True)
    lo = bottom(pts)
    b.add(torus(0.006, 0.002, seg=12), "Silk", Matrix.Translation(lo + Vector((0, 0, -0.006))) @ Matrix.Rotation(math.pi / 2, 4, "X"))
    sac = sphere(0.013, 1.0, 0.75, 1.3, seg=16, rings=10)           # the dried sac, wrapped in silk bands
    b.add(sac, "Venom", Matrix.Translation(lo + Vector((0, 0, -0.026))))
    for z in (-0.019, -0.03):
        b.add(torus(0.0115 if z > -0.025 else 0.0125, 0.0013, seg=16), "Silk", Matrix.Translation(lo + Vector((0, 0, z))))
    return b.finish(coll)


def rat_skull(b, at, s, turn=0.0):
    m = Matrix.Translation(at) @ Matrix.Rotation(turn, 4, "Y") @ Matrix.Scale(s, 4)
    b.add(sphere(0.012, 1.0, 0.9, 0.85), "Bone", m)                                         # the cranium
    b.add(sphere(0.007, 0.8, 0.8, 1.6), "Bone", m @ Matrix.Translation(Vector((0, -0.002, -0.015))))   # the snout, down
    for x in (-0.0045, 0.0045):
        b.add(sphere(0.003, 1, 1, 1, seg=8, rings=6), "Cord", m @ Matrix.Translation(Vector((x, -0.0085, -0.004))))   # eye holes
    for x in (-0.0015, 0.0015):
        b.add(horn(0.006, 0.0012, 0.4, seg=4, ring=5), "Ivory", m @ Matrix.Translation(Vector((x, -0.004, -0.025))))  # incisors


def goblin_fetish(coll):
    b = Builder("goblin_fetish")
    pts = loop_points(0.15, 0.17)
    cord(b, "Cord", pts, 0.0024, twist=True)
    lo = bottom(pts)
    rat_skull(b, lo + Vector((0, -0.002, -0.017)), 1.0)
    for dx, turn in ((-0.03, 0.3), (0.03, -0.3)):
        p = min(pts, key=lambda q: abs(q.x - dx) + (0 if q.z < lo.z + 0.05 else 1))
        rat_skull(b, p + Vector((0, -0.002, -0.014)), 0.75, turn)
    random.seed(7)
    for dx in (-0.05, -0.042, -0.016, -0.01, 0.012, 0.018, 0.044, 0.05):   # a goblin's own teeth between them
        p = min(pts, key=lambda q: abs(q.x - dx) + (0 if q.z < lo.z + 0.06 else 1))
        b.add(horn(0.012, 0.0025, 0.5, seg=5, ring=5), "Bone",
              Matrix.Translation(p + Vector((0, 0, -0.002))) @ Matrix.Rotation(random.uniform(-0.3, 0.3), 4, "Y"))
    return b.finish(coll)


def guild_seal(coll):
    b = Builder("guild_seal")
    pts = loop_points(0.15, 0.18)
    chain(b, "Bronze", pts, link=0.011, wire=0.002)
    lo = bottom(pts)
    b.add(torus(0.005, 0.0018), "Bronze", Matrix.Translation(lo + Vector((0, 0, -0.005))) @ Matrix.Rotation(math.pi / 2, 4, "X"))
    at = lo + Vector((0, 0, -0.03))
    face = Matrix.Translation(at) @ Matrix.Rotation(math.pi / 2, 4, "X")
    b.add(cyl(0.02, 0.004, seg=28), "Bronze", face)                                   # the seal
    b.add(torus(0.0195, 0.0016, seg=28), "Bronze", face @ Matrix.Translation(Vector((0, 0, 0.002))))   # its rim
    front = at + Vector((0, -0.0025, 0))                                              # its mark: a tower over crossed blades
    for a in (0.7, -0.7):
        b.add(box(0.0018, 0.0012, 0.03), "Bronze", Matrix.Translation(front) @ Matrix.Rotation(a, 4, "Y"))
    b.add(box(0.008, 0.002, 0.014), "Bronze", Matrix.Translation(front + Vector((0, -0.0005, 0.001))))
    for x in (-0.003, 0.0, 0.003):
        b.add(box(0.0018, 0.002, 0.003), "Bronze", Matrix.Translation(front + Vector((x, -0.0005, 0.009))))
    return b.finish(coll)


def tusk_necklace(coll):
    b = Builder("tusk_necklace")
    pts = loop_points(0.17, 0.19)
    cord(b, "Leather", pts, 0.003)
    lo = bottom(pts)
    for dx, ln in ((-0.03, 0.05), (0.0, 0.062), (0.03, 0.05)):
        p = min(pts, key=lambda q: abs(q.x - dx) + (0 if q.z < lo.z + 0.05 else 1))
        b.add(torus(0.0045, 0.0022, seg=10), "Leather", Matrix.Translation(p + Vector((0, 0, -0.004))) @ Matrix.Rotation(math.pi / 2, 4, "X"))
        side = 1 if dx >= 0 else -1
        b.add(horn(ln, 0.009, 0.9), "Ivory", Matrix.Translation(p + Vector((0, 0, -0.007))) @ Matrix.Rotation(-dx * 5.0, 4, "Y")
              @ Matrix.Scale(1, 4) @ (Matrix.Scale(-1, 4, Vector((1, 0, 0))) if side < 0 else Matrix()))
    return b.finish(coll)


def pilgrims_pendant(coll):
    b = Builder("pilgrims_pendant")
    pts = loop_points(0.14, 0.17)
    cord(b, "Cord", pts, 0.0022)
    lo = bottom(pts)
    b.add(torus(0.004, 0.0014), "Pewter", Matrix.Translation(lo + Vector((0, 0, -0.004))) @ Matrix.Rotation(math.pi / 2, 4, "X"))
    hinge = lo + Vector((0, 0, -0.01))                             # a scallop shell, the pilgrim's sign: ribs fanned from its hinge
    b.add(box(0.012, 0.003, 0.004), "Pewter", Matrix.Translation(hinge))
    ribs = 9
    for k in range(ribs):
        a = math.radians(-62 + 124 * k / (ribs - 1))
        d = Vector((math.sin(a), 0, -math.cos(a)))
        rib = horn(0.028, 0.0036, 0.0, seg=4, ring=6)
        rot = Vector((0, 0, -1)).rotation_difference(d).to_matrix().to_4x4()
        b.add(rib, "Pewter", Matrix.Translation(hinge + Vector((0, -0.0025, 0))) @ rot)
    fan = sphere(0.025, 1.15, 0.06, 0.95, seg=20, rings=8)         # the shell's web between the ribs
    b.add(fan, "Pewter", Matrix.Translation(hinge + Vector((0, 0.001, -0.016))))
    return b.finish(coll)


def silver_locket(coll):
    b = Builder("silver_locket")
    pts = loop_points(0.14, 0.17)
    chain(b, "Silver", pts, link=0.008, wire=0.0014)
    lo = bottom(pts)
    b.add(torus(0.004, 0.0013), "Silver", Matrix.Translation(lo + Vector((0, 0, -0.004))) @ Matrix.Rotation(math.pi / 2, 4, "X"))
    at = lo + Vector((0, 0, -0.024))
    b.add(sphere(0.015, 0.85, 0.32, 1.0, seg=24, rings=10), "Silver", Matrix.Translation(at))     # the locket's two halves
    b.add(torus(0.0145, 0.0012, seg=28), "Silver", Matrix.Translation(at) @ Matrix.Scale(1, 4) @ Matrix.Rotation(math.pi / 2, 4, "X")
          @ Matrix.Scale(0.85, 4, Vector((1, 0, 0))))
    b.add(box(0.003, 0.004, 0.004), "Silver", Matrix.Translation(at + Vector((0, 0, 0.016))))
    return b.finish(coll)


# ------------------------------------------------------------------ the berries


def berries(coll):
    """a handful of wild berries: red and dark ones on a forked stem, two leaves"""
    b = Builder("berries")
    random.seed(11)
    stem = [Vector((0.0, 0, 0.035)), Vector((0.002, 0, 0.02)), Vector((0.0, 0, 0.005)), Vector((-0.004, 0, -0.008))]
    b.add(tube(stem, 0.0012, ring=5, closed=False), "Stem")
    spots = [(-0.012, 0.0, -0.012), (0.004, -0.004, -0.016), (0.016, 0.002, -0.008), (-0.004, 0.006, -0.026), (0.012, -0.002, -0.028),
             (-0.016, -0.004, -0.03), (0.0, -0.008, -0.04), (0.02, 0.004, -0.04), (-0.01, 0.004, -0.044)]
    for k, (x, y, z) in enumerate(spots):
        r = random.uniform(0.0065, 0.0085)
        m = "BerryDark" if k in (2, 5, 8) else "BerryRed"
        p = Vector((x, y, z))
        b.add(tube([Vector((-0.002, 0, 0.0)), p + Vector((0, 0, r))], 0.0006, ring=4, closed=False), "Stem")
        b.add(sphere(r, 1.0, 1.0, 0.95, seg=12, rings=8), m, Matrix.Translation(p))
        b.add(sphere(r * 0.25, 1, 1, 0.4, seg=6, rings=4), "Stem", Matrix.Translation(p + Vector((0, 0, -r * 0.95))))   # the dry calyx
    for side in (-1, 1):                                            # two leaves at the top of the stem
        leaf = sphere(0.016, 0.42, 0.06, 1.0, seg=12, rings=8)
        b.add(leaf, "Leaf", Matrix.Translation(Vector((side * 0.012, 0.004, 0.03))) @ Matrix.Rotation(side * 0.9, 4, "Y"))
    return b.finish(coll)


# ------------------------------------------------------------------ the second set (2026-10-21, the user: "keep working on
# the icons ... You can use stuff from the medieval kit, I know we have cheese over there"): food on the kit's goods
# atlas, potions and scrolls tinted per item in Unity (IT_Tint), loot, ores and the crafting materials. Items with a kit
# or weapon model of their own (the tomes' book, the candlestick, the war horns, arrows and bolts) are not made here.


def lathe(profile, seg=20):
    """a body of revolution round Z from (radius, z) pairs bottom to top, closed at both ends (a zero radius: a pole)"""
    bm = bmesh.new()
    rows = []
    for r, z in profile:
        if r < 1e-6:
            rows.append(bm.verts.new((0, 0, z)))
        else:
            rows.append([bm.verts.new((r * math.cos(2 * math.pi * j / seg), r * math.sin(2 * math.pi * j / seg), z)) for j in range(seg)])
    for r0, r1 in zip(rows, rows[1:]):
        for j in range(seg):
            k = (j + 1) % seg
            if isinstance(r0, list) and isinstance(r1, list):
                bm.faces.new((r0[j], r0[k], r1[k], r1[j]))
            elif isinstance(r1, list):
                bm.faces.new((r0, r1[k], r1[j]))
            elif isinstance(r0, list):
                bm.faces.new((r0[j], r0[k], r1))
    if isinstance(rows[0], list):
        bm.faces.new(list(reversed(rows[0])))
    if isinstance(rows[-1], list):
        bm.faces.new(rows[-1])
    return bm


def lump(r, seed, rough=0.28, sx=1.0, sy=1.0, sz=1.0, subdiv=2):
    """a rough stone lump: an icosphere pushed in and out"""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=r)
    rnd = random.Random(seed)
    for v in bm.verts:
        v.co *= 1 + rnd.uniform(-rough, rough)
        v.co.x *= sx; v.co.y *= sy; v.co.z *= sz
    return bm


def cone(r0, r1, h, seg=12):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r0, radius2=r1, depth=h)
    return bm


def leaves(b, at, n=3, size=0.035, seed=1, m="Leaf"):
    rnd = random.Random(seed)
    for k in range(n):
        a = 2 * math.pi * k / n + rnd.uniform(-0.3, 0.3)
        leaf = sphere(size, 0.35, 0.05, 1.0, seg=10, rings=6)
        b.add(leaf, m, Matrix.Translation(at) @ Matrix.Rotation(a, 4, "Z") @ Matrix.Rotation(0.5, 4, "X")
              @ Matrix.Translation(Vector((0, 0, size * 0.9))))


# ---- food (the goods atlas)

def apple(coll):
    b = Builder("apple")
    b.add(sphere(0.04, 1.0, 1.0, 0.9, seg=16, rings=10), "VK_Goods", uv=("goods", "apple", (0, 0, 1)))
    b.add(tube([Vector((0, 0, 0.03)), Vector((0.003, 0, 0.05))], 0.002, ring=5, closed=False), "Stem")
    b.add(sphere(0.016, 0.35, 0.06, 1.0, seg=8, rings=6), "Leaf", Matrix.Translation(Vector((0.012, 0, 0.048))) @ Matrix.Rotation(-0.9, 4, "Y"))
    return b.finish(coll)


def cabbage(coll):
    b = Builder("cabbage")
    b.add(sphere(0.09, 1.0, 1.0, 0.92, seg=18, rings=12), "VK_Goods", uv=("goods", "cabbage", (0, 0, 1)))
    for k in range(5):                                              # outer leaves cupping it
        a = 2 * math.pi * k / 5
        shell = sphere(0.075, 1.0, 0.25, 1.0, seg=12, rings=8)
        b.add(shell, "VK_Goods", Matrix.Rotation(a, 4, "Z") @ Matrix.Translation(Vector((0, -0.07, -0.01))) @ Matrix.Rotation(0.35, 4, "X"),
              uv=("goods", "cabbage", (0, 1, 0)))
    return b.finish(coll)


def carrot(coll):
    """a carrot (2026-10-22, the user: "fix ... the carrot"; the first was a thin cone with strings): a root with full
    shoulders tapering to a point and bent a little, on the kit's carrot cell (its rings), its crown and three feathery
    fronds -- a stalk each with leaflets in pairs along it"""
    b = Builder("carrot")
    prof = [(0.0, -0.2), (0.004, -0.19), (0.008, -0.16), (0.013, -0.12), (0.018, -0.07), (0.022, -0.03), (0.024, -0.008),
            (0.021, 0.002), (0.012, 0.007), (0.0, 0.008)]
    root = lathe(prof, 18)
    rnd = random.Random(4)
    for v in root.verts:                                            # bent a little toward its tip, a bit lumpy
        t = -v.co.z / 0.2
        v.co.x += 0.018 * t * t
        k = 1 + rnd.uniform(-0.04, 0.04)
        v.co.x *= k if v.co.z < 0 else 1
    b.add(root, "VK_Goods", uv=("goods", "carrot", (0, 0, 1)))
    b.add(lathe([(0.0, 0.004), (0.01, 0.006), (0.006, 0.014), (0.0, 0.015)], 10), "Stem")   # the crown
    for k, (a, lean, ln) in enumerate(((0.3, 0.25, 0.16), (2.4, 0.4, 0.13), (4.4, 0.35, 0.145))):
        d = Vector((math.cos(a) * math.sin(lean), math.sin(a) * math.sin(lean), math.cos(lean)))
        side = Vector((-math.sin(a), math.cos(a), 0))
        pts = [Vector((0, 0, 0.01)) + d * ln * t + Vector((0, 0, -0.015 * t * t)) for t in (0.0, 0.33, 0.66, 1.0)]
        b.add(tube(pts, 0.0028, ring=5, closed=False, taper=lambda t: 1 - 0.6 * t), "Leaf")
        for j in range(5):                                          # leaflets in pairs, smaller toward the tip
            t = 0.3 + 0.14 * j
            at = Vector((0, 0, 0.01)) + d * ln * t + Vector((0, 0, -0.015 * t * t))
            sz = 0.02 * (1.1 - 0.5 * (j / 4))
            for sgn in (-1, 1):
                leaf = sphere(sz, 0.22, 0.05, 1.0, seg=8, rings=6)
                out = (side * sgn + d * 0.6).normalized()
                rot = Vector((0, 0, 1)).rotation_difference(out).to_matrix().to_4x4()
                b.add(leaf, "Leaf", Matrix.Translation(at + out * sz * 0.8) @ rot)
        b.add(sphere(0.012, 0.25, 0.05, 1.0, seg=8, rings=6), "Leaf", Matrix.Translation(pts[-1] + d * 0.01)
              @ Vector((0, 0, 1)).rotation_difference(d).to_matrix().to_4x4())   # its tip leaflet
    return b.finish(coll)


def onion(coll):
    b = Builder("onion")
    b.add(lathe([(0.004, -0.04), (0.03, -0.032), (0.045, -0.01), (0.042, 0.012), (0.025, 0.03), (0.008, 0.045), (0.003, 0.06)], 18), "Onion")
    for k in range(6):                                              # its dry roots
        a = 2 * math.pi * k / 6
        b.add(tube([Vector((0, 0, -0.038)), Vector((math.cos(a) * 0.012, math.sin(a) * 0.012, -0.05))], 0.0012, ring=4, closed=False), "Stem")
    return b.finish(coll)


def pumpkin(coll):
    b = Builder("pumpkin")
    prof = sphere(0.12, 1.0, 1.0, 0.75, seg=32, rings=14)
    for v in prof.verts:                                            # its ribs
        a = math.atan2(v.co.y, v.co.x)
        v.co.x *= 1 - 0.06 * abs(math.cos(4 * a)); v.co.y *= 1 - 0.06 * abs(math.cos(4 * a))
    b.add(prof, "VK_Goods", uv=("goods", "pumpkin", (0, 0, 1)))
    b.add(tube([Vector((0, 0, 0.08)), Vector((0.01, 0, 0.115)), Vector((0.025, 0, 0.125))], 0.009, ring=6, closed=False), "Stem")
    return b.finish(coll)


def turnip(coll):
    b = Builder("turnip")
    b.add(lathe([(0.001, -0.09), (0.006, -0.06), (0.03, -0.03), (0.05, 0.0), (0.045, 0.025), (0.02, 0.04), (0.006, 0.045)], 18),
          "VK_Goods", uv=("goods", "turnip", (0, 0, 1)))
    leaves(b, Vector((0, 0, 0.04)), 4, 0.04, 3)
    return b.finish(coll)


def wheel_part(prof, a0, a1, seg):
    """a cheese's rind: the profile (radius, z) turned from angle a0 to a1 (an open ring: a wheel with a wedge out, or the
    wedge itself) and its two cut faces (separate: the paste)"""
    rind = bmesh.new()
    rows = []
    for j in range(seg + 1):
        a = a0 + (a1 - a0) * j / seg
        rows.append([rind.verts.new((r * math.cos(a), r * math.sin(a), z)) for r, z in prof])
    for j in range(seg):
        for i in range(len(prof) - 1):
            q = (rows[j][i], rows[j + 1][i], rows[j + 1][i + 1], rows[j][i + 1])
            if len({v.co.to_tuple(6) for v in q}) >= 3:
                rind.faces.new(q)
    rind.verts.ensure_lookup_table()
    bmesh.ops.remove_doubles(rind, verts=rind.verts, dist=1e-6)
    cuts = []
    for a, flip in ((a0, False), (a1, True)):
        c = bmesh.new()
        vs = [c.verts.new((r * math.cos(a), r * math.sin(a), z)) for r, z in prof]
        vs = [v for i, v in enumerate(vs) if i == 0 or (v.co - vs[i - 1].co).length > 1e-6]
        c.faces.new(list(reversed(vs)) if flip else vs)
        cuts.append((c, a))
    return rind, cuts


def holes(b, a, R, H, seed, flip, M=Matrix()):
    """the paste's holes on a cut face at angle a: dark rounds just proud of it"""
    rnd = random.Random(seed)
    n = Vector((-math.sin(a), math.cos(a), 0)) * (1 if flip else -1)   # out of the face: back at the start angle, on at the end
    for k in range(5):
        r = rnd.uniform(0.25, 0.85) * R
        z = rnd.uniform(0.2, 0.8) * H
        size = rnd.uniform(0.006, 0.011)
        at = Vector((r * math.cos(a), r * math.sin(a), z)) + n * 0.0008
        d = cyl(size, 0.001, seg=10)
        b.add(d, "CheeseHole", M @ Matrix.Translation(at) @ Vector((0, 0, 1)).rotation_difference(n).to_matrix().to_4x4(), flat=True)


def cheese(coll):
    """a cheese (2026-10-22, the user: "fix the cheese"; the kit's cheese cell is plain yellow, so the first read as a
    yellow blob): a wheel with rounded edges, its rind the kit's cheese cell, a wedge cut out showing the pale paste and
    its holes, the wedge lying before it"""
    b = Builder("cheese")
    R, H, e = 0.12, 0.085, 0.014
    prof = [(0.0, 0.0), (R - e, 0.0), (R - e * 0.3, e * 0.3), (R, e), (R, H - e), (R - e * 0.3, H - e * 0.3), (R - e, H), (0.0, H)]
    cut = math.radians(50)
    rind, cuts = wheel_part(prof, cut / 2, 2 * math.pi - cut / 2, 40)
    turn = Matrix.Rotation(-math.pi / 2 - 0.35, 4, "Z")              # its cut toward the front (-Y), a little to the left
    b.add(rind, "VK_Goods", turn, uv=("goods", "cheese", (0, 0, 1), "caps"))
    for c, a in cuts:
        b.add(c, "CheesePaste", turn, flat=True)
        holes(b, a, R, H, int(a * 100), a > math.pi, turn)
    wrind, wcuts = wheel_part(prof, -cut / 2, cut / 2, 8)          # the wedge, laid on its side before the wheel
    place = Matrix.Translation(Vector((0.17, -0.07, 0.0))) @ Matrix.Rotation(-0.9, 4, "Z") @ Matrix.Rotation(math.pi / 2, 4, "X") \
        @ Matrix.Translation(Vector((0, 0, -H / 2)))
    b.add(wrind, "VK_Goods", place, uv=("goods", "cheese", (0, 0, 1), "caps"))
    for (c, a) in wcuts:
        b.add(c, "CheesePaste", place, flat=True)
        holes(b, a, R, H, 7 + int(a * 100), a > 0, place)
    return b.finish(coll)


def eggs(coll):
    b = Builder("eggs")
    for x, y, rz in ((-0.03, 0, 0.3), (0.03, 0.01, -0.4), (0.0, -0.035, 1.2)):
        b.add(sphere(0.022, 1.0, 1.0, 1.32, seg=14, rings=10), "Egg",
              Matrix.Translation(Vector((x, y, 0.022))) @ Matrix.Rotation(rz, 4, "Z") @ Matrix.Rotation(1.4, 4, "X"))
    return b.finish(coll)


def honey(coll):
    """a honey pot (2026-10-27, Daniel: "the honey is weird"; the first, a clay jar under a burlap cap, read as a sack with
    a crust): a glazed pot, open, full to the neck, a wooden dipper standing in it, honey run over the lip"""
    b = Builder("honey")                                            # (about a potion's budget: 16 sides, no inside under the honey)
    pot = [(0.0, 0.0), (0.04, 0.0), (0.055, 0.022), (0.06, 0.058), (0.053, 0.09), (0.044, 0.106),   # outside, up
           (0.05, 0.114), (0.05, 0.119), (0.043, 0.119),                                          # the lip
           (0.039, 0.108), (0.041, 0.099), (0.0, 0.099)]                                          # inside, down to the honey
    b.add(lathe(pot, 16), "Glaze")
    b.add(lathe([(0.0425, 0.0995), (0.0425, 0.1), (0.0, 0.1015)], 16), "Honey")   # full to the neck
    tilt = Matrix.Translation(Vector((0.004, 0.0, 0.1))) @ Matrix.Rotation(math.radians(24), 4, "Y")   # the dipper, standing in it
    b.add(cyl(0.0035, 0.115, seg=6), "Oak", tilt @ Matrix.Translation(Vector((0, 0, 0.045))))
    for k in range(3):                                              # the grooved head, half sunk, coated
        b.add(cyl(0.0105 - 0.0015 * abs(k - 1), 0.005, seg=8), "Honey", tilt @ Matrix.Translation(Vector((0, 0, -0.002 + k * 0.0065))))
    for a, z_end in ((4.2, 0.064), (0.6, 0.08)):                    # honey run over the lip (front -Y, back)
        c, s = math.cos(a), math.sin(a)
        pts = [Vector((c * r, s * r, z)) for r, z in ((0.047, 0.1195), (0.0515, 0.116), (0.047, 0.106), (0.051, 0.096),
                                                       (0.057, 0.082), (0.0605, z_end))]
        pts = [p for p in pts if p.z >= z_end]
        b.add(tube(pts, 0.0035, ring=5, closed=False, taper=lambda t: 1 + 0.35 * t * t), "Honey")   # gathering to a drop
    return b.finish(coll)


def meat_slab(name, w, h, d, seed, bone=False):
    def f(coll):
        b = Builder(name)
        slab = lump(0.5, seed, 0.12, w, d, h, subdiv=3)
        b.add(slab, "VK_Goods", uv=("goods", "meat", (0, 0, 1), "plane"))
        if bone:
            b.add(tube([Vector((-w * 0.5, 0, 0)), Vector((w * 0.62, 0, 0))], 0.012, ring=8, closed=False), "Bone")
            b.add(sphere(0.02, 1, 1, 1), "Bone", Matrix.Translation(Vector((w * 0.64, 0, 0))))
        return b.finish(coll)
    return f


def haunch(name, s, seed):
    """a haunch (the ham cell) with its bone sticking out"""
    def f(coll):
        b = Builder(name)
        body = lathe([(0.0, -0.11), (0.05, -0.1), (0.085, -0.04), (0.08, 0.03), (0.05, 0.08), (0.022, 0.11), (0.0, 0.115)], 20)
        rnd = random.Random(seed)
        for v in body.verts:
            v.co *= 1 + rnd.uniform(-0.04, 0.04)
        b.add(body, "VK_Goods", Matrix.Scale(s, 4), uv=("goods", "ham", (0, 0, 1)))
        b.add(tube([Vector((0, 0, 0.1 * s)), Vector((0, 0, 0.17 * s))], 0.013 * s, ring=8, closed=False), "Bone")
        b.add(sphere(0.02 * s, 1.1, 1, 0.8), "Bone", Matrix.Translation(Vector((0, 0, 0.175 * s))))
        return b.finish(coll)
    return f


def venison(coll):
    """a haunch of venison (2026-10-22, the user: "Then you can do venison and mammoths meat"; the two were one cured ham
    at two sizes): a deer's hind leg -- a lean, dark red haunch narrowing to a long slender shank, the bone and knuckle
    out at its end, tied round with a string -- raw meat (the kit's meat cell), not the cured ham"""
    b = Builder("venison")
    prof = [(0.0, -0.13), (0.045, -0.12), (0.07, -0.08), (0.072, -0.03), (0.055, 0.02), (0.034, 0.07), (0.022, 0.12),
            (0.018, 0.16), (0.0, 0.165)]
    body = lathe(prof, 18)
    rnd = random.Random(26)
    for v in body.verts:                                            # a haunch, not a cone: flatter one way, lumpy
        v.co.y *= 0.78
        v.co *= 1 + rnd.uniform(-0.03, 0.03)
    b.add(body, "VK_Goods", uv=("goods", "meat", (0, 0, 1)))
    b.add(tube([Vector((0, 0, 0.15)), Vector((0, 0, 0.22))], 0.011, ring=8, closed=False), "Bone")
    b.add(sphere(0.019, 1.2, 0.9, 0.8), "Bone", Matrix.Translation(Vector((0, 0, 0.225))))   # the knuckle
    b.add(torus(0.025, 0.003, seg=16, ring=4), "Cord", Matrix.Translation(Vector((0, 0, 0.09))) @ Matrix.Scale(0.82, 4, Vector((0, 1, 0))))
    return b.finish(coll)


def mammoth_meat(coll):
    """a slab of mammoth meat: a great block of red meat under a thick cap of fat, a strip of the shaggy brown hide still
    on one side, the round of a big bone with its marrow in the cut face -- heavier than anything a deer gives"""
    b = Builder("mammoth_meat")
    meat = lump(0.5, 27, 0.06, 0.42, 0.28, 0.16, subdiv=3)
    for v in meat.verts:                                            # a squarer block
        v.co.x = math.copysign(min(abs(v.co.x) * 1.15, 0.21), v.co.x)
        v.co.y = math.copysign(min(abs(v.co.y) * 1.15, 0.14), v.co.y)
    b.add(meat, "VK_Goods", uv=("goods", "meat", (0, 0, 1), "plane"))
    fat = lump(0.5, 28, 0.05, 0.4, 0.26, 0.06, subdiv=3)
    b.add(fat, "Fat", Matrix.Translation(Vector((0, 0, 0.075))))
    rnd = random.Random(29)
    for k in range(90):                                             # the hide's shaggy hair over the back edge, hanging down
        x = rnd.uniform(-0.2, 0.2)
        root = Vector((x, rnd.uniform(0.09, 0.125), rnd.uniform(0.07, 0.1)))
        tip = root + Vector((rnd.uniform(-0.02, 0.02), rnd.uniform(0.04, 0.07), rnd.uniform(-0.12, -0.06)))
        mid = root.lerp(tip, 0.4) + Vector((0, 0.02, 0.015))
        b.add(tube([root, mid, tip], rnd.uniform(0.006, 0.009), ring=5, closed=False, taper=lambda t: 1 - 0.8 * t),
              rnd.choice(("WoolBrown", "WoolDark", "WoolDark")))
    face = Matrix.Translation(Vector((0.05, -0.141, 0.0))) @ Matrix.Rotation(math.pi / 2, 4, "X")   # the bone in the cut face
    b.add(cyl(0.04, 0.006, seg=20), "Bone", face, flat=True)
    b.add(cyl(0.024, 0.008, seg=16), "Marrow", face, flat=True)
    return b.finish(coll)


def wolf_meat(coll):
    b = Builder("wolf_meat")
    for k, (x, rz) in enumerate(((-0.025, 0.25), (0.02, -0.2))):    # two lean strips
        b.add(lump(0.5, 30 + k, 0.08, 0.18, 0.05, 0.03, subdiv=3), "VK_Goods",
              Matrix.Translation(Vector((x, 0, k * 0.02))) @ Matrix.Rotation(rz, 4, "Z") @ Matrix.Rotation(1.2, 4, "Z"),
              uv=("goods", "meat", (0, 0, 1), "plane"))
    return b.finish(coll)


def smoked_fish(coll):
    b = Builder("smoked_fish")
    body = sphere(0.1, 1.0, 0.32, 0.4, seg=20, rings=10)            # along x, head to +x
    for v in body.verts:
        t = (v.co.x + 0.1) / 0.2
        k = 0.45 + 0.55 * math.sin(min(1.0, t * 1.15) * math.pi * 0.62)
        v.co.y *= k; v.co.z *= k
    b.add(body, "VK_Goods", uv=("goods", "fish_smoked", (1, 0, 0)))
    tail = bmesh.new()
    vs = [tail.verts.new(p) for p in ((-0.095, 0, 0), (-0.15, 0, 0.045), (-0.14, 0, 0.0), (-0.15, 0, -0.045))]
    tail.faces.new(vs)
    bmesh.ops.solidify(tail, geom=list(tail.faces), thickness=0.004)
    b.add(tail, "VK_Goods", uv=("goods", "fish_smoked", (1, 0, 0)))
    b.add(tube([Vector((0.09, 0, 0.03)), Vector((0.06, 0, 0.07)), Vector((0.02, 0, 0.09))], 0.002, ring=4, closed=False), "Cord")   # hung by a cord
    return b.finish(coll)


def rat_skewer(coll):
    b = Builder("rat_skewer")
    b.add(tube([Vector((-0.13, 0, 0)), Vector((0.13, 0, 0))], 0.004, ring=6, closed=False, taper=lambda t: 1 - 0.7 * t), "VK_Wood")
    for k, x in enumerate((-0.05, 0.0, 0.05)):
        b.add(lump(0.022, 50 + k, 0.2, 1.1, 1.0, 0.9), "VK_Goods", Matrix.Translation(Vector((x, 0, 0))), uv=("goods", "sausage", (1, 0, 0)))
    return b.finish(coll)


# ---- potions (the liquid IT_Tint: the potion's colour in Unity), the antidote's vial

def flask(name, big=False):
    def f(coll):
        b = Builder(name)
        s = 1.25 if big else 1.0
        b.add(lathe([(0.0, 0.0), (0.035, 0.004), (0.05, 0.03), (0.048, 0.06), (0.03, 0.082), (0.0, 0.086)], 24), "Tint", Matrix.Scale(s, 4))
        b.add(lathe([(0.012, 0.078), (0.012, 0.115), (0.016, 0.118), (0.016, 0.124), (0.0, 0.125)], 14), "Glass", Matrix.Scale(s, 4))
        b.add(lathe([(0.0, 0.12), (0.011, 0.12), (0.013, 0.145), (0.0, 0.147)], 12), "Cork", Matrix.Scale(s, 4))
        b.add(torus(0.013, 0.0018, seg=14, ring=4), "Cord", Matrix.Scale(s, 4) @ Matrix.Translation(Vector((0, 0, 0.095))))
        return b.finish(coll)
    return f


def tall_bottle(coll):
    b = Builder("potion_tall")
    b.add(lathe([(0.0, 0.0), (0.03, 0.002), (0.034, 0.02), (0.034, 0.09), (0.024, 0.11), (0.0, 0.112)], 6), "Tint")   # six-sided
    b.add(lathe([(0.01, 0.105), (0.01, 0.14), (0.014, 0.143), (0.014, 0.15), (0.0, 0.151)], 14), "Glass")
    b.add(lathe([(0.0, 0.147), (0.009, 0.147), (0.012, 0.155), (0.016, 0.162), (0.0, 0.17)], 12), "Gold")   # a stopper
    return b.finish(coll)


def vial(coll):
    b = Builder("antidote")
    b.add(lathe([(0.0, 0.0), (0.014, 0.003), (0.016, 0.01), (0.016, 0.075), (0.0, 0.076)], 16), "Tint")
    b.add(lathe([(0.009, 0.072), (0.009, 0.09), (0.012, 0.093), (0.0, 0.094)], 12), "Glass")
    b.add(lathe([(0.0, 0.088), (0.008, 0.088), (0.01, 0.105), (0.0, 0.107)], 10), "Cork")
    return b.finish(coll)


# ---- scrolls (2026-10-22, the user: "Scrolls nexts, we could use several types of scrolls. Lets start working on the
# mesh that will be dropped in game"; the first was one tube for all five). Each lies on the ground as it would when
# dropped (z 0 the ground, its roll along X) at its real size, light enough to lie about: its paper a real spiral sheet,
# so its ends show the roll.

def spiral(cx, cz, r0, r1, turns, end, per_turn=18):
    """points (x, z) of a paper spiral round (cx, cz), r0 inside to r1 outside, ending at angle `end`, wound
    counter-clockwise (seen from -Y) toward its end"""
    n = max(4, int(turns * per_turn))
    out = []
    for i in range(n + 1):
        t = i / n
        a = end - (1 - t) * turns * 2 * math.pi
        r = r0 + (r1 - r0) * t
        out.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return out


def sheet(prof, y0, y1, thick, rag=0.0, seed=0, rows=1, tele=0.0):
    """a paper sheet: the profile prof (x, z) swept along Y from y0 to y1 (numbers, or one a profile point: an uneven
    edge), in rows strips, solidified thick; rag: its two Y edges torn by up to that much; tele: the inner turns pushed
    out along Y by up to that (a roll telescoping)"""
    bm = bmesh.new()
    rnd = random.Random(seed)
    jag = [[rnd.uniform(0, rag) for _ in prof] for _ in (0, 1)]
    grid = []
    for i, (x, z) in enumerate(prof):
        col = []
        sh = tele * (1 - i / (len(prof) - 1)) ** 1.5
        a_ = y0[i] if isinstance(y0, list) else y0
        c_ = y1[i] if isinstance(y1, list) else y1
        for k in range(rows + 1):
            y = a_ + (c_ - a_) * k / rows + sh
            if k == 0:
                y += jag[0][i]
            elif k == rows:
                y -= jag[1][i]
            col.append(bm.verts.new((x, y, z)))
        grid.append(col)
    for i in range(len(prof) - 1):
        for k in range(rows):
            bm.faces.new((grid[i][k], grid[i + 1][k], grid[i + 1][k + 1], grid[i][k + 1]))
    bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=thick)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    return bm


def quad(x, y, z=0.0):
    """a single face, x by y, facing up (a stroke of ink on a page)"""
    bm = bmesh.new()
    bm.faces.new([bm.verts.new((sx * x / 2, sy * y / 2, z)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    return bm


def band(pts, side, w, t, normal=None):
    """a flat strip (a ribbon) along pts, w wide along side, t thick; normal(p): the surface it lies on (its side then
    across the path in that surface)"""
    bm = bmesh.new()
    n = len(pts)
    rows = []
    for i, p in enumerate(pts):
        a, c = pts[max(0, i - 1)], pts[min(n - 1, i + 1)]
        d = (c - a).normalized()
        s = d.cross(normal(p)).normalized() if normal else (Vector(side) - d * d.dot(Vector(side))).normalized()
        up = d.cross(s).normalized()
        rows.append([bm.verts.new(p + s * sx * w / 2 + up * ux * t / 2) for sx, ux in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    for r0, r1 in zip(rows, rows[1:]):
        for j in range(4):
            bm.faces.new((r0[j], r1[j], r1[(j + 1) % 4], r0[(j + 1) % 4]))
    bm.faces.new(list(reversed(rows[0])))
    bm.faces.new(rows[-1])
    return bm


def wax_seal(b, at, r, m="Tint", seed=0, normal=(0, 0, 1)):
    """a blob of wax pressed flat: an uneven disc with a raised ring stamped in it"""
    rot = Vector((0, 0, 1)).rotation_difference(Vector(normal)).to_matrix().to_4x4()
    rnd = random.Random(seed)
    disc = lathe([(0.0, 0.0), (r * 1.05, 0.0), (r, r * 0.3), (r * 0.8, r * 0.38), (0.0, r * 0.36)], 14)
    for v in disc.verts:
        if v.co.xy.length > r * 0.9:
            v.co.xy *= 1 + rnd.uniform(-0.12, 0.12)
    b.add(disc, m, Matrix.Translation(at) @ rot)
    b.add(torus(r * 0.55, r * 0.09, seg=14, ring=4), m, Matrix.Translation(at) @ rot @ Matrix.Translation(Vector((0, 0, r * 0.38))))


def scroll(coll):
    """a sealed scroll: a roll of parchment tied round its middle with a ribbon, a wax seal on the knot, the ribbon's
    two tails trailing -- the ribbon and the seal the scroll's colour"""
    b = Builder("scroll")
    R, L = 0.024, 0.24
    prof = spiral(0, R, 0.007, R, 3.2, -math.pi / 2 + 0.5)
    prof.append((prof[-1][0] + 0.012, 0.0009))                      # the outer edge lying on the ground
    b.add(sheet(prof, -L / 2, L / 2, 0.0012, rows=4, tele=0.008), "VK_Paper", Matrix.Rotation(math.pi / 2, 4, "Z"))
    rr = R + 0.0016
    loop = [Vector((0.0, math.cos(a) * rr, R + math.sin(a) * rr)) for a in [2 * math.pi * k / 28 for k in range(29)]]
    b.add(band(loop, (1, 0, 0), 0.018, 0.0012), "Tint")             # the ribbon round it
    on_roll = lambda p_: Vector((0, p_.y, p_.z - R)).normalized() if p_.z > 0.006 else Vector((0, 0, 1))
    top = Vector((0.0, -0.012, R + math.sqrt(rr * rr - 0.012 ** 2)))
    for s_ in (-1, 1):                                              # the tails, off the knot, over the roll to the ground
        pts = []
        for k in range(9):
            a = math.radians(115 + 70 * k / 8)                      # round the roll's near side...
            pts.append(Vector((s_ * (0.004 + 0.022 * k / 8), math.cos(a) * rr, R + math.sin(a) * rr)))
        for k in range(1, 4):                                       # ...and out over the ground
            pts.append(Vector((s_ * (0.026 + 0.008 * k), -rr - 0.012 * k, 0.0012 + 0.003 * (3 - k) / 3)))
        tail = band(pts, (1, 0, 0), 0.015, 0.0012, normal=on_roll)
        b.add(tail, "Tint")
    wax_seal(b, top + Vector((0, 0.002, 0.001)), 0.017, seed=3, normal=(0, -0.3, 0.95))
    return b.finish(coll)


def scroll_rod(coll):
    """a prayer scroll: the parchment wound on a turned wooden rod, its knobs out at both ends, a cord round it with a
    tassel -- the cord the scroll's colour"""
    b = Builder("scroll_rod")
    R, L, rr = 0.021, 0.2, 0.0055
    prof = spiral(0, R + 0.002, rr + 0.0008, R, 2.6, -math.pi / 2 + 0.3)
    prof.append((prof[-1][0] + 0.01, 0.0009))
    b.add(sheet(prof, -L / 2, L / 2, 0.0012, rows=4, tele=0.004), "VK_Paper", Matrix.Rotation(math.pi / 2, 4, "Z"))
    along = Matrix.Translation(Vector((0, 0, R + 0.002))) @ Matrix.Rotation(math.pi / 2, 4, "Y")
    b.add(cyl(rr, L + 0.02, seg=10), "VK_Wood", along)
    for s_ in (-1, 1):                                              # the turned knobs
        knob = lathe([(0.0, 0.0), (0.008, 0.0), (0.009, 0.004), (0.006, 0.008), (0.011, 0.016), (0.009, 0.024), (0.004, 0.028), (0.0, 0.029)], 12)
        b.add(knob, "Gold", along @ Matrix.Translation(Vector((0, 0, s_ * (L / 2 + 0.01)))) @ Matrix.Rotation(0 if s_ > 0 else math.pi, 4, "X"))
    for x in (-0.03, 0.03):                                         # the cord, round twice
        cr = torus(R + 0.002, 0.0021, seg=20, ring=5)
        b.add(cr, "Tint", along @ Matrix.Translation(Vector((0, 0, x))))
    knot = Vector((0.03, -0.008, 2 * R + 0.001))
    b.add(sphere(0.004, seg=8, rings=6), "Tint", Matrix.Translation(knot))
    tail = [knot, knot + Vector((0.006, -0.01, -0.006)), Vector((0.042, -0.026, R)), Vector((0.05, -0.04, 0.006))]
    b.add(tube(tail, 0.002, ring=5, closed=False), "Tint")
    tip = tail[-1]
    b.add(lathe([(0.0, 0.022), (0.004, 0.019), (0.008, 0.005), (0.009, 0.0), (0.0, 0.0)][::-1], 10), "Tint",
          Matrix.Translation(tip) @ Matrix.Rotation(-math.pi / 2, 4, "X") @ Matrix.Rotation(math.pi, 4, "Z"))   # the tassel
    return b.finish(coll)


def scroll_open(coll):
    """an open scroll: half unrolled, the two rolls at its ends, lines of ink across the sheet between and a ring of
    signs at its heart -- the signs the scroll's colour"""
    b = Builder("scroll_open")
    W, R0, R1, gap = 0.17, 0.016, 0.012, 0.13
    left = spiral(-gap / 2, R0, 0.005, R0, 2.4, -math.pi / 2)
    right = [(-x, z) for x, z in spiral(-gap / 2, R1, 0.005, R1, 1.8, -math.pi / 2)]
    right = [(x + 0.0, z) for x, z in right][::-1]
    mid = [(-gap / 2 + gap * k / 6, 0.0006 + 0.0012 * math.sin(math.pi * k / 6)) for k in range(1, 6)]
    prof = left + mid + right
    b.add(sheet(prof, -W / 2, W / 2, 0.0011, rows=4), "VK_Paper")
    rnd = random.Random(11)
    z = 0.0006 + 0.0012 + 0.0004
    for row in range(-4, 5):                                        # lines of writing, round the sign
        x = row * 0.0118
        y = -W / 2 + 0.014
        while y < W / 2 - 0.014:
            w = rnd.uniform(0.004, 0.016)
            if abs(x) < 0.044 and abs(y) < 0.048:                    # (none over the sign)
                y += w + 0.004
                continue
            zz = 0.0006 + 0.0012 * math.sin(math.pi * (x + gap / 2) / gap) + 0.0009
            b.add(quad(0.0024, w), "Ink", Matrix.Translation(Vector((x, y + w / 2, zz))), flat=True)
            y += w + rnd.uniform(0.0022, 0.0035)
    zc = 0.0006 + 0.0012 + 0.0009
    b.add(torus(0.04, 0.0017, seg=36, ring=4), "Tint", Matrix.Translation(Vector((0, 0, zc))) @ Matrix.Scale(0.5, 4, Vector((0, 0, 1))))
    b.add(torus(0.032, 0.0011, seg=32, ring=4), "Tint", Matrix.Translation(Vector((0, 0, zc))) @ Matrix.Scale(0.5, 4, Vector((0, 0, 1))))
    for k in range(8):                                              # a ward's star: two squares, one turned
        a0, a1 = 2 * math.pi * k / 8, 2 * math.pi * (k + 2) / 8
        p0 = Vector((math.cos(a0) * 0.029, math.sin(a0) * 0.029, zc))
        p1 = Vector((math.cos(a1) * 0.029, math.sin(a1) * 0.029, zc))
        b.add(band([p0, p1], (0, 0, 1), 0.0024, 0.0006, normal=lambda p_: Vector((0, 0, 1))), "Tint", flat=True)
    for k in range(12):                                             # signs round the ring
        a = 2 * math.pi * k / 12
        p = Vector((math.cos(a) * 0.036, math.sin(a) * 0.036, zc))
        b.add(quad(0.0034, 0.0034), "Tint", Matrix.Translation(p) @ Matrix.Rotation(a + 0.6, 4, "Z"), flat=True)
    return b.finish(coll)


def scroll_singed(coll):
    """a singed scroll: rolled, one end burnt away -- its outer turns most, a ragged black edge, a brown scorch running
    unevenly in from the char -- the other end only browned, a wax seal holding it; the seal the scroll's colour"""
    from mathutils import noise
    b = Builder("scroll_singed")
    R, L = 0.022, 0.22
    prof = spiral(0, R, 0.006, R, 3.0, -math.pi / 2 + 0.6, per_turn=22)
    prof.append((prof[-1][0] + 0.014, 0.0009))
    n = len(prof)
    arc = [0.0]
    for (x0, z0), (x1, z1) in zip(prof, prof[1:]):
        arc.append(arc[-1] + math.hypot(x1 - x0, z1 - z0))
    rnd = random.Random(31)
    front, char, scorch, brown = [], [], [], []
    for i in range(n):
        t = i / (n - 1)                                             # 0 inside the roll, 1 its outer turn
        burnt = 0.004 + 0.03 * t ** 1.5 + 0.014 * (noise.noise(Vector((arc[i] * 35, 0.3, 0.7))) + 0.5) + rnd.uniform(0, 0.003)
        front.append(L / 2 - burnt)                                 # the burnt end (+Y), eaten back unevenly
        char.append(front[-1] - 0.006 - 0.008 * (noise.noise(Vector((arc[i] * 25, 2.1, 0.2))) + 0.5))
        scorch.append(char[-1] - 0.01 - 0.014 * (noise.noise(Vector((arc[i] * 18, 4.7, 1.3))) + 0.5))
        brown.append(-L / 2 + 0.004 + 0.007 * (noise.noise(Vector((arc[i] * 30, 7.7, 2.9))) + 0.5))   # the other end browned
    turn = Matrix.Rotation(math.pi / 2, 4, "Z")
    for y0, y1, m in ((-L / 2, brown, "Scorch"), (brown, scorch, "VK_Paper"), (scorch, char, "Scorch"), (char, front, "Char")):
        b.add(sheet(prof, y0, y1, 0.0012, rows=1 if m != "VK_Paper" else 3), m, turn)
    wax_seal(b, Vector((0.012, -0.012, 2 * R - 0.003)), 0.016, seed=5, normal=(0, -0.5, 0.87))
    return b.finish(coll)


# ---- the gathered herbs (2026-10-22, the user: "Make the plants now"; their icons were the kit's whole growing plants,
# the goblin herb and the ghostpipe dim): what the player picks -- a bunch, as the berries are the berries, not the bush.
# Each lies as dropped (z 0 the ground, the bunch along +X from its cut ends), at its real size; the leaves and flowers
# on the kit plant's own sheet (VK_GoblinHerb, VK_WildGarlic, VK_Yarrow, VK_Fireweed: the same look as in the field),
# two-sided cards. Sheets' regions (u0, u1, v0, v1) as the kit maps them (vk_nature GH_UV, WG_UV, YA_UV, FW_UV).
GH_LEAF = ((0.004, 0.496, 0.004, 0.996), (0.504, 0.996, 0.004, 0.996))   # smooth, crinkled
WG = {"leaf": (0.004, 0.496, 0.004, 0.996), "flower": (0.504, 0.996, 0.504, 0.996)}
YA = {"leaf": (0.004, 0.496, 0.004, 0.996), "flower": (0.504, 0.996, 0.504, 0.996)}
FW = {"leaf": (0.004, 0.496, 0.004, 0.996), "spike": (0.504, 0.996, 0.504, 0.996)}


def card_grid(P, uvr, flip=False):
    """a two-sided card over a grid of points P[j][i] (j along, i across), its uvs spread over the sheet's region uvr
    (flip: mirrored across) -- on the part's own UVMap (Builder.add uv="keep")"""
    bm = bmesh.new()
    lay = bm.loops.layers.uv.new("UVMap")
    u0, u1, v0, v1 = uvr
    if flip:
        u0, u1 = u1, u0
    rows, cols = len(P) - 1, len(P[0]) - 1
    vs = [[bm.verts.new(p) for p in row] for row in P]
    for j in range(rows):
        for i in range(cols):
            ids = ((j, i), (j, i + 1), (j + 1, i + 1), (j + 1, i))
            for back in (False, True):
                order = ids[::-1] if back else ids
                f = bm.faces.new([vs[a][b] for a, b in order]) if not back else None
                if back:                                            # (the back: its own verts, so its normals face away)
                    f = bm.faces.new([bm.verts.new(vs[a][b].co) for a, b in order])
                for l, (a, b) in zip(f.loops, order):
                    l[lay].uv = (u0 + (u1 - u0) * b / cols, v0 + (v1 - v0) * a / rows)
    return bm


def lying_leaf(base, az, L, W, rng, uvr, rows=6, e0=(15, 30), e1=(-25, -8), fold=0.12, lift=0.0):
    """a picked leaf from base out along azimuth az, rising a little off the bunch then arching down toward the ground,
    twisting a little, its halves folded up from the midrib; the points of its card (3 across)"""
    a0, a1 = math.radians(rng.uniform(*e0)), math.radians(rng.uniform(*e1))
    roll = rng.uniform(-0.35, 0.35)
    side = Vector((-math.sin(az), math.cos(az), 0.0))
    p = Vector(base)
    P = []
    for j in range(rows + 1):
        t = j / rows
        e = a0 + (a1 - a0) * t ** 1.2
        d = Vector((math.cos(az) * math.cos(e), math.sin(az) * math.cos(e), math.sin(e)))
        s = (Quaternion(d, roll * t) @ side).normalized()
        n = s.cross(d).normalized()
        if n.z < 0:
            n = -n
        w = W * (0.35 + 0.65 * min(1.0, t * 2.2))
        q = Vector((p.x, p.y, max(p.z, 0.0015 + lift)))
        mid = q - n * W * fold * math.sin(math.pi * min(t, 0.9))
        P.append([q - s * w / 2, mid, q + s * w / 2])
        p = p + d * (L / rows)
    return P


def diagonal(b, deg=22):
    """the bunch turned about Z, so the icon's shot from above lays it along the cell's diagonal (a dropped item's
    turn is free anyway)"""
    bmesh.ops.rotate(b.bm, verts=list(b.bm.verts), cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(deg), 3, "Z"))


def stem_bunch(b, n, x0, x1, r, rng, m="StemGreen", z=0.006, spread=0.006):
    """the cut stems of a bunch, side by side along X from x0 to x1 (the bunch's foot)"""
    for i in range(n):
        y, zz = rng.uniform(-spread, spread), z + rng.uniform(-0.002, 0.003)
        b.add(tube([Vector((x0 + rng.uniform(0, 0.006), y, zz)), Vector((x1, y * 0.5, zz + 0.001))], r, ring=6, closed=False), m)


def tie(b, x, R, z=0.007):
    """twine wound round a bunch's stems at x"""
    for k in range(2):
        b.add(torus(R, 0.0013, seg=14, ring=4), "Cord", Matrix.Translation(Vector((x + k * 0.0032, 0, z))) @ Matrix.Rotation(math.pi / 2, 4, "Y"))


def goblin_herb(coll):
    """a bunch of goblin herb: long olive strap leaves, some crinkled and blotched, fanning out from their cut stems,
    tied with twine"""
    b = Builder("goblin_herb")
    rng = random.Random(41)
    stem_bunch(b, 7, -0.05, 0.012, 0.0028, rng)
    tie(b, -0.02, 0.009)
    for i in range(7):
        az = math.radians(-34 + 68 * i / 6 + rng.uniform(-5, 5))
        L = rng.uniform(0.2, 0.27)
        base = Vector((0.008, rng.uniform(-0.004, 0.004), 0.006 + 0.0012 * i))
        b.add(card_grid(lying_leaf(base, az, L, L * 0.34, rng, None, rows=7), GH_LEAF[rng.random() < 0.4], rng.random() < 0.5),
              "VK_GoblinHerb", uv="keep")
    diagonal(b)
    return b.finish(coll)


def wild_garlic(coll):
    """a bunch of wild garlic: broad leaves from their cut stalks, two flower stalks among them with loose heads of
    white stars, tied with twine"""
    b = Builder("wild_garlic")
    rng = random.Random(43)
    stem_bunch(b, 6, -0.04, 0.01, 0.0026, rng)
    tie(b, -0.015, 0.008)
    for i in range(5):
        az = math.radians(-30 + 60 * i / 4 + rng.uniform(-6, 6))
        L = rng.uniform(0.17, 0.22)
        base = Vector((0.006, rng.uniform(-0.004, 0.004), 0.006 + 0.0012 * i))
        b.add(card_grid(lying_leaf(base, az, L, L * 0.38, rng, None), WG["leaf"], rng.random() < 0.5), "VK_WildGarlic", uv="keep")
    for s_ in (-1, 0, 1):                                           # three flower stalks, their heads past the leaf tips
        az = math.radians(s_ * 15)
        reach = 0.24 - 0.02 * abs(s_)
        top = Vector((0.006 + math.cos(az) * reach, math.sin(az) * reach, 0.018))
        b.add(tube([Vector((-0.04, s_ * 0.002, 0.009)), Vector((0.08, s_ * 0.008, 0.015)), top], 0.0018, ring=5, closed=False), "StemGreen")
        for k in range(13):                                         # the head: star flowers round the stalk's top
            th = math.radians(rng.uniform(0, 70)) if k else 0.0
            ph = k * 2.39996 + rng.uniform(-0.3, 0.3)
            fwd = Vector((math.cos(az) * 0.5, math.sin(az) * 0.5 - 0.6, 1.0)).normalized()    # (up and to the icon's camera)
            ref = fwd.cross(Vector((0, 0, 1))).normalized()
            up = ref.cross(fwd).normalized()
            d = (fwd * math.cos(th) + (ref * math.cos(ph) + up * math.sin(ph)) * math.sin(th)).normalized()
            if d.z < -0.2:
                d = (d + Vector((0, 0, 0.6))).normalized()
            c = top + d * 0.027
            r = d.cross(Vector((1, 0, 0)) if abs(d.x) < 0.9 else Vector((0, 1, 0))).normalized()
            u = d.cross(r)
            sz = 0.03 * rng.uniform(0.85, 1.1)
            b.add(card_grid([[c - r * sz / 2 - u * sz / 2, c + r * sz / 2 - u * sz / 2], [c - r * sz / 2 + u * sz / 2, c + r * sz / 2 + u * sz / 2]],
                            WG["flower"]), "VK_WildGarlic", uv="keep")
    diagonal(b)
    return b.finish(coll)


def flat_head(b, top, r, m, uvr, rng, normal=(0, 0, 1), n=10):
    """a flat flower head (yarrow's): a shallow dome, centre and two rings, the sheet's round head mapped on it"""
    T, tilt = Vector(top), Vector(normal).normalized()
    u0, u1, v0, v1 = uvr
    uc, vc, ur, vr = (u0 + u1) / 2, (v0 + v1) / 2, (u1 - u0) / 2, (v1 - v0) / 2
    a_ = tilt.cross(Vector((1, 0, 0)) if abs(tilt.x) < 0.9 else Vector((0, 1, 0))).normalized()
    b_ = tilt.cross(a_)
    rot = rng.uniform(0, 6.28)
    bm = bmesh.new()
    lay = bm.loops.layers.uv.new("UVMap")
    ctr = bm.verts.new(T + tilt * r * 0.18)
    rings = []
    for rf, dz in ((0.55, 0.1), (1.0, -0.12)):
        rings.append([(bm.verts.new(T + (a_ * math.cos(rot + 2 * math.pi * i / n) + b_ * math.sin(rot + 2 * math.pi * i / n)) * r * rf * rng.uniform(0.92, 1.06)
                                    + tilt * r * dz), 2 * math.pi * i / n, rf * 0.98) for i in range(n)])
    uv = lambda th, rf: (uc + math.cos(th) * rf * ur, vc + math.sin(th) * rf * vr)
    for i in range(n):
        j = (i + 1) % n
        (va, ta, fa), (vb, tb, fb) = rings[0][i], rings[0][j]
        f = bm.faces.new((ctr, va, vb))
        for l, q in zip(f.loops, ((uc, vc), uv(ta, fa), uv(ta + 2 * math.pi / n, fb))):
            l[lay].uv = q
        (wa, sa, ga), (wb, sb, gb) = rings[1][i], rings[1][j]
        f = bm.faces.new((va, wa, wb, vb))
        for l, q in zip(f.loops, (uv(ta, fa), uv(sa, ga), uv(sa + 2 * math.pi / n, gb), uv(ta + 2 * math.pi / n, fb))):
            l[lay].uv = q
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    if sum((f.normal.dot(tilt) for f in bm.faces)) < 0:
        bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
    b.add(bm, m, uv="keep")


def yarrow(coll):
    """a bunch of yarrow: stiff stalks, each topped with its flat head of white florets, feathery leaves at their feet,
    tied with twine"""
    b = Builder("yarrow")
    rng = random.Random(47)
    tie(b, -0.03, 0.008)
    for i in range(4):
        az = math.radians(-36 + 72 * i / 3 + rng.uniform(-3, 3))
        foot = Vector((-0.06, rng.uniform(-0.003, 0.003), 0.006 + 0.001 * i))
        reach = (0.2, 0.17, 0.21, 0.18)[i]                          # (staggered, so the heads don't hide each other)
        top = Vector((0.0 + math.cos(az) * reach, math.sin(az) * reach, 0.024 + rng.uniform(0, 0.01)))
        mid = foot.lerp(top, 0.5) + Vector((0, 0, 0.006))
        b.add(tube([foot, mid, top], 0.0021, ring=5, closed=False), "StemGreen")
        flat_head(b, top + Vector((0.004, 0, 0.004)), rng.uniform(0.042, 0.048), "VK_Yarrow", YA["flower"], rng,
                  normal=(0.15, -0.8, 1))                           # (toward the icon's camera: Blender's front, above)
    for i in range(5):                                              # feathery leaves along the stalks
        az = math.radians(-40 + 80 * i / 4 + rng.uniform(-6, 6))
        L = rng.uniform(0.08, 0.11)
        base = Vector((-0.005 + rng.uniform(0, 0.03), rng.uniform(-0.006, 0.006), 0.009 + 0.001 * i))
        b.add(card_grid(lying_leaf(base, az, L, L * 0.36, rng, None, rows=4), YA["leaf"], rng.random() < 0.5), "VK_Yarrow", uv="keep")
    diagonal(b)
    return b.finish(coll)


def fireweed(coll):
    """a bunch of fireweed: three cut stems, narrow leaves up them, each topped by its spike of magenta flowers, tied
    with twine"""
    b = Builder("fireweed")
    rng = random.Random(53)
    tie(b, -0.05, 0.008)
    for i in range(3):
        az = math.radians(-12 + 12 * i + rng.uniform(-3, 3))
        foot = Vector((-0.08, rng.uniform(-0.003, 0.003), 0.006 + 0.0015 * i))
        d = Vector((math.cos(az), math.sin(az), 0.0))
        spk0 = Vector((0.07, 0, 0)) + d * 0.0 + Vector((0, math.sin(az) * 0.15, 0.012))
        spk0 = foot + d * 0.15 + Vector((0, 0, 0.008))
        tip = spk0 + d * 0.11 + Vector((0, 0, 0.012))
        b.add(tube([foot, foot.lerp(spk0, 0.5) + Vector((0, 0, 0.003)), spk0], 0.0024, ring=5, closed=False), "StemGreen")
        q0 = rng.uniform(0, math.pi)
        for m in range(3):                                          # the spike: three crossed cards round its axis
            ax = (tip - spk0).normalized()
            ref = ax.cross(Vector((0, 0, 1))).normalized()
            up = ref.cross(ax)
            s = (ref * math.cos(q0 + m * math.pi / 3) + up * math.sin(q0 + m * math.pi / 3)) * 0.017
            b.add(card_grid([[spk0 - s, spk0 + s], [spk0.lerp(tip, 0.5) - s, spk0.lerp(tip, 0.5) + s], [tip - s * 0.8, tip + s * 0.8]],
                            FW["spike"], rng.random() < 0.5), "VK_Fireweed", uv="keep")
        for j in range(4):                                          # narrow leaves up the stem
            t = 0.25 + 0.6 * j / 4
            p = foot.lerp(spk0, t) + Vector((0, 0, 0.002))
            L = rng.uniform(0.06, 0.08)
            b.add(card_grid(lying_leaf(p, az + (0.9 if j % 2 else -0.9) + rng.uniform(-0.2, 0.2), L, L * 0.3, rng, None, rows=3,
                                       e0=(5, 15), e1=(-15, -5)), FW["leaf"], rng.random() < 0.5), "VK_Fireweed", uv="keep")
    diagonal(b)
    return b.finish(coll)


def ghostpipe(coll):
    """a few picked ghostpipe stems: waxy white, each curling over at its end like a shepherd's crook into a nodding
    bell that faces back down the stem, the bells' rims darkening as they do once picked"""
    b = Builder("ghostpipe")
    rng = random.Random(59)
    for i in range(5):
        az = math.radians(-14 + 7 * i + rng.uniform(-3, 3))
        d = Vector((math.cos(az), math.sin(az), 0.0))
        side = Vector((-d.y, d.x, 0.0)) * (1 if i % 2 else -1)
        foot = Vector((-0.07, -0.008 + 0.004 * i, 0.0045 + 0.002 * (i % 2)))
        L = rng.uniform(0.09, 0.12)
        bend = foot + d * L
        w = (Vector((0, 0, 1)) * 0.65 + side * 0.76).normalized()  # the crook curls up and to one side
        R = rng.uniform(0.011, 0.014)
        c = bend + w * R
        arc = [c - w * R * math.cos(t) + d * R * math.sin(t) for t in [math.radians(160) * k / 6 for k in range(7)]]
        r = rng.uniform(0.0036, 0.0042)
        b.add(tube([foot, foot.lerp(bend, 0.5) + Vector((0, 0, 0.002))] + arc, r, ring=7, closed=False,
                   taper=lambda t: 1.0 - 0.2 * t), "Ghost")
        t_ = math.radians(160)
        axis = (d * math.cos(t_) + w * math.sin(t_)).normalized()  # the bell's way: back along the stem
        rot = axis.to_track_quat("Z", "Y").to_matrix().to_4x4()
        at = arc[-1] - axis * 0.002
        bell = lathe([(0.0, -0.001), (r * 1.15, 0.0), (r * 2.4, 0.01), (r * 3.2, 0.021), (r * 3.0, 0.026), (r * 2.2, 0.0265)], 10)
        b.add(bell, "Ghost", Matrix.Translation(at) @ rot)
        b.add(torus(r * 3.05, r * 0.32, seg=10, ring=4), "GhostTip", Matrix.Translation(at + axis * 0.0262) @ rot)
        for k in range(3):                                          # small scale leaves pressed to the stem
            p = foot.lerp(bend, 0.2 + 0.25 * k)
            b.add(sphere(r * 1.15, 1.0, 0.7, 2.2, seg=6, rings=4), "Ghost",
                  Matrix.Translation(p + Vector((0, 0, r * 0.4))) @ d.to_track_quat("Z", "Y").to_matrix().to_4x4())
    diagonal(b)
    return b.finish(coll)


def cotton(coll):
    """a sprig of wild cotton: a dry brown twig, three open bolls on it -- white puffs bursting from their split,
    pointed brown husks"""
    b = Builder("cotton")
    rng = random.Random(61)
    twig = [Vector((-0.07, 0, 0.004)), Vector((-0.02, 0.004, 0.006)), Vector((0.03, -0.004, 0.007)), Vector((0.07, 0.002, 0.008))]
    b.add(tube(twig, 0.0025, ring=6, closed=False, taper=lambda t: 1 - 0.4 * t), "Stem")
    for at, out, rr in ((Vector((0.08, 0.004, 0.026)), Vector((1, 0.1, 0.3)), 0.026), (Vector((0.0, 0.036, 0.024)), Vector((0.1, 1, 0.3)), 0.023),
                        (Vector((-0.03, -0.034, 0.022)), Vector((-0.2, -1, 0.3)), 0.022)):
        o = out.normalized()
        root = at - o * rr * 0.9
        b.add(tube([twig[1] if at.x < 0.05 else twig[3], root], 0.0018, ring=5, closed=False), "Stem")
        rot = o.to_track_quat("Z", "Y").to_matrix().to_4x4()
        for k in range(4):                                          # the husk: four pointed bracts cupping the boll
            a = 2 * math.pi * k / 4 + rng.uniform(-0.2, 0.2)
            pts = [Vector((0, 0, 0)), Vector((math.cos(a) * rr * 0.6, math.sin(a) * rr * 0.6, rr * 0.2)),
                   Vector((math.cos(a) * rr * 1.05, math.sin(a) * rr * 1.05, rr * 0.42)), Vector((math.cos(a) * rr * 1.4, math.sin(a) * rr * 1.4, rr * 0.5))]
            b.add(band(pts, (-math.sin(a), math.cos(a), 0), rr * 0.7, 0.0012), "Husk", Matrix.Translation(root) @ rot)
        for k in range(4):                                          # the white lobes bursting out
            a = 2 * math.pi * (k + 0.5) / 4
            c = Vector((math.cos(a) * rr * 0.42, math.sin(a) * rr * 0.42, rr * 0.75))
            lobe = lump(rr * 0.62, 70 + k, 0.25, 1.0, 1.0, 1.1, subdiv=2)
            b.add(lobe, "Cotton", Matrix.Translation(root) @ rot @ Matrix.Translation(c))
    diagonal(b)
    return b.finish(coll)


# ---- arrows (2026-10-22, the user: "ok, back to the items"; the arrows and the arrows of cold were one arrow, the
# weapon kit's, a thin line in the cell and the same for both): a sheaf of five, crossed at the cord that ties them
# round their middle (both ends fanned), built heads up (+Z) and turned heads to +Y at the end (the weapon kit's
# arrows' way: the long pose then puts the nocks to the lower left), the fan across X (to the camera). The cold ones rimed: pale heads furred with
# frost crystals, the shafts frosted below them, the fletching gone icy.

def broadhead(L=0.05, W=0.024, T=0.004):
    """a leaf-shaped arrowhead along +Z from its socket at 0: a flat diamond, its edges thin"""
    bm = bmesh.new()
    prof = [(0.0, 0.0), (0.45 * W, 0.35 * L), (0.5 * W, 0.45 * L), (0.0, L)]
    pts = [(0.0, 0.0)] + [(w, z) for w, z in prof[1:-1]] + [(0.0, L)] + [(-w, z) for w, z in prof[1:-1][::-1]]
    front = [bm.verts.new((x, -T / 2 * (1 if abs(x) < 1e-6 else 0.25), z)) for x, z in pts]
    back = [bm.verts.new((x, T / 2 * (1 if abs(x) < 1e-6 else 0.25), z)) for x, z in pts]
    mid_f = bm.verts.new((0, -T / 2, L * 0.4))
    mid_b = bm.verts.new((0, T / 2, L * 0.4))
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((front[i], front[j], mid_f))
        bm.faces.new((back[j], back[i], mid_b))
        bm.faces.new((front[j], front[i], back[i], back[j]))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    return bm


def vane(L=0.09, H=0.012, t=0.0008):
    """a fletching vane: low at the front, rising to a rounded back, cut square at the nock end (a thin solid, in XZ)"""
    pts = [(0.0, L), (H * 0.25, L * 0.92), (H * 0.6, L * 0.7), (H * 0.9, L * 0.4), (H, L * 0.12), (H, 0.0), (0.0, 0.0)]
    bm = bmesh.new()
    f = bm.faces.new([bm.verts.new((x, 0.0, z)) for x, z in pts])
    bmesh.ops.solidify(bm, geom=[f], thickness=t)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    return bm


def one_arrow(b, M, cold, rng, red=True):
    """an arrow along +Z under M, its nock at 0: an ash shaft, a broadhead, three vanes (the cock feather red), a nock"""
    L = 0.76
    b.add(cyl(0.0042, L - 0.03, seg=6), "Ash", M @ Matrix.Translation(Vector((0, 0, (L - 0.03) / 2))))
    b.add(cone(0.0055, 0.0042, 0.02, seg=6), "Steel" if not cold else "Rime", M @ Matrix.Translation(Vector((0, 0, L - 0.035))))
    b.add(broadhead(), "Steel" if not cold else "Rime", M @ Matrix.Translation(Vector((0, 0, L - 0.027))))
    b.add(cyl(0.005, 0.012, seg=6), "Horn", M @ Matrix.Translation(Vector((0, 0, 0.006))))   # the nock
    for k in range(3):
        m = ("FletchIce" if cold else "FletchRed") if (k == 0 and red) else ("FletchIce" if cold else "Fletch")
        b.add(vane(), m, M @ Matrix.Translation(Vector((0, 0, 0.025))) @ Matrix.Rotation(k * 2 * math.pi / 3 + 0.3, 4, "Z")
              @ Matrix.Translation(Vector((0.0042, 0, 0))))
    if cold:                                                        # frost: a rimed sleeve below the head, crystals on it
        sleeve = lump(0.0075, int(rng.random() * 1000), 0.35, 1.0, 1.0, 9.0, subdiv=2)
        b.add(sleeve, "Frost", M @ Matrix.Translation(Vector((0, 0, L - 0.085))))
        for k in range(7):
            a = rng.uniform(0, 2 * math.pi)
            z = L - rng.uniform(0.0, 0.11)
            p = Vector((math.cos(a) * 0.006, math.sin(a) * 0.006, z))
            d = Vector((math.cos(a), math.sin(a), rng.uniform(-0.2, 0.6))).normalized()
            rot = d.to_track_quat("Z", "Y").to_matrix().to_4x4()
            b.add(cone(0.0026, 0.0, rng.uniform(0.008, 0.014), seg=4), "Frost", M @ Matrix.Translation(p) @ rot, flat=True)


def sheaf(name, cold):
    def f(coll):
        b = Builder(name)
        rng = random.Random(71 if cold else 73)
        tie_z = 0.4
        for i in range(5):
            a = math.radians(-5.0 + 2.5 * i + rng.uniform(-0.5, 0.5))
            y = (-1) ** i * 0.0045 + rng.uniform(-0.001, 0.001)     # (side by side at the cord, crossing there)
            M = Matrix.Translation(Vector(((i - 2) * 0.003, y, tie_z))) @ Matrix.Rotation(a, 4, "Y") @ Matrix.Translation(Vector((0, 0, -tie_z))) \
                @ Matrix.Rotation(rng.uniform(0, 6.28), 4, "Z")
            one_arrow(b, M, cold, rng)
        for k in range(3):                                          # the cord round the sheaf
            cr = torus(0.0135, 0.0017, seg=18, ring=4)
            bmesh.ops.scale(cr, vec=Vector((1.0, 0.85, 1.0)), verts=cr.verts)
            b.add(cr, "Cord", Matrix.Translation(Vector((0, 0, tie_z - 0.004 + 0.004 * k))))
        bmesh.ops.rotate(b.bm, verts=list(b.bm.verts), cent=(0, 0, 0), matrix=Matrix.Rotation(-math.pi / 2, 3, "X"))   # heads to +Y, the weapon kit's way
        return b.finish(coll)
    return f


def one_bolt(b, M):
    """a crossbow bolt along +Z under M, its butt at 0: a short thick oak shaft (darker than the arrows' ash), an iron bodkin (four-sided, heavy), two
    leather vanes crossed at the back"""
    L = 0.33
    b.add(cyl(0.0058, L - 0.03, seg=6), "Oak", M @ Matrix.Translation(Vector((0, 0, (L - 0.03) / 2))))
    b.add(cone(0.0078, 0.0058, 0.016, seg=4), "IronTrim", M @ Matrix.Translation(Vector((0, 0, L - 0.036))) @ Matrix.Rotation(math.pi / 4, 4, "Z"))
    b.add(cone(0.0095, 0.0, 0.05, seg=4), "IronTrim", M @ Matrix.Translation(Vector((0, 0, L - 0.004))) @ Matrix.Rotation(math.pi / 4, 4, "Z"))
    for k in range(2):
        b.add(vane(0.055, 0.013, 0.0014), "Leather", M @ Matrix.Translation(Vector((0, 0, 0.012))) @ Matrix.Rotation(k * math.pi / 2 + 0.4, 4, "Z")
              @ Matrix.Translation(Vector((0.0056, 0, 0))))
        b.add(vane(0.055, 0.013, 0.0014), "Leather", M @ Matrix.Translation(Vector((0, 0, 0.012))) @ Matrix.Rotation(k * math.pi / 2 + 0.4 + math.pi, 4, "Z")
              @ Matrix.Translation(Vector((0.0056, 0, 0))))


def bolts(coll):
    """a bundle of crossbow bolts (2026-10-22, the user: "Do the bolts next, as a bundle like the arrows"; it was the
    weapon kit's single bolt): six, crossed at the cord round their middle, two leather vanes each; turned heads to +Y
    as the arrows"""
    b = Builder("bolts")
    rng = random.Random(79)
    tie_z = 0.165
    for i in range(6):
        a = math.radians(-7.5 + 3.0 * i + rng.uniform(-0.5, 0.5))
        y = (-1) ** i * 0.006 + rng.uniform(-0.001, 0.001)
        M = Matrix.Translation(Vector(((i - 2.5) * 0.004, y, tie_z))) @ Matrix.Rotation(a, 4, "Y") @ Matrix.Translation(Vector((0, 0, -tie_z)))             @ Matrix.Rotation(rng.uniform(0, 6.28), 4, "Z")
        one_bolt(b, M)
    for k in range(3):                                              # the cord round the bundle
        cr = torus(0.0175, 0.0019, seg=18, ring=4)
        bmesh.ops.scale(cr, vec=Vector((1.0, 0.85, 1.0)), verts=cr.verts)
        b.add(cr, "Cord", Matrix.Translation(Vector((0, 0, tie_z - 0.0045 + 0.0045 * k))))
    bmesh.ops.rotate(b.bm, verts=list(b.bm.verts), cent=(0, 0, 0), matrix=Matrix.Rotation(-math.pi / 2, 3, "X"))
    return b.finish(coll)


# ---- bags

def cloth_sack(coll):
    b = Builder("cloth_sack")
    body = lathe([(0.0, 0.0), (0.09, 0.01), (0.12, 0.07), (0.115, 0.14), (0.07, 0.2), (0.03, 0.22), (0.035, 0.24), (0.06, 0.27), (0.0, 0.265)], 20)
    rnd = random.Random(5)
    for v in body.verts:
        v.co.x *= 1 + rnd.uniform(-0.05, 0.05); v.co.y *= 1 + rnd.uniform(-0.05, 0.05)
    b.add(body, "VK_Burlap")
    b.add(torus(0.032, 0.005, seg=16, ring=5), "Cord", Matrix.Translation(Vector((0, 0, 0.222))))
    return b.finish(coll)


def rbox(x, y, z, r, seg=3):
    """a box with its edges rounded (r: the round's radius)"""
    bm = box(x, y, z)
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=r, segments=seg, profile=0.5, affect="EDGES")
    return bm


def plate(w, h, t, r, seg=6):
    """a flat plate in the XZ plane (t thick along Y), its top edge straight at z 0, its bottom corners rounded by r:
    a flap hanging down"""
    pts = [Vector((-w / 2, 0, 0)), Vector((w / 2, 0, 0))]
    for cx, a0 in ((w / 2 - r, 0.0), (-w / 2 + r, -math.pi / 2)):
        for k in range(seg + 1):
            a = a0 - math.pi / 2 * k / seg
            pts.append(Vector((cx + r * math.cos(a), 0, -h + r + r * math.sin(a))))
    bm = bmesh.new()
    f = bm.faces.new([bm.verts.new(p_) for p_ in pts])
    bmesh.ops.solidify(bm, geom=[f], thickness=t)
    return bm


def buckle(b, at, w=0.03, h=0.024):
    """a buckle's frame on a strap (its face to -Y)"""
    for dx, dz, sx, sz in ((-w / 2, 0, 0.004, h), (w / 2, 0, 0.004, h), (0, h / 2, w, 0.004), (0, -h / 2, w, 0.004)):
        b.add(box(sx, 0.005, sz), "Gold", Matrix.Translation(at + Vector((dx, 0, dz))))
    b.add(box(0.003, 0.006, h * 0.9), "Gold", Matrix.Translation(at + Vector((0, -0.002, 0))) @ Matrix.Rotation(0.15, 4, "Y"))   # its tongue


def leather_backpack(coll):
    """an adventurer's rucksack (2026-10-22, the user: "Improve the leather backpack"; the lumpy first one read as a
    face): a rounded leather body, the top flap over its shoulders and down its front, two straps buckled to the body,
    a pocket with its own flap and buckle, a wool bedroll strapped on top, the shoulder straps behind"""
    b = Builder("leather_backpack")
    W, D, H = 0.34, 0.2, 0.42                                       # the body; its front to -Y, standing on z 0
    body = rbox(W, D, H, 0.045)
    for v in body.verts:                                            # a little fuller at the bottom, slumped at the top
        t = v.co.z / H + 0.5
        v.co.x *= 1.04 - 0.08 * t
        v.co.y *= 1.08 - 0.12 * t
    b.add(body, "LeatherCured", Matrix.Translation(Vector((0, 0, H / 2))))
    top, front = H + 0.008, -D / 2 - 0.012                          # the flap over the top and down the front
    b.add(rbox(W + 0.02, D + 0.02, 0.014, 0.006), "Leather", Matrix.Translation(Vector((0, -0.004, top))))
    b.add(plate(W + 0.02, 0.17, 0.012, 0.06), "Leather", Matrix.Translation(Vector((0, front, top + 0.004))), flat=True)
    b.add(tube([Vector((-(W + 0.02) / 2, front + 0.004, top - 0.002)), Vector(((W + 0.02) / 2, front + 0.004, top - 0.002))],
               0.012, ring=10, closed=False), "Leather")            # its rolled front edge over the top
    for x in (-0.085, 0.085):                                       # the flap's two straps down to their buckles on the body
        b.add(box(0.03, 0.006, 0.2), "Leather", Matrix.Translation(Vector((x, front - 0.008, top - 0.12))))
        buckle(b, Vector((x, front - 0.013, top - 0.205)))
        b.add(box(0.03, 0.005, 0.07), "Leather", Matrix.Translation(Vector((x, -D / 2 - 0.006, top - 0.25))))   # the body's strap end
    pz = 0.12                                                       # the front pocket, its flap and buckle
    b.add(rbox(0.24, 0.07, 0.15, 0.025), "LeatherCured", Matrix.Translation(Vector((0, -D / 2 - 0.02, pz))))
    b.add(plate(0.25, 0.07, 0.01, 0.03), "Leather", Matrix.Translation(Vector((0, -D / 2 - 0.058, pz + 0.075))), flat=True)
    b.add(box(0.026, 0.005, 0.06), "Leather", Matrix.Translation(Vector((0, -D / 2 - 0.064, pz - 0.01))))
    buckle(b, Vector((0, -D / 2 - 0.068, pz - 0.0)), 0.026, 0.02)
    roll_z = top + 0.007 + 0.06                                     # the bedroll on top, wool, tied with two thongs
    b.add(tube([Vector((-0.22, 0.01, roll_z)), Vector((0.22, 0.01, roll_z))], 0.06, ring=16, closed=False), "Wool")
    for x in (-0.22, 0.22):                                         # its rolled ends
        for r_ in (0.045, 0.028):
            b.add(torus(r_, 0.007, seg=16, ring=5), "Wool", Matrix.Translation(Vector((x, 0.01, roll_z))) @ Matrix.Rotation(math.pi / 2, 4, "Y"))
    for x in (-0.12, 0.12):
        b.add(torus(0.062, 0.006, seg=18, ring=5), "Leather", Matrix.Translation(Vector((x, 0.01, roll_z))) @ Matrix.Rotation(math.pi / 2, 4, "Y"))
    for x in (-0.09, 0.09):                                         # the shoulder straps, behind
        b.add(tube([Vector((x, D / 2 - 0.01, top - 0.02)), Vector((x, D / 2 + 0.06, top - 0.12)), Vector((x, D / 2 + 0.07, 0.2)),
                    Vector((x * 1.2, D / 2 + 0.03, 0.05))], 0.014, ring=6, closed=False), "Leather")
    return b.finish(coll)


# ---- loot

def cage_key(coll):
    b = Builder("cage_key")
    b.add(torus(0.022, 0.005, seg=18, ring=6), "VK_Iron", Matrix.Rotation(math.pi / 2, 4, "X") @ Matrix.Translation(Vector((-0.07, 0, 0))))
    b.add(tube([Vector((-0.048, 0, 0)), Vector((0.07, 0, 0))], 0.0045, ring=8, closed=False), "VK_Iron")
    b.add(box(0.012, 0.006, 0.026), "VK_Iron", Matrix.Translation(Vector((0.062, 0, -0.016))))
    b.add(box(0.006, 0.006, 0.014), "VK_Iron", Matrix.Translation(Vector((0.048, 0, -0.012))))
    return b.finish(coll)


def chitin_plate(coll):
    """a chitin plate (2026-10-22, the user: "Chitin plate"; the first was a plain black oval): a piece of a giant
    crawler's back -- three curved plates overlapping like roof tiles, a keel ridge down the middle, amber-brown edges,
    two short spines off the rear plate; glossy and dark"""
    b = Builder("chitin_plate")
    R, sweep, L = 0.11, math.radians(150), 0.11                     # a plate: part of a shell round X, L long
    for k in range(3):
        bm = bmesh.new()
        nu, nv = 6, 14
        rows = []
        for i in range(nu + 1):
            u = i / nu
            x = -L / 2 + L * u
            sc = 1.0 - 0.12 * k - 0.05 * u                          # each plate a little narrower, tapering back
            row = []
            for j in range(nv + 1):
                a = -sweep / 2 + sweep * j / nv
                bulge = 1 + 0.06 * math.sin(u * math.pi)            # domed along its length
                row.append(bm.verts.new((x, math.sin(a) * R * sc * bulge, (math.cos(a) - 1) * R * sc * bulge)))
            rows.append(row)
        for i in range(nu):
            for j in range(nv):
                bm.faces.new((rows[i][j], rows[i][j + 1], rows[i + 1][j + 1], rows[i + 1][j]))
        bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=0.006)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        place = Matrix.Translation(Vector((k * 0.085, 0, -0.012 * k))) @ Matrix.Rotation(0.12, 4, "Y")   # overlapping, each lower
        b.add(bm, "Chitin", place)
        sc = 1.0 - 0.12 * k - 0.05                                  # its rear rim, amber, over the next plate
        edge = [Vector((L / 2, math.sin(a) * R * sc, (math.cos(a) - 1) * R * sc)) for a in [-sweep / 2 + sweep * j / 20 for j in range(21)]]
        b.add(tube(edge, 0.004, ring=5, closed=False), "ChitinEdge", place)
        b.add(tube([Vector((-L / 2, 0, 0.003)), Vector((L / 2, 0, 0.004))], 0.006 - 0.001 * k, ring=6, closed=False), "Chitin", place)   # the keel
    rear = Matrix.Translation(Vector((2 * 0.085, 0, -0.024))) @ Matrix.Rotation(0.12, 4, "Y")
    for sy in (-1, 1):                                              # two spines off the rear plate
        base = Vector((L * 0.25, sy * R * 0.55, -R * 0.2))
        b.add(tube([base, base + Vector((0.05, sy * 0.025, 0.02))], 0.007, ring=6, closed=False, taper=lambda t: 1 - 0.9 * t), "ChitinEdge", rear)
    return b.finish(coll)


def ring(name, metal, bezel):
    def f(coll):
        b = Builder(name)
        b.add(torus(0.011, 0.0025, seg=24, ring=8), metal, Matrix.Rotation(math.pi / 2, 4, "X"))
        if bezel:
            b.add(cyl(0.007, 0.004, seg=18), metal, Matrix.Translation(Vector((0, 0, 0.0125))))
            b.add(cyl(0.0055, 0.0015, seg=18), "Cord", Matrix.Translation(Vector((0, 0, 0.0145))))   # the seal's cut face
        return b.finish(coll)
    return f


def keeper_whistle(coll):
    b = Builder("keeper_whistle")
    b.add(tube([Vector((-0.04, 0, 0)), Vector((0.04, 0, 0))], 0.008, ring=10, closed=False, taper=lambda t: 1 - 0.25 * t), "Bone")
    b.add(box(0.008, 0.012, 0.006), "Cord", Matrix.Translation(Vector((-0.015, 0, 0.007))))
    b.add(torus(0.006, 0.0015, seg=10, ring=4), "Cord", Matrix.Translation(Vector((0.045, 0, 0))) @ Matrix.Rotation(math.pi / 2, 4, "X"))
    return b.finish(coll)


def tusk(name, ln, base, bend, m="Ivory"):
    def f(coll):
        b = Builder(name)
        b.add(horn(ln, base, bend, seg=14, ring=10), m)
        return b.finish(coll)
    return f


def tusk_path(pts, r0, r1, root_share, body, root, ring=12, bands=0, point=0.2):
    """a tusk along a path: r0 at the root narrowing to r1, then closing to a point over the last share of it (2026-10-22,
    the user: "Dont the tusks have points, though?" -- they ended cut off); its root (the first share) in the root's
    colour, a few growth bands round it there. The path is sampled finely so the point stays round."""
    dense = [pts[0]]                                                # (finer steps, finest toward the tip)
    for a, c in zip(pts, pts[1:]):
        for j in range(1, 5):
            dense.append(a.lerp(c, j / 4))
    pts = dense
    n = len(pts)
    body_end = 1.0 - point

    def rad(T):                                                     # the radius at a share T of the length
        if T <= body_end:
            return r0 + (r1 - r0) * (T / body_end)
        u = (T - body_end) / point                                  # the point: a rounded close, sharp at the end
        return max(r1 * 0.02, r1 * math.sqrt(max(0.0, 1 - u * u)) * (1 - 0.35 * u))

    k = max(2, int(n * root_share))
    b_ = []
    b_.append((tube(pts[:k + 1], r0, ring=ring, closed=False, taper=lambda t: rad(t * k / (n - 1)) / r0), root))
    b_.append((tube(pts[k:], r0, ring=ring, closed=False, taper=lambda t: rad((k + t * (n - 1 - k)) / (n - 1)) / r0), body))
    for j in range(bands):                                          # growth bands near the root
        i = int(k + (j + 1) * n * 0.025)
        if i >= n - 1:
            break
        d = (pts[i + 1] - pts[i - 1]).normalized()
        rot = Vector((0, 0, 1)).rotation_difference(d).to_matrix().to_4x4()
        b_.append((torus(rad(i / (n - 1)), r0 * 0.05, seg=16, ring=4), root, Matrix.Translation(pts[i]) @ rot))
    return b_


def mammoth_tusk(coll):
    """a mammoth's tusk (2026-10-22, the user: "then tusks"; the three were one curve at three sizes): long and thick,
    curving up and inward and twisting out of its plane as a mammoth's does, ivory, its root stained brown with growth
    bands"""
    b = Builder("mammoth_tusk")
    pts = []
    for i in range(30):
        t = i / 29
        a = t * 2.1                                                 # sweeping round...
        pts.append(Vector((math.sin(a) * 0.9, 0.35 * t * t, (1 - math.cos(a)) * 0.9 * 0.75)))   # ...and drifting out of its plane
    for part in tusk_path(pts, 0.085, 0.012, 0.16, "Ivory", "IvoryRoot", ring=14, bands=4):
        b.add(*part)
    return b.finish(coll)


def orc_tusk(coll):
    """an orc's tusk: short and stout, a gentle hook, yellowed, its root darker where it sat in the jaw, worn flat at the
    tip"""
    b = Builder("orc_tusk")
    pts = [Vector((math.sin(t * 0.9) * 0.1, 0, (1 - math.cos(t * 0.9)) * 0.1)) for t in [i / 11 for i in range(12)]]
    for part in tusk_path(pts, 0.022, 0.008, 0.28, "IvoryOld", "IvoryRoot", ring=10, bands=2):
        b.add(*part)
    return b.finish(coll)


def rat_fang(coll):
    """a giant rat's incisor: long and curved to a point, orange enamel down its front, a pale root"""
    b = Builder("rat_fang")
    pts = [Vector((math.sin(t * 1.6) * 0.03, 0, (1 - math.cos(t * 1.6)) * 0.03)) for t in [i / 13 for i in range(14)]]
    for part in tusk_path(pts, 0.006, 0.0045, 0.3, "Ivory", "IvoryOld", ring=6, bands=0, point=0.3):
        b.add(*part)
    front = []                                                      # the enamel on the outer curve
    for i, p_ in enumerate(pts[3:-3]):
        t = (i + 3) / 13
        a = t * 1.6
        out = Vector((math.sin(a), 0, -math.cos(a)))                # (away from the curve's middle)
        front.append(p_ + out * 0.0045)
    b.add(tube(front, 0.0028, ring=5, closed=False), "RatEnamel")
    return b.finish(coll)


def rhino_horn(coll):
    """a woolly rhino's front horn (2026-10-22, the user: "Rhino horn also needs work"; the first was a plain cone): long,
    flattened from side to side, sweeping forward and up to a point, ridged with growth bands, dark at its broad base
    and paler toward the tip"""
    b = Builder("rhino_horn")
    pts = [Vector((math.sin(t * 0.85) * 0.62, 0, (1 - math.cos(t * 0.85)) * 0.62 + t * 0.12)) for t in [i / 13 for i in range(14)]]
    flat = Matrix.Scale(0.5, 4, Vector((0, 1, 0)))                  # flattened sideways
    for part in tusk_path(pts, 0.11, 0.035, 0.38, "Horn", "HornDark", ring=16, bands=6, point=0.25):
        bm, m = part[0], part[1]
        M = part[2] if len(part) > 2 else Matrix()
        b.add(bm, m, flat @ M)
    return b.finish(coll)


def mammoth_wool(coll):
    """a hank of mammoth hair (2026-10-22, the user: "Mammoth wool also needs work"; the first was a brown lumpy heap):
    long shaggy hair in reddish and dark browns, gathered at one end and tied with a cord, fanning and waving to the
    other -- not the sheep's fluffy fleece"""
    b = Builder("mammoth_wool")
    rnd = random.Random(31)
    core = lathe([(0.0, -0.01), (0.024, 0.0), (0.032, 0.06), (0.036, 0.15), (0.028, 0.24), (0.012, 0.31), (0.0, 0.33)], 14)
    for v in core.verts:                                            # the hank's body, lying along +X, flattened a little
        v.co = Vector((v.co.z, v.co.x, v.co.y * 0.6))
    b.add(core, "WoolBrown")
    for k in range(70):                                             # strands from the knot (at the origin) down +X
        a = rnd.uniform(0, 2 * math.pi)
        spread = rnd.uniform(0.0, 1.0) ** 0.7 * 0.6
        ln = rnd.uniform(0.28, 0.38)
        wave, phase = rnd.uniform(0.006, 0.014), rnd.uniform(0, 6.3)
        pts = []
        for i in range(10):
            t = i / 9
            body = 0.024 + 0.012 * math.sin(min(1.0, t * 1.1) * math.pi * 0.9)   # the hank's radius here (its core)
            r_ = (body * 1.02 + spread * 0.012 * t) * (1 - 0.6 * max(0.0, t - 0.8) / 0.2)
            pts.append(Vector((ln * t, math.cos(a) * r_ + wave * math.sin(t * 9 + phase), math.sin(a) * r_ * 0.45 + wave * 0.5 * math.cos(t * 7 + phase))))
        m = rnd.choice(("WoolBrown", "WoolBrown", "WoolDark"))
        b.add(tube(pts, rnd.uniform(0.009, 0.015), ring=6, closed=False, taper=lambda t: 1 - 0.8 * t), m)
    b.add(sphere(0.026, 1.3, 1.0, 0.75, seg=12, rings=8), "WoolDark", Matrix.Translation(Vector((-0.004, 0, 0))))   # the gathered end
    for x in (0.022, 0.036):                                        # the cord tying it, round the bundle
        b.add(torus(0.026, 0.0045, seg=16, ring=6), "Cord", Matrix.Translation(Vector((x, 0, 0))) @ Matrix.Rotation(math.pi / 2, 4, "Y")
              @ Matrix.Scale(0.75, 4, Vector((1, 0, 0))))
    return b.finish(coll)


def orc_silver(coll):
    b = Builder("orc_silver")
    for k, (x, rz) in enumerate(((-0.02, 0.2), (0.025, -0.3))):
        bar = lump(0.5, 80 + k, 0.08, 0.09, 0.035, 0.022, subdiv=2)
        b.add(bar, "Silver", Matrix.Translation(Vector((x, 0, k * 0.022))) @ Matrix.Rotation(rz, 4, "Z"))
    return b.finish(coll)


def pewter_tankard(coll):
    b = Builder("pewter_tankard")
    b.add(lathe([(0.0, 0.0), (0.045, 0.0), (0.048, 0.01), (0.042, 0.12), (0.045, 0.125), (0.0, 0.125)], 22), "Pewter")
    b.add(tube([Vector((0.04, 0, 0.105)), Vector((0.075, 0, 0.1)), Vector((0.08, 0, 0.06)), Vector((0.065, 0, 0.025)), Vector((0.043, 0, 0.022))],
               0.006, ring=6, closed=False), "Pewter")
    b.add(lathe([(0.0, 0.125), (0.048, 0.125), (0.046, 0.132), (0.02, 0.14), (0.0, 0.142)], 22), "Pewter", Matrix.Translation(Vector((0.004, 0, 0.002))))
    return b.finish(coll)


def gland(name, m, seed, s=1.0):
    def f(coll):
        b = Builder(name)
        b.add(lump(0.03 * s, seed, 0.18, 1.1, 0.9, 1.3, subdiv=3), m)
        b.add(tube([Vector((0, 0, 0.035 * s)), Vector((0.01, 0, 0.055 * s)), Vector((0.025, 0, 0.06 * s))], 0.004 * s, ring=5, closed=False,
                   taper=lambda t: 1 - 0.6 * t), m)
        return b.finish(coll)
    return f


def rat_tail(coll):
    b = Builder("rat_tail")
    pts = [Vector((0.06 * math.cos(t * 4.2) * (1 - t * 0.7), 0.06 * math.sin(t * 4.2) * (1 - t * 0.7), 0)) for t in [i / 30 for i in range(31)]]
    b.add(tube(pts, 0.006, ring=6, closed=False, taper=lambda t: 1 - 0.85 * t), "RatTail")
    return b.finish(coll)


def spider_silk(coll):
    """spider silk (2026-10-22, the user: "spider silk also need to look better"; the first, loops round a ball, read as a
    ribbed ball): a cocoon-like bundle of silk wound round and round with fine threads crossing each other, a few loose
    strands trailing from one end"""
    b = Builder("spider_silk")
    L, Rr = 0.07, 0.032                                             # the bundle: along X
    body = sphere(1.0, L, Rr, Rr * 0.9, seg=20, rings=12)
    rnd = random.Random(14)
    for v in body.verts:
        v.co *= 1 + rnd.uniform(-0.03, 0.03)
    b.add(body, "Silk")
    for k in range(9):                                              # threads wound round it, each at its own slant
        tilt, phase = rnd.uniform(-0.9, 0.9), rnd.uniform(0, 2 * math.pi)
        turns = rnd.uniform(1.5, 3.0)
        pts = []
        for i in range(60):
            t = i / 59
            a = phase + t * turns * 2 * math.pi
            x = (t * 2 - 1) * L * 0.92
            k_ = math.sqrt(max(0.0, 1 - (x / L) ** 2))
            y, z = math.cos(a) * Rr * k_ * 1.04, math.sin(a) * Rr * 0.9 * k_ * 1.04
            pts.append(Matrix.Rotation(tilt * 0.4, 4, "Z") @ Vector((x, y, z)))
        b.add(tube(pts, 0.0011, ring=4, closed=False), "SilkSheen")
    for k in range(4):                                              # loose strands from one end
        a = rnd.uniform(-0.8, 0.8)
        pts = [Vector((L * 0.95, 0, 0))]
        for i in range(1, 8):
            t = i / 7
            pts.append(Vector((L * 0.95 + t * 0.07, math.sin(a) * t * 0.04 + 0.006 * math.sin(t * 9 + k), -t * t * 0.03 + math.cos(a) * t * 0.01)))
        b.add(tube(pts, 0.0008, ring=4, closed=False, taper=lambda t: 1 - 0.6 * t), "SilkSheen")
    return b.finish(coll)


def pelt(name, rolled, cell):
    def f(coll):
        b = Builder(name)
        if rolled:                                                  # rolled up and tied
            roll = bmesh.new()
            bmesh.ops.create_cone(roll, cap_ends=True, segments=18, radius1=0.05, radius2=0.05, depth=0.24)
            b.add(roll, "VK_Goods", Matrix.Rotation(math.pi / 2, 4, "Y"), uv=("goods", cell, (1, 0, 0)))
            for x in (-0.06, 0.06):
                b.add(torus(0.051, 0.004, seg=18, ring=5), "Cord", Matrix.Translation(Vector((x, 0, 0))) @ Matrix.Rotation(math.pi / 2, 4, "Y"))
        else:                                                       # folded in a stack
            for k in range(3):
                layer = lump(0.5, 90 + k, 0.03, 0.26 - k * 0.02, 0.18 - k * 0.01, 0.035, subdiv=3)
                b.add(layer, "VK_Goods", Matrix.Translation(Vector((k * 0.006, 0, k * 0.032))), uv=("goods", cell, (0, 0, 1), "plane"))
        return b.finish(coll)
    return f


def cured_leather(coll):
    b = Builder("cured_leather")
    roll = bmesh.new()
    bmesh.ops.create_cone(roll, cap_ends=True, segments=18, radius1=0.04, radius2=0.04, depth=0.22)
    b.add(roll, "LeatherCured", Matrix.Rotation(math.pi / 2, 4, "Y"))
    b.add(box(0.2, 0.004, 0.06), "LeatherCured", Matrix.Translation(Vector((0, -0.04, -0.03))))   # the loose end
    b.add(torus(0.041, 0.003, seg=18, ring=5), "Cord", Matrix.Rotation(math.pi / 2, 4, "Y"))
    return b.finish(coll)


def cloth(coll):
    """a square of cloth (2026-10-22, the user: "Cloth should be a square cloth piece"; the first was a stack of discs):
    lying flat with soft wrinkles, one corner curling up"""
    b = Builder("cloth")
    n, half, c = 28, 0.2, 0.16                                      # 0.4 m a side; the curl from x + y = c
    bm = bmesh.new()
    rows = []
    for j in range(n + 1):
        row = []
        for i in range(n + 1):
            x, y = -half + 2 * half * i / n, -half + 2 * half * j / n
            z = 0.006 * math.sin(x * 14 + 0.6) * math.cos(y * 9) + 0.004 * math.sin((x - y) * 22)   # wrinkles
            over = (x + y - c) / 0.2                                # one corner curling up off the floor
            if over > 0:
                z += 0.06 * over * over
            row.append(bm.verts.new((x, y, z)))
        rows.append(row)
    for j in range(n):
        for i in range(n):
            bm.faces.new((rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]))
    bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=0.003)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))         # (the shell came out facing in)
    b.add(bm, "Linen")
    return b.finish(coll)


def blob(balls, resolution=0.006):
    """one soft mass from (centre, radius) balls (Blender's metaballs, turned to a mesh)"""
    mb = bpy.data.metaballs.new("tmp_blob")
    mb.resolution = resolution
    mb.render_resolution = resolution
    ob = bpy.data.objects.new("tmp_blob", mb)
    bpy.context.scene.collection.objects.link(ob)
    for at, r in balls:
        e = mb.elements.new()
        e.co = at
        e.radius = r
    bpy.context.view_layer.update()
    me = ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
    bm = bmesh.new()
    bm.from_mesh(me)
    ob.to_mesh_clear()
    bpy.data.objects.remove(ob)
    bpy.data.metaballs.remove(mb)
    return bm


def wool(coll):
    """wool as it comes off the sheep (2026-10-22, the user: "Wool ... also need to look better"; a skein read as a ring,
    separate curls as pebbles): one soft heap of fleece -- many curls melted into a mound (metaballs), its surface
    tufted, cream in its hollows"""
    b = Builder("wool")
    rnd = random.Random(23)
    balls = []
    for k in range(70):
        u, v = rnd.uniform(-1, 1), rnd.uniform(-1, 1)
        if u * u + v * v > 1:
            continue
        hgt = math.sqrt(max(0.0, 1 - u * u - v * v))
        balls.append((Vector((u * 0.1, v * 0.07, hgt * 0.04)), rnd.uniform(0.022, 0.034)))
    for x, y in ((-0.05, -0.02), (0.0, 0.0), (0.05, 0.02), (-0.03, 0.035), (0.04, -0.03), (0.0, -0.04), (0.0, 0.045)):
        balls.append((Vector((x, y, 0.02)), 0.045))                 # a full body under the curls (no holes through it)
    bm = blob(balls, 0.005)
    for v in bm.verts:                                              # tufts: the surface pushed in and out
        n = v.normal
        v.co += n * 0.0022 * (math.sin(v.co.x * 260) * math.sin(v.co.y * 230) + math.sin(v.co.z * 300 + v.co.x * 90))
    b.add(bm, "Wool")
    return b.finish(coll)


def lumps(name, m, seed, extra=None):
    def f(coll):
        b = Builder(name)
        for k, (x, y, z, r) in enumerate(((-0.03, 0, 0.02, 0.03), (0.03, 0.01, 0.018, 0.026), (0.0, -0.03, 0.015, 0.022), (0.005, 0.01, 0.05, 0.024))):
            b.add(lump(r, seed + k, 0.3), m, Matrix.Translation(Vector((x, y, z))))
        if extra:
            for k, (x, y, z) in enumerate(((-0.022, -0.02, 0.03), (0.035, -0.012, 0.03), (0.0, -0.008, 0.07))):
                b.add(lump(0.008, seed + 20 + k, 0.4), extra, Matrix.Translation(Vector((x, y, z))))
        return b.finish(coll)
    return f


def garnet(coll):
    """a garnet (2026-10-22, the user: "each gem should have a different mesh"; its item: "A dark red stone,
    rough-cut"): the stone as it grows, a dodecahedron of twelve rhombic faces, a little uneven, its colour the item's"""
    b = Builder("garnet")
    pts = [(sx, sy, sz) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)] + \
          [(2, 0, 0), (-2, 0, 0), (0, 2, 0), (0, -2, 0), (0, 0, 2), (0, 0, -2)]
    bm = bmesh.new()
    rnd = random.Random(61)
    vs = [bm.verts.new(Vector(p_) * (1 + rnd.uniform(-0.06, 0.06))) for p_ in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    bmesh.ops.dissolve_limit(bm, angle_limit=0.08, verts=list(bm.verts), edges=list(bm.edges))   # (the hull's rhombi whole)
    b.add(bm, "Tint", Matrix.Rotation(0.4, 4, "Z") @ Matrix.Rotation(0.5, 4, "X") @ Matrix.Scale(0.005, 4))
    return b.finish(coll, flat=True)


def sapphire(coll):
    """a sapphire (2026-10-22; its item: "A clear blue gem the size of a thumbnail"): an oval cut, a broad table and a
    stepped crown over a deep pavilion, its colour the item's"""
    b = Builder("sapphire")
    bm = lathe([(0.0, -0.016), (0.009, -0.007), (0.0125, 0.0), (0.0125, 0.0012), (0.0095, 0.0045), (0.0065, 0.0062), (0.0, 0.0064)], 12)
    b.add(bm, "Tint", Matrix.Scale(1.35, 4, Vector((1, 0, 0))))
    return b.finish(coll, flat=True)


def ruby(coll):
    """a ruby (2026-10-22; its item: "A flawless red gem that seems to hold a light of its own"): a step cut, eight-sided
    (a long rectangle with its corners cut), flat stepped facets round a wide table, its colour the item's"""
    b = Builder("ruby")
    bm = lathe([(0.0, -0.011), (0.006, -0.0075), (0.01, -0.0035), (0.012, 0.0), (0.012, 0.001), (0.0105, 0.0028),
                (0.0088, 0.0042), (0.0, 0.0043)], 8)
    b.add(bm, "Tint", Matrix.Scale(1.3, 4, Vector((1, 0, 0))) @ Matrix.Rotation(math.pi / 8, 4, "Z"))
    return b.finish(coll, flat=True)


def rings_face(b, M, r, bands, seg=28):
    """a sawn face of rings (local XY, facing +Z): bands of (outer radius as a share of r, material) from the middle out"""
    r0 = 0.0
    for share, m in bands:
        r1 = r * share
        ann = bmesh.new()
        outer = [ann.verts.new((r1 * math.cos(2 * math.pi * k / seg), r1 * math.sin(2 * math.pi * k / seg), 0)) for k in range(seg)]
        if r0 < 1e-6:
            c = ann.verts.new((0, 0, 0))
            for k in range(seg):
                ann.faces.new((c, outer[k], outer[(k + 1) % seg]))
        else:
            inner = [ann.verts.new((r0 * math.cos(2 * math.pi * k / seg), r0 * math.sin(2 * math.pi * k / seg), 0)) for k in range(seg)]
            for k in range(seg):
                ann.faces.new((inner[k], outer[k], outer[(k + 1) % seg], inner[(k + 1) % seg]))
        b.add(ann, m, M, flat=True)
        r0 = r1


def heartwood(coll):
    """heartwood (2026-10-22, the user: "fix heartwood first"; the first, a slice with a dark smear for a face): a thick
    sawn slice of oak standing on its edge, its face to the front -- the dark heart in the middle in tight rings, the
    pale sapwood round it, then the bark; a check (crack) in the heart"""
    b = Builder("heartwood")
    R, Tk = 0.15, 0.07
    rim = lathe([(R * 0.985, -Tk / 2), (R, -Tk / 2 + 0.006), (R, Tk / 2 - 0.006), (R * 0.985, Tk / 2)], 28)
    for v in rim.verts:                                             # the bark a little rough
        k = 1 + 0.025 * math.sin(math.atan2(v.co.y, v.co.x) * 7) + 0.015 * math.sin(math.atan2(v.co.y, v.co.x) * 17)
        v.co.x *= k
        v.co.y *= k
    stand = Matrix.Rotation(math.pi / 2, 4, "X") @ Matrix.Rotation(-0.25, 4, "Z")   # on its edge, a face to -Y
    b.add(rim, "VK_BarkOak", stand, uv=("wrap", (0, 0, 1), 3.0, 4.0))
    bands = [(0.05, "WoodPith"), (0.16, "HeartDark"), (0.27, "Heart"), (0.36, "HeartDark"), (0.46, "Heart"), (0.54, "HeartDark"),
             (0.62, "Heart"), (0.7, "WoodRing"), (0.8, "WoodEnd"), (0.88, "WoodRing"), (0.955, "WoodEnd"), (0.985, "CoverShade")]
    for z, flip in ((Tk / 2, False), (-Tk / 2, True)):
        M = stand @ Matrix.Translation(Vector((0, 0, z + (-0.0015 if flip else 0.0015)))) @ (Matrix.Rotation(math.pi, 4, "X") if flip else Matrix())   # (clear of the rim's caps)
        rings_face(b, M, R, bands)
        b.add(box(R * 0.5, 0.004, 0.0016), "WoodPith", M @ Matrix.Rotation(0.6, 4, "Z") @ Matrix.Translation(Vector((R * 0.27, 0, 0.0008))), flat=True)
    return b.finish(coll)


def log_end(b, at, normal, r, seed):
    """a log's sawn end: pale wood in growth rings round a dark pith, a crack or two from the middle"""
    rnd = random.Random(seed)
    rot = Vector((0, 0, 1)).rotation_difference(normal).to_matrix().to_4x4()
    M = Matrix.Translation(at) @ rot
    radii = sorted([0.0] + [r * t for t in (0.16, 0.34, 0.5, 0.64, 0.78, 0.9)] + [r * 0.97])
    for i, (r0, r1) in enumerate(zip(radii, radii[1:])):
        ann = bmesh.new()
        seg = 20
        outer = [ann.verts.new((r1 * math.cos(2 * math.pi * k / seg), r1 * math.sin(2 * math.pi * k / seg), 0)) for k in range(seg)]
        if r0 < 1e-6:
            c = ann.verts.new((0, 0, 0))
            for k in range(seg):
                ann.faces.new((c, outer[k], outer[(k + 1) % seg]))
        else:
            inner = [ann.verts.new((r0 * math.cos(2 * math.pi * k / seg), r0 * math.sin(2 * math.pi * k / seg), 0)) for k in range(seg)]
            for k in range(seg):
                ann.faces.new((inner[k], outer[k], outer[(k + 1) % seg], inner[(k + 1) % seg]))
        m = "WoodPith" if i == 0 else "WoodRing" if i % 2 == 0 else "WoodEnd"
        b.add(ann, m, M, flat=True)
    for k in range(rnd.randrange(1, 3)):                            # cracks from the pith
        a = rnd.uniform(0, 2 * math.pi)
        b.add(box(r * 0.55, 0.003, 0.0015), "WoodPith", M @ Matrix.Rotation(a, 4, "Z") @ Matrix.Translation(Vector((r * 0.3, 0, 0.0008))), flat=True)


def tight_loop(logs, y, L, rope_r, n=96):
    """a rope pulled tight round logs at a height along them (2026-10-22, the user: "Tighten the rope, is there a blender
    method for this?" -- Blender's Shrinkwrap would pull it down into the gaps between the logs; a tight rope bridges
    them): the outline of the logs' sections there -- for each direction round, the point of the log reaching furthest
    that way (arcs round each log, straight runs between them where the direction passes from one to the next)"""
    secs = []
    for x, z, r, y0, k in logs:
        t = (y - y0 + L / 2) / L * 10                               # where along the log (its swell, its bend)
        secs.append((Vector((x + 0.008 * math.sin((y - y0) * 3 + k), z)), r * (1 + 0.05 * math.sin(t * 1.7 + k)) + rope_r * 0.9))
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        u = Vector((math.cos(a), math.sin(a)))
        c, rr = max(secs, key=lambda s_: s_[0].dot(u) + s_[1])
        q = c + u * rr
        pts.append(Vector((q.x, y, q.y)))
    out = [pts[0]]                                                  # (the jumps between logs are the straight runs:
    for q in pts[1:]:                                               #  points along them so the tube stays round)
        last = out[-1]
        gap = (q - last).length
        if gap > 0.012:
            steps = int(gap / 0.008)
            out += [last.lerp(q, j / (steps + 1)) for j in range(1, steps + 1)]
        out.append(q)
    return out


def timber(coll):
    """timber (2026-10-22, the user: "Timber icon also needs rework"; the first, three grey pipes with dark blobs for
    ends): three oak logs, a little crooked and uneven, stacked two and one and lashed with a rope; the kit's oak bark
    wrapped along them, their sawn ends pale with growth rings"""
    b = Builder("timber")
    L = 0.9
    rnd = random.Random(44)
    logs = []
    for k, (x, z, r) in enumerate(((-0.06, 0.0, 0.058), (0.062, 0.0, 0.055), (0.0, 0.098, 0.052))):
        y0 = rnd.uniform(-0.03, 0.03)
        logs.append((x, z, r, y0, k))
        prof = [(r * (1 + 0.05 * math.sin(t * 1.7 + k)), -L / 2 + L * t / 10) for t in range(11)]   # a log's swell along it
        log = lathe(prof, 16)
        for v in log.verts:                                         # uneven bark, a slight bend
            if abs(v.co.x) + abs(v.co.y) > 1e-6:
                v.co.x += rnd.uniform(-0.002, 0.002)
                v.co.y += rnd.uniform(-0.002, 0.002)
            v.co.x += 0.008 * math.sin(v.co.z * 3 + k)
        place = Matrix.Translation(Vector((x, y0, z))) @ Matrix.Rotation(-math.pi / 2, 4, "X")   # along +Y
        b.add(log, "VK_BarkOak", place, uv=("wrap", (0, 1, 0), 2.0, 2.2))
        pts = [place @ Vector((0.008 * math.sin(-L / 2 * 3 + k), 0, -L / 2)), place @ Vector((0.008 * math.sin(L / 2 * 3 + k), 0, L / 2))]
        for end, n in ((pts[0], Vector((0, -1, 0))), (pts[-1], Vector((0, 1, 0)))):
            log_end(b, end + n * 0.0015, n, r * 0.97, 50 + k * 3 + int(n.y))
        if k == 0:                                                  # a branch stub
            stub = pts[0].lerp(pts[1], 0.35) + Vector((-r * 0.6, 0, r * 0.6))
            b.add(tube([stub, stub + Vector((-0.04, 0.02, 0.03))], 0.016, ring=8, closed=False, taper=lambda t: 1 - 0.3 * t),
                  "VK_BarkOak", uv=("wrap", (-0.7, 0.35, 0.5), 1.0, 2.2))
    for y in (-0.22, 0.24):                                         # a rope round the bundle, pulled tight
        b.add(tube(tight_loop(logs, y, L, 0.007), 0.007, ring=6), "Rope")
    return b.finish(coll)


def stag_antler(coll):
    b = Builder("stag_antler")
    beam = [Vector((0.0, 0, 0.0)), Vector((0.03, 0, 0.08)), Vector((0.03, 0, 0.17)), Vector((0.0, 0, 0.25)), Vector((-0.04, 0, 0.3))]
    b.add(tube(beam, 0.014, ring=8, closed=False, taper=lambda t: 1 - 0.6 * t), "Bone")
    for p, d in ((beam[1], Vector((-0.07, -0.01, 0.05))), (beam[2], Vector((-0.06, 0.0, 0.07))), (beam[3], Vector((0.05, 0, 0.06)))):
        b.add(tube([p, p + d * 0.5, p + d], 0.008, ring=6, closed=False, taper=lambda t: 1 - 0.8 * t), "Bone")
    b.add(torus(0.02, 0.008, seg=12, ring=6), "Bone")              # the burr
    return b.finish(coll)


def stone(coll):
    b = Builder("stone")
    b.add(box(0.2, 0.12, 0.1), "VK_StoneFresh", Matrix.Translation(Vector((0, 0, 0.05))))
    b.add(box(0.14, 0.1, 0.08), "VK_StoneFresh", Matrix.Translation(Vector((0.02, 0.0, 0.14))) @ Matrix.Rotation(0.3, 4, "Z"))
    return b.finish(coll)


# ---- the tomes (2026-10-22, the user: "tomes per class is a good call. Plus the neutral tomes. Make 3 tomes per class,
# with a common color theme"): six themes -- a class's leather, the metal of its fittings, its emblem, gilt page edges for
# the wizard's and the cleric's -- and three builds each: iron-bound (metal corners, a clasp), strapped (two buckled
# straps), banded (raised spine bands, an embossed frame). Lying flat, the front cover up (+Z), the spine to -X.

THEMES = {   # class: (cover, metal, emblem, pages, (width, height, thickness))
    "fighter": ("CoverFighter", "IronTrim", "swords", "Pages", (0.21, 0.28, 0.07)),
    "rogue": ("CoverRogue", "Silver", "dagger", "Pages", (0.15, 0.2, 0.04)),
    "wizard": ("CoverWizard", "Gold", "star", "Gold", (0.2, 0.27, 0.065)),
    "ranger": ("CoverRanger", "Bronze", "leaf", "Pages", (0.18, 0.24, 0.05)),
    "cleric": ("CoverCleric", "Gold", "sun", "Gold", (0.19, 0.26, 0.055)),
    "general": ("CoverGeneral", "Bronze", "medallion", "Pages", (0.18, 0.25, 0.05)),
}


def prism(pts2d, h):
    """a flat plate from an outline in XY, h thick (bottom at z 0)"""
    bm = bmesh.new()
    lo = [bm.verts.new((x, y, 0)) for x, y in pts2d]
    hi = [bm.verts.new((x, y, h)) for x, y in pts2d]
    n = len(pts2d)
    bm.faces.new(list(reversed(lo)))
    bm.faces.new(hi)
    for i in range(n):
        bm.faces.new((lo[i], lo[(i + 1) % n], hi[(i + 1) % n], hi[i]))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    return bm


def emblem(b, kind, m, at, size):
    """a raised emblem on the cover, its middle at `at` (on the cover's top), about `size` across"""
    T = Matrix.Translation(at)
    t = 0.003
    if kind == "swords":
        for a in (0.75, -0.75):
            R_ = T @ Matrix.Rotation(a, 4, "Z")
            b.add(box(size, size * 0.09, t), m, R_ @ Matrix.Translation(Vector((0, 0, t / 2))), flat=True)
            b.add(box(size * 0.08, size * 0.32, t * 1.2), m, R_ @ Matrix.Translation(Vector((-size * 0.3, 0, t / 2))), flat=True)
    elif kind == "dagger":
        b.add(prism([(-size * 0.5, -size * 0.06), (size * 0.25, -size * 0.07), (size * 0.5, 0), (size * 0.25, size * 0.07), (-size * 0.5, size * 0.06)], t),
              m, T @ Matrix.Rotation(math.pi / 2, 4, "Z"), flat=True)
        b.add(box(size * 0.4, size * 0.07, t * 1.3), m, T @ Matrix.Translation(Vector((0, -size * 0.12, t * 0.6))), flat=True)
        b.add(sphere(size * 0.06, 1, 1, 0.6, seg=8, rings=6), m, T @ Matrix.Translation(Vector((0, -size * 0.55, t * 0.5))))
    elif kind == "star":
        pts = []
        for i in range(12):
            r = size * (0.5 if i % 2 == 0 else 0.24)
            a = math.pi / 2 + i * math.pi / 6
            pts.append((r * math.cos(a), r * math.sin(a)))
        b.add(prism(pts, t), m, T, flat=True)
        b.add(torus(size * 0.62, size * 0.025, seg=24, ring=4), m, T @ Matrix.Translation(Vector((0, 0, t * 0.5))))
    elif kind == "leaf":
        b.add(sphere(size * 0.5, 0.45, 1.0, 0.08, seg=14, rings=8), m, T @ Matrix.Rotation(-0.5, 4, "Z") @ Matrix.Translation(Vector((0, 0, t * 0.5))))
        b.add(box(size * 0.025, size * 1.15, t * 1.4), "CoverShade", T @ Matrix.Rotation(-0.5, 4, "Z") @ Matrix.Translation(Vector((0, 0, t * 0.9))), flat=True)
    elif kind == "sun":
        b.add(cyl(size * 0.2, t, seg=20), m, T @ Matrix.Translation(Vector((0, 0, t / 2))), flat=True)
        for i in range(12):
            a = i * math.pi / 6
            ln = size * (0.3 if i % 2 == 0 else 0.2)
            b.add(prism([(size * 0.24, -size * 0.04), (size * 0.24 + ln, 0), (size * 0.24, size * 0.04)], t), m, T @ Matrix.Rotation(a, 4, "Z"), flat=True)
    else:                                                           # a plain medallion
        b.add(cyl(size * 0.32, t, seg=24), m, T @ Matrix.Translation(Vector((0, 0, t / 2))), flat=True)
        b.add(torus(size * 0.32, size * 0.035, seg=24, ring=5), m, T @ Matrix.Translation(Vector((0, 0, t))))


def tome(cls, v):
    """a book of a class's theme, build v (0 iron-bound, 1 strapped, 2 banded)"""
    def f(coll):
        cover, metal, emb, pages, (W, H, Tk) = THEMES[cls]
        b = Builder(f"tome_{cls}_{v}")
        bt = 0.006                                                  # a board's thickness
        top = Tk / 2
        for z in (top - bt / 2, -top + bt / 2):                     # the boards
            b.add(rbox(W, H, bt, 0.0025), cover, Matrix.Translation(Vector((0, 0, z))))
        b.add(box(W - 0.012, H - 0.012, Tk - 2 * bt + 0.001), pages, Matrix.Translation(Vector((0.004, 0, 0))), flat=True)   # the page block
        spine = cyl(Tk / 2, H, seg=16)                              # the rounded spine
        b.add(spine, cover, Matrix.Translation(Vector((-W / 2 + 0.002, 0, 0))) @ Matrix.Rotation(math.pi / 2, 4, "X")
              @ Matrix.Scale(0.45, 4, Vector((1, 0, 0))))
        face = top + 0.0002                                         # the front cover's top
        if v == 0:                                                  # iron-bound: corners, a clasp across the fore-edge
            c = 0.034
            for sx in (-1, 1):
                for sy in (-1, 1):
                    x0, y0 = sx * W / 2, sy * H / 2
                    b.add(prism([(x0, y0), (x0 - sx * c, y0), (x0, y0 - sy * c)], 0.003), metal, Matrix.Translation(Vector((0, 0, face))), flat=True)
            b.add(box(0.05, 0.03, 0.003), "CoverShade", Matrix.Translation(Vector((W / 2 - 0.022, 0, face + 0.0015))), flat=True)
            b.add(box(0.004, 0.03, Tk + 0.004), "CoverShade", Matrix.Translation(Vector((W / 2 + 0.002, 0, 0))), flat=True)
            b.add(box(0.016, 0.036, 0.005), metal, Matrix.Translation(Vector((W / 2 - 0.042, 0, face + 0.0025))), flat=True)
            emblem(b, emb, metal, Vector((-0.01, 0, face)), min(W, H) * 0.42)
        elif v == 1:                                                # strapped: two straps round it, buckled on top
            for y in (-H * 0.27, H * 0.27):
                b.add(box(W * 0.62, 0.022, 0.003), "CoverShade", Matrix.Translation(Vector((W * 0.19, y, face + 0.0015))), flat=True)
                b.add(box(0.004, 0.022, Tk + 0.004), "CoverShade", Matrix.Translation(Vector((W / 2 + 0.002, y, 0))), flat=True)
                fr = Matrix.Translation(Vector((-W * 0.08, y, face + 0.003)))
                for dx, dy, sx_, sy_ in ((-0.012, 0, 0.004, 0.03), (0.012, 0, 0.004, 0.03), (0, 0.013, 0.024, 0.004), (0, -0.013, 0.024, 0.004)):
                    b.add(box(sx_, sy_, 0.004), metal, fr @ Matrix.Translation(Vector((dx, dy, 0))), flat=True)
            emblem(b, emb, metal, Vector((0.0, 0, face)), min(W, H) * 0.3)
        else:                                                       # banded: raised spine bands, an embossed frame
            for y in (-H * 0.28, 0.0, H * 0.28):
                b.add(cyl(Tk / 2 + 0.003, 0.012, seg=16), cover, Matrix.Translation(Vector((-W / 2 + 0.002, y, 0))) @ Matrix.Rotation(math.pi / 2, 4, "X")
                      @ Matrix.Scale(0.5, 4, Vector((1, 0, 0))))
            inset = 0.018
            for (cx, cy, sx_, sy_) in ((0, H / 2 - inset, W - 2 * inset, 0.006), (0, -H / 2 + inset, W - 2 * inset, 0.006),
                                       (W / 2 - inset, 0, 0.006, H - 2 * inset), (-W / 2 + inset, 0, 0.006, H - 2 * inset)):
                b.add(box(sx_, sy_, 0.003), metal, Matrix.Translation(Vector((cx, cy, face + 0.0015))), flat=True)
            emblem(b, emb, metal, Vector((0.0, 0, face)), min(W, H) * 0.46)
        return b.finish(coll)
    return f


TOMES_ALL = [tome(c, v) for c in THEMES for v in range(3)]


# ---- worn armour as it lies on the ground (2026-10-22, the user: "every item now needs a world mesh, so we need to keep
# track this part and build the ones that don't exist"; the armour's icons are a dressed body, so it had no model of its
# own): each piece laid out flat, as dropped -- z 0 the ground, the garment in the XY plane (its neck to +Y), at real size.

def slab(outline, depth=0.004, bevel=0.01, res=3):
    """a soft flat piece (a garment, a strap) from a 2D outline (x, y): a filled curve, extruded and bevelled round its
    edge like a cushion, bottom on z 0; the outline may be concave (sleeves, fingers)"""
    cu = bpy.data.curves.new("tmp_slab", "CURVE")
    cu.dimensions = "2D"
    cu.fill_mode = "BOTH"
    cu.extrude = depth
    cu.bevel_depth = bevel
    cu.bevel_resolution = res
    sp = cu.splines.new("POLY")
    sp.points.add(len(outline) - 1)
    for p, (x, y) in zip(sp.points, outline):
        p.co = (x, y, 0, 1)
    sp.use_cyclic_u = True
    ob = bpy.data.objects.new("tmp_slab", cu)
    bpy.context.scene.collection.objects.link(ob)
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bm = bmesh.new()
    bm.from_mesh(me)
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    bpy.data.meshes.remove(me)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4], quad_method="BEAUTY", ngon_method="BEAUTY")
    lo = min(v.co.z for v in bm.verts)
    for v in bm.verts:
        v.co.z -= lo
    return bm


def mirror_x(half):
    """a closed outline from its right half (x >= 0, listed from the top centre round to the bottom centre)"""
    return half + [(-x, y) for x, y in reversed(half) if abs(x) > 1e-6]


def smooth_outline(pts, n=3):
    """corners cut (Chaikin), n times: a hand-drawn outline made soft"""
    for _ in range(n):
        out = []
        for i in range(len(pts)):
            a, b = Vector(pts[i]), Vector(pts[(i + 1) % len(pts)])
            out += [tuple(a.lerp(b, 0.25)), tuple(a.lerp(b, 0.75))]
        pts = out
    return pts


def studs_on(b, pts, z, m="IronTrim", r=0.0065):
    for x, y in pts:
        b.add(sphere(r, 1, 1, 0.6, seg=8, rings=4), m, Matrix.Translation(Vector((x, y, z))))


COAT = mirror_x([(0.0, 0.33), (0.07, 0.4), (0.21, 0.37), (0.34, 0.27), (0.46, 0.12), (0.5, 0.0), (0.44, -0.05),
                 (0.36, 0.06), (0.22, 0.14), (0.19, -0.08), (0.3, -0.5), (0.16, -0.54), (0.025, -0.53), (0.0, -0.44)])
CUIRASS = mirror_x([(0.0, 0.27), (0.06, 0.35), (0.13, 0.36), (0.2, 0.3), (0.2, 0.1), (0.18, -0.12), (0.0, -0.15)])


def leather_coat(b, m_coat, m_cuirass, z0=0.0):
    """the leather set laid out: a long coat, sleeves spread and its skirt split, a cuirass over the chest, a belt"""
    b.add(slab(smooth_outline(COAT, 2), depth=0.003, bevel=0.009, res=2), m_coat)
    b.add(slab(smooth_outline(CUIRASS, 2), depth=0.002, bevel=0.008), m_cuirass, Matrix.Translation(Vector((0, 0, 0.014))))
    for s_ in (-1, 1):                                              # the shoulder straps
        b.add(slab([(-0.025, -0.06), (0.025, -0.06), (0.025, 0.06), (-0.025, 0.06)], 0.001, 0.003, 2), "Leather",
              Matrix.Translation(Vector((s_ * 0.15, 0.31, 0.03))) @ Matrix.Rotation(s_ * 0.5, 4, "Z"))
    for k in range(5):                                              # the lacing down the front
        y = 0.22 - k * 0.07
        for s_ in (-1, 1):
            b.add(tube([Vector((-0.02, y, 0.034)), Vector((0.02, y - s_ * 0.02, 0.034))], 0.0018, ring=4, closed=False), "Cord")
    b.add(slab([(-0.21, -0.03), (0.21, -0.03), (0.21, 0.015), (-0.21, 0.015)], 0.002, 0.004, 2), "LeatherCured",
          Matrix.Translation(Vector((0, -0.1, 0.03))))
    b.add(torus(0.016, 0.0028, seg=12, ring=4), "IronTrim", Matrix.Translation(Vector((0.0, -0.093, 0.041))) @ Matrix.Scale(1.25, 4, Vector((1, 0, 0))))


def leather(coll):
    """leather armour laid out: a brown coat and its lighter cuirass, laced, belted"""
    b = Builder("leather")
    leather_coat(b, "Leather", "LeatherCured")
    return b.finish(coll)


def studded_leather(coll):
    """studded leather laid out: the coat and cuirass in the item's colour (oxblood, or blackened: IT_Tint), riveted with
    iron studs, pauldrons at the shoulders"""
    b = Builder("studded_leather")
    leather_coat(b, "Tint", "Leather")
    pts = [(x * 0.05, 0.28 - k * 0.075) for k in range(5) for x in (-3, -2, 2, 3)]
    studs_on(b, pts, 0.03)
    for s_ in (-1, 1):                                              # pauldrons, studded
        pd = slab(smooth_outline([(-0.09, -0.05), (0.09, -0.05), (0.1, 0.03), (0.0, 0.08), (-0.1, 0.03)], 2), 0.003, 0.009)
        M = Matrix.Translation(Vector((s_ * 0.27, 0.27, 0.02))) @ Matrix.Rotation(s_ * -0.6, 4, "Z")
        b.add(pd, "Tint", M)
        studs_on(b, [(M @ Vector((x, y, 0))).xy for x, y in ((-0.05, 0.0), (0.0, 0.03), (0.05, 0.0), (0.0, -0.02))], 0.045)
    return b.finish(coll)


def dome(rx, ry, rz, seg=20, rings=6, t=0.004):
    """an open shell (a breastplate, a pauldron): the top half of an ellipsoid, solid t thick, rim on z 0"""
    bm = bmesh.new()
    rows = []
    for j in range(rings + 1):
        th = (math.pi / 2) * j / rings
        r, z = math.cos(th), math.sin(th)
        if j == rings:
            rows.append([bm.verts.new((0, 0, rz))])
            break
        rows.append([bm.verts.new((math.cos(2 * math.pi * i / seg) * rx * r, math.sin(2 * math.pi * i / seg) * ry * r, rz * z)) for i in range(seg)])
    for j in range(rings):
        a, c = rows[j], rows[j + 1]
        for i in range(seg):
            k = (i + 1) % seg
            if len(c) == 1:
                bm.faces.new((a[i], a[k], c[0]))
            else:
                bm.faces.new((a[i], a[k], c[k], c[i]))
    bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=t)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    return bm


def platemail(coll):
    """plate laid down: the breastplate on its back, pauldrons and the faulds' lames beside it, a gorget at the neck,
    leather straps"""
    b = Builder("platemail")
    bp = dome(0.19, 0.27, 0.1, seg=28, rings=7)
    for v in bp.verts:                                              # a ridge down the middle, the waist pinched, the top squared
        v.co.z += 0.015 * max(0.0, 1 - abs(v.co.x) / 0.06) * (v.co.z > 0.02)
        v.co.x *= 1 - 0.18 * max(0.0, -v.co.y / 0.27)
        if v.co.y > 0.0:
            v.co.x *= 1 + 0.25 * (v.co.y / 0.27)
        if v.co.y > 0.2 and abs(v.co.x) < 0.09:                     # the neck cut
            v.co.y = 0.2 + (v.co.y - 0.2) * 0.25 + 0.04 * (abs(v.co.x) / 0.09) ** 2
    b.add(bp, "Steel", Matrix.Translation(Vector((0, 0.02, 0.0))))
    b.add(torus(0.075, 0.009, seg=18, ring=6), "Steel", Matrix.Translation(Vector((0, 0.27, 0.012))) @ Matrix.Scale(0.6, 4, Vector((0, 0, 1))))
    for k in range(3):                                              # the faulds: lames below the waist
        lame = dome(0.2 - 0.01 * k, 0.04, 0.035, seg=16, rings=3, t=0.003)
        b.add(lame, "Steel", Matrix.Translation(Vector((0, -0.25 - 0.05 * k, 0.0))))
    for s_ in (-1, 1):                                              # pauldrons
        pd = dome(0.1, 0.085, 0.07, seg=16, rings=5)
        b.add(pd, "Steel", Matrix.Translation(Vector((s_ * 0.32, 0.16, 0.0))) @ Matrix.Rotation(s_ * 0.5, 4, "Z"))
        b.add(slab([(-0.012, -0.07), (0.012, -0.07), (0.012, 0.07), (-0.012, 0.07)], 0.001, 0.003, 2), "Leather",
              Matrix.Translation(Vector((s_ * 0.16, 0.12, 0.0))) @ Matrix.Rotation(s_ * 0.9, 4, "Z"))
    return b.finish(coll)


BOOT = [(-0.05, 0.0), (0.2, 0.0), (0.24, 0.02), (0.24, 0.05), (0.18, 0.075), (0.07, 0.1), (0.06, 0.32), (-0.05, 0.32),
        (-0.055, 0.05)]


def boot_pair(b, m, sole, shaft_plate=None, low=False):
    """a pair of boots lying on their sides, one a little behind the other"""
    out = [(x, min(y, 0.12) if low else y) for x, y in BOOT]
    for k, (dx, dy, a) in enumerate(((-0.06, -0.04, 0.15), (0.12, 0.12, -0.45))):
        M = Matrix.Translation(Vector((dx - 0.09, dy - 0.16, 0.0))) @ Matrix.Rotation(a, 4, "Z")
        b.add(slab(smooth_outline(out, 2), depth=0.028, bevel=0.016), m, M)
        b.add(slab(smooth_outline([(-0.055, -0.012), (0.245, -0.012), (0.25, 0.012), (-0.06, 0.012)], 1), 0.03, 0.012), sole,
              M @ Matrix.Translation(Vector((0, 0.0, -0.001))))
        if shaft_plate:
            b.add(slab(smooth_outline([(-0.03, 0.12), (0.06, 0.12), (0.055, 0.3), (-0.035, 0.3)], 1), 0.004, 0.006), shaft_plate,
                  M @ Matrix.Translation(Vector((0, 0, 0.088))))   # (on top: the boot stands 2 x (0.028 + 0.016))
        if k == 0 and not low:
            b.add(torus(0.06, 0.006, seg=16, ring=4), m, M @ Matrix.Translation(Vector((0.005, 0.32, 0.03))) @ Matrix.Scale(0.5, 4, Vector((0, 1, 0))))


def leather_boots(coll):
    b = Builder("leather_boots")
    boot_pair(b, "Leather", "WoolDark")
    return b.finish(coll)


HAND = [(-0.045, 0.0), (-0.05, 0.08), (-0.075, 0.11), (-0.095, 0.15), (-0.085, 0.16), (-0.05, 0.13), (-0.045, 0.2),
        (-0.035, 0.205), (-0.03, 0.14), (-0.02, 0.215), (-0.008, 0.215), (-0.006, 0.145), (0.006, 0.21), (0.018, 0.21),
        (0.02, 0.14), (0.03, 0.19), (0.042, 0.19), (0.045, 0.1), (0.05, 0.0)]


def glove_pair(b, m, cuff, plates=None):
    for k, (dx, dy, a, flip) in enumerate(((-0.06, -0.1, 0.25, 1), (0.07, -0.08, -0.3, -1))):
        M = Matrix.Translation(Vector((dx, dy, 0.0))) @ Matrix.Rotation(a, 4, "Z") @ Matrix.Scale(flip, 4, Vector((1, 0, 0)))
        pts = smooth_outline(HAND, 1)
        if flip < 0:
            pts = pts[::-1]
        b.add(slab(pts, depth=0.006, bevel=0.009), m, M)
        b.add(slab(smooth_outline([(-0.06, -0.06), (0.065, -0.06), (0.055, 0.02), (-0.05, 0.02)], 1), 0.004, 0.009), cuff, M)
        if plates:
            for j in range(4):
                b.add(slab([(-0.045, 0.0), (0.045, 0.0), (0.042, 0.022), (-0.042, 0.022)], 0.002, 0.004, 2), plates,
                      M @ Matrix.Translation(Vector((0, 0.03 + 0.024 * j, 0.022))))


def leather_gloves(coll):
    b = Builder("leather_gloves")
    glove_pair(b, "LeatherCured", "Leather")
    return b.finish(coll)


def coin_pile(name, n, R, seed):
    """gold on the ground: n coins in a low heap R across (a few scattered for a little, a heap for a lot)"""
    def f(coll):
        b = Builder(name)
        rnd = random.Random(seed)
        placed = []
        for k in range(n):
            a = rnd.uniform(0, 2 * math.pi)
            d = R * math.sqrt(rnd.random())
            x, y = math.cos(a) * d, math.sin(a) * d
            under = sum(1 for (px, py) in placed if (px - x) ** 2 + (py - y) ** 2 < 0.028 ** 2)
            z = 0.0018 + under * 0.0034 + max(0.0, (R - d)) * (0.3 if n > 12 else 0.0)
            tilt = Matrix.Rotation(rnd.uniform(-0.25, 0.25), 4, "X") @ Matrix.Rotation(rnd.uniform(-0.25, 0.25), 4, "Y")
            b.add(cyl(0.018, 0.0034, seg=12), "Gold", Matrix.Translation(Vector((x, y, z))) @ tilt, flat=False)
            placed.append((x, y))
        return b.finish(coll)
    return f


def lines_on(b, segs, z, m, w=0.004):
    """flat strips on a piece (quilting, a seam, trim): each segment a thin card from a to b at height z"""
    for (x0, y0), (x1, y1) in segs:
        a, c = Vector((x0, y0, z)), Vector((x1, y1, z))
        b.add(band([a, c], (0, 0, 1), w, 0.0008, normal=lambda p_: Vector((0, 0, 1))), m, flat=True)


GAMBESON = mirror_x([(0.0, 0.33), (0.07, 0.39), (0.2, 0.37), (0.33, 0.27), (0.45, 0.12), (0.49, 0.0), (0.43, -0.05),
                     (0.35, 0.06), (0.21, 0.14), (0.2, -0.1), (0.23, -0.34), (0.03, -0.36), (0.0, -0.3)])


def padded_vest(coll):
    """a padded vest laid out: a quilted gambeson, sleeves spread, sewn in long channels, tied down the front"""
    b = Builder("padded_vest")
    b.add(slab(smooth_outline(GAMBESON, 2), depth=0.008, bevel=0.012, res=2), "Padding")
    z = 0.041                                                       # (a slab stands 2 x (depth + bevel) high)
    segs = [((x, 0.3 - 0.02 * abs(x) / 0.2), (x * 1.05, -0.32)) for x in (-0.15, -0.09, -0.03, 0.03, 0.09, 0.15)]
    segs += [((0.22 * sx, 0.13), (0.43 * sx, 0.04)) for sx in (-1, 1)] + [((0.24 * sx, 0.19), (0.41 * sx, 0.1)) for sx in (-1, 1)]
    segs += [((-0.19, -0.1), (0.19, -0.1))]
    lines_on(b, segs, z, "PaddingDark", 0.0035)
    for k in range(4):                                              # the ties down the front
        y = 0.24 - k * 0.12
        b.add(tube([Vector((-0.016, y, z + 0.002)), Vector((0.0, y - 0.006, z + 0.004)), Vector((0.016, y, z + 0.002))], 0.0025, ring=4, closed=False), "Cord")
    return b.finish(coll)


HAUBERK = mirror_x([(0.0, 0.3), (0.08, 0.36), (0.2, 0.35), (0.32, 0.26), (0.42, 0.13), (0.45, 0.04), (0.39, 0.0),
                    (0.31, 0.08), (0.21, 0.14), (0.21, -0.12), (0.26, -0.4), (0.03, -0.41), (0.0, -0.33)])


def chainmail(coll):
    """chainmail laid out: the hauberk with its wide sleeves, the coif at its neck, the quilted jack's hem showing under
    it; a row of rings along the hem and the cuffs"""
    b = Builder("chainmail")
    jack = [(x * 1.02, y - 0.03) for x, y in GAMBESON]
    b.add(slab(smooth_outline(jack, 2), depth=0.004, bevel=0.01, res=2), "Padding")
    b.add(slab(smooth_outline(HAUBERK, 2), depth=0.004, bevel=0.01, res=2), "Mail", Matrix.Translation(Vector((0, 0, 0.012))))
    coif = smooth_outline([(-0.13, 0.27), (0.13, 0.27), (0.16, 0.36), (0.12, 0.46), (0.0, 0.5), (-0.12, 0.46), (-0.16, 0.36)], 2)
    b.add(slab(coif, depth=0.006, bevel=0.012, res=2), "Mail", Matrix.Translation(Vector((0, 0.01, 0.022))))
    z = 0.0412
    for k in range(22):                                             # rings along the hem
        x = -0.24 + 0.48 * k / 21
        b.add(torus(0.007, 0.0016, seg=8, ring=3), "Steel", Matrix.Translation(Vector((x, -0.395 + 0.01 * abs(x) / 0.24, z))))
    for sx in (-1, 1):                                              # and the cuffs
        for k in range(5):
            t = k / 4
            p_ = Vector((0.45 * sx, 0.04, 0)).lerp(Vector((0.39 * sx, 0.0, 0)), t)
            b.add(torus(0.007, 0.0016, seg=8, ring=3), "Steel", Matrix.Translation(Vector((p_.x, p_.y, z))))
    return b.finish(coll)


ROBE = mirror_x([(0.0, 0.32), (0.06, 0.38), (0.18, 0.37), (0.3, 0.29), (0.44, 0.15), (0.54, 0.02), (0.5, -0.06),
                 (0.38, -0.02), (0.3, 0.06), (0.2, 0.1), (0.21, -0.2), (0.3, -0.78), (0.0, -0.8)])


def robe(name, m, trim, sash, clasp=None):
    def f(coll):
        """a robe laid out: long to the ankle, wide sleeves spread, a sash at the waist; trim along the hem, the cuffs
        and the opening down the front"""
        b = Builder(name)
        b.add(slab(smooth_outline(ROBE, 2), depth=0.004, bevel=0.01, res=2), m)
        z = 0.0296                                                  # (just above the robe: it stands 0.028)
        if trim:
            lines_on(b, [((-0.29, -0.765), (0.29, -0.765))], z, trim, 0.03)                    # the hem
            for sx in (-1, 1):
                lines_on(b, [((0.535 * sx, 0.03), (0.49 * sx, -0.05))], z, trim, 0.03)         # the cuffs
            lines_on(b, [((0.0, 0.31), (0.0, -0.78))], z, trim, 0.025)                        # the front's edge
            lines_on(b, [((-0.06, 0.37), (0.0, 0.3)), ((0.06, 0.37), (0.0, 0.3))], z, trim, 0.02)   # the collar
        b.add(slab([(-0.215, -0.03), (0.215, -0.03), (0.215, 0.03), (-0.215, 0.03)], 0.002, 0.005, 2), sash,
              Matrix.Translation(Vector((0, -0.16, z - 0.006))))
        for sx in (-1, 1):                                          # the sash's ends hanging from the knot
            b.add(slab(smooth_outline([(-0.02, 0.0), (0.02, 0.0), (0.03, -0.22), (-0.01, -0.23)], 1), 0.002, 0.004),
                  sash, Matrix.Translation(Vector((0.03 * sx, -0.17, z))) @ Matrix.Rotation(0.12 * sx, 4, "Z"))
        if clasp:
            b.add(cyl(0.022, 0.006, seg=14), clasp, Matrix.Translation(Vector((0.0, -0.16, z + 0.006))))
        return b.finish(coll)
    return f


def cloth_gloves(coll):
    """plain wool gloves, their wrist wraps wound round the cuffs"""
    b = Builder("cloth_gloves")
    glove_pair(b, "RobeUndyed", "Linen")
    return b.finish(coll)


def iron_gauntlets(coll):
    """plated gauntlets over mail gloves: steel lames over the backs of the hands, flared steel cuffs"""
    b = Builder("iron_gauntlets")
    glove_pair(b, "Mail", "Steel", plates="Steel")
    return b.finish(coll)


def cloth_boots(coll):
    """felted shoes with soft soles"""
    b = Builder("cloth_boots")
    boot_pair(b, "Felt", "WoolDark", low=True)
    return b.finish(coll)


def heavy_boots(coll):
    """iron-shod boots: dark leather, steel plates over the shins"""
    b = Builder("heavy_boots")
    boot_pair(b, "BootDark", "IronTrim", shaft_plate="Steel")
    return b.finish(coll)



# the world models of the worn armour and the gold, built with the rest (items_build.ITEMS). The armour slabs were the
# mocks: since 2026-10-27 the armour on the ground is the worn garments laid down (armour_drop.py), so only the slabs'
# builders stay here (SLAB_ARMOUR, not built) -- never over the new IT_<armour>.fbx
SLAB_ARMOUR = [leather, studded_leather, platemail, padded_vest, chainmail,
               robe("apprentice_robe", "RobeUndyed", None, "Rope"), robe("journeyman_robe", "RobeBlue", "RobeCream", "RobeCream"),
               robe("magister_robe", "RobeViolet", "Gold", "Gold", clasp="Gold"),
               leather_gloves, cloth_gloves, iron_gauntlets, leather_boots, cloth_boots, heavy_boots]
WORLD_ARMOUR = [coin_pile("gold_few", 5, 0.045, 1), coin_pile("gold_some", 16, 0.07, 2), coin_pile("gold_heap", 40, 0.1, 3)]


MORE = [apple, cabbage, carrot, onion, pumpkin, turnip, cheese, eggs, honey,
        meat_slab("raw_meat", 0.16, 0.05, 0.11, 21), meat_slab("bear_meat", 0.2, 0.08, 0.14, 22),
        meat_slab("rhino_meat", 0.2, 0.07, 0.13, 23, bone=True), wolf_meat, venison, mammoth_meat,
        smoked_fish, rat_skewer, flask("potion_flask"), flask("potion_big", True), tall_bottle, vial, scroll, scroll_rod, scroll_open, scroll_singed,
        goblin_herb, wild_garlic, yarrow, fireweed, ghostpipe, cotton, sheaf("arrows", False), sheaf("arrows_cold", True), bolts,
        cloth_sack, leather_backpack, cage_key, chitin_plate, ring("garrick_signet", "Gold", True), ring("silver_ring", "Silver", False),
        keeper_whistle, mammoth_tusk, orc_tusk, rat_fang,
        rhino_horn, mammoth_wool, orc_silver, pewter_tankard,
        gland("plague_gland", "Plague", 41), gland("venom_gland", "Venom", 42), rat_tail, spider_silk,
        pelt("bear_pelt", False, "fur"), pelt("wolf_pelt", True, "fur"), pelt("deer_hide", True, "hide"), pelt("rhino_hide", False, "hide"),
        cured_leather, cloth, wool, lumps("coal", "VK_Coal", 110), lumps("iron_ore", "VK_OreIronChunk", 120),
        lumps("silver_ore", "VK_OreSilverChunk", 130), lumps("gold_ore", "VK_Rock", 140, "Gold"), garnet, sapphire, ruby, heartwood, timber, stag_antler, stone]


ITEMS = [silver_necklace, gold_necklace, bear_claw_necklace, silk_venom_cord, goblin_fetish, guild_seal,
         tusk_necklace, pilgrims_pendant, silver_locket, berries] + MORE + TOMES_ALL + WORLD_ARMOUR


# the real longest side (metres) of the models first built at a handy size, scaled to it after building (2026-10-22, the
# user: "small objects like daggers should be smaller than two handed weapons ... a rat tusk should be smaller than the
# orc one, while the mammoth tusk should barelly fit the square": the icons are framed by real size, so it must be real)
SIZE = {
    "mammoth_tusk": 2.2, "rhino_horn": 0.7, "orc_tusk": 0.12, "rat_fang": 0.035, "stag_antler": 0.9,
    "mammoth_meat": 0.7, "venison": 0.35, "rhino_meat": 0.35, "bear_meat": 0.3, "raw_meat": 0.2, "wolf_meat": 0.2,
    "bear_pelt": 0.55, "rhino_hide": 0.6, "wolf_pelt": 0.5, "deer_hide": 0.5, "cured_leather": 0.4, "cloth": 0.4,
    "timber": 0.9, "heartwood": 0.3, "stone": 0.4, "spider_silk": 0.2, "mammoth_wool": 0.4, "chitin_plate": 0.35,
    "cloth_sack": 0.5, "leather_backpack": 0.5, "wool": 0.25, "smoked_fish": 0.3,
}


def build():
    """the items in scene Items, laid out in a row (front to -Y) for a look"""
    sc = bpy.data.scenes.get("Items") or bpy.data.scenes.new("Items")
    for w in bpy.context.window_manager.windows:                    # (on screen, for a look)
        w.scene = sc
    for ob in list(sc.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for me in [m for m in bpy.data.meshes if m.users == 0]:
        bpy.data.meshes.remove(me)
    coll = sc.collection
    made = []
    for i, f in enumerate(ITEMS):
        ob = f(coll)
        want = SIZE.get(ob.name[3:])
        if want:                                                    # to its real size (about the bottom of its box)
            lo = Vector([min(v.co[k] for v in ob.data.vertices) for k in range(3)])
            hi = Vector([max(v.co[k] for v in ob.data.vertices) for k in range(3)])
            ob.data.transform(Matrix.Scale(want / max(hi - lo), 4))
        ob.location = Vector(((i % 10) * 0.32, 0, -(i // 10) * 0.34))
        made.append(ob)
    print("built", ", ".join(f"{o.name} {len(o.data.polygons)} faces" for o in made))
    return made


def export():
    """one FBX a item into MedievalSetting (Assets/Game/Items/Models), at the origin"""
    import os
    os.makedirs(OUT, exist_ok=True)
    sc = bpy.data.scenes["Items"]
    for ob in [o for o in sc.objects if o.name.startswith("IT_")]:
        keep = ob.location.copy()
        ob.location = (0, 0, 0)
        bpy.ops.object.select_all(action="DESELECT")
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        bpy.ops.export_scene.fbx(filepath=f"{OUT}/{ob.name}.fbx", use_selection=True, apply_scale_options="FBX_SCALE_UNITS",
                                 axis_forward="-Z", axis_up="Y", mesh_smooth_type="FACE", add_leaf_bones=False, bake_anim=False)
        ob.location = keep
    print("exported to", OUT)
