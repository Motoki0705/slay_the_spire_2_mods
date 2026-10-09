extends SceneTree
## Production PNGs/rigs through the real Godot renderer; no game process/resources.
const PUPPET = preload("res://PopSpireWomen/animation/puppet.gd")
const SCHEMA = preload("res://PopSpireWomen/animation/rig_schema.gd")
const BINDINGS = preload("res://PopSpireWomen/animation/binding_lease.gd")
var checks := 0
var failures := 0
var output := ""
var viewport: SubViewport
var content: Node2D

func _initialize() -> void:
	_run.call_deferred()

func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		printerr("FAIL ", label)

func v(point: Array) -> Vector2:
	return Vector2(point[0], point[1])

func locate(mesh: Dictionary, point: Vector2) -> Dictionary:
	for triangle: Array in mesh.triangles:
		var a := v(mesh.uv[triangle[0]])
		var b := v(mesh.uv[triangle[1]])
		var c := v(mesh.uv[triangle[2]])
		var denominator := (b-a).cross(c-a)
		if absf(denominator) < 0.000001: continue
		var y := (point-a).cross(c-a)/denominator
		var z := (b-a).cross(point-a)/denominator
		var x := 1-y-z
		if minf(x,minf(y,z)) >= -0.000001:
			return {"indices":triangle,"factors":[x,y,z]}
	return {}

func at(puppet: Node2D, site: Dictionary) -> Vector2:
	var polygon: PackedVector2Array = puppet.get_node("body").polygon
	var point := Vector2.ZERO
	for i in 3: point += polygon[site.indices[i]] * float(site.factors[i])
	return point

func binding_checks(id: String, rig: Dictionary, puppet: Node2D) -> void:
	if rig.get("bindings",[]).is_empty(): return
	var original := Node2D.new()
	root.add_child(original)
	var driver := Node2D.new()
	original.add_child(driver)
	var independent: Array[Node2D] = []
	for name in ["Osty","Weapons","Orbs"]:
		var actor := Node2D.new()
		actor.name=name
		actor.position=Vector2(101,203)
		actor.scale=Vector2(0.8,1.2)
		original.add_child(actor)
		independent.append(actor)
	var effects: Array[Node2D] = []
	for definition: Dictionary in rig.bindings:
		var parent: Node = original
		for part: String in definition.path.split("/"):
			var child: Node = parent.get_node_or_null(NodePath(part))
			if child==null:
				child=Node2D.new()
				child.name=part
				parent.add_child(child)
			parent=child
		parent.position=Vector2(17,23)
		parent.scale=Vector2(2,3)
		parent.rotation=0.37
		effects.append(parent)
	var bindings:=BINDINGS.new()
	check(bindings.configure(original,driver,rig.bindings),id+" exact VFX paths configure")
	puppet.sample_animation("attack",0.34,false,1)
	for iteration in 2:
		check(bindings.apply(puppet),id+" VFX apply")
		for i in effects.size():
			var definition: Dictionary=rig.bindings[i]
			check(effects[i].global_position.distance_to(puppet.to_global(puppet.anchor_position(definition.anchor)))<0.03,id+" VFX at measured anchor")
			check(effects[i].scale.is_equal_approx(Vector2(2,3)*v(definition.get("scale_multiplier",[1,1]))),id+" VFX scale does not compound")
			check(is_equal_approx(effects[i].rotation,0.37),id+" VFX rotation preserved")
	bindings.restore()
	for effect in effects:
		check(effect.position==Vector2(17,23) and effect.scale==Vector2(2,3),id+" VFX original position/scale restored")
	for actor in independent:
		check(actor.position==Vector2(101,203) and actor.scale==Vector2(0.8,1.2) and actor.visible,id+" independent "+actor.name+" unchanged")
	original.free()

func metrics(entry: Dictionary, rig: Dictionary) -> Dictionary:
	var id: String = entry.character+"/"+entry.surface
	check(SCHEMA.validate(rig).is_empty(), id+" schema")
	check(rig.surface==entry.surface and rig.motion_profile=="contextual_v02",id+" contextual surface")
	var puppet := PUPPET.new()
	root.add_child(puppet)
	check(puppet.configure(rig,entry.character.to_upper()), id+" loads")
	var body: Dictionary
	for mesh: Dictionary in rig.meshes:
		if mesh.id == "body": body = mesh
	var probes: Dictionary = entry.get("probes",{}).duplicate(true)
	if entry.has("weapon"):
		for name: String in entry.weapon.probes:
			probes["weapon_"+name] = {"position":entry.weapon.probes[name],"bone":rig.weapon_hand}
	var sites := {}
	for name: String in probes:
		sites[name] = locate(body,v(probes[name].position))
		check(not sites[name].is_empty(),id+" probe exists "+name)
	var ambient: String = {"combat":"idle_loop","merchant":"relaxed_loop","rest":"overgrowth_loop"}[entry.surface]
	var animations := [ambient,"attack","cast","hurt","die"]
	if entry.surface=="combat":
		animations.append({"ironclad":"attack_heavy","silent":"shiv","regent":"attack_sovereign","necrobinder":"cast_mighty","defect":"process"}[entry.character])
	if entry.surface=="rest": animations.append_array(["hive_loop","glory_loop"])
	var results := {}
	for animation: String in animations:
		var error := 0.0
		var fixed_error := 0.0
		var distance_error := 0.0
		var neutral := PackedVector2Array()
		var maximum_change := 0.0
		for step in range(51):
			var phase := step/50.0
			check(puppet.sample_animation(animation,phase,false,phase*4),id+" sample "+animation)
			var polygon: PackedVector2Array = puppet.get_node("body").polygon
			if step==0: neutral = polygon.duplicate()
			for name: String in probes:
				if sites[name].is_empty(): continue
				var source := v(probes[name].position)
				var actual := at(puppet,sites[name])
				var desired: Vector2 = puppet.deform_point(source,{probes[name].bone:1.0})-v(rig.origin)
				error = maxf(error,actual.distance_to(desired))
				if probes[name].get("fixed",false): fixed_error=maxf(fixed_error,actual.distance_to(source-v(rig.origin)))
				for other: String in probes:
					if other<=name or sites[other].is_empty() or probes[other].bone!=probes[name].bone: continue
					var original_distance := source.distance_to(v(probes[other].position))
					if original_distance>1:
						distance_error=maxf(distance_error,absf(actual.distance_to(at(puppet,sites[other]))-original_distance))
			for i in polygon.size(): maximum_change=maxf(maximum_change,polygon[i].distance_to(neutral[i]))
		check(error<0.03,id+" rigid probes "+animation+" "+str(error))
		check(fixed_error<0.03,id+" contacts fixed "+animation+" "+str(fixed_error))
		check(distance_error<0.03,id+" bone pair lengths "+animation+" "+str(distance_error))
		check(maximum_change>0.1,id+" has local motion "+animation)
		results[animation]={"rigid_error_px":error,"contact_error_px":fixed_error,"pair_distance_error_px":distance_error,"max_vertex_motion_px":maximum_change}
	puppet.sample_animation("die",1,false,2)
	var dead: PackedVector2Array = puppet.get_node("body").polygon.duplicate()
	puppet.sample_animation("die",1,false,200)
	check(dead==puppet.get_node("body").polygon,id+" death held independent of seconds")
	puppet.sample_animation(ambient,0,true,0)
	var reset: PackedVector2Array = puppet.get_node("body").polygon.duplicate()
	puppet.sample_animation("attack",0.34,false,2)
	puppet.sample_animation(ambient,0.8,true,100)
	check(reset==puppet.get_node("body").polygon,id+" revive/reduced ambient reset")
	for weight in [0.0,0.3,0.7,1.0]:
		puppet.sample_tracks([{"animation":"attack","phase":0.34,"weight":1-weight},{"animation":"hurt","phase":0.18,"weight":weight}],false,3)
		for name: String in probes:
			if sites[name].is_empty(): continue
			var expected: Vector2 = puppet.deform_point(v(probes[name].position),{probes[name].bone:1.0})-v(rig.origin)
			check(at(puppet,sites[name]).distance_to(expected)<0.03,id+" mixed pose "+name)
	for name: String in rig.anchors:
		var anchor: Dictionary = rig.anchors[name]
		check(puppet.anchor_position(name).distance_to(puppet.deform_point(v(anchor.position),{anchor.bone:1.0})-v(rig.origin))<0.03,id+" anchor "+name)
	binding_checks(id,rig,puppet)
	puppet.free()
	return results

func clear_content(size: Vector2i) -> void:
	if is_instance_valid(viewport): viewport.free()
	viewport=SubViewport.new()
	viewport.size=size
	viewport.disable_3d=true
	viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	content=Node2D.new()
	viewport.add_child(content)
	var background:=ColorRect.new()
	background.size=size
	background.color=Color("292f3d")
	content.add_child(background)

func label_at(text: String, position: Vector2, size:=20) -> void:
	var label:=Label.new()
	label.text=text
	label.position=position
	label.add_theme_font_size_override("font_size",size)
	content.add_child(label)

func capture(name: String) -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	viewport.get_texture().get_image().save_png(output.path_join(name+".png"))

func draw_rig(entry: Dictionary, rig: Dictionary, origin: Vector2, animation: String, phase: float, reduced:=false) -> Node2D:
	var data:=rig.duplicate(true)
	var bounds: Array = entry.get("preview_bounds",[0,0,rig.canvas[0],rig.canvas[1]])
	var drawing_scale: float = 540.0/float(bounds[3])
	data.display_height=rig.canvas[1]*drawing_scale
	var puppet:=PUPPET.new()
	content.add_child(puppet)
	check(puppet.configure(data,entry.character.to_upper()),entry.character+" render")
	# Source canvas top left stays consistent for all contexts, regardless of hip/foot origin.
	puppet.position=origin+(v(rig.origin)-Vector2(bounds[0],bounds[1]))*drawing_scale
	puppet.sample_animation(animation,phase,reduced,phase*4)
	return puppet

func _run() -> void:
	output=OS.get_environment("PSW_CONTEXTUAL_OUTPUT")
	var entries: Array = JSON.parse_string(FileAccess.get_file_as_string("res://contextual-inputs.json")).poses
	var report:={}
	for entry: Dictionary in entries:
		var id: String = entry.character+"-"+entry.surface
		var rig: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://PopSpireWomen/rigs/"+entry.character+"/"+entry.surface+".json"))
		report[id]=metrics(entry,rig)
		var ambient: String = {"combat":"idle_loop","merchant":"relaxed_loop","rest":"overgrowth_loop"}[entry.surface]
		clear_content(Vector2i(1600,620))
		label_at(id+" / Godot 4.5.1 / standalone production texture",Vector2(15,5))
		var poses: Array = [[ambient,0.0],[ambient,0.5],["attack",0.34],["die",1.0]]
		if entry.surface=="combat": poses[1]=["hurt",0.18]
		for i in 4:
			draw_rig(entry,rig,Vector2(i*400+18,65),poses[i][0],poses[i][1],i==0)
			label_at(poses[i][0]+" "+str(poses[i][1]),Vector2(i*400+15,35),18)
		await capture(id+"-states")
		# Neutral renderer comparison catches atlas patches that repaint visible pixels.
		for is_mesh in [false,true]:
			clear_content(Vector2i(rig.canvas[0],rig.canvas[1]))
			var data:=rig.duplicate(true)
			if not is_mesh:
				data.meshes = rig.meshes.filter(func(mesh): return mesh.id.begins_with("support_"))
				var points: Array = [[0,0],[rig.canvas[0],0],rig.canvas,[0,rig.canvas[1]]]
				data.meshes.append({"id":"body","texture":rig.body,"vertices":points,"uv":points,
					"weights":[{"root":1},{"root":1},{"root":1},{"root":1}],"triangles":[[0,1,2],[0,2,3]]})
			data.display_height=rig.canvas[1]
			var puppet:=PUPPET.new()
			content.add_child(puppet)
			puppet.configure(data,entry.character.to_upper())
			puppet.position=v(rig.origin)
			puppet.sample_animation(ambient,0,true,0)
			await capture(id+("-neutral-mesh" if is_mesh else "-neutral-original"))
		# A real renderer frame sequence, later encoded as a review GIF.
		clear_content(Vector2i(800,620))
		label_at(id+" / ambient + "+("attack" if entry.surface=="combat" else ambient),Vector2(15,8))
		var left:=draw_rig(entry,rig,Vector2(18,60),ambient,0)
		var right:=draw_rig(entry,rig,Vector2(418,60),ambient,0)
		for frame in 24:
			var phase:=frame/23.0
			left.sample_animation(ambient,phase,false,phase*4)
			right.sample_animation("attack" if entry.surface=="combat" else ambient,phase,false,phase*4+1.2)
			await capture(id+"-frame-%02d"%frame)
	if is_instance_valid(viewport): viewport.free()
	var file:=FileAccess.open(output.path_join("metrics.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"checks":checks,"failures":failures,"poses":report},"  ")+"\n")
	file.close()
	print("CHECKS=",checks," FAILURES=",failures," (context rigs; game not launched)")
	quit(1 if failures else 0)
