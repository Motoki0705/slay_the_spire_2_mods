extends SceneTree
const PUPPET = preload("res://PopSpireWomen/animation/puppet.gd")
const CHARACTERS = ["ironclad", "silent", "regent", "necrobinder", "defect"]

func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 1:
		quit(2)
		return
	var result := {}
	for character: String in CHARACTERS:
		var surfaces := {}
		for surface: String in ["combat", "merchant", "rest", "select"]:
			var puppet := PUPPET.new()
			var path := "res://PopSpireWomen/rigs/%s/%s.json" % [character, surface]
			var valid: bool = puppet.load_rig(path, character.to_upper())
			surfaces[surface] = {"ok": valid, "reason": puppet.last_error}
			puppet.free()
		var select_path := "res://PopSpireWomen/select/production/%s.tscn" % character
		if surfaces.select.ok:
			var scene := ResourceLoader.load(select_path, "PackedScene") as PackedScene if ResourceLoader.exists(select_path, "PackedScene") else null
			if scene == null:
				surfaces.select = {"ok": false, "reason": "Production selection scene missing"}
			else:
				var instance := scene.instantiate()
				var valid: bool = instance is Control and instance.has_method("set_preferences") and instance.get("character_entry") == character.to_upper() and instance.get("rig_path") == "res://PopSpireWomen/rigs/%s/select.json" % character
				surfaces.select = {"ok": valid, "reason": "" if valid else "Selection descriptor contract mismatch"}
				instance.free()
		var ui := {}
		var sizes := {"top": Vector2(85,85), "outline": Vector2(85,85), "portrait": Vector2(132,195), "locked": Vector2(132,195), "map": Vector2(49,64)}
		for name: String in sizes:
			var path := "res://PopSpireWomen/ui/%s/%s.png" % [character, name]
			var texture := ResourceLoader.load(path, "Texture2D") as Texture2D if ResourceLoader.exists(path, "Texture2D") else null
			ui[name] = {"ok": texture is CompressedTexture2D and texture.get_size() == sizes[name], "size": [sizes[name].x, sizes[name].y]}
		var icon_path := "res://PopSpireWomen/ui/%s/icon.tscn" % character
		var icon_scene := ResourceLoader.load(icon_path, "PackedScene") as PackedScene if ResourceLoader.exists(icon_path, "PackedScene") else null
		ui.icon = {"ok": false}
		if icon_scene != null:
			var icon := icon_scene.instantiate()
			ui.icon.ok = icon is TextureRect and icon.get_child_count() == 0 and icon.get_script() == null and icon.texture is CompressedTexture2D and icon.texture.get_size() == Vector2(85,85)
			icon.free()
		result[character] = {"surfaces": surfaces, "ui": ui}
	var file := FileAccess.open(args[0], FileAccess.WRITE)
	if file == null:
		quit(2)
		return
	file.store_string(JSON.stringify(result, "  "))
	file.close()
	print("PCK_PREFLIGHT_COMPLETE")
	quit(0)
