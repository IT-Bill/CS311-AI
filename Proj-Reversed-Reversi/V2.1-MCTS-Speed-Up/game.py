BLACK = -1
WHITE = 1
EMPTY = 0

BOARD_SIZE = 8

DIRS = [(-1, 0), (-1, 1), (0, 1), (1, 1),
        (1, 0), (1, -1), (0, -1), (-1, -1)]

POSITIONS = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7),
             (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7),
             (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7),
             (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7),
             (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7),
             (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7),
             (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7),
             (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7)]

# move format
# (row, col, state)
MOVE_NONE = 0  # 针对开局情况
MOVE_PASS = -1


class GameState:
    def __init__(self, board, next_player, prev_state=None, last_move=(-1, -1)):
        self.board = board  # nparray
        self.next_player = next_player

        self.prev_state = prev_state
        self.last_move = last_move

    def apply_move(self, move):
        pass

    def is_valid_move(self, move):
        if self.is_over():
            return False

        # if len(move) == 3 and move[2] == MOVE_PASS:
        #     return True

        i, j = move

        if self.is_on_grid(i, j) and self.board[i, j] == EMPTY:
            for dx, dy in DIRS:
                op_cnt = 1  # 1是为了算上己方将要下的位置
                x, y = i + dx, j + dy

                while self.board.is_on_grid(x, y):
                    if self.board[x, y] == -self.next_player:
                        op_cnt += 1
                        x += dx
                        y += dy
                    elif self.board[x, y] == self.next_player and op_cnt > 1:
                        return True

                    else:
                        break
        return False

    def get_reverse(self, move):
        if self.is_over():
            return []

        # if move[2] == MOVE_PASS:
        #     return []

        reverse = []
        i, j = move[0], move[1]

        if self.is_on_grid(i, j) and self.board[i, j] == EMPTY:
            for dx, dy in DIRS:
                op_cnt = 0
                x, y = i + dx, j + dy

                while self.board.is_on_grid(x, y):
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
        if self.last_move[2] != MOVE_PASS:
            return False
        second_last_move = self.prev_state.last_move
        if second_last_move[2] != MOVE_PASS:
            return False
        return True

    def is_on_grid(self, i, j):
        return 0 <= i < BOARD_SIZE and 0 <= i < BOARD_SIZE

    def legal_moves(self):
        moves = []
        empty_points = self.board.argwhere(self.board == 0)
        
