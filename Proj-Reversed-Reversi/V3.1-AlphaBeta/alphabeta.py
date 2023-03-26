import numpy as np
from game import WHITE, BLACK
MAX_SCORE = 999999
MIN_SCORE = -999999

__all__ = ['select_move']


def alphabeta_search(game_state, max_depth, alpha, beta):
    if game_state.over:
        if game_state.winner == game_state.next_player:
            return MAX_SCORE
        else:
            return MIN_SCORE

    if max_depth == 0:
        return evaluate(game_state)

    best_score = MIN_SCORE
    for move in game_state.legal_moves():
        next_state = game_state.apply_move(move)

        opponent_best_score = alphabeta_search(
            next_state, max_depth - 1,
            alpha, beta
        )
        my_score = -1 * opponent_best_score

        if my_score > best_score:
            best_score = my_score

        if game_state.next_player == WHITE:
            if best_score > beta:
                beta = best_score
            outcome_for_black = -1 * best_score
            if outcome_for_black < alpha:
                return best_score

        elif game_state.next_player == BLACK:
            if best_score > alpha:
                alpha = best_score
            outcome_for_white = -1 * best_score
            if outcome_for_white < alpha:
                return best_score

    return best_score


# def max_value(game_state, alpha, beta, max_depth):
def get_weight_map(a):
    return np.append(np.append(a, np.flipud(a), axis=0), np.fliplr(np.append(a, np.flipud(a), axis=0)), axis=1)


WEIGHT_MAP = np.array([
    [-5000,  2000,  1000,  1000],
    [2000,  2000,  100,  100],
    [1000,  100,  250,  500],
    [1000,  100,  500, 1000],
], dtype=int)
WEIGHT_MAP = get_weight_map(WEIGHT_MAP)


def evaluate(game_state):
    black_score = (WEIGHT_MAP[game_state.board == BLACK]).sum()
    white_score = (WEIGHT_MAP[game_state.board == WHITE]).sum()

    if game_state.next_player == BLACK:
        return black_score - white_score
    else:
        return white_score - black_score


def alphabeta_select_move(game_state, max_depth):
    best_moves = []
    best_score = MIN_SCORE
    best_black = best_white = MIN_SCORE

    for move in game_state.legal_moves():
        next_state = game_state.apply_move(move)

        opponent_best_score = alphabeta_search(
            next_state, max_depth, best_black, best_white
        )

        my_best_score = -1 * opponent_best_score
        if my_best_score > best_score:
            best_moves = [move]
            best_score = my_best_score

            if game_state.next_player == BLACK:
                best_black = best_score
            elif game_state.next_player == WHITE:
                best_white = best_score
        elif my_best_score == best_score:
            best_moves.append(move)

    import random
    return random.choice(best_moves)


class AlphaBetaAgent:
    def __init__(self):
        pass