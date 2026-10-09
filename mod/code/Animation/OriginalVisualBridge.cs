using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.RestSite;
using MegaCrit.Sts2.Core.Nodes.Screens.Shops;
using PopSpireWomen.Routing;

namespace PopSpireWomen.Animation;

// Presentation-only postfixes. No trigger, command, RNG, timing, save or animator patch.
internal static class OriginalVisualBridge
{
    private const string Scene = "res://PopSpireWomen/animation/driver_overlay.tscn";
    private static IReadOnlyDictionary<string, SkinDefinition> _skins = new Dictionary<string, SkinDefinition>();
    private static bool _installed;

    public static void Install(IReadOnlyList<SkinDefinition> skins)
    {
        _skins = skins.Where(s => s.CombatRig is not null || s.MerchantRig is not null || s.RestRig is not null)
            .ToDictionary(s => s.CharacterEntry, StringComparer.Ordinal);
        if (_skins.Count == 0 || _installed) return;
        var harmony = new Harmony(Bootstrap.ModId + ".OriginalVisualBridge");
        try
        {
            harmony.Patch(AccessTools.Method(typeof(CharacterModel), nameof(CharacterModel.CreateVisuals)),
                postfix: new HarmonyMethod(typeof(OriginalVisualBridge), nameof(CombatCreated)));
            harmony.Patch(AccessTools.Method(typeof(NMerchantCharacter), nameof(NMerchantCharacter._Ready)),
                postfix: new HarmonyMethod(typeof(OriginalVisualBridge), nameof(MerchantReady)));
            harmony.Patch(AccessTools.Method(typeof(NRestSiteCharacter), nameof(NRestSiteCharacter._Ready)),
                postfix: new HarmonyMethod(typeof(OriginalVisualBridge), nameof(RestReady)));
            _installed = true;
        }
        catch
        {
            harmony.UnpatchAll(harmony.Id);
            _skins = new Dictionary<string, SkinDefinition>();
            throw;
        }
    }

    private static void CombatCreated(CharacterModel __instance, NCreatureVisuals __result)
    {
        if (_skins.TryGetValue(__instance.Id.Entry, out var skin) && skin.CombatRig is not null)
            Attach(__result, skin.CharacterEntry, skin.CombatRig, "Visuals", "combat",
                $"res://scenes/creature_visuals/{skin.CharacterEntry.ToLowerInvariant()}.tscn");
    }

    private static void MerchantReady(NMerchantCharacter __instance)
    {
        foreach (var skin in _skins.Values)
        {
            if (skin.MerchantRig is null) continue;
            // The game requires the original first child for PlayAnimation, including direct die calls.
            var driver = __instance.GetChildCount() > 0 ? __instance.GetChild(0) : null;
            if (driver is null) continue;
            Attach(__instance, skin.CharacterEntry, skin.MerchantRig, driver.Name, "merchant",
                $"res://scenes/merchant/characters/{skin.CharacterEntry.ToLowerInvariant()}_merchant.tscn");
        }
    }

    private static void RestReady(NRestSiteCharacter __instance)
    {
        var id = __instance.Player.Character.Id.Entry;
        if (!_skins.TryGetValue(id, out var skin) || skin.RestRig is null) return;
        var driver = id switch { "REGENT" => "SpineSprite2", "NECROBINDER" => "Necro", _ => "SpineSprite" };
        Attach(__instance, id, skin.RestRig, driver, "rest",
            $"res://scenes/rest_site/characters/{id.ToLowerInvariant()}_rest_site.tscn");
    }

    private static void Attach(Node root, string id, string rig, string driverPath, string surface, string originalPath)
    {
        // Other skins own other scenes. Do not guess at their node/animation contracts.
        if (root.SceneFilePath != originalPath || root.HasNode("PopSpireWomenOverlay")) return;
        Node? overlay = null;
        try
        {
            var driver = root.GetNodeOrNull<Node>(driverPath);
            if (driver?.GetClass() != "SpineSprite" || !ResourceLoader.Exists(Scene, "PackedScene")) return;
            overlay = ResourceLoader.Load<PackedScene>(Scene)?.Instantiate();
            if (overlay is null) return;
            overlay.Name = "PopSpireWomenOverlay";
            overlay.Set("character_entry", id);
            overlay.Set("rig_path", rig);
            overlay.Set("driver_path", new NodePath("../" + driverPath));
            overlay.Set("surface", surface);
            root.AddChild(overlay);
        }
        catch (Exception ex) when (ex is not OutOfMemoryException)
        {
            if (GodotObject.IsInstanceValid(overlay)) overlay!.QueueFree();
            Log.Warn($"[{Bootstrap.ModId}] {id}/{surface} overlay inactive ({ex.GetType().Name}); original retained.");
        }
    }
}
