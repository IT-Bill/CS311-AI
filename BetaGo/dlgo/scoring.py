import numpy as np
from dlgo.gotypes import Player, Point
from dlgo.agent.helpers import is_point_an_eye

class compute_game_result():
    def __init__(self, game_state):
        self.winner = None
        self.board = game_state.board
        self.matrix = np.zeros((game_state.board.num_rows, game_state.board.num_cols))
        self._grid = game_state.board._grid
        self.black = 0
        self.white = 0
        for m in self._grid.keys():
            if self._grid[m] is not None:
                if self._grid[m].color == Player.black:
                    self.matrix[m.row - 1, m.col - 1] = 1
                elif self._grid[m].color == Player.white:
                    self.matrix[m.row - 1, m.col - 1] = 2
        for i in range(0, game_state.board.num_rows):
            for j in range(0, game_state.board.num_cols):
                if self.matrix[i, j] == 1:
                    self.black += 1
                elif self.matrix[i, j] == 2:
                    self.white += 1
                else:
                    if (is_point_an_eye(self.board, Point(i + 1, j + 1), Player.black)):
                        self.black += 1
                    else:
                        self.white += 1
        # print(self.black)
        # print(self.white)
        # self.white += 7.5
        if (self.black > self.white):
            self.winner = Player.black
        elif (self.black < self.white):
            self.winner = Player.white

