extends SceneTree

func _initialize() -> void:
    call_deferred("_inspect")

func _inspect() -> void:
    var actual := OS.get_user_data_dir().replace("\\", "/")
    var expected := OS.get_environment("PSW_QA_USERDIR").replace("\\", "/")
    var isolated := not expected.is_empty() and actual.to_lower() == expected.to_lower() and "popspirewomenqa" in actual.to_lower()
    var report := {
        "engine": Engine.get_version_info(),
        "user_data_dir": actual,
        "expected_user_data_dir": expected,
        "isolated": isolated,
        "spine_sprite_class": ClassDB.class_exists("SpineSprite"),
        "spine_mesh_class": ClassDB.class_exists("SpineMesh2D"),
        "display_server": DisplayServer.get_name(),
        "game_scene_started": false,
        "command_line": OS.get_cmdline_args()
    }
    print("PSW_ENVIRONMENT " + JSON.stringify(report))
    if isolated:
        var path := OS.get_environment("PSW_QA_REPORT")
        if not path.is_empty():
            var file := FileAccess.open(path, FileAccess.WRITE)
            if file != null:
                file.store_string(JSON.stringify(report, "  "))
    quit(0 if isolated and report.spine_sprite_class else 2)
