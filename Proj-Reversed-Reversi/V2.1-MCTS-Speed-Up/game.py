BLACK = -1
WHITE = 1
EMPTY = 0

BOARD_SIZE = 8

DIRS = [(-1, 0), (-1, 1), (0, 1), (1, 1),
             (1, 0), (1, -1), (0, -1), (-1, -1)]

# move format
# (row, col, state)
MOVE_NONE = 0  # 针对开局情况
MOVE_PASS = -1


class GameState:
    def __init__(self, board, next_player, prev_state, last_move=(-1, -1, 0)):
        self.board = board  # nparray
        self.next_player = next_player

        self.prev_state = prev_state
        self.last_move = last_move

    def apply_move(self, move):
        pass

    def is_valid_move(self, move):
        if self.is_over():
            return False

        if move[2] == MOVE_PASS:
            return True

        i, j = move[0], move[1]

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
        # ! 注释了，看看行不行
        # if self.is_over():
        #     return False

        # if move[2] == MOVE_PASS:
        #     return True

        reverse = []
        i, j = move[0], move[1]

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

    
    def is_over(self):
        if self.last_move[0] != MOVE_PASS:
            return False
        second_last_move = self.prev_state.last_move
        if second_last_move[0] != MOVE_PASS:
            return False
        return True
    

    def is_on_grid(self, i, j):
        return 0 <= i < BOARD_SIZE and 0 <= i < BOARD_SIZE
    
