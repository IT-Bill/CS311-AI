from dlgo.gotypes import Player
from dlgo.goboard import GameState
from dlgo.agent.base import Agent
from dlgo.agent.naive import RandomBot
import random
from typing import List
import math


class MCTSNode:
    def __init__(self, game_state, parent=None, prev_move=None):
        self.game_state: GameState = game_state
        self.parent = parent  # 父节点
        self.prev_move = prev_move  # 触发当前棋局的上一步操作

        # 从当前节点开始的所有推演的统计信息
        self.win_counts = {
            Player.black: 0,
            Player.white: 0
        }
        self.num_rollouts = 0

        self.children: List[MCTSNode] = []
        self.unvisited_moves = self.game_state.legal_moves()

    def add_random_child(self):
        index = random.randint(0, len(self.unvisited_moves) - 1)
        new_move = self.unvisited_moves.pop(index)
        new_game_state = self.game_state.apply_move(new_move)
        new_node = MCTSNode(new_game_state, self, new_move)
        self.children.append(new_node)
        return new_node

    def record_win(self, winner):
        self.win_counts[winner] += 1
        self.num_rollouts += 1

    def can_add_child(self):
        return len(self.unvisited_moves) > 0

    def is_terminal(self):
        return self.game_state.is_over()

    def winner_frac(self, player):
        return float(self.win_counts[player]) / float(self.num_rollouts)


class MCTSAgent(Agent):
    def __init__(self, num_rounds=10):
        self.num_rounds = num_rounds

    def select_move(self, game_state: GameState):
        root = MCTSNode(game_state)

        for _ in range(self.num_rounds):
            node = root

            # 一直找到有孩子的node
            while (not node.can_add_child()) and (not node.is_terminal()):
                node = self.select_child(node)

            # 将新的子节点添加到子树中
            if node.can_add_child():
                node = node.add_random_child()

            # 从当前节点开始，模拟一局随机推演
            winner = self.simulate_random_game(node.game_state)

            # 将推演出来的得分沿着树分支向上传递
            while node is not None:
                node.record_win(winner)
                node = node.parent

        # 完成所有推演后，选择下一步动作
        best_move = None
        best_pct = -1.0

        for child in root.children:
            child_pct = child.winner_frac(game_state.next_player)
            if child_pct > best_pct:
                best_pct = child_pct
                best_move = child.prev_move

        return best_move

    def select_child(self, node: MCTSNode):
        best_score = -1
        best_child = None
        for child in node.children:
            score = self.uct_score(
                node.num_rollouts, 
                child.num_rollouts, 
                child.winner_frac(node.game_state.next_player))
            if score > best_score:
                score = best_score
                best_child = child
        return best_child
    
    @staticmethod
    def simulate_random_game(game_state: GameState):
        bots = {
            Player.black: RandomBot(),
            Player.white: RandomBot()
        }
        while not game_state.is_over():
            move = bots[game_state.next_player].select_move(game_state)
            game_state = game_state.apply_move(move)
        return game_state.winner()

    @staticmethod
    def uct_score(parent_rollouts, child_rollouts, win_pct, temperature=1.5):
        exporation = math.sqrt(math.log(parent_rollouts) / child_rollouts)
        return win_pct + temperature * exporation
