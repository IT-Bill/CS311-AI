import numpy as np
from game import *

board = np.array([
    [ 0,  1, -1,  0, -1, -1, -1,  0],
    [ 0,  0,  0,  0,  0, -1,  1, -1],
    [ 0,  0,  0,  0,  0, -1, -1, -1],
    [ 0,  0,  0,  0,  0,  0,  0, -1],
    [ 0,  0,  0,  0,  0,  0,  0, -1],
    [ 0,  0,  0,  0,  0,  0,  0, -1],
    [ 0,  0,  0,  0,  0,  0,  0,  1],
    [ 0,  0,  0,  0,  0,  0,  0,  0]
])

# print(select_move_easy(board, 1, 2))
b, w = get_bin_board(board)
w, b = apply_move(w, b, 7)
board = get_np_board(b, w)
print(board)

b, w = get_bin_board(board)
b, w = apply_move(b, w, 0)
board = get_np_board(b, w)
print(board)