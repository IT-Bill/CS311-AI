from old_AlphaBeta.game import popcount, get_bin_board

from old_AlphaBeta.game import select_move_easy as old
from new_AlphaBeta.game import select_move_easy as new

from MCTS.game import GameState, BLACK, WHITE
from MCTS.mcts import MCTSAgent
from MCTS.utils import print_board

import time
import sys
import os

dir = os.path.abspath(os.path.dirname(__file__))
f1 = open(dir + "\\alphabeta_v_mcts.txt", "a")
f1.truncate(0)


f2 = open(dir + "\\result.txt", "a")
f2.truncate(0)

def main():
    sys.stdout = f1
    game = GameState.new_game()
    bots = {
        BLACK: old,
        WHITE: new
    }

    while not game.is_over():

        start = time.perf_counter()
        bot_move = bots[game.next_player](game.board, game.next_player, 6)
        end = time.perf_counter()
        print("Time: ", end - start)

        print(game.next_player, bot_move)

        game = game.apply_move(bot_move)
        print_board(game.board)
        # print(game.board)
        b, w = get_bin_board(game.board)
        print(popcount(b), ":", popcount(w))
        print("-------------------------")
        f1.flush()

    print("Winner", game.winner)
    sys.stdout = f2
    print("Winner", game.winner)
    f2.flush()


if __name__ == '__main__':
    for i in range(50):
        main()
    f1.close()
    f2.close()
