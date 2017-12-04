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

MAX_SCORE = 10000
MIN_SCORE = -10000


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
        return INT_TO_FILES[self.ypos] + str(NROWS - self.xpos)


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


class Undo:
    '''
    Tracks starting and ending square so that positions can be restored.

    :param start_square: (Square) Square moved from
    :param end_square: (Square) Square moved to
    :param start_piece: (char) Piece moving. Tracked in case of promotion.
    :param end_piece: (char) Character at Square moved to. Tracked in case of capture.
    '''
    def __init__(self, board, move):
        self.startx = move.start_square.xpos
        self.starty = move.start_square.ypos
        self.endx = move.end_square.xpos
        self.endy = move.end_square.ypos
        self.start_piece = board[move.start_square.xpos][move.start_square.ypos]
        self.end_piece = board[move.end_square.xpos][move.end_square.ypos]


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


    def __str__(self):
        '''
        :returns: String representation of the board state.
        '''
        builder = self.on_move+ ' ' + str(self.ply // 2) + '\n'
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                builder += self.board[i][j]
            builder += '\n'
        return builder


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


    def set_board(self, board):
        '''
        Set the board. Currently only used for ease of testing.

        :board: List of lists containing board description, as in
                make_starting_board.
        '''
        self.board = board


    def make_move(self, move):
        '''
        Update the board state based on a move, including moving the
        piece, promoting if necessary, changing active player, and increasing
        number of plies.

        :move: Move object describing move to be executed.
        '''
        piece = self.board[move.start_square.xpos][move.start_square.ypos]
        assert piece != '.'

        # Empty the square the piece is moving from.
        self.board[move.start_square.xpos][move.start_square.ypos] = '.'

        captured = self.board[move.end_square.xpos][move.end_square.ypos]
        if captured != '.':
            if captured.upper() == 'K':
                move.win = True

            # Remove the captured piece from the appropriate piece list.
            if str.islower(captured):
                self.b_pieces.remove(captured)
            else:
                self.w_pieces.remove(captured)

        # Place the piece in the square it is moving to.
        self.board[move.end_square.xpos][move.end_square.ypos] = piece

        # Do promotion as needed after placing the piece
        self.do_promotion(move.end_square.xpos, move.end_square.ypos)

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

        if undo.end_piece != '.':
            # Replace captured pieces in list
            if str.islower(undo.end_piece):
                self.b_pieces.append(undo.end_piece)
            else:
                self.w_pieces.append(undo.end_piece)

        if undo.start_piece.upper() == 'P':
            # Revert promotion in list
            if undo.endx == 0:
                self.w_pieces.remove('Q')
                self.w_pieces.append('P')
            elif undo.endx == 5:
                self.b_pieces.remove('q')
                self.b_pieces.append('p')

        self.on_move = flip_color(self.on_move)
        self.ply -= 1


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
        return False


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
            scores.append(-(self.__negamax(depth - 1)))
            self.do_undo(undo)
        return moves[scores.index(max(scores))]


    def __negamax(self, depth):
        '''
        XXX
        '''
        if self.check_end() or depth <= 0:
            return self.compute_score()

        # Generate moves and score them
        moves = move_gen.find_moves(self)

        max_score = MIN_SCORE

        # For the rest of the moves, make the move, compare it to the
        # score found so far, and save the best of them.
        for move in moves:
            undo = Undo(self.board, move)
            self.make_move(move)
            val = -(self.__negamax(depth - 1))
            max_score = max(max_score, val)
            self.do_undo(undo)

        return max_score


    def alpha_beta_move(self, depth, moves):
        '''
        XXX
        '''
        scores = []
        alpha = MAX_SCORE
        for move in moves:
            undo = Undo(self.board, move)
            self.make_move(move)
            score = -(self.__alpha_beta(depth - 1, -alpha, MAX_SCORE))
            alpha = max(score, alpha)
            scores.append(score)
            self.do_undo(undo)
        return moves[scores.index(max(scores))]


    def __alpha_beta(self, depth, alpha, beta):
        '''
        XXX
        '''
        if self.check_end() or depth <= 0:
            return self.compute_score()

        # Generate moves and score them
        moves = move_gen.find_moves(self)

        # Extract the first move arbitrarily
        move = moves.pop()

        # Make the move and do negamax search
        undo = Undo(self.board, move)
        self.make_move(move)
        max_score = -(self.__alpha_beta(depth - 1, -beta, -alpha))

        # Undo the move
        self.do_undo(undo)

        if max_score >= beta:
            return max_score

        alpha = max(alpha, max_score)
        for move in moves:
            undo = Undo(self.board, move)
            self.make_move(move)
            val = -(self.__alpha_beta(depth - 1, -beta, -alpha))
            self.do_undo(undo)
            if val >= beta:
                return val
            max_score = max(max_score, val)
            alpha = max(alpha, val)
        return max_score


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
            scores.append(-(self.__alpha_beta(depth, MIN_SCORE, MAX_SCORE)))
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

                scores.append(-(self.__alpha_beta(depth, MIN_SCORE, MAX_SCORE)))
                self.do_undo(undo)

            curr_move = moves[scores.index(max(scores))]
        return curr_move


    def do_promotion(self, xpos, ypos):
        '''
        Promotes a pawn to a queen and updates the respective piece list.

        :param xpos: x coordinate of pawn.
        :param ypos: y coordinate of pawn.
        '''
        if self.on_move == 'W' \
        and xpos == 0 \
        and self.board[xpos][ypos] == 'P':
            self.board[xpos][ypos] = 'Q'
            self.w_pieces.append('Q')
            self.w_pieces.remove('P')

        elif self.on_move == 'B' \
        and xpos == (NROWS - 1) \
        and self.board[xpos][ypos] == 'p':
            self.board[xpos][ypos] = 'q'
            self.b_pieces.append('q')
            self.b_pieces.remove('p')


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


    def compute_score(self):
        '''
        Compute the score for the given color for the current position.
        '''
        w_score = 0
        b_score = 0
        for i in range(NROWS):
            for j in range(NCOLS):
                piece = self.board[i][j]
                if piece == '.':
                    continue
                if str.isupper(piece):
                    w_score += self.center_control(i, j)
                    if piece == 'K':
                        w_score += 10000
                        w_score += self.king_formation(i, j, 'W')
                    elif piece == 'Q':
                        w_score += 900
                    elif piece == 'B':
                        w_score += 300
                    elif piece == 'N':
                        w_score += 400
                    elif piece == 'R':
                        w_score += 500
                    else:
                        w_score += 100
                        w_score += self.pawn_formation(i, j, 'P')
                else:
                    b_score += self.center_control(i, j)
                    if piece == 'k':
                        b_score += 10000
                        b_score += self.king_formation(i, j, 'B')
                    elif piece == 'q':
                        b_score += 900
                    elif piece == 'b':
                        b_score += 300
                    elif piece == 'n':
                        b_score += 400
                    elif piece == 'r':
                        b_score += 500
                    else:
                        b_score += 100
                        b_score += self.pawn_formation(i, j, 'p')

        if self.on_move == 'W':
            return w_score - b_score
        else:
            return b_score - w_score


    def center_control(self, xpos, ypos):
        '''
        Heuristic that increases score based on how close to the center a piece
        is.

        :param xpos: x-coord of square to check.
        :param ypos: x-coord of square to check.
        :returns: score of position
        '''
        score = 0
        if xpos == 2 or xpos == 3:
            score += 20
        if ypos == 3:
            score += 50
        if ypos == 2:
            score += 20
        return score

    def pawn_formation(self, xpos, ypos, pawn_type):
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
        if pawn_type == 'P':
            score += (6 - xpos) * 50
        else:
            score += xpos*50
        for i in (1, -1):
            for j in (1, -1):
                try:
                    if pawn_type == 'P' and self.board[xpos][ypos+j] == 'P':
                        score += 50
                    elif pawn_type == 'P' and self.board[xpos+i][ypos+j] == 'P':
                        score += 25
                    elif pawn_type == 'p' and self.board[xpos][ypos+j] == 'p':
                        score += 50
                    elif pawn_type == 'p' and self.board[xpos+i][ypos+j] == 'p':
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
                        score += 15
                    elif color == 'B' and str.islower(self.board[xpos + i][ypos + j]):
                        score += 15
                except IndexError:
                    continue
        return score


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
            return self.compute_score()

        if color == 'W':
            pieces = list(self.b_pieces)
            pieces.remove(piece)
            return self.compute_score()

        pieces = list(self.w_pieces)
        pieces.remove(piece)
        return self.compute_score()
