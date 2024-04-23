import numpy as np
import random, time, math, copy
from enum import Enum
from typing import List
from collections import namedtuple


class AI(object):
    def __init__(self, chessboard_size, color, time_out):
        self.chessboard_size = chessboard_size
        self.color = color
        self.time_out = time_out
        self.candidate_list = []

    def go(self, chessboard):
        self.candidate_list.clear()
        board = Board(grid=chessboard)
        game_state = GameState(board, Player(self.color), None, None)
        for move in game_state.legal_moves():
            if not move.is_pass:
                self.candidate_list.append((move.point.row, move.point.col))

        if len(self.candidate_list) > 0:
            agent = MCTSAgent()
            point = agent.select_move(game_state).point
            self.candidate_list.append((point.row, point.col))



