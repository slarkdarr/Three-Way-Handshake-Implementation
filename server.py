import sys
import socket
from util import *
import constant

HOST = 'localhost'
PORT = int(sys.argv[1])
source_filename = sys.argv[2]
STATE = ''
MAX_SEQUENCE_NO = count_max_sequence(source_filename)

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
        if decoded_segment[64] == '1' and decoded_segment[67] == '1' and temp == seq_no:
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

    print('==================================================================')
    print('SERVER STARTED')
    print('==================================================================')
    print()
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print('LISTENING')
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')




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
        print()
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print('INITIATING HANDSHAKE')
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print("Initiating handshake with " + str(addr[0]) + ":" + str(addr[1]))
        conn = server_handshake(server_socket, addr)
        if conn:
            print()
            print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print('CONNECTION ESTABLISHED')
            print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print("Connected with client (" + str(addr[0]) + ":" + str(addr[1]) + ")")
            print()
            print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print('INITIATING FILE TRANSFERS')
            print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            
            # GO Back N
            Rn = 1
            Sb = 1
            Sm = constant.WINDOW_SIZE + 1
            last_ack = 0

            server_socket.settimeout(7.0)
            while 1:
                count = 1
                while(count <= constant.WINDOW_SIZE):
                    try:
                        message, _ = server_socket.recvfrom(1024)
                        decoded_segment = message.decode()
                        
                        temp = last_ack
                        last_ack = int(decoded_segment[32:64], 2)
                        
                        if last_ack == temp:
                            print("[Segment SEQ=%d] NOT ACKED. Duplicate Ack found" % last_ack+1)
                            print("### Commencing Go Back-N Protocol ###")
                            break
                        else:
                            print("[Segment SEQ=%d] ACKED." % last_ack)

                        Rn = last_ack + 1
                        count += 1
                    except:
                        break
                
                if(last_ack == MAX_SEQUENCE_NO):
                    break
                
                if (Rn > Sb):
                    Sm = (Sm - Sb) + Rn
                    Sb = Rn
                
                temp = min(Sm, MAX_SEQUENCE_NO+1)
                for i in range(Sb, temp):
                    data = encode_file(source_filename, i-1)
                    msg = make_message_segment(i, last_ack, encoded_data=data)
                    server_socket.sendto(msg.encode(), addr)
                    print("[Segment SEQ=%d] Sent" % i)
        
        server_socket.settimeout(None)
        print()
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print('FILE TRANSFER COMPLETE')
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

        print('Closing connection with ' + str(addr[0]) + ":" + str(addr[1]))
        server_close(server_socket, addr)
        print()
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print('SERVER CONNECTION CLOSED')
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print('Connection closed with ' + str(addr[0]) + ":" + str(addr[1]))

    print()
    print('==================================================================')
    print('SERVER SHUTTING DOWN')
    print('==================================================================')
    print()
    print("All client served, shutting down server...")

