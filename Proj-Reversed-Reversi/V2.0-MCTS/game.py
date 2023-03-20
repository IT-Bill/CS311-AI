import utils
import zobrist
import numpy as np
import copy
from gotypes import Player, Point
from utils import point_to_coord

__all__ = ["Move"]

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
    def __init__(self, board_size=8, grid=utils.INIT_GRID):
        self.board_size = board_size
        self.grid = np.copy(grid)   # nparray
        self._hash = zobrist.INIT_BOARD
        self.num_grid = board_size * board_size

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
    
    @property
    def num_empty(self):
        return (self.board.grid == 0).sum()
    
    @property
    def num_stones(self):
        return self.board.num_grid - self.num_empty
    