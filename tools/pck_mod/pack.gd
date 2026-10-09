extends SceneTree
## PCKPacker adds only the reviewed file map. No project/UID cache/C#/extensions/autoloads.
func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 2:
		quit(2)
		return
	var files: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if not files is Dictionary:
		quit(2)
		return
	var pack := PCKPacker.new()
	if pack.pck_start(args[1]) != OK:
		quit(2)
		return
	for path: String in files:
		if pack.add_file("res://" + path, files[path]) != OK:
			push_error("Cannot pack " + path)
			quit(2)
			return
	if pack.flush() != OK:
		quit(2)
		return
	print("PCK_PACK_COMPLETE files=", files.size())
	quit(0)
