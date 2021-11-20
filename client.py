import sys 
import socket
from util import *

HOST = 'localhost'
PORT = int(sys.argv[1])
dest_filename = sys.argv[2]
identifier = 'message'
byte_identifier = str.encode(identifier)
STATE = ''


def client_handshake(socket, addr):
    seq_no = random_num()
    ack_no = 0

    message, _ = socket.recvfrom(1024)
    decoded_segment = message.decode()
    print(decoded_segment)
    if decoded_segment[65] == '1':
        STATE = constant.SYN_RECEIVED 
        ack_no = int(decoded_segment[0:32],2)

    if STATE == constant.SYN_RECEIVED:
        message = make_message_segment(seq_no, ack_no+1, syn=True, ack=True)
        print(message)
        socket.sendto(message.encode(), addr)
        STATE = constant.SYN_ACK_SENT 

    if STATE == constant.SYN_ACK_SENT:
        message, _ = socket.recvfrom(1024)
        decoded_segment = message.decode()
        ack_no = int(decoded_segment[32:64],2)
        if decoded_segment[67] == '1' and ack_no == seq_no + 1:
            STATE = constant.ESTABLISHED
        
    if STATE == constant.ESTABLISHED:
        return True
    
    return False

if len(sys.argv) != 3:
    print("Please fill in the port and the destination filename!")
else:
    client_socket = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client_socket.bind(('localhost', PORT))
    print(client_socket)

    conn = client_handshake(client_socket, ('localhost', 5000))
    if conn:
        print("connection established")

        