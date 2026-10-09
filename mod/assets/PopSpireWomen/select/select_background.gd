extends Control
## Silent selection movie or Godot presentation. Never calls gameplay or consumes input.
signal presentation_changed(active: bool, reduced_motion: bool)

const PUPPET = preload("res://PopSpireWomen/animation/puppet.gd")
const SCHEMA = preload("res://PopSpireWomen/animation/rig_schema.gd")
const VIDEO = preload("res://PopSpireWomen/animation/selection_video.gd")
const SETTINGS = preload("res://PopSpireWomen/config/settings.gd")
const SETTINGS_ENABLED = "PopSpireWomen/select/enabled"
const SETTINGS_REDUCED = "PopSpireWomen/select/reduced_motion"
const CHARACTERS = ["IRONCLAD", "SILENT", "REGENT", "NECROBINDER", "DEFECT"]

@export_enum("IRONCLAD", "SILENT", "REGENT", "NECROBINDER", "DEFECT") var character_entry := "SILENT"
@export_file("*.png", "*.webp") var poster_path := ""
@export_file("*.ogv") var video_path := ""
@export_file("*.png", "*.webp") var background_path := ""
@export_file("*.json") var rig_path := ""
@export_file("*.tscn") var overlay_scene_path := ""
@export_file("*.tscn") var original_scene_path := ""
@export var figure_position := Vector2(0.62, 0.94)
@export_range(0.1, 2.0) var figure_height := 0.88
@export_range(1.0, 60.0) var loop_seconds := 8.0

@onready var _poster: TextureRect = $Poster
@onready var _background: TextureRect = $Background
@onready var _overlay: Control = $Overlay
@onready var _media: Node2D = $ViewportMedia
@onready var _video_poster: TextureRect = $ViewportMedia/VideoPoster
var state := "inactive"
var _enabled := false
var _reduced := false
var _ready_once := false
var _original: Node
var _puppet: Node2D
var _seconds := 0.0
var _warnings: Dictionary = {}
var _video: VideoStreamPlayer
var _freeze_rig := false
var _preference_override := false

func _enter_tree() -> void:
	if _ready_once: _refresh.call_deferred()

func _ready() -> void:
	_ready_once = true
	var preferences := SETTINGS.read()
	if not _preference_override:
		_enabled = SETTINGS.enabled(preferences, character_entry) and bool(ProjectSettings.get_setting(SETTINGS_ENABLED, true))
		_reduced = bool(ProjectSettings.get_setting(SETTINGS_REDUCED, preferences.ReducedMotion))
	visibility_changed.connect(_visibility_changed)
	resized.connect(_layout)
	_refresh()

func set_preferences(enabled: bool, reduced_motion: bool) -> void:
	_preference_override = true
	if _enabled == enabled and _reduced == reduced_motion: return
	_enabled = enabled
	_reduced = reduced_motion
	if _ready_once and is_inside_tree(): _refresh()

func configure(poster: String, rig: String, video := "") -> void:
	poster_path = poster
	rig_path = rig
	video_path = video
	if _ready_once and is_inside_tree(): _refresh()

func _visibility_changed() -> void:
	if _ready_once and is_inside_tree(): _refresh()

func _clear_layers() -> void:
	_stop_video()
	_video_poster.texture = null
	_media.hide()
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
	# On re-entry the parent's visibility notification precedes child _enter_tree.
	# _enter_tree schedules a refresh after the entire subtree is attached.
	if not is_inside_tree() or is_queued_for_deletion() or not _media.is_inside_tree(): return
	_clear_layers()
	set_process(false)
	# Viewport media may extend outside the original background's local rectangle.
	# The viewport clips it; the legacy figure still uses its local clipping boundary.
	clip_contents = video_path.is_empty()
	_seconds = 0.0
	if not is_visible_in_tree():
		state = "hidden"
		presentation_changed.emit(false, _reduced)
		return
	if not _enabled:
		_show_original()
		return
	set_process(true)
	if not video_path.is_empty() and not _reduced and _start_video():
		_show_overlay()
		presentation_changed.emit(true, _reduced)
		return
	_show_static()

func _show_static() -> void:
	# A configured movie needs a composition-matched poster, including under reduced motion.
	# If the poster is missing, the Godot rig is kept still until the movie is available again.
	_freeze_rig = _reduced or not video_path.is_empty()
	if not video_path.is_empty():
		_video_poster.texture = _texture(poster_path)
		if _video_poster.texture != null:
			_media.show()
			state = "poster"
			_layout()
			_show_overlay()
			presentation_changed.emit(true, _reduced)
			return
	_poster.texture = _texture(poster_path)
	_poster.show()
	if not rig_path.is_empty():
		_puppet = PUPPET.new()
		$Layers.add_child(_puppet)
		if _puppet.load_rig(rig_path, character_entry):
			_puppet.surface = "select"
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

func _start_video() -> bool:
	var reason := VIDEO.inspect(video_path)
	if not reason.is_empty():
		_warn_once(reason + "; using static fallback")
		return false
	var stream := ResourceLoader.load(video_path, "VideoStreamTheora") as VideoStreamTheora
	if stream == null: return false
	_video = VideoStreamPlayer.new()
	_video.name = "Video"
	_video.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_video.expand = true
	_video.volume = 0.0
	_video.loop = true
	_media.add_child(_video)
	_video.stream = stream
	var texture := _video.get_video_texture()
	if texture == null or texture.get_width() <= 0 or texture.get_height() <= 0:
		_stop_video()
		_warn_once("Video decoder unavailable; using static fallback")
		return false
	_media.show()
	_poster.hide()
	state = "video"
	_layout()
	_video.play()
	return true

func _stop_video() -> void:
	if is_instance_valid(_video):
		_video.stop()
		_video.stream = null
		_dispose(_video)
	_video = null

func _texture(path: String) -> Texture2D:
	if SCHEMA.owned(path) and ResourceLoader.exists(path, "Texture2D"):
		return ResourceLoader.load(path, "Texture2D") as Texture2D
	return null

func _process(delta: float) -> void:
	if _media.visible: _layout()
	if state == "video" and (not is_instance_valid(_video) or not _video.is_playing()):
		_stop_video()
		# Also retire the old overlay before creating the fallback presentation.
		_clear_layers()
		_show_static()
		return
	if state != "rig" or _freeze_rig or not is_visible_in_tree(): return
	_seconds += delta
	_animate()

func _animate() -> void:
	if is_instance_valid(_puppet):
		_puppet.sample_animation("select", fposmod(_seconds / maxf(loop_seconds,1), 1), _freeze_rig, _seconds)

func _layout() -> void:
	if is_instance_valid(_media) and _media.visible:
		# The game's 2560x1200 background parent can pan/zoom. Cancel its complete
		# canvas transform so a movie composed in screen coordinates stays in the UI safe area.
		var canvas := get_global_transform_with_canvas()
		if not is_zero_approx(canvas.determinant()): _media.transform = canvas.affine_inverse()
		var viewport_size := get_viewport_rect().size
		if _video_poster.texture != null:
			var rect: Rect2 = VIDEO.cover(_video_poster.texture.get_size(), viewport_size)
			_video_poster.position = rect.position
			_video_poster.size = rect.size
		if is_instance_valid(_video) and _video.get_video_texture() != null:
			var rect: Rect2 = VIDEO.cover(_video.get_video_texture().get_size(), viewport_size)
			_video.position = rect.position
			_video.size = rect.size
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
	set_process(false)
	state = "unavailable"
	presentation_changed.emit(false, _reduced)
	if character_entry not in CHARACTERS: return
	var path := original_scene_path
	# PCK aliases have no original scene UID. They cannot resolve back to this replacement.
	if not path.is_empty():
		if path != SETTINGS.original_select(character_entry):
			_warn_once("Invalid original selection alias")
			return
	else:
		path = SETTINGS.original_select(character_entry)
		if not ResourceLoader.exists(path, "PackedScene"):
			# Standalone / historical DLL host only. A PCK host must never use the override path.
			if FileAccess.file_exists("res://PopSpireWomen/config/pck-build.json"):
				_warn_once("Original selection alias unavailable")
				return
			path = "res://scenes/screens/char_select/char_select_bg_%s.tscn" % character_entry.to_lower()
	if path == scene_file_path:
		_warn_once("Recursive selection fallback refused")
		return
	if ResourceLoader.exists(path, "PackedScene"):
		var scene := ResourceLoader.load(path, "PackedScene") as PackedScene
		if scene != null:
			_original = scene.instantiate()
			if _original != null:
				add_child(_original)
				state = "original"
	if state == "unavailable": _warn_once("Original background unavailable in this host")

func _exit_tree() -> void:
	if not _ready_once: return
	_clear_layers()
	set_process(false)
	state = "inactive"
	presentation_changed.emit(false, _reduced)

func _warn_once(message: String) -> void:
	if not _warnings.has(message):
		_warnings[message] = true
		push_warning("[PopSpireWomen] " + message)
