import sys 
import socket
from util import *

HOST = 'localhost'
PORT = int(sys.argv[1])
dest_filename = sys.argv[2]
identifier = 'message'
byte_identifier = str.encode(identifier)
STATE = ''

# Three way handshake from the client side
def client_handshake(socket, addr):
    seq_no = random_num()
    ack_no = 0

    message, _ = socket.recvfrom(1024)
    decoded_segment = message.decode()

    print("Syn packet received from server")
    if decoded_segment[65] == '1':
        STATE = constant.SYN_RECEIVED 
        ack_no = int(decoded_segment[0:32],2)

    if STATE == constant.SYN_RECEIVED:
        message = make_message_segment(seq_no, ack_no+1, syn=True, ack=True)
        print("Syn Ack packet sent to server")
        socket.sendto(message.encode(), addr)
        STATE = constant.SYN_ACK_SENT 

    if STATE == constant.SYN_ACK_SENT:
        message, _ = socket.recvfrom(1024)
        print("Ack packet received from server")
        decoded_segment = message.decode()
        ack_no = int(decoded_segment[32:64],2)
        if decoded_segment[67] == '1' and ack_no == seq_no + 1:
            STATE = constant.ESTABLISHED
        
    if STATE == constant.ESTABLISHED:
        return True
    
    return False

# Closing connection from the client side
def client_close(socket, addr):
    seq_no = 0
    ack_no = 0

    message, _ = socket.recvfrom(1024)
    decoded_segment = message.decode()
    if decoded_segment[64] == '1' and decoded_segment[67] == '1':
        STATE = constant.CLOSE_WAIT
        print("Closing connection with server")
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

    print("Client binded to address and ready to request connection")
    print("Sending request message to broadcast")
    client_socket.sendto(b'request', ('255.255.255.255', 5000))
    STATE = constant.BROADCAST_SENT
    client_handshake(client_socket, ('', 5000))
    STATE = constant.ESTABLISHED

    # Go-Back-N
    Rn = 0
    while 1:
        message, _ = client_socket.recvfrom(32768+96)
        decoded_segment = message.decode()
        
        if ():

        else:
            Sn = int(decoded_segment[0:32], 2)
            last_ack = Rn

            if (Sn == Rn and verify_checksum(decoded_segment)):
                print("[Segment SEQ="+str(Rn+1)+"] Received, Ack sent")
                write_to_file(decoded_segment, dest_filename)
                Rn += 1
            else:
                print("[Segment SEQ="+str(Rn+1)+"] Segment damaged. Ack prev sequence number.")
                
            msg = make_message_segment(0, last_ack, ack=True)
            client_socket.sendto(msg.encode(), ('', 5000))

    client_close(client_socket, ('', 5000))
    STATE = constant.CLOSED
    print("Connection closed with server")
    print("Shutting down client")

        