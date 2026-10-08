extends Control
var active := false
var reduced := false
var hovers := 0

func _ready() -> void:
	$Hover.mouse_entered.connect(func():
		hovers += 1
		$Hover.color = Color.YELLOW)

func set_presentation_state(is_active: bool, reduced_motion: bool) -> void:
	active = is_active
	reduced = reduced_motion
