namespace PopSpireWomen.Routing;

// These are existing model Id.Entry values, not new character registrations.
internal sealed record SkinDefinition(
    string CharacterEntry,
    bool Approved = false,
    string? CombatScene = null,
    string? SelectScene = null);

internal static class ApprovedSkinCatalog
{
    // Design review images are not runtime assets. Add reviewed, validated resources in a later Issue.
    public static IReadOnlyList<SkinDefinition> Entries { get; } = Array.Empty<SkinDefinition>();
}
