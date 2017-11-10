'''
Contains the various kinds of players.
'''

import random as r

import move_gen
import representation
from representation import Posn

class HumanPlayer(object):
    '''
    Object to represent a human player.
    '''
    def __init__(self, color):
        self.posn = Posn(color)


    def make_move(self):
        '''
        Get a move from input and execute it.
        '''
        move = representation.decode(input())
        self.posn.make_move(move)
        return move.toStr(), move.win


    def get_move(self, move):
        '''
        Update position representation with received move.
        '''
        move = representation.decode(move)
        self.posn.make_move(move)


class RandomPlayer(object):
    '''
    Player that chooses moves randomly.
    '''
    def __init__(self, color):
        self.posn = Posn(color)

    def make_move(self):
        '''
        Choose move randomly and execute it.
        '''
        moves = move_gen.find_moves(self.posn)
        move = moves[r.randint(0, len(moves))-1]
        self.posn.make_move(move)
        return move.toStr(), move.win


    def get_move(self, move):
        '''
        Update position representation with received move.
        '''
        move = representation.decode(move)
        self.posn.make_move(move)


class HeuristicPlayer(object):
    '''
    Player that chooses highest-scoring move.
    '''
    def __init__(self, color):
        self.posn = Posn(color)


    def make_move(self):
        '''
        Generate all moves and choose highest-scoring.
        '''
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
        '''
        Update position representation with received move.
        '''
        move = representation.decode(move)
        self.posn.make_move(move)


class NegamaxPlayer:
    '''
    Choose move based on negamax algorithm. Requires depth to search to.
    '''
    def __init__(self, color, depth):
        self.posn = Posn(color)
        self.depth = depth


    def make_move(self):
        '''
        Run negamax algorithm to choose move.
        '''
        moves = move_gen.find_moves(self.posn)
        move = self.posn.negamax_move(self.depth, moves)
        self.posn.make_move(move)
        return move.toStr(), move.win


    def get_move(self, move):
        '''
        Update position representation with received move.
        '''
        move = representation.decode(move)
        self.posn.make_move(move)


class AlphaBetaPlayer:
    '''
    Player that chooses move based on alpha-beta algorithm.
    '''
    def __init__(self, color, depth):
        self.posn = Posn(color)
        self.depth = depth


    def make_move(self):
        '''
        Run alpha-beta algorithm to choose move.
        '''
        moves = move_gen.find_moves(self.posn)
        move = self.posn.alpha_beta_move(self.depth, moves)
        self.posn.make_move(move)
        return move.toStr(), move.win


    def get_move(self, move):
        '''
        Update position representation with received move.
        '''
        move = representation.decode(move)
        self.posn.make_move(move)


class IDPlayer:
    '''
    Player that chooses move based on alpha-beta using iterative deepening.
    '''
    def __init__(self, color, limit):
        self.posn = Posn(color)
        self.use_adjustment = False
        if limit is None:
            self.use_adjustment = True
        self.limit = limit


    def make_move(self):
        '''
        Choose move using iteratively deepened alpha-beta.
        '''
        moves = move_gen.find_moves(self.posn)
        if self.use_adjustment is True:
            self.limit = self.determine_time()
        move = self.posn.iterative_deepening(self.limit, moves)
        self.posn.make_move(move)
        return move.toStr(), move.win


    def get_move(self, move):
        '''
        Update position representation with received move.
        '''
        move = representation.decode(move)
        self.posn.make_move(move)


    def determine_time(self):
        '''
        Adjust time spent doing iterative deepening depending on how long the
        game has lastest so far.
        '''
        if self.posn.ply // 2 < 5:
            return 1
        elif self.posn.ply // 2 < 10:
            return 2
        elif self.posn.ply // 2 < 35:
            return 10
        else:
            return 4
