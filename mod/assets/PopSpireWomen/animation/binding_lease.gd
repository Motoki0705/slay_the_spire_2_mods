extends RefCounted
## Retarget effect children only. Optional static scale calibration is restored with position.
var _bindings: Array = []
var _active := false

func configure(root: Node, driver: Node, definitions: Array) -> bool:
	restore()
	_bindings.clear()
	for definition: Dictionary in definitions:
		var node := root.get_node_or_null(NodePath(definition.path)) as Node2D
		if node == null or node == driver or node.is_ancestor_of(driver) or node.get_class() in ["SpineSprite", "SpineSlotNode", "SpineBoneNode"]:
			_bindings.clear()
			return false
		var multiplier: Array = definition.get("scale_multiplier", [1.0, 1.0])
		_bindings.append({"node":weakref(node), "anchor":definition.anchor, "position":node.position,
			"scale":node.scale, "multiplier":Vector2(multiplier[0], multiplier[1])})
	return true

func apply(puppet: Node2D) -> bool:
	# Validate the whole set before changing anything this frame.
	for binding: Dictionary in _bindings:
		if not is_instance_valid(binding.node.get_ref()): return false
	for binding: Dictionary in _bindings:
		var node: Node2D = binding.node.get_ref()
		if not _active:
			binding.position = node.position
			binding.scale = node.scale
		node.global_position = puppet.to_global(puppet.anchor_position(binding.anchor))
		if binding.multiplier != Vector2.ONE:
			node.scale = binding.scale * binding.multiplier
	_active = true
	return true

func restore() -> void:
	if _active:
		for binding: Dictionary in _bindings:
			var node: Node2D = binding.node.get_ref()
			if is_instance_valid(node):
				node.position = binding.position
				if binding.multiplier != Vector2.ONE: node.scale = binding.scale
	_active = false
