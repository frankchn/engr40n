# FRANK CHEN + NICK WU
# audiocom library: Source and sink functions
import common_srcsink as common
import Image
from graphs import *
import binascii
import random
import os
import itertools
from heapq import *
import math

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

        if content_type == 'monotone':
            header = self.get_header(content_type, content_len, None)
            databits = header + payload
        
        else:
            (data_stats, huffman_encode) = self.huffman_encode(payload) 
            header = self.get_header(content_type, len(huffman_encode), data_stats)
            databits = header + huffman_encode
        
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

    def get_header(self, srctype, payload_length, data_stats): 
        if srctype == 'monotone':
            return [1,0] + self.num2bits(payload_length)
        if srctype == 'text':
            header = [0,0] + self.num2bits(payload_length)
        else:
            header = [0,1] + self.num2bits(payload_length)
        i = 0
        while i < 16:
            temp = [0,0,0,0,0,0,0,0,0,0]
            j = 0
            while j < 10:
                if (data_stats[i] & (1 << j)) != 0:
                    temp[9-j] = 1
                j = j+1
            i = i+1
            header = header + temp
        return header
               
    def huffman_encode(self, src_bits):
        raw_data_stats = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        i = 0
        while i < len(src_bits):
            count = (src_bits[i] << 3) | (src_bits[i+1] << 2) | (src_bits[i+2] << 1) | (src_bits[i+3])
            raw_data_stats[count] = raw_data_stats[count] + 1
            i = i + 4

        # reduce the counts into the k-th order statistic
        final_stats = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        for i in xrange(0, 16):
            final_stats[i] = int(math.floor((raw_data_stats[i] * 1.0) / (max(raw_data_stats) * 1.0) * 1023))
            print final_stats[i]

        data_stats = final_stats

        huffman_encode = []
        encodings = []
        i = 0
        while i < 16:
            encodings.append([])
            i = i+1
        queue = []
        queue.append((common.get_hamming_tree(data_stats), []))
        while len(queue) > 0:
            state = queue.pop(0)
            curr_node = state[0]
            path = state[1]
            if curr_node.value >= 0:
                encodings[curr_node.value] = path
            else:
                left_path = []
                j = 0
                while j < len(path):
                    left_path.append(path[j])
                    j = j+1
                left_path.append(0)
                queue.append((curr_node.left, left_path))
                right_path = []
                j = 0
                while j < len(path):
                    right_path.append(path[j])
                    j = j+1
                right_path.append(1)
                queue.append((curr_node.right, right_path))
        i = 0
        while i < len(src_bits):
            curr = (src_bits[i] << 3) | (src_bits[i+1] << 2) | (src_bits[i+2] << 1) | (src_bits[i+3])
            j = 0
            while j < len(encodings[curr]):
                huffman_encode.append(encodings[curr][j])
                j = j+1
            i = i + 4

        return data_stats, huffman_encode
