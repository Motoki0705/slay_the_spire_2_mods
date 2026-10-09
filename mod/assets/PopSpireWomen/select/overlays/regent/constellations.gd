extends Control
## Cosmetic, non-consuming pointer observation. No buttons, tasks, timers or game calls.
signal constellation_changed(skin_name: String)

const MOTIFS = preload("res://PopSpireWomen/select/overlays/regent/motifs.gd")
const NORMAL_SKIN := "normal"

@export var reference_size := Vector2(2560, 1200)
@export var layout_offset := Vector2.ZERO
@export_range(0.1, 3.0) var layout_scale := 1.0
## Empty arrays use the authored defaults in motifs.gd; overrides keep callback order.
@export var constellation_positions := PackedVector2Array()
@export var constellation_scales := PackedFloat32Array()
@export_range(0.05, 0.5) var transition_seconds := 0.18
@export_range(0.0, 1.0) var idle_line_opacity := 0.13
@export_range(0.0, 1.0) var ambient_opacity := 0.28
@export var star_color := Color("b9d9ef")
@export var hover_color := Color("8edcff")
@export var accent_color := Color("f5bb70")

var hovered_index := -1
var _active := false
var _reduced := false
var _ready_once := false
var _pointer_known := false
var _pointer_position := Vector2.ZERO # Viewport position, transformed on each sample.
var _seconds := 0.0
var _weights := PackedFloat32Array([0, 0, 0, 0, 0, 0, 0])
var _paths: Array = []
var _viewport: Viewport
var _window: Window

func _enter_tree() -> void:
	if _ready_once: _bind_host.call_deferred()

func _ready() -> void:
	_ready_once = true
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	for i in MOTIFS.SKINS.size(): _paths.append(MOTIFS.paths(i))
	visibility_changed.connect(_sync_presentation)
	resized.connect(_layout_changed)
	_bind_host()

func _bind_host() -> void:
	if not is_inside_tree(): return
	_viewport = get_viewport()
	_window = get_window()
	if not _viewport.mouse_exited.is_connected(_pointer_left):
		_viewport.mouse_exited.connect(_pointer_left)
	if not _window.focus_exited.is_connected(_pointer_left):
		_window.focus_exited.connect(_pointer_left)
	_sync_presentation()

func set_presentation_state(active: bool, reduced_motion: bool) -> void:
	_active = active
	_reduced = reduced_motion
	if _reduced:
		_seconds = 0.0
		_snap_weights()
	if _ready_once and is_inside_tree(): _sync_presentation()

func get_active_skin() -> String:
	return NORMAL_SKIN if hovered_index < 0 else MOTIFS.SKINS[hovered_index]

func _presenting() -> bool:
	return _active and is_inside_tree() and is_visible_in_tree() and not is_queued_for_deletion()

func _sync_presentation() -> void:
	var presenting := _presenting()
	var was_observing := is_processing_input()
	set_process_input(presenting)
	set_process(presenting and not _reduced)
	if not presenting:
		_pointer_left()
		_seconds = 0.0
		_weights.fill(0.0)
	elif not was_observing and can_process():
		_resume_pointer()
	queue_redraw()

func _resume_pointer() -> void:
	# Re-evaluate the actual pointer after activation/unpause, not a pre-pause position.
	_pointer_position = get_viewport().get_mouse_position()
	_pointer_known = get_viewport().get_visible_rect().has_point(_pointer_position)
	_sample_pointer()

func _notification(what: int) -> void:
	if what == NOTIFICATION_UNPAUSED and _ready_once and _presenting(): _resume_pointer()

func _pointer_left() -> void:
	_pointer_known = false
	_select(-1)

func _input(event: InputEvent) -> void:
	if not _presenting() or not can_process(): return
	if event is InputEventMouseMotion:
		_pointer_known = true
		_pointer_position = event.position
		_sample_pointer()
	# Never accept_event/set_input_as_handled. Mouse buttons, wheel and keys pass intact.

func _sample_pointer() -> void:
	if not _pointer_known: return
	var local := get_global_transform_with_canvas().affine_inverse() * _pointer_position
	if not Rect2(Vector2.ZERO, size).has_point(local):
		_select(-1)
		return
	var point := _reference_transform().affine_inverse() * local
	var nearest := -1
	var distance := INF
	for i in MOTIFS.SKINS.size():
		var relative: Vector2 = (point - _center(i)) / (MOTIFS.RADII[i] * _motif_scale(i) * 1.25)
		var candidate := relative.length_squared()
		if candidate <= 1.0 and candidate < distance:
			nearest = i
			distance = candidate
	_select(nearest)

func _select(index: int) -> void:
	if hovered_index == index: return
	hovered_index = index
	if _reduced: _snap_weights()
	constellation_changed.emit(get_active_skin())
	queue_redraw()

func _snap_weights() -> void:
	for i in _weights.size(): _weights[i] = 1.0 if i == hovered_index else 0.0

func _process(delta: float) -> void:
	if not _presenting() or _reduced: return
	_seconds = fmod(_seconds + minf(delta, 0.1), 120.0)
	_sample_pointer() # Background parallax/resize can move beneath a stationary pointer.
	for i in _weights.size():
		_weights[i] = move_toward(_weights[i], 1.0 if i == hovered_index else 0.0,
			minf(delta, 0.1) / maxf(transition_seconds, 0.01))
	queue_redraw()

func _layout_changed() -> void:
	if _presenting() and can_process(): _sample_pointer()
	queue_redraw()

func _reference_transform() -> Transform2D:
	var fit := minf(size.x / maxf(reference_size.x, 1.0), size.y / maxf(reference_size.y, 1.0))
	fit = maxf(fit, 0.0001)
	return Transform2D(0.0, Vector2.ONE * fit * maxf(layout_scale, 0.01), 0.0,
		(size - reference_size * fit) * 0.5 + layout_offset * fit)

func _center(index: int) -> Vector2:
	return constellation_positions[index] if index < constellation_positions.size() else MOTIFS.POSITIONS[index]

func _motif_scale(index: int) -> float:
	return maxf(constellation_scales[index], 0.1) if index < constellation_scales.size() else 1.0

func constellation_position(index: int) -> Vector2:
	return _reference_transform() * _center(index)

func _draw() -> void:
	if not _presenting() or _paths.is_empty(): return
	draw_set_transform_matrix(_reference_transform())
	for i in MOTIFS.SKY.size():
		var pulse := 1.0 if _reduced else 0.88 + 0.12 * sin(_seconds * TAU / 6.0 + i * 1.7)
		var color := accent_color if i % 5 == 0 else star_color
		_star(MOTIFS.SKY[i], 1.0 + (i % 3) * 0.5, color, ambient_opacity * pulse, false)
	for i in MOTIFS.SKINS.size(): _draw_motif(i)

func _draw_motif(index: int) -> void:
	var weight := _weights[index]
	weight = weight * weight * (3.0 - 2.0 * weight)
	var center := _center(index)
	var radii: Vector2 = MOTIFS.RADII[index] * _motif_scale(index)
	var color := star_color.lerp(hover_color, weight)
	for path in _paths[index]:
		var points := PackedVector2Array()
		for point in path: points.append(center + point * radii)
		if weight > 0.0:
			draw_polyline(points, Color(hover_color, 0.035 * weight), 9.0, true)
			draw_polyline(points, Color(hover_color, 0.085 * weight), 4.0, true)
		draw_polyline(points, Color(color, lerpf(idle_line_opacity, 0.88, weight)),
			lerpf(1.0, 1.5, weight), true)
		var step := 3 if points.size() > 10 else 2
		for n in range(0, points.size() - 1, step):
			_star(points[n], 1.5 + weight * 0.65, color, 0.54 + weight * 0.42, false)
	# A warm principal star and two short arcs mark the hovered mode even when frozen.
	var principal: Vector2 = center + _paths[index][0][0] * radii
	_star(principal, 3.0 + weight * 1.5, star_color.lerp(accent_color, weight),
		0.75 + weight * 0.25, true)
	if weight > 0.0:
		for start in [-0.4, PI - 0.4]:
			draw_arc(center, maxf(radii.x, radii.y) * 1.26, start, start + 0.23, 10,
				Color(accent_color, 0.6 * weight), 1.0, true)

func _star(point: Vector2, radius: float, color: Color, opacity: float, cross: bool) -> void:
	draw_circle(point, radius * 3.0, Color(color, opacity * 0.055), true, -1.0, true)
	draw_circle(point, radius * 1.7, Color(color, opacity * 0.14), true, -1.0, true)
	draw_circle(point, radius * 0.65, Color(color, opacity), true, -1.0, true)
	if cross:
		draw_line(point - Vector2(radius * 1.5, 0), point + Vector2(radius * 1.5, 0), Color(color, opacity * 0.7), 1.0, true)
		draw_line(point - Vector2(0, radius * 2.0), point + Vector2(0, radius * 2.0), Color(color, opacity * 0.7), 1.0, true)

func _exit_tree() -> void:
	if is_instance_valid(_viewport) and _viewport.mouse_exited.is_connected(_pointer_left):
		_viewport.mouse_exited.disconnect(_pointer_left)
	if is_instance_valid(_window) and _window.focus_exited.is_connected(_pointer_left):
		_window.focus_exited.disconnect(_pointer_left)
	_viewport = null
	_window = null
	_active = false
	_pointer_left()
	_weights.fill(0.0)
	_seconds = 0.0
	set_process(false)
	set_process_input(false)
