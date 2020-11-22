from typing import Iterable

from . import baselib as bs

class CoordinateManager(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scale_factor = 1
    
    def __getitem__(self, item):
        return self.__scale(super().__getitem__(item))

    def __scale(self, item):
        if isinstance(item, Iterable):
            iter(item)
            return item.__class__([self.__scale(i) for i in item])
        return item * self.scale_factor


class GUI:
    pass


bs.GUI.coords = CoordinateManager({
    "arrow thickness": 20,
    "square size": 68,
})
