from gotypes import Player, Point
import random
import numpy as np

COLS = 'ABCDEFGH'

STONE_TO_CHAR = {
    None: ' . ',
    Player.black: ' ● ',
    Player.white: ' o ',
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
    return "%s%d" % (COLS[point.row], point.col)

def coord_to_point(coord):
    col = COLS.index(coord[0])
    row = int(coord[1:])
    return Point(row, col)

def print_move(player, move):
    print("%s %s" % (player, move))


def print_board(board):
    for row in range(board.board_size):
        line = []
        for col in range(board.board_size):
            stone = board.grid[(row, col)]
            if stone == 0:
                line.append(STONE_TO_CHAR[None])
            else:
                line.append(STONE_TO_CHAR[Player(stone)])
        print("%2s %s" % (COLS[row], ''.join(line)))
    
    print("    " + "  ".join(str(e) for e in range(len(COLS))))


def get_zobrist():
    def to_python(player_state):
        if player_state is None:
            return 'None'
        return player_state

    MAX63 = 0x7fff_ffff_ffff_ffff
    table = {}
    empty_board = 0
    for row in range(8):
        for col in range(8):
            for state in (Player.black, Player.white):
                code = random.randint(0, MAX63)
                table[Point(row, col), state] = code

    print('from gotypes import Player, Point')
    print('')
    print('__all__ = ["HASH_CODE", "INIT_BOARD"]')
    print()
    print('HASH_CODE = {')
    for (pt, state), hash_code in table.items():
        print('    (%r, %s): %r,' % (pt, to_python(state), hash_code))
    print('}')
    print()
    print('INIT_BOARD = %d' % (empty_board, ))
