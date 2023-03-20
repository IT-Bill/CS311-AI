from gotypes import Player
from game import GameState
from agent import RandomAgent
from mcts import MCTSAgent
from utils import print_board, print_move
import time, sys, os

dir = os.path.abspath(os.path.dirname(__file__))
f = open(dir + "\\mcts_v_mcts.txt", "a")
f.truncate(0)
sys.stdout = f


def main():
    
    game = GameState.new_game()
    bots = {
        Player.black: MCTSAgent(auto_set_param=False, temperature=5),
        Player.white: MCTSAgent(auto_set_param=True, temperature=5),
    }
    while not game.is_over():

        start = time.perf_counter()
        bot_move = bots[game.next_player].select_move(game)
        end = time.perf_counter()
        print("Time: ", end - start)

        print_move(game.next_player, bot_move)
        game = game.apply_move(bot_move)
        print_board(game.board)
        print("-------------------------")
        f.flush()
    
    print("Winner", game.winner())

if __name__ == '__main__':
    main()
    f.close()