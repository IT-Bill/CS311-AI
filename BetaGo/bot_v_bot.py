from dlgo import goboard, gotypes
from dlgo.agent import naive
from dlgo.utils import print_board, print_move
import time

def main():
    
    board_size = 4
    game = goboard.GameState.new_game(board_size)
    bots = {
        gotypes.Player.black: naive.RandomBot(),
        gotypes.Player.white: naive.RandomBot(),
    }
    while not game.is_over():
        time.sleep(0.4)
        # print(chr(27) + "[2J") # 清屏
        bot_move = bots[game.next_player].select_move(game)
        print_move(game.next_player, bot_move)
        game = game.apply_move(bot_move)
        print_board(game.board)
        print("-------------------------")

if __name__ == '__main__':
    main()
