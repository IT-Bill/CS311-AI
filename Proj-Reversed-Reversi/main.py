import numpy as np
import random
import time

COLOR_BLACK = -1
COLOR_WHITH = 1
COLOR_NONE = 0
INT_MIN = -10e5
INT_MAX = 10e5
random.seed(0)

WEIGHT_MAP = -np.array([[500, -25, 10, 5, 5, 10, -25, 500],
                        [-25, -45, 1, 1, 1, 1, -45, -25],
                        [10, 1, 3, 2, 2, 3, 1, 10],
                        [5, 1, 2, 1, 1, 2, 1, 5],
                        [5, 1, 2, 1, 1, 2, 1, 5],
                        [10, 1, 3, 2, 2, 3, 1, 10],
                        [-25, -45, 1, 1, 1, 1, -45, -25],
                        [500, -25, 10, 5, 5, 10, -25, 500]])


class AI(object):
    def __init__(self, chessboard_size, color, time_out):
        self.chessboard_size = chessboard_size
        self.color = color
        self.time_out = time_out
        self.candidate_list = []

    def go(self, chessboard):
        self.candidate_list.clear()
        legal_pos, best_step = alpha_bate(chessboard, self.color, 1)
        if len(legal_pos) != 0:  # 有合法的位置
            self.candidate_list += legal_pos
            self.candidate_list.append((best_step))


my_color = op_color = 0


def alpha_bate(board, color, depth):
    my_color = color
    op_color = -color

    controller = BoardController(board, my_color)
    legal_pos = controller.get_all_legal_pos()
    if len(legal_pos) == 0:
        return [], None

    best_val = INT_MIN
    for pos in legal_pos:
        new_board = BoardController(controller.board, my_color)
        new_board.board_after_rev(*pos)  # 我方走棋

        temp = min_node(new_board.board, depth - 1, INT_MIN, INT_MAX)

        if temp > best_val:
            best_val = temp
            best_step = pos

    return legal_pos, best_step


def min_node(board, depth, alpha, beta):
    if depth <= 0:
        return evaluate(board)


def evaluate(board):
    return WEIGHT_MAP[board == my_color].sum() - WEIGHT_MAP[board == op_color].sum()


class BoardController:
    def __init__(self, board, cur_color):
        self.board = np.copy(board)
        self.cur_color = cur_color
        self.legal_pos = []
        self.rev_pos = []
        self.dir = ((-1, 0), (-1, 1), (0, 1), (1, 1),
                    (1, 0), (1, -1), (0, -1), (-1, -1))

    def on_board(self, x, y):
        return 0 <= x <= 7 and 0 <= y <= 7

    def is_legal_pos(self, cheak_only, i, j):
        self.rev_pos.clear()

        if self.on_board(i, j) and self.board[i, j] == 0:
            for dx, dy in self.dir:
                op_cnt = 1
                x, y = i + dx, j + dy
                while self.on_board(x, y): 
                    if self.board[x, y] == -self.cur_color:
                        op_cnt += 1 
                        x += dx
                        y += dy
                    elif self.board[x, y] == self.cur_color and op_cnt > 1:
                        if cheak_only:
                            return True
                        while op_cnt > 0:
                            x -= dx
                            y -= dy
                            self.rev_pos.append((x, y))
                            op_cnt -= 1
                    else:
                        break
        return len(self.rev_pos) > 0

    def get_all_legal_pos(self):
        self.legal_pos.clear()
        for i in range(8):
            for j in range(8):
                if self.is_legal_pos(True, i, j):
                    self.legal_pos.append((i, j))
        return self.legal_pos

    def board_after_rev(self, x, y):
        if (self.is_legal_pos(False, x, y)):
            for pos in self.rev_pos:
                self.board[x, y] = self.cur_color

    