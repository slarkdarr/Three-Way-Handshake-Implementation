import sys
import socket
from util import *
import constant

HOST = 'localhost'
PORT = int(sys.argv[1])
source_filename = sys.argv[2]
STATE = ''

def server_handshake(socket, addr):
    seq_no = random_num()
    ack_no = 0

    message = make_message_segment(seq_no,ack_no, syn=True)
    socket.sendto(message.encode(), addr)
    STATE = constant.SYN_SENT
    
    message, _ = socket.recvfrom(1024)
    decoded_segment = message.decode()
    print(decoded_segment)
    if(decoded_segment[65] == '1' and decoded_segment[67] == '1'):
        STATE = constant.SYN_ACK_RECEIVED
        ack_no = int(decoded_segment[32:64], 2)

    if STATE == constant.SYN_ACK_RECEIVED and ack_no == seq_no+1:
        seq_no = int(decoded_segment[0:32], 2)
        message = make_message_segment(ack_no+1,seq_no+1, ack=True)
        socket.sendto(message.encode(), addr)
        STATE = constant.ESTABLISHED 

    if STATE == constant.ESTABLISHED:
        return True
    
    return False



if len(sys.argv) != 3:
    print("Please fill in the port and the source filename!")
else:
    server_socket = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server_socket.bind(('localhost', PORT))
    print(server_socket)
    

    conn = server_handshake(server_socket, ('localhost', 5003))

    if conn:
        print("connection established")


