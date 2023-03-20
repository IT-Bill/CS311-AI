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

        

class Player(Enum):
    black = -1
    white = 1

    @property
    def opposite(self):
        return Player.black if self == Player.white else Player.white


class Point(namedtuple("Point", "row col")):
    @property
    def neighbors(self):
        return [
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1),
            Point(self.row, self.col + 1),
            Point(self.row - 1, self.col - 1),
            Point(self.row - 1, self.col + 1),
            Point(self.row + 1, self.col - 1),
            Point(self.row + 1, self.col + 1),
        ]

    @staticmethod
    def dirs():
        return ((-1, 0), (-1, 1), (0, 1), (1, 1),
                (1, 0), (1, -1), (0, -1), (-1, -1))
    
    def __str__(self):
        # from utils import point_to_coord
        return point_to_coord(self)

class Move:
    """设置棋手能够采取的一种动作"""
    def __init__(self, point=None, is_pass=False):
        assert(point is not None) ^ is_pass
        self.point = point
        self.is_play = (point is not None)
        self.is_pass = is_pass

    @classmethod
    def play(cls, point):
        """在棋盘上落一颗子"""
        return Move(point=point)
    
    @classmethod
    def pass_turn(cls):
        return Move(is_pass=True)
    
    def __str__(self) -> str:
        if self.is_pass:
            move_str = "pass"
        else:
            move_str = point_to_coord(self.point)
        return move_str


class Board:
    def __init__(self, board_size=8, grid=None):
        self.board_size = board_size
        self.grid = np.copy(grid)   # nparray
        self._hash = 0

    def place_stones(self, player, point, reverse):
        # ! 这里debug了很久，对numpy不熟。。
        p = np.array(reverse + [point])
        self.grid[p[:, 0], p[:, 1]] = player.value

    
    def is_on_grid(self, point):
        return 0 <= point.row < self.board_size and \
            0 <= point.col < self.board_size

    @property
    def zobrist_hash(self):
        return self._hash



class GameState:
    def __init__(self, board, next_player, prev_state, last_move):
        self.board: Board = board
        self.next_player = next_player

        # 应用zobrist_hash
        self.prev_state = prev_state
        if self.prev_state is None:
            self.prev_states = frozenset()
        else:
            self.prev_states = frozenset(
                prev_state.prev_states |
                {(prev_state.next_player, prev_state.board.zobrist_hash)}
            )

        self.last_move = last_move

    def apply_move(self, move):
        """执行落子动作，返回新的GameState对象"""
        if move.is_play:
            next_board = copy.deepcopy(self.board)
            reverse = self.get_reverse(move)
            next_board.place_stones(self.next_player, move.point, reverse)
        else: 
            next_board = self.board
        
        return GameState(next_board, self.next_player.opposite, self, move)
    
    @classmethod
    def new_game(cls, board_size=8):
        board = Board(board_size)
        return GameState(board, Player.black, None, None)
    
    def is_over(self):
        # 计算棋盘上是否还有0即可
        # ! 上面的说法是错误的！！！
        # 有时棋盘上还有空格，但是两方都没法下
        if self.last_move is None:
            return False
        second_last_move = self.prev_state.last_move
        if second_last_move is None:
            return False
        return self.last_move.is_pass and second_last_move.is_pass
        # return (self.board.grid == 0).sum() == 0
    
    
    def is_valid_move(self, move: Move) -> bool:
        if self.is_over():
            return False
        
        if move.is_pass:
            return True
        
        point = move.point
        i, j = point

        # 黑白棋落子合法主逻辑
        # nparray[Point]是正确的
        if self.board.is_on_grid(point) and self.board.grid[point] == 0:
            for dx, dy in Point.dirs():
                op_cnt = 1
                x, y = i + dx, j + dy
                new_point = Point(x, y)

                while self.board.is_on_grid(new_point):
                    # if self.board.grid[new_point] == self.next_player.opposite:
                    if self.board.grid[new_point] == self.next_player.opposite.value:
                        # 且为对方棋子，可以继续前进
                        op_cnt += 1 # 记录要翻转的棋子个数
                        x += dx
                        y += dy
                        new_point = Point(x, y)
                    elif self.board.grid[new_point] == self.next_player.value and op_cnt > 1:
                        # 己方棋子，而且至少遇到一个对方棋子
                        return True

                    else:
                        # 是NONE，向下一个方向搜索
                        break

                # 前进之后，不在棋盘上，继续搜索下一个方向
        
        return False
    
    def get_reverse(self, move: Move):
        reverse = []
        if self.is_over():
            return reverse
        
        if move.is_pass:
            return reverse
        
        point = move.point
        i, j = point

        # 黑白棋落子合法主逻辑
        # nparray[Point]是正确的
        if self.board.is_on_grid(point) and self.board.grid[point] == 0:
            for dx, dy in Point.dirs():
                op_cnt = 1
                x, y = i + dx, j + dy
                new_point = Point(x, y)

                while self.board.is_on_grid(new_point):
                    # if self.board.grid[new_point] == self.next_player.opposite:
                    if self.board.grid[new_point] == self.next_player.opposite.value:
                        # 且为对方棋子，可以继续前进
                        op_cnt += 1 # 记录要翻转的棋子个数
                        x += dx
                        y += dy
                        new_point = Point(x, y)

                    elif self.board.grid[new_point] == self.next_player.value and op_cnt > 1:
                        # 己方棋子，而且至少遇到一个对方棋子

                        while op_cnt > 1:
                            x -= dx
                            y -= dy 
                            new_point = Point(x, y)
                            reverse.append(new_point)
                            op_cnt -= 1
                        break

                    else:
                        # 是NONE，向下一个方向搜索
                        break

                # 前进之后，不在棋盘上，继续搜索下一个方向
        return reverse
    
    def legal_moves(self):
        moves = []
        for row in range(self.board.board_size):
            for col in range(self.board.board_size):
                move = Move.play(Point(row, col))
                if self.is_valid_move(move): # 仅仅做检查，不获取翻转列表
                    moves.append(move)
        if len(moves) == 0:
            # ! 如果没有地方可以下，就pass！！
            moves.append(Move.pass_turn())
            
        return moves

    def winner(self):
        if not self.is_over():
            return None
        num_black = (self.board.grid == Player.black.value).sum()
        num_white = (self.board.grid == Player.white.value).sum()
        if num_black < num_white:
            return Player.black
        elif num_white < num_black:
            return Player.white
        else:
            # ! 平局
            return None

COLS = 'ABCDEFGH'

STONE_TO_CHAR = {
    None: ' . ',
    Player.black: ' x ',
    Player.white: ' o ',
}

INIT_GRID = np.array([[0,  0,  0,  0,  0,  0,  0,  0],
                      [0,  0,  0,  0,  0,  0,  0,  0],
                      [0,  0,  0,  0,  0,  0,  0,  0],
                      [0,  0,  0,  1, -1,  0,  0,  0],
                      [0,  0,  0, -1,  1,  0,  0,  0],
                      [0,  0,  0,  0,  0,  0,  0,  0],
                      [0,  0,  0,  0,  0,  0,  0,  0],
                      [0,  0,  0,  0,  0,  0,  0,  0]])

def point_to_coord(point):
    """将纯数字坐标转化为字母数字坐标"""
    return "%s%d" % (COLS[point.row], point.col)

def coord_to_point(coord):
    col = COLS.index(coord[0])
    row = int(coord[1:])
    return Point(row, col)

def print_move(player, move):
    print("%s(%s) %s" % (player, STONE_TO_CHAR[player], move))


def print_board(board):
    for row in range(board.board_size):
        line = []
        for col in range(board.board_size):
            stone = board.grid[(row, col)]
            if stone == 0:
                line.append(STONE_TO_CHAR[None])
            else:
                line.append(STONE_TO_CHAR[Player(stone)])
        print("%2s %s" % (COLS[row], ''.join(line)))
    
    print("    " + "  ".join(str(e) for e in range(len(COLS))))


def get_zobrist():
    def to_python(player_state):
        if player_state is None:
            return 'None'
        return player_state

    MAX63 = 0x7fff_ffff_ffff_ffff
    table = {}
    empty_board = 0
    for row in range(8):
        for col in range(8):
            for state in (Player.black, Player.white):
                code = random.randint(0, MAX63)
                table[Point(row, col), state] = code

    print('from gotypes import Player, Point')
    print('')
    print('__all__ = ["HASH_CODE", "INIT_BOARD"]')
    print()
    print('HASH_CODE = {')
    for (pt, state), hash_code in table.items():
        print('    (%r, %s): %r,' % (pt, to_python(state), hash_code))
    print('}')
    print()
    print('INIT_BOARD = %d' % (empty_board, ))


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


class Agent:
    """围棋机器人统一接口"""
    def __init__(self):
        pass

    def select_move(self, game_state):
        raise NotImplementedError
    


class MCTSAgent(Agent):
    def __init__(self, num_rounds=300, temperature=5):
        self.num_rounds = num_rounds
        self.temperature = temperature

    def select_move(self, game_state):
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

        # scored_moves = [
        #     (child.winning_frac(game_state.next_player), 
        #      child.prev_move, child.num_rollouts)
        #     for child in root.children
        # ]
        # scored_moves.sort(key=lambda x: x[0], reverse=True)
        # for s, m, n in scored_moves[:]:
        #     print('%s - %.3f (%d)' % (m, s, n))

        # 完成所有推演后，选择下一步动作
        best_move = None
        best_pct = -1.0

        for child in root.children:
            child_pct = child.winning_frac(game_state.next_player)
            # print(child.prev_move, "胜率", child_pct)
            if child_pct > best_pct:
                best_pct = child_pct
                best_move = child.prev_move
        # print('Select move %s with win pct %.3f' % (best_move, best_pct))
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
        
        if empty < 20:
            r = 300
            t = 7
        elif empty < 35:
            r = 200
            t = 5
        elif empty < 50:
            r = 150
            t = 4
        else:
            r = 100
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

