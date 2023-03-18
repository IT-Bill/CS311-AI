from dlgo.gotypes import Point
from dlgo.goboard import Board

def is_point_an_eye(board: Board, point: Point, color):
    if board.get(point) is not None:
        return False
    for neighbor in point.neighbors:
        if board.is_on_grad(neighbor):
            neighbor_color = board.get(neighbor)
            if neighbor_color != color:
                return False
    
    friendly_corners = 0
    off_board_corners = 0
    
    for corner in point.corners:
        if board.is_on_grad(corner):
            corner_color = board.get(corner)
            if corner_color == color:
                friendly_corners += 1
        
        else:
            off_board_corners += 1

    if off_board_corners > 0:
        return friendly_corners + off_board_corners == 4
    return friendly_corners >= 3



    