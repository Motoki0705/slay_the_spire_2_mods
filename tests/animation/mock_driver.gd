extends Node2D
## A deterministic behavioral fixture for the read adapter, not a Spine implementation.
class AnimationData extends RefCounted:
	var id := "idle_loop"
	var duration := 2.0
	func get_name() -> String: return id
	func get_duration() -> float: return duration

class Track extends RefCounted:
	var animation := AnimationData.new()
	var time := 0.0
	var loop := false
	var mix_time := 0.0
	var mix_duration := 0.0
	var previous: Track
	func get_animation() -> Object: return animation
	func get_animation_time() -> float: return fposmod(time,animation.duration) if loop else minf(time,animation.duration)
	func get_mixing_from() -> Object: return previous
	func get_mix_time() -> float: return mix_time
	func get_mix_duration() -> float: return mix_duration

class AnimationState extends RefCounted:
	var track := Track.new()
	func get_current(_index: int) -> Object: return track

class SlotData extends RefCounted:
	var id := "body"
	func get_name() -> String: return id

class Slot extends RefCounted:
	var data := SlotData.new()
	func get_data() -> Object: return data

class Skeleton extends RefCounted:
	var time := 0.0
	var slots: Array = []
	func get_draw_order() -> Array: return slots
	func get_time() -> float: return time

var animation_state := AnimationState.new()
var skeleton := Skeleton.new()
var events := 0

func _init() -> void:
	for id in ["shadow", "body", "slash_mesh"]:
		var slot := Slot.new()
		slot.data.id = id
		skeleton.slots.append(slot)

func get_animation_state() -> Object: return animation_state
func get_skeleton() -> Object: return skeleton

func play(id: String, duration := 2.0, loop := false) -> void:
	var track := Track.new()
	track.animation.id = id
	track.animation.duration = duration
	track.loop = loop
	animation_state.track = track

func advance(delta: float) -> void:
	animation_state.track.time += delta
	skeleton.time += delta
	events += 1
