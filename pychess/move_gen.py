import representation
from representation import Square
from representation import Move
from representation import Posn
from enum import Enum


class Capture(Enum):
    YES = True
    NO = False
    ONLY = 2


def movescan(x0, y0, dx, dy, posn, capture=True, stop_short=False):
    x = x0
    y = y0

    # Check the color of the piece to move
    c = posn.piece_color(x, y)

    moves = []
    i = 0
    while True:
        x = x + dx
        y = y + dy
        if x >= representation.NROWS or y >= representation.NCOLS \
                or x < 0 or y < 0:
            break
        if posn.board[x][y] != '.' :
            if posn.piece_color(x, y) == c:
                break
            if capture == False:
                break
            stop_short = True
        elif capture == Capture.ONLY:
            break
        moves.append(Move(Square(x0, y0), Square(x, y)))
        i += 1
        if posn.board[x][y] == 'k' or posn.board[x][y] == 'K':
            moves[i-1].win = True
        if stop_short:
            break
    return moves


def symmscan(x, y, dx, dy, posn, capture=True, stop_short=False):
    moves = []
    for i in range(4):
        moves += movescan(x, y, dx, dy, posn, capture=capture, stop_short=stop_short)
        dx, dy = dy, dx
        dx *= -1
    return moves


def movelist(x, y, posn):
    assert(posn.board[x][y] != '.')
    moves = []
    kind = posn.kind(x, y)
    if kind == 'king' or kind == 'queen':
        stop_short = (kind == 'king')
        moves += symmscan(x, y, 1, 0, posn, stop_short=stop_short)
        moves += symmscan(x, y, 1, 1, posn, stop_short=stop_short)
    elif kind == 'bishop' or kind == 'rook':
        stop_short = (kind == 'bishop')
        capture = (kind == 'rook')
        moves += symmscan(x, y, 1, 0, posn, capture=capture, stop_short=stop_short)
        if kind == 'bishop':
            stop_short = False
            capture = True
            moves += symmscan(x, y, 1, 1, posn, capture=capture, stop_short=stop_short)
    elif kind == 'knight':
        moves += symmscan(x, y, 2, 1, posn, stop_short=True)
        moves += symmscan(x, y, 2, -1, posn, stop_short=True)
    elif kind == 'pawn':
        d = 1
        if posn.piece_color(x, y) == 'W':
            d = -1
        moves += movescan(x, y, d, -1, posn, capture=Capture.ONLY, stop_short=True)
        moves += movescan(x, y, d, 1, posn, capture=Capture.ONLY, stop_short=True)
        moves += movescan(x, y, d, 0, posn, capture=False, stop_short=True)
    return moves


def find_moves(posn):
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

