from dlgo import goboard, gotypes
from dlgo.agent import naive
from dlgo.utils import print_board, print_move, point_from_coords
import time

def main():
    
    board_size = 4
    game = goboard.GameState.new_game(board_size)
    bot = naive.RandomBot()
    while not game.is_over():
        time.sleep(0.4)

        if game.next_player == gotypes.Player.black:
            human_move = input("-- ")
            point = point_from_coords(human_move.strip())
            move = goboard.Move.play(point)
        else:
            move = bot.select_move(game)

        print_move(game.next_player, move)
        game = game.apply_move(move)
        print_board(game.board)
        
        print("-------------------------")

if __name__ == '__main__':
    main()
