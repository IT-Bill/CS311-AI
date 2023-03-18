class Agent:
    """围棋机器人统一接口"""
    def __init__(self):
        pass

    def select_move(self, game_state):
        raise NotImplementedError