"""Armour on the ground, made from the worn garments (2026-10-27, Daniel: "Remake then from the worn pieces"; the leather
first, then "Looks good. Do the other 12 the same way"): the Humans pipeline's garments (humans.blend, one build at rest)
- body armour: laid on its back, sleeves swung, pressed flat with soft folds (every layer stays over the one under it; a
  cloth simulation pushed the cuirass through the coat and blew the buckles and the hood apart, 2026-10-27); plate is
  rigid: laid, not pressed, its arms let down to the ground
- gloves and gauntlets: the pair split, each laid on its broad side, side by side
- boots and shoes: the pair split, one standing, one fallen on its side
then the garments' own materials (Humans/Cloth and Humans/Plate maths, each garment in the game's colour for it) baked
into one plain texture over a fresh UV, with a little ground AO for the folds. Replaces items_build's flat WORLD_ARMOUR
slabs.

Headless (the live Blender may hold another session's file):
    blender.exe -b --factory-startup --python Items/src/armour_drop.py -- <item> [export] [norender]
Writes blender/armour_<item>.blend (the result beside the old slab, a camera), renders/armour_<item>_*.png,
textures/T_IT_<item>.png and, with 'export', the FBX into MedievalSetting's item models (IT_<item>.fbx; its material
IT_Armour_<item>, which ItemIconsMenu.PrepareModels makes from the texture).
"""
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

ROOT = "E:/Unity/Projects/GameArtGeneration/Items"
HUMANS = "E:/Unity/Projects/GameArtGeneration/Humans/blender/humans.blend"
PATTERNS = "E:/Unity/Projects/GameArtGeneration/Humans/export/Textures"
OUT = "E:/Unity/Projects/MedievalSetting/Assets/Game/Items/Models"
BUILD = "MStrong"
TEX = 512


def srgb(h):
    """'#rrggbb' -> linear rgb (the game passes sRGB hex to the shader as a colour)"""
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


# the game's colours (MedievalSetting HumanActor.ArmourColour by Humans hum_faces.armour_group; the robes' hum_robe
# SET_COLOURS; gloves and boots the item's own look colour)
LEATHER, PLATES, PADDING, STEEL = "#4a2e1a", "#5a3a22", "#8c7a62", "#74777c"
OXBLOOD, BLACKENED = "#5c2418", "#2e1c12"                                # Studded Leather's leather; the dark drop's
STUDDED = ["StuddedCoat", "Jerkin", "Pauldrons", "Hood"]

# per item: mode (body: laid + pressed; plate: laid; pair: gloves flat side by side; boots: one up, one fallen), the
# garments worn for it with their colours (gloves under the cuffs: the icon's hand; "Garment:_L1" its own LOD), the LOD, its turn on the ground (degrees about Z), how far each sleeve swings
# in from the A pose (degrees, + toward the hem; left, right), the folds' seed
ITEMS = {
    "leather": dict(garments={"Coat": LEATHER, "Cuirass": PLATES, "Hood": LEATHER}),
    "studded_leather": dict(garments=dict(zip(STUDDED, (OXBLOOD, PLATES, PLATES, OXBLOOD)))),
    "blackened_studded_leather": dict(garments=dict(zip(STUDDED, (BLACKENED, PLATES, PLATES, BLACKENED)))),
    "padded_vest": dict(garments={"Gambeson": PADDING, "PaddedCoif": PADDING}, turn=-10, sleeves=(18, -20), seed=5),
    "chainmail": dict(garments={"Gambeson": PADDING, "Hauberk": STEEL, "MailCoif": STEEL}, turn=8, sleeves=(24, -8),
                      seed=7, metal=(0.35, 0.35)),
    "platemail": dict(mode="plate", garments={"PlateCuirass": STEEL, "PlateGorget": STEEL, "PlatePauldrons": STEEL,
                                              "PlateArms": STEEL}, turn=-14, sleeves=(20, -6), metal=(0.55, 0.45)),
    "apprentice_robe": dict(garments={"Robe": "#6e6150", "RobeTrim": "#4a3e32"}, turn=10, sleeves=(22, -14), seed=11),
    "journeyman_robe": dict(garments={"Robe": "#2e4c80", "RobeTrim": "#d4c9a6"}, turn=-8, sleeves=(14, -24), seed=13),
    "magister_robe": dict(garments={"Robe": "#47235e", "RobeTrim": "#d4a83a"}, turn=14, sleeves=(26, -10), seed=17),
    "cloth_gloves": dict(mode="pair", garments={"Gloves:_L1": "#8a7a5e", "Bracers": "#8a7a5e"}, lod="", turn=20),
    "leather_gloves": dict(mode="pair", garments={"Gloves:_L1": "#5a3a22", "Bracers": "#5a3a22"}, lod="", turn=-25),
    "iron_gauntlets": dict(mode="pair", garments={"Gloves:_L1": "#8a8a8e", "PlateGauntlets": "#8a8a8e"}, lod="",
                           turn=15, metal=(0.55, 0.45)),
    "cloth_boots": dict(mode="boots", garments={"Shoes": "#6a5a44"}, turn=-20),
    "leather_boots": dict(mode="boots", garments={"Boots": "#4a2e1a"}, turn=15),
    "heavy_boots": dict(mode="boots", garments={"Boots": "#2a2826"}, turn=-30),
}
DEFAULTS = dict(mode="body", lod="_L1", turn=12, sleeves=(28, -12), seed=3, metal=(0.0, 0.15))
PRESS = 0.15        # the laid outfit's depth kept (front over back: 38 cm -> 6 cm)
FOLDS = ((0.022, 6.0), (0.014, 2.4))   # soft folds: (height m, frequency 1/m), on the top layers, none on the ground


def spec_of(item):
    return dict(DEFAULTS, **ITEMS[item])


def box(ob, tag=""):
    """(debug) the object's bounds, rounded"""
    vs = [ob.matrix_world @ v.co for v in ob.data.vertices]
    lo = [round(min(v[k] for v in vs), 3) for k in range(3)]
    hi = [round(max(v[k] for v in vs), 3) for k in range(3)]
    print(f"  {tag} {ob.name}: {lo} .. {hi}")


def clear():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)


def append(names):
    """the garments at rest, unparented and unrigged, without the helper vertices (hum_helpers: no faces)"""
    with bpy.data.libraries.load(HUMANS) as (src, dst):
        missing = [n for n in names if n not in src.objects]
        if missing:
            raise RuntimeError(f"not in humans.blend: {missing}")
        dst.objects = list(names) + ["HumanRig"]
    sc = bpy.context.scene
    for ob in dst.objects:
        sc.collection.objects.link(ob)
    bpy.context.view_layer.update()
    rig = bpy.data.objects["HumanRig"]
    out = []
    for n in names:
        ob = bpy.data.objects[n]
        ob.hide_render = ob.hide_viewport = False                        # (the other builds' garments are hidden there)
        ob.hide_set(False)
        mw = ob.matrix_world.copy()
        for m in list(ob.modifiers):
            ob.modifiers.remove(m)
        ob.parent = None
        ob.data = ob.data.copy()
        ob.data.transform(mw)
        ob.matrix_world = Matrix()
        ob.vertex_groups.clear()
        if ob.data.shape_keys:
            ob.shape_key_clear()
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        bm.to_mesh(ob.data)
        bm.free()
        out.append(ob)
    bpy.data.objects.remove(rig, do_unlink=True)
    for img in bpy.data.images:                                          # the patterns, if the library's paths miss
        if img.source == "FILE" and not img.has_data:
            p = f"{PATTERNS}/{img.name.split('.')[0]}.png"
            if os.path.exists(p):
                img.filepath = p
                img.reload()
    return out


def colour_materials(ob, hexcol):
    """the garment's own materials (Humans/Cloth, Humans/Plate), copied with its colour in place of the hum_color
    attribute and their base colour emitted (for the bake); an image node, active, in each"""
    col = (*srgb(hexcol), 1.0)
    for slot in ob.material_slots:
        m = slot.material.copy()
        m.name = f"BAKE_{ob.name}"
        nt = m.node_tree
        for n in list(nt.nodes):
            if n.type == "ATTRIBUTE" and n.attribute_name == "hum_color":
                rgb = nt.nodes.new("ShaderNodeRGB")
                rgb.outputs[0].default_value = col
                for out in n.outputs:
                    for link in list(out.links):
                        nt.links.new(rgb.outputs[0], link.to_socket)
                nt.nodes.remove(n)
        bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
        em = nt.nodes.new("ShaderNodeEmission")
        base = bsdf.inputs["Base Color"]
        if base.links:
            nt.links.new(base.links[0].from_socket, em.inputs["Color"])
        else:
            em.inputs["Color"].default_value = base.default_value
        out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output)
        nt.links.new(em.outputs[0], out.inputs["Surface"])
        img = nt.nodes.new("ShaderNodeTexImage")
        img.name = "BakeTarget"
        nt.nodes.active = img
        slot.material = m


def swing_sleeves(obs, degrees):
    """each sleeve turned about its shoulder (at rest, front -Y, up +Z: in the XZ plane), blended in past the shoulder
    so the cloth doesn't tear; + swings it down toward the hem"""
    pts = [v.co for ob in obs for v in ob.data.vertices]
    top = max(p.z for p in pts)
    for side, deg in zip((1, -1), degrees):                              # +X is the wearer's left (front -Y)
        sx, sz = 0.17 * side, top - 0.25                                 # the shoulder joint, roughly
        for ob in obs:
            for v in ob.data.vertices:
                d = (v.co.x - sx) * side
                if d <= 0:
                    continue
                w = min(1.0, d / 0.1) ** 2 * (3 - 2 * min(1.0, d / 0.1))     # smoothstep over the first 10 cm
                a = math.radians(deg) * w * -side
                x, z = v.co.x - sx, v.co.z - sz
                v.co.x = sx + x * math.cos(a) - z * math.sin(a)
                v.co.z = sz + x * math.sin(a) + z * math.cos(a)
            ob.data.update()


def bounds(obs):
    pts = [v.co for ob in obs for v in ob.data.vertices]
    return (Vector([min(p[k] for p in pts) for k in range(3)]), Vector([max(p[k] for p in pts) for k in range(3)]))


def to_ground(obs, centre=True):
    lo, hi = bounds(obs)
    T = Matrix.Translation(Vector((-(lo.x + hi.x) / 2 if centre else 0, -(lo.y + hi.y) / 2 if centre else 0, -lo.z)))
    for ob in obs:
        ob.data.transform(T)


def lay(obs, turn):
    """on its back (front up, head to +Y), turned a little; bottom on the ground"""
    R = Matrix.Rotation(math.radians(turn), 4, "Z") @ Matrix.Rotation(math.radians(-90), 4, "X")
    for ob in obs:
        ob.data.transform(R)
    to_ground(obs)


def press(obs, seed):
    """pressed flat as cloth lies: the depth scaled (so every layer stays over the one under it: front over back, the
    cuirass over the coat), soft folds rising with the height (the back panel stays flat on the ground)"""
    from mathutils import noise
    zmax = max(v.co.z for ob in obs for v in ob.data.vertices)
    for ob in obs:
        for v in ob.data.vertices:
            x, y, z = v.co
            h = z / zmax
            fold = sum(a * noise.noise(Vector((x * f, y * f, seed + i * 7.3))) for i, (a, f) in enumerate(FOLDS))
            v.co.z = z * PRESS + fold * h + 0.002
        ob.data.update()


def join(obs):
    with bpy.context.temp_override(active_object=obs[0], selected_editable_objects=obs):
        bpy.ops.object.join()
    return obs[0]


def halves(ob):
    """a pair garment (both hands, both feet in one mesh) split into its left (+X) and right halves"""
    out = []
    for side in (1, -1):
        h = ob.copy()
        h.data = ob.data.copy()
        bpy.context.scene.collection.objects.link(h)
        bm = bmesh.new()
        bm.from_mesh(h.data)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.x * side < 0], context="VERTS")
        bm.to_mesh(h.data)
        bm.free()
        h.name = f"{ob.name}_{'L' if side > 0 else 'R'}"
        out.append(h)
    bpy.data.objects.remove(ob, do_unlink=True)
    return out


def flat_side(ob, flip):
    """laid on its broadest side: its long axis along X, its thinnest across the ground (the principal axes)"""
    P = np.array([v.co[:] for v in ob.data.vertices])
    c = P.mean(0)
    w, V = np.linalg.eigh(np.cov((P - c).T))
    V = V[:, ::-1]                                                       # long, mid, thin
    if np.linalg.det(V) < 0:
        V[:, 2] *= -1
    R = Matrix([list(V[:, 0]), list(V[:, 1]), list(V[:, 2])]).to_4x4()
    ob.data.transform(R @ Matrix.Translation(-Vector(c)))
    if flip:
        ob.data.transform(Matrix.Rotation(math.pi, 4, "X"))


def side_by_side(pieces, gap, turns, stagger):
    """the pieces next to each other along X, each turned a little, on the ground"""
    for ob, t in zip(pieces, turns):
        ob.data.transform(Matrix.Rotation(math.radians(t), 4, "Z"))
        to_ground([ob])
    x = 0.0
    for i, ob in enumerate(pieces):
        lo, hi = bounds([ob])
        ob.data.transform(Matrix.Translation((x - lo.x, stagger * (1 if i % 2 else -1), 0)))
        x += hi.x - lo.x + gap


def pair(obs, spec):
    """gloves and gauntlets: each hand on its broad side, the two side by side and a little askew"""
    left, right = halves(join(obs))
    flat_side(left, False)
    flat_side(right, True)
    side_by_side([left, right], 0.03, (90 + 8, 90 - 14), 0.03)
    return [left, right]


def boots(obs, spec):
    """boots and shoes: the left one standing, the right one fallen on its outer side"""
    left, right = halves(join(obs))
    right.data.transform(Matrix.Rotation(math.radians(-90), 4, "Y"))     # (its outer side, -X, down)
    side_by_side([left, right], 0.06, (-8, 28), 0.05)
    return [left, right]


def drop(item):
    spec = spec_of(item)
    names = {}
    for key, col in spec["garments"].items():
        g, _, lod = key.partition(":")
        names[f"Cloth_{g}_{BUILD}{lod or spec['lod']}"] = col
    obs = append(list(names))
    for ob in obs:
        colour_materials(ob, names[ob.name])
    if spec["mode"] in ("body", "plate"):
        swing_sleeves(obs, spec["sleeves"])
        lay(obs, spec["turn"])
        if spec["mode"] == "body":
            press(obs, spec["seed"])
        else:                                                            # rigid: the arms let down onto the ground
            for ob in obs:
                if "Arms" in ob.name:
                    to_ground([ob], centre=False)
    else:
        obs = (pair if spec["mode"] == "pair" else boots)(obs, spec)
        R = Matrix.Rotation(math.radians(spec["turn"]), 4, "Z")
        for ob in obs:
            ob.data.transform(R)
        to_ground(obs)
    main = join(obs)
    main.name = "IT_" + item
    to_ground([main])
    box(main, "laid")
    print("joined:", len(main.data.polygons), "faces,", sum(len(p.vertices) - 2 for p in main.data.polygons), "tris")
    return main


# ------------------------------------------------------------------ the bake

def ground():
    me = bpy.data.meshes.new("Ground")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=2.0)
    bm.to_mesh(me)
    ob = bpy.data.objects.new("Ground", me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def bake_into(ob, img, kind):
    for m in ob.data.materials:
        m.node_tree.nodes["BakeTarget"].image = img
        m.node_tree.nodes.active = m.node_tree.nodes["BakeTarget"]
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob], selected_editable_objects=[ob]):
        bpy.ops.object.bake(type=kind)


def bake(ob, item):
    spec = spec_of(item)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 16
    me = ob.data
    bake_uv = me.uv_layers.new(name="UVBake")
    me.uv_layers.active = bake_uv
    for o in bpy.context.view_layer.objects:
        o.select_set(o == ob)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.01)
    bpy.ops.object.mode_set(mode="OBJECT")
    me.uv_layers["UVMap"].active_render = True                          # the materials read the pattern's UV by name
    colour = bpy.data.images.new(f"T_IT_{item}", TEX, TEX, alpha=False)
    sc.render.bake.margin = 8
    sc.render.bake.use_clear = True
    sc.render.bake.target = "IMAGE_TEXTURES"
    bake_into(ob, colour, "EMIT")
    g = ground()                                                         # ground AO for the folds (the ground back for it)
    ao = bpy.data.images.new(f"AO_{item}", TEX, TEX, alpha=False)
    sc.world = sc.world or bpy.data.worlds.new("World")
    sc.cycles.samples = 64
    bake_into(ob, ao, "AO")
    bpy.data.objects.remove(g, do_unlink=True)
    c = np.array(colour.pixels[:]).reshape(-1, 4)
    a = np.array(ao.pixels[:]).reshape(-1, 4)[:, :1]
    c[:, :3] *= 0.55 + 0.45 * a
    colour.pixels[:] = c.ravel()
    os.makedirs(f"{ROOT}/textures", exist_ok=True)
    colour.filepath_raw = f"{ROOT}/textures/T_IT_{item}.png"
    colour.file_format = "PNG"
    colour.save()
    # the shipped mesh: one UV (the bake's), the colour as its only material
    for n in [u.name for u in me.uv_layers if u.name != "UVBake"]:    # (by name: removing one moves the others)
        me.uv_layers.remove(me.uv_layers[n])
    me.uv_layers["UVBake"].name = "UVMap"
    for n in [a_.name for a_ in me.color_attributes]:
        me.color_attributes.remove(me.color_attributes[n])
    final = bpy.data.materials.new(f"IT_Armour_{item}")
    final.use_nodes = True
    bsdf = next(n for n in final.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    t = final.node_tree.nodes.new("ShaderNodeTexImage"); t.image = colour
    final.node_tree.links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Metallic"].default_value = spec["metal"][0]
    bsdf.inputs["Roughness"].default_value = 1 - spec["metal"][1]
    me.materials.clear()
    me.materials.append(final)
    for p in me.polygons:
        p.material_index = 0
    print("baked", colour.filepath_raw)


# ------------------------------------------------------------------ a look

def old_slab(item, at):
    path = f"{OUT}/IT_{'studded_leather' if item == 'blackened_studded_leather' else item}.fbx"
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path, axis_forward="-Z", axis_up="Y")
    new = [o for o in bpy.data.objects if o not in before]
    for o in new:
        o.location.x += at
        o.name = "OLD_" + o.name
    return new


def review(ob, item):
    sc = bpy.context.scene
    lo, hi = bounds([ob])
    size = max(hi.x - lo.x, hi.y - lo.y, 0.3)
    old_slab(item, -(size + 0.15))
    centre = Vector((-(size + 0.15) / 2, 0, 0.03))
    g = ground()
    g.scale = (3, 2, 1)
    gm = bpy.data.materials.new("GroundGrey")
    gm.use_nodes = True
    next(n for n in gm.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Base Color"].default_value = (0.16, 0.15, 0.13, 1)
    g.data.materials.append(gm)
    w = sc.world = bpy.data.worlds.new("Drop")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.6
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 3.5
    sun.rotation_euler = (math.radians(40), 0, math.radians(30))
    sc.collection.objects.link(sun)
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    sc.cycles.samples = 48
    sc.cycles.use_denoising = True
    os.makedirs(f"{ROOT}/renders", exist_ok=True)
    # close up, and the game camera's distance (22 m) with a narrow lens: a crop of the game view, about 2 m across
    for tag, pitch, dist, fov in (("close", 50, 3.0 * size + 0.3, 40), ("game", 60, 22.0, 6.5)):
        cam.data.angle = math.radians(fov)
        d = Vector((0, -math.cos(math.radians(pitch)), math.sin(math.radians(pitch)))) * dist
        cam.location = centre + d
        cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = f"{ROOT}/renders/armour_{item}_{tag}.png"
        bpy.ops.render.render(write_still=True)
        print("render", sc.render.filepath)


def export(ob, item):
    for o in bpy.data.objects:
        o.select_set(o == ob)
    bpy.context.view_layer.objects.active = ob
    keep = ob.location.copy()
    ob.location = (0, 0, 0)
    bpy.ops.export_scene.fbx(filepath=f"{OUT}/IT_{item}.fbx", use_selection=True, apply_scale_options="FBX_SCALE_UNITS",
                             axis_forward="-Z", axis_up="Y", mesh_smooth_type="FACE", add_leaf_bones=False, bake_anim=False,
                             path_mode="STRIP")
    ob.location = keep
    print("exported", f"{OUT}/IT_{item}.fbx")


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["leather"]
    item = args[0]
    sc = bpy.context.scene
    sc.name = "Drop"
    clear()
    ob = drop(item)
    bake(ob, item)
    os.makedirs(f"{ROOT}/blender", exist_ok=True)
    if "export" in args:
        export(ob, item)
    if "norender" not in args:
        review(ob, item)
    try:                                                                 # (the garments' orphan shape keys: harmless)
        bpy.ops.wm.save_as_mainfile(filepath=f"{ROOT}/blender/armour_{item}.blend")
    except RuntimeError as e:
        print("save:", e)
    print("saved", f"{ROOT}/blender/armour_{item}.blend")
