extends SceneTree
## Uses the real schema, puppet, motion clips and unmodified production PNGs.
const PUPPET = preload("res://PopSpireWomen/animation/puppet.gd")
const SCHEMA = preload("res://PopSpireWomen/animation/rig_schema.gd")
var output := ""
var failures := 0
var checks := 0
var content: Node2D
var viewport: SubViewport

func _initialize() -> void:
	_run.call_deferred()

func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		printerr("FAIL ", label)

func label_at(text: String, point: Vector2, size := 22) -> void:
	var label := Label.new()
	label.text = text
	label.position = point
	label.add_theme_font_size_override("font_size", size)
	content.add_child(label)

func clear_content(size: Vector2i) -> void:
	if is_instance_valid(viewport): viewport.free()
	viewport = SubViewport.new()
	viewport.size = size
	viewport.disable_3d = true
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	content = Node2D.new()
	viewport.add_child(content)
	var background := ColorRect.new()
	background.size = size
	background.color = Color("283044")
	content.add_child(background)

func capture(name: String) -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	viewport.get_texture().get_image().save_png(output.path_join(name + ".png"))

func point_in_mesh(mesh: Dictionary, point: Vector2) -> Dictionary:
	for triangle: Array in mesh.triangles:
		var a := Vector2(mesh.uv[triangle[0]][0], mesh.uv[triangle[0]][1])
		var b := Vector2(mesh.uv[triangle[1]][0], mesh.uv[triangle[1]][1])
		var c := Vector2(mesh.uv[triangle[2]][0], mesh.uv[triangle[2]][1])
		var den := (b-a).cross(c-a)
		var v := (point-a).cross(c-a) / den
		var w := (b-a).cross(point-a) / den
		var u := 1.0-v-w
		if minf(u, minf(v, w)) >= -0.00001:
			return {"indices": triangle, "factors": [u, v, w]}
	return {}

func sample_point(puppet: Node2D, location: Dictionary) -> Vector2:
	var polygon: PackedVector2Array = puppet.get_node("body").polygon
	var point := Vector2.ZERO
	for i in 3:
		point += polygon[location.indices[i]] * float(location.factors[i])
	return point

func mesh_from_puppet(puppet: Node2D) -> Dictionary:
	var node: Polygon2D = puppet.get_node("body")
	var triangles: Array = []
	for triangle in node.polygons: triangles.append(Array(triangle))
	var uv: Array = []
	for point in node.uv: uv.append([point.x,point.y])
	return {"uv": uv, "triangles": triangles}

func metrics(character: String, rig: Dictionary, rule: Dictionary, dense: Array) -> Dictionary:
	var old_rig := rig.duplicate(true)
	old_rig.erase("meshes")
	var old := PUPPET.new()
	var fixed := PUPPET.new()
	root.add_child(old)
	root.add_child(fixed)
	check(old.configure(old_rig, character.to_upper()), character+" starter rig loads")
	check(fixed.configure(rig, character.to_upper()), character+" explicit rig loads")
	var old_mesh := mesh_from_puppet(old)
	var new_mesh: Dictionary = rig.meshes[0]
	var sites := {}
	var probes: Dictionary = rule.probes.duplicate()
	probes.merge(rule.protected)
	for name in probes:
		var point := Vector2(probes[name][0],probes[name][1])
		sites[name] = [point_in_mesh(old_mesh,point), point_in_mesh(new_mesh,point)]
		check(not sites[name][0].is_empty() and not sites[name][1].is_empty(), character+" probe mapped "+name)
	var result := {}
	for animation in ["attack", "attack_heavy", "shiv", "hurt", "die", "cast", "select", "idle_loop"]:
		var errors := {"before_rigid_error_px":0.0,"after_rigid_error_px":0.0,"before_length_error_fraction":0.0,"after_length_error_fraction":0.0,"protected_shift_px":0.0,"dense_body_shift_px":0.0,"dense_body_worst_source":[],"grip_error_px":0.0}
		for step in range(101):
			var phase := step / 100.0
			check(old.sample_animation(animation,phase,false,phase*2),character+" old samples "+animation)
			check(fixed.sample_animation(animation,phase,false,phase*2),character+" new samples "+animation)
			for name in rule.probes:
				var point := Vector2(probes[name][0],probes[name][1])
				var desired: Vector2 = fixed.deform_point(point,{rule.bone:1.0})-Vector2(rig.origin[0],rig.origin[1])
				var actual := sample_point(fixed,sites[name][1])
				errors.before_rigid_error_px = maxf(errors.before_rigid_error_px,sample_point(old,sites[name][0]).distance_to(desired))
				errors.after_rigid_error_px = maxf(errors.after_rigid_error_px,actual.distance_to(desired))
				if name == "grip": errors.grip_error_px = maxf(errors.grip_error_px,actual.distance_to(desired))
				for other in rule.probes:
					if name >= other: continue
					var rest_length := point.distance_to(Vector2(probes[other][0],probes[other][1]))
					var before_length := sample_point(old,sites[name][0]).distance_to(sample_point(old,sites[other][0]))
					var after_length := actual.distance_to(sample_point(fixed,sites[other][1]))
					errors.before_length_error_fraction = maxf(errors.before_length_error_fraction,absf(before_length/rest_length-1))
					errors.after_length_error_fraction = maxf(errors.after_length_error_fraction,absf(after_length/rest_length-1))
			for name in rule.protected:
				errors.protected_shift_px = maxf(errors.protected_shift_px,sample_point(old,sites[name][0]).distance_to(sample_point(fixed,sites[name][1])))
			if step in [0,16,18,34,50,72,100]:
				for site in dense:
					var shift := sample_point(old,site[0]).distance_to(sample_point(fixed,site[1]))
					if shift > errors.dense_body_shift_px:
						errors.dense_body_shift_px = shift
						errors.dense_body_worst_source = site[2]
		check(errors.after_rigid_error_px < 0.01,character+" "+animation+" follows the hand rigidly")
		check(errors.after_length_error_fraction < 0.00001,character+" "+animation+" keeps pair distances")
		check(errors.protected_shift_px < 0.01,character+" "+animation+" face, torso and feet landmarks unchanged")
		# Refinement resamples the old weight field; it is not exact interpolation
		# of old deformed triangles. Bound this local difference to 3.125 display
		# pixels at the artist rig's height 300; record the actual maximum/site.
		check(errors.dense_body_shift_px < 16,character+" "+animation+" dense visible body drift under 16 source px: "+str(errors.dense_body_shift_px))
		result[animation] = errors
	# Pose mixing changes joint angles, not the rigid weapon's local shape.
	for weight in [0.0,0.25,0.5,0.75,1.0]:
		fixed.sample_tracks([{"animation":"attack","phase":0.34,"weight":1.0-weight},{"animation":"die","phase":0.72,"weight":weight}],false,3)
		for name in rule.probes:
			var point := Vector2(probes[name][0],probes[name][1])
			var desired: Vector2 = fixed.deform_point(point,{rule.bone:1.0})-Vector2(rig.origin[0],rig.origin[1])
			check(sample_point(fixed,sites[name][1]).distance_to(desired)<0.01,character+" mixed pose rigid "+name)
	fixed.sample_animation("die",1,false,2)
	var dead: PackedVector2Array = fixed.get_node("body").polygon.duplicate()
	fixed.sample_animation("die",1,false,200)
	check(dead == fixed.get_node("body").polygon,character+" death holds")
	fixed.sample_animation("idle_loop",0,true,0)
	var neutral: PackedVector2Array = fixed.get_node("body").polygon.duplicate()
	fixed.sample_animation("attack",0.34,false,1)
	fixed.sample_animation("idle_loop",0,true,10)
	check(neutral == fixed.get_node("body").polygon,character+" revive clears weapon pose")
	var timings := []
	for puppet in [old,fixed]:
		var start := Time.get_ticks_usec()
		for i in 100: puppet.sample_animation("attack",(i%100)/100.0,false,1)
		timings.append((Time.get_ticks_usec()-start)/100.0)
	result["sampling_usec_per_pose"] = {"before":timings[0],"after":timings[1],"iterations":100}
	result["dense_body_samples"] = dense.size()
	old.free()
	fixed.free()
	return result

func _run() -> void:
	output = OS.get_environment("PSW_WEAPON_OUTPUT")
	var rules: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://weapon-rules.json"))
	var samples: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://weapon-body-samples.json"))
	var report := {}
	for character: String in rules.characters:
		var path := "res://PopSpireWomen/art/"+character+"/rig.json"
		var rig: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(path))
		check(SCHEMA.validate(rig).is_empty(),character+" schema 1")
		report[character] = metrics(character,rig,rules.characters[character],samples[character])
		clear_content(Vector2i(1800,1180))
		label_at(character + " / source rig / Godot 4.5.1 / top: before; bottom: rigid",Vector2(24,5))
		var clips := [["idle_loop",0.0],["attack",0.34],["hurt",0.18],["die",1.0]]
		for row in 2:
			for col in 4:
				var data := rig.duplicate(true)
				if row == 0: data.erase("meshes")
				data.display_height = 500
				var puppet := PUPPET.new()
				content.add_child(puppet)
				check(puppet.configure(data,character.to_upper()),character+" render configuration")
				puppet.position = Vector2(col*450+245, row*565+535)
				puppet.sample_animation(clips[col][0],clips[col][1],col==0,1.0)
				label_at(clips[col][0]+" "+str(clips[col][1]),Vector2(col*450+20,row*565+43),20)
		await capture(character+"-before-after")
		# Compare neutral images without labels/viewport resizing. UV underlays must
		# be concealed by the original weapon at rest, not repaint visible clothes.
		for fixed in [false,true]:
			clear_content(Vector2i(1024,1536))
			var data := rig.duplicate(true)
			if not fixed: data.erase("meshes")
			data.display_height = 1536
			var puppet := PUPPET.new()
			content.add_child(puppet)
			puppet.configure(data,character.to_upper())
			puppet.position = Vector2(rig.origin[0],rig.origin[1])
			puppet.sample_animation("idle_loop",0,true,0)
			await capture(character+("-neutral-after" if fixed else "-neutral-before"))
		clear_content(Vector2i(1024,1536))
		var sprite := Sprite2D.new()
		sprite.texture = load(rig.body)
		sprite.centered = false
		content.add_child(sprite)
		var outline := Line2D.new()
		for pair in rules.characters[character].polygon: outline.add_point(Vector2(pair[0],pair[1]))
		outline.closed = true
		outline.width = 2
		outline.default_color = Color("29ff8c")
		content.add_child(outline)
		for name in rules.characters[character].probes:
			var pair: Array = rules.characters[character].probes[name]
			label_at("+ "+name,Vector2(pair[0],pair[1])-Vector2(5,12),16)
		await capture(character+"-outline")
	if is_instance_valid(viewport): viewport.free()
	var file := FileAccess.open(output.path_join("metrics.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"checks":checks,"failures":failures,"characters":report},"  ")+"\n")
	file.close()
	print("CHECKS=",checks," FAILURES=",failures," (standalone production-texture weapon checks; game not launched)")
	quit(1 if failures else 0)
