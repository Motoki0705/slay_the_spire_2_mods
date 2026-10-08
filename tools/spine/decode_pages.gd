extends SceneTree
## Decode selected embedded CTEX images only. Never load a game Resource or PCK.


func fail(message: String) -> void:
	printerr("spine image decode: " + message)
	quit(1)


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 1:
		fail("expected one jobs.json argument")
		return
	var document = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if not document is Dictionary or not document.get("jobs") is Array:
		fail("invalid jobs document")
		return
	var results: Array = []
	for job in document["jobs"]:
		var encoded := FileAccess.get_file_as_bytes(job["input"])
		var image := Image.new()
		var status: Error
		if job["encoding"] == "webp":
			status = image.load_webp_from_buffer(encoded)
		elif job["encoding"] == "png":
			status = image.load_png_from_buffer(encoded)
		else:
			fail("unsupported encoding")
			return
		if status != OK or image.is_empty():
			fail("image decode failed: " + job["name"])
			return
		if image.get_width() != int(job["size"][0]) or image.get_height() != int(job["size"][1]):
			fail("image/atlas dimension mismatch: " + job["name"])
			return
		# Apply the same RGB8/RGBA8 format conversion used by Godot's CTEX loader.
		image.convert(int(job["format"]))
		var pixels := image.get_data()
		var png := image.save_png_to_buffer()
		var reloaded := Image.new()
		if reloaded.load_png_from_buffer(png) != OK:
			fail("PNG verification decode failed")
			return
		reloaded.convert(int(job["format"]))
		if reloaded.get_data() != pixels:
			fail("PNG pixels differ from decoded CTEX pixels")
			return
		if FileAccess.file_exists(job["output"]):
			fail("refusing to overwrite output")
			return
		var file := FileAccess.open(job["output"], FileAccess.WRITE)
		if file == null:
			fail("could not create PNG")
			return
		file.store_buffer(png)
		file.close()
		if FileAccess.get_file_as_bytes(job["output"]) != png:
			fail("saved PNG bytes differ from the verified buffer")
			return
		var digest := HashingContext.new()
		digest.start(HashingContext.HASH_SHA256)
		digest.update(pixels)
		results.append({"name": job["name"], "size": [image.get_width(), image.get_height()],
			"format": image.get_format(), "pixels_sha256": digest.finish().hex_encode(),
			"png_pixels_equal": true, "alpha": image.detect_alpha()})
	var result := FileAccess.open(document["result"], FileAccess.WRITE)
	if result == null:
		fail("could not create decode results")
		return
	result.store_string(JSON.stringify({"engine": Engine.get_version_info(), "pages": results}))
	result.close()
	quit(0)
