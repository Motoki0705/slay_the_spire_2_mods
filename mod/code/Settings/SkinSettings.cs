using System.Text.Json;
using System.Text.Json.Serialization;

namespace PopSpireWomen.Settings;

internal sealed record SkinSettings
{
    public int SchemaVersion { get; init; } = 1;
    public bool Enabled { get; init; }
    public string[] EnabledCharacters { get; init; } = [];

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow
    };

    // Missing, invalid, or newer settings never activate a skin. Does not write user data.
    public static SkinSettings Parse(string? json, Action<string> report)
    {
        if (json is null)
            return new();

        try
        {
            var settings = JsonSerializer.Deserialize<SkinSettings>(json, JsonOptions);
            if (settings is null || settings.SchemaVersion != 1 ||
                settings.EnabledCharacters is null ||
                settings.EnabledCharacters.Any(string.IsNullOrWhiteSpace))
            {
                report("Invalid settings schema; keeping original appearances.");
                return new();
            }
            return settings;
        }
        catch (JsonException)
        {
            report("Cannot parse settings; keeping original appearances.");
            return new();
        }
    }
}
