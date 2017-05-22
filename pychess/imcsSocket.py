import socket

ending = bytes('\r\n', 'utf-8')


class IMCSSocket:

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = 'imcs.svcs.cs.pdx.edu'
        self.port = 3589


    def connect(self):
        self.sock.connect((self.host, self.port))
        if self.sock.recv(100)[:3] != b'100':
            print('Could not connect to IMCS!')
            exit(1)


    def login(self, user, passwd):
        self.sock.send(b'me ' + bytes(user, 'utf-8') + b' ' + 
                bytes(passwd, 'utf-8') + ending)
        if self.sock.recv(100)[:3] != b'201':
            print('Could not login using these credentials!')
            self.sock.close()
            exit(1)


    def offer(self):
        # Offer to play as either color
        self.sock.send(b'offer ?\r\n')
        # Receive game offer boilerplate
        offer = self.sock.recv(100).decode('utf-8')
        if offer[:3] != '103':
            print('Could not offer game!')
            print(str(offer))
            self.sock.close()
            exit(1)
        builder = ''
        i = 4
        while offer[i] != ' ':
            builder += offer[i]
            i += 1
        print('Game ' + builder + ' offered!')
        
        # Return the color we'll be playing as
        print('Waiting for game acceptance...')
        color = self.sock.recv(1024)
        if color[:3] == b'105':
            self.sock.recv(1024)
            return 'W', builder
        elif color[:3] == b'106':
            return 'B', builder
        else:
            print('Error with game offer:')
            print(color)
            self.sock.close()
            exit(1)


    def accept(self, game):
       self.sock.send(b'accept ' + bytes(str(game), 'utf-8') + ending)
       color = self.sock.recv(1024)
       if color[:3] == b'105':
           # Get starting board state and ignore
           self.sock.recv(1024)
           return 'W'
       elif color[:3] == b'106':
           return 'B'
       else:
           print('Error accepting game offer:')
           print(color)
           self.sock.close()
           exit(1)


    def send_move(self, move):
        self.sock.send(bytes(move, 'utf-8') + ending)


    def recv_move(self):
        move = self.sock.recv(1024).decode('utf-8')
        print(move)
        # Sometimes moves are separated into a move and a board state packet
        if len(move) < 20:
            print(self.sock.recv(1024).decode('utf-8'))
        if move[:1] == '!':
            return move[2:7]
        elif move[:1] == '=':
            if move[4:8] == 'wins':
                return True 
            else:
                return True 
        elif move == '':
            print('Game over!')
            return True
        else:
            print('Unexcepted move format:')
            print(str(move))
            self.sock.close()
            exit(1)


    def close(self):
        self.sock.close()


