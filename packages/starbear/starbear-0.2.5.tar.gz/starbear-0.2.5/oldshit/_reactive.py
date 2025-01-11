from contextvars import ContextVar

current_block = ContextVar(name="reactive_block", default=None)


class State(dict):
    def __getitem__(self, item):
        return super().__getitem__(item)

    def __setitem__(self, item, value):
        super().__setitem__(item, value)


class Opaque:
    def __init__(self, obj):
        self._object = obj


class Reactive:
    def __init__(self, fn):
        self.fn = fn

    def __call__(self, *args, **kwargs):
        try:
            token = current_block.set(self)
            result = self.fn(*args, **kwargs)
            return Opaque(result)
        finally:
            current_block.reset(token)


# class ReactiveBlock:
#     def __init__(self, state):
#         self.state = state
#         self.touched = defaultdict(set)


reactive = Reactive
