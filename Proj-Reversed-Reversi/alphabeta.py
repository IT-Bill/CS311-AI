from const import *
from board_controller import BoardController

my_color = op_color = 0

def alpha_bate(board, color, depth):
    my_color = color
    op_color = -color

    controller = BoardController(board, my_color)
    legal_pos = controller.get_all_legal_pos()
    if len(legal_pos) == 0:
        return None

    best_val = INT_MIN
    for pos in legal_pos:
        new_board = BoardController(controller.board, my_color)
        new_board.board_after_rev(*pos)  # 我方走棋

        temp = min_node(new_board.board, depth - 1, INT_MIN, INT_MAX)

        if temp > best_val:
            best_val = temp
            best_step = pos 
    
    return best_step


def min_node(board, depth, alpha, beta):
    if depth <= 0:
        return evaluate(board)
    

def evaluate(board):
    return WEIGHT_MAP[board == my_color].sum() - WEIGHT_MAP[board == op_color].sum()
