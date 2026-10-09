extends SceneTree
## Run ONLY in a dedicated copied game, --force-steam=off, with a verified custom user dir.
## The original main scene is never instantiated. No save, input, mod-manager or command calls.
const CHARACTERS = ["ironclad", "silent", "regent", "necrobinder", "defect"]
var report := {"checks": [], "failures": 0, "game_main_started": false}
var output := ""

func check(condition: bool, label: String) -> void:
	report.checks.append({"ok": condition, "label": label})
	if not condition: report.failures += 1
	print("PASS " if condition else "FAIL ", label)
	if not output.is_empty():
		var file := FileAccess.open(output, FileAccess.WRITE)
		file.store_string(JSON.stringify(report, "  "))
		file.close()

func _initialize() -> void: _run.call_deferred()

func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var config_path := args[0] if args.size() == 1 else ""
	var config: Variant = JSON.parse_string(FileAccess.get_file_as_string(config_path))
	if not config is Dictionary:
		quit(2)
		return
	var actual := OS.get_user_data_dir().replace("\\", "/")
	var expected: String = config.user_dir.replace("\\", "/")
	var isolated: bool = actual.to_lower() == expected.to_lower() and "popspirewomenpck33" in actual.to_lower()
	if not isolated or not "--force-steam=off" in OS.get_cmdline_args():
		printerr("Probe requires verified isolation and --force-steam=off")
		quit(2)
		return
	output = config.output
	report.user_dir = actual
	report.engine = Engine.get_version_info()
	check(isolated, "isolated user://; main scene not started")
	check(ClassDB.class_exists("SpineSprite"), "original native SpineSprite is registered")
	for character: String in config.get("characters", CHARACTERS):
		check(not ResourceLoader.has_cached("res://scenes/creature_visuals/%s.tscn" % character), character + " combat not cached before pack")
	# Demonstrate the host's cache behavior explicitly. This function releases all old
	# resources before the cold-path checks; the shipped runtime never clears host caches.
	probe_cache(config.pck)
	var settings_script := load("res://PopSpireWomen/config/settings.gd")
	var preferences: Dictionary = settings_script.read()
	check(preferences.Enabled and preferences.EnabledCharacters.size() == 5, "omitted settings enable all five")
	for character: String in config.get("characters", CHARACTERS):
		for surface: String in ["combat", "merchant", "rest"]:
			var path: String = {"combat": "res://scenes/creature_visuals/%s.tscn", "merchant": "res://scenes/merchant/characters/%s_merchant.tscn", "rest": "res://scenes/rest_site/characters/%s_rest_site.tscn"}[surface] % character
			var scene := ResourceLoader.load(path, "PackedScene") as PackedScene
			check(scene != null, character + "/" + surface + " load")
			if scene == null: continue
			var node := scene.instantiate()
			var script := node.get_script() as Script
			var script_name: String = {"combat":"NCreatureVisuals.cs", "merchant":"NMerchantCharacter.cs", "rest":"NRestSiteCharacter.cs"}[surface]
			check(script != null and script.resource_path.ends_with(script_name), character + "/" + surface + " original C# script retained")
			var overlay := node.get_node_or_null("PopSpireWomenOverlay")
			check(overlay != null and overlay.get_index() == node.get_child_count() - 1, character + "/" + surface + " overlay is last child")
			if overlay != null:
				var driver: Node = overlay.get_node_or_null(overlay.driver_path)
				check(driver != null and driver.get_class() == "SpineSprite", character + "/" + surface + " original driver path")
				if driver != null and surface == "combat": await exercise_driver(driver, overlay, character)
			if character == "necrobinder" and surface == "rest": check(node.get_node("Osty").get_class() == "SpineSprite", "Osty independent rest node retained")
			if character == "regent" and surface == "combat": check(node.has_node("Visuals/Weapons/WeaponAnim1") and node.has_node("Visuals/Weapons/WeaponAnim2"), "Regent independent weapons retained")
			node.free()
		await check_selection(character)
		var dimensions := {"portrait": Vector2(132,195), "locked": Vector2(132,195), "map": Vector2(49,64), "top": Vector2(85,85), "outline": Vector2(85,85)}
		var paths := {"portrait": "res://images/packed/character_select/char_select_%s.png", "locked": "res://images/packed/character_select/char_select_%s_locked.png", "map": "res://images/packed/map/icons/map_marker_%s.png", "top": "res://images/ui/top_panel/character_icon_%s.png", "outline": "res://images/ui/top_panel/character_icon_%s_outline.png"}
		for name: String in paths:
			var texture := ResourceLoader.load(paths[name] % character, "Texture2D") as Texture2D
			var own := ResourceLoader.load("res://PopSpireWomen/ui/%s/%s.png" % [character,name], "Texture2D") as Texture2D
			check(texture is CompressedTexture2D and texture.get_size() == dimensions[name], character + "/" + name + " original path resolves CompressedTexture2D and size")
			if texture != null and own != null:
				check(texture.get_image().get_data() == own.get_image().get_data(), character + "/" + name + " remap returns our pixels")
				var uid := ResourceLoader.get_resource_uid(paths[name] % character)
				if uid != ResourceUID.INVALID_ID:
					var by_uid := ResourceLoader.load(ResourceUID.id_to_text(uid), "Texture2D") as Texture2D
					check(by_uid == texture, character + "/" + name + " original UID/cache agrees with path")
		var icon_scene := load("res://scenes/ui/character_icons/%s_icon.tscn" % character) as PackedScene
		var icon := icon_scene.instantiate()
		check(icon is TextureRect and icon.get_child_count() == 0 and icon.get_script() == null, character + " icon remains plain TextureRect")
		icon.free()
	var file := FileAccess.open(output, FileAccess.WRITE)
	report.completed = true
	file.store_string(JSON.stringify(report, "  "))
	file.close()
	print("PCK_NATIVE_COMPLETE checks=", report.checks.size(), " failures=", report.failures)
	quit(0 if report.failures == 0 else 1)

func probe_cache(pck: String) -> void:
	var path := "res://images/packed/character_select/char_select_ironclad.png"
	var cached := ResourceLoader.load(path, "Texture2D") as Texture2D
	check(cached is CompressedTexture2D, "original texture can be preloaded before mounting")
	check(ProjectSettings.load_resource_pack(pck), "local resource PCK loaded")
	var reused := ResourceLoader.load(path, "Texture2D") as Texture2D
	check(reused == cached, "warm cache keeps existing instance; hot reload is unsupported")
	var fresh := ResourceLoader.load(path, "Texture2D", ResourceLoader.CACHE_MODE_IGNORE_DEEP) as Texture2D
	var own := ResourceLoader.load("res://PopSpireWomen/ui/ironclad/portrait.png", "Texture2D") as Texture2D
	check(fresh.get_image().get_data() == own.get_image().get_data() and fresh.get_image().get_data() != cached.get_image().get_data(), "fresh VFS read gets our pixels while warm instance stays original")

func check_selection(character: String) -> void:
	var path := "res://scenes/screens/char_select/char_select_bg_%s.tscn" % character
	var alias := "res://PopSpireWomen/compat/original_select/%s.tscn" % character
	var replaced := ResourceLoader.load(path, "PackedScene") as PackedScene
	var original := ResourceLoader.load(alias, "PackedScene") as PackedScene
	check(replaced != null and original != null and replaced != original, character + " alias has separate resource identity")
	if replaced == null or original == null: return
	var wrapper := replaced.instantiate()
	root.add_child(wrapper)
	await process_frame
	check(wrapper.state == "custom", character + " selection router starts custom scene")
	var background: Node = wrapper.get_child(0)
	check(background.state == "rig", character + " selection production rig starts")
	background.set_preferences(false, false)
	await process_frame
	check(background.state == "original" and background._original.scene_file_path == alias, character + " disable falls back to alias without recursion")
	background.set_preferences(true, false)
	background.configure("", "res://PopSpireWomen/rigs/missing.json")
	await process_frame
	check(background.state == "original", character + " missing rig falls back without recursion")
	wrapper.queue_free()
	await process_frame

func exercise_driver(original_driver: Node, original_overlay: Node, character: String) -> void:
	# Isolate the native skeleton/mesh reader from game callbacks requiring a running NGame.
	# Full original typed scenes remain detached above; game _Ready/combat logic is parent QA.
	var host := Node2D.new()
	var driver: Node2D = ClassDB.instantiate("SpineSprite")
	driver.name = "Driver"
	driver.set("skeleton_data_res", original_driver.get("skeleton_data_res"))
	host.add_child(driver)
	var overlay: Node2D = load("res://PopSpireWomen/animation/driver_overlay.tscn").instantiate()
	overlay.character_entry = character.to_upper()
	overlay.rig_path = original_overlay.rig_path
	overlay.driver_path = NodePath("../Driver")
	host.add_child(overlay)
	root.add_child(host)
	var state: Object = driver.call("get_animation_state")
	state.call("set_animation", "idle_loop", true, 0)
	for i in 5: await process_frame
	check(overlay.state == "active", character + " native idle track drives actual rig/mesh suppression")
	var track: Object = state.call("get_current", 0)
	var time_before: float = track.call("get_track_time")
	for i in 4: await process_frame
	check(float(track.call("get_track_time")) > time_before, character + " original native track still advances")
	var meshes: Array = []
	for child: Node in driver.get_children():
		if child.get_class() == "SpineMesh2D": meshes.append(child)
	check(meshes.any(func(mesh): return not mesh.visible), character + " only direct mesh drawing suppressed")
	overlay._fallback("Deliberate probe failure")
	check(meshes.all(func(mesh): return mesh.visible), character + " fallback restores original mesh visibility")
	check(driver.visible and driver.process_mode != Node.PROCESS_MODE_DISABLED, character + " native driver stays visible and processing")
	host.queue_free()
	await process_frame
