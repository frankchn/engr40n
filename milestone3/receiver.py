import sys
import math
import numpy
import scipy.cluster.vq
import common_txrx as common
from numpy import linalg as LA
import receiver_mil3
from hamming_db import *

class Receiver:
    def __init__(self, carrier_freq, samplerate, spb, hamming_on = 0):
        '''
        The physical-layer receive function, which processes the
        received samples by detecting the preamble and then
        demodulating the samples from the start of the preamble 
        sequence. Returns the sequence of received bits (after
        demapping)
        '''
        self.fc = carrier_freq
        self.samplerate = samplerate
        self.spb = spb 
        self.hamming_on = hamming_on
        print 'Receiver: '

    def decode(self, rcd_bits):
        if self.hamming_on == 0:
            return rcd_bits

        header = rcd_bits[0:96]
        body = rcd_bits[96:]

        (header_decoded, header_errors) = self.hamming_decoding(header, 0)

        index = header_decoded[0] * 2 + header_decoded[1]
        
        payload_length = int(''.join(map(str, header_decoded[2:])), 2)
        
        print " ! Channel Coding Rate:" , (float(parameters[index][1]) / parameters[index][0])
        
        (body_decoded, body_errors) = self.hamming_decoding(body, index)
        body_decoded = body_decoded[:payload_length]

        print " ! Errors Corrected:" , (header_errors + body_errors)
        
        return body_decoded

    def hamming_decoding(self, coded_bits, index):
        (n, k, H) = parity_lookup(index)
        num_columns = len(H[0])

        H_T = numpy.transpose(H)        
        errors_corrected = 0
        
        decoded_bits = []
        i = 0
        while i + n <= len(coded_bits):
            temp = numpy.arange(n).reshape(n,1)
            j = 0
            while j < n:
                temp[j][0] = coded_bits[i+j]
                j = j+1

            synd = numpy.transpose(numpy.dot(H, temp) % 2)[0]

            bit_error = -1
            for z in xrange(len(H_T)):
                if numpy.array_equal(synd,H_T[z]):
                    bit_error = z
                    break

            for z in xrange(k):
                if bit_error != z:
                    decoded_bits.append(coded_bits[i+z])
                else:
                    errors_corrected += 1
                    decoded_bits.append((coded_bits[i+z] + 1) % 2)

            i = i+n
        
        return decoded_bits, errors_corrected

    def detect_threshold(self, demod_samples):
        '''
        Calls the detect_threshold function in another module.
        No need to touch this.
        ''' 
        return receiver_mil3.detect_threshold(demod_samples)
 
    def detect_preamble(self, demod_samples, thresh, one):
        '''
        Find the sample corresp. to the first reliable bit "1"; this step 
        is crucial to a proper and correct synchronization w/ the xmitter.
        '''

        '''
        First, find the first sample index where you detect energy based on the
        moving average method described in the milestone 2 description.
        '''

        print " + Detecting preamble"

        prefix_sum = [0]
        prefix_sum_squared = [0]
        
        index = 0
        while index < len(demod_samples):
            prefix_sum.append(prefix_sum[-1] + demod_samples[index])
            prefix_sum_squared.append(prefix_sum_squared[-1] + demod_samples[index] * demod_samples[index])
            index = index + 1
        
        index = 0
        ret = -1
        while ret == -1 and index + self.spb <= len(demod_samples):
            average = sum(demod_samples[index+self.spb/4:index+self.spb*3/4]) * 2.0 / self.spb
            if(average > (one + thresh)/2):
                ret = index
            index += 1
        
        energy_offset = ret
        if energy_offset < 0:
            print '*** ERROR: Could not detect any ones (so no preamble). ***'
            print '\tIncrease volume / turn on mic?'
            print '\tOr is there some other synchronization bug? ***'
            sys.exit(1)

        '''
        Then, starting from the demod_samples[offset], find the sample index where
        the cross-correlation between the signal samples and the preamble 
        samples is the highest. 
        [1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1]
        '''
        # Fill in your implementation of the cross-correlation check procedure
        
        preamble = [1,1,1,1,1,0,1,1,1,1,0,0,1,1,1,0,1,0,1,1,0,0,0,0,1,0,1,1,1,0,0,0,1,1,0,1,1,0,1,0,0,1,0,0,0,1,0,0,1,1,0,0,1,0,1,0,1,0,0,0,0,0,0]
        
        best_offset = 0
        highest_correlation = -1000
        offset = 0
        
        while offset <= 3 * self.spb * len(preamble):
        #while offset <= 256:
            curr_correlation = 0
            preamble_index = 0
            curr_offset = offset
            while preamble_index < len(preamble):
                if preamble[preamble_index] == 1:
                    curr_correlation = curr_correlation + prefix_sum[energy_offset + offset + (preamble_index+1) * self.spb] - prefix_sum[energy_offset + offset + (preamble_index) * self.spb]
                preamble_index = preamble_index + 1
            curr_correlation = curr_correlation / ((prefix_sum_squared[energy_offset + offset + preamble_index * self.spb] - prefix_sum_squared[energy_offset + offset]) ** 0.5)
            if curr_correlation > highest_correlation:
                highest_correlation = curr_correlation
                best_offset = offset
            offset = offset + 1

        preamble_offset = best_offset
        
        '''
        [preamble_offset] is the additional amount of offset starting from [offset],
        (not a absolute index reference by [0]). 
        Note that the final return value is [offset + pre_offset]
        '''

        return energy_offset + preamble_offset
        
    def demap_and_check(self, demod_samples, preamble_start):
        preamble = [1,1,1,1,1,0,1,1,1,1,0,0,1,1,1,0,1,0,1,1,0,0,0,0,1,0,1,1,1,0,0,0,1,1,0,1,1,0,1,0,0,1,0,0,0,1,0,0,1,1,0,0,1,0,1,0,1,0,0,0,0,0,0]
        '''
        Demap the demod_samples (starting from [preamble_start]) into bits.
        1. Calculate the average values of midpoints of each [spb] samples
           and match it with the known preamble bit values.
        '''
        zero_sum = 0.0
        zero_cnt = 0
        one_sum  = 1.0
        one_cnt  = 0

        print " + Demap and check"

        for index, val in enumerate(preamble):
            start_location = preamble_start + self.spb * index + self.spb / 4
            end_location = start_location + self.spb / 2
            current_avg = sum(demod_samples[start_location : end_location]) * 1.0 / (self.spb / 2)
            if val == 1:
                one_sum += current_avg
                one_cnt += 1
            else:
                zero_sum += current_avg
                zero_cnt += 1

        one = one_sum / one_cnt
        zero = zero_sum / zero_cnt

        '''
        2. Use the average values and bit values of the preamble samples from (1)
           to calculate the new [thresh], [one], [zero]
        '''
        thresh = (one + zero) / 2.0

        '''
        3. Demap the average values from (1) with the new three values from (2)
        '''
        bits = []
        offset = preamble_start
        while offset < len(demod_samples):
            start_location = offset + self.spb / 4
            end_location = start_location + self.spb / 2
            current_value = sum(demod_samples[start_location : end_location]) * 1.0 / (self.spb / 2)

            if current_value > thresh:
                bits.append(1)
            else:
                bits.append(0)

            offset += self.spb

        '''
        4. Check whether the first [preamble_length] bits of (3) are equal to
           the preamble. If it is proceed, if not terminate the program. 
        Output is the array of data_bits (bits without preamble)
        THIS HAS BEEN REMOVED BY REQUEST OF MILESTONE
        '''

        return bits[len(preamble):]

    def demodulate(self, samples):
        return common.demodulate(self.fc, self.samplerate, samples)
