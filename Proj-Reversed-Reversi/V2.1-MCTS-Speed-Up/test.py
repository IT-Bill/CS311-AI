
from main import MCTSAgent, GameState, AI, INIT_BOARD

ai = AI(8, 1, 5)
ai.go(INIT_BOARD)



print(ai.candidate_list)