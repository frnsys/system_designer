import asyncio
import inspect


def isexposedmethod(a):
    return inspect.ismethod(a) \
        and not a.__name__.startswith('_') \
        and hasattr(a, '__rpc__') \
        and a.__rpc__


class LocalProxy():
    """this emulates a proxy for a remote agent
    so that local agent's methods are accessed
    the same way"""
    def __init__(self, obj):
        self.obj = obj
        self.addr = obj.addr
        self._cache = {}
        for name, m in inspect.getmembers(self.obj,
                                         predicate=isexposedmethod):
            self._cache[name] = asyncio.coroutine(m)

    def __getattr__(self, method):
        try:
            return self._cache[method]
        except KeyError:
            raise LookupError(
                '{} not defined or exposed for {}'.format(
                    method, self.obj.__class__))

    def __repr__(self):
        return '<LocalProxy({}.{}:{})>'.format(
            self.obj.__module__,
            self.obj.__class__.__name__,
            hex(id(self.obj)))
