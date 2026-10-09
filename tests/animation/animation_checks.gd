extends SceneTree
const PUPPET = preload("res://PopSpireWomen/animation/puppet.gd")
const SCHEMA = preload("res://PopSpireWomen/animation/rig_schema.gd")
const READER = preload("res://PopSpireWomen/animation/driver_reader.gd")
const BINDINGS = preload("res://PopSpireWomen/animation/binding_lease.gd")
const LEASE = preload("res://PopSpireWomen/animation/draw_lease.gd")
const MOCK = preload("res://PopSpireWomen/test-fixtures/mock_driver.gd")
const PATH = "res://PopSpireWomen/test-fixtures/rig.json"
var failures := 0
var checks := 0
var output := ""

func _initialize() -> void: _run.call_deferred()
func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		printerr("FAIL ", label)
	else: print("PASS ", label)

func frame() -> void:
	await process_frame
	await RenderingServer.frame_post_draw

func screenshot(name: String) -> Image:
	await frame()
	var img := root.get_texture().get_image()
	img.save_png(output.path_join(name+".png"))
	return img

func _run() -> void:
	output = OS.get_environment("PSW_ANIMATION_OUTPUT")
	root.size = Vector2i(800,600)
	root.content_scale_size = Vector2i(800,600)
	var backdrop := ColorRect.new()
	backdrop.color = Color("243047")
	backdrop.size = Vector2(800,600)
	root.add_child(backdrop)
	var puppet := PUPPET.new()
	root.add_child(puppet)
	check(puppet.load_rig(PATH,"SILENT"), "JSON rig and three separate alpha layers load from exported fixture PCK")
	puppet.position = Vector2(400,550)
	var rig: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PATH))
	var bad := rig.duplicate(true)
	bad.markers.erase("hand_r")
	check(not SCHEMA.validate(bad).is_empty(), "Missing hand marker rejected before replacing original")
	bad = rig.duplicate(true)
	bad.body = "res://PopSpireWomen/../foreign.png"
	check(not SCHEMA.validate(bad).is_empty(), "Escaping texture path rejected")
	bad = rig.duplicate(true)
	bad.clips = {"attack":{"head":[[0.9,0,0,0],[0.1,1,0,0]]}}
	check(not SCHEMA.validate(bad).is_empty(), "Unordered normalized keys rejected")
	puppet.sample_animation("idle_loop",0,true,0)
	var neutral: PackedVector2Array = puppet.get_node("body").polygon.duplicate()
	var rest_head := puppet.anchor_position("face")
	var rest_hand := puppet.anchor_position("weapon")
	var idle := await screenshot("idle")
	var visible_pixels := 0
	var cloth_pixels := 0
	for y in range(0,600,4):
		for x in range(0,800,4):
			if idle.get_pixel(x,y).r > 0.5: visible_pixels += 1
			if idle.get_pixel(x,y).is_equal_approx(Color("396b88")): cloth_pixels += 1
	check(cloth_pixels > 10, "Negative local layer order still renders cloth in front of background")
	check(visible_pixels > 150, "Texture-backed triangles actually render colored fixture pixels")
	puppet.sample_animation("attack",0.34,false,0.4)
	var attack := await screenshot("attack")
	check(idle.get_data() != attack.get_data(), "Rendered attack differs from neutral frame")
	check(puppet.anchor_position("weapon").distance_to(rest_hand) > puppet.anchor_position("face").distance_to(rest_head) + 25, "Weapon hand moves independently of face; not a translated poster")
	puppet.sample_animation("idle_loop",0.4,false,1.1)
	var hair_a: PackedVector2Array = puppet.get_node("hair_back").polygon.duplicate()
	var cloth_a: PackedVector2Array = puppet.get_node("cloth").polygon.duplicate()
	puppet.sample_animation("idle_loop",0.4,false,2.3)
	check(hair_a != puppet.get_node("hair_back").polygon and cloth_a != puppet.get_node("cloth").polygon, "Hair and cloth carry independent secondary motion")
	puppet.sample_animation("select",0.2,false,4.65)
	check(puppet.get_node("eyes").visible, "Blink is a separate optional expression layer")
	puppet.sample_animation("select",0.8,true,4.65)
	check(not puppet.get_node("eyes").visible, "Reduced motion disables expression cycling")
	var reduced: PackedVector2Array = puppet.get_node("body").polygon.duplicate()
	puppet.sample_animation("select",0.2,true,8.3)
	check(reduced == puppet.get_node("body").polygon, "Reduced ambient pose is invariant across phase/time")
	var driver := MOCK.new()
	root.add_child(driver)
	driver.play("attack",1.0)
	driver.advance(0.34)
	var snap := READER.snapshot(driver)
	check(snap.tracks[0].phase == 0.34, "Native-method reader uses authoritative current animation time")
	var time_before: float = driver.animation_state.track.time
	var event_before: int = driver.events
	for i in 20: READER.snapshot(driver)
	check(time_before == driver.animation_state.track.time and event_before == driver.events, "Observer never advances tracks, forwards events or invokes command waits")
	driver.play("hurt",0.5)
	driver.advance(0.1)
	check(puppet.sample_tracks(READER.snapshot(driver).tracks,false,0.1) and puppet.last_animation == "hurt", "Hit interrupts attack immediately via observed current track")
	driver.play("hurt",0.5)
	check(READER.snapshot(driver).tracks[0].phase == 0, "Repeated same-name hit starts at new track's zero time")
	var previous = driver.animation_state.track
	previous.time = 0.25
	driver.play("die",2.0)
	driver.animation_state.track.previous = previous
	driver.animation_state.track.mix_duration = 0.2
	driver.animation_state.track.mix_time = 0.1
	snap = READER.snapshot(driver)
	check(snap.tracks.size() == 2 and is_equal_approx(snap.tracks[0].weight,0.5) and is_equal_approx(snap.tracks[1].weight,0.5), "Mix reads old/new track weights without an independent wall clock")
	driver.animation_state.track.previous = null
	driver.advance(2.5)
	puppet.sample_tracks(READER.snapshot(driver).tracks,false,2.5)
	var dead: PackedVector2Array = puppet.get_node("body").polygon.duplicate()
	await screenshot("dead")
	driver.advance(20)
	puppet.sample_tracks(READER.snapshot(driver).tracks,false,22.5)
	check(dead == puppet.get_node("body").polygon, "Death holds final pose indefinitely including initial-dead seek")
	check(dead != neutral, "Death endpoint does not show living neutral pose")
	driver.play("idle_loop",2,true)
	puppet.sample_tracks(READER.snapshot(driver).tracks,true,0)
	check(neutral == puppet.get_node("body").polygon, "Revive idle reset clears corpse pose")
	puppet.modulate.a = 0.0
	var faded := await screenshot("revive-transparent")
	puppet.modulate.a = 1.0
	check(faded.get_data() != (await screenshot("revived")).get_data(), "Parent/visual alpha fade also affects custom mesh")
	driver.play("idle_loop",2,true)
	driver.advance(5)
	check(READER.snapshot(driver).tracks[0].phase == 0.5, "Loop phase follows wrapped animation time")
	driver.play("attack",2)
	driver.advance(1.5)
	check(READER.snapshot(driver).tracks[0].phase == 0.75, "Speed/seek represented by driver time, independent of frame delta")
	check(not puppet.sample_animation("unmapped_future_state",0.2,false,0), "Unknown animation requests original rendering fallback")
	var lease := LEASE.new()
	var meshes: Array = []
	for i in 3:
		var mesh := Polygon2D.new()
		driver.add_child(mesh)
		meshes.append(mesh)
	var independent_weapon := Node2D.new()
	driver.add_child(independent_weapon)
	check(lease.suppress(meshes,["shadow","body","slash_mesh"],["shadow","slash_mesh"]), "Mesh suppression takes an exact draw-order map")
	check(not meshes[1].visible and meshes[0].visible and meshes[2].visible and driver.visible and independent_weapon.visible, "Only body drawing hidden; driver, slash and independent weapon visible")
	driver.advance(0.1)
	check(driver.events == event_before+6, "Suppression leaves simulated driver event progression running")
	check(not lease.suppress(meshes,["wrong-size"],[]), "Changed slot/mesh contract fails closed")
	lease.restore()
	check(meshes[1].visible, "Error/disable lease restores original drawing")
	meshes[1].visible = false
	lease.suppress(meshes,["shadow","body","slash_mesh"],[])
	meshes[0].free()
	lease.restore()
	check(not meshes[1].visible, "Restore preserves preexisting hidden state and tolerates freed mesh")
	var vfx := Node2D.new()
	vfx.name = "Vfx"
	driver.add_child(vfx)
	vfx.position = Vector2(17,23)
	vfx.rotation = 0.3
	vfx.scale = Vector2(2,3)
	var bindings := BINDINGS.new()
	check(bindings.configure(driver,driver,[{"path":"Vfx","anchor":"weapon"}]), "Effect anchor binding uses existing descendant")
	puppet.sample_animation("attack",0.34,false,0.4)
	check(bindings.apply(puppet) and vfx.global_position.is_equal_approx(puppet.to_global(puppet.anchor_position("weapon"))), "VFX follows deformed weapon-hand anchor in world space")
	check(is_equal_approx(vfx.rotation,0.3) and vfx.scale == Vector2(2,3), "Anchor retarget leaves effect rotation and scale alone")
	bindings.restore()
	check(vfx.position == Vector2(17,23), "Fallback restores original effect position")
	vfx.position = Vector2(50,50)
	bindings.restore()
	check(vfx.position == Vector2(50,50), "Inactive binding does not overwrite subsequent original motion")
	bindings.apply(puppet)
	vfx.free()
	check(not bindings.apply(puppet), "Removed effect requests fallback before partial mapping")
	bindings.restore()
	check(not bindings.configure(driver,driver,[{"path":".","anchor":"weapon"}]), "Binding cannot take over original driver")
	var custom := rig.duplicate(true)
	custom.meshes = [{"id":"body", "texture":rig.body, "vertices":[[0,0],[1024,0],[1024,1536],[0,1536]], "uv":[[0,0],[1024,0],[1024,1536],[0,1536]], "triangles":[[0,1,2],[0,2,3]], "weights":[{"head":1},{"head":1},{"foot_r":0.5,"hip":0.5},{"foot_l":0.5,"hip":0.5}]}]
	check(puppet.configure(custom,"DEFECT"), "Explicit JSON UVs, triangles and per-joint weights accepted")
	custom.meshes[0].weights[0] = {"head":0.5}
	check(not SCHEMA.validate(custom).is_empty(), "Unnormalized vertex weights rejected")
	for id in ["IRONCLAD","SILENT","REGENT","NECROBINDER","DEFECT"]:
		check(puppet.configure(rig,id), "Marker rig available for " + id)
		for animation in ["idle_loop","attack","attack_heavy","cast","cast_mighty","process","shiv","attack_sovereign","hurt","die","relaxed_loop","overgrowth_loop","hive_loop","glory_loop","select"]:
			check(puppet.sample_animation(animation,0.45,false,1), id+" accepts "+animation)
	# Parse/instantiate the actual adapter scene even though this standard Godot has no native Spine.
	var bridge: Node = load("res://PopSpireWomen/animation/driver_overlay.tscn").instantiate()
	bridge.free()
	puppet.free()
	driver.free()
	backdrop.free()
	await process_frame
	print("CHECKS=",checks," FAILURES=",failures," (standalone Godot; game connection unexecuted)")
	quit(1 if failures else 0)
