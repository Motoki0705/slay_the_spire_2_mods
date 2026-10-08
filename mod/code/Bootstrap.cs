using Godot;
using MegaCrit.Sts2.Core.Debug;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Modding;
using PopSpireWomen.Routing;
using PopSpireWomen.Settings;

namespace PopSpireWomen;

[ModInitializer(nameof(Initialize))]
public static class Bootstrap
{
    public const string ModId = "PopSpireWomen";
    private static int _initialized;

    public static void Initialize()
    {
        if (Interlocked.Exchange(ref _initialized, 1) != 0)
            return;

        try
        {
            var settingsPath = ProjectSettings.GlobalizePath($"user://{ModId}/settings.json");
            var settings = SkinSettings.Parse(
                System.IO.File.Exists(settingsPath) ? System.IO.File.ReadAllText(settingsPath) : null,
                message => Log.Warn($"[{ModId}] {message}"));
            var release = ReleaseInfoManager.Instance.ReleaseInfo;
            SkinBootstrap.Initialize(
                settings, ApprovedSkinCatalog.Entries, release?.Version, release?.Commit,
                path => ResourceLoader.Exists(path, "PackedScene"),
                RitsuSkinRegistrar.Register,
                message => Log.Info($"[{ModId}] {message}"));
        }
        catch (Exception ex) when (ex is not OutOfMemoryException)
        {
            // Startup is optional presentation work. Never interrupt loading the game for missing settings/dependencies.
            Log.Warn($"[{ModId}] Bootstrap inactive ({ex.GetType().Name}); no skin activation completed.");
        }
    }
}
