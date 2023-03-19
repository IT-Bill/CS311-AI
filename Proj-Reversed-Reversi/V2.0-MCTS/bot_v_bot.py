from gotypes import Player
from game import GameState
from agent import RandomAgent
from mcts import MCTSAgent
from utils import print_board, print_move
import time, sys, os


def main():
    
    game = GameState.new_game()
    bots = {
        Player.black: RandomAgent(),
        Player.white: MCTSAgent(),
    }
    while not game.is_over():
        time.sleep(0.1)
        # print(chr(27) + "[2J") # 清屏
        bot_move = bots[game.next_player].select_move(game)
        print_move(game.next_player, bot_move)
        game = game.apply_move(bot_move)
        print_board(game.board)
        print("-------------------------")
        # f.flush()
    
    print("Winner", game.winner())

if __name__ == '__main__':
    main()