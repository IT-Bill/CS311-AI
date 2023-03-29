import numpy as np
from numpy import uint64 as u64


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

BLACK = -1
WHITE = 1
EMPTY = 0

masks_dir = (
    u64(0xffff_ffff_ffff_ffff),  # up
    u64(0xffff_ffff_ffff_ffff),  # down
    u64(0xfefe_fefe_fefe_fefe),  # left
    u64(0x7f7f_7f7f_7f7f_7f7f),  # right
    u64(0xfefe_fefe_fefe_fe00),  # left-up
    u64(0x007f_7f7f_7f7f_7f7f),  # right-down
    u64(0x00fe_fefe_fefe_fefe),  # left-down
    u64(0x7f7f_7f7f_7f7f_7f00),  # right-up
)
mask_all = u64(0xffff_ffff_ffff_ffff)

mask_corner = u64(0x8100_0000_0000_0081)  # 角
mask_star = u64(0x4281_0000_0000_8142)  # 角旁边的两个位置
mask_inner = mask_all ^ (mask_corner | mask_star)  # 其他位置

mask_zero = u64(0)
mask_one = u64(1)
mask_high_one = u64(0x8000_0000_0000_0000)


steps = [
    u64(8),
    u64(1),
    u64(9),
    u64(7)
]

MAX_INT = 0x7fff_ffff
MIN_INT = -0x7fff_ffff

DEBUG_MAX_DEPTH = 0  # debug
################################


def get_bin_board(board):
    s = list('0' * 64)
    for p in np.argwhere(board == -1):
        s[p[0] * 8 + p[1]] = '1'
    black_bin_board = u64(int(''.join(s), 2))

    s = list('0' * 64)
    for p in np.argwhere(board == 1):
        s[p[0] * 8 + p[1]] = '1'
    white_bin_board = u64(int(''.join(s), 2))
    return (black_bin_board, white_bin_board)


def legal_moves(my_board, opp_board):

    empty = ~(my_board | opp_board)
    legal_moves = mask_zero

    _masks = masks_dir

    for i in range(4):
        mask1, mask2 = masks_dir[2 * i], masks_dir[2 * i + 1]
        mask_op1, mask_op2 = mask1 & opp_board, mask2 & opp_board
        step = steps[i]

        tmp = (my_board << step) & mask_op1

        tmp |= (tmp << step) & mask_op1
        tmp |= (tmp << step) & mask_op1
        tmp |= (tmp << step) & mask_op1
        tmp |= (tmp << step) & mask_op1
        tmp |= (tmp << step) & mask_op1

        legal_moves |= (tmp << step) & mask1 & empty
        ############################
        tmp = (my_board >> step) & mask_op2

        tmp |= (tmp >> step) & mask_op2
        tmp |= (tmp >> step) & mask_op2
        tmp |= (tmp >> step) & mask_op2
        tmp |= (tmp >> step) & mask_op2
        tmp |= (tmp >> step) & mask_op2

        legal_moves |= (tmp >> step) & mask2 & empty

    return legal_moves


def apply_move(my_board, opp_board, board_idx):

    captured_board = mask_zero
    # ! 棋盘左上角为idx=0，所以使用mask_high_one，而且为右移
    new_board = mask_high_one >> u64(board_idx)
    my_board ^= new_board

    for i in range(4):
        mask1, mask2 = masks_dir[2 * i], masks_dir[2 * i + 1]
        mask_op1, mask_op2 = mask1 & opp_board, mask2 & opp_board
        step = steps[i]

        tmp = (new_board << step) & mask_op1

        tmp |= (tmp << step) & mask_op1
        tmp |= (tmp << step) & mask_op1
        tmp |= (tmp << step) & mask_op1
        tmp |= (tmp << step) & mask_op1
        tmp |= (tmp << step) & mask_op1

        captured_board |= tmp if (
            (tmp << step) & mask1 & my_board) else mask_zero
        ############################
        tmp = (new_board >> step) & mask_op2

        tmp |= (tmp >> step) & mask_op2
        tmp |= (tmp >> step) & mask_op2
        tmp |= (tmp >> step) & mask_op2
        tmp |= (tmp >> step) & mask_op2
        tmp |= (tmp >> step) & mask_op2

        captured_board |= tmp if (
            (tmp >> step) & mask2 & my_board) else mask_zero

    # change my_board and opp_board
    my_board ^= captured_board
    opp_board ^= captured_board

    return my_board, opp_board


def print_2d_board(bin_board):
    board = np.array([int(s)
                     for s in list('{:064b}'.format(bin_board))]).reshape(8, 8)
    print(board)


def popcount(x):
    n = 0
    mask = mask_one
    while x:
        x &= x - mask
        n += 1
    return n


def find_one(x):
    return [i for i, j in enumerate("{:064b}".format(x)) if j == '1']


def negamax(my_board, opp_board, max_depth, alpha, beta):
    """
    :return (best_score, best_move)
    """
    my_moves = legal_moves(my_board, opp_board)
    opp_moves = legal_moves(opp_board, my_board)

    # 两方都不能走
    if not my_moves and not opp_moves:
        return final_evaluate(my_board, opp_board), None

    # 深度达到限制
    if max_depth == 0:
        return evaluate(my_board, opp_board, my_moves, opp_moves), None

    # 我不能走，但是对方能走
    if not my_moves and opp_moves:
        # 元组不能直接加负号
        return -negamax(opp_board, my_board, max_depth,
                        -beta, -alpha)[0], None

    best_score, best_move = MIN_INT, None

    # find the position of 1
    # star, inner, corner
    star_moves = my_moves & mask_star
    inner_moves = my_moves & mask_inner
    corner_moves = my_moves & mask_corner

    ones = [i for i, j in enumerate("{:064b}".format(star_moves)) if j == '1'] + \
           [i for i, j in enumerate("{:064b}".format(inner_moves)) if j == '1'] + \
           [i for i, j in enumerate("{:064b}".format(corner_moves)) if j == '1']

    # print(ones)

    for idx in ones:
        my_new_board, opp_new_board = apply_move(my_board, opp_board, idx)
        # new board ，记得反过来！
        score = -negamax(opp_new_board, my_new_board , max_depth - 1,
                         -beta, -alpha)[0]
        
        ############
        # ! print
        if max_depth == DEBUG_MAX_DEPTH:
            print((idx // 8, idx % 8), score)
        ##############

        if score > best_score:
            
            

            best_score = score
            best_move = idx

            alpha = max(best_score, alpha)

            if alpha >= beta:
                # pruning
                break

    return best_score, best_move


def select_move(my_board, opp_board, max_depth):
    global DEBUG_MAX_DEPTH

    empty_cnt = popcount(~(my_board | opp_board))
    if empty_cnt <= 10:
        # 搜完
        DEBUG_MAX_DEPTH = empty_cnt
        score, move = negamax(my_board, opp_board, empty_cnt, MIN_INT, MAX_INT)
    else:
        DEBUG_MAX_DEPTH = max_depth
        score, move = negamax(my_board, opp_board, max_depth, MIN_INT, MAX_INT)
    return move


def select_move_easy(board, player, max_depth):
    

    black, white = get_bin_board(board)
    if player == BLACK:
        m = select_move(black, white, max_depth)
    elif player == WHITE:
        m = select_move(white, black, max_depth)
    
    if m is not None:
        return (m // 8, m % 8)
    else:
        return (-1, -1)

###########################
# evaluate
score_corner_shift = 12  # 4096 -
score_star_shift = 7  # 128 +
score_inner_shift = 3  # 8 -
score_mobility_shift3 = 3 # 8 +  行动力
score_mobility_shift4 = 4 # 8 +  行动力

score_win_shift = 20  # 0xfffff


def evaluate(
    my_board, opp_board,
    my_moves, opp_moves,
):
    empty_cnt = popcount(~(my_board | opp_board))

    my_star = my_board & mask_star
    my_inner = my_board & mask_inner
    my_corner = my_board & mask_corner

    opp_star = opp_board & mask_star
    opp_inner = opp_board & mask_inner
    opp_corner = opp_board & mask_corner

    score = 0
    # ! 直接作差是错误的！！！会溢出
    # score += (popcount(my_star) - popcount(opp_star)) << score_star_shift
    # score -= (popcount(my_inner) - popcount(opp_inner)) << score_inner_shift
    # score -= (popcount(my_corner) - popcount(opp_corner)) << score_corner_shift
    # score += (popcount(my_moves) - popcount(opp_moves)) << score_mobility_shift

    # 正收益
    score += popcount(my_star) << score_star_shift
    score -= popcount(opp_star) << score_star_shift

    # 负收益
    score -= popcount(my_inner) << score_inner_shift
    score += popcount(opp_inner) << score_inner_shift
    
    # 负收益
    score -= popcount(my_corner) << score_corner_shift
    score += popcount(opp_corner) << score_corner_shift

    # 正收益
    score += popcount(my_moves) << score_mobility_shift
    score -= popcount(opp_moves) << score_mobility_shift


    return score

def final_evaluate(
    my_board, opp_board
):
    # ! 别写反了！！
    return (popcount(opp_board) - popcount(my_board)) << score_win_shift
    
