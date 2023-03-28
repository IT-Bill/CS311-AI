from game import *
import numpy as np
board = np.array([[0,  0,  0,  0,  0,  0,  0,  0],
                  [0,  0,  0,  0,  0,  0,  0,  0],
                  [0,  0,  0,  1,  0,  0,  0,  0],
                  [0,  0,  0,  1,  1,  0,  0,  0],
                  [0,  0,  0,  1, -1,  0,  0,  0],
                  [0,  0,  0,  0,  0,  0,  0,  0],
                  [0,  0,  0,  0,  0,  0,  0,  0],
                  [0,  0,  0,  0,  0,  0,  0,  0]])

black_board, white_board = get_bin_board(board)


moves = legal_moves(black_board, white_board)
print_2d_board(moves)

print(select_move(black_board, white_board, 8))
