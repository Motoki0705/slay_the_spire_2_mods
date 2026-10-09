extends SceneTree
## A labeled source-art comparison. This is neither runtime QA nor generated video.

const CHARACTERS := ["ironclad", "silent", "regent", "necrobinder", "defect"]
const CONTEXTS := ["SELECT / SOURCE POSE", "COMBAT / READY", "MERCHANT / APPRAISAL", "REST / SEATED"]

func _initialize() -> void:
	call_deferred("_render")

func _label(parent: Node, content: String, location: Vector2, font_size: int, color: Color) -> void:
	var label := Label.new()
	label.text = content
	label.position = location
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	parent.add_child(label)

func _picture(parent: Node, path: String, box: Rect2) -> void:
	var source := Image.load_from_file(ProjectSettings.globalize_path(path))
	if source == null or source.is_empty():
		push_error("Gallery source unavailable: " + path)
		quit(2)
		return
	var art := TextureRect.new()
	art.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	art.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	art.texture = ImageTexture.create_from_image(source)
	art.position = box.position
	art.size = box.size
	art.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(art)

func _render() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 1:
		push_error("Expected absolute output directory")
		quit(2)
		return
	var output := args[0]
	DirAccess.make_dir_recursive_absolute(output)
	root.size = Vector2i(1560, 860)
	root.content_scale_size = root.size
	var receipts: Array = []
	for character: String in CHARACTERS:
		var board := Control.new()
		board.size = Vector2(1560, 860)
		root.add_child(board)
		var background := ColorRect.new()
		background.color = Color("111820")
		background.size = board.size
		board.add_child(background)
		_label(board, "POP SPIRE WOMEN   /   " + character.to_upper(), Vector2(28, 18), 29, Color("ead8ab"))
		_label(board, "v0.2 SOURCE ART COMPARISON  -  NOT IN-GAME FOOTAGE", Vector2(30, 58), 15, Color("adb8c4"))
		var sources := ["body.png", "combat_body.png", "merchant_body.png", "rest_body_v03.png"]
		var items: Array = []
		for index in 4:
			var x := 20 + index * 386
			var panel := ColorRect.new()
			panel.color = Color("202a34")
			panel.position = Vector2(x, 102)
			panel.size = Vector2(374, 708)
			board.add_child(panel)
			_label(board, CONTEXTS[index], Vector2(x + 14, 118), 18, Color("d9e0e7"))
			var path := "res://PopSpireWomen/art/%s/%s" % [character, sources[index]]
			var box := Rect2(x + 8, 152, 358, 632)
			if index == 0 and character == "regent":
				_picture(board, "res://PopSpireWomen/art/regent/layers/throne.png", box)
			_picture(board, path, box)
			items.append({"context": CONTEXTS[index], "image": path, "sha256": FileAccess.get_sha256(path)})
		_label(board, "Character design retained. Scene-specific pose derivatives selected under delegated production authority.", Vector2(28, 825), 15, Color("aab5be"))
		for frame in 4:
			await process_frame
		await RenderingServer.frame_post_draw
		var path := output.path_join(character + "-poses.png")
		var capture := root.get_texture().get_image()
		capture.convert(Image.FORMAT_RGB8)
		if capture.save_png(path) != OK:
			quit(2)
			return
		receipts.append({"character": character, "image": path.get_file(), "sha256": FileAccess.get_sha256(path), "sources": items})
		root.remove_child(board)
		board.queue_free()
		await process_frame
	var receipt := FileAccess.open(output.path_join("source-gallery.json"), FileAccess.WRITE)
	receipt.store_string(JSON.stringify({"schema": 1, "scope": "source-art comparison, not game or motion verification", "width": 1560, "height": 860, "images": receipts}, "  "))
	print("Rendered five alpha-composited context comparisons without modifying input artwork.")
	quit(0)
