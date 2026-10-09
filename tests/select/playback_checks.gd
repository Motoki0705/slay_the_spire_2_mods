extends SceneTree
## Current selection suite uses Godot meshes, never a video decoder.
const BASE = "res://PopSpireWomen/select/select_background.tscn"
const FIXTURE = "res://PopSpireWomen/test-fixtures/"
var failures := 0
var checks := 0
var pressed := 0
var host: Control

func _initialize() -> void: _run.call_deferred()
func check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures += 1
		printerr("FAIL ",label)
	else: print("PASS ",label)
func frames(count := 2) -> void:
	for i in count: await process_frame
func background() -> Control:
	var result: Control = load(BASE).instantiate()
	result.poster_path = FIXTURE+"poster.svg"
	result.background_path = FIXTURE+"poster.svg"
	result.rig_path = FIXTURE+"rig.json"
	result.overlay_scene_path = FIXTURE+"overlay.tscn"
	host.add_child(result)
	return result
func remove_background(node: Control) -> void:
	host.remove_child(node)
	check(node.state == "inactive" and node._puppet == null and node.get_node("Poster").texture == null, "exit releases custom mesh and textures immediately")
	node.queue_free()

func _run() -> void:
	root.size = Vector2i(800,600)
	host = Control.new()
	host.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(host)
	host.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var button := Button.new()
	button.position = Vector2(620,535)
	button.size = Vector2(160,50)
	button.text = "Embark fixture"
	button.pressed.connect(func(): pressed += 1)
	root.add_child(button)
	for id in ["ironclad","silent","regent","necrobinder","defect"]:
		var descriptor: Control = load("res://PopSpireWomen/select/%s.tscn" % id).instantiate()
		host.add_child(descriptor)
		check(descriptor.character_entry == id.to_upper() and descriptor.state == "original", "disabled descriptor uses original stub: "+id)
		remove_background(descriptor)
	await frames()
	ProjectSettings.set_setting("PopSpireWomen/select/enabled",true)
	ProjectSettings.set_setting("PopSpireWomen/select/reduced_motion",true)
	var reduced := background()
	check(reduced.state == "rig" and reduced._reduced and not reduced.has_node("Video"), "reduced startup displays frozen custom rig without video node")
	remove_background(reduced)
	await frames()
	ProjectSettings.set_setting("PopSpireWomen/select/reduced_motion",false)
	var a := background()
	check(a.state == "rig" and not a.get_node("Poster").visible, "valid rig is displayed over background")
	check(a.mouse_filter == Control.MOUSE_FILTER_IGNORE and a.get_node("Background").mouse_filter == Control.MOUSE_FILTER_IGNORE and a.get_node("Overlay").mouse_filter == Control.MOUSE_FILTER_IGNORE, "background controls pass input through")
	await frames(8)
	var before: PackedVector2Array = a._puppet.get_node("body").polygon.duplicate()
	await frames(8)
	check(before != a._puppet.get_node("body").polygon, "selection mesh moves while processing")
	paused = true
	before = a._puppet.get_node("body").polygon.duplicate()
	await frames(8)
	check(before == a._puppet.get_node("body").polygon, "scene pause freezes selection mesh")
	paused = false
	await frames(8)
	check(before != a._puppet.get_node("body").polygon, "scene unpause resumes selection mesh")
	var motion := InputEventMouseMotion.new()
	motion.position = Vector2(32,32)
	Input.parse_input_event(motion)
	await frames()
	check(a.get_node("Overlay").get_child(0).hovers > 0, "independent overlay receives hover (#21 integration surface)")
	for down in [true,false]:
		var click := InputEventMouseButton.new()
		click.button_index = MOUSE_BUTTON_LEFT
		click.position = Vector2(700,560)
		click.pressed = down
		Input.parse_input_event(click)
		await frames()
	check(pressed == 1, "embark UI remains clickable during animation")
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(OS.get_environment("PSW_ANIMATION_OUTPUT").path_join("selection.png"))
	a.set_preferences(true,true)
	await frames()
	before = a._puppet.get_node("body").polygon.duplicate()
	await frames(10)
	check(before == a._puppet.get_node("body").polygon and a.get_node("Overlay").get_child(0).reduced, "reduced preference freezes rig and reaches overlay")
	a.set_preferences(true,false)
	host.hide()
	check(a.state == "hidden" and a._puppet == null, "ancestor hiding releases mesh")
	host.show()
	check(a.state == "rig", "ancestor showing reconstructs rig")
	a.set_preferences(false,false)
	check(a.state == "original" and a._puppet == null, "live disable restores original stub")
	a.set_preferences(true,false)
	check(a.state == "rig", "live enable rebuilds mesh")
	a.configure(FIXTURE+"poster.svg",FIXTURE+"missing.json")
	check(a.state == "poster" and a._puppet == null, "missing rig falls back to poster")
	a.configure("",FIXTURE+"missing.json")
	check(a.state == "original", "missing rig and poster restore original")
	a.configure(FIXTURE+"poster.svg",FIXTURE+"rig.json")
	check(a.state == "rig", "valid configuration recovers from missing asset")
	host.remove_child(a)
	await frames()
	host.add_child(a)
	await frames()
	check(a.state == "rig" and a.get_node("Layers").get_child_count() == 1, "re-entry creates exactly one rig")
	remove_background(a)
	for i in 12:
		var quick := background()
		remove_background(quick)
	await frames(4)
	check(host.get_child_count() == 0, "rapid switching leaves no active scene/mesh")
	host.queue_free()
	button.queue_free()
	await frames()
	print("CHECKS=",checks," FAILURES=",failures," (Godot selection; Regent seven hover behaviors remain #21)")
	quit(1 if failures else 0)
