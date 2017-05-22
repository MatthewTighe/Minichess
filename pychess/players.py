import move_gen
import random as r
import representation
from representation import Posn

class HumanPlayer(object):
    
    def __init__(self, color):
        self.posn = Posn(color)

    
    def make_move(self):
        move = representation.decode(input())
        self.posn.make_move(move)
        return move.toStr(), move.win

    
    def get_move(self, move):
        move = representation.decode(move)
        self.posn.make_move(move)


class RandomPlayer(object):

    
    def __init__(self, color):
        self.posn = Posn(color)

    def make_move(self):
        moves = move_gen.find_moves(self.posn)
        move = moves[r.randint(0, len(moves))-1]
        self.posn.make_move(move)
        return move.toStr(), move.win


    def get_move(self, move):
        move = representation.decode(move)        
        self.posn.make_move(move)


class HeuristicPlayer(object):

    def __init__(self, color):
        self.posn = Posn(color)


    def make_move(self):
        moves = move_gen.find_moves(self.posn)
        scored_moves = []
        for move in moves:
            scored_moves.append(self.posn.check_score_post_move(
                self.posn.color, move.to.x, move.to.y))
        m = max(scored_moves)
        indices = [i for i, j in enumerate(scored_moves) if j == m]
        move = moves[indices[r.randint(0, len(indices))-1]]
        self.posn.make_move(move)
        return move.toStr(), move.win


    def get_move(self, move):
        move = representation.decode(move)
        self.posn.make_move(move)


class NegamaxPlayer:

    def __init__(self, color, depth):
        self.posn = Posn(color)
        self.depth = depth


    def make_move(self):
        moves = move_gen.find_moves(self.posn)
        move = self.posn.negamax_move(self.depth, moves)
        self.posn.make_move(move)
        return move.toStr(), move.win

    
    def get_move(self, move):
        move = representation.decode(move)
        self.posn.make_move(move)


class AlphaBetaPlayer:

    def __init__(self, color, depth):
        self.posn = Posn(color)
        self.depth = depth


    def make_move(self):
        moves = move_gen.find_moves(self.posn)
        move = self.posn.alpha_beta_move(self.depth, moves)
        self.posn.make_move(move)
        return move.toStr(), move.win


    def get_move(self, move):
        move = representation.decode(move)
        self.posn.make_move(move)


class IDPlayer:

    def __init__(self, color, limit):
        self.posn = Posn(color)
        self.use_adjustment = False
        if limit is None:
            self.use_adjustment = True
        self.limit = limit


    def make_move(self):
        moves = move_gen.find_moves(self.posn)
        if self.use_adjustment is True:
            self.limit = self.determine_time()
        move = self.posn.id(self.limit, moves)
        self.posn.make_move(move)
        return move.toStr(), move.win


    def get_move(self, move):
        move = representation.decode(move)
        self.posn.make_move(move)


    def determine_time(self):
        if self.posn.ply // 2 < 5:
            return 1
        elif self.posn.ply // 2 < 10:
            return 2
        elif self.posn.ply // 2 < 35:
            return 10
        else:
            return 4
