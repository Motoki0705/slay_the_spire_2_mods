extends Node
## A single tree-owned drain for ResourceLoader's non-cancellable threaded requests.
## Clients are weak references; leaving a background never waits for file I/O.

static var _instance: WeakRef
var _pending: Dictionary = {}

static func for_tree(tree: SceneTree) -> Node:
	var current: Node = _instance.get_ref() if _instance != null else null
	if not is_instance_valid(current):
		current = load("res://PopSpireWomen/select/video_loads.gd").new()
		current.name = "PopSpireWomenSelectLoads"
		current.process_mode = Node.PROCESS_MODE_ALWAYS
		_instance = weakref(current)
		# A background may be entering while the root is adding children.
		tree.root.add_child.call_deferred(current)
	return current

func request(path: String, client: Node, generation: int) -> void:
	if not _pending.has(path):
		var error := ResourceLoader.load_threaded_request(path, "VideoStream", false, ResourceLoader.CACHE_MODE_IGNORE)
		if error != OK:
			client.video_loaded(generation, null)
			return
		_pending[path] = []
	_pending[path].append([weakref(client), generation])

func cancel(client: Node) -> void:
	for path in _pending:
		_pending[path] = _pending[path].filter(func(item: Array) -> bool: return item[0].get_ref() != client)
	# Even with no clients, retain the job until load_threaded_get releases it.

func pending_count() -> int:
	return _pending.size()

func _process(_delta: float) -> void:
	for path in _pending.keys():
		var status := ResourceLoader.load_threaded_get_status(path)
		if status == ResourceLoader.THREAD_LOAD_IN_PROGRESS:
			continue
		var resource: Resource = null
		if status != ResourceLoader.THREAD_LOAD_INVALID_RESOURCE:
			resource = ResourceLoader.load_threaded_get(path)
		var clients: Array = _pending[path]
		_pending.erase(path)
		for item in clients:
			var client: Node = item[0].get_ref()
			if is_instance_valid(client) and client.is_inside_tree() and not client.is_queued_for_deletion():
				client.video_loaded(item[1], resource)

func _exit_tree() -> void:
	# Only application/tree shutdown can wait for the engine's outstanding I/O.
	# No scene or game action awaits a movie, signal, task, or this drain.
	for path in _pending:
		ResourceLoader.load_threaded_get(path)
	_pending.clear()
