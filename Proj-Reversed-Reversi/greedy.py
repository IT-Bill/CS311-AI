import numpy as np

WEIGHT_MAP = -np.array([[500, -25, 10, 5, 5, 10, -25, 500],
     [-25, -45, 1, 1, 1, 1, -45, -25],
     [10, 1, 3, 2, 2, 3, 1, 10],
     [5, 1, 2, 1, 1, 2, 1, 5],
     [5, 1, 2, 1, 1, 2, 1, 5],
     [10, 1, 3, 2, 2, 3, 1, 10],
     [-25, -45, 1, 1, 1, 1, -45, -25],
     [500, -25, 10, 5, 5, 10, -25, 500]])


def greedy(board_controller):
    board_controller.get_all_legal_pos()
    min_flip = 64
    for pos in board_controller.legal_pos:
        board_controller.is_legal_pos(False, pos[0], pos[1])
        if len(board_controller.rev_pos) < min_flip:
            min_pos = pos 
    
    return min_pos
