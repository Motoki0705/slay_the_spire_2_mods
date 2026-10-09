extends SceneTree
## Real Godot rendering/input; sky/UI fixtures are not release artwork or native game QA.
const SELECT = preload("res://PopSpireWomen/select/regent.tscn")
const OVERLAY = preload("res://PopSpireWomen/select/overlays/regent/constellations.tscn")
const NAMES = ["Spheric Guardian", "Deca", "Sentry", "Snecko", "Cultist", "Shapes", "Amogus"]
const SKINS = ["spheric guardian constellation", "deca outline", "sentry constellation",
	"snecko constellation", "cultist constellation", "shapes constellation", "amogus constellation"]
var checks := 0
var failures := 0
var pressed := 0
var stage: Control
var canvas: Control
var behind: Button
var selection: Control
var idle_crops: Array[Image] = []
var hover_crops: Array[Image] = []

func _initialize() -> void: _run.call_deferred()

func check(condition: bool, label: String) -> void:
	checks += 1
	if not condition:
		failures += 1
		printerr("FAIL ", label)
	else: print("PASS ", label)

func frames(count := 2) -> void:
	for i in count: await process_frame

func move_mouse(point: Vector2) -> void:
	var event := InputEventMouseMotion.new()
	event.position = point
	Input.parse_input_event(event)

func physical_pointer_at(point: Vector2) -> void:
	# Activation/unpause sample the OS cursor. Let X11's warp-generated events settle
	# before injecting a deterministic final event; never mix two asynchronous streams.
	root.warp_mouse(point)
	await frames(5)
	move_mouse(point)
	await frames(2)

func point_for(overlay: Control, index: int) -> Vector2:
	return overlay.get_global_transform_with_canvas() * overlay.constellation_position(index)

func click_at(point: Vector2) -> void:
	for down in [true, false]:
		var event := InputEventMouseButton.new()
		event.position = point
		event.button_index = MOUSE_BUTTON_LEFT
		event.pressed = down
		Input.parse_input_event(event)
		await frames(1)

func label_at(parent: Node, text: String, position: Vector2, font_size := 22) -> Label:
	var label := Label.new()
	label.text = text
	label.position = position
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", Color("bdcbdc"))
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(label)
	return label

func new_selection() -> Control:
	var result: Control = SELECT.instantiate()
	# Harness-only input wiring. Production catalog/descriptor rig choices belong to parent.
	result.rig_path = "res://PopSpireWomen/art/regent/rig.json"
	result.background_path = "res://PopSpireWomen/test-fixtures/sky.svg"
	canvas.add_child(result)
	return result

func current_overlay() -> Control:
	return selection.get_node("Overlay").get_child(0)

func screenshot(name: String) -> Image:
	await RenderingServer.frame_post_draw
	var result := root.get_texture().get_image()
	if not name.is_empty():
		check(result.save_png(OS.get_environment("PSW_REGENT_OUTPUT").path_join(name)) == OK, "render saved: " + name)
	return result

func crop(image: Image, point: Vector2) -> Image:
	# Only the motif area is used for the proof sheet; captures remain actual Godot pixels.
	var region := Rect2i(Vector2i(point) - Vector2i(158, 158), Vector2i(316, 316))
	region.position = region.position.clamp(Vector2i.ZERO, image.get_size() - region.size)
	return image.get_region(region)

func connection_count(overlay: Control) -> int:
	var count := 0
	for connection in root.mouse_exited.get_connections():
		if connection.callable.get_object() == overlay: count += 1
	return count

func _run() -> void:
	root.size = Vector2i(1920, 1080)
	root.position = Vector2i.ZERO
	stage = Control.new()
	stage.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(stage)
	stage.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	behind = Button.new()
	behind.text = "Underlying UI fixture"
	behind.pressed.connect(func(): pressed += 1)
	stage.add_child(behind) # Earlier sibling: truly behind the entire background/overlay.
	behind.hide()
	canvas = Control.new()
	canvas.mouse_filter = Control.MOUSE_FILTER_IGNORE
	stage.add_child(canvas)
	canvas.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	# Exact AnimatedBg layout from v0.107.1 character_select_screen.tscn:81-93.
	canvas.offset_left = -388
	canvas.offset_top = -80
	canvas.offset_right = 252
	canvas.offset_bottom = 40
	canvas.pivot_offset = Vector2(1280, 600)
	canvas.scale = Vector2(1.1, 1.1)
	label_at(stage, "REGENT", Vector2(296, 355), 48)
	label_at(stage, "UI PLACEMENT FIXTURE\nName / description / relic region\n\nProduction star overlay\nDelegated Regent body + rig\nTemporary sky; final art is separate", Vector2(296, 430), 24)
	label_at(stage, "CHARACTER BUTTONS  /  UI FIXTURE", Vector2(745, 942), 21)
	label_at(stage, "STANDALONE GODOT 4.5.1   /   NO NATIVE GAME SESSION", Vector2(32, 1034), 20)
	ProjectSettings.set_setting("PopSpireWomen/select/enabled", true)
	ProjectSettings.set_setting("PopSpireWomen/select/reduced_motion", false)
	selection = new_selection()
	await frames(4)
	var overlay := current_overlay()
	check(selection.state == "rig", "descriptor attaches production overlay to actual Regent rig in harness")
	check(canvas.size == Vector2(2560, 1200) and overlay.size == canvas.size, "overlay fills original 2560 x 1200 extended canvas")
	check(overlay.get_active_skin() == "normal", "startup is normal, not an eighth invented hover")
	check(overlay.mouse_filter == Control.MOUSE_FILTER_IGNORE and overlay.focus_mode == Control.FOCUS_NONE
		and overlay.get_child_count() == 0, "pure drawing control: no mouse/focus stealing child widgets")
	check(connection_count(overlay) == 1, "one viewport-exit connection")
	move_mouse(Vector2(400, 500))
	await frames(16)
	var idle := await screenshot("standalone-normal.png")
	for i in 7: idle_crops.append(crop(idle, point_for(overlay, i)))
	for i in 7:
		move_mouse(point_for(overlay, i))
		await frames(2)
		check(overlay.get_active_skin() == SKINS[i] and overlay.hovered_index == i, "hover callback order " + str(i + 1) + ": " + SKINS[i])
		await frames(14)
		check(overlay._weights[i] == 1.0, "hover transition settles: " + NAMES[i])
		if i == 0: await screenshot("standalone-spheric-guardian.png")
		if i == 3: await screenshot("standalone-snecko.png")
	move_mouse(Vector2(400, 500))
	await frames(16)
	check(overlay.get_active_skin() == "normal" and overlay._weights.count(0.0) == 7, "leaving every hit region restores normal and removes highlight")
	for repetition in 8:
		for i in [6, 0, 5, 1, 4, 2, 3]: move_mouse(point_for(overlay, i))
	await frames(16)
	check(overlay.hovered_index == 3 and overlay._weights.count(1.0) == 1 and overlay._weights[3] == 1.0,
		"56 rapid pointer switches leave exactly the last hover, no queued animation")
	root.mouse_exited.emit()
	await frames(16)
	check(overlay.get_active_skin() == "normal", "viewport exit resets hover without a final mouse motion")
	move_mouse(point_for(overlay, 4))
	await frames(2)
	root.focus_exited.emit()
	await frames(16)
	check(overlay.get_active_skin() == "normal", "window focus loss resets hover")
	var target := point_for(overlay, 0)
	behind.position = target - Vector2(100, 40)
	behind.size = Vector2(200, 80)
	behind.show()
	move_mouse(target)
	await frames(1)
	await click_at(target)
	check(pressed == 1, "underlying UI receives click inside a live constellation hit region")
	check(overlay.get_active_skin() == SKINS[0], "click does not latch or change cosmetic hover")
	behind.hide()
	var before: float = overlay._seconds
	await frames(8)
	check(overlay._seconds > before, "local decorative clock advances when active")
	paused = true
	before = overlay._seconds
	var weights: PackedFloat32Array = overlay._weights.duplicate()
	await physical_pointer_at(point_for(overlay, 5))
	await frames(8)
	check(overlay._seconds == before and overlay._weights == weights and overlay.hovered_index == 0,
		"SceneTree pause freezes motion and ignores hover input")
	paused = false
	await frames(16)
	check(overlay._seconds > before and overlay.hovered_index == 5, "unpause samples pointer moved during pause without another motion event")
	selection.set_preferences(true, true)
	await frames(4)
	check(not is_instance_valid(overlay), "preference rebuild frees old overlay")
	overlay = current_overlay()
	check(overlay._reduced and not overlay.is_processing(), "runtime forwards reduced motion and stops periodic overlay processing")
	move_mouse(Vector2(400, 500))
	await frames(2)
	var static_idle := await screenshot("")
	idle_crops.clear()
	for i in 7: idle_crops.append(crop(static_idle, point_for(overlay, i)))
	for i in 7:
		move_mouse(point_for(overlay, i))
		await frames(2)
		check(overlay.get_active_skin() == SKINS[i] and overlay._weights[i] == 1.0 and overlay._weights.count(1.0) == 1,
			"reduced motion switches static outline immediately: " + NAMES[i])
		var rendered := await screenshot("")
		hover_crops.append(crop(rendered, point_for(overlay, i)))
		check(hover_crops[i].get_data() != idle_crops[i].get_data(), "static hover pixels differ from normal: " + NAMES[i])
	var frozen := await screenshot("standalone-reduced.png")
	await frames(10)
	var frozen_later := await screenshot("")
	check(frozen.get_data() == frozen_later.get_data() and overlay._seconds == 0,
		"reduced canvas is pixel-identical over ten rendered frames")
	move_mouse(Vector2(400, 500))
	await frames(2)
	check(overlay.get_active_skin() == "normal" and overlay._weights.count(0.0) == 7,
		"reduced mouse exit snaps to static normal")
	move_mouse(point_for(overlay, 1))
	overlay.set_presentation_state(false, true)
	check(overlay.get_active_skin() == "normal" and not overlay.is_processing_input(), "inactive contract clears hover and input immediately")
	await physical_pointer_at(point_for(overlay, 2))
	await frames(2)
	check(overlay.get_active_skin() == "normal", "inactive overlay ignores pointer motion")
	overlay.set_presentation_state(true, true)
	await frames(2)
	check(overlay.hovered_index == 2, "active contract restores current pointer without another motion event")
	overlay.hide()
	check(overlay.get_active_skin() == "normal" and not overlay.is_processing_input(), "direct hide clears interaction")
	overlay.show()
	move_mouse(point_for(overlay, 6))
	await frames(2)
	check(overlay.hovered_index == 6, "direct show restores interaction")
	var container: Control = selection.get_node("Overlay")
	container.remove_child(overlay)
	check(overlay.get_active_skin() == "normal" and connection_count(overlay) == 0 and not overlay.is_processing_input(),
		"tree exit clears state and disconnects host signals")
	container.add_child(overlay)
	overlay.set_presentation_state(true, true)
	await frames(2)
	move_mouse(point_for(overlay, 0))
	await frames(2)
	check(overlay.hovered_index == 0 and connection_count(overlay) == 1, "same overlay reentry reconnects once and receives input")
	await physical_pointer_at(point_for(overlay, 0))
	canvas.hide()
	await frames(3)
	check(selection.state == "hidden" and not is_instance_valid(overlay), "ancestor hide frees runtime overlay")
	canvas.show()
	await frames(3)
	overlay = current_overlay()
	check(overlay.hovered_index == 0 and overlay._reduced, "ancestor show rebuilds and freshly resolves stationary pointer")
	selection.set_preferences(false, false)
	await frames(3)
	check(selection.state == "original" and not is_instance_valid(overlay), "disable uses original stub and releases custom overlay")
	selection.set_preferences(true, false)
	await frames(3)
	overlay = current_overlay()
	canvas.remove_child(selection)
	await frames(3)
	check(not is_instance_valid(overlay), "selection tree exit frees overlay")
	canvas.add_child(selection)
	await frames(4)
	overlay = current_overlay()
	check(selection.get_node("Overlay").get_child_count() == 1 and connection_count(overlay) == 1, "selection reentry creates exactly one overlay")
	# Resize/layout changes exercise canvas coordinates, not an untransformed hit map.
	overlay.layout_offset = Vector2(-50, 25)
	overlay.layout_scale = 0.92
	overlay.constellation_positions = PackedVector2Array([Vector2(1190, 330)])
	move_mouse(point_for(overlay, 0))
	await frames(3)
	check(overlay.hovered_index == 0, "exported offset, scale and per-motif position align drawing and hit map")
	root.size = Vector2i(1280, 720)
	await frames(3)
	move_mouse(point_for(overlay, 0))
	await frames(3)
	check(overlay.hovered_index == 0, "resized extended canvas still uses transformed hit coordinates")
	root.size = Vector2i(1920, 1080)
	await frames(3)
	# An isolated overlay must not advance Godot's global RNG at construction or on input.
	seed(210107)
	var expected := randi()
	seed(210107)
	var probe: Control = OVERLAY.instantiate()
	stage.add_child(probe)
	probe.set_presentation_state(true, false)
	move_mouse(point_for(probe, 1))
	for i in 8: probe._process(0.02)
	check(randi() == expected, "construction, drawing clock and hover leave global RNG unchanged")
	probe.queue_free()
	selection.queue_free()
	await frames(3)
	var baseline_connections := root.mouse_exited.get_connections().size()
	var refs: Array[WeakRef] = []
	for i in 12:
		var quick := new_selection()
		refs.append(weakref(quick.get_node("Overlay").get_child(0)))
		canvas.remove_child(quick)
		quick.queue_free()
	await frames(4)
	var released := true
	for ref in refs: released = released and ref.get_ref() == null
	check(released and root.mouse_exited.get_connections().size() == baseline_connections,
		"twelve rapid selection replacements release overlays and signal connections")
	stage.queue_free()
	await frames(3)
	await contact_sheet()
	print("CHECKS=", checks, " FAILURES=", failures, " (standalone production overlay; UI/sky fixtures; native game untested)")
	quit(1 if failures else 0)

func contact_sheet() -> void:
	var sheet := Control.new()
	root.add_child(sheet)
	var fill := ColorRect.new()
	fill.size = Vector2(1920, 1080)
	fill.color = Color("0b1424")
	sheet.add_child(fill)
	label_at(sheet, "REGENT / SEVEN CONSTELLATIONS", Vector2(36, 36), 34)
	label_at(sheet, "Production Godot overlay  |  callback order 1-7  |  temporary sky/UI fixture  |  reduced motion", Vector2(36, 85), 23)
	label_at(sheet, "NORMAL", Vector2(36, 162), 20)
	label_at(sheet, "STATIC HOVER / no periodic animation", Vector2(36, 568), 20)
	for i in 7:
		label_at(sheet, str(i + 1) + "  " + NAMES[i], Vector2(22 + i * 271, 206), 19)
		for row in 2:
			var texture := TextureRect.new()
			texture.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
			texture.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
			texture.texture = ImageTexture.create_from_image(idle_crops[i] if row == 0 else hover_crops[i])
			sheet.add_child(texture)
			texture.position = Vector2(17 + i * 271, 244 + row * 384)
			texture.size = Vector2(260, 260)
	label_at(sheet, "Drawn geometry adapts the original seven atlas motifs; it does not redistribute the source atlas or add zodiac lore.", Vector2(36, 985), 21)
	await frames(3)
	await screenshot("seven-modes.png")
	sheet.queue_free()
	await frames(3)
