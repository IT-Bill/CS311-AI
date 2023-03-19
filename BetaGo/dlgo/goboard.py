from dlgo.gotypes import Player, Point
from typing import Optional, Union, Any, Set, List, Tuple
from dlgo import zobrist
import copy
from dlgo.scoring import compute_game_result
from dlgo.utils import COLS

__all__ = ["Move", "GoString", "GameState", "Board"]


class Move:
    """设置棋手能够采取的一种动作"""

    def __init__(self, point=None, is_pass=False, is_resign=False):
        assert (point is not None) ^ is_pass ^ is_resign
        self.point = point
        self.is_play = (point is not None)
        self.is_pass = is_pass
        self.is_resign = is_resign

    @classmethod
    def play(cls, point):
        """在棋盘上落一颗子"""
        return Move(point=point)

    @classmethod
    def pass_turn(cls):
        return Move(is_pass=True)

    @classmethod
    def resign(cls):
        return Move(is_resign=True)

    def __str__(self) -> str:
        if self.is_pass:
            move_str = "passes"
        elif self.is_resign:
            move_str = "resigns"
        else:
            move_str = '%s%d' % (COLS[self.point.col - 1], self.point.row)
        return move_str


class GoString:
    """棋链类，一系列同色且相连的棋子"""

    def __init__(self, color, stones, liberties):
        self.color = color
        # frozenset创建之后无法修改
        self.stones = frozenset(stones)
        self.liberties = frozenset(liberties)

    def without_liberty(self, point):
        new_liberties = self.liberties - set([point])
        return GoString(self.color, self.stones, new_liberties)

    def with_liberty(self, point):
        new_liberties = self.liberties | set([point])
        return GoString(self.color, self.stones, new_liberties)

    def merged_with(self, go_string):
        """
        返回一条新的棋链，包含self和go_string的所有棋子
        :param go_string: GoString对象
        """
        assert go_string.color == self.color
        combined_stones = self.stones | go_string.stones
        return GoString(
            self.color, combined_stones,
            (self.liberties | go_string.liberties) - combined_stones
        )

    @property
    def num_liberties(self):
        return len(self.liberties)

    def __eq__(self, other) -> bool:
        return isinstance(other, GoString) and \
            self.color == other.color and \
            self.stones == other.stones and \
            self.liberties == other.liberties


class Board:
    """棋盘类"""

    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid = {}  # 存储棋链的字典
        self._hash = zobrist.EMPTY_BOARD

    def place_stones(self, player: Player, point: Point):
        assert self.is_on_grid(point)
        assert self._grid.get(point) is None  # 这个位置是空的才能落子
        adjacent_same_color: List[GoString] = []
        adjacent_opposite_color: List[GoString] = []
        liberties = []

        # 检查相邻点的气数
        for neighbor in point.neighbors:
            if not self.is_on_grid(neighbor):
                continue
            neighbor_string = self._grid.get(neighbor)

            if neighbor_string is None:
                liberties.append(neighbor)  # ? 什么意思
            elif neighbor_string.color == player:
                if neighbor_string not in adjacent_same_color:
                    adjacent_same_color.append(neighbor_string)
            elif neighbor_string.color == player.other:
                if neighbor_string not in adjacent_opposite_color:
                    adjacent_opposite_color.append(neighbor_string)

        new_string = GoString(player, [point], liberties)

        # 合并同色相邻的棋链
        for same_color_string in adjacent_same_color:
            new_string = new_string.merged_with(same_color_string)

        # 设置stone对应的棋链为键值对
        for new_string_point in new_string.stones:
            self._grid[new_string_point] = new_string

        # 应用哈希值
        self._hash ^= zobrist.HASH_CODE[point, player]

        # 减少对方相邻棋链的气
        for opposite_color_string in adjacent_opposite_color:
            replacement = opposite_color_string.without_liberty(point)
            if replacement.num_liberties > 0:
                self._replace_string(replacement)
            else:
                self._remove_string(opposite_color_string)

        # 提走
        for opposite_color_string in adjacent_opposite_color:
            if opposite_color_string.num_liberties == 0:
                self._remove_string(opposite_color_string)

    def _replace_string(self, new_string):
        for point in new_string.stones:
            self._grid[point] = new_string

    def _remove_string(self, string: GoString):
        for point in string.stones:
            for neighbor in point.neighbors:
                neighbor_string = self.get_go_string(neighbor)
                if neighbor_string is None:
                    continue

                # 为己方相邻棋链增加气数
                if neighbor_string is not string:
                    self._replace_string(neighbor_string.with_liberty(point))
            self._grid[point] = None

            # 应用哈希值提子
            self._hash ^= zobrist.HASH_CODE[point, string.color]

    def is_on_grid(self, point):
        return 1 <= point.row <= self.num_rows and \
            1 <= point.col <= self.num_cols

    def get(self, point) -> Player:
        """返回棋盘上某点的状态(黑白空)"""
        string = self._grid.get(point)
        if string is None:
            return None
        return string.color

    def get_go_string(self, point) -> GoString:
        """返回某个点所在的棋链"""
        return self._grid.get(point)

    @property
    def zobrist_hash(self):
        return self._hash

    def __eq__(self, other):
        return isinstance(other, Board) and \
            self.num_rows == other.num_rows and \
            self.num_cols == other.num_cols and \
            self._hash() == other._hash()

    def __deepcopy__(self, memodict={}):
        copied = Board(self.num_rows, self.num_cols)
        # Can do a shallow copy b/c the dictionary maps tuples
        # (immutable) to GoStrings (also immutable)
        copied._grid = copy.copy(self._grid)
        copied._hash = self._hash
        return copied


class GameState:
    def __init__(self, board, next_player, prev_state, last_move):
        self.board: Board = board
        self.next_player: Player = next_player

        # 应用zobrist_hash
        self.prev_state: GameState = prev_state
        if self.prev_state is None:
            self.prev_states = frozenset()
        else:
            self.prev_states = frozenset(
                prev_state.prev_states |
                {(prev_state.next_player, prev_state.board.zobrist_hash)}
            )

        self.last_move: Move = last_move

    def apply_move(self, move: Move):
        """执行落子动作，返回新的GameState对象"""
        if move.is_play:
            next_board = copy.deepcopy(self.board)
            next_board.place_stones(self.next_player, move.point)
        else:
            next_board = self.board
        return GameState(next_board, self.next_player.other, self, move)

    @classmethod
    def new_game(cls, board_size):
        if isinstance(board_size, int):
            board_size = (board_size, board_size)
        board = Board(*board_size)
        return GameState(board, Player.black, None, None)

    def is_over(self):
        # 两个None都是防止开局的时候判断错误
        if self.last_move is None:
            return False
        if self.last_move.is_resign:
            return True
        second_last_move = self.prev_state.last_move
        if second_last_move is None:
            return False
        return self.last_move.is_pass and second_last_move.is_pass

    def is_move_self_capture(self, player, move) -> bool:
        """判断是否是自吃"""
        if not move.is_play:
            return False
        next_board = copy.deepcopy(self.board)
        next_board.place_stones(player, move.point)
        new_string = next_board.get_go_string(move.point)
        return new_string.num_liberties == 0

    @property
    def situation(self):
        return (self.next_player, self.board)

    def is_move_violate_ko(self, player, move):
        """判断是否违反劫争规则"""
        if not move.is_play:
            return False
        next_board = copy.deepcopy(self.board)
        next_board.place_stones(player, move.point)
        next_situation = (player.other, next_board.zobrist_hash)
        return next_situation in self.prev_states

    def is_valid_move(self, move):
        if self.is_over():
            return False

        if move.is_pass or move.is_resign:
            return True

        return (
            self.board.get(move.point) is None and
            not self.is_move_self_capture(self.next_player, move) and
            not self.is_move_violate_ko(self.next_player, move)
        )

    def legal_moves(self):
        moves = []
        for row in range(1, self.board.num_rows + 1):
            for col in range(1, self.board.num_cols + 1):
                move = Move.play(Point(row, col))
                if self.is_valid_move(move):
                    moves.append(move)
        # These two moves are always legal.
        moves.append(Move.pass_turn())
        moves.append(Move.resign())

        return moves

    # TODO 复制粘贴来的
    def winner(self):
        if not self.is_over():
            return None
        if self.last_move.is_resign:
            return self.next_player
        game_result = compute_game_result(self)
        return game_result.winner
