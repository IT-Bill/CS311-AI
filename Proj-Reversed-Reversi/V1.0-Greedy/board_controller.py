import numpy as np

class BoardController:
    def __init__(self, board, cur_color):
        # numpy array
        self.board = np.copy(board)
        # 当前执棋色
        self.cur_color = cur_color
        self.legal_pos = []
        self.rev_pos = []
        self.dir = ((-1, 0), (-1, 1), (0, 1), (1, 1),
                    (1, 0), (1, -1), (0, -1), (-1, -1))
        
     
    def on_board(self, x, y):
        """判断某位置是否在棋盘上"""
        return 0 <= x <= 7 and 0 <= y <= 7
    
    def is_legal_pos(self, cheak_only, i, j):
        self.rev_pos.clear()

        # 当前位置为空，且在棋盘上,可能是落子点，可以搜索
        if self.on_board(i, j) and self.board[i, j] == 0:
            for dx, dy in self.dir:
                op_cnt = 1
                x, y = i + dx, j + dy 

                while self.on_board(x, y): # 在棋盘上
                    if self.board[x, y] == -self.cur_color:
                        # 且为对方棋子，可以继续前进
                        op_cnt += 1 # 记录要翻转的棋子个数
                        x += dx
                        y += dy
                    elif self.board[x, y] == self.cur_color and op_cnt > 1:
                        # 己方棋子，而且至少遇到一个对方棋子

                        if cheak_only:
                            return True

                        while op_cnt > 0:
                            x -= dx
                            y -= dy 
                            self.rev_pos.append((x, y))
                            op_cnt -= 1
                    
                    else:
                        # 是NONE，向下一个方向搜索
                        break
                
                # 前进之后，不在棋盘上，继续搜索下一个方向
        
        return len(self.rev_pos) > 0
    
    def get_all_legal_pos(self):
        """直接返回合法的列表，不再返回True or False"""
        # has_legal_pos = False
        self.legal_pos.clear()

        for i in range(8):
            for j in range(8):
                if self.is_legal_pos(True, i, j):
                    self.legal_pos.append((i, j))
                    # has_legal_pos = True 
        
        return self.legal_pos


    def board_after_rev(self, x, y):
        """落子方法，调用后修改原棋盘，落子位置一定要合法"""
        if (self.is_legal_pos(False, x, y)):
            # TODO 可以加速
            for pos in self.rev_pos:
                self.board[x, y] = self.cur_color

