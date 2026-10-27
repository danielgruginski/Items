using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace MedievalGame.EditorTools
{
    /// <summary>
    /// Item icons rendered from the items' own models (2026-10-21, the user on the trial sheet: "these icons are really
    /// great! You can wire them in"): every weapon, thrown weapon and shield with a model is put alone in a preview scene
    /// (the open scenes are not touched), lit from the upper left and shot by an orthographic camera onto a transparent
    /// 128 px square -- a long piece diagonal (its longest side up, turned 25 degrees to show its depth, then laid 45 degrees,
    /// hilt or haft to the lower left), a shield face on (its thinnest side to the camera, its painted face, its point
    /// down). Saved as sprites in Items/Icons (one a model, named after the first item using it) and set as the
    /// <see cref="ItemDefinition.icon"/> of every item with that model (an enchanted copy shares its plain one's). The HUD
    /// shows an icon where it has one (<see cref="ItemGlyph"/>), the letters otherwise. Run again after new models.
    /// Since 2026-10-21 (the user: "new icons ... for the armors, and the plants"; "For wild berries, however, it is not
    /// the bush, but the berry that is the item"; "You might need to create models for some items, like the necklaces")
    /// also the gathered plants from the kit's own plant models standing upright (<see cref="Props"/>), and the berries
    /// and the nine necklaces from models made for their icons alone (GameArtGeneration/Items, Items/Models: laid face on
    /// like a shield, their IT_ materials remapped to this project's by <see cref="PrepareModels"/>).
    /// </summary>
    public static class ItemIconsMenu
    {
        const string Dir = "Assets/Game/Items/Icons";
        const int Size = 128;

        [MenuItem("Game/Items/Render Icons")]
        public static void RenderMenu() => Debug.Log(Render());

        const string Kit = "Packages/com.danielgruginski.medievalkit/Generated/Prefabs/";
        const string Models = "Assets/Game/Items/Models";

        /// <summary>items whose icon is a model of their own, not a weapon's or shield's: the mushrooms (the kit's), the
        /// berries and the necklaces (made for the icon: Items/Models). The gathered herbs are picked bunches of their own
        /// (2026-10-22, the user: "Make the plants now"; they were the kit's whole growing plants): IT_&lt;id&gt;</summary>
        static readonly Dictionary<string, string> Props = new Dictionary<string, string>
        {
            ["mushrooms"] = Kit + "VK/Mushrooms/SM_VK_Mushrooms_Brown.prefab",
            ["berries"] = Models + "/IT_berries.fbx",
            ["silver_necklace"] = Models + "/IT_silver_necklace.fbx",
            ["gold_necklace"] = Models + "/IT_gold_necklace.fbx",
            ["bear_claw_necklace"] = Models + "/IT_bear_claw_necklace.fbx",
            ["silk_venom_cord"] = Models + "/IT_silk_venom_cord.fbx",
            ["goblin_fetish"] = Models + "/IT_goblin_fetish.fbx",
            ["guild_seal"] = Models + "/IT_guild_seal.fbx",
            ["tusk_necklace"] = Models + "/IT_tusk_necklace.fbx",
            ["pilgrims_pendant"] = Models + "/IT_pilgrims_pendant.fbx",
            ["silver_locket"] = Models + "/IT_silver_locket.fbx",
            // the second batch (2026-10-21, the user: "keep working on the icons ... You can use stuff from the medieval
            // kit"): the kit's and the weapon kit's own models where there is one, a shared icon model for alike items;
            // any other item with a model of its own id (Items/Models/IT_<id>) takes that (ModelOf)
            ["brass_candlestick"] = Kit + "VKI/Prop/SM_VKI_Prop_Candlestick.prefab",
            ["war_horn"] = "Assets/Weapons/Prefabs/Wpn_WarHorn.prefab", ["chieftain_horn"] = "Assets/Weapons/Prefabs/Wpn_WarHorn.prefab",
            ["potion"] = Models + "/IT_potion_flask.fbx", ["energy_potion"] = Models + "/IT_potion_flask.fbx",
            ["potion_strength"] = Models + "/IT_potion_flask.fbx", ["potion_hawkeye"] = Models + "/IT_potion_flask.fbx",
            ["potion_swiftness"] = Models + "/IT_potion_flask.fbx",
            ["greater_potion"] = Models + "/IT_potion_big.fbx", ["greater_energy_potion"] = Models + "/IT_potion_big.fbx",
            ["potion_invisibility"] = Models + "/IT_potion_tall.fbx", ["potion_ironskin"] = Models + "/IT_potion_tall.fbx",
            ["potion_magus"] = Models + "/IT_potion_tall.fbx", ["elixir_fortitude"] = Models + "/IT_potion_tall.fbx",
        };

        /// <summary>the colours of the icon models' IT_ materials (Blender's names): base, metallic, smoothness</summary>
        static readonly Dictionary<string, (Color c, float metal, float smooth)> Mats = new Dictionary<string, (Color, float, float)>
        {
            ["Silver"] = (new Color(0.82f, 0.83f, 0.86f), 0.5f, 0.6f), ["Gold"] = (new Color(0.95f, 0.72f, 0.28f), 0.5f, 0.6f),
            ["Bronze"] = (new Color(0.68f, 0.46f, 0.24f), 0.45f, 0.5f), ["Pewter"] = (new Color(0.64f, 0.66f, 0.68f), 0.35f, 0.45f),
            ["Leather"] = (new Color(0.36f, 0.22f, 0.12f), 0f, 0.25f), ["Cord"] = (new Color(0.2f, 0.15f, 0.1f), 0f, 0.15f),
            ["Silk"] = (new Color(0.9f, 0.88f, 0.8f), 0f, 0.35f), ["Venom"] = (new Color(0.48f, 0.66f, 0.2f), 0f, 0.7f),
            ["Bone"] = (new Color(0.88f, 0.84f, 0.7f), 0f, 0.3f), ["Horn"] = (new Color(0.55f, 0.45f, 0.34f), 0f, 0.5f),
            ["Ivory"] = (new Color(0.92f, 0.88f, 0.74f), 0f, 0.5f), ["BerryRed"] = (new Color(0.7f, 0.06f, 0.08f), 0f, 0.75f),
            ["BerryDark"] = (new Color(0.24f, 0.05f, 0.22f), 0f, 0.75f), ["Leaf"] = (new Color(0.22f, 0.42f, 0.12f), 0f, 0.3f),
            ["Stem"] = (new Color(0.36f, 0.25f, 0.14f), 0f, 0.2f),
            ["Tint"] = (new Color(0.8f, 0.2f, 0.2f), 0f, 0.8f), ["Glass"] = (new Color(0.78f, 0.86f, 0.86f), 0.1f, 0.85f),
            ["Cork"] = (new Color(0.58f, 0.42f, 0.26f), 0f, 0.1f), ["Egg"] = (new Color(0.93f, 0.87f, 0.75f), 0f, 0.35f),
            ["Honey"] = (new Color(0.88f, 0.56f, 0.1f), 0f, 0.8f), ["Onion"] = (new Color(0.76f, 0.5f, 0.24f), 0f, 0.45f),
            ["Chitin"] = (new Color(0.3f, 0.27f, 0.16f), 0.2f, 0.8f), ["ChitinEdge"] = (new Color(0.55f, 0.36f, 0.13f), 0.05f, 0.6f),
            ["StemGreen"] = (new Color(0.26f, 0.38f, 0.13f), 0f, 0.3f), ["Ghost"] = (new Color(0.94f, 0.94f, 0.96f), 0f, 0.7f),
            ["GhostTip"] = (new Color(0.2f, 0.17f, 0.2f), 0f, 0.5f), ["Husk"] = (new Color(0.38f, 0.25f, 0.13f), 0f, 0.15f),
            ["Cotton"] = (new Color(0.97f, 0.96f, 0.93f), 0f, 0.05f),
            ["Ash"] = (new Color(0.74f, 0.6f, 0.42f), 0f, 0.3f), ["Oak"] = (new Color(0.48f, 0.33f, 0.2f), 0f, 0.3f), ["Steel"] = (new Color(0.6f, 0.61f, 0.64f), 0.85f, 0.65f), ["Rime"] = (new Color(0.45f, 0.75f, 1f), 0.4f, 0.85f),
            ["Frost"] = (new Color(0.85f, 0.94f, 1f), 0f, 0.4f), ["Fletch"] = (new Color(0.8f, 0.78f, 0.72f), 0f, 0.2f),
            ["FletchRed"] = (new Color(0.62f, 0.12f, 0.08f), 0f, 0.2f), ["FletchIce"] = (new Color(0.62f, 0.84f, 1f), 0f, 0.4f),
            ["Padding"] = (new Color(0.55f, 0.48f, 0.38f), 0f, 0.1f), ["PaddingDark"] = (new Color(0.36f, 0.3f, 0.23f), 0f, 0.1f),
            ["Mail"] = (new Color(0.36f, 0.37f, 0.4f), 0.8f, 0.45f), ["RobeUndyed"] = (new Color(0.62f, 0.56f, 0.45f), 0f, 0.1f),
            ["RobeBlue"] = (new Color(0.14f, 0.2f, 0.45f), 0f, 0.15f), ["RobeCream"] = (new Color(0.86f, 0.8f, 0.66f), 0f, 0.15f),
            ["RobeViolet"] = (new Color(0.3f, 0.14f, 0.4f), 0f, 0.15f), ["Felt"] = (new Color(0.42f, 0.35f, 0.26f), 0f, 0.05f),
            ["BootDark"] = (new Color(0.17f, 0.15f, 0.14f), 0f, 0.3f),
            ["Ink"] = (new Color(0.07f, 0.05f, 0.04f), 0f, 0.3f), ["Scorch"] = (new Color(0.4f, 0.25f, 0.12f), 0f, 0.1f), ["Char"] = (new Color(0.05f, 0.045f, 0.04f), 0f, 0.05f), ["RatTail"] = (new Color(0.8f, 0.58f, 0.55f), 0f, 0.35f),
            ["Plague"] = (new Color(0.58f, 0.55f, 0.24f), 0f, 0.6f), ["Wool"] = (new Color(0.92f, 0.9f, 0.84f), 0f, 0.1f),
            ["CheesePaste"] = (new Color(0.98f, 0.9f, 0.58f), 0f, 0.3f), ["CheeseHole"] = (new Color(0.74f, 0.6f, 0.3f), 0f, 0.1f),
            ["WoolBrown"] = (new Color(0.46f, 0.29f, 0.18f), 0f, 0.1f), ["WoolCream"] = (new Color(0.88f, 0.82f, 0.66f), 0f, 0.1f),
            ["SilkSheen"] = (new Color(0.97f, 0.97f, 1f), 0.1f, 0.75f),
            ["WoolDark"] = (new Color(0.28f, 0.16f, 0.09f), 0f, 0.15f), ["WoolRed"] = (new Color(0.5f, 0.29f, 0.15f), 0f, 0.15f),
            ["Linen"] = (new Color(0.92f, 0.87f, 0.74f), 0f, 0.1f),
            ["WoodEnd"] = (new Color(0.84f, 0.67f, 0.45f), 0f, 0.15f), ["WoodRing"] = (new Color(0.66f, 0.48f, 0.3f), 0f, 0.15f),
            ["WoodPith"] = (new Color(0.36f, 0.23f, 0.13f), 0f, 0.1f),
            ["Heart"] = (new Color(0.48f, 0.23f, 0.1f), 0f, 0.2f), ["HeartDark"] = (new Color(0.33f, 0.14f, 0.06f), 0f, 0.2f),
            ["IvoryRoot"] = (new Color(0.55f, 0.4f, 0.22f), 0f, 0.3f), ["IvoryOld"] = (new Color(0.86f, 0.78f, 0.58f), 0f, 0.45f),
            ["RatEnamel"] = (new Color(0.88f, 0.55f, 0.18f), 0f, 0.6f), ["HornDark"] = (new Color(0.24f, 0.19f, 0.15f), 0f, 0.35f),
            ["Fat"] = (new Color(0.94f, 0.88f, 0.75f), 0f, 0.45f), ["Marrow"] = (new Color(0.62f, 0.25f, 0.19f), 0f, 0.4f),
            ["CoverFighter"] = (new Color(0.5f, 0.1f, 0.08f), 0f, 0.3f), ["CoverRogue"] = (new Color(0.17f, 0.16f, 0.18f), 0f, 0.3f),
            ["CoverWizard"] = (new Color(0.15f, 0.18f, 0.52f), 0f, 0.3f), ["CoverRanger"] = (new Color(0.21f, 0.34f, 0.15f), 0f, 0.3f),
            ["CoverCleric"] = (new Color(0.9f, 0.87f, 0.78f), 0f, 0.3f), ["CoverGeneral"] = (new Color(0.43f, 0.27f, 0.14f), 0f, 0.3f),
            ["CoverShade"] = (new Color(0.18f, 0.11f, 0.06f), 0f, 0.25f), ["Pages"] = (new Color(0.92f, 0.87f, 0.72f), 0f, 0.1f),
            ["IronTrim"] = (new Color(0.5f, 0.5f, 0.53f), 0.45f, 0.5f), ["Rope"] = (new Color(0.66f, 0.55f, 0.36f), 0f, 0.1f), ["LeatherCured"] = (new Color(0.54f, 0.33f, 0.17f), 0f, 0.35f),
        };

        /// <summary>the icon models' materials (Items/Models/Materials, URP Lit) and every IT_ model's import remapped to them</summary>
        public static string PrepareModels()
        {
            string dir = Models + "/Materials";
            Directory.CreateDirectory(dir);
            var lit = Shader.Find("Universal Render Pipeline/Lit");
            var mats = new Dictionary<string, Material>();
            foreach (var kv in Mats)
            {
                string path = $"{dir}/IT_{kv.Key}.mat";
                var m = AssetDatabase.LoadAssetAtPath<Material>(path);
                if (m == null) { m = new Material(lit); AssetDatabase.CreateAsset(m, path); }
                m.SetColor("_BaseColor", kv.Value.c);
                m.SetFloat("_Metallic", kv.Value.metal);
                m.SetFloat("_Smoothness", kv.Value.smooth);
                EditorUtility.SetDirty(m);
                mats["IT_" + kv.Key] = m;
            }
            foreach (var tex in Directory.GetFiles(Models + "/Textures", "T_IT_*.png"))
            {                                                              // the armour on the ground: one baked texture each
                string id = Path.GetFileNameWithoutExtension(tex).Substring("T_IT_".Length);
                string path = $"{dir}/IT_Armour_{id}.mat";
                var m = AssetDatabase.LoadAssetAtPath<Material>(path);
                if (m == null) { m = new Material(lit); AssetDatabase.CreateAsset(m, path); }
                m.SetTexture("_BaseMap", AssetDatabase.LoadAssetAtPath<Texture2D>(tex.Replace('\\', '/')));
                m.SetColor("_BaseColor", Color.white);
                var metal = ArmourMetal.TryGetValue(id, out var ms) ? ms : (0f, 0.15f);
                m.SetFloat("_Metallic", metal.Item1);
                m.SetFloat("_Smoothness", metal.Item2);
                EditorUtility.SetDirty(m);
                mats["IT_Armour_" + id] = m;
            }
            AssetDatabase.SaveAssets();
            int n = 0;
            foreach (var guid in AssetDatabase.FindAssets("t:Model", new[] { Models }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                if (!(AssetImporter.GetAtPath(path) is ModelImporter mi)) continue;
                mi.materialImportMode = ModelImporterMaterialImportMode.ImportViaMaterialDescription;
                mi.importAnimation = false; mi.animationType = ModelImporterAnimationType.None;
                mi.bakeAxisConversion = true;                             // Blender's Z up baked in: the root's turn is free for the shot
                foreach (var kv in mats) mi.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material), kv.Key), kv.Value);
                foreach (var kit in KitMats)                                // the kit's own (the goods atlas, paper, bark...)
                {
                    var km = AssetDatabase.LoadAssetAtPath<Material>($"Packages/com.danielgruginski.medievalkit/Generated/Materials/M_{kit}.mat");
                    if (km != null) mi.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material), kit), km);
                }
                mi.SaveAndReimport();
                n++;
            }
            return $"icon models: {mats.Count} materials, {n} models remapped";
        }

        /// <summary>the armour on the ground (Items/src/armour_drop.py, 2026-10-27): metallic and smoothness of the steel ones</summary>
        static readonly Dictionary<string, (float, float)> ArmourMetal = new Dictionary<string, (float, float)>
        {
            ["platemail"] = (0.55f, 0.45f), ["iron_gauntlets"] = (0.55f, 0.45f), ["chainmail"] = (0.35f, 0.35f),
        };

        /// <summary>the kit's materials the icon models use by name (Blender's VK_X: the kit's M_VK_X)</summary>
        static readonly string[] KitMats = { "VK_Goods", "VK_Paper", "VK_Wood", "VK_EndGrain", "VK_BarkOak", "VK_Burlap", "VK_Clay",
            "VK_Iron", "VK_Coal", "VK_OreIronChunk", "VK_OreSilverChunk", "VK_Rock", "VK_StoneFresh", "VK_Cloth_Cream", "VK_Hide", "VK_Pigskin",
            "VK_GoblinHerb", "VK_WildGarlic", "VK_Yarrow", "VK_Fireweed" };

        [MenuItem("Game/Items/Prepare Icon Models")]
        public static void PrepareMenu() => Debug.Log(PrepareModels());

        enum Pose { Long, Flat, Hang, Upright, Top }

        static Pose PoseOf(ItemDefinition d) =>
            d is ShieldDefinition ? Pose.Flat : d is ArmourDefinition a && a.slot == EquipSlot.Neck ? Pose.Hang
            : d is WeaponDefinition || d is ThrownDefinition || d is AmmoDefinition || d.Id.EndsWith("_horn") || LongProps.Contains(d.Id) ? Pose.Long
            : d is TomeDefinition || d is ScrollDefinition || TopProps.Contains(d.Id) ? Pose.Top : Pose.Upright;

        /// <summary>icon models lying flat (a cheese, a folded pelt, a slab of meat): seen more from above</summary>
        static readonly HashSet<string> TopProps = new HashSet<string>
            { "cheese", "wool", "chitin_plate", "raw_meat", "bear_meat", "rhino_meat", "wolf_meat", "bear_pelt", "rhino_hide", "cloth", "orc_silver", "eggs",
              "goblin_herb", "wild_garlic", "yarrow", "fireweed", "ghostpipe", "cotton" };

        /// <summary>icon models laid diagonal like a weapon (long and thin: a tusk, a key, a fish)</summary>
        static readonly HashSet<string> LongProps = new HashSet<string>
            { "mammoth_tusk", "orc_tusk", "rat_fang", "stag_antler", "mammoth_wool", "spider_silk", "cage_key", "keeper_whistle", "rat_skewer", "smoked_fish", "carrot" };

        /// <summary>a model with a part in the item's own colour (IT_Tint: a potion, a scroll's seal, a gem): one icon an item</summary>
        static bool Tinted(GameObject m) =>
            m.GetComponentsInChildren<Renderer>(true).Any(r => r.sharedMaterials.Any(x => x != null && x.name == "IT_Tint"));

        public static string Render()
        {
            if (EditorApplication.isPlaying) return "playing: not rendered";
            var db = Resources.Load<ItemDatabase>("ItemDatabase");
            if (db == null) return "no ItemDatabase";
            TomeOrder.Clear();                                              // the tomes' turn in their class
            var perClass = new Dictionary<string, int>();
            foreach (var t in db.items.OfType<TomeDefinition>())
            {
                string cls = GameRules.Get.skills.FirstOrDefault(s => s != null && s.id == t.skill)?.classId ?? GameRules.GeneralClass;
                perClass.TryGetValue(cls, out var n);
                TomeOrder[t.Id] = n;
                perClass[cls] = n + 1;
            }
            var byModel = new Dictionary<GameObject, List<ItemDefinition>>();
            var tinted = new List<(GameObject m, ItemDefinition d)>();
            var order = new List<GameObject>();
            foreach (var d in db.items)
            {
                var m = ModelOf(d);
                if (m == null) continue;
                if (Tinted(m)) { tinted.Add((m, d)); continue; }
                if (!byModel.TryGetValue(m, out var list)) { byModel[m] = list = new List<ItemDefinition>(); order.Add(m); }
                list.Add(d);
            }
            Directory.CreateDirectory(Dir);
            var scene = EditorSceneManager.NewPreviewScene();
            var rt = new RenderTexture(Size, Size, 24, RenderTextureFormat.ARGB32) { antiAliasing = 8 };
            var tex = new Texture2D(Size, Size, TextureFormat.RGBA32, false);
            var made = new List<(string path, List<ItemDefinition> items)>();
            try
            {
                var cam = Stage(scene, rt);
                foreach (var m in order)
                {
                    var items = byModel[m];
                    string path = $"{Dir}/{items[0].Id}.png";
                    Shoot(scene, cam, m, PoseOf(items[0]), rt, tex);
                    File.WriteAllBytes(path, tex.EncodeToPNG());
                    made.Add((path, items));
                }
                foreach (var (m, d) in tinted)                                  // a potion, a scroll, a gem: an item at a time
                {
                    string path = $"{Dir}/{d.Id}.png";
                    Shoot(scene, cam, m, PoseOf(d), rt, tex, d.color);
                    File.WriteAllBytes(path, tex.EncodeToPNG());
                    made.Add((path, new List<ItemDefinition> { d }));
                }
                Armour(scene, cam, db, rt, tex, made);
            }
            finally
            {
                EditorSceneManager.ClosePreviewScene(scene);
                rt.Release();
                Object.DestroyImmediate(rt);
                Object.DestroyImmediate(tex);
            }
            int set = 0;
            Directory.CreateDirectory(OutlineDir);
            foreach (var (path, items) in made)
            {
                var sprite = ImportSprite(path);
                var outline = ImportSprite(Outline(path));
                foreach (var d in items)
                {
                    if (d.icon == sprite && d.iconOutline == outline) continue;
                    d.icon = sprite; d.iconOutline = outline;
                    EditorUtility.SetDirty(d);
                    set++;
                }
            }
            AssetDatabase.SaveAssets();
            return $"item icons: {made.Count} rendered to {Dir}, set on {set} items ({byModel.Values.Sum(l => l.Count)} with a model)";
        }

        const string OutlineDir = Dir + "/Outline";

        static Sprite ImportSprite(string path)
        {
            AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceSynchronousImport);
            if (AssetImporter.GetAtPath(path) is TextureImporter ti)
            {
                ti.textureType = TextureImporterType.Sprite;
                ti.spriteImportMode = SpriteImportMode.Single;
                ti.alphaIsTransparency = true;
                ti.mipmapEnabled = false;
                ti.maxTextureSize = Size;
                ti.textureCompression = TextureImporterCompression.Uncompressed;
                ti.SaveAndReimport();
            }
            return AssetDatabase.LoadAssetAtPath<Sprite>(path);
        }

        /// <summary>an icon's soft outline (2026-10-22, the user on the painted effects behind magical items: "these are too
        /// much. I was thinking more like a faint colored outline"): its shape grown by 2 px and blurred, white (the HUD
        /// tints it with the element's colour and lays it under the icon, so only a rim shows); Items/Icons/Outline. Since
        /// 2026-10-22 (the user: "I would request the decay to the background to happen slower, covering a greater area
        /// with the glow") a tight soft rim with two wider halos under it (blurred about 6 and 12 px), fading slowly; and
        /// the first round light under all (the user: "a middle ground of the outline and the generic round effect we had in
        /// the beginning"). Since then one blended glow, not the two summed (the user: "I wanted a result that was a middle
        /// ground of the two ... Maybe the problem is that the outline is too thick and saturared"; of three mocks: "I liked
        /// C the best"): the shape's halo, blurred about 15 px, faded toward the square's corners as the round light was,
        /// over a faint thin edge; its strength is in the mask (the HUD tints it at full)</summary>
        static string Outline(string iconPath)
        {
            var src = new Texture2D(2, 2);
            src.LoadImage(File.ReadAllBytes(iconPath));
            int w = src.width, h = src.height;
            var px = src.GetPixels32();
            Object.DestroyImmediate(src);
            var a = new float[w * h];
            for (int i = 0; i < a.Length; i++) a[i] = px[i].a / 255f;
            float[] Pass(float[] f, int r, bool max, bool horizontal)          // a max (grow) or mean (blur) along one axis
            {
                var o = new float[f.Length];
                for (int y = 0; y < h; y++)
                    for (int x = 0; x < w; x++)
                    {
                        float acc = 0f; int n = 0;
                        for (int k = -r; k <= r; k++)
                        {
                            int xx = horizontal ? x + k : x, yy = horizontal ? y : y + k;
                            if (xx < 0 || yy < 0 || xx >= w || yy >= h) { n++; continue; }
                            float v = f[yy * w + xx];
                            if (max) acc = Mathf.Max(acc, v); else acc += v;
                            n++;
                        }
                        o[y * w + x] = max ? acc : acc / n;
                    }
                return o;
            }
            float[] Blur(float[] f, int r, int passes)                        // three box passes: about a gaussian
            {
                for (int i = 0; i < passes; i++) f = Pass(Pass(f, r, false, true), r, false, false);
                return f;
            }
            var halo = Blur(Pass(Pass(a, 1, true, true), 1, true, false), 15, 3);   // the shape grown 1 px, blurred about 15
            var rim = Blur(a, 1, 2);                                          // its own edge, barely softened
            for (int i = 0; i < a.Length; i++)
            {
                float dx = (i % w + 0.5f) / w * 2f - 1f, dy = (i / w + 0.5f) / h * 2f - 1f;
                float r = Mathf.Clamp01(1f - Mathf.Sqrt(dx * dx + dy * dy));
                float disc = r * r * (3f - 2f * r);                           // the round light's falloff to the square's edge
                a[i] = Mathf.Max(0.65f * Mathf.Clamp01(halo[i] * 4.5f) * (0.35f + 0.65f * disc), 0.28f * rim[i]);
            }
            var outPx = new Color32[w * h];
            for (int i = 0; i < a.Length; i++) outPx[i] = new Color32(255, 255, 255, (byte)Mathf.RoundToInt(Mathf.Clamp01(a[i]) * 255f));
            var t = new Texture2D(w, h, TextureFormat.RGBA32, false);
            t.SetPixels32(outPx);
            t.Apply();
            string path = $"{OutlineDir}/{Path.GetFileName(iconPath)}";
            File.WriteAllBytes(path, t.EncodeToPNG());
            Object.DestroyImmediate(t);
            return path;
        }

        /// <summary>the model an icon is made from (null: the item keeps its letters); worn armour has none (its icon is a
        /// dressed body, <see cref="Armour"/>)</summary>
        static GameObject ModelOf(ItemDefinition d) =>
            Dressed(d) ? null : d is WeaponDefinition w ? w.model : d is ShieldDefinition s ? s.model : d is ThrownDefinition t ? t.model
            : AssetDatabase.LoadAssetAtPath<GameObject>(Props.TryGetValue(d.Id, out var p) ? p : d is TomeDefinition t2 ? TomeModel(t2)
                                                        : d is ScrollDefinition sc ? ScrollModel(sc) : $"{Models}/IT_{d.Id}.fbx");

        /// <summary>armour shown on a body (its icon a dressed Human), not a necklace</summary>
        static bool Dressed(ItemDefinition d) => d is ArmourDefinition a && a.slot != EquipSlot.Neck && !string.IsNullOrEmpty(a.look);

        /// <summary>items that are never dropped, so need no model on the ground</summary>
        static readonly HashSet<string> NeverDropped = new HashSet<string> { "fists" };
        /// <summary>items lying on the ground as another's model (the same armour in another colour: its IT_Tint part)</summary>
        static readonly Dictionary<string, string> WorldShared = new Dictionary<string, string>();   // (2026-10-27: the
                                                                  // blackened studded leather has its own baked model)

        /// <summary>the model a dropped item lies on the ground as (2026-10-22, the user: "every item now needs a world mesh,
        /// so we need to keep track this part and build the ones that don't exist. Once every item has a mesh we begin the
        /// transition"): the icon's model; worn armour its own Items/Models/IT_&lt;id&gt; (or a shared one)</summary>
        static GameObject WorldModelOf(ItemDefinition d) =>
            Dressed(d) ? AssetDatabase.LoadAssetAtPath<GameObject>($"{Models}/IT_{(WorldShared.TryGetValue(d.Id, out var s) ? s : d.Id)}.fbx")
                       : ModelOf(d);

        const string WorldReport = "Assets/Game/Items/WORLD_MODELS.md";
        /// <summary>gold's ground models, by the amount (GameRules.goldModels)</summary>
        static readonly string[] GoldModels = { "gold_few", "gold_some", "gold_heap" };

        [MenuItem("Game/Items/World Models")]
        public static void WorldModelsMenu() => Debug.Log(WorldModels());

        /// <summary>every item's <see cref="ItemDefinition.worldModel"/> set from <see cref="WorldModelOf"/>, and the ones still
        /// without a model listed in Items/WORLD_MODELS.md (the tracker for the ground-drop switch)</summary>
        public static string WorldModels()
        {
            if (EditorApplication.isPlaying) return "playing: not done";
            var db = Resources.Load<ItemDatabase>("ItemDatabase");
            if (db == null) return "no ItemDatabase";
            int set = 0, have = 0;
            var missing = new List<ItemDefinition>();
            foreach (var d in db.items.Where(x => x != null).OrderBy(x => x.GetType().Name).ThenBy(x => x.Id))
            {
                if (NeverDropped.Contains(d.Id)) continue;
                var m = WorldModelOf(d);
                if (m == null) missing.Add(d); else have++;
                if (d.worldModel == m) continue;
                d.worldModel = m;
                EditorUtility.SetDirty(d);
                set++;
            }
            var R = GameRules.Get;
            var gold = GoldModels.Select(g => AssetDatabase.LoadAssetAtPath<GameObject>($"{Models}/IT_{g}.fbx")).ToArray();
            int goldHave = gold.Count(g => g != null);
            if (R != null && (R.goldModels == null || !R.goldModels.SequenceEqual(gold)))
            {
                R.goldModels = gold;
                EditorUtility.SetDirty(R);
            }
            var sb = new System.Text.StringBuilder();
            sb.AppendLine("# World models (generated)");
            sb.AppendLine();
            sb.AppendLine("Every item's model lying on the ground once loot drops Diablo-style (2026-10-22, the user: \"every item now needs a world");
            sb.AppendLine("mesh, so we need to keep track this part and build the ones that don't exist. Once every item has a mesh we begin the");
            sb.AppendLine("transition\"). Written by Game > Items > World Models, which also sets ItemDefinition.worldModel. Do not edit by hand.");
            sb.AppendLine();
            sb.AppendLine($"- Items with a world model: {have}");
            sb.AppendLine($"- Items still without one: {missing.Count}");
            sb.AppendLine(goldHave == GoldModels.Length ? "- Gold: a few coins, some, a heap (GameRules.goldModels: IT_gold_few, _some, _heap)"
                                                        : $"- Gold: {goldHave} of {GoldModels.Length} piles made (IT_gold_few, _some, _heap)");
            sb.AppendLine();
            if (missing.Count > 0)
            {
                sb.AppendLine("## Still to make");
                sb.AppendLine();
                foreach (var d in missing)
                    sb.AppendLine($"- `{d.Id}` ({d.Name}, {d.GetType().Name.Replace("Definition", "")}" +
                                  (d is ArmourDefinition a ? $", {a.slot}" : "") + ")" +
                                  (WorldShared.TryGetValue(d.Id, out var s) ? $" -- shares IT_{s}" : $" -- Items/Models/IT_{d.Id}.fbx"));
                sb.AppendLine();
            }
            File.WriteAllText(WorldReport, sb.ToString().Replace("\r\n", "\n"));
            AssetDatabase.ImportAsset(WorldReport);
            AssetDatabase.SaveAssets();
            return $"world models: {have} items have one, {missing.Count} still to make (set on {set}); {WorldReport}";
        }

        /// <summary>a scroll's look (2026-10-22, the user: "we could use several types of scrolls. Lets start working on the
        /// mesh that will be dropped in game"; all five were one roll): a priest's prayer on a rod (cleansing), a fire spell
        /// singed, a ward open on its sign, the rest sealed with a ribbon; each in the scroll's own colour</summary>
        static string ScrollModel(ScrollDefinition s) =>
            $"{Models}/IT_" + (s.cleanse ? "scroll_rod" : s.skill.Contains("fire") ? "scroll_singed" : s.skill.EndsWith("_ward") ? "scroll_open" : "scroll") + ".fbx";

        /// <summary>a tome's book (2026-10-22, the user: "tomes per class ... Plus the neutral tomes. Make 3 tomes per class,
        /// with a common color theme"): its skill's class's theme (general for the rest), one of its three builds in turn</summary>
        static string TomeModel(TomeDefinition t)
        {
            var R = GameRules.Get;
            string cls = R.skills.FirstOrDefault(s => s != null && s.id == t.skill)?.classId;
            if (string.IsNullOrEmpty(cls) || !TomeClasses.Contains(cls)) cls = GameRules.GeneralClass;
            int v = TomeOrder.TryGetValue(t.Id, out var i) ? i % 3 : 0;
            return $"{Models}/IT_tome_{cls}_{v}.fbx";
        }

        static readonly string[] TomeClasses = { "fighter", "rogue", "wizard", "ranger", "cleric", GameRules.GeneralClass };
        static readonly Dictionary<string, int> TomeOrder = new Dictionary<string, int>();

        /// <summary>the camera and two lights in the preview scene: a key from the upper left and front, a soft fill behind</summary>
        static Camera Stage(Scene scene, RenderTexture rt)
        {
            var camGo = new GameObject("IconCam");
            SceneManager.MoveGameObjectToScene(camGo, scene);
            var cam = camGo.AddComponent<Camera>();
            cam.scene = scene; cam.orthographic = true; cam.enabled = false;
            cam.clearFlags = CameraClearFlags.SolidColor; cam.backgroundColor = new Color(0f, 0f, 0f, 0f);
            cam.nearClipPlane = 0.01f; cam.farClipPlane = 50f; cam.targetTexture = rt;
            foreach (var (rot, intensity) in new[] { (Quaternion.Euler(35f, 30f, 0f), 1.3f), (Quaternion.Euler(-20f, -140f, 0f), 0.45f) })
            {
                var lg = new GameObject("Light");
                SceneManager.MoveGameObjectToScene(lg, scene);
                var l = lg.AddComponent<Light>();
                l.type = LightType.Directional; l.intensity = intensity;
                lg.transform.rotation = rot;
            }
            return cam;
        }

        /// <summary>the armour worn (body, hands, feet) on the Humans character with its body, head and hair hidden, in
        /// its rest pose (arms down) turned a little off the camera: body armour from the top of its head piece to the
        /// hips, gloves the left hand's, boots the pair; each item its own icon (gloves and boots differ by colour only)</summary>
        static void Armour(Scene scene, Camera cam, ItemDatabase db, RenderTexture rt, Texture2D tex, List<(string, List<ItemDefinition>)> made)
        {
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Humans/Prefabs/Human.prefab");
            if (prefab == null) return;
            var h = (GameObject)Object.Instantiate(prefab);
            SceneManager.MoveGameObjectToScene(h, scene);
            var hf = h.GetComponentInChildren<Humans.HumanFace>();
            var anim = h.GetComponentInChildren<Animator>();
            if (hf == null || anim == null) { Object.DestroyImmediate(h); return; }
            foreach (var d in db.items.OfType<ArmourDefinition>())
            {
                if (string.IsNullOrEmpty(d.look) || d.slot == EquipSlot.Neck) continue;
                bool body = d.slot == EquipSlot.Body;
                h.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);
                if (body) MedievalGame.HumanActor.Dress(hf, d.look, null);
                else MedievalGame.HumanActor.Dress(hf, null, new string[0], IconLook(d));
                h.transform.rotation = Quaternion.Euler(0f, 180f + (d.slot == EquipSlot.Feet ? 35f : 20f), 0f);   // its front to the camera, turned a little
                var cloth = new List<Renderer>();
                foreach (var r in h.GetComponentsInChildren<Renderer>(true))
                {
                    bool show = r.name.StartsWith("Cloth_") && !r.name.EndsWith("_L1") && !r.name.EndsWith("_L2");
                    r.enabled = show;
                    if (show && r.gameObject.activeInHierarchy) cloth.Add(r);
                }
                if (cloth.Count == 0) continue;
                var b = cloth[0].bounds;
                foreach (var r in cloth) b.Encapsulate(r.bounds);
                Vector3 mid; float half;
                if (body)
                {
                    float top = b.max.y + 0.04f, low = Mathf.Max(b.min.y, top - 1.0f);   // head piece (a little room over it) to the hips
                    mid = new Vector3(b.center.x, (top + low) / 2f, b.center.z);
                    half = Mathf.Max((top - low) / 2f, b.extents.x) * 1.04f;
                }
                else if (d.slot == EquipSlot.Hands)                       // the left hand's half of the pair
                {
                    var hand = anim.GetBoneTransform(HumanBodyBones.LeftHand).position;
                    float x = hand.x < b.center.x ? (b.min.x + b.center.x) / 2f : (b.center.x + b.max.x) / 2f;
                    mid = new Vector3(x, b.center.y, b.center.z);
                    half = Mathf.Max(b.extents.x / 2f, b.extents.y) * 1.1f;
                }
                else { mid = b.center; half = Mathf.Max(b.extents.x, b.extents.y) * 1.08f; }
                cam.transform.SetPositionAndRotation(mid - Vector3.forward * 10f, Quaternion.identity);
                cam.orthographicSize = half / Fill(body ? 1.2f : d.slot == EquipSlot.Hands ? 0.25f : 0.45f);   // a suit (a little room round it), a glove, a pair of boots
                cam.Render();
                RenderTexture.active = rt;
                tex.ReadPixels(new Rect(0, 0, Size, Size), 0, 0);
                tex.Apply();
                RenderTexture.active = null;
                string path = $"{Dir}/{d.Id}.png";
                File.WriteAllBytes(path, tex.EncodeToPNG());
                made.Add((path, new List<ItemDefinition> { d }));
            }
            Object.DestroyImmediate(h);
        }

        /// <summary>what a hand or foot item wears for its icon: its look, and under a cuff or a gauntlet the glove itself
        /// (the bracers alone are a ring round an empty wrist): the item's colour, a mail glove's grey under plate</summary>
        static string[] IconLook(ArmourDefinition d)
        {
            int c = d.look.IndexOf(':');
            string g = c >= 0 ? d.look.Substring(0, c) : d.look, col = c >= 0 ? d.look.Substring(c + 1) : "#5e5344";
            if (g == "Bracers") return new[] { "Gloves:" + col, d.look };
            if (g == "PlateGauntlets") return new[] { "Gloves:#6e6e72", d.look };
            return new[] { d.look };
        }

        /// <summary>how much of its square an item fills, by its real longest side (2026-10-22, the user: "small objects like
        /// daggers should be smaller than two handed weapons. They dont have to be at scale, but a rat tusk should be
        /// smaller than the orc one, while the mammoth tusk should barelly fit the square"): a compressed curve from 0.3 for
        /// a ring (3 cm and less) to the whole square at 2 m and more -- a dagger about 0.65, a two-handed sword 0.96</summary>
        static float Fill(float longest)
        {
            float t = Mathf.Clamp01(Mathf.Log(Mathf.Max(longest, 1e-3f) / 0.03f) / Mathf.Log(2f / 0.03f));
            return Mathf.Lerp(0.3f, 1f, Mathf.Pow(t, 1.3f));
        }

        static void Shoot(Scene scene, Camera cam, GameObject model, Pose pose, RenderTexture rt, Texture2D tex, Color? tint = null)
        {
            var inst = (GameObject)Object.Instantiate(model);
            SceneManager.MoveGameObjectToScene(inst, scene);
            inst.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);
            inst.SetActive(true);                                          // (a kit prefab may be saved switched off: the ghostpipe)
            var rs = inst.GetComponentsInChildren<Renderer>();
            Material tintMat = null;
            if (tint.HasValue)                                             // the item's own colour on its IT_Tint part
                foreach (var r in rs)
                {
                    var ms = r.sharedMaterials;
                    for (int i = 0; i < ms.Length; i++)
                        if (ms[i] != null && ms[i].name == "IT_Tint")
                        {
                            if (tintMat == null) { tintMat = new Material(ms[i]); tintMat.SetColor("_BaseColor", tint.Value); }
                            ms[i] = tintMat;
                        }
                    r.sharedMaterials = ms;
                }
            if (rs.Length == 0) { Object.DestroyImmediate(inst); return; }
            Bounds B() { var b = rs[0].bounds; foreach (var r in rs) b.Encapsulate(r.bounds); return b; }
            var s0 = B().size;
            float fill = Fill(Mathf.Max(s0.x, Mathf.Max(s0.y, s0.z)));
            if (pose == Pose.Upright || pose == Pose.Top)                 // as it stands (the import's turn: Z up), seen a little from above
                inst.transform.rotation = Quaternion.Euler(pose == Pose.Top ? -55f : -22f, -30f, 0f) * model.transform.localRotation;
            else if (pose == Pose.Hang)                                   // a necklace hanging, its pendant's face to the camera
                inst.transform.rotation = Quaternion.Euler(8f, -18f, 0f) * model.transform.localRotation;   // (the import's turn: Z up)
            else if (pose == Pose.Flat)
            {
                var face = s0.x <= s0.y && s0.x <= s0.z ? Quaternion.Euler(0f, 90f, 0f) : s0.y <= s0.z ? Quaternion.Euler(90f, 0f, 0f) : Quaternion.identity;
                var front = Quaternion.Euler(0f, 180f, 0f) * face;                     // the painted face to the camera
                inst.transform.rotation = front;
                var b1 = B();
                var stand = b1.size.x > b1.size.y * 1.1f ? Quaternion.Euler(0f, 0f, 90f) : Quaternion.identity;   // upright, point down
                inst.transform.rotation = Quaternion.Euler(8f, -18f, 0f) * stand * front;
            }
            else
            {
                var up = s0.x >= s0.y && s0.x >= s0.z ? Quaternion.Euler(0f, 0f, 90f) : s0.z >= s0.y ? Quaternion.Euler(-90f, 0f, 0f) : Quaternion.identity;
                inst.transform.rotation = Quaternion.Euler(0f, 0f, -45f) * Quaternion.Euler(0f, 25f, 0f) * up;
            }
            var b2 = B();
            cam.transform.SetPositionAndRotation(b2.center - Vector3.forward * 10f, Quaternion.identity);
            cam.orthographicSize = Mathf.Max(b2.extents.x, b2.extents.y) * 1.08f / fill;
            cam.Render();
            RenderTexture.active = rt;
            tex.ReadPixels(new Rect(0, 0, Size, Size), 0, 0);
            tex.Apply();
            RenderTexture.active = null;
            Object.DestroyImmediate(inst);
            if (tintMat != null) Object.DestroyImmediate(tintMat);
        }
    }
}
