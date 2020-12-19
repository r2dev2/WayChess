from typing import Iterable

import pygame as pg

from . import baselib as bs


class CoordinateManager(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scale_factor = 1

    def __getitem__(self, item):
        return self.scale(super().__getitem__(item))

    def scale(self, item):
        if isinstance(item, Iterable):
            iter(item)
            return item.__class__([self.scale(i) for i in item])
        elif isinstance(item, pg.Surface):
            size = item.get_size()
            return pg.transform.smoothscale(item, self.scale(size))
        else:
            return item * self.scale_factor


class GUI:
    pass


bs.GUI.coords = CoordinateManager({"arrow thickness": 20, "square size": 68,})
