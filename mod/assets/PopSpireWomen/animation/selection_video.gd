extends RefCounted
## Restrict selection media to a complete, single-stream, silent Ogg Theora file.
## Read page headers before opening a native decoder; no external codec or DLL.
const SCHEMA = preload("res://PopSpireWomen/animation/rig_schema.gd")
const MAX_BYTES = 128 * 1024 * 1024

static func inspect(path: String) -> String:
	if not SCHEMA.owned(path, ".ogv") or not FileAccess.file_exists(path): return "Video unavailable"
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null or file.get_length() < 64 or file.get_length() > MAX_BYTES: return "Invalid video size"
	var serial := -1
	var sequence := 0
	var ended := false
	while file.get_position() < file.get_length():
		var header := file.get_buffer(27)
		if ended or header.size() != 27 or header.slice(0,4).get_string_from_ascii() != "OggS" or header[4] != 0: return "Invalid Ogg page"
		var flags := int(header[5])
		if flags & ~7 or header.decode_u32(18) != sequence: return "Invalid Ogg sequence"
		if sequence == 0:
			if flags != 2: return "Missing Ogg beginning"
			serial = header.decode_u32(14)
		elif header.decode_u32(14) != serial or flags & 2:
			return "Video must contain one Theora stream and no audio"
		var segments := file.get_buffer(header[26])
		if segments.size() != header[26]: return "Truncated Ogg segments"
		var bytes := 0
		for length in segments: bytes += length
		if file.get_position() + bytes > file.get_length(): return "Truncated Ogg payload"
		if sequence == 0:
			var packet := file.get_buffer(bytes)
			if packet.size() < 42 or packet[0] != 128 or packet.slice(1,7).get_string_from_ascii() != "theora": return "Expected Theora identification header"
		else:
			file.seek(file.get_position() + bytes)
		sequence += 1
		ended = bool(flags & 4)
	return "" if ended and sequence >= 3 else "Incomplete Theora stream"

static func cover(frame_size: Vector2, viewport_size: Vector2) -> Rect2:
	var factor := maxf(viewport_size.x / frame_size.x, viewport_size.y / frame_size.y)
	var fitted := frame_size * factor
	return Rect2((viewport_size - fitted) * 0.5, fitted)
