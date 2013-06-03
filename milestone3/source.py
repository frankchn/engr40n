# FRANK CHEN + NICK WU
# audiocom library: Source and sink functions
import common_srcsink as common
import Image
from graphs import *
import binascii
import random
import os
import itertools

class HammingNode:
    def __init__(self, valueIn, countIn, leftIn = None, rightIn = None):
        self.value = valueIn
        self.count = countIn
        self.left = leftIn
        self.right = rightIn
    

class Source:
    def __init__(self, monotone, filename=None):
        # The initialization procedure of source object
        self.monotone = monotone
        self.fname = filename
        print 'Source'

    # header format is 32 bits long
    # bits one and two are:
    # 0,0 - TXT
    # 0,1 - PNG
    # 1,1 - Monotone
    # The next 30 bits are the range. The maximum is 2^30-1 (or 1 byte less than 1 GB)

    def process(self):
        # Form the databits, from the filename 
        if self.fname is not None:
            if self.fname.endswith('.png') or self.fname.endswith('.PNG'):
                payload = self.bits_from_image(self.fname)
                content_type = 'image'
                content_len = self.filesize(self.fname)
            else:
                payload = self.text2bits(self.fname)  
                content_type = 'text'
                content_len = self.filesize(self.fname)
        else:               
            payload = [ 1 for x in range(self.monotone) ]
            content_type = 'monotone'
            content_len = self.monotone

        header = self.get_header(content_len, content_type)
        databits = header + payload

        (a, b) = self.huffman_encode(databits)
        
        return payload, databits

    def filesize(self, filename):
        return os.path.getsize(filename)

    def num2bits(self, n):
        return [ int(z) for z in bin(n)[2:].zfill(30) ][:30]

    def text2bits(self, filename):
        with open(filename, "r") as myfile:
            data = myfile.read()
        return [int(j) for j in list(itertools.chain(*[list('%08d' % int(bin(ord(i))[2:])) for i in data]))]

    def bits_from_image(self, filename):
        with open(filename, "r") as myfile:
            data = myfile.read()
        return [int(j) for j in list(itertools.chain(*[list('%08d' % int(bin(ord(i))[2:])) for i in data]))]

    def get_header(self, payload_length, srctype): 
        # Given the payload length and the type of source 
        # (image, text, monotone), form the header
        return {
                  'text':     [0,0] + self.num2bits(payload_length),
                  'image':    [0,1] + self.num2bits(payload_length),
                  'monotone': [1,0] + self.num2bits(payload_length)
               }[srctype]
               
    def huffman_encode(self, src_bits):
        data_stats = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        i = 0
        while i < len(src_bits):
            count = (src_bits[i] << 3) | (src_bits[i+1] << 2) | (src_bits[i+2] << 1) | (src_bits[i+3])
            data_stats[count] = data_stats[count] + 1
            i = i + 4
        huffman_encode = []
        return data_stats, huffman_encode
