namespace PopSpireWomen.Routing;

internal enum DesignAcceptance
{
    None,
    UserApproved,
    DelegatedProductionSelection
}

// Acceptance describes who selected the design; ProductionReady describes the integrated assets.
// Neither concept implies that the other has been satisfied.
internal sealed record SkinDefinition(
    string CharacterEntry,
    DesignAcceptance Acceptance = DesignAcceptance.None,
    bool ProductionReady = false,
    string? CombatScene = null,
    string? SelectScene = null,
    string? CombatRig = null,
    string? MerchantRig = null,
    string? RestRig = null);

internal static class ProductionSkinCatalog
{
    // Parent integration adds actual art/rigs after validation. Never register tests/animation fixtures.
    public static IReadOnlyList<SkinDefinition> Entries { get; } = Array.Empty<SkinDefinition>();
}
