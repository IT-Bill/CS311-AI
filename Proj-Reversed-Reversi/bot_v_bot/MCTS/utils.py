import random, time
import numpy as np
from MCTS.game import BLACK, WHITE, BOARD_SIZE

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


# def print_board(board):
#     for row in range(BOARD_SIZE):
#         line = []
#         for col in range(BOARD_SIZE):
#             stone = board[row, col]
#             line.append(STONE_TO_CHAR[stone])
#         print("%2s %s" % (row, ''.join(line)))
    
#     print("    " + "  ".join(str(e) for e in range(BOARD_SIZE)))

def print_board(board):
    for row in range(BOARD_SIZE):
        print("%2s %s" % (row, ''.join([STONE_TO_CHAR[board[row, col]] for col in range(BOARD_SIZE)])))
    print("    " + "  ".join(str(e) for e in range(BOARD_SIZE)))

def cost_time(func):
    def fun(*args, **kwargs):
        t = time.perf_counter()
        result = func(*args, **kwargs)
        print(f'func {func.__name__} cost time:{time.perf_counter() - t:.8f} s')
        return result

    return fun