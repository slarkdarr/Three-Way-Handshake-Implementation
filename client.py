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

def client_close(socket, addr):
    seq_no = 0
    ack_no = 0

    message, _ = socket.recvfrom(1024)
    decoded_segment = message.decode()
    if decoded_segment[64] == '1' and decoded_segment[67] == '1':
        STATE = constant.CLOSE_WAIT
        seq_no = int(decoded_segment[32:64],2)
        ack_no = int(decoded_segment[0:32],2) + 1
    
    if STATE == constant.CLOSE_WAIT:
        message = make_message_segment(seq_no, ack_no, ack=True)
        socket.sendto(message.encode(), addr)
        STATE = constant.LAST_ACK

    if STATE == constant.LAST_ACK:
        message = make_message_segment(seq_no, ack_no, ack=True, fin=True)
        socket.sendto(message.encode(), addr)

        message, _ = socket.recvfrom(1024)
        decoded_segment = message.decode()
        if decoded_segment[67] == '1':
            ack_no_received = int(decoded_segment[32:64], 2)
            seq_no_received = int(decoded_segment[0:32], 2)
            if seq_no+1 == ack_no_received and seq_no_received == ack_no:
                STATE = constant.CLOSED
    
    if STATE == constant.CLOSED:
        return True 
    
    return False

    
    
if len(sys.argv) != 3:
    print("Please fill in the port and the destination filename!")
else:
    client_socket = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client_socket.bind(('localhost', PORT))
    print(client_socket)

    close = client_close(client_socket, ('', 5000))
    if close:
        print("connection closed")
    else:
        print("weird but client")

        