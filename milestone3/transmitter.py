import math
import common_txrx as common
import numpy
from hamming_db import *

class Transmitter:
    def __init__(self, carrier_freq, samplerate, one, spb, silence, hamming_length = 0):
        self.fc = carrier_freq  # in cycles per sec, i.e., Hz
        self.samplerate = samplerate
        self.one = one
        self.spb = spb
        self.silence = silence
        self.hamming_length = hamming_length
        print 'Transmitter: '
    
    def num2bits(self, n):
        return [ int(z) for z in bin(n)[2:].zfill(30) ][:30]

    def get_header(self, length):
        header_start = []
        if self.hamming_length == 3:
            header_start.append([0,0])
        elif self.hamming_length == 7:
            header_start.append([0,self.one])
        elif self.hamming_length == 15:
            header_start.append([self.one,0])
        elif self.hamming_length == 31:
            header_start.append([self.one,self.one])
        else:
            print '\tNo Hamming code with n =', cc_len
            sys.exit(1)

        header_start.append(self.num2bits(length))

        return [val for subl in header_start for val in subl]

    def encode(self, databits):
        if self.hamming_length == 0:
            return databits

        header = self.get_header(len(databits))
        header_output = self.hamming_encoding(header, 1)

        data_output = self.hamming_encoding(databits, 0)

        return list(numpy.append(header_output, data_output))

    def hamming_encoding(self, databits, is_header):
        hamming_len = self.hamming_length
        if is_header > 0:
            hamming_len = 3

        (n, k, index, G) = gen_lookup(hamming_len)
        i = 0
        x = 0

        output = numpy.array([])
        output.resize(math.ceil((len(databits) * 1.0) / (k * 1.0)) * n)

        while i < len(databits):
            data_chunk = numpy.array(databits[i:i+k])
            data_chunk.resize(k)
            coded_chunk = numpy.dot(data_chunk, G)
            
            for z in xrange(0, n):
                output[x] = coded_chunk[z]
                x += 1

            i += k

        return output

    def add_preamble(self, databits):
        '''
        Prepend the array of source bits with silence bits and preamble bits
        The recommended preamble bits is 
         [1,1,1,1,1,0,1,1,1,1,0,0,1,1,1,0,1,0,1,1,0,0,0,0,1,0,1,1,1,0,0,0,1,1,0,1,1,0,1,0,0,1,0,0,0,1,0,0,1,1,0,0,1,0,1,0,1,0,0,0,0,0,0]
        The output should be the concatenation of arrays of
            [silence bits], [preamble bits], and [databits]
        '''
        
        silence_bits = [ 0 for x in range(self.silence) ]
        preamble_bits = [1,1,1,1,1,0,1,1,1,1,0,0,1,1,1,0,1,0,1,1,0,0,0,0,1,0,1,1,1,0,0,0,1,1,0,1,1,0,1,0,0,1,0,0,0,1,0,0,1,1,0,0,1,0,1,0,1,0,0,0,0,0,0]
        databits_with_preamble = silence_bits + preamble_bits + databits

        return databits_with_preamble


    def bits_to_samples(self, databits_with_preamble):
        '''
        Convert each bits into [spb] samples. 
        Sample values for bit '1', '0' should be [one], 0 respectively.
        Output should be an array of samples.
        '''
        samples = numpy.array([])

        for i in range(len(databits_with_preamble)):
            if databits_with_preamble[i] == 1:
                samples = numpy.append(samples, self.one)
            else:
                samples = numpy.append(samples, 0.0)

        repeat_times = numpy.repeat(numpy.array([self.spb]), len(databits_with_preamble))
        samples = numpy.repeat(samples, repeat_times)

        return samples

    def modulate(self, samples):
        '''
        Calls modulation function. No need to touch it.
        '''
        return common.modulate(self.fc, self.samplerate, samples)
