import sys 
import socket
from util import *

HOST = 'localhost'
PORT = int(sys.argv[1])
dest_filename = sys.argv[2]
identifier = 'message'
byte_identifier = str.encode(identifier)


def client_handshake():
    pass

if len(sys.argv) != 3:
    print("Please fill in the port and the destination filename!")
else:
    client_socket = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client_socket.bind((HOST, PORT))
    segment = rdt_send(dest_filename, 1024, 0)

    client_socket.sendto(b'test', ('<broadcast>', 5002))

        