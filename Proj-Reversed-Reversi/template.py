import numpy as np
import random
import time

COLOR_BLACK = -1
COLOR_WHITH = 1
COLOR_NONE = 0
random.seed(0)


class AI:
    """don't change the class name"""

    def __init__(self, chessboard_size, color, time_out):
        """chessboard_size, color, time_out passed from age"""
        self.chessboard_size = chessboard_size
        # You are white or black
        self.color = color
        # the max time you should use, your algorithm's run time must not exceed the time limit
        self.time_out = time_out
        # You need to add your decision to your candidate_list. The system will get the end of your candidate_list as you decision
        self.candidate_list = []

    def go(self, chessboard):
        """The input is the current chessboard. Chessboard is a numpy array"""
        # Clear candidate_list, must do this st
        self.candidate_list.clear()
        # ===================================
        
        # ============================
