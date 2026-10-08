using PopSpireWomen.Routing;
using PopSpireWomen.Settings;

var checks = new (string Name, Action Run)[]
{
    ("missing and disabled configuration performs no resource or registry calls", () =>
    {
        ExpectInactive(SkinSettings.Parse(null, _ => { }), [Valid("SILENT")]);
        ExpectInactive(new(), [Valid("SILENT")]);
        ExpectInactive(new() { Enabled = true }, [Valid("SILENT")]);
    }),
    ("malformed, null, wrong-schema and mistyped settings fail closed", () =>
    {
        string[] invalid = ["{", "null", "[]", "{\"Enabled\":\"true\"}",
            "{\"SchemaVersion\":2,\"Enabled\":true}", "{\"EnabledCharacters\":null}",
            "{\"EnabledCharacters\":[null]}", "{\"Enabled\":true,\"EnabldCharacters\":[\"SILENT\"]}"];
        foreach (var json in invalid)
        {
            var diagnostics = new List<string>();
            var settings = SkinSettings.Parse(json, diagnostics.Add);
            Require(!settings.Enabled && diagnostics.Count > 0, $"Must reject {json}");
        }
    }),
    ("shipping empty catalog remains inactive even with all five enabled", () =>
    {
        ExpectInactive(Enabled("IRONCLAD", "SILENT", "REGENT", "NECROBINDER", "DEFECT"), ApprovedSkinCatalog.Entries);
    }),
    ("unknown version or commit cannot register or probe resources", () =>
    {
        ExpectInactive(Enabled("SILENT"), [Valid("SILENT")], "v0.107.2");
        ExpectInactive(Enabled("SILENT"), [Valid("SILENT")], commit: "other");
    }),
    ("unapproved, unknown and ambiguous entries are not probed", () =>
    {
        ExpectInactive(Enabled("SILENT"), [Valid("SILENT") with { Approved = false }]);
        ExpectInactive(Enabled("OSTY"), [Valid("OSTY")]);
        ExpectInactive(Enabled("SILENT"), [Valid("SILENT"), Valid("SILENT")]);
    }),
    ("foreign, escaping, empty and non-scene paths cannot register", () =>
    {
        string[] paths = ["res://scenes/vanilla.tscn", "res://PopSpireWomen/../other.tscn",
            "res://PopSpireWomen//other.tscn", "res://PopSpireWomen/a\\b.tscn",
            "user://other.tscn", "res://PopSpireWomen/preview.png", ""];
        foreach (var path in paths)
            ExpectInactive(Enabled("SILENT"), [Valid("SILENT") with { CombatScene = path }]);
    }),
    ("missing scene keeps that character unchanged without blocking another", () =>
    {
        var received = new List<SkinDefinition>();
        var count = SkinBootstrap.Initialize(Enabled("SILENT", "DEFECT"), [Valid("SILENT"), Valid("DEFECT")],
            SkinBootstrap.GameVersion, SkinBootstrap.GameCommit,
            path => path.Contains("DEFECT", StringComparison.Ordinal), received.AddRange, _ => { });
        Require(count == 1 && received.Single().CharacterEntry == "DEFECT", "Only available character may register.");
    }),
    ("resource probe failure leaves character unchanged", () =>
    {
        var count = SkinBootstrap.Initialize(Enabled("SILENT"), [Valid("SILENT")],
            SkinBootstrap.GameVersion, SkinBootstrap.GameCommit,
            _ => throw new IOException("probe failed"), _ => throw new Exception("must not register"), _ => { });
        Require(count == 0, "Failure must skip registration.");
    }),
    ("only explicitly enabled existing ID registers once with its requested fields", () =>
    {
        var received = new List<SkinDefinition>();
        var silent = Valid("SILENT") with { SelectScene = "res://PopSpireWomen/SILENT/select.tscn" };
        var count = SkinBootstrap.Initialize(Enabled("SILENT", "SILENT"), [silent, Valid("DEFECT")],
            SkinBootstrap.GameVersion, SkinBootstrap.GameCommit, _ => true, received.AddRange, _ => { });
        Require(count == 1 && received.Single() == silent, "Must preserve selected existing ID and scene paths.");
    }),
    ("a profile with one missing surface does not partially register", () =>
    {
        var count = SkinBootstrap.Initialize(Enabled("SILENT"),
            [Valid("SILENT") with { SelectScene = "res://PopSpireWomen/SILENT/missing.tscn" }],
            SkinBootstrap.GameVersion, SkinBootstrap.GameCommit, path => !path.Contains("missing"),
            _ => throw new Exception("must not register"), _ => { });
        Require(count == 0, "Both requested surfaces must exist.");
    })
};

foreach (var (name, check) in checks)
{
    check();
    Console.WriteLine($"PASS {name}");
}
Console.WriteLine($"{checks.Length} bootstrap checks passed; no game/Godot runtime loaded.");

static SkinSettings Enabled(params string[] characters) => new() { Enabled = true, EnabledCharacters = characters };
static SkinDefinition Valid(string character) => new(character, true, $"res://PopSpireWomen/{character}/combat.tscn");
static void Require(bool condition, string message)
{
    if (!condition) throw new Exception(message);
}
static void ExpectInactive(SkinSettings settings, IReadOnlyList<SkinDefinition> catalog,
    string version = SkinBootstrap.GameVersion, string commit = SkinBootstrap.GameCommit)
{
    var probes = 0;
    var registrations = 0;
    var count = SkinBootstrap.Initialize(settings, catalog, version, commit,
        _ => { probes++; return true; },
        _ => registrations++, _ => { });
    Require(count == 0 && probes == 0 && registrations == 0, "Must remain inactive without probing or registering.");
}
