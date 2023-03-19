import numpy as np
import random
import time
from board_controller import BoardController
from greedy import greedy

COLOR_BLACK = -1
COLOR_WHITH = 1
COLOR_NONE = 0
random.seed(0)


class AI(object):
    def __init__(self, chessboard_size, color, time_out):
        self.chessboard_size = chessboard_size
        self.color = color
        self.time_out = time_out
        self.candidate_list = []

    def go(self, chessboard):
        self.candidate_list.clear()
        board_controller = BoardController(chessboard, self.color)
        self.candidate_list += board_controller.get_all_legal_pos()
        if len(self.candidate_list) != 0: # 有合法的位置
            self.candidate_list.append(greedy(board_controller))
