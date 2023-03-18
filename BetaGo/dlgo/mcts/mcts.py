from dlgo.gotypes import Player
from dlgo.goboard import GameState

class MCTSNode:
    def __init__(self, game_state, parent=None, prev_move=None):
        self.game_state: GameState = game_state
        self.parent = parent  # 父节点
        self.prev_move = prev_move

        # 从当前节点开始的所有推演的统计信息
        self.win_counts = {
            Player.black: 0,
            Player.white: 0
        }
        self.num_rollouts = 0

        self.children = []
        self.unvisited_moves = self.game_state.legal_moves()
