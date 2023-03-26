from game import GameState, BLACK, WHITE
from utils import print_board, print_move
import time, sys, os
from alphabeta import alphabeta_select_move

dir = os.path.abspath(os.path.dirname(__file__))
f1 = open(dir + "\\mcts_v_mcts.txt", "a")
f1.truncate(0)


f2 = open(dir + "\\result.txt", "a")
f2.truncate(0)





def main():
    sys.stdout = f1
    game = GameState.new_game()
    bots = {
        BLACK: alphabeta_select_move,
        WHITE: alphabeta_select_move,
    }
    while not game.is_over():

        start = time.perf_counter()

        if game.next_player == BLACK:
            bot_move = bots[game.next_player](game, 1)
        else:
            bot_move = bots[game.next_player](game, 4)
        
        end = time.perf_counter()
        print("Time: ", end - start)

        print_move(game.next_player, bot_move)
        game = game.apply_move(bot_move)
        print_board(game.board)
        print("-------------------------")
        f1.flush()
    
    sys.stdout = f2
    print("Winner", game.winner)
    f2.flush()

if __name__ == '__main__':
    main()
    f1.close()
    f2.close()



