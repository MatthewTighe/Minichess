import glob, os
import collections
import move_gen
import representation
from representation import Posn
from representation import Square
from representation import Move
from representation import decode 

# Test board printing
def do_board_init_test():
    board = Posn('W')
    assert(board.get_board() == 'W 0\nkqbnr\nppppp\n.....\n.....\nPPPPP\nRNBQK\n')


def do_rep_tests():
    s1 = Square(0, 0)
    assert(s1.toStr() == 'a6')
    s2 = Square(0, 4)
    assert(s2.toStr() == 'e6')
    s3 = Square(5, 0)
    assert(s3.toStr() == 'a1')
    s4 = Square(5, 4)
    assert(s4.toStr() == 'e1')

    m = Move(s3, s2)
    assert(m.toStr() == 'a1-e6')

    assert(m.toStr() == (s3.toStr() + '-' + s2.toStr()))

    board = Posn('W')
    assert(board.compute_score('W') == 0)
    assert(board.compute_score('B') == 0)
    assert(board.compute_score('W', w_pieces=[]) == representation.MIN_SCORE)
    assert(board.compute_score('B', b_pieces=[]) == representation.MIN_SCORE)
    assert(board.compute_score('B', w_pieces=[]) == representation.MAX_SCORE)
    assert(board.compute_score('W', b_pieces=[]) == representation.MAX_SCORE)
    assert(board.compute_score('W', w_pieces=['Q'], b_pieces=[]) == 900)

    # Check that scores are 900 if the opponents queen is captured.
    assert(board.check_score_post_move('W', 0, 1) == 900)
    assert(board.check_score_post_move('B', 5, 3) == 900)


def do_print_rep_tests():
    board = Posn('W')
    board.print_board()

    s1 = Square(0, 0)
    s2 = Square(0, 4)
    s3 = Square(5, 0)
    s4 = Square(5, 4)
    print(s1.toStr())
    print(s2.toStr())
    print(s3.toStr())
    print(s4.toStr())

    m1 = Move(s3, s2)
    print('encode ' + m1.toStr())
    m2 = decode(m1.toStr())
    print('decode ' + m2.toStr())
    assert(m1.toStr() == m2.toStr())


def do_test_moves():
    # Check pawn forward movement
    board = Posn('W')
    moves = move_gen.find_moves(board)

    # Do Bart's move checking
    ins = glob.glob('move-tests/*.in')
    for f in ins:
        with open(f) as i:
            lines = i.readlines()
        color = lines[0].split()[1]
        board = []
        for i in range(1, len(lines)):
            line = lines[i].strip()
            row = []
            for c in line:
                row.append(c)
            board.append(row)
        posn = Posn('W')
        posn.on_move= color
        posn.set_board(board)
        moves = move_gen.find_moves(posn)
        move_strs = []
        for move in moves:
            move_strs.append(move.toStr())
        with open(f[0:-2] + 'out') as o:
            lines = o.readlines()
        out = []
        for line in lines:
            out.append(line.strip())
        if collections.Counter(move_strs) != collections.Counter(out):
            print(f)
            print(posn.on_move)
            print(move_strs)
            print(out)
            print(set(move_strs) - set(out))
            posn.print_board()


def ab_neg_test():
    t1 = Posn('W')
    t2 = Posn('W')
    t1_moves = move_gen.find_moves(t1)
    t2_moves = move_gen.find_moves(t2)
    t1_move = t1.negamax_move(3, t1_moves)
    t2_move = t2.alpha_beta_move(3, t2_moves)
    print('t1 ' + t1_move.toStr() + ' t2 ' + t2_move.toStr())
    assert(t1_move.toStr() == t2_move.toStr())


def promotion_test():
    t1 = Posn('W')
    move = Move(Square(4, 0), Square(0, 1))
    assert(t1.w_pieces == ['K', 'Q', 'B', 'N', 'R', 'P', 'P', 'P', 'P', 'P'])
    undo = representation.Undo(t1.board, move)
    t1.make_move(move)
    assert(t1.w_pieces == ['K', 'Q', 'B', 'N', 'R', 'P', 'P', 'P', 'P', 'Q'])
    t1.do_undo(undo)
    assert(t1.w_pieces == ['K', 'B', 'N', 'R', 'P', 'P', 'P', 'P', 'Q', 'P'])

    t2 = Posn('B')
    t2.on_move = 'B'
    move = Move(Square(1, 0), Square(5, 1))
    assert(t2.b_pieces == ['k', 'q', 'b', 'n', 'r', 'p', 'p', 'p', 'p', 'p'])
    undo = representation.Undo(t2.board, move)
    t2.make_move(move)
    assert(t2.b_pieces == ['k', 'q', 'b', 'n', 'r', 'p', 'p', 'p', 'p', 'q'])
    t2.do_undo(undo)
    assert(t2.b_pieces == ['k', 'b', 'n', 'r', 'p', 'p', 'p', 'p', 'q', 'p'])


do_board_init_test()
# do_rep_tests()
do_print_rep_tests()
do_test_moves()
ab_neg_test()
promotion_test()
