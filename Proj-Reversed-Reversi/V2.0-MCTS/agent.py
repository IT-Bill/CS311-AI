from gotypes import Point
from game import Move
import numpy as np

class Agent:
    """围棋机器人统一接口"""
    def __init__(self):
        pass

    def select_move(self, game_state):
        raise NotImplementedError
    

class RandomAgent(Agent):
    def __init__(self):
        super().__init__()
        self.cache = []
        self.board_size = None

    def set_cache(self, board_size):
        self.board_size = board_size

        for r in range(board_size):
            for c in range(board_size):
                self.cache.append(Point(r, c))

    def select_move(self, game_state):
        if self.board_size is None:
            self.set_cache(game_state.board.board_size)

        # print(game_state.next_player)
        idx = np.arange(len(self.cache))
        np.random.shuffle(idx)
        for i in idx:
            p = self.cache[i]
            # print(i, p)
            if game_state.is_valid_move(Move.play(p)):
                return Move.play(p)
            
        return Move.pass_turn()

