extends SceneTree
## Deliberately no preload: mount the packed assets before loading their runtime.
func _initialize() -> void: _run.call_deferred()

func _run() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 3 or not ProjectSettings.load_resource_pack(args[0]):
		quit(2)
		return
	var paths: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[1]))
	if not paths is Array:
		quit(2)
		return
	var contract = load("res://PopSpireWomen/animation/selection_video.gd")
	var result := {}
	for path: String in paths:
		var reason: String = contract.inspect(path)
		var check := {"ok": false, "reason": reason}
		if reason.is_empty():
			var video := VideoStreamPlayer.new()
			video.volume = 0.0
			video.expand = true
			root.add_child(video)
			video.stream = load(path) as VideoStreamTheora
			video.play()
			await create_timer(0.25).timeout
			var texture := video.get_video_texture()
			check.ok = video.is_playing() and video.stream_position > 0 and texture != null and texture.get_width() > 0
			check["position"] = video.stream_position
			check["size"] = [texture.get_width(), texture.get_height()] if texture != null else []
			if not check.ok: check.reason = "Packed Theora failed to decode/advance"
			video.stop()
			video.stream = null
			video.free()
		result[path] = check
	var file := FileAccess.open(args[2], FileAccess.WRITE)
	if file == null:
		quit(2)
		return
	file.store_string(JSON.stringify(result, "  "))
	file.close()
	print("PCK_VIDEO_READBACK_COMPLETE")
	quit(0)
