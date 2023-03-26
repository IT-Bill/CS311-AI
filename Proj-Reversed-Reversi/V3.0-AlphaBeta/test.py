from alphabeta import select_move
from game import GameState

game_state = GameState.new_game()

m = select_move(game_state, 0)

print(m)