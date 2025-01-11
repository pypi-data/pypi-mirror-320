# from starbear.live import component


from contextvars import ContextVar
from itertools import count

paths = ContextVar("paths", default=None)
_id = count()


class Context:
    def __init__(self, path):
        self.path = path
        self.omap = {}

    def associate(self, opq, value):
        self.omap[opq] = value


class Opaque:
    def __init__(self):
        self._id = next(_id)

    def __str__(self):
        return f"<Opaque #{self._id}>"

    __repr__ = __str__


class Proxy:
    def __init__(self, path, obj):
        self._path = path
        self._obj = obj

    def __getattribute__(self, attr):
        spath = object.__getattribute__(self, "_path")
        sobj = object.__getattribute__(self, "_obj")
        pth = (*spath, ("attr", attr))
        print("ACCESS", pth)
        result = getattr(sobj, attr)
        return Proxy(pth, result)

    def __getitem__(self, item):
        spath = object.__getattribute__(self, "_path")
        sobj = object.__getattribute__(self, "_obj")
        pth = (*spath, ("item", item))
        print("ACCESS", pth)
        result = sobj[item]
        return Proxy(pth, result)

    def __iter__(self):
        spath = object.__getattribute__(self, "_path")
        sobj = object.__getattribute__(self, "_obj")
        for x in iter(sobj):
            yield Proxy(spath, x)

    def __str__(self):
        sobj = object.__getattribute__(self, "_obj")
        return str(sobj)

    def __repr__(self):
        sobj = object.__getattribute__(self, "_obj")
        return repr(sobj)


p = Proxy((), [[0, 1], 2, 3])
for x in p:
    print(x)


# def component(fn):
#     def wrapped(state):
#         result = fn(state)
#         opq = Opaque()
#         context.associate(opq, result)
#         return opq

#     return fn


# @component
# def row(state):
#     return f"Hello, {state['name']}"


# @component
# def greetings(state):
#     return [row(x) for x in state]
