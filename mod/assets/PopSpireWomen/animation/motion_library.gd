extends RefCounted
## Original names, presentation-only channels [phase, dx_px, dy_px, degrees].
## No gameplay signals, event forwarding, delays or random-number calls.

const ALIASES = {
	"idle_loop": "idle", "relaxed_loop": "relax", "attack": "attack",
	"attack_heavy": "heavy", "shiv": "shiv", "attack_sovereign": "sovereign",
	"cast": "cast", "cast_mighty": "summon", "process": "process",
	"hurt": "hit", "die": "die", "overgrowth_loop": "rest",
	"hive_loop": "rest", "glory_loop": "rest", "select": "select"
}

static func clip(animation: String, character: String) -> Dictionary:
	var name: String = ALIASES.get(animation, "")
	match name:
		"idle", "relax", "rest":
			return {"chest": [[0,0,0,0],[0.5,0,-6,0.5],[1,0,0,0]],
				"head": [[0,0,0,0],[0.5,0,-2,-0.6],[1,0,0,0]]}
		"attack", "heavy", "shiv", "sovereign":
			var power := 1.0
			if name == "heavy": power = 1.5
			if name == "shiv": power = 0.65
			return {"chest": [[0,0,0,0],[0.16,-12,3,-3],[0.34,28*power,-3,4*power],[1,0,0,0]],
				"hand_r": [[0,0,0,0],[0.16,-24,-28,-9],[0.34,82*power,-38,14*power],[0.72,18,0,4],[1,0,0,0]],
				"head": [[0,0,0,0],[0.34,3,0,-3],[1,0,0,0]]}
		"cast", "summon", "process":
			return {"chest": [[0,0,0,0],[0.36,0,-12,-2],[1,0,0,0]],
				"hand_l": [[0,0,0,0],[0.3,-26,-56,-12],[0.65,-16,-40,-7],[1,0,0,0]],
				"hand_r": [[0,0,0,0],[0.4,24,-66,12],[0.7,18,-44,6],[1,0,0,0]],
				"head": [[0,0,0,0],[0.4,0,-5,-4],[1,0,0,0]]}
		"hit":
			return {"chest": [[0,0,0,0],[0.18,-35,8,-6],[0.58,-12,2,-2],[1,0,0,0]],
				"head": [[0,0,0,0],[0.18,-12,2,-4],[1,0,0,0]]}
		"die":
			return {"hip": [[0,0,0,0],[0.45,-12,48,-5],[1,-25,125,-12]],
				"chest": [[0,0,0,0],[0.5,12,16,10],[1,48,40,22]],
				"head": [[0,0,0,0],[0.65,0,14,9],[1,8,26,17]],
				"hand_r": [[0,0,0,0],[1,0,70,14]], "hand_l": [[0,0,0,0],[1,0,55,-12]]}
		"select":
			var gesture: Dictionary = {
				"IRONCLAD": {"hand_r": [[0,0,0,0],[0.3,-8,-16,-3],[0.6,0,0,0],[1,0,0,0]]},
				"SILENT": {"head": [[0,0,0,0],[0.22,3,0,-2],[0.4,3,0,-2],[0.7,0,0,0],[1,0,0,0]]},
				"REGENT": {"hand_l": [[0,0,0,0],[0.3,-18,-22,-7],[0.5,-18,-22,-7],[0.7,0,0,0],[1,0,0,0]]},
				"NECROBINDER": {"head": [[0,0,0,0],[0.3,-3,-2,3],[0.6,0,0,0],[1,0,0,0]]},
				"DEFECT": {"hand_r": [[0,0,0,0],[0.3,-14,-20,-4],[0.65,-14,-20,-4],[1,0,0,0]]}
			}.get(character, {})
			gesture["chest"] = [[0,0,0,0],[0.5,0,-6,0.4],[1,0,0,0]]
			return gesture
	return {}

static func sample(keys: Array, phase: float) -> Vector3:
	if keys.is_empty(): return Vector3.ZERO
	var previous: Array = keys[0]
	for key: Array in keys:
		if phase <= float(key[0]):
			var weight := 0.0 if float(key[0]) == float(previous[0]) else clampf((phase-float(previous[0]))/(float(key[0])-float(previous[0])), 0, 1)
			return Vector3(previous[1], previous[2], previous[3]).lerp(Vector3(key[1],key[2],key[3]), weight)
		previous = key
	return Vector3(previous[1],previous[2],previous[3])
