import sys
import random as r
import move_gen
from time import time

NROWS = 6
NCOLS = 5

FILES_TO_INT = {
    'a': 0,
    'b': 1,
    'c': 2,
    'd': 3,
    'e': 4
}

INT_TO_FILES = {
    0: 'a',
    1: 'b',
    2: 'c',
    3: 'd',
    4: 'e'
}

MAX_SCORE = 100000
MIN_SCORE = -100000


def flip_color(current):
    if current == 'W':
        return 'B'
    return 'W'


'''
Decode a string representing a move in standard chess format into a Move object.
'''
# XXX this might need to check whether the to Square has a king, so it can set a win
def decode(move):
    frm = Square(abs(int(move[1]) - NROWS), FILES_TO_INT[move[0]])
    to = Square(abs(int(move[4]) - NROWS), FILES_TO_INT[move[3]])
    return Move(frm, to) 


class Undo(object):
    
    '''
    Tracks starting and ending square.
    @start_square (Square) Square moved from
    @end_square (Square) Square moved to
    @start_piece (char) Piece moving. Tracked in case of promotion.
    @end_square (char) Character at Square moved to. Tracked in case of capture.
    '''
    def __init__(self, board, move):
        self.startx = move.frm.x 
        self.starty = move.frm.y
        self.endx = move.to.x 
        self.endy = move.to.y 
        self.start_piece = board[move.frm.x][move.frm.y] 
        self.end_piece = board[move.to.x][move.to.y] 


class Posn:

    def __init__(self, color):
        self.board = self.make_starting_board()
        self.color = color 
        self.on_move = 'W'
        self.ply = 0
        self.w_pieces = ['K', 'Q', 'B', 'N', 'R', 'P', 'P', 'P', 'P', 'P']
        self.b_pieces = ['k', 'q', 'b', 'n', 'r', 'p', 'p', 'p', 'p', 'p']
        self.prunes = 0



    '''
    Determines color of piece at square. Square must hold a piece.
    '''
    def piece_color(self, x, y):
        assert(self.board[x][y] != '.')
        if str.islower(self.board[x][y]):
            return 'B'
        return 'W'


    '''
    Determines kind of piece at square. Square must hold a piece.
    '''
    def kind(self, x, y):
        assert(self.board[x][y] != '.')
        if self.board[x][y] == 'k' or self.board[x][y] == 'K':
            return 'king'
        elif self.board[x][y] == 'q' or self.board[x][y] == 'Q':
            return 'queen'
        elif self.board[x][y] == 'b' or self.board[x][y] == 'B':
            return 'bishop'
        elif self.board[x][y] == 'n' or self.board[x][y] == 'N':
            return 'knight'
        elif self.board[x][y] == 'r' or self.board[x][y] == 'R':
            return 'rook'
        elif self.board[x][y] == 'p' or self.board[x][y] == 'P':
            return 'pawn'


    def make_starting_board(self):
        board = [['k', 'q', 'b', 'n', 'r'],
                 ['p', 'p', 'p', 'p', 'p'],
                 ['.', '.', '.', '.', '.'],
                 ['.', '.', '.', '.', '.'],
                 ['P', 'P', 'P', 'P', 'P'],
                 ['R', 'N', 'B', 'Q', 'K']]
        assert(len(board) == NROWS)
        assert(len(board[0]) == NCOLS)
        return board


    '''
    Builds a position string.
    '''
    def get_board(self):
        builder = self.on_move+ ' ' + str(self.ply // 2) + '\n'
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                builder += self.board[i][j]
            builder += '\n'
        return builder


    '''
    Set the board. Would require a list of lists as seen in make_starting_board.
    Board is automatically updated when make_move is called, so it is better to
    use that.
    '''
    def set_board(self, board):
        self.board = board


    # Prints the position 
    def print_board(self):
        print(self.get_board())


    # Requires Move object
    # XXX finish updating this
    def make_move(self, move):

        piece = self.board[move.frm.x][move.frm.y]
        assert(piece != '.')

        self.board[move.frm.x][move.frm.y] = '.'

        if self.board[move.to.x][move.to.y] != '.':
            if str.islower(self.board[move.to.x][move.to.y]):
                self.b_pieces.remove(self.board[move.to.x][move.to.y])
            elif str.isupper(self.board[move.to.x][move.to.y]):
                self.w_pieces.remove(self.board[move.to.x][move.to.y])

        self.board[move.to.x][move.to.y] = piece

        # Do promotion as needed after placing the piece
        self.do_promotion(move.to.x, move.to.y)

        self.on_move = flip_color(self.on_move)

        self.ply += 1


    def do_undo(self, undo):
        assert(undo is not None)
        assert(undo.start_piece != '.')
        # Replace pieces on board
        self.board[undo.startx][undo.starty] = undo.start_piece
        self.board[undo.endx][undo.endy] = undo.end_piece

        # Replace captured pieces in list
        if undo.end_piece != '.':
            if str.islower(undo.end_piece):
                self.b_pieces.append(undo.end_piece)
            else:
                self.w_pieces.append(undo.end_piece)
        
        # Revert promotion in list
        # XXX This needs testing real bad
        if undo.start_piece == 'p' or undo.start_piece == 'P':
            if undo.endx == 0:
                self.w_pieces.remove('Q')
                self.w_pieces.append('P')
            elif undo.endx == 5:
                self.b_pieces.remove('q')
                self.b_pieces.append('p')

        self.ply -= 1
        self.on_move = flip_color(self.on_move)


    def scored_moves(self, moves):
        scored_moves = []
        for move in moves:
            scored_moves.append((
                self.check_score_post_move(self.on_move, move.to.x, move.to.y),
                move))
        sorted_moves = sorted(scored_moves, key=lambda move: move[0])
        moves = []
        for move in sorted_moves:
            assert(self.board[move[1].frm.x][move[1].frm.y] != '.')
            moves.append(move[1])

        return moves 


    def check_win(self, x, y):
        if self.board[x][y] == 'k' or self.board[x][y] == 'K':
            return True
        return False


    def check_end(self):
        if 'k' not in self.b_pieces:
            return True
        elif 'K' not in self.w_pieces:
            return True
        elif self.ply // 2 == 40:
            return True

    
    def negamax_move(self, d, moves):
        scores = []
        for move in moves:
            undo = Undo(self.board, move)
            self.make_move(move)
            scores.append(-(self.negamax(d)))
            self.do_undo(undo)
        # m = max(scores)
        # indices = [i for i, j in enumerate(scores) if j == m]
        # move = moves[indices[r.randint(0, len(indices))-1]]
        # return move
        return moves[scores.index(max(scores)) ]


    def negamax(self, d):
        if self.check_end() or d <= 0:
            return self.compute_score(self.on_move)

        # Generate moves and score them
        moves = move_gen.find_moves(self)

        # Extract the first move arbitrarily
        move = moves.pop(0)

        # Make the move and do negamax search
        undo = Undo(self.board, move)
        self.make_move(move) # XXX better heuristic?
        val_prime = -(self.negamax(d-1))

        # Undo the move
        self.do_undo(undo)

        # For the rest of the moves, make the move, compare it to the
        # score found so far, and save the best of them.
        for move in moves:
            undo = Undo(self.board, move)
            self.make_move(move)
            val = -(self.negamax(d-1))
            val_prime = max(val_prime, val)
            self.do_undo(undo)

        return val_prime


    def alpha_beta_move(self, d, moves):
        scores = []
        alpha = MAX_SCORE 
        for move in moves:
            self.prunes = 0
            undo = Undo(self.board, move)
            self.make_move(move)
            score = -(self.alpha_beta(d, -alpha, MAX_SCORE)) 
            alpha = max(score, alpha)
            scores.append(score)
            self.do_undo(undo)
        return moves[scores.index(max(scores)) ]


    def alpha_beta(self, d, alpha, beta):
        if self.check_end() or d <= 0:
            return self.compute_score(self.on_move)

        # Generate moves and score them
        moves = move_gen.find_moves(self)

        # Extract the first move arbitrarily
        move = moves.pop(0)

        # Make the move and do negamax search
        undo = Undo(self.board, move)
        self.make_move(move) # XXX better heuristic?
        val_prime = -(self.alpha_beta(d-1, -beta, -alpha))

        # Undo the move
        self.do_undo(undo)
        
        if val_prime > beta:
            self.prunes += 1
            return val_prime

        alpha = max(alpha, val_prime)
        for move in moves:
            undo = Undo(self.board, move)
            self.make_move(move)
            val = -(self.alpha_beta(d-1, -beta, -alpha))
            self.do_undo(undo)
            if val >= beta:
                self.prunes += 1
                return val
            val_prime = max(val_prime, val)
            alpha = max(alpha, val)
        return val_prime


    def id(self, limit, moves):
        start = time()
        d = 1
        scores = []
        for move in moves:
            undo = Undo(self.board, move)
            self.make_move(move)
            scores.append(-(self.alpha_beta(d, -12500, 12500)))
            self.do_undo(undo)
        curr_move = moves[scores.index(max(scores)) ]
        while d < 40:
            d += 1
            scores = []
            for move in moves:
                self.prunes = 0
                if time() - start > limit:
                    # print(str(self.ply // 2) + ' ' + str(d) + ', ', file=sys.stderr)
                    return curr_move
                undo = Undo(self.board, move)
                self.make_move(move)

                if move.win is True:
                    self.do_undo(undo)
                    return move

                # Check for loss
                if self.on_move == 'W' and 'K' not in self.w_pieces:
                    self.do_undo(undo)
                    return curr_move
                elif self.on_move == 'B' and 'k' not in self.b_pieces:
                    self.do_undo(undo)
                    return curr_move 

                scores.append(-(self.alpha_beta(d, -12500, 12500)))
                self.do_undo(undo)
            curr_move = moves[scores.index(max(scores))]

        return curr_move


    '''
    Promotes a pawn to a queen and updates the respective piece list.
    '''
    def do_promotion(self, x, y):
        if self.on_move == 'W' and x == 0 and self.kind(x, y) == 'pawn':
            self.board[x][y] = 'Q'
            self.w_pieces.append('Q')
            for piece in self.w_pieces:
                if piece == 'P':
                    self.w_pieces.remove(piece)
                    break

        elif self.on_move == 'B' and x == (NROWS - 1) and self.kind(x, y) == 'pawn':
            self.board[x][y] = 'q'
            self.b_pieces.append('q')
            for piece in self.b_pieces:
                if piece == 'p':
                    self.b_pieces.remove(piece)
                    break


    '''
    Compute the score for the given color for the current position.
    '''
    def compute_score(self, color, w_pieces=None, b_pieces=None):
        if w_pieces is None:
            w_pieces = self.w_pieces
        if b_pieces is None:
            b_pieces = self.b_pieces

        w_score = 0
        b_score = 0
        for piece in w_pieces:
            if piece == 'K':
                w_score += 1500 
            if piece == 'Q':
                w_score += 900
            elif piece == 'B':
                w_score += 300
            elif piece == 'N':
                w_score += 400 
            elif piece == 'R':
                w_score += 500
            elif piece == 'P':
                w_score += 100

        for piece in b_pieces:
            if piece == 'k':
                b_score += 1500 
            if piece == 'q':
                b_score += 900
            elif piece == 'b':
                b_score += 300
            elif piece == 'n':
                b_score += 400 
            elif piece == 'r':
                b_score += 500
            elif piece == 'p':
                b_score += 100

        for i in range(NROWS):
            for j in range(NCOLS):
                if self.board[i][j] == '.':
                    continue
                elif color == 'W' and str.isupper(self.board[i][j]):
                    if i == 2 or i == 3:
                        w_score += 5
                    if j == 1 or j == 2 or j == 3:
                        w_score += 5
                    if self.board[i][j] == 'P':
                        w_score += self.pawn_formation(color, i, j)
                    # elif self.board[i][j] == 'K':
                    #     w_score += self.king_formation(color, i, j)
                elif color == 'B' and str.islower(self.board[i][j]):
                    if i == 2 or i == 3:
                        b_score += 5
                    if j == 1 or j == 2 or j == 3:
                        b_score += 5
                    if self.board[i][j] == 'p':
                        b_score += self.pawn_formation(color, i, j)
                    # elif self.board[i][j] == 'k':
                    #     b_score += self.king_formation(color, i, j)

        if color == 'W':
            return w_score - b_score

        return b_score - w_score


    '''
    Checks score after a given move.
    @x x-coord of square moving to.
    @y y-coord of square moving to.
    '''
    def check_score_post_move(self, color, x, y):
        piece = self.board[x][y]
        if piece == '.':
            return self.compute_score(color)

        if color == 'W':
            pieces = list(self.b_pieces)
            pieces.remove(piece)
            return self.compute_score(color, b_pieces=pieces)

        pieces = list(self.w_pieces)
        pieces.remove(piece)
        return self.compute_score(color, w_pieces=pieces)


    def pawn_formation(self, color, x, y):
        assert(self.board[x][y] == 'p' or self.board[x][y] == 'P')
        score = 0
        if color == 'W':
            score += (6 - x) * 50 
            if x == 0:
                score += 900
        else:
            score += x*50
            if x == 5:
                score += 900
        for i in (1, -1):
            for j in (1, -1):
                try:
                    if color == 'W' and self.board[x][y+j] == 'P':
                        score += 50 
                    elif color == 'W' and self.board[x+i][y+j] == 'P':
                        score += 25 
                    elif color == 'B' and self.board[x][y+j] == 'p':
                        score += 50 
                    elif color == 'B' and self.board[x+i][y+j] == 'p':
                        score += 25 
                except IndexError:
                    continue

        return score


    def king_formation(self, color, x, y):
        score = 0
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                try:
                    if color == 'W' and str.isupper(self.board[i][j]):
                        score += 10
                    elif color == 'B' and str.islower(self.board[i][j]):
                        score += 10
                except IndexError:
                    continue
        return score



'''
Uses an x and y coordinate to build a square.
Coordinates are tracked in array fashion, such that the following (slightly
unintuitive) positions correspond to the following pairs.
a1 = (5, 0)
a6 = (0, 0)
e1 = (5, 4)
e6 = (0, 4)
'''
class Square(object):

    def __init__(self, x, y):
        assert(x >= 0 and x < NROWS)
        assert(y >= 0 and y < NCOLS)
        self.x = x
        self.y = y

    def toStr(self):
        return INT_TO_FILES[self.y] + str(NROWS - self.x)


'''
A move is comprised of two squares, where the piece is moving from and where
the piece is moving to. It also tracks the win condition of kind capture, which
is set in movescan from move_gen.
'''
class Move(object):

    def __init__(self, frm, to):
        self.frm = frm 
        self.to = to
        self.win = False

    def toStr(self):
        return self.frm.toStr() + '-' + self.to.toStr()

