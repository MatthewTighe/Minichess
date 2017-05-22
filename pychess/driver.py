import sys, getopt
import socket

from players import HumanPlayer
from players import RandomPlayer
from players import HeuristicPlayer
from players import NegamaxPlayer
from players import AlphaBetaPlayer
from players import IDPlayer

from imcsSocket import IMCSSocket

def play_local(p1_type, p2_type, p1_depth, p2_depth):
    if p1_type == 'random':
        p1 = RandomPlayer('W')
    elif p1_type == 'heuristic':
        p1 = HeuristicPlayer('W')
    elif p1_type == 'human':
        p1 = HumanPlayer('W')
    elif p1_type == 'negamax':
        p1 = NegamaxPlayer('W', p1_depth)
    elif p1_type == 'ab':
        p1 = AlphaBetaPlayer('W', p1_depth)
    elif p1_type == 'id':
        p1 = IDPlayer('W', p1_depth)

    if p2_type == 'random':
        p2 = RandomPlayer('B')
    elif p2_type == 'heuristic':
        p2 = HeuristicPlayer('B')
    elif p2_type == 'human':
        p2 = HumanPlayer('B')
    elif p2_type == 'negamax':
        p2 = NegamaxPlayer('B', p2_depth)
    elif p2_type == 'ab':
        p2 = AlphaBetaPlayer('B', p2_depth)
    elif p2_type == 'id':
        p2 = IDPlayer('B', p2_depth)

    p1.posn.print_board()
    while p1.posn.ply // 2 < 40:
        move, win = p1.make_move()
        print(move)
        p1.posn.print_board()
        if win is True:
            exit(0)

        p2.get_move(move)
        move, win = p2.make_move()
        print(move)
        p2.posn.print_board()
        if win is True:
            exit(0)

        p1.get_move(move)


def play_online(user, passwd, game_number):
    s = IMCSSocket()
    s.connect()
    s.login(user, passwd)
    if game_number is None:
        color, game_number = s.offer()
    else:
        color = s.accept(game_number)

    player = AlphaBetaPlayer(color, 6)
    if color == 'B':
        move = s.recv_move()
        player.get_move(move)

    while True: 
        move, win = player.make_move()
        player.posn.print_board()
        print(move)
        s.send_move(move)
        if win is True:
            s.close()
            break
        move = s.recv_move()
        if move is True:
            s.close()
            break
        player.get_move(move)


def print_help():
    print('usage: python3 driver.py -1 <type> -2 <type>')
    print('usage: python3 driver.py -u <user> -p <password> -a <number>') 
    print('usage: python3 driver.py --p1_type=<type> --p2_type=<type>')
    print('<type>s usage: human random heuristic negamax<depth> ab<depth> id<time>')
    print('<depth> usage: integer (2 <= x)')
    print('<time> usage: number for time limit of move')
    print('-1: player 1 type. Offline play.')
    print('-2: player 2 type. Offline play.')
    print('-u: IMCS user name. Default small314')
    print('-p: IMCS password. Required for online play.')
    print('-o: Offer game. Default behavior.')
    print('-a: Accept game <number>')


def main(argv):
    p1_type = ''
    p2_type = ''
    user = 'small314'
    passwd = None
    game_number = None
    try:
        opts, args = getopt.getopt(argv, 'h1:2:u:p:oa:', 
                ['p1_type', 'p2_type'])
    except getopt.GetoptError as e:
        print(e)
        print_help()
        exit(2)

    p1_depth = p2_depth = 0
    for opt, arg in opts:
        if opt == '-h':
            print_help()
            exit(0)
        elif opt in ('-1', '--p1_type'):
            p1_type = arg
            if p1_type[-1:].isdigit():
                parse = p1_type.split(':')
                p1_type = parse[0]
                p1_depth = int(parse[1])
        elif opt in ('-2', '--p2_type'):
            p2_type = arg
            if p2_type[-1:].isdigit():
                parse = p2_type.split(':')
                p2_type = parse[0]
                p2_depth = int(parse[1])
        elif opt == '-u':
            user = arg
        elif opt == '-p':
            passwd = arg
        elif opt == '-a':
            game_number = arg

    if passwd is None:
        play_local(p1_type, p2_type, p1_depth, p2_depth)
    elif passwd is not None:
        play_online(user, passwd, game_number)
    else:
        print_help()
        exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])

