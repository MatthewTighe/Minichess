import socket
from players import IDPlayer

HOST = ''
PORT = 8080

AI_PLAYER = IDPlayer('B', 7)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind((HOST, PORT))
    sock.listen(1)
    sock.settimeout(10)
    while True:
        try:
            CONN, ADDR = sock.accept()
        except Exception as e:
            break
        DATA = CONN.recv(1024)
        if not DATA:
            break
        # TODO add more error checking for properly received move
        move = DATA.decode('utf-8')
        AI_PLAYER.get_move(move)
        print(AI_PLAYER.posn)
        AI_PLAYER.make_move()
        CONN.sendall(AI_PLAYER.posn.__str__().encode('utf-8'))
        print(AI_PLAYER.posn)
