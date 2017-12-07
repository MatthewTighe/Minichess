import socket

HOST = ''
PORT = 8080
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind((HOST, PORT))
    sock.listen(1)
    CONN, ADDR = sock.accept()
    with CONN:
        print('Got a connection from :', ADDR)
        while True:
            DATA = CONN.recv(1024)
            if not DATA:
                break
            CONN.sendall(DATA)
