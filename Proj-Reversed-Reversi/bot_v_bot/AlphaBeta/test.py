import numpy as np
from game import *

board = np.array([
    [ 0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0, -1, -1,  0,  0],
    [ 1,  1, -1,  1, -1, -1,  0,  0],
    [ 1,  1,  1, -1,  1, -1,  0,  0],
    [-1, -1, -1, -1, -1, -1,  0,  0],
    [ 0, -1, -1,  0,  0, -1,  1,  0]])

b, w = get_bin_board(board)
print(popcount(b), popcount(w))

print(select_move_easy(board, 1, 7))