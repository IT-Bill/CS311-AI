import random, time
import numpy as np
from game import BLACK, WHITE, BOARD_SIZE

COLS = 'ABCDEFGH'

STONE_TO_CHAR = {
    0: ' . ',
    BLACK: ' x ',
    WHITE: ' o ',
}

INIT_GRID = np.array([[0,  0,  0,  0,  0,  0,  0,  0],
                      [0,  0,  0,  0,  0,  0,  0,  0],
                      [0,  0,  0,  0,  0,  0,  0,  0],
                      [0,  0,  0,  1, -1,  0,  0,  0],
                      [0,  0,  0, -1,  1,  0,  0,  0],
                      [0,  0,  0,  0,  0,  0,  0,  0],
                      [0,  0,  0,  0,  0,  0,  0,  0],
                      [0,  0,  0,  0,  0,  0,  0,  0]])

def point_to_coord(point):
    """将纯数字坐标转化为字母数字坐标"""
    return "%s%d" % (COLS[point[0]], point[1])

def coord_to_point(coord):
    col = COLS.index(coord[0])
    row = int(coord[1:])
    return row, col

def print_move(player, move):
    print("%s(%s) %s" % (player, STONE_TO_CHAR[player], point_to_coord(move)))


def print_board(board):
    for row in range(BOARD_SIZE):
        line = []
        for col in range(BOARD_SIZE):
            stone = board[row, col]
            line.append(STONE_TO_CHAR[stone])
        print("%2s %s" % (COLS[row], ''.join(line)))
    
    print("    " + "  ".join(str(e) for e in range(len(COLS))))



def cost_time(func):
    def fun(*args, **kwargs):
        t = time.perf_counter()
        result = func(*args, **kwargs)
        print(f'func {func.__name__} cost time:{time.perf_counter() - t:.8f} s')
        return result

    return fun