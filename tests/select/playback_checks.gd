extends SceneTree

const BASE = "res://PopSpireWomen/select/select_background.tscn"
const FIXTURE = "res://PopSpireWomen/test-fixtures/"
var host: Control
var checks: Array[String] = []
var failures: Array[String] = []
var pressed := 0
var finished := 0

func _initialize() -> void:
	_run.call_deferred()

func check(condition: bool, label: String) -> void:
	if condition:
		checks.append(label)
		print("PASS ", label)
	else:
		failures.append(label)
		printerr("FAIL ", label)

func frames(count: int = 2) -> void:
	for index in count:
		await process_frame

func until(predicate: Callable, seconds: float = 5.0) -> bool:
	var deadline := Time.get_ticks_msec() + int(seconds * 1000.0)
	while not predicate.call() and Time.get_ticks_msec() < deadline:
		await process_frame
	return predicate.call()

func background(video: String = "a.ogv", overlay: bool = false) -> Control:
	var result: Control = load(BASE).instantiate()
	result.poster_path = FIXTURE + "poster.png"
	result.video_path = FIXTURE + video
	if overlay:
		result.overlay_scene_path = FIXTURE + "overlay.tscn"
	host.add_child(result)
	return result

func remove_background(node: Control) -> void:
	host.remove_child(node) # Matches the game's RemoveChildSafely then QueueFree lifecycle.
	check(node.get_node("Video").stream == null and node.state == "inactive", "exit releases decoder immediately")
	node.queue_free()

func _run() -> void:
	root.size = Vector2i(384, 216)
	host = Control.new()
	host.name = "AnimatedBgStub"
	host.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(host)
	host.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var button := Button.new()
	button.text = "Embark (test)"
	button.position = Vector2(255, 170)
	button.size = Vector2(125, 42)
	button.pressed.connect(func(): pressed += 1)
	root.add_child(button)

	for id in ["ironclad", "silent", "regent", "necrobinder", "defect"]:
		var descriptor: Control = load("res://PopSpireWomen/select/%s.tscn" % id).instantiate()
		host.add_child(descriptor)
		check(descriptor.character_entry == id.to_upper() and descriptor.state == "original", "disabled descriptor restores original stub: " + id)
		remove_background(descriptor)
	await frames()
	ProjectSettings.set_setting("PopSpireWomen/select/enabled", true)
	ProjectSettings.set_setting("PopSpireWomen/select/reduced_motion", true)
	var reduced_start := background()
	check(reduced_start.state == "poster" and reduced_start.get_node("Video").stream == null, "startup reduced motion never requests a decoder")
	remove_background(reduced_start)
	await frames()
	ProjectSettings.set_setting("PopSpireWomen/select/reduced_motion", false)
	var a := background("a.ogv", true)
	check(a.state == "loading" and a.get_node("Poster").visible and not a.get_node("Video").visible, "poster covers initial threaded load and decode")
	check(a.mouse_filter == Control.MOUSE_FILTER_IGNORE and a.get_node("Poster").mouse_filter == Control.MOUSE_FILTER_IGNORE and a.get_node("Video").mouse_filter == Control.MOUSE_FILTER_IGNORE, "background controls ignore UI input")
	check(await until(func(): return a.state == "playing"), "Theora fixture starts playing")
	var video: VideoStreamPlayer = a.get_node("Video")
	video.finished.connect(func(): finished += 1)
	check(video.loop and video.volume == 0.0, "native loop with muted player")
	var image_before := video.get_video_texture().get_image()
	var before_hash := hash(image_before.get_data())
	await create_timer(0.25).timeout
	var image_after := video.get_video_texture().get_image()
	check(not image_after.is_empty() and before_hash != hash(image_after.get_data()), "real decoded pixels change over time")
	check(video.size.x / video.size.y == 1.5 and video.size.x >= host.size.x and video.size.y >= host.size.y, "video covers without stretching its aspect")

	var motion := InputEventMouseMotion.new()
	motion.position = Vector2(32, 32)
	Input.parse_input_event(motion)
	await frames()
	var overlay: Control = a.get_node("Overlay").get_child(0)
	check(overlay.hovers > 0 and overlay.active, "independent overlay receives hover")
	for down in [true, false]:
		var click := InputEventMouseButton.new()
		click.button_index = MOUSE_BUTTON_LEFT
		click.position = Vector2(315, 190)
		click.pressed = down
		Input.parse_input_event(click)
		await frames()
	check(pressed == 1 and a.state == "playing", "UI button works during playback without waiting for movie end")
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(OS.get_environment("PSW_SELECT_OUTPUT") + "/playback.png")
	var previous := video.stream_position
	var wrapped := false
	var deadline := Time.get_ticks_msec() + 1800
	while Time.get_ticks_msec() < deadline:
		await process_frame
		if video.stream_position < previous:
			wrapped = true
		previous = video.stream_position
	check(wrapped and finished == 0 and video.is_playing(), "loop wraps without Finished or manual restart")

	a.set_preferences(true, true)
	check(a.state == "poster" and video.stream == null and a.get_node("Poster").visible, "reduced motion releases decoder and displays poster")
	await frames()
	check(a.get_node("Overlay").get_child(0).reduced, "reduced motion reaches independent overlay")
	a.set_preferences(true, false)
	check(await until(func(): return a.state == "playing"), "motion can resume")
	host.hide()
	check(a.state == "hidden" and video.stream == null, "ancestor visibility stops and releases video")
	host.show()
	check(await until(func(): return a.state == "playing"), "ancestor visibility resumes video")
	a.set_preferences(false, false)
	check(a.state == "original" and video.stream == null, "live disable restores original stub")
	a.set_preferences(true, false)
	check(await until(func(): return a.state == "playing"), "live enable starts a fresh decoder")

	var old_generation: int = a._generation
	a.configure(FIXTURE + "poster.png", FIXTURE + "missing.ogv")
	a.video_loaded(old_generation, load(FIXTURE + "a.ogv"))
	check(a.state == "poster" and video.stream == null, "missing video uses poster and stale generation cannot revive it")
	a.configure(FIXTURE + "poster.png", FIXTURE + "broken.ogv")
	check(await until(func(): return a.state == "poster"), "corrupt Theora falls back after decode failure")
	check(video.stream == null, "decode failure releases invalid stream")
	a.configure(FIXTURE + "missing.png", FIXTURE + "a.ogv")
	check(a.state == "original" and video.stream == null, "missing poster restores original stub even when video exists")
	a.configure(FIXTURE + "wrong_type.tres", FIXTURE + "a.ogv")
	check(a.state == "original", "wrong poster resource type restores original stub")
	a.configure(FIXTURE + "poster.png", FIXTURE + "a.ogv")
	check(await until(func(): return a.state == "playing"), "valid configuration recovers from failures")
	# A decoder that silently stalls must not cover the poster indefinitely.
	video.speed_scale = 0.0
	check(await until(func(): return a.state == "poster"), "decode watchdog returns to poster on stalled progress")
	video.speed_scale = 1.0

	# Remove and re-add the same node: Godot calls Ready only once.
	host.remove_child(a)
	check(video.stream == null, "detached reusable node has no stream")
	host.add_child(a)
	check(await until(func(): return a.state == "playing"), "same node re-entry restarts after Ready has already run")
	remove_background(a)
	await frames()
	check(not is_instance_valid(a), "old background is freed")

	# Request A, then B, then A in the same frame, before the loader can dispatch.
	var a1 := background("a.ogv")
	var a1_ref: WeakRef = weakref(a1)
	remove_background(a1)
	var b := background("b.ogv")
	var b_ref: WeakRef = weakref(b)
	remove_background(b)
	var a2 := background("a.ogv")
	check(await until(func(): return a2.state == "playing"), "rapid A to B to A keeps only newest scene playing")
	var loads: Node = a2._loads
	check(await until(func(): return loads.pending_count() == 0), "cancelled threaded jobs are drained without a client")
	check(a1_ref.get_ref() == null and b_ref.get_ref() == null, "cancelled old scenes have no retained references")
	remove_background(a2)
	await frames()
	var transient := background("b.ogv")
	remove_background(transient)
	check(await until(func(): return loads.pending_count() == 0), "leaving while loading still drains the request")
	await frames()
	check(host.get_child_count() == 0, "no player or overlay nodes remain after exit")
	# The independent loader also has a deterministic application shutdown path.
	var at_shutdown := background("a.ogv")
	remove_background(at_shutdown)
	check(loads.pending_count() > 0, "shutdown begins with an uncollected threaded request")
	root.remove_child(loads)
	check(loads.pending_count() == 0, "loader shutdown collects every outstanding request")
	loads.queue_free()
	host.queue_free()
	button.queue_free()
	await frames()
	var report := {"checks": checks, "failures": failures, "game_launched": false,
		"rendering_method": RenderingServer.get_current_rendering_method(), "fixture_only": true,
		"resources_loaded_from": "technical-fixtures.pck"}
	var file := FileAccess.open(OS.get_environment("PSW_SELECT_OUTPUT") + "/playback-results.json", FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  ") + "\n")
	file.close()
	print("SELECT_CHECKS=", checks.size(), " FAILURES=", failures.size())
	quit(0 if failures.is_empty() else 1)
