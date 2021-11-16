import sys
import socket

port = int(sys.argv[1])
source_filename = sys.argv[2]


if len(sys.argv) != 3:
    print("Please fill in the port and the source filename!")
else:
    pass