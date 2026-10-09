extends RefCounted
## Build-time preferences, embedded in the PCK. Changing them requires rebuilding and restarting.
const PATH = "res://PopSpireWomen/config/settings.json"
const CHARACTERS = ["IRONCLAD", "SILENT", "REGENT", "NECROBINDER", "DEFECT"]

static func read() -> Dictionary:
	var defaults := {"SchemaVersion": 1, "Enabled": true, "EnabledCharacters": CHARACTERS.duplicate(), "ReducedMotion": false}
	if not FileAccess.file_exists(PATH): return defaults
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(PATH))
	if parsed is Dictionary and not parsed.get("SchemaVersion") is bool and parsed.get("SchemaVersion") == 1 and parsed.get("Enabled") is bool and parsed.get("ReducedMotion") is bool and parsed.get("EnabledCharacters") is Array:
		var valid := true
		for key: Variant in parsed:
			if key not in defaults: valid = false
		var seen := []
		for entry: Variant in parsed.EnabledCharacters:
			if entry not in CHARACTERS or entry in seen: valid = false
			seen.append(entry)
		if valid: return parsed
	push_warning("[PopSpireWomen] Invalid PCK settings; retaining originals")
	return {"SchemaVersion": 1, "Enabled": false, "EnabledCharacters": [], "ReducedMotion": false}

static func enabled(preferences: Dictionary, character: String) -> bool:
	return preferences.Enabled and character in preferences.EnabledCharacters

static func original_select(character: String) -> String:
	if character not in CHARACTERS: return ""
	return "res://PopSpireWomen/compat/original_select/%s.tscn" % character.to_lower()
