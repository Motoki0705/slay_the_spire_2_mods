extends SceneTree

func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 1 or not ProjectSettings.load_resource_pack(args[0], false):
		printerr("PCK mount failed")
		quit(1)
		return
	for id in ["ironclad", "silent", "regent", "necrobinder", "defect"]:
		var scene := load("res://PopSpireWomen/select/%s.tscn" % id) as PackedScene
		if scene == null:
			quit(1)
			return
		var node := scene.instantiate()
		if not node is Control or node.character_entry != id.to_upper():
			printerr("Invalid packed descriptor: ", id)
			quit(1)
			return
		node.free()
	var bridge := load("res://PopSpireWomen/animation/driver_overlay.tscn") as PackedScene
	if bridge == null:
		printerr("Missing animation adapter")
		quit(1)
		return
	var instance := bridge.instantiate()
	instance.free()
	if DirAccess.dir_exists_absolute("res://PopSpireWomen/test-fixtures"):
		printerr("Development fixtures leaked into production pack")
		quit(1)
		return
	print("PACK_CHECKS=5 descriptors instantiate from standalone PCK; no fixture")
	quit(0)
