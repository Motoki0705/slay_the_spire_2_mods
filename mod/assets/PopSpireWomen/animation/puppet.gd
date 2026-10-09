extends Node2D
## CPU skinning keeps JSON authoring and tests independent of native Spine or C# scripts.
## Polygons use fixed source-pixel UVs; each vertex may be weighted to several joints.
const SCHEMA = preload("res://PopSpireWomen/animation/rig_schema.gd")
const MOTION = preload("res://PopSpireWomen/animation/motion_library.gd")

var rig: Dictionary = {}
var character_entry := ""
var last_error := ""
var last_animation := ""
var _bones: Array = []
var _rest: Dictionary = {}
var _skin: Dictionary = {}
var _meshes: Array = []
var _canvas := Vector2.ZERO
var _origin := Vector2.ZERO

func load_rig(path: String, character: String) -> bool:
	if not SCHEMA.owned(path, ".json") or not FileAccess.file_exists(path):
		return _fail("Rig file unavailable")
	var json := JSON.new()
	if json.parse(FileAccess.get_file_as_string(path)) != OK: return _fail("Cannot parse rig JSON")
	return configure(json.data, character)

func configure(data: Variant, character: String) -> bool:
	clear()
	last_error = SCHEMA.validate(data)
	if not last_error.is_empty(): return false
	rig = data.duplicate(true)
	character_entry = character
	_canvas = _v(rig.canvas)
	_origin = _v(rig.origin)
	scale = Vector2.ONE * float(rig.display_height) / _canvas.y
	position = _v(rig.get("offset", [0,0]))
	_bones = rig.get("bones", _default_bones())
	for bone: Dictionary in _bones:
		_rest[bone.name] = _v(bone.position)
		_skin[bone.name] = Transform2D.IDENTITY
	if rig.get("meshes", []).is_empty():
		if not _add_grid("body", rig.body): return _fail("Body texture unavailable or wrong canvas")
	else:
		for mesh: Dictionary in rig.meshes:
			if not _add_mesh(mesh): return _fail("Mesh texture unavailable or wrong canvas")
	for layer: Dictionary in rig.get("layers", []):
		if not _add_grid(layer.id, layer.texture, layer.bone, int(layer.get("z", 0)), layer.get("expression", "")):
			return _fail("Layer texture unavailable or wrong canvas")
	# Sort locally instead of using negative CanvasItem z: negative z would place
	# hair/cloth behind the selection background (and positive z over game UI).
	_meshes.sort_custom(func(a, b): return a.z < b.z)
	for i in _meshes.size(): move_child(_meshes[i].node, i)
	sample_animation("idle_loop", 0.0, true, 0.0)
	return true

func _default_bones() -> Array:
	var out: Array = [{"name":"root", "parent":"", "position":rig.origin}]
	var parents := {"hip":"root", "chest":"hip", "head":"chest", "hand_l":"chest", "hand_r":"chest", "foot_l":"root", "foot_r":"root", "hair":"head", "cloth":"hip"}
	for id in SCHEMA.MARKERS:
		out.append({"name":id, "parent":parents[id], "position":rig.markers[id]})
	return out

func _add_grid(id: String, texture: String, bone := "", z := 0, expression := "") -> bool:
	var mesh := {"id":id, "texture":texture, "z":z, "expression":expression, "vertices":[], "uv":[], "weights":[], "triangles":[]}
	var cols := 12 if bone.is_empty() else 1
	var rows := 18 if bone.is_empty() else 1
	for y in rows + 1:
		for x in cols + 1:
			var point := Vector2(float(x)/cols, float(y)/rows) * _canvas
			mesh.vertices.append([point.x, point.y])
			mesh.uv.append([point.x, point.y])
			mesh.weights.append({bone:1.0} if not bone.is_empty() else _auto_weights(point))
	for y in rows:
		for x in cols:
			var i := y*(cols+1)+x
			mesh.triangles.append([i,i+1,i+cols+1])
			mesh.triangles.append([i+1,i+cols+2,i+cols+1])
	return _add_mesh(mesh)

func _auto_weights(point: Vector2) -> Dictionary:
	var candidates: Array = []
	# Separate hair/cloth layers use their own bones. On a single body, nearby vertices
	# receive smaller secondary weights; explicit meshes can completely replace this starter rig.
	for bone in SCHEMA.MARKERS:
		var distance := point.distance_to(_rest[bone]) / _canvas.y
		var weight := 1.0 / pow(maxf(distance, 0.025), 4)
		if bone in ["hair", "cloth"]: weight *= 0.22
		candidates.append([bone, weight])
	candidates.sort_custom(func(a, b): return a[1] > b[1])
	var weights := {}
	var total := float(candidates[0][1] + candidates[1][1] + candidates[2][1])
	for i in 3: weights[candidates[i][0]] = candidates[i][1]/total
	return weights

func _add_mesh(mesh: Dictionary) -> bool:
	if not ResourceLoader.exists(mesh.texture, "Texture2D"): return false
	var texture := ResourceLoader.load(mesh.texture, "Texture2D") as Texture2D
	if texture == null or texture.get_size() != _canvas: return false
	var polygon := Polygon2D.new()
	polygon.name = mesh.id
	polygon.texture = texture
	polygon.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	polygon.uv = _vectors(mesh.uv)
	var triangles: Array[PackedInt32Array] = []
	for triangle in mesh.triangles: triangles.append(PackedInt32Array(triangle))
	polygon.polygons = triangles
	polygon.polygon = _vectors(mesh.vertices)
	add_child(polygon)
	_meshes.append({"node":polygon, "rest":_vectors(mesh.vertices), "weights":mesh.weights, "expression":mesh.get("expression", ""), "z":int(mesh.get("z",0))})
	return true

func supports(animation: String) -> bool:
	return rig.get("clips", {}).has(animation) or MOTION.ALIASES.has(animation)

func sample_animation(animation: String, phase: float, reduced: bool, seconds: float) -> bool:
	return sample_tracks([{"animation":animation, "phase":phase, "weight":1.0}], reduced, seconds)

func sample_tracks(tracks: Array, reduced: bool, seconds: float) -> bool:
	if rig.is_empty() or tracks.is_empty(): return false
	var pose := {}
	for bone: Dictionary in _bones: pose[bone.name] = Vector3.ZERO
	var dying := false
	for track: Dictionary in tracks:
		if not supports(track.animation): return false
		last_animation = track.animation
		dying = dying or track.animation == "die"
		var channels: Dictionary = rig.get("clips", {}).get(track.animation, MOTION.clip(track.animation, character_entry))
		if not rig.get("clips", {}).has(track.animation) and rig.get("weapon_hand", "hand_r") == "hand_l":
			channels = channels.duplicate(true)
			var left: Variant = channels.get("hand_l")
			var right: Variant = channels.get("hand_r")
			channels.erase("hand_l")
			channels.erase("hand_r")
			if left != null: channels["hand_r"] = left
			if right != null: channels["hand_l"] = right
		for bone in channels:
			# Reduced motion freezes ambient loops but still represents hit/death/attack poses.
			var phase: float = track.phase
			if reduced and track.animation in ["idle_loop", "relaxed_loop", "select", "overgrowth_loop", "hive_loop", "glory_loop"]: phase = 0.0
			pose[bone] += MOTION.sample(channels[bone], phase) * float(track.weight)
	if not reduced and not dying:
		var secondary: Dictionary = rig.get("secondary", {
			"hair":{"degrees":1.8,"period":2.7,"phase":0.6},
			"cloth":{"degrees":1.2,"period":3.4,"phase":1.4}})
		for bone in secondary:
			var channel: Dictionary = secondary[bone]
			pose[bone].z += sin(seconds * TAU / float(channel.period) + float(channel.get("phase",0))) * float(channel.degrees)
	var world := {}
	for bone: Dictionary in _bones:
		var parent: String = bone.get("parent", "")
		var delta: Vector3 = pose[bone.name]
		var origin: Vector2 = _rest[bone.name] - _rest.get(parent, Vector2.ZERO) + Vector2(delta.x, delta.y)
		world[bone.name] = world.get(parent, Transform2D.IDENTITY) * Transform2D(deg_to_rad(delta.z), origin)
		_skin[bone.name] = world[bone.name] * Transform2D(0, -_rest[bone.name])
	for mesh: Dictionary in _meshes:
		var points := PackedVector2Array()
		for i in mesh.rest.size():
			points.append(deform_point(mesh.rest[i], mesh.weights[i]) - _origin)
		mesh.node.polygon = points
		var expression: String = mesh.expression
		mesh.node.visible = expression.is_empty() or (not reduced and not dying and (
			(expression == "blink" and fposmod(seconds, 4.7) > 4.54) or
			(expression == "look" and fposmod(seconds, 7.8) > 5.8)))
	return true

func deform_point(point: Vector2, weights: Dictionary) -> Vector2:
	var result := Vector2.ZERO
	for bone in weights: result += (_skin[bone] * point) * float(weights[bone])
	return result

func anchor_position(id: String) -> Vector2:
	var anchor: Dictionary = rig.anchors[id]
	return (_skin[anchor.bone] * _v(anchor.position)) - _origin

func clear() -> void:
	for mesh: Dictionary in _meshes:
		if is_instance_valid(mesh.node): mesh.node.free()
	_meshes.clear()
	_bones.clear()
	_rest.clear()
	_skin.clear()
	rig = {}

func _fail(message: String) -> bool:
	clear()
	last_error = message
	return false

static func _v(array: Array) -> Vector2:
	return Vector2(float(array[0]), float(array[1]))

static func _vectors(array: Array) -> PackedVector2Array:
	var result := PackedVector2Array()
	for point: Array in array: result.append(_v(point))
	return result
