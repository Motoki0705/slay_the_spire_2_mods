extends SceneTree
## Deterministic crops and alpha variants of API-created artwork; no character drawing.

func _initialize() -> void:
    var arguments := OS.get_cmdline_user_args()
    if arguments.size() != 1:
        push_error("Expected the absolute ui-recipes.json path after --")
        quit(2)
        return
    var recipes: Variant = JSON.parse_string(FileAccess.get_file_as_string(arguments[0]))
    if not recipes is Dictionary or recipes.get("schema") != 1:
        quit(2)
        return
    var receipts: Array = []
    for character: String in recipes.characters:
        var recipe: Dictionary = recipes.characters[character]
        var body_path := "res://PopSpireWomen/art/%s/body.png" % character
        var source := Image.load_from_file(ProjectSettings.globalize_path(body_path))
        var rig: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://PopSpireWomen/art/%s/rig.json" % character))
        if source == null or source.is_empty() or rig.is_empty():
            push_error("UI source missing: " + character)
            quit(2)
            return
        source.convert(Image.FORMAT_RGBA8)
        var head := Vector2(rig.markers.head[0], rig.markers.head[1] + recipe.head_y_offset)
        var width := int(recipe.head_size)
        var rect := Rect2i(int(head.x - width * 0.5), int(head.y - width * 0.5), width, width)
        var top := _resize(source.get_region(rect), Vector2i(85, 85))
        var outline := _outline(top, 3)
        var portrait_width := int(recipe.portrait_width)
        var portrait_height := int(round(portrait_width * 195.0 / 132.0))
        var portrait_rect := Rect2i(int(head.x - portrait_width * 0.5), int(head.y - portrait_height * 0.32), portrait_width, portrait_height)
        var subject := _resize(source.get_region(portrait_rect), Vector2i(132, 195))
        var portrait := Image.create(132, 195, false, Image.FORMAT_RGBA8)
        portrait.fill(Color(recipe.background))
        portrait.blend_rect(subject, Rect2i(Vector2i.ZERO, subject.get_size()), Vector2i.ZERO)
        var locked := Image.create(132, 195, false, Image.FORMAT_RGBA8)
        locked.fill(Color(0.035, 0.04, 0.045, 1))
        for y in 195:
            for x in 132:
                var shade := lerpf(0.035, 0.14, subject.get_pixel(x, y).a)
                locked.set_pixel(x, y, Color(shade, shade, shade, 1))
        var map_height := int(round(width * 64.0 / 49.0))
        var map_rect := Rect2i(int(head.x - width * 0.5), int(head.y - width * 0.48), width, map_height)
        var map_icon := _resize(source.get_region(map_rect), Vector2i(49, 64))
        var prefix := "res://PopSpireWomen/ui/" + character
        DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(prefix))
        var images := {"top": top, "outline": outline, "portrait": portrait, "locked": locked, "map": map_icon}
        var hashes := {}
        for name: String in images:
            var path := prefix + "/" + name + ".png"
            if (images[name] as Image).save_png(ProjectSettings.globalize_path(path)) != OK:
                quit(2)
                return
            hashes[name] = FileAccess.get_sha256(path)
        var scene := "[gd_scene load_steps=2 format=3]\n\n[ext_resource type=\"Texture2D\" path=\"%s/top.png\" id=\"1\"]\n\n[node name=\"CharacterIcon\" type=\"TextureRect\"]\nanchor_right = 1.0\nanchor_bottom = 1.0\ngrow_horizontal = 2\ngrow_vertical = 2\nmouse_filter = 2\ntexture = ExtResource(\"1\")\nexpand_mode = 1\nstretch_mode = 5\n" % prefix
        var scene_file := FileAccess.open(prefix + "/icon.tscn", FileAccess.WRITE)
        scene_file.store_string(scene)
        receipts.append({"character": character, "source": body_path, "source_sha256": FileAccess.get_sha256(body_path), "top_crop": [rect.position.x, rect.position.y, rect.size.x, rect.size.y], "portrait_crop": [portrait_rect.position.x, portrait_rect.position.y, portrait_rect.size.x, portrait_rect.size.y], "output_sha256": hashes})
    var file := FileAccess.open("res://PopSpireWomen/ui/build-receipt.json", FileAccess.WRITE)
    file.store_string(JSON.stringify({"schema": 1, "recipe_sha256": FileAccess.get_sha256(arguments[0]), "characters": receipts}, "  "))
    print("Created all five UI sets with the game's original texture dimensions.")
    quit(0)

func _resize(source: Image, size: Vector2i) -> Image:
    # Premultiplied filtering avoids colored fringes from fully transparent source pixels.
    source.premultiply_alpha()
    source.resize(size.x, size.y, Image.INTERPOLATE_LANCZOS)
    for y in size.y:
        for x in size.x:
            var color := source.get_pixel(x, y)
            if color.a > 0.001:
                color.r = clampf(color.r / color.a, 0, 1)
                color.g = clampf(color.g / color.a, 0, 1)
                color.b = clampf(color.b / color.a, 0, 1)
            else:
                color = Color.TRANSPARENT
            source.set_pixel(x, y, color)
    return source

func _outline(source: Image, radius: int) -> Image:
    var result := Image.create(source.get_width(), source.get_height(), false, Image.FORMAT_RGBA8)
    for y in source.get_height():
        for x in source.get_width():
            var alpha := 0.0
            for oy in range(-radius, radius + 1):
                for ox in range(-radius, radius + 1):
                    if ox * ox + oy * oy > radius * radius:
                        continue
                    var px := clampi(x + ox, 0, source.get_width() - 1)
                    var py := clampi(y + oy, 0, source.get_height() - 1)
                    alpha = maxf(alpha, source.get_pixel(px, py).a)
            result.set_pixel(x, y, Color(1, 1, 1, alpha))
    return result
