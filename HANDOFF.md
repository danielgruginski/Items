# Items: handoff

Where things stand (2026-10-27) and what a next session needs to know. README.md has the overview.

## State

- 116 item models in MedievalSetting `Assets/Game/Items/Models` (IT_<id>.fbx): 101 from `items_build.py`, 15 armour
  pieces from `armour_drop.py`. Checked in to the game's Plastic repository as cs:97.
- 203 icons rendered by `ItemIconsMenu` (Unity: Game/Items/Render Icons), with glow masks for magic items.
- The armour models only matter for the itch pack today: armour does not normally drop in the game. They are wired up
  anyway (every item has a world model: 328).
- The itch pack (itch/4_Items, built by itch/_tools/stage.sh `items`) ships these models, their materials and the icons.

## Rebuilding

- Other items: open Blender, `exec(open(r"E:/Unity/Projects/GameArtGeneration/Items/src/items_build.py").read());
  build(); export()`. Then in Unity: Game/Items/Prepare Icon Models (remaps the IT_/VK_ materials), Render Icons,
  World Models.
- Armour: headless, one item at a time (`armour_drop.py <item> export`); copy `textures/T_IT_<item>.png` to
  `Assets/Game/Items/Models/Textures`, then Prepare Icon Models makes `IT_Armour_<item>.mat` from it.
- `items_build.py`'s old flat armour slabs (`SLAB_ARMOUR`) are not built any more, so they never overwrite the new
  armour FBX files.

## Gotchas

- Body armour is pressed flat by code, not simulated: a cloth simulation pushed the cuirass through the coat and blew the
  buckles and hood apart.
- The bake copies each garment's material, swaps its `hum_color` attribute node for a fixed colour, and emits the base
  colour. Removing the meshes' CORNER FLOAT2 attributes deletes the UV map too (every render came out black).
- Platemail is the roughest of the set: steel can't fold, so it's laid down whole.
