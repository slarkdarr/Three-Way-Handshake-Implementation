import sys
import socket
from client import Rn
from util import *
import constant

HOST = 'localhost'
PORT = int(sys.argv[1])
source_filename = sys.argv[2]
STATE = ''

# Three way handshake from the server side
def server_handshake(socket, addr):
    seq_no = random_num()
    ack_no = 0

    message = make_message_segment(seq_no,ack_no, syn=True)
    socket.sendto(message.encode(), addr)
    STATE = constant.SYN_SENT
    print("Syn packet sent to client " + str(addr[0]) + ":" + str(addr[1]))
    
    while(1):
        message, rec_addr = socket.recvfrom(1024)
        decoded_segment = message.decode()
        if len(decoded_segment) > 10:
            if(decoded_segment[65] == '1' and decoded_segment[67] == '1'):
                STATE = constant.SYN_ACK_RECEIVED
                print("Syn Ack packet received from client " + str(addr[0]) + ":" + str(addr[1]))
                ack_no = int(decoded_segment[32:64], 2)
                break

    if STATE == constant.SYN_ACK_RECEIVED and ack_no == seq_no+1:
        seq_no = int(decoded_segment[0:32], 2)
        message = make_message_segment(ack_no+1,seq_no+1, ack=True)
        socket.sendto(message.encode(), addr)
        print("Ack packet sent to client " + str(addr[0]) + ":" + str(addr[1]))
        STATE = constant.ESTABLISHED


    if STATE == constant.ESTABLISHED:
        return True
    
    return False

# Closing connection from the server side
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

    STATE = constant.LISTEN_STATE
    client_list = []
    while(1):
        message, addr = server_socket.recvfrom(1024)
        client_list.append(addr)
        print('Client (127.0.0.1:' + str(addr[1]) + ')')
        command = input('Keep listening?[y/n]: ')
        if command == 'n' or command == 'N':
            break
    
    for addr in client_list:
        print("Initiating handshake with " + str(addr[0]) + ":" + str(addr[1]))
        conn = server_handshake(server_socket, addr)
        if conn:
            print("Connected with client (" + str(addr[0]) + ":" + str(addr[1]) + ")")
            print("Initiating file transfers...")
            
            # GO Back N
            Rn = 0
            Sb = 0
            Sm = constant.WINDOW_SIZE + 1

            while 1:
                message, _ = server_socket.recvfrom(1024)
                decoded_segment = message.decode()
                
                last_ack = int(decoded_segment[32:64], 2)
                Rn = last_ack + 1

                #print([Segment SEQ=1] Sent)

                if (Rn > Sb and Rn >= Sm):
                    for i in range(Sb, Sm):
                        print("[Segment SEQ="+str(Sb+1)+"] Acked")
                    Sm += constant.WINDOW_SIZE
                    Sb += constant.WINDOW_SIZE
                elif (Rn > Sb and Rn < Sm):
                    for i in range(Sb, Rn):
                        print("[Segment SEQ="+str(Sb+1)+"] Acked")
                    print("[Segment SEQ="+str(Rn)+"] NOT ACKED. Duplicate Ack found")
                    Sm = (Sm - Sb) + Rn
                    Sb = Rn
                
                if ():
                    for i in range(Sb, Sm):
                        data = encode_file(source_filename, i)
                        msg = make_message_segment(i, last_ack, encoded_data=data)
                        add_message_checksum(msg)
                        server_socket.sendto(msg.encode(), addr)
        
        print('File transfers completed')
        print('Closing connection with ' + str(addr[0]) + ":" + str(addr[1]))
        server_close(server_socket, addr)
        print('Connection closed with ' + str(addr[0]) + ":" + str(addr[1]))

    print(client_list)

    print("All client served, shutting down server...")

