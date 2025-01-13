from collections import OrderedDict


class TypeBase:
    _cls_suffix = None
    _typed = None

    @classmethod
    def get_typed(cls):
        if cls._typed:
            return cls._typed
        return cls.__name__[:-len(cls._cls_suffix)]

    @classmethod
    def on_registered(cls, types):
        pass


class TypesBase:
    def __init__(self):
        self._maps = OrderedDict()

    def __getitem__(self, item):
        return self._maps[item]

    def keys(self):
        return self._maps.keys()

    def items(self):
        return self._maps.items()

    def get(self, typed):
        return self._maps.get(typed)

    def register(self, cls):
        self._maps[cls.get_typed()] = cls
        cls.on_registered(self)
        return cls


def split_function(body, a='$', p='$$'):
    if body is None:
        body = {}
    body = body.copy()
    args = body.pop(a, None) or []
    params = body.pop(p, None) or {}
    return args, params, body
