from dlgo.gotypes import Player, Point 

COLS = "ABCDEFGHJKLMNOPQRST"
STONE_TO_CHAR = {
    None: ' . ',
    Player.black: ' x ',
    Player.white: ' o ',
}

def print_move(player, move):
    print("%s %s" % (player, move))


def print_board(board):
    for row in range(board.num_rows, 0, -1):
        bump = " " if row <= 9 else ""
        line = []
        for col in range(1, board.num_cols + 1):
            stone = board.get(Point(row, col))
            line.append(STONE_TO_CHAR[stone])
        print("%2d %s" % (row, ''.join(line)))
    
    print("    " + "  ".join(COLS[:board.num_cols]))

def point_from_coords(coords):
    """将人工输入转化为围棋坐标"""
    col = COLS.index(coords[0]) + 1
    row = int(coords[1:])
    return Point(row, col)