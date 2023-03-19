from dlgo.mcts.mcts import MCTSAgent as Bot
from dlgo.utils import print_board, print_move, point_from_coords

from dlgo.gotypes import Player
from dlgo.goboard import GameState, Move
from dlgo.agent.naive import RandomBot
from dlgo.mcts.mcts import MCTSAgent
import time

def main():
    
    board_size = 5
    game = GameState.new_game(board_size)
    bot = Bot()
    while not game.is_over():
        time.sleep(0.4)

        if game.next_player == Player.black:
            human_move = input("-- ")
            point = point_from_coords(human_move.strip())
            move = Move.play(point)
        else:
            move = bot.select_move(game)

        print_move(game.next_player, move)
        game = game.apply_move(move)
        print_board(game.board)
        
        print("-------------------------")

if __name__ == '__main__':
    main()
