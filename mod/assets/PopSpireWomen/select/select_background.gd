extends Control
## Background-only replacement for CharacterModel.CharacterSelectBg.
## No input callbacks, game actions, audio cues, or animation completion awaits.

signal presentation_changed(active: bool, reduced_motion: bool)

const LOADS = preload("res://PopSpireWomen/select/video_loads.gd")
const SETTINGS_ENABLED = "PopSpireWomen/select/enabled"
const SETTINGS_REDUCED = "PopSpireWomen/select/reduced_motion"
const CHARACTERS = ["IRONCLAD", "SILENT", "REGENT", "NECROBINDER", "DEFECT"]
const DECODE_TIMEOUT_MS = 3000

@export_enum("IRONCLAD", "SILENT", "REGENT", "NECROBINDER", "DEFECT") var character_entry: String = "SILENT"
@export_file("*.png", "*.webp") var poster_path: String = ""
@export_file("*.ogv") var video_path: String = ""
@export_file("*.tscn") var overlay_scene_path: String = ""

@onready var _poster: TextureRect = $Poster
@onready var _video: VideoStreamPlayer = $Video
@onready var _overlay: Control = $Overlay

var state: String = "inactive"
var _enabled := false
var _reduced := false
var _generation := 0
var _ready_once := false
var _loads: Node
var _original: Node
var _last_progress_ms := 0
var _last_position := -1.0
var _warnings: Dictionary = {}

func _enter_tree() -> void:
	if _ready_once:
		_refresh.call_deferred()

func _ready() -> void:
	_ready_once = true
	_enabled = bool(ProjectSettings.get_setting(SETTINGS_ENABLED, false))
	_reduced = bool(ProjectSettings.get_setting(SETTINGS_REDUCED, false))
	visibility_changed.connect(_visibility_changed)
	resized.connect(_layout_video)
	# Loop is exclusively owned by Godot; never restart from Finished.
	_video.loop = true
	_video.volume = 0.0
	_refresh()

func set_preferences(enabled: bool, reduced_motion: bool) -> void:
	if _enabled == enabled and _reduced == reduced_motion:
		return
	_enabled = enabled
	_reduced = reduced_motion
	if _ready_once and is_inside_tree():
		_refresh()

func configure(poster: String, video: String) -> void:
	poster_path = poster
	video_path = video
	if _ready_once and is_inside_tree():
		_refresh()

func _visibility_changed() -> void:
	if _ready_once and is_inside_tree():
		_refresh()

func _stop_video() -> void:
	_generation += 1
	if is_instance_valid(_loads):
		_loads.cancel(self)
	_video.stop()
	_video.stream = null
	_video.hide()
	_poster.show()
	_last_position = -1.0

func _clear_layers() -> void:
	if is_instance_valid(_original):
		if _original is CanvasItem:
			_original.hide()
		_original.process_mode = Node.PROCESS_MODE_DISABLED
		_original.queue_free()
	_original = null
	for child in _overlay.get_children():
		if child.has_method("set_presentation_state"):
			child.set_presentation_state(false, _reduced)
		if child is CanvasItem:
			child.hide()
		child.process_mode = Node.PROCESS_MODE_DISABLED
		child.queue_free()
	_overlay.hide()

func _refresh() -> void:
	if not is_inside_tree() or is_queued_for_deletion():
		return
	_stop_video()
	_clear_layers()
	_poster.texture = null
	if not is_visible_in_tree():
		state = "hidden"
		presentation_changed.emit(false, _reduced)
		return
	if not _enabled:
		_show_original()
		return
	if _owned(poster_path) and ResourceLoader.exists(poster_path, "Texture2D"):
		_poster.texture = ResourceLoader.load(poster_path, "Texture2D") as Texture2D
	if _poster.texture == null:
		_warn_once("Poster unavailable; retaining the original background.")
		_show_original()
		return
	state = "poster"
	_show_overlay()
	presentation_changed.emit(true, _reduced)
	if _reduced or video_path.is_empty():
		return
	if not _owned(video_path) or not video_path.ends_with(".ogv") or not ResourceLoader.exists(video_path, "VideoStream"):
		_warn_once("Video unavailable; retaining the poster.")
		return
	state = "loading"
	_last_progress_ms = Time.get_ticks_msec()
	_loads = LOADS.for_tree(get_tree())
	_loads.request(video_path, self, _generation)

func video_loaded(generation: int, resource: Resource) -> void:
	if generation != _generation or not is_inside_tree() or is_queued_for_deletion() or not is_visible_in_tree() or not _enabled or _reduced:
		return
	if not resource is VideoStreamTheora:
		_video_failed()
		return
	_video.stream = resource
	_video.paused = false
	_video.play()
	_last_progress_ms = Time.get_ticks_msec()

func _process(_delta: float) -> void:
	if state != "loading" and state != "playing":
		return
	if _video.stream != null:
		var position := _video.stream_position
		var texture := _video.get_video_texture()
		if _video.is_playing() and position != _last_position and position > 0.0 and texture != null and texture.get_width() > 0:
			_last_position = position
			_last_progress_ms = Time.get_ticks_msec()
			if state != "playing":
				state = "playing"
				_layout_video()
				_video.show()
				_poster.hide()
		elif not _video.is_playing():
			_video_failed()
	if (state == "loading" or state == "playing") and Time.get_ticks_msec() - _last_progress_ms > DECODE_TIMEOUT_MS:
		_video_failed()

func _video_failed() -> void:
	_stop_video()
	state = "poster"
	_warn_once("Video load/decode stopped or timed out; retaining the poster.")

func _layout_video() -> void:
	if not _ready_once:
		return
	var texture := _video.get_video_texture()
	if texture == null or texture.get_width() <= 0 or texture.get_height() <= 0:
		return
	var dimensions := texture.get_size()
	var factor := maxf(size.x / dimensions.x, size.y / dimensions.y)
	_video.size = dimensions * factor
	_video.position = (size - _video.size) * 0.5

func _show_overlay() -> void:
	if overlay_scene_path.is_empty():
		return
	if not _owned(overlay_scene_path) or not ResourceLoader.exists(overlay_scene_path, "PackedScene"):
		_warn_once("Overlay unavailable.")
		return
	var scene := ResourceLoader.load(overlay_scene_path, "PackedScene") as PackedScene
	if scene == null:
		return
	var instance := scene.instantiate()
	_overlay.add_child(instance)
	_overlay.show()
	# Interactive children opt in to mouse PASS; the canvas itself stays IGNORE.
	if instance.has_method("set_presentation_state"):
		instance.set_presentation_state(true, _reduced)

func _show_original() -> void:
	state = "unavailable"
	presentation_changed.emit(false, _reduced)
	if character_entry not in CHARACTERS:
		return
	# Direct original path avoids re-entering Ritsu's CharacterSelectBg getter.
	var path := "res://scenes/screens/char_select/char_select_bg_%s.tscn" % character_entry.to_lower()
	if ResourceLoader.exists(path, "PackedScene"):
		var scene := ResourceLoader.load(path, "PackedScene") as PackedScene
		if scene != null:
			_original = scene.instantiate()
			add_child(_original)
			state = "original"
	if state == "unavailable":
		_warn_once("Original background unavailable in this host.")

func _exit_tree() -> void:
	if not _ready_once:
		return
	_stop_video()
	_clear_layers()
	_poster.texture = null
	state = "inactive"
	presentation_changed.emit(false, _reduced)

func _owned(path: String) -> bool:
	return path.begins_with("res://PopSpireWomen/") and not "/../" in path and not "\\" in path

func _warn_once(message: String) -> void:
	if not _warnings.has(message):
		_warnings[message] = true
		push_warning("[PopSpireWomen] " + message)
