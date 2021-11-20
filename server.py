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
    
    while(1):
        message, rec_addr = socket.recvfrom(1024)
        decoded_segment = message.decode()
        if len(decoded_segment) > 10 and rec_addr == addr:
            if(decoded_segment[65] == '1' and decoded_segment[67] == '1'):
                STATE = constant.SYN_ACK_RECEIVED
                ack_no = int(decoded_segment[32:64], 2)
                break

    if STATE == constant.SYN_ACK_RECEIVED and ack_no == seq_no+1:
        seq_no = int(decoded_segment[0:32], 2)
        message = make_message_segment(ack_no+1,seq_no+1, ack=True)
        socket.sendto(message.encode(), addr)
        STATE = constant.ESTABLISHED 

    if STATE == constant.ESTABLISHED:
        return True
    
    return False

def server_close(socket, addr):
    seq_no = 100 
    ack_no = 300

    message = make_message_segment(seq_no, ack_no, ack=True, fin=True)
    socket.sendto(message.encode(), addr)
    STATE = constant.FIN_WAIT_1

    if STATE == constant.FIN_WAIT_1:
        message, _ = socket.recvfrom(1024)
        decoded_segment = message.decode()
        temp = int(decoded_segment[32:64],2)
        
        if decoded_segment[67] == '1' and temp == seq_no + 1:
            STATE = constant.FIN_WAIT_2
            ack_no =  int(decoded_segment[0:32], 2)
            seq_no = temp

    if STATE == constant.FIN_WAIT_2:
        message, _ = socket.recvfrom(1024)
        decoded_segment = message.decode()
        temp = int(decoded_segment[32:64],2)
        print(temp)
        print(seq_no)
        if decoded_segment[64] == '1' and decoded_segment[67] == '1' and temp == seq_no:
            print('test')
            STATE = constant.TIME_WAIT
    
    if STATE == constant.TIME_WAIT:
        message = make_message_segment(seq_no, ack_no+1, ack=True)
        socket.sendto(message.encode(), addr)
        STATE = constant.CLOSED

    if STATE == constant.CLOSED:
        return True
    
    return False 

if len(sys.argv) != 3:
    print("Please fill in the port and the source filename!")
else:
    server_socket = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server_socket.bind(('', PORT))
    print("Server is listening on " + '0.0.0.0:' + str(PORT))

    segment_data = encode_file(source_filename, 0)
    message = make_message_segment(0, 0, encoded_data=segment_data)
    server_socket.sendto(message.encode(), ('localhost', 5003))
    print("done sending")

