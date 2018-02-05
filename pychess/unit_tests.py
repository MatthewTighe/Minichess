'''
Tests for pychess.
'''

import glob
import collections
import move_gen
import representation
from representation import Posn
from representation import Square
from representation import Move
from representation import decode

def run_tests():
    '''Run all tests.'''
    do_rep_tests()
    do_print_rep_tests()
    do_test_moves()
    ab_neg_test()
    promotion_test()


def do_rep_tests():
    ''' Test various state representation fundamentals. '''
    # Test square translation.
    test_square1 = Square(0, 0)
    assert test_square1.to_str() == 'a6'
    test_square2 = Square(0, 4)
    assert test_square2.to_str() == 'e6'
    test_square3 = Square(5, 0)
    assert test_square3.to_str() == 'a1'
    test_square4 = Square(5, 4)
    assert test_square4.to_str() == 'e1'

    # Test move translation and ensure move and square translation are equal.
    test_move = Move(test_square3, test_square2)
    assert test_move.to_str() == 'a1-e6'

    assert test_move.to_str() == (test_square3.to_str() + '-' + test_square2.to_str())


def do_print_rep_tests():
    ''' Test representation printing. '''
    board = Posn('W')
    print(board)

    test_square1 = Square(0, 0)
    test_square2 = Square(0, 4)
    test_square3 = Square(5, 0)
    test_square4 = Square(5, 4)
    print(test_square1.to_str())
    print(test_square2.to_str())
    print(test_square3.to_str())
    print(test_square4.to_str())

    test_move1 = Move(test_square3, test_square2)
    print('encode ' + test_move1.to_str())
    test_move2 = decode(test_move1.to_str())
    print('decode ' + test_move2.to_str())
    assert test_move1.to_str() == test_move2.to_str()


def do_test_moves():
    ''' Test piece movement. '''
    # Check pawn forward movement
    board = Posn('W')
    moves = move_gen.find_moves(board)

    # Do Bart's move checking
    ins = glob.glob('move-tests/*.in')
    for filename in ins:
        with open(filename) as i:
            lines = i.readlines()
        color = lines[0].split()[1]
        board = []
        for i in range(1, len(lines)):
            line = lines[i].strip()
            row = []
            for char in line:
                row.append(char)
            board.append(row)
        posn = Posn('W')
        posn.on_move = color
        posn.set_board(board)
        moves = move_gen.find_moves(posn)
        move_strs = []
        for move in moves:
            move_strs.append(move.to_str())
        with open(filename[0:-2] + 'out') as out:
            lines = out.readlines()
        output = []
        for line in lines:
            output.append(line.strip())
        if collections.Counter(move_strs) != collections.Counter(output):
            print(filename)
            print(posn.on_move)
            print(move_strs)
            print(output)
            print(set(move_strs) - set(output))
            print(posn)


def ab_neg_test():
    ''' Test that alpha-beta and negamax arrive at the same move '''
    test_posn1 = Posn('W')
    test_posn2 = Posn('W')
    test_moves1 = move_gen.find_moves(test_posn1)
    test_moves2 = move_gen.find_moves(test_posn2)
    test_move1 = test_posn1.negamax_move(3, test_moves1)
    test_move2 = test_posn2.alpha_beta_move(3, test_moves2)
    print('negamax move: ' + test_move1.to_str() + ' alpha-beta move: ' + test_move2.to_str())
    assert test_move1.to_str() == test_move2.to_str()


def promotion_test():
    test_posn1 = Posn('W')
    move = Move(Square(4, 0), Square(0, 1))
    assert test_posn1.w_pieces == ['K', 'Q', 'B', 'N', 'R', 'P', 'P', 'P', 'P', 'P']
    undo = representation.Undo(test_posn1.board, move)
    test_posn1.make_move(move)
    assert test_posn1.w_pieces == ['K', 'Q', 'B', 'N', 'R', 'P', 'P', 'P', 'P', 'Q']
    test_posn1.do_undo(undo)
    assert test_posn1.w_pieces == ['K', 'B', 'N', 'R', 'P', 'P', 'P', 'P', 'Q', 'P']

    test_posn2 = Posn('B')
    test_posn2.on_move = 'B'
    move = Move(Square(1, 0), Square(5, 1))
    assert test_posn2.b_pieces == ['k', 'q', 'b', 'n', 'r', 'p', 'p', 'p', 'p', 'p']
    undo = representation.Undo(test_posn2.board, move)
    test_posn2.make_move(move)
    assert test_posn2.b_pieces == ['k', 'q', 'b', 'n', 'r', 'p', 'p', 'p', 'p', 'q']
    test_posn2.do_undo(undo)
    assert test_posn2.b_pieces == ['k', 'b', 'n', 'r', 'p', 'p', 'p', 'p', 'q', 'p']

if __name__ == '__main__':
    run_tests()
