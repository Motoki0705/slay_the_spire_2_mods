extends RefCounted
## Own only drawing visibility, never parent visibility/processing/materials/animation state.
var _saved: Dictionary = {}

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
