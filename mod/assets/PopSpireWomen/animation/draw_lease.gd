extends RefCounted
## Own only drawing visibility, never parent visibility/processing/materials/animation state.
var _saved: Dictionary = {}

static func runtime_meshes(meshes: Array, slot_count: int) -> Array:
	if meshes.size() == slot_count: return meshes
	# Some pinned scenes contain editor-saved empty SpineMesh2D placeholders.
	# Native generate_meshes_for_slots creates unowned children; serialized scene
	# children have an owner. Do not delete them or guess by generated node names.
	var runtime: Array = []
	for mesh: Node in meshes:
		if mesh.owner == null: runtime.append(mesh)
	return runtime if runtime.size() == slot_count else []

func suppress(meshes: Array, slots: Array, keep: Array) -> bool:
	if meshes.is_empty() or meshes.size() != slots.size(): return false
	for i in meshes.size():
		var mesh: CanvasItem = meshes[i]
		if not _saved.has(mesh.get_instance_id()):
			_saved[mesh.get_instance_id()] = {"node":weakref(mesh), "visible":mesh.visible}
		var preserve := false
		for pattern: String in keep:
			if String(slots[i]).match(pattern): preserve = true
		mesh.visible = _saved[mesh.get_instance_id()].visible if preserve else false
	return true

func restore() -> void:
	for saved: Dictionary in _saved.values():
		var node: CanvasItem = saved.node.get_ref()
		if is_instance_valid(node): node.visible = saved.visible
	_saved.clear()
