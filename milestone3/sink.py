# FRANK CHEN + NICK WU
# audiocom library: Source and sink functions
import common_srcsink as common
import Image
from graphs import *
import binascii
import random


class Sink:
    def __init__(self):
        # no initialization required for sink 
        print 'Sink:'

    def process(self, recd_bits):
        # Process the recd_bits to form the original transmitted
        # file. 
        # Here recd_bits is the array of bits that was 
        # passed on from the receiver. You can assume, that this 
        # array starts with the header bits (the preamble has 
        # been detected and removed). However, the length of 
        # this array could be arbitrary. Make sure you truncate 
        # it (based on the payload length as mentioned in 
        # header) before converting into a file.
        
        # If its an image, save it as "rcd-image.png"
        # If its a text, just print out the text
        
        rcd_payload = None
        header = recd_bits[:32]

        srctype, payload_length = self.read_type_size(header)
        to_decrypt = None
        if srctype == 'monotone':
            to_decrypt = recd_bits[32:(32 + payload_length * 8)]
        else:
            to_decrypt = recd_bits[192:(192 + payload_length * 8)]
            data_stats = self.read_stat(recd_bits[32:192])
            payload = self.huffman_decode(data_stats, to_decrypt)
            
        if srctype == 'text':
            print self.bits2text(payload)
        elif srctype == 'image':
            self.image_from_bits(payload, '')
        
        # Return the received payload for comparison purposes
        return to_decrypt

    def bits2text(self, bits):
        string_bits = [str(i) for i in bits]
        text = ''
        
        for i in range(len(string_bits)):
            if i % 8 > 0:
                continue
            val = chr(int(''.join(string_bits[i:i+8]), 2))
            text += val

        return  text

    def image_from_bits(self, bits,filename):
        v = self.bits2text(bits)
        with open("rcd-image.png", "w+") as f:
            f.write(v)
        pass 

    def read_type_size(self, header_bits): 
        string_bits = [str(i) for i in header_bits]

        payload_length = int(''.join(string_bits[2:]), 2)
        payload_type = int(''.join(string_bits[:2]), 2)
        srctype = {
            0: 'text',
            1: 'image',
            2: 'monotone'
        }[payload_type]

        print '\tRecd header: ', header_bits
        print '\tLength from header: ', payload_length
        print '\tSource type: ', srctype
        return srctype, payload_length
        
    def read_stat(self, header_bits):
        data_stats = []
        i = 0
        while i < 16:
            count = 0;
            j = 0
            while j < 10:
                count = count + (header_bits[18+i+j] << (9-j))
                j = j+1
            data_stats.append(count)
            i = i+1
        return data_stats
        
    def huffman_decode(self, data_stats, huffman_encode):
        source_bits = []
        root = common.get_hamming_tree(data_stats)
        curr = root
        i = 0
        path = []
        while i < len(huffman_encode):
            if curr.value >= 0:
                source_bits = source_bits + path
                path = []
                curr = root
            if huffman_encode[i] == 0:
                path.append(0)
                curr = curr.left
            else:
                path.append(1)
                curr = curr.right
            i = i+1
        source_bits = source_bits + path
        return source_bits