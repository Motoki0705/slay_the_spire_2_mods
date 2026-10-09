extends SceneTree

var control_dir := ""
var output_dir := ""
var main_game: Node
var observations: Array = []
var tracked: Array = []
var last_track_summary := ""
var last_scan := 0

func _initialize() -> void:
    call_deferred("_start")

func _start() -> void:
    var actual := OS.get_user_data_dir().replace("\\", "/").to_lower()
    var expected := OS.get_environment("PSW_QA_USERDIR").replace("\\", "/").to_lower()
    if expected.is_empty() or actual != expected or "popspirewomenqa" not in actual:
        push_error("PSW QA requires the isolated user directory")
        quit(2)
        return
    if "--force-steam=off" not in OS.get_cmdline_args():
        push_error("PSW QA requires the existing game's offline platform option")
        quit(2)
        return
    control_dir = OS.get_environment("PSW_QA_CONTROL_DIR")
    output_dir = OS.get_environment("PSW_QA_OUTPUT_DIR")
    if control_dir.is_empty() or output_dir.is_empty():
        quit(2)
        return
    DirAccess.make_dir_recursive_absolute(control_dir)
    DirAccess.make_dir_recursive_absolute(output_dir)
    var main_path := str(ProjectSettings.get_setting("application/run/main_scene"))
    var scene := load(main_path) as PackedScene
    if scene == null:
        push_error("PSW QA cannot instantiate the original main scene")
        quit(2)
        return
    main_game = scene.instantiate()
    root.add_child(main_game)
    current_scene = main_game
    _write_json("harness-ready.json", {"isolated": true, "user_dir": actual, "main_scene": main_path, "game_process_id": OS.get_process_id()})
    print("PSW_QA_HARNESS_READY")
    process_frame.connect(_observe)
    _poll()

func _poll() -> void:
    while is_instance_valid(main_game):
        var files := DirAccess.get_files_at(control_dir)
        files.sort()
        for filename in files:
            if not filename.ends_with(".json"):
                continue
            var path := control_dir.path_join(filename)
            var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
            if not data is Dictionary:
                _write_json(filename, {"ok": false, "error": "Invalid command JSON"})
            else:
                var response: Dictionary = await _execute(data)
                response["id"] = data.get("id", filename)
                _write_json(filename, response)
            DirAccess.rename_absolute(path, path + ".done")
        await create_timer(0.1).timeout

func _execute(command: Dictionary) -> Dictionary:
    match str(command.get("op", "")):
        "status":
            return {"ok": true, "size": [root.size.x, root.size.y], "paused": paused, "display": DisplayServer.get_name(), "nodes": root.get_child_count(), "mouse": [root.get_mouse_position().x, root.get_mouse_position().y]}
        "observations":
            _write_json(_safe_name(str(command.get("file", "observations.json"))), observations)
            return {"ok": true, "count": observations.size()}
        "appearance":
            var enabled := bool(command.get("enabled", true))
            var count := 0
            for node: Node in tracked:
                if not is_instance_valid(node): continue
                var script: Script = node.get_script()
                if script.resource_path.ends_with("driver_overlay.gd"):
                    if not enabled and node.get("state") == "active":
                        node.set("state", "qa_original")
                        node.call("_restore")
                        count += 1
                    elif enabled and node.get("state") == "qa_original":
                        node.set("state", "waiting")
                        node.call("_sync")
                        count += 1
            await process_frame
            return {"ok": true, "changed": count, "note": "QA-only original mesh comparison; gameplay untouched"}
        "measure":
            var seconds := clampf(float(command.get("seconds", 3)), 1, 5)
            var start := Time.get_ticks_msec()
            var frames := 0
            var process_total := 0.0
            var draw_total := 0.0
            while Time.get_ticks_msec() - start < seconds * 1000:
                await process_frame
                frames += 1
                process_total += Performance.get_monitor(Performance.TIME_PROCESS)
                draw_total += Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
            return {"ok": true, "seconds": (Time.get_ticks_msec() - start)/1000.0, "frames": frames, "mean_process_ms": process_total/maxi(frames, 1)*1000, "mean_draw_calls": draw_total/maxi(frames, 1), "video_mem_bytes": Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED)}
        "field":
            var path := str(command.get("path", ""))
            if not path.begins_with("/root/Game/"):
                return {"ok": false, "error": "Field must belong to the owned game"}
            var field := root.get_node_or_null(path)
            if field is LineEdit:
                (field as LineEdit).text = str(command.get("text", "")).left(200)
                (field as LineEdit).text_changed.emit((field as LineEdit).text)
            elif field is OptionButton:
                var options := field as OptionButton
                var index := int(command.get("index", -1))
                if index < 0 or index >= options.item_count: return {"ok": false, "error": "Invalid item"}
                options.select(index)
                options.item_selected.emit(index)
            else:
                return {"ok": false, "error": "Expected a native LineEdit or OptionButton"}
            await process_frame
            return {"ok": true}
        "mainmenu":
            if main_game.get_node_or_null("RootSceneContainer/MainMenu") == null or not main_game.has_method("ReloadMainMenu"):
                return {"ok": false, "error": "Main menu reload is only allowed outside a run"}
            main_game.call("ReloadMainMenu")
            await create_timer(1).timeout
            return {"ok": true}
        "native_visual":
            var path := str(command.get("path", ""))
            if not path.begins_with("/root/Game/RootSceneContainer/Run/RoomContainer/CombatRoom/") or "/AllyContainer/" not in path:
                return {"ok": false, "error": "Expected a player creature in the owned combat"}
            var creature := root.get_node_or_null(path)
            if creature == null or not creature.has_method("StartReviveAnim") or not creature.has_method("StartDeathAnim"):
                return {"ok": false, "error": "Native creature contract unavailable"}
            match str(command.get("action", "")):
                "death": creature.call("StartDeathAnim", false)
                "revive": creature.call("StartReviveAnim")
                _ : return {"ok": false, "error": "Unsupported visual transition"}
            await process_frame
            return {"ok": true, "kind": "Synthetic native visual transition; HP and gameplay are not changed"}
        "console":
            var text := str(command.get("text", ""))
            if text.get_slice(" ", 0) not in ["help", "card", "energy", "damage", "die", "relic", "heal", "win", "room", "fight", "stars", "remove_card"]:
                return {"ok": false, "error": "Command is outside the isolated visual QA recipe"}
            var console := main_game.get_node_or_null("CanvasLayer/ConsoleScreen")
            var field := main_game.get_node_or_null("CanvasLayer/ConsoleScreen/InputContainer/InputBufferContainer/InputBuffer") as LineEdit
            var buffer := main_game.get_node_or_null("CanvasLayer/ConsoleScreen/OutputContainer/OutputBuffer") as RichTextLabel
            if field == null or buffer == null or console == null or not console.has_method("ProcessCommand") or text.length() > 200 or "\n" in text:
                return {"ok": false, "error": "Native console unavailable or invalid command"}
            # The original, mod-enabled native console parses the text; no DLL/reflection or script evaluation.
            field.text = text
            console.call("ProcessCommand")
            await create_timer(0.7).timeout
            return {"ok": true, "native_output": buffer.get_parsed_text().right(2500)}
        "move":
            var point := Vector2(float(command.get("x", 0)), float(command.get("y", 0)))
            await _move(point)
            return {"ok": true, "mouse": [root.get_mouse_position().x, root.get_mouse_position().y]}
        "drag":
            var start := Vector2(float(command.get("x", 0)), float(command.get("y", 0)))
            var end := Vector2(float(command.get("to_x", 0)), float(command.get("to_y", 0)))
            await _move(start)
            await _button(start, true)
            for step in range(1, 13):
                await _move(start.lerp(end, step / 12.0), MOUSE_BUTTON_MASK_LEFT)
            await _button(end, false)
            await create_timer(0.45).timeout
            return {"ok": true}
        "tree":
            var rows: Array = []
            _walk(root, rows, 0)
            _write_json(_safe_name(str(command.get("file", "tree.json"))), rows)
            return {"ok": true, "count": rows.size()}
        "screenshot":
            await RenderingServer.frame_post_draw
            var image := root.get_texture().get_image()
            if image == null or image.is_empty():
                return {"ok": false, "error": "Viewport image unavailable"}
            var filename := _safe_name(str(command.get("file", "screen.png")))
            var error := image.save_png(output_dir.path_join(filename))
            return {"ok": error == OK, "file": filename, "width": image.get_width(), "height": image.get_height()}
        "record":
            var name := _safe_name(str(command.get("file", "capture")))
            if name == "invalid-output-name.json": return {"ok": false, "error": "Invalid recording name"}
            var folder := output_dir.path_join(name)
            if DirAccess.dir_exists_absolute(folder): return {"ok": false, "error": "Recording already exists"}
            DirAccess.make_dir_recursive_absolute(folder)
            var seconds := clampf(float(command.get("seconds", 6)), 1, 8)
            var fps := clampf(float(command.get("fps", 10)), 4, 15)
            var width := clampi(int(command.get("width", 1280)), 640, 1280)
            var start := Time.get_ticks_msec()
            var frames: Array = []
            while Time.get_ticks_msec() - start < seconds * 1000:
                await RenderingServer.frame_post_draw
                var stamp := Time.get_ticks_msec() - start
                var frame := root.get_texture().get_image()
                var height := int(round(frame.get_height() * width / float(frame.get_width())))
                frame.resize(width, height, Image.INTERPOLATE_LANCZOS)
                var filename := "%05d.jpg" % frames.size()
                if frame.save_jpg(folder.path_join(filename), 0.9) != OK:
                    return {"ok": false, "error": "Frame write failed"}
                frames.append({"file": filename, "time_ms": stamp})
                var wait := maxf(0.001, (frames.size() * 1000.0/fps - (Time.get_ticks_msec()-start))/1000.0)
                await create_timer(wait).timeout
            var meta := {"kind": "actual game viewport recording; no generated video", "frames": frames, "elapsed_ms": Time.get_ticks_msec()-start, "requested_fps": fps}
            var file := FileAccess.open(folder.path_join("capture.json"), FileAccess.WRITE)
            file.store_string(JSON.stringify(meta, "  "))
            return {"ok": true, "folder": name, "frames": frames.size(), "elapsed_ms": meta.elapsed_ms}
        "click":
            var point := Vector2(float(command.get("x", 0)), float(command.get("y", 0)))
            await _move(point)
            await _button(point, true)
            await _button(point, false)
            await create_timer(0.35).timeout
            return {"ok": true, "point": [point.x, point.y]}
        "key":
            var names := {"escape": KEY_ESCAPE, "enter": KEY_ENTER, "space": KEY_SPACE, "tab": KEY_TAB}
            var name := str(command.get("key", ""))
            if not names.has(name):
                return {"ok": false, "error": "Unsupported key"}
            var press := InputEventKey.new()
            press.keycode = names[name]
            press.pressed = true
            Input.parse_input_event(press)
            await process_frame
            var release := press.duplicate() as InputEventKey
            release.pressed = false
            Input.parse_input_event(release)
            return {"ok": true}
        "quit":
            call_deferred("quit", 0)
            return {"ok": true, "quit_requested": true}
        _:
            return {"ok": false, "error": "Unsupported command"}

func _move(point: Vector2, buttons := 0) -> void:
    # Card targeting reads the viewport's OS mouse position, not only event.position.
    Input.warp_mouse(point)
    var motion := InputEventMouseMotion.new()
    motion.position = point
    motion.global_position = point
    motion.relative = point - root.get_mouse_position()
    motion.button_mask = buttons
    Input.parse_input_event(motion)
    await process_frame
    await process_frame

func _button(point: Vector2, pressed: bool) -> void:
    var event := InputEventMouseButton.new()
    event.button_index = MOUSE_BUTTON_LEFT
    event.button_mask = MOUSE_BUTTON_MASK_LEFT if pressed else 0
    event.position = point
    event.global_position = point
    event.pressed = pressed
    Input.parse_input_event(event)
    await process_frame
    await process_frame

func _observe() -> void:
    if Time.get_ticks_msec() - last_scan > 600:
        tracked.clear()
        _track_nodes(root)
        last_scan = Time.get_ticks_msec()
    var sample: Array = []
    for node: Node in tracked:
        if not is_instance_valid(node) or not node.is_inside_tree(): continue
        var state := str(node.get("state"))
        var row := {"path": str(node.get_path()), "state": state, "character": str(node.get("character_entry"))}
        var script: Script = node.get_script()
        if script.resource_path.ends_with("driver_overlay.gd"):
            row["surface"] = str(node.get("surface"))
            var driver: Node = node.get("_driver")
            if is_instance_valid(driver):
                var native_state: Object = driver.call("get_animation_state")
                var entry: Object = native_state.call("get_current", 0)
                if is_instance_valid(entry):
                    var animation: Object = entry.call("get_animation")
                    if is_instance_valid(animation): row["animation"] = str(animation.call("get_name"))
            var puppet: Node2D = node.get("_puppet")
            row["custom_visible"] = is_instance_valid(puppet) and puppet.is_visible_in_tree()
        sample.append(row)
    var summary := JSON.stringify(sample)
    if summary != last_track_summary:
        observations.append({"time_ms": Time.get_ticks_msec(), "visuals": sample})
        if observations.size() > 3000: observations.pop_front()
        last_track_summary = summary

func _track_nodes(node: Node) -> void:
    var script: Script = node.get_script() as Script
    if script != null and (script.resource_path.ends_with("driver_overlay.gd") or script.resource_path.ends_with("select_background.gd")):
        tracked.append(node)
    for child in node.get_children(): _track_nodes(child)

func _walk(node: Node, rows: Array, depth: int) -> void:
    if depth > 20 or rows.size() >= 12000:
        return
    var row := {"path": str(node.get_path()), "name": str(node.name), "class": node.get_class()}
    var script: Script = node.get_script() as Script
    if script != null:
        row["script"] = script.resource_path
    if node is CanvasItem:
        row["visible"] = (node as CanvasItem).is_visible_in_tree()
    if node is Control:
        var rect := (node as Control).get_global_rect()
        row["rect"] = [rect.position.x, rect.position.y, rect.size.x, rect.size.y]
    if node is Node2D:
        var item := node as Node2D
        row["position"] = [item.global_position.x, item.global_position.y]
        row["scale"] = [item.global_scale.x, item.global_scale.y]
    if node is Label and (node as Label).is_visible_in_tree():
        row["text"] = (node as Label).text.left(180)
    if node is OptionButton:
        var options := node as OptionButton
        var items: Array = []
        for i in options.item_count: items.append(options.get_item_text(i))
        row["items"] = items
        row["selected"] = options.selected
    rows.append(row)
    for child in node.get_children():
        _walk(child, rows, depth + 1)

func _safe_name(value: String) -> String:
    var cleaned := value.get_file()
    if cleaned.is_empty() or cleaned != value:
        return "invalid-output-name.json"
    return cleaned

func _write_json(filename: String, data: Variant) -> void:
    var file := FileAccess.open(output_dir.path_join(_safe_name(filename)), FileAccess.WRITE)
    if file != null:
        file.store_string(JSON.stringify(data, "  "))
