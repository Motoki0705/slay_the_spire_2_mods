extends SceneTree
const BASE = "res://PopSpireWomen/select/select_background.tscn"
const FIXTURE = "res://PopSpireWomen/test-fixtures/"
const CONTRACT = preload("res://PopSpireWomen/animation/selection_video.gd")
var failures := 0
var checks := 0
var presses := 0
var host: Control

func _initialize() -> void: _run.call_deferred()
func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		printerr("FAIL ", label)
	else: print("PASS ", label)
func frames(count := 2) -> void:
	for i in count: await process_frame
func selection(id := "SILENT", movie := FIXTURE+"movie.ogv") -> Control:
	var node: Control = load(BASE).instantiate()
	node.character_entry = id
	node.poster_path = FIXTURE+"video-poster.png"
	node.video_path = movie
	node.rig_path = FIXTURE+"rig.json"
	if id == "REGENT": node.overlay_scene_path = "res://PopSpireWomen/select/overlays/regent/constellations.tscn"
	node.set_preferences(true, false)
	host.add_child(node)
	return node
func screen_rect(control: Control) -> Rect2:
	return control.get_global_transform_with_canvas() * Rect2(Vector2.ZERO, control.size)
func capture(name: String) -> Image:
	await RenderingServer.frame_post_draw
	var img := root.get_texture().get_image()
	img.save_png(OS.get_environment("PSW_ANIMATION_OUTPUT").path_join(name+".png"))
	return img
func remove(node: Control) -> void:
	var player: VideoStreamPlayer = node._video
	host.remove_child(node)
	check(node.state == "inactive" and node._video == null and not node.is_processing(), "exit releases decoder and stops scene processing")
	if is_instance_valid(player): check(player.stream == null and not player.is_playing(), "detached player releases stream and audio immediately")
	node.queue_free()

func _run() -> void:
	root.size = Vector2i(1280,720)
	root.content_scale_size = Vector2i(1280,720)
	host = Control.new()
	host.mouse_filter = Control.MOUSE_FILTER_IGNORE
	host.position = Vector2(-650,-160)
	host.size = Vector2(2560,1200)
	host.scale = Vector2(1.2,1.2)
	root.add_child(host)
	var button := Button.new()
	button.position = Vector2(1030,650)
	button.size = Vector2(220,50)
	button.text = "Input fixture"
	button.pressed.connect(func(): presses += 1)
	root.add_child(button)
	check(CONTRACT.inspect(FIXTURE+"movie.ogv").is_empty(), "complete silent 768P Theora accepted from PCK")
	for path in ["invalid.ogv", "truncated.ogv", "missing.ogv", "with-audio.ogv"]:
		check(not CONTRACT.inspect(FIXTURE+path).is_empty(), "bad video rejected before decoder: "+path)
	for id in ["IRONCLAD","SILENT","REGENT","NECROBINDER","DEFECT"]:
		var node := selection(id)
		await frames(5)
		check(node.state == "video" and node._puppet == null and node.get_node("Layers").get_child_count() == 0, id+" uses movie with no second character")
		remove(node)
		await frames()
	var node := selection()
	await frames(12)
	check(node._video.volume == 0.0 and node._video.mouse_filter == Control.MOUSE_FILTER_IGNORE, "decoder is muted and input transparent")
	var rect := screen_rect(node._video)
	check(rect.encloses(Rect2(0,0,1280,720)) and absf(rect.size.x-1280) < 8, "viewport-cover cancels enlarged 2560x1200 parent")
	var first := await capture("video-a")
	await frames(20)
	var second := await capture("video-b")
	check(first.get_data() != second.get_data(), "actual decoded movie pixels change")
	var looped := false
	var last: float = node._video.stream_position
	for i in 110:
		await frames(1)
		var now: float = node._video.stream_position
		if now < last: looped = true
		last = now
	check(looped and node.state == "video", "short fixture loops through EOF without falling back")
	paused = true
	var before: float = node._video.stream_position
	await frames(10)
	check(is_equal_approx(before,node._video.stream_position), "tree pause freezes decoder")
	paused = false
	await frames(10)
	check(not is_equal_approx(before,node._video.stream_position), "tree resume advances decoder")
	host.position += Vector2(75,-35)
	host.scale = Vector2(1.1,1.35)
	await frames(2)
	check(screen_rect(node._video).is_equal_approx(rect), "movie stays composed while background parent pans and scales")
	for viewport_size: Vector2i in [Vector2i(1024,768),Vector2i(1600,720)]:
		root.size = viewport_size
		root.content_scale_size = viewport_size
		await frames(4)
		var crop := screen_rect(node._video)
		check(crop.encloses(Rect2(Vector2.ZERO,Vector2(viewport_size))) and absf(crop.size.x/crop.size.y-1360.0/768.0) < 0.001, "resize covers viewport without distorting movie: "+str(viewport_size))
	root.size = Vector2i(1280,720)
	root.content_scale_size = Vector2i(1280,720)
	await frames(4)
	node.set_preferences(true,true)
	check(node.state == "poster" and node._video == null and node._puppet == null, "reduced motion switches to composition-matched static poster")
	check(screen_rect(node._video_poster).is_equal_approx(rect), "poster and movie have identical viewport crop")
	node.set_preferences(true,false)
	await frames(4)
	check(node.state == "video" and node._video.stream_position < 0.5, "motion restore restarts movie")
	host.hide()
	check(node.state == "hidden" and node._video == null and not node.is_processing(), "ancestor hide stops and releases movie")
	host.show()
	await frames(4)
	check(node.state == "video", "ancestor show reconstructs movie")
	node.set_preferences(false,false)
	check(node.state == "original" and node._video == null and node._puppet == null, "disabled restores original alias without custom media")
	node.set_preferences(true,false)
	node._video.stop()
	await frames()
	check(node.state == "poster" and node._video == null, "unexpected decoder stop falls back instead of blank screen")
	remove(node)
	await frames()
	for path in ["invalid.ogv", "truncated.ogv", "missing.ogv"]:
		node = selection("SILENT",FIXTURE+path)
		check(node.state == "poster" and node._video == null, "configured bad movie uses static poster: "+path)
		remove(node)
		await frames()
	node = selection("SILENT",FIXTURE+"missing.ogv")
	node.configure("",FIXTURE+"rig.json",FIXTURE+"missing.ogv")
	await frames()
	var polygon: PackedVector2Array = node._puppet.get_node("body").polygon.duplicate()
	await frames(10)
	check(node.state == "rig" and node._freeze_rig and polygon == node._puppet.get_node("body").polygon, "missing movie and poster use frozen Godot fallback")
	remove(node)
	await frames()
	# Use all seven authored hover regions, over an active movie, without consuming clicks.
	host.position = Vector2.ZERO
	host.scale = Vector2(0.5,0.5)
	node = selection("REGENT")
	await frames(2)
	var overlay = node.get_node("Overlay").get_child(0)
	for i in 7:
		var event := InputEventMouseMotion.new()
		event.position = overlay.get_global_transform_with_canvas() * overlay.constellation_position(i)
		Input.parse_input_event(event)
		await frames(2)
		check(overlay.hovered_index == i and node.state == "video", "Regent movie preserves hover "+str(i))
	for down in [true,false]:
		var click := InputEventMouseButton.new()
		click.button_index = MOUSE_BUTTON_LEFT
		click.position = Vector2(1150,675)
		click.pressed = down
		Input.parse_input_event(click)
		await frames()
	check(presses == 1, "UI remains clickable above Regent movie and hover overlay")
	var overlay_image := await capture("video-regent-overlay")
	check(overlay_image.get_pixel(20,700).s > 0.2, "viewport movie pixels extend past smaller original parent rectangle")
	if OS.get_environment("PSW_RECORD_VIDEO") == "1":
		var label := Label.new()
		label.text = "Godot 4.5.1 technical fixture / not H3 or game footage"
		label.position = Vector2(260,670)
		root.add_child(label)
		var directory := OS.get_environment("PSW_ANIMATION_OUTPUT").path_join("recording")
		DirAccess.make_dir_recursive_absolute(directory)
		for frame in 28:
			var pointer := InputEventMouseMotion.new()
			pointer.position = overlay.get_global_transform_with_canvas() * overlay.constellation_position(frame / 4)
			Input.parse_input_event(pointer)
			await create_timer(1.0/12.0).timeout
			await RenderingServer.frame_post_draw
			root.get_texture().get_image().save_png(directory.path_join("%03d.png" % frame))
		label.queue_free()
	host.remove_child(node)
	await frames()
	host.add_child(node)
	await frames(4)
	check(node.state == "video" and node.get_node("ViewportMedia").get_child_count() == 2 and node.get_node("Overlay").get_child_count() == 1, "re-entry creates exactly one decoder and overlay")
	remove(node)
	await frames()
	for i in 10:
		node = selection()
		remove(node)
	await frames(3)
	check(host.get_child_count() == 0, "rapid character switches leave no active decoder")
	host.queue_free()
	button.queue_free()
	await frames(3)
	print("CHECKS=",checks," FAILURES=",failures," (synthetic selection video; not H3 or game evidence)")
	quit(1 if failures else 0)
