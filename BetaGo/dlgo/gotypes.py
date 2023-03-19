import enum
from collections import namedtuple

__all__ = ["Player", "Point"]

class Player(enum.Enum):
    """棋子颜色类"""
    black = 1
    white = 2

    @property
    def other(self):
        """切换棋手"""
        return Player.black if self == Player.white else Player.white


class Point(namedtuple("Point", "row col")):
    """命名元组，可以使用Point.row而不是Point[0]"""

    @property
    def neighbors(self):
        return [
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1),
            Point(self.row, self.col + 1),
        ]
    
    @property
    def corners(self):
        return [
            Point(self.row - 1, self.col - 1),
            Point(self.row - 1, self.col + 1),
            Point(self.row + 1, self.col - 1),
            Point(self.row + 1, self.col + 1),
        ]
    