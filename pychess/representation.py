'''
XXX
'''
from time import time
import move_gen

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
    '''
    Switches color from white to black or vice versa.

    :param current: Color to be switched.
    :returns: Switched color.
    '''
    if current == 'W':
        return 'B'
    return 'W'



def decode(move):
    '''
    Decode a string representing a move in standard chess format into a Move object.

    :param move: String to be decoded.
    :returns: Move object representation of string.
    '''
    start = Square(abs(int(move[1]) - NROWS), FILES_TO_INT[move[0]])
    end = Square(abs(int(move[4]) - NROWS), FILES_TO_INT[move[3]])
    return Move(start, end)


class Undo:
    '''
    Tracks starting and ending square so that positions can be restored.

    :param start_square: (Square) Square moved from
    :param end_square: (Square) Square moved to
    :param start_piece: (char) Piece moving. Tracked in case of promotion.
    :param end_piece: (char) Character at Square moved to. Tracked in case of capture.
    '''
    def __init__(self, board, move):
        self.startx = move.frm.x
        self.starty = move.frm.y
        self.endx = move.to.x
        self.endy = move.to.y
        self.start_piece = board[move.frm.x][move.frm.y]
        self.end_piece = board[move.to.x][move.to.y]


class Posn:
    '''
    XXX
    '''
    def __init__(self, color):
        self.board = self.make_starting_board()
        self.color = color
        self.on_move = 'W'
        self.ply = 0
        self.w_pieces = ['K', 'Q', 'B', 'N', 'R', 'P', 'P', 'P', 'P', 'P']
        self.b_pieces = ['k', 'q', 'b', 'n', 'r', 'p', 'p', 'p', 'p', 'p']


    def piece_color(self, xpos, ypos):
        '''
        Determines color of piece at square. Square must hold a piece.

        :param xpos: x coordinate of piece.
        :param ypos: y coordinate of piece.
        :returns: Color of piece found at (x, y) of board.
        '''
        assert self.board[xpos][ypos] != '.'
        if str.islower(self.board[xpos][ypos]):
            return 'B'
        return 'W'


    def kind(self, xpos, ypos):
        '''
        Determines kind of piece at square. Square must hold a piece.

        :param xpos: x coordinate of piece.
        :param ypos: y coordinate of piece.
        :returns:  Piece type found at (x, y) of board.
        '''
        assert self.board[xpos][ypos] != '.'
        if self.board[xpos][ypos] == 'k' or self.board[xpos][ypos] == 'K':
            return 'king'
        elif self.board[xpos][ypos] == 'q' or self.board[xpos][ypos] == 'Q':
            return 'queen'
        elif self.board[xpos][ypos] == 'b' or self.board[xpos][ypos] == 'B':
            return 'bishop'
        elif self.board[xpos][ypos] == 'n' or self.board[xpos][ypos] == 'N':
            return 'knight'
        elif self.board[xpos][ypos] == 'r' or self.board[xpos][ypos] == 'R':
            return 'rook'
        elif self.board[xpos][ypos] == 'p' or self.board[xpos][ypos] == 'P':
            return 'pawn'


    def make_starting_board(self):
        '''
        Generate starting position of board.

        :returns: List of lists describing starting board position.
        '''
        board = [['k', 'q', 'b', 'n', 'r'],
                 ['p', 'p', 'p', 'p', 'p'],
                 ['.', '.', '.', '.', '.'],
                 ['.', '.', '.', '.', '.'],
                 ['P', 'P', 'P', 'P', 'P'],
                 ['R', 'N', 'B', 'Q', 'K']]
        assert len(board) == NROWS
        assert len(board[0]) == NCOLS
        return board


    def get_board(self):
        '''
        :returns: String representation of the board state.
        '''
        builder = self.on_move+ ' ' + str(self.ply // 2) + '\n'
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                builder += self.board[i][j]
            builder += '\n'
        return builder


    def set_board(self, board):
        '''
        Set the board. Currently only used for ease of testing.

        :board: List of lists containing board description, as in
                make_starting_board.
        '''
        self.board = board


    def print_board(self):
        '''Print the stringified representation of the board.'''
        print(self.get_board())


    def make_move(self, move):
        '''
        Update the board state based on a move, including moving the
        piece, promoting if necessary, changing active player, and increasing
        number of plies.

        :move: Move object describing move to be executed.
        '''
        piece = self.board[move.frm.x][move.frm.y]
        assert piece != '.'

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
        '''
        Return the board state to a previous position.

        :undo: Undo object containing information necessary for reversion.
        '''
        assert undo is not None
        assert undo.start_piece != '.'
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
        '''
        Score each move based on it's resulting board state.

        :moves: List of possible moves.
        '''
        scored_moves = []
        for move in moves:
            scored_moves.append((
                self.check_score_post_move(self.on_move, move.to.x, move.to.y),
                move))
        sorted_moves = sorted(scored_moves, key=lambda move: move[0])
        moves = []
        for move in sorted_moves:
            assert self.board[move[1].frm.x][move[1].frm.y] != '.'
            moves.append(move[1])

        return moves


    def check_win(self, xpos, ypos):
        '''
        Check if the new position is a win for either side.

        :xpos: xpos coordinate of position
        :ypos: ypos coordinate of position
        :returns: Boolean indicating if game is won.
        '''
        if self.board[xpos][ypos] == 'k' or self.board[xpos][ypos] == 'K':
            return True
        return False


    def check_end(self):
        '''
        Check if the game has ended by determining if a king has been captured
        of if the ply limit has been reach.

        :returns: Boolean indicating if game is over.
        '''
        if 'k' not in self.b_pieces:
            return True
        elif 'K' not in self.w_pieces:
            return True
        elif self.ply // 2 == 40:
            return True


    def negamax_move(self, depth, moves):
        '''
        Determine move using negamax algorithm.

        :depth: Integer depth to execute search to.
        :moves: List of possible moves.

        :returns: Move object containing "best" move.
        '''
        scores = []
        for move in moves:
            undo = Undo(self.board, move)
            self.make_move(move)
            scores.append(-(self.negamax(depth)))
            self.do_undo(undo)
        # m = max(scores)
        # indices = [i for i, j in enumerate(scores) if j == m]
        # move = moves[indices[r.randint(0, len(indices))-1]]
        # return move
        return moves[scores.index(max(scores))]


    def __negamax(self, depth):
        '''
        XXX
        '''
        if self.check_end() or depth <= 0:
            return self.compute_score(self.on_move)

        # Generate moves and score them
        moves = move_gen.find_moves(self)

        # Extract the first move arbitrarily
        move = moves.pop(0)

        # Make the move and do negamax search
        undo = Undo(self.board, move)
        self.make_move(move)
        val_prime = -(self.negamax(depth-1))

        # Undo the move
        self.do_undo(undo)

        # For the rest of the moves, make the move, compare it to the
        # score found so far, and save the best of them.
        for move in moves:
            undo = Undo(self.board, move)
            self.make_move(move)
            val = -(self.negamax(depth-1))
            val_prime = max(val_prime, val)
            self.do_undo(undo)

        return val_prime


    def alpha_beta_move(self, depth, moves):
        '''
        XXX
        '''
        scores = []
        alpha = MAX_SCORE
        for move in moves:
            undo = Undo(self.board, move)
            self.make_move(move)
            score = -(self.alpha_beta(depth, -alpha, MAX_SCORE))
            alpha = max(score, alpha)
            scores.append(score)
            self.do_undo(undo)
        return moves[scores.index(max(scores))]


    def __alpha_beta(self, depth, alpha, beta):
        '''
        XXX
        '''
        if self.check_end() or depth <= 0:
            return self.compute_score(self.on_move)

        # Generate moves and score them
        moves = move_gen.find_moves(self)

        # Extract the first move arbitrarily
        move = moves.pop(0)

        # Make the move and do negamax search
        undo = Undo(self.board, move)
        self.make_move(move)
        val_prime = -(self.alpha_beta(depth-1, -beta, -alpha))

        # Undo the move
        self.do_undo(undo)

        if val_prime > beta:
            return val_prime

        alpha = max(alpha, val_prime)
        for move in moves:
            undo = Undo(self.board, move)
            self.make_move(move)
            val = -(self.alpha_beta(depth-1, -beta, -alpha))
            self.do_undo(undo)
            if val >= beta:
                return val
            val_prime = max(val_prime, val)
            alpha = max(alpha, val)
        return val_prime


    def iterative_deepening(self, limit, moves):
        '''
        XXX
        '''
        start = time()
        depth = 1
        scores = []
        for move in moves:
            undo = Undo(self.board, move)
            self.make_move(move)
            scores.append(-(self.alpha_beta(depth, -12500, 12500)))
            self.do_undo(undo)
        curr_move = moves[scores.index(max(scores))]
        while depth < 40:
            depth += 1
            scores = []
            for move in moves:
                if time() - start > limit:
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

                scores.append(-(self.alpha_beta(depth, -12500, 12500)))
                self.do_undo(undo)
            curr_move = moves[scores.index(max(scores))]

        return curr_move



    def do_promotion(self, xpos, ypos):
        '''
        Promotes a pawn to a queen and updates the respective piece list.

        :param xpos: x coordinate of pawn.
        :param ypos: y coordinate of pawn.
        '''
        if self.on_move == 'W' and xpos == 0 and self.kind(xpos, ypos) == 'pawn':
            self.board[xpos][ypos] = 'Q'
            self.w_pieces.append('Q')
            for piece in self.w_pieces:
                if piece == 'P':
                    self.w_pieces.remove(piece)
                    break

        elif self.on_move == 'B' and xpos == (NROWS - 1) and self.kind(xpos, ypos) == 'pawn':
            self.board[xpos][ypos] = 'q'
            self.b_pieces.append('q')
            for piece in self.b_pieces:
                if piece == 'p':
                    self.b_pieces.remove(piece)
                    break


    def compute_score(self, color, w_pieces=None, b_pieces=None):
        '''
        Compute the score for the given color for the current position.
        '''
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



    def check_score_post_move(self, color, xpos, ypos):
        '''
        Checks score after a given move.
        :param xpos: x-coord of square moving to.
        :param ypos: y-coord of square moving to.

        :returns: Score found after piece is removed.
        XXX
        '''
        piece = self.board[xpos][ypos]
        if piece == '.':
            return self.compute_score(color)

        if color == 'W':
            pieces = list(self.b_pieces)
            pieces.remove(piece)
            return self.compute_score(color, b_pieces=pieces)

        pieces = list(self.w_pieces)
        pieces.remove(piece)
        return self.compute_score(color, w_pieces=pieces)


    def pawn_formation(self, color, xpos, ypos):
        '''
        Calculate pawn heuristic score. Increases for adjacent friendly pawns
        and for pawn advancement.

        :param color: Color on move.
        :param xpos: x coordinate of pawn to check formation of.
        :param ypos: y coordinate of pawn to check formation of.
        :returns: Heuristic score of pawn formation.
        '''

        assert self.board[xpos][ypos] == 'p' or self.board[xpos][ypos] == 'P'
        score = 0
        if color == 'W':
            score += (6 - xpos) * 50
            if xpos == 0:
                score += 900
        else:
            score += xpos*50
            if xpos == 5:
                score += 900
        for i in (1, -1):
            for j in (1, -1):
                try:
                    if color == 'W' and self.board[xpos][ypos+j] == 'P':
                        score += 50
                    elif color == 'W' and self.board[xpos+i][ypos+j] == 'P':
                        score += 25
                    elif color == 'B' and self.board[xpos][ypos+j] == 'p':
                        score += 50
                    elif color == 'B' and self.board[xpos+i][ypos+j] == 'p':
                        score += 25
                except IndexError:
                    continue

        return score


    def king_formation(self, color, xpos, ypos):
        '''
        Heuristic score that increases proportionally to the number of
        friendly pieces surrounding the king.

        :param color: Color on move.
        :param xpos: x coordinate of the king.
        :param ypos: y coordinate of the king.
        :returns: Heuristic score.
        '''
        score = 0
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                try:
                    if color == 'W' and str.isupper(self.board[xpos + i][ypos + j]):
                        score += 10
                    elif color == 'B' and str.islower(self.board[xpos + i][ypos + j]):
                        score += 10
                except IndexError:
                    continue
        return score




class Square:
    '''
    Uses an x and y coordinate to build a square.
    Coordinates are tracked in array fashion, such that the following (slightly
    unintuitive) positions correspond to the following pairs.
    a1 = (5, 0)
    a6 = (0, 0)
    e1 = (5, 4)
    e6 = (0, 4)
    '''
    def __init__(self, xpos, ypos):
        assert xpos >= 0 and xpos < NROWS
        assert ypos >= 0 and ypos < NCOLS
        self.xpos = xpos
        self.ypos = ypos

    def to_str(self):
        ''':returns: Strified version of a square.'''
        return INT_TO_FILES[self.yps] + str(NROWS - self.xpos)



class Move:
    '''
    A move is comprised of two squares, where the piece is moving from and where
    the piece is moving to. It also tracks the win condition of kind capture, which
    is set in movescan from move_gen.
    '''
    def __init__(self, start_square, end_square):
        self.start_square = start_square
        self.end_square = end_square
        self.win = False

    def to_str(self):
        ''':returns: Stringified version of move.'''
        return self.start_square.to_str() + '-' + self.end_square.to_str()
