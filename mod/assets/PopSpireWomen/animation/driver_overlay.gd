extends Node2D
## Attached to the original typed scene; the original driver and callbacks remain untouched.
const PUPPET = preload("res://PopSpireWomen/animation/puppet.gd")
const READER = preload("res://PopSpireWomen/animation/driver_reader.gd")
const BINDING_LEASE = preload("res://PopSpireWomen/animation/binding_lease.gd")
const DRAW_LEASE = preload("res://PopSpireWomen/animation/draw_lease.gd")
const SETTINGS = preload("res://PopSpireWomen/config/settings.gd")

@export var character_entry := ""
@export_file("*.json") var rig_path := ""
@export var driver_path: NodePath
@export_enum("combat", "merchant", "rest") var surface := "combat"

var state := "inactive"
var _driver: Node2D
var _puppet: Node2D
var _lease = DRAW_LEASE.new()
var _bindings = BINDING_LEASE.new()
var _ready_once := false
var _warning := false
var _reduced := false

func _enter_tree() -> void:
	if _ready_once: _start.call_deferred()

func _ready() -> void:
	_ready_once = true
	process_priority = 100
	_start.call_deferred()

func _start() -> void:
	if not is_inside_tree() or is_queued_for_deletion(): return
	var preferences := SETTINGS.read()
	if not SETTINGS.enabled(preferences, character_entry):
		_restore()
		state = "disabled"
		return
	_reduced = bool(ProjectSettings.get_setting("PopSpireWomen/select/reduced_motion", preferences.ReducedMotion))
	_driver = get_node_or_null(driver_path) as Node2D
	if _driver == null or _driver.get_class() != "SpineSprite":
		_fallback("Original Spine driver unavailable")
		return
	_puppet = PUPPET.new()
	add_child(_puppet)
	_puppet.hide()
	if not _puppet.load_rig(rig_path, character_entry):
		_fallback(_puppet.last_error)
		return
	if not _bindings.configure(get_parent(), _driver, _puppet.rig.get("bindings", [])):
		_fallback("Invalid VFX binding")
		return
	state = "waiting"
	if _driver.has_signal("world_transforms_changed"):
		_driver.connect("world_transforms_changed", _driver_updated)
	_sync()

func _driver_updated(_sprite: Object) -> void:
	if state in ["waiting", "active", "original"]: _sync()

func _process(_delta: float) -> void:
	if state in ["waiting", "active", "original"]: _sync()

func _sync() -> void:
	if not is_instance_valid(_driver) or not is_instance_valid(_puppet) or _puppet.rig.is_empty():
		_fallback("Driver or custom drawing was removed")
		return
	var snapshot := READER.snapshot(_driver)
	if snapshot.is_empty():
		_restore()
		state = "waiting"
		return
	if not _puppet.sample_tracks(snapshot.tracks, _reduced, snapshot.seconds):
		_restore()
		state = "original"
		return
	var meshes: Array = []
	for child in _driver.get_children():
		if child is CanvasItem and child.get_class() == "SpineMesh2D": meshes.append(child)
	meshes = DRAW_LEASE.runtime_meshes(meshes, snapshot.slots.size())
	var defaults := ["shadow", "slash_mesh"]
	if character_entry == "REGENT": defaults.append_array(["throne*", "*guy*"])
	if not _lease.suppress(meshes, snapshot.slots, _puppet.rig.get("preserve_slots", defaults)):
		_restore()
		state = "original"
		return
	# Parent NCreatureVisuals already owns revive fades, hit shakes and removal.
	# Mirror driver-only tint/flip/visibility without changing its scale, skeleton or process mode.
	modulate = _driver.modulate * _driver.self_modulate
	scale = Vector2(signf(_driver.scale.x), signf(_driver.scale.y))
	visible = _driver.visible
	_puppet.show()
	if not _bindings.apply(_puppet):
		_fallback("VFX binding was removed")
		return
	state = "active"

func _restore() -> void:
	_lease.restore()
	if is_instance_valid(_puppet): _puppet.hide()
	_bindings.restore()

func _fallback(message: String) -> void:
	_restore()
	state = "failed"
	if not _warning:
		_warning = true
		push_warning("[PopSpireWomen] " + character_entry + "/" + surface + ": " + message + "; original retained")

func _exit_tree() -> void:
	_restore()
	if is_instance_valid(_driver) and _driver.is_connected("world_transforms_changed", _driver_updated):
		_driver.disconnect("world_transforms_changed", _driver_updated)
	if is_instance_valid(_puppet): _puppet.queue_free()
	_puppet = null
	_driver = null
	_bindings = BINDING_LEASE.new()
	state = "inactive"
