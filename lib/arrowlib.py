import math
import re
import sys

import pygame
import pygame.gfxdraw

from . import baselib as bs


def get_line_points(sx, sy, ex, ey, thickness):
    cos = math.cos
    sin = math.sin
    try:
        (ey - sy) / (ex - sx)
        theta = math.atan2(ey - sy, ex - sx)
        p_theta = math.atan2(ex - sx, sy - ey)
        c = cos(p_theta)
        s = sin(p_theta)
        cr = cos(theta)
        sr = sin(theta)
    except ZeroDivisionError:
        c = 1 if sx > ex else -1
        s = 0
        sr = -1 if sy > ey else 1
        cr = 0

    thickness /= 2
    dx = thickness * c
    dy = thickness * s
    drx = thickness * cr
    dry = thickness * sr
    oex = ex
    oey = ey
    ex -= thickness * cr * 2
    ey -= thickness * sr * 2
    res = (
        (
            (int(sx + dx), int(sy + dy)),
            (int(sx - dx), int(sy - dy)),
            (int(ex - dx), int(ey - dy)),  # (int(ex-dx*2), int(ey+dy*2)),
            # (int(ex+dx*2), int(ey+dy*2)),
            (int(oex + drx * 0), int(oey + dry * 0)),
            (int(ex + dx), int(ey + dy)),
        ),
        c,
        s,
    )
    return res


def arrow(screen, lcolor, tricolor, start, end, trirad, thickness=2):
    """
    Draws an antialiased arrow
    """
    points, c, s = get_line_points(*start, *end, thickness)

    pygame.gfxdraw.filled_polygon(screen, points, lcolor)
    pygame.gfxdraw.aapolygon(screen, points, lcolor)


class Arrow:
    def __init__(self, beg, end, color):
        self.beg = beg
        self.end = end
        self.color = color

    @classmethod
    def one_from_str(cls, string):
        matches = re.findall(r"\([^\(\)]+\)", string[6:-1])
        try:
            return cls(*map(eval, matches))
        except:
            return None

    @classmethod
    def set_from_str(cls, string):
        try:
            arrow_strs = re.findall(
                r"Arrow\([^a-z]+\)\)", re.findall("Arrows: (.+)", string)[-1]
            )
            return {cls.one_from_str(a) for a in arrow_strs}
        except IndexError:
            return set()

    def __hash__(self):
        return hash((self.beg, self.end, self.color))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"Arrow({self.beg}, {self.end}, {self.color})"


class GUI:
    @property
    def is_mac(self):
        try:
            return self._is_mac
        except AttributeError:
            self._is_mac = sys.platform == "darwin"
            return self._is_mac

    @property
    def arrows(self):
        return Arrow.set_from_str(self.node.comment)

    @property
    def move_arrow_color(self):
        if self.board.turn:
            return (0, 0, 0, 100)[: 3 if self.is_mac else 4]
        return (255, 255, 255, 100)[: 3 if self.is_mac else 4]

    @property
    def arrow_color(self):
        if self.key_pressed[306]:
            return (0, 255, 0, 150)[: 3 if self.is_mac else 4]
        return (255, 143, 0, 150)[: 3 if self.is_mac else 4]

    def write_arrows(self, arrows):
        if "Arrows: " not in self.node.comment:
            start = len(self.node.comment)
        else:
            start = self.node.comment.rfind("Arrows: ")
        self.node.comment = (
            self.node.comment[:start] + "Arrows: " + " ".join(map(str, arrows))
        )

    def add_arrow(self, arrow):
        arrows = self.arrows
        assert arrow not in arrows, "Shouldn't be calling add_arrow"
        arrows.add(arrow)
        self.write_arrows(arrows)

    def remove_arrow(self, arrow):
        arrows = self.arrows
        assert arrow in self.arrows, "Shouldn't be calling remove_arrow"
        arrows.remove(arrow)
        self.write_arrows(arrows)

    def draw_raw_arrow(self, start, end, color=None):
        """
        Draw an arrow from start to end

        :param start: the raw coordinates of the beginning of the arrow
        :param end: the raw coordinates of the end of the arrow
        :return: None
        """
        SQ = bs.GUI.coords["square size"]
        at = bs.GUI.coords["arrow thickness"]
        if all(0 <= val <= SQ*8 for val in [*start, *end]):
            if color is None:
                color = self.arrow_color
            arrow(self.screen, color, color, start, end, at, at)

    def draw_arrow(self, start, end):
        """
        Draw a permanent arrow from start to end

        :param start: the processed coordinates of the beginning of the arrow
        :param end: the processed coordinates of the end of the arrow
        :return: None
        """
        assert all(0 <= val <= 7 for val in [*start, *end])
        a = Arrow(start, end, self.arrow_color)
        if a in self.arrows:
            self.stdout(a)
            self.remove_arrow(a)
        else:
            self.add_arrow(a)
        # print(self.arrows[self.move])
        self.set_arrows(True)

    def set_arrows(self, drawing=False):
        """Render all arrows"""
        SQUARE_SIZE = bs.GUI.coords["square size"]
        arrows = self.arrows
        for arrow in arrows:
            start = arrow.beg
            end = arrow.end
            s = tuple(i + SQUARE_SIZE // 2 for i in self.get_coords(*start))
            e = tuple(i + SQUARE_SIZE // 2 for i in self.get_coords(*end))
            self.draw_raw_arrow(s, e, arrow.color)
        if self.move_arrow is not None:
            self.draw_raw_arrow(*self.move_arrow, self.move_arrow_color)
        if not drawing:
            self.update_explorer()
