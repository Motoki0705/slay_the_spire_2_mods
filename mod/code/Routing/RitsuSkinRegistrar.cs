using System.Runtime.CompilerServices;
using STS2RitsuLib;
using PopSpireWomen.Animation;
using STS2RitsuLib.Scaffolding.Characters;

namespace PopSpireWomen.Routing;

internal static class RitsuSkinRegistrar
{
    // Delay resolving RitsuLib until there actually are accepted production resources.
    [MethodImpl(MethodImplOptions.NoInlining)]
    public static void Register(IReadOnlyList<SkinDefinition> skins)
    {
        if (typeof(RitsuLibFramework).Assembly.GetName().Version != new Version(0, 6, 7, 0))
            throw new NotSupportedException("This bootstrap pins RitsuLib 0.6.7.");

        var pack = RitsuLibFramework.CreateContentPack(Bootstrap.ModId);
        foreach (var skin in skins)
        {
            if (skin.CombatScene is null && skin.SelectScene is null) continue;
            // Non-null fields only: do not overwrite unrelated assets or register CharacterModel subclasses.
            var profile = new CharacterAssetProfile(
                Scenes: skin.CombatScene is null ? null : new CharacterSceneAssetSet(VisualsPath: skin.CombatScene),
                Ui: skin.SelectScene is null ? null : new CharacterUiAssetSet(CharacterSelectBgPath: skin.SelectScene));
            pack.CharacterAssetReplacement(skin.CharacterEntry, profile);
        }
        pack.Apply();
        OriginalVisualBridge.Install(skins);
    }
}
