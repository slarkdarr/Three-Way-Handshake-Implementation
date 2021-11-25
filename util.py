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

    ## Calculate the binary sum of packets
    packet_sum = 0
    for i in chunks:
        packet_sum += int(i,2)

    bin_sum = bin(packet_sum)[2:]
    
    # Add overflow bits
    if (len(bin_sum) > 16):
        x = len(bin_sum) - 16
        bin_sum = bin(int(bin_sum[0:x], 2)+int(bin_sum[x:], 2))[2:]
    if (len(bin_sum) < 16):
        bin_sum = '0'*(k-len(bin_sum))+bin_sum

    checksum = ''
    for i in bin_sum:
        if (i == '1'):
            checksum += '0'
        else:
            checksum += '1'

    return checksum

## Implement checksum verification here
def verify_checksum(message):
    chunks = []
    for i in range(0, len(message), 16):
        chunks.append(message[i:i+16])

    checksum = add_message_checksum(message)

    ## Calculate the binary sum of packets + checksum
    packet_sum = int(checksum,2)
    for i in chunks:
        packet_sum += int(i,2)

    bin_sum = bin(packet_sum)[2:]

    if (len(bin_sum) > 16):
        x = len(bin_sum) - 16
        bin_sum = bin(int(bin_sum[0:x], 2)+int(bin_sum[x:], 2))[2:]

    receiver_checksum = ''
    for i in bin_sum:
        if (i == '1'):
            receiver_checksum += '0'
        else:
            receiver_checksum += '1'

    if (int(receiver_checksum, 2) != 0):
        return False

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
