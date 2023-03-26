from game import GameState, BLACK, WHITE
from random import randint, choice
from math import sqrt, log, inf
from numpy.random import shuffle
from numpy import argwhere

from time import perf_counter


ratio = [0.4877705155428074,
         0.5143542577150955,
         0.520639688918028,
         0.5401054416452242,
         0.547504989839517,
         0.5767900128084937,
         0.5794970493896976,
         0.5983126636715594,
         0.6217454247742333,
         0.6321946786762482,
         0.6611604506795605,
         0.6664941221883359,
         0.6808657794246635,
         0.7035956766172825,
         0.7281276137453017,
         0.7650647385327211,
         0.7628725066532253,
         0.8148406510887584,
         0.8065575303043343,
         0.8631343688844811,
         0.8783857916563264,
         0.9248221335831562,
         0.9496744747797716,
         1.0013714830407132,
         1.0463317652307942,
         1.0916644488530234,
         1.1316255524734085,
         1.1823553536019284,
         1.2324197825845264,
         1.278971264519784,
         1.3407759076413728,
         1.3833527967854677,
         1.3514685748983872,
         1.5749842107832883,
         1.5936755836892387,
         1.7052485090377838,
         1.8195469785026082,
         1.9343045401456562,
         2.0524104486783945,
         2.2052330385142143,
         2.3260461013682145,
         2.505559574486062,
         2.6518109340208404,
         2.859548297770733,
         3.024310037073069,
         3.2267480907781447,
         3.59561776141526,
         3.998053412877828,
         4.281299710992333,
         5.354358946262075,
         5.859853827990377,
         7.092280465055747,
         8.518866317195043,
         12.026037770149381,
         21.15838725851597,
         48.285093156553,
         64.19117625106773,
         88.6217869449699,
         94.47829306288936,
         106.82088621584255]


def random_select_move(game_state):

    start = perf_counter()

    empty = argwhere(game_state.board == 0)
    shuffle(empty)
    for m in empty:
        if game_state.is_valid_move(m):
            return m

    end = perf_counter()
    # print(end - start)

    return (-1, -1)


def alphabeta_select_move(game_state):
    # ! 注意
    next_player = game_state.next_player

    def max_value(game, alpha, beta):
        if game.is_over():
            
            return next_player * game.winner, None
        
        v, move = -inf, None
        for m in game.legal_moves():
            v2, _ = min_value(game.apply_move(m), alpha, beta)

            if v2 > v:
                v, move = v2, m
            if v >= beta:
                break
            alpha = max(alpha, v)

        return v, move
    
    def min_value(game, alpha, beta):
        if game.is_over():
            return next_player * game.winner, None
        
        v, move = +inf, None
        for m in game.legal_moves():
            v2, _ = max_value(game.apply_move(m), alpha, beta)

            if v2 < v:
                v, move = v2, m
            if v <= alpha:
                break
            alpha = min(alpha, v)

        return v, move

    return max_value(game_state, -inf, +inf)[1]


class MCTSNode:
    def __init__(self, game_state, parent=None, prev_move=None):
        self.game_state: GameState = game_state
        self.parent = parent  # 父节点
        self.prev_move = prev_move  # 触发当前棋局的上一步操作

        # 从当前节点开始的所有推演的统计信息
        self.win_counts = {
            BLACK: 0,
            WHITE: 0
        }
        self.num_rollouts = 0

        self.children = []
        self.unvisited_moves = self.game_state.legal_moves()

    def add_random_child(self):
        index = randint(0, len(self.unvisited_moves) - 1)
        new_move = self.unvisited_moves.pop(index)
        new_game_state = self.game_state.apply_move(new_move)
        new_node = MCTSNode(new_game_state, self, new_move)
        self.children.append(new_node)
        return new_node

    def record_win(self, winner):
        self.num_rollouts += 1
        if winner != 0:
            self.win_counts[winner] += 1

    def can_add_child(self):
        return len(self.unvisited_moves) > 0

    def winning_frac(self, player):
        return float(self.win_counts[player]) / float(self.num_rollouts)


class MCTSAgent:
    def __init__(self, auto_set_param=True, use_dfs=False, num_rounds=400, temperature=5, ):
        self.num_rounds = num_rounds
        self.temperature = temperature
        self.auto_set_param = auto_set_param
        self.use_dfs = use_dfs

    def select_move(self, game_state):
        # ! 最后8步DFS、AlphaBeta
        if self.use_dfs and game_state.num_empty < 10:
            print("use_dfs")
            return alphabeta_select_move(game_state)

        root = MCTSNode(game_state)
        if self.auto_set_param:
            self.set_param(root)

        for _ in range(self.num_rounds):
            node = root

            # 一直找到有孩子的node
            while (not node.can_add_child()) and (not node.game_state.is_over()):
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

        # TODO ! 简化
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
        if empty > 7:
            self.num_rounds = int(ratio[60 - empty] * 1000)

        # if empty < 10:
        #     r = 200
        # elif empty < 20:
        #     r = 120
        #     t = 7
        # elif empty < 35:
        #     r = 80
        #     t = 5
        # elif empty < 50:
        #     r = 60
        #     t = 4
        # else:
        #     r = 60
        #     t = 3

        # self.num_rounds = len(node.unvisited_moves) * r
        # self.temperature = t

    @staticmethod
    def simulate_random_game(game_state: GameState):
        bots = {
            BLACK: random_select_move,
            WHITE: random_select_move
        }
        while not game_state.is_over():
            move = bots[game_state.next_player](game_state)
            game_state = game_state.apply_move(move)
        return game_state.get_winner()

    def uct_score(self, parent_rollouts, child_rollouts, win_pct):

        exporation = sqrt(log(parent_rollouts) / child_rollouts)
        return win_pct + self.temperature * exporation
