import random, time
import numpy as np
from game import BLACK, WHITE, BOARD_SIZE

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


def print_board(board):
    for row in range(BOARD_SIZE):
        line = []
        for col in range(BOARD_SIZE):
            stone = board[row, col]
            line.append(STONE_TO_CHAR[stone])
        print("%2s %s" % (row, ''.join(line)))
    
    print("    " + "  ".join(str(e) for e in range(BOARD_SIZE)))
