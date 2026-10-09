extends Control
## A small, dependency-free VFS entrypoint. Never reload the overridden original path.
const SETTINGS = preload("res://PopSpireWomen/config/settings.gd")
@export var character_entry := ""
var state := "unavailable"

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var preferences := SETTINGS.read()
	var original := SETTINGS.original_select(character_entry)
	if SETTINGS.enabled(preferences, character_entry):
		var path := "res://PopSpireWomen/select/production/%s.tscn" % character_entry.to_lower()
		var scene := ResourceLoader.load(path, "PackedScene") as PackedScene if ResourceLoader.exists(path, "PackedScene") else null
		if scene != null:
			var node := scene.instantiate()
			if node is Control and node.has_method("set_preferences") and node.get("character_entry") == character_entry:
				node.set("original_scene_path", original)
				add_child(node)
				state = "custom"
				return
			if node != null: node.free()
	if not original.is_empty() and ResourceLoader.exists(original, "PackedScene"):
		var scene := ResourceLoader.load(original, "PackedScene") as PackedScene
		if scene != null:
			var node := scene.instantiate()
			if node != null:
				add_child(node)
				state = "original"
	if state == "unavailable": push_warning("[PopSpireWomen] Original selection alias unavailable")
