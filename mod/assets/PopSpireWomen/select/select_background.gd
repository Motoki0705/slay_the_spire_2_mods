extends Control
## Godot mesh/layer background. No video, audio, gameplay calls or input handlers.
signal presentation_changed(active: bool, reduced_motion: bool)

const PUPPET = preload("res://PopSpireWomen/animation/puppet.gd")
const SCHEMA = preload("res://PopSpireWomen/animation/rig_schema.gd")
const SETTINGS_ENABLED = "PopSpireWomen/select/enabled"
const SETTINGS_REDUCED = "PopSpireWomen/select/reduced_motion"
const CHARACTERS = ["IRONCLAD", "SILENT", "REGENT", "NECROBINDER", "DEFECT"]

@export_enum("IRONCLAD", "SILENT", "REGENT", "NECROBINDER", "DEFECT") var character_entry := "SILENT"
@export_file("*.png", "*.webp") var poster_path := ""
@export_file("*.png", "*.webp") var background_path := ""
@export_file("*.json") var rig_path := ""
@export_file("*.tscn") var overlay_scene_path := ""
@export var figure_position := Vector2(0.62, 0.94)
@export_range(0.1, 2.0) var figure_height := 0.88
@export_range(1.0, 60.0) var loop_seconds := 8.0

@onready var _poster: TextureRect = $Poster
@onready var _background: TextureRect = $Background
@onready var _overlay: Control = $Overlay
var state := "inactive"
var _enabled := false
var _reduced := false
var _ready_once := false
var _original: Node
var _puppet: Node2D
var _seconds := 0.0
var _warnings: Dictionary = {}

func _enter_tree() -> void:
	if _ready_once: _refresh.call_deferred()

func _ready() -> void:
	_ready_once = true
	_enabled = bool(ProjectSettings.get_setting(SETTINGS_ENABLED, false))
	_reduced = bool(ProjectSettings.get_setting(SETTINGS_REDUCED, false))
	visibility_changed.connect(_visibility_changed)
	resized.connect(_layout)
	_refresh()

func set_preferences(enabled: bool, reduced_motion: bool) -> void:
	if _enabled == enabled and _reduced == reduced_motion: return
	_enabled = enabled
	_reduced = reduced_motion
	if _ready_once and is_inside_tree(): _refresh()

func configure(poster: String, rig: String) -> void:
	poster_path = poster
	rig_path = rig
	if _ready_once and is_inside_tree(): _refresh()

func _visibility_changed() -> void:
	if _ready_once and is_inside_tree(): _refresh()

func _clear_layers() -> void:
	if is_instance_valid(_original): _dispose(_original)
	_original = null
	if is_instance_valid(_puppet): _dispose(_puppet)
	_puppet = null
	for child in _overlay.get_children():
		if child.has_method("set_presentation_state"): child.set_presentation_state(false, _reduced)
		_dispose(child)
	_overlay.hide()
	_poster.texture = null
	_background.texture = null

func _dispose(node: Node) -> void:
	if node is CanvasItem: node.hide()
	node.process_mode = Node.PROCESS_MODE_DISABLED
	node.queue_free()

func _refresh() -> void:
	if not is_inside_tree() or is_queued_for_deletion(): return
	_clear_layers()
	_seconds = 0.0
	if not is_visible_in_tree():
		state = "hidden"
		presentation_changed.emit(false, _reduced)
		return
	if not _enabled:
		_show_original()
		return
	_poster.texture = _texture(poster_path)
	_poster.show()
	if not rig_path.is_empty():
		_puppet = PUPPET.new()
		$Layers.add_child(_puppet)
		if _puppet.load_rig(rig_path, character_entry):
			_background.texture = _texture(background_path)
			_poster.hide()
			state = "rig"
			_layout()
			_animate()
		else:
			_warn_once(_puppet.last_error + "; using static fallback")
			_dispose(_puppet)
			_puppet = null
	if _puppet == null:
		if _poster.texture == null:
			_show_original()
			return
		state = "poster"
	_show_overlay()
	presentation_changed.emit(true, _reduced)

func _texture(path: String) -> Texture2D:
	if SCHEMA.owned(path) and ResourceLoader.exists(path, "Texture2D"):
		return ResourceLoader.load(path, "Texture2D") as Texture2D
	return null

func _process(delta: float) -> void:
	if state != "rig" or _reduced or not is_visible_in_tree(): return
	_seconds += delta
	_animate()

func _animate() -> void:
	if is_instance_valid(_puppet):
		_puppet.sample_animation("select", fposmod(_seconds / maxf(loop_seconds,1), 1), _reduced, _seconds)

func _layout() -> void:
	if is_instance_valid(_puppet) and not _puppet.rig.is_empty():
		_puppet.position = size * figure_position
		_puppet.scale = Vector2.ONE * size.y * figure_height / float(_puppet.rig.canvas[1])

func _show_overlay() -> void:
	if overlay_scene_path.is_empty(): return
	if not SCHEMA.owned(overlay_scene_path, ".tscn") or not ResourceLoader.exists(overlay_scene_path, "PackedScene"):
		_warn_once("Overlay unavailable")
		return
	var scene := ResourceLoader.load(overlay_scene_path, "PackedScene") as PackedScene
	if scene == null: return
	var instance := scene.instantiate()
	_overlay.add_child(instance)
	_overlay.show()
	# #21 owns Regent's seven constellation hit regions and their semantics.
	# The background and overlay container stay IGNORE; interactive children can opt in.
	if instance.has_method("set_presentation_state"): instance.set_presentation_state(true, _reduced)

func _show_original() -> void:
	state = "unavailable"
	presentation_changed.emit(false, _reduced)
	if character_entry not in CHARACTERS: return
	var path := "res://scenes/screens/char_select/char_select_bg_%s.tscn" % character_entry.to_lower()
	if ResourceLoader.exists(path, "PackedScene"):
		var scene := ResourceLoader.load(path, "PackedScene") as PackedScene
		if scene != null:
			_original = scene.instantiate()
			add_child(_original)
			state = "original"
	if state == "unavailable": _warn_once("Original background unavailable in this host")

func _exit_tree() -> void:
	if not _ready_once: return
	_clear_layers()
	state = "inactive"
	presentation_changed.emit(false, _reduced)

func _warn_once(message: String) -> void:
	if not _warnings.has(message):
		_warnings[message] = true
		push_warning("[PopSpireWomen] " + message)
