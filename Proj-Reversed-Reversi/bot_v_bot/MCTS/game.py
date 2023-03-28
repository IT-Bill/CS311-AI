import numpy as np

BLACK = -1
WHITE = 1
EMPTY = 0

BOARD_SIZE = 8

DIRS = set([(-1, 0), (-1, 1), (0, 1), (1, 1),
            (1, 0), (1, -1), (0, -1), (-1, -1)])

# move format
# (row, col, state)
MOVE_PASS = -1
MOVE_NONE = -2  # 针对开局情况

INIT_BOARD = np.array([[0,  0,  0,  0,  0,  0,  0,  0],
                      [0,  0,  0,  0,  0,  0,  0,  0],
                      [0,  0,  0,  0,  0,  0,  0,  0],
                      [0,  0,  0,  1, -1,  0,  0,  0],
                      [0,  0,  0, -1,  1,  0,  0,  0],
                      [0,  0,  0,  0,  0,  0,  0,  0],
                      [0,  0,  0,  0,  0,  0,  0,  0],
                      [0,  0,  0,  0,  0,  0,  0,  0]])


class GameState:
    def __init__(self, board, next_player, prev_state=None, last_move=(-2, -2)):
        self.board = board  # nparray
        self.next_player = next_player

        self.prev_state = prev_state
        self.last_move = last_move

        self.winner = None
        self.over = None

        self.num_empty = (board == 0).sum()

    def apply_move(self, move):
        """执行落子动作，返回新的GameState对象"""
        if move[0] != MOVE_PASS:
            next_board = np.copy(self.board)
            reverse = np.array(self.get_reverse(move))
            next_board[reverse[:, 0], reverse[:, 1]] = self.next_player
        else:
            next_board = self.board

        return GameState(next_board, -self.next_player, self, move)

    @classmethod
    def new_game(cls):
        return GameState(INIT_BOARD, BLACK, None)

    def is_valid_move(self, move):
        if self.over:
            return False

        # if len(move) == 3 and move[2] == MOVE_PASS:
        #     return True

        i, j = move

        if self.is_on_grid(i, j) and self.board[i, j] == EMPTY:
            for dx, dy in DIRS:
                op_cnt = 0
                x, y = i + dx, j + dy

                while self.is_on_grid(x, y):
                    if self.board[x, y] == -self.next_player:
                        op_cnt += 1
                        x += dx
                        y += dy
                    elif self.board[x, y] == self.next_player and op_cnt > 0:
                        return True

                    else:
                        break
        return False

    def get_reverse(self, move):
        if self.over or move[0] == MOVE_PASS:
            return []
        

        reverse = []
        i, j = move


        if self.is_on_grid(i, j) and self.board[i, j] == EMPTY:
            for dx, dy in DIRS:
                op_cnt = 0
                x, y = i + dx, j + dy

                while self.is_on_grid(x, y):
                    if self.board[x, y] == -self.next_player:
                        op_cnt += 1
                        x += dx
                        y += dy
                    elif self.board[x, y] == self.next_player and op_cnt > 0:
                        while op_cnt > 0:
                            x -= dx
                            y -= dy
                            reverse.append((x, y))
                            op_cnt -= 1
                        break

                    else:
                        break

        if len(reverse) > 0:
            reverse.append((i, j))  # 自己将要下的位置
        return reverse

    def is_over(self):
        if self.over is not None:
            return self.over

        if self.last_move[0] != MOVE_PASS:
            return False
        second_last_move = self.prev_state.last_move
        if second_last_move[0] != MOVE_PASS:
            return False
        
        self.winner = self.get_winner()
        return True

    def is_on_grid(self, i, j):
        return 0 <= i < BOARD_SIZE and 0 <= j < BOARD_SIZE

    def legal_moves(self):
        moves = []
        empty_points = np.argwhere(self.board == 0)
        # empty_points = self.board.argwhere(self.board == 0)
        for p in empty_points:
            if self.is_valid_move(p):
                moves.append(p)

        # ! 当没有位置可以下的时候，加入跳过
        if (len(moves) == 0):
            moves = [(-1, -1)]

        return moves

    def get_winner(self):
        # if not self.is_over():
        #     return None
        
        num_black = (self.board == BLACK).sum()
        num_white = (self.board == WHITE).sum()

        if num_black < num_white:
            return BLACK
        elif num_white < num_black:
            return WHITE
        else:
            # draw
            return 0


