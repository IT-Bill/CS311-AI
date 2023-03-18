from dlgo import gotypes, goboard


COLS = "ABCDEFGHJKLMNOPQRST"
STONE_TO_CHAR = {
    None: ' . ',
    gotypes.Player.black: ' x ',
    gotypes.Player.white: ' o ',
}

def print_move(player, move):
    if move.is_pass:
        move_str = "passes"
    elif move.is_resign:
        move_str = "resigns"
    else:
        move_str = '%s%d' % (COLS[move.point.col - 1], move.point.row)

    print("%s %s" % (player, move_str))


def print_board(board: goboard.Board):
    for row in range(board.num_rows, 0, -1):
        bump = " " if row <= 9 else ""
        line = []
        for col in range(1, board.num_cols + 1):
            stone = board.get(gotypes.Point(row, col))
            line.append(STONE_TO_CHAR[stone])
        print("%2d %s" % (row, ''.join(line)))
    
    print("    " + "  ".join(COLS[:board.num_cols]))

def point_from_coords(coords):
    """将人工输入转化为围棋坐标"""
    col = COLS.index(coords[0]) + 1
    row = int(coords[1:])
    return gotypes.Point(row, col)