'''
Generate all possible moves for a position.
'''

from enum import Enum

import representation
from representation import Square
from representation import Move


class Capture(Enum):
    '''
    Enumeration to represent whether a piece can move in a direction and
    capture. ONLY shows that pawns can only move diagonally to capture.
    '''
    YES = True
    NO = False
    ONLY = 2


def movescan(x_start, y_start, x_change, y_change, posn, capture=True, stop_short=False):
    '''
    Scan for possible moves.

    :param x_start:     x coord to start scan at.
    :param y_start:     y coord to start scan at.
    :param x_change:    Rate to move in x direction.
    :param y_change:    Rate to move in y direction.
    :param posn:        The board representation to scan.
    :param capture:     Whether to attempt capture.
    :param stop_short:  Whether to stop before enemy pieces.

    :returns: All possible moves.
    '''
    x_coord = x_start
    y_coord = y_start

    # Check the color of the piece to move
    color = posn.piece_color(x_coord, y_coord)

    moves = []
    i = 0
    while True:
        x_coord = x_coord + x_change
        y_coord = y_coord + y_change
        if x_coord >= representation.NROWS or y_coord >= representation.NCOLS \
                or x_coord < 0 or y_coord < 0:
            break
        if posn.board[x_coord][y_coord] != '.':
            if posn.piece_color(x_coord, y_coord) == color:
                break
            if capture is False:
                break
            stop_short = True
        elif capture == Capture.ONLY:
            break
        moves.append(Move(Square(x_start, y_start), Square(x_coord, y_coord)))
        i += 1
        if posn.board[x_coord][y_coord] == 'k' or posn.board[x_coord][y_coord] == 'K':
            moves[i-1].win = True
        if stop_short:
            break
    return moves


def symmscan(x_start, y_start, x_change, y_change, posn, capture=True, stop_short=False):
    '''
    Rotate the board and perform move scan for each rotation.
    See movescan for parameters.
    '''
    moves = []
    for _ in range(4):
        moves += \
        movescan(x_start, y_start, x_change, y_change, posn, capture=capture, stop_short=stop_short)
        x_change, y_change = y_change, x_change
        x_change *= -1
    return moves


def movelist(x_start, y_start, posn):
    '''
    Generate all possible moves for a piece.
    See movescan for parameters.
    '''
    assert posn.board[x_start][y_start] != '.'
    moves = []
    kind = posn.kind(x_start, y_start)
    if kind == 'king' or kind == 'queen':
        stop_short = (kind == 'king')
        moves += symmscan(x_start, y_start, 1, 0, posn, stop_short=stop_short)
        moves += symmscan(x_start, y_start, 1, 1, posn, stop_short=stop_short)
    elif kind == 'bishop' or kind == 'rook':
        stop_short = (kind == 'bishop')
        capture = (kind == 'rook')
        moves += symmscan(x_start, y_start, 1, 0, posn, capture=capture, stop_short=stop_short)
        if kind == 'bishop':
            stop_short = False
            capture = True
            moves += symmscan(x_start, y_start, 1, 1, posn, capture=capture, stop_short=stop_short)
    elif kind == 'knight':
        moves += symmscan(x_start, y_start, 2, 1, posn, stop_short=True)
        moves += symmscan(x_start, y_start, 2, -1, posn, stop_short=True)
    elif kind == 'pawn':
        direction = 1 if posn.piece_color(x_start, y_start) == 'W' else -1
        moves += \
        movescan(x_start, y_start, direction, -1, posn, capture=Capture.ONLY, stop_short=True)
        moves += \
        movescan(x_start, y_start, direction, 1, posn, capture=Capture.ONLY, stop_short=True)
        moves += \
        movescan(x_start, y_start, direction, 0, posn, capture=False, stop_short=True)
    return moves


def find_moves(posn):
    '''
    Find all pieces for the color on move, then find all moves for those pieces.

    :param posn: Current board state.
    :returns: Move list containing all possible moves for color on move.
    '''
    locations = []
    for i in range(len(posn.board)):
        for j in range(len(posn.board[i])):
            if posn.board[i][j] == '.':
                continue
            elif posn.on_move == 'W' and str.isupper(posn.board[i][j]):
                locations.append((i, j))
            elif posn.on_move == 'B' and str.islower(posn.board[i][j]):
                locations.append((i, j))
    moves = []
    for location in locations:
        moves += movelist(location[0], location[1], posn)
    return moves
