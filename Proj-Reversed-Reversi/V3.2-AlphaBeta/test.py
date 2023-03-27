from game import Game
import numpy as np

INIT_BOARD = np.array([[0,  0,  0,  0,  0,  0,  0,  0],
                      [0,  0,  0,  0,  0,  0,  0,  0],
                      [0,  0,  0,  0,  0,  0,  0,  0],
                      [0,  0,  0,  -1, 1,  0,  0,  0],
                      [0,  0,  0, 1,  -1,  0,  0,  0],
                      [0,  0,  0,  0,  0,  0,  0,  0],
                      [0,  0,  0,  0,  0,  0,  0,  0],
                      [0,  0,  0,  0,  0,  0,  0,  0]])

game = Game(INIT_BOARD)

moves = game.get_legal_moves(-1)
game.print_2d_board(moves)
m1 = list("{:064b}".format(moves))
print("--------------------")
black_board, white_board = game.apply_move(-1, 20)
game.print_2d_board(black_board)
print()
game.print_2d_board(white_board)