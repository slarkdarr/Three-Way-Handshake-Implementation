import constant
import random
import os
from math import ceil

# encode chunks of file into binary
def encode_file(file_name, seq_num):
    data_segment = ''
    with open(file_name, 'r') as fptr:
        offset = seq_num * constant.MAX_DATA_SEGMENT
        fptr.seek(offset, 0)
        for i in range(1, constant.MAX_DATA_SEGMENT+1):
            temp = fptr.read(1)
            if temp:
                data_segment += str(temp)

    fptr.close()

    encoded_data = ''
    for i in range(len(data_segment)):
        temp = data_segment[i]
        byte = '{0:08b}'.format(ord(temp))
        encoded_data += byte
    

    return encoded_data



# Create message segment to send
def make_message_segment(seq_no, ack_no, encoded_data='', syn=False, ack=False, fin=False):
    message = '{0:032b}'.format(seq_no)
    message += '{0:032b}'.format(ack_no)

    if fin:
        message += '1'
    else:
        message += '0'

    if syn:
        message += '1'
    else:
        message += '0'

    message += '0'

    if ack:
        message += '1'
    else:
        message += '0'

    message += '0' * 28
    message += encoded_data
    message = add_message_checksum(message)
    
    return message

# Add checksum to message
def add_message_checksum(message):
    chunks = []
    for i in range(0, len(message), 16):
        chunks.append(message[i:i+16])

    ## Add checksum algorithm here
    return message

## Implement checksum verification here
def verify_checksum(message):
    return True

# generate random number
def random_num():
	generated_number = random.randint(0, 400000)
	return generated_number 


# Write message from segment into file
def write_to_file(message, file_name):
    fptr = open(file_name, 'a')
    segment_data = str(message[96:])
    text = ''

    for i in range(len(segment_data)//8):
        char_byte = str(segment_data[i*8:(i+1)*8])
        char = chr(int(char_byte, 2))
        text += char 
    
    fptr.write(text)
    fptr.close()

# Count the maximum sequence number for a file transmission
def count_max_sequence(filename):
    file_size = os.path.getsize(filename)
    max_sequence = ceil(file_size/constant.MAX_DATA_SEGMENT)

    return max_sequence
