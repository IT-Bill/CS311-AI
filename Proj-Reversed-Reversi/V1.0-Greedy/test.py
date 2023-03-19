from main import *
import numpy as np

board = np.zeros((8, 8))
board[3, 4] = board[4, 3] = COLOR_BLACK
board[3, 3] = board[4, 4] = COLOR_WHITH

ai = AI(8, COLOR_BLACK, 5)
ai.go(board)

print(ai.candidate_list)