import socket

PORT = 5000
server_socket = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
server_socket.bind(('', PORT))
print("Server is listening on " + '0.0.0.0:' + str(PORT))