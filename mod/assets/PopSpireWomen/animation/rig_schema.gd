extends RefCounted
## Validate before allocating or suppressing any original drawing.
const MARKERS = ["hip", "chest", "head", "hand_l", "hand_r", "foot_l", "foot_r", "hair", "cloth"]

static func owned(path: Variant, suffix: String = "") -> bool:
	if not path is String or not path.begins_with("res://PopSpireWomen/"): return false
	if not suffix.is_empty() and not path.ends_with(suffix): return false
	for part in path.trim_prefix("res://").split("/"):
		if part.is_empty() or part in [".", ".."] or "\\" in part: return false
	return true

static func number(v: Variant) -> bool:
	return (v is float or v is int) and is_finite(float(v))

static func vector(v: Variant, count := 2) -> bool:
	if not v is Array or v.size() != count: return false
	for n in v:
		if not number(n): return false
	return true

static func validate(data: Variant) -> String:
	if not data is Dictionary or data.get("schema") != 1: return "Expected rig schema 1"
	if data.get("surface", "") not in ["", "combat", "merchant", "rest", "select"]: return "Invalid surface"
	if data.get("motion_profile", "legacy_v01") not in ["legacy_v01", "contextual_v02"]: return "Invalid motion_profile"
	if not vector(data.get("canvas")) or data.canvas[0] <= 0 or data.canvas[1] <= 0 or data.canvas[0] > 8192 or data.canvas[1] > 8192: return "Invalid canvas"
	if not vector(data.get("origin")): return "Invalid origin"
	if not number(data.get("display_height")) or data.display_height <= 0 or data.display_height > 4096: return "Invalid display_height"
	if not owned(data.get("body")): return "Invalid body texture path"
	if data.get("weapon_hand", "hand_r") not in ["hand_l", "hand_r"]: return "Invalid weapon_hand"
	if not data.get("markers") is Dictionary: return "Missing character markers"
	for id in MARKERS:
		if not vector(data.markers.get(id)): return "Missing or invalid marker: " + id
	var names := ["root"] + MARKERS
	if data.has("bones"):
		if not data.bones is Array or data.bones.size() > 64: return "Invalid bones"
		names = []
		for bone in data.bones:
			if not bone is Dictionary or not bone.get("name") is String or bone.name in names or not vector(bone.get("position")): return "Invalid bone"
			if bone.get("parent", "") != "" and bone.get("parent") not in names: return "Bones must follow parent order"
			names.append(bone.name)
		for id in ["root"] + MARKERS:
			if id not in names: return "Custom bones must include " + id
	for optional in ["layers", "meshes", "bindings"]:
		if not data.get(optional, []) is Array or data.get(optional, []).size() > 64: return "Invalid " + optional
	for layer in data.get("layers", []):
		if not layer is Dictionary or not layer.get("id") is String or not owned(layer.get("texture")) or layer.get("bone") not in names: return "Invalid layer"
		if not number(layer.get("z", 0)) or absf(layer.get("z", 0)) > 100: return "Invalid layer z"
		if layer.get("expression", "") not in ["", "blink", "look"]: return "Invalid expression"
	for mesh in data.get("meshes", []):
		if not mesh is Dictionary or not mesh.get("id") is String or not owned(mesh.get("texture")): return "Invalid mesh"
		if not number(mesh.get("z", 0)) or absf(mesh.get("z", 0)) > 100: return "Invalid mesh z"
		var vertices: Variant = mesh.get("vertices")
		if not vertices is Array or vertices.size() < 3 or vertices.size() > 4096: return "Invalid vertices"
		if not mesh.get("uv") is Array or mesh.uv.size() != vertices.size() or not mesh.get("weights") is Array or mesh.weights.size() != vertices.size(): return "Vertex/UV/weight count mismatch"
		for i in vertices.size():
			if not vector(vertices[i]) or not vector(mesh.uv[i]) or not mesh.weights[i] is Dictionary: return "Invalid mesh vertex"
			var total := 0.0
			for bone in mesh.weights[i]:
				if bone not in names or not number(mesh.weights[i][bone]) or mesh.weights[i][bone] < 0: return "Invalid weight"
				total += float(mesh.weights[i][bone])
			if not is_equal_approx(total, 1.0): return "Weights must sum to 1"
		if not mesh.get("triangles") is Array or mesh.triangles.is_empty() or mesh.triangles.size() > 8192: return "Missing triangles"
		for triangle in mesh.triangles:
			if not vector(triangle, 3): return "Invalid triangle"
			for i in triangle:
				if i != int(i) or i < 0 or i >= vertices.size(): return "Invalid triangle index"
	if not data.get("clips", {}) is Dictionary: return "Invalid clips"
	for clip in data.get("clips", {}).values():
		if not clip is Dictionary: return "Invalid clip"
		for bone in clip:
			if bone not in names or not clip[bone] is Array or clip[bone].is_empty(): return "Invalid channel"
			var last := -1.0
			for key in clip[bone]:
				if not vector(key, 4) or key[0] < 0 or key[0] > 1 or key[0] <= last: return "Invalid key phase"
				last = key[0]
	if not data.get("anchors", {}) is Dictionary: return "Invalid anchors"
	for anchor in data.get("anchors", {}).values():
		if not anchor is Dictionary or anchor.get("bone") not in names or not vector(anchor.get("position")): return "Invalid anchor"
	for binding in data.get("bindings", []):
		if not binding is Dictionary or not binding.get("path") is String or binding.get("anchor") not in data.get("anchors", {}): return "Invalid binding"
		if binding.path.is_empty() or binding.path.begins_with("/") or ".." in binding.path or "%" in binding.path: return "Binding must stay inside original visual"
		if binding.has("scale_multiplier"):
			if not vector(binding.scale_multiplier): return "Invalid effect scale multiplier"
			for component in binding.scale_multiplier:
				if component <= 0 or component > 4: return "Effect scale multiplier outside supported range"
	if not vector(data.get("offset", [0,0])): return "Invalid offset"
	if not data.get("preserve_slots", []) is Array: return "Invalid preserve_slots"
	for slot in data.get("preserve_slots", []):
		if not slot is String: return "Invalid preserved slot"
	if not data.get("secondary", {}) is Dictionary: return "Invalid secondary motion"
	for bone in data.get("secondary", {}):
		var channel: Variant = data.secondary[bone]
		if bone not in names or not channel is Dictionary or not number(channel.get("degrees")) or not number(channel.get("period")) or channel.period <= 0 or not number(channel.get("phase",0)): return "Invalid secondary channel"
	return ""
