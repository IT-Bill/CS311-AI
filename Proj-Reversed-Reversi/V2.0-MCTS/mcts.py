from typing import List
from gotypes import Player
from game import GameState, Move
import random, math
from agent import Agent, RandomAgent

__all__ = ["MCTSAgent"]

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
        self.num_rollouts += 1
        if winner is not None:
            self.win_counts[winner] += 1

    def can_add_child(self):
        return len(self.unvisited_moves) > 0

    def is_terminal(self):
        return self.game_state.is_over()

    def winning_frac(self, player):
        return float(self.win_counts[player]) / float(self.num_rollouts)
    

class MCTSAgent(Agent):
    def __init__(self, auto_set_param=True, num_rounds=400, temperature=5):
        self.num_rounds = num_rounds
        self.temperature = temperature
        self.auto_set_param = auto_set_param

    def select_move(self, game_state):
        root = MCTSNode(game_state)
        if self.auto_set_param:
            self.set_param(root)

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

        scored_moves = [
            (child.winning_frac(game_state.next_player), 
             child.prev_move, child.num_rollouts)
            for child in root.children
        ]
        scored_moves.sort(key=lambda x: x[0], reverse=True)
        for s, m, n in scored_moves[:]:
            print('%s - %.3f (%d)' % (m, s, n))


        # 完成所有推演后，选择下一步动作
        best_move = None
        best_pct = -1.0

        for child in root.children:
            child_pct = child.winning_frac(game_state.next_player)
            # print(child.prev_move, "胜率", child_pct)
            if child_pct > best_pct:
                best_pct = child_pct
                best_move = child.prev_move
        print('Select move %s with win pct %.3f' % (best_move, best_pct))

        print("Rounds: ", self.num_rounds)
        print("Temperature: ", self.temperature)

        return best_move
    
    def select_child(self, node: MCTSNode):
        best_score = -1
        best_child = None
        for child in node.children:
            score = self.uct_score(
                node.num_rollouts, 
                child.num_rollouts, 
                child.winning_frac(node.game_state.next_player))
            if score > best_score:
                best_score = score
                best_child = child
        return best_child
    
    def set_param(self, node: MCTSNode):
        """设置参数"""
        empty = node.game_state.num_empty
        
        if empty < 10:
            r = 200
        elif empty < 20:
            r = 120
            t = 7
        elif empty < 35:
            r = 80
            t = 5
        elif empty < 50:
            r = 60
            t = 4
        else:
            r = 60
            t = 3

        self.num_rounds = len(node.unvisited_moves) * r
        # self.temperature = t

    
    @staticmethod
    def simulate_random_game(game_state: GameState):
        bots = {
            Player.black: RandomAgent(),
            Player.white: RandomAgent()
        }
        while not game_state.is_over():
            move = bots[game_state.next_player].select_move(game_state)
            game_state = game_state.apply_move(move)
        return game_state.winner()

    def uct_score(self, parent_rollouts, child_rollouts, win_pct):
        exporation = math.sqrt(math.log(parent_rollouts) / child_rollouts)
        return win_pct + self.temperature * exporation