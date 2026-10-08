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
            report("No enabled, approved skin assets; keeping original appearances.");
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
            if (matches.Length != 1 || !matches[0].Approved)
            {
                report($"No unique approved skin for '{character}'; skipped.");
                continue;
            }

            var skin = matches[0];
            var paths = new[] { skin.CombatScene, skin.SelectScene }.OfType<string>().ToArray();
            if (paths.Length == 0 || paths.Any(path => !IsOwnedScene(path)))
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

    private static bool IsOwnedScene(string path) =>
        path.StartsWith("res://PopSpireWomen/", StringComparison.Ordinal) &&
        path.EndsWith(".tscn", StringComparison.Ordinal) &&
        path["res://".Length..].Split('/').All(segment =>
            segment.Length > 0 && segment is not "." and not ".." &&
            segment.All(c => char.IsAsciiLetterOrDigit(c) || c is '_' or '-' or '.'));
}
