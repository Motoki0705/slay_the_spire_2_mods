extends RefCounted
## Read native Godot methods already used by the game. No native source or data is shipped.

static func methods(object: Object, names: Array) -> bool:
	if not is_instance_valid(object): return false
	for method: String in names:
		if not object.has_method(method): return false
	return true

static func snapshot(driver: Node) -> Dictionary:
	if not methods(driver, ["get_animation_state", "get_skeleton"]): return {}
	var state: Object = driver.call("get_animation_state")
	var skeleton: Object = driver.call("get_skeleton")
	if not methods(state, ["get_current"]) or not methods(skeleton, ["get_draw_order", "get_time"]): return {}
	# Holding these References only for this sample avoids keeping disposed track handles.
	var current: Object = state.call("get_current", 0)
	var tracks := _tracks(current, 1.0, 0)
	if tracks.is_empty(): return {}
	var slots: Array = []
	for slot: Object in skeleton.call("get_draw_order"):
		if not methods(slot, ["get_data"]): return {}
		var data: Object = slot.call("get_data")
		if not methods(data, ["get_name"]): return {}
		slots.append(String(data.call("get_name")))
	var time := float(skeleton.call("get_time"))
	if not is_finite(time): return {}
	return {"tracks":tracks, "slots":slots, "seconds":time}

static func _tracks(entry: Object, weight: float, depth: int) -> Array:
	if depth > 8 or not methods(entry, ["get_animation", "get_animation_time", "get_mixing_from", "get_mix_duration", "get_mix_time"]): return []
	var animation: Object = entry.call("get_animation")
	if not methods(animation, ["get_name", "get_duration"]): return []
	var duration := float(animation.call("get_duration"))
	var time := float(entry.call("get_animation_time"))
	if not is_finite(duration) or duration <= 0 or not is_finite(time): return []
	var result: Array = []
	var previous: Object = entry.call("get_mixing_from")
	var mix_duration := float(entry.call("get_mix_duration"))
	var mix_time := float(entry.call("get_mix_time"))
	if not is_finite(mix_duration) or not is_finite(mix_time): return []
	if is_instance_valid(previous) and mix_duration > 0 and mix_time < mix_duration:
		var mix := clampf(mix_time / mix_duration, 0, 1)
		result = _tracks(previous, weight * (1-mix), depth+1)
		if result.is_empty(): return []
		weight *= mix
	result.append({"animation":String(animation.call("get_name")), "phase":clampf(time/duration,0,1), "weight":weight})
	return result
