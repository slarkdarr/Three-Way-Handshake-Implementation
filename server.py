import sys
import socket

HOST = 'localhost'
PORT = int(sys.argv[1])
source_filename = sys.argv[2]


def server_handshake():
    pass


if len(sys.argv) != 3:
    print("Please fill in the port and the source filename!")
else:
    server_socket = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server_socket.bind(('localhost', PORT))
    print(server_socket)
    
    while(1):
        message = server_socket.recvfrom(1024)
        print(message[0])
        print(message[1])

