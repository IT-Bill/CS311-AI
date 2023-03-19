from enum import Enum
from collections import namedtuple


__all__ = ["Player", "Point"]


class Player(Enum):
    black = -1
    white = 1

    @property
    def opposite(self):
        return Player.black if self == Player.white else Player.white


class Point(namedtuple("Point", "row col")):
    @property
    def neighbors(self):
        return [
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1),
            Point(self.row, self.col + 1),
            Point(self.row - 1, self.col - 1),
            Point(self.row - 1, self.col + 1),
            Point(self.row + 1, self.col - 1),
            Point(self.row + 1, self.col + 1),
        ]

    @staticmethod
    def dirs():
        return ((-1, 0), (-1, 1), (0, 1), (1, 1),
                (1, 0), (1, -1), (0, -1), (-1, -1))
    
    def __str__(self):
        from utils import point_to_coord
        return point_to_coord(self)
