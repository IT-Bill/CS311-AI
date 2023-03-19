from dlgo.gotypes import Player
from dlgo.goboard import GameState
from dlgo.agent.naive import RandomBot
from dlgo.mcts.mcts import MCTSAgent
from dlgo.utils import print_board, print_move
import time

def main():
    
    board_size = 9
    game = GameState.new_game(board_size)
    bots = {
        Player.black: RandomBot(),
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
    
    print("Winner", game.winner())

if __name__ == '__main__':
    main()
