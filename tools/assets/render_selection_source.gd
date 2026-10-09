extends SceneTree
## Render existing authored Godot layers into a UI-free video input, in screen coordinates.

const CHARACTERS := ["ironclad", "silent", "regent", "necrobinder", "defect"]

func _initialize() -> void:
	call_deferred("_render")

func _render() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 1:
		push_error("Expected an absolute output directory after --")
		quit(2)
		return
	var output := args[0]
	root.size = Vector2i(1920, 1080)
	root.content_scale_size = Vector2i(1920, 1080)
	var receipts: Array = []
	for character: String in CHARACTERS:
		var source := "res://PopSpireWomen/select/production/%s.tscn" % character
		var packed := load(source) as PackedScene
		if packed == null:
			quit(2)
			return
		var scene := packed.instantiate() as Control
		# Hover controls remain a live independent layer in the game, never pixels in the movie.
		scene.overlay_scene_path = ""
		scene.set("video_path", "")
		scene.poster_path = ""
		root.add_child(scene)
		scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		scene.set_preferences(true, true)
		for frame in 5:
			await process_frame
		await RenderingServer.frame_post_draw
		if scene.state != "rig":
			push_error("Selection rig unavailable: " + character)
			quit(2)
			return
		var folder := output.path_join(character)
		DirAccess.make_dir_recursive_absolute(folder)
		var path := folder.path_join("selection-v02-input.png")
		if FileAccess.file_exists(path):
			push_error("Refusing to overwrite video input: " + path)
			quit(2)
			return
		var picture := root.get_texture().get_image()
		picture.convert(Image.FORMAT_RGB8)
		if picture.save_png(path) != OK:
			quit(2)
			return
		receipts.append({"character": character, "output": path.get_file(), "width": picture.get_width(),
			"height": picture.get_height(), "sha256": FileAccess.get_sha256(path),
			"scene": source, "scene_sha256": FileAccess.get_sha256(source),
			"rig": scene.rig_path, "rig_sha256": FileAccess.get_sha256(scene.rig_path),
			"background": scene.background_path, "background_sha256": FileAccess.get_sha256(scene.background_path),
			"presentation": "frozen authored Godot layers; no UI, hover motifs, image generation or gameplay"})
		root.remove_child(scene)
		scene.queue_free()
		await process_frame
	var receipt := FileAccess.open(output.path_join("selection-inputs-v02.json"), FileAccess.WRITE)
	receipt.store_string(JSON.stringify({"schema": 1, "renderer": "Godot 4.5.1 standalone", "captures": receipts}, "  "))
	print("Rendered five UI-free 1920x1080 selection inputs from existing artwork.")
	quit(0)
