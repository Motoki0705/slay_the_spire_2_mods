using PopSpireWomen.Settings;

namespace PopSpireWomen.Routing;

internal static class SkinBootstrap
{
    internal const string GameVersion = "v0.107.1";
    internal const string GameCommit = "59260271";
    private static readonly HashSet<string> SupportedCharacters =
        new(["IRONCLAD", "SILENT", "REGENT", "NECROBINDER", "DEFECT"], StringComparer.Ordinal);

    // Kept free of Godot/native code so the fail-closed startup policy can run in tests.
    public static int Initialize(
        SkinSettings settings,
        IReadOnlyList<SkinDefinition> catalog,
        string? gameVersion,
        string? gameCommit,
        Func<string, bool> resourceExists,
        Action<IReadOnlyList<SkinDefinition>> register,
        Action<string> report)
    {
        if (!settings.Enabled || settings.EnabledCharacters.Length == 0 || catalog.Count == 0)
        {
            report("No enabled, production skin assets; keeping original appearances.");
            return 0;
        }

        if (gameVersion != GameVersion || gameCommit != GameCommit)
        {
            report("Unsupported game build; keeping original appearances.");
            return 0;
        }

        var candidates = new List<SkinDefinition>();
        foreach (var character in settings.EnabledCharacters.Distinct(StringComparer.Ordinal))
        {
            if (!SupportedCharacters.Contains(character))
            {
                report($"Unknown character '{character}'; skipped.");
                continue;
            }

            var matches = catalog.Where(skin => skin.CharacterEntry == character).ToArray();
            if (matches.Length != 1 || !matches[0].ProductionReady ||
                matches[0].Acceptance is not (DesignAcceptance.UserApproved or DesignAcceptance.DelegatedProductionSelection))
            {
                report($"No unique accepted production skin for '{character}'; skipped.");
                continue;
            }

            var skin = matches[0];
            var scenes = new[] { skin.CombatScene, skin.SelectScene }.OfType<string>().ToArray();
            var rigs = new[] { skin.CombatRig, skin.MerchantRig, skin.RestRig }.OfType<string>().ToArray();
            var paths = scenes.Concat(rigs).ToArray();
            if (paths.Length == 0 || scenes.Any(path => !IsOwned(path, ".tscn")) ||
                rigs.Any(path => !IsOwned(path, ".json")) ||
                (skin.CombatScene is not null && skin.CombatRig is not null))
            {
                report($"Invalid resource paths for '{character}'; skipped.");
                continue;
            }

            try
            {
                if (paths.All(resourceExists))
                    candidates.Add(skin);
                else
                    report($"Missing scene for '{character}'; keeping its original appearance.");
            }
            catch (Exception ex) when (ex is not OutOfMemoryException)
            {
                report($"Resource check failed for '{character}' ({ex.GetType().Name}); skipped.");
            }
        }

        if (candidates.Count > 0)
            register(candidates);
        return candidates.Count;
    }

    private static bool IsOwned(string path, string extension) =>
        path.StartsWith("res://PopSpireWomen/", StringComparison.Ordinal) &&
        path.EndsWith(extension, StringComparison.Ordinal) &&
        path["res://".Length..].Split('/').All(segment =>
            segment.Length > 0 && segment is not "." and not ".." &&
            segment.All(c => char.IsAsciiLetterOrDigit(c) || c is '_' or '-' or '.'));
}
