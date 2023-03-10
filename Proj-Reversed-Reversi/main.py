import numpy as np
import random
import time

COLOR_BLACK = -1
COLOR_WHITH = 1
COLOR_NONE = 0
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
        board = BoardController(chessboard, self.color)
        board.get_all_legal_pos()
        self.candidate_list += board.legal_pos
        self.candidate_list += greedy(board)



def greedy(board_controller):
    # board_controller.get_all_legal_pos()
    min_flip = 64
    for pos in board_controller.legal_pos:
        board_controller.is_legal_pos(False, pos[0], pos[1])
        if len(board_controller.rev_pos) < min_flip:
            min_pos = pos

    return min_pos


class BoardController(object):
    def __init__(self, board, cur_color):
        # numpy array
        self.board = board
        # 当前执棋色
        self.cur_color = cur_color
        self.legal_pos = []
        self.rev_pos = []
        self.dir = ((-1, 0), (-1, 1), (0, 1), (1, 1),
                    (1, 0), (1, -1), (0, -1), (-1, -1))

    def on_board(x, y):
        """判断某位置是否在棋盘上"""
        return 0 <= x <= 7 and 0 <= y <= 7

    def is_legal_place(self, cheak_only, i, j):
        self.rev_pos.clear()

        # 当前位置为空，且在棋盘上,可能是落子点，可以搜索
        if self.on_board(i, j) and self.board[i, j] == 0:
            for dx, dy in self.dir:
                op_cnt = 1
                x, y = i + dx, j + dy

                while self.on_board(x, y):  # 在棋盘上
                    if self.board[x, y] == -self.cur_color:
                        # 且为对方棋子，可以继续前进
                        op_cnt += 1  # 记录要翻转的棋子个数
                        x += dx
                        y += dy
                    elif self.board[x, y] == self.cur_color and op_cnt > 1:
                        # 己方棋子，而且至少遇到一个对方棋子

                        if cheak_only:
                            return True

                        while op_cnt > 0:
                            x -= dx
                            y -= dy
                            self.rev_pos.append((x, y))
                            op_cnt -= 1

                    else:
                        # 是NONE，向下一个方向搜索
                        break

                # 前进之后，不在棋盘上，继续搜索下一个方向

        return len(self.rev_pos) > 0

    def get_all_legal_pos(self):
        has_legal_pos = False
        self.legal_pos.clear()

        for i in range(8):
            for j in range(8):
                if self.is_legal_place(True, i, j):
                    self.legal_pos.append((i, j))
                    has_legal_pos = True

        return has_legal_pos
