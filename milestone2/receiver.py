import sys
import math
import numpy
import scipy.cluster.vq
import common_txrx as common
from numpy import linalg as LA
import receiver_mil3

class Receiver:
    def __init__(self, carrier_freq, samplerate, spb):
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
        print 'Receiver: '

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

        prefix_sum = [0]
        index = 0
        while index < len(demod_samples):
            prefix_sum.append(prefix_sum[-1] + demod_samples[index])
            index = index + 1
        
        index = 0
        ret = -1
        while ret == -1 and index + self.spb <= len(demod_samples):
            average = sum(demod_samples[index:index+self.spb]) * 1.0 / self.spb
            if(average > thresh):
                ret = index
            index += 1
            print "sample", index, "threshold", average, "target", thresh
        
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
        
        preamble = [1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1];
        
        best_offset = 0
        highest_correlation = -1
        offset = 0
        while offset <= 3 * self.spb * len(preamble):
            curr_correlation = 0
            preamble_index = 0
            curr_offset = offset
            while preamble_index < len(preamble):
                if preamble[preamble_index] == 1:
                    curr_correlation = curr_correlation + demod_samples[energy_offset + offset + (preamble_index+1) * self.spb] - demod_samples[energy_offset + offset + (preamble_index) * self.spb]
                preamble_index = preamble_index + 1
            if curr_correlation > highest_correlation:
                highest_correlation = curr_correlation
                best_offset = offset
            offset = offset + 1
            print "offset", offset, "curr_correlation", curr_correlation

        
        preamble_offset = best_offset

        print preamble_offset
        
        '''
        [preamble_offset] is the additional amount of offset starting from [offset],
        (not a absolute index reference by [0]). 
        Note that the final return value is [offset + pre_offset]
        '''

        return energy_offset + preamble_offset
        
    def demap_and_check(self, demod_samples, preamble_start):
        preamble = [1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1];
        '''
        Demap the demod_samples (starting from [preamble_start]) into bits.
        1. Calculate the average values of midpoints of each [spb] samples
           and match it with the known preamble bit values.
        '''
        zero_sum = 0.0
        zero_cnt = 0
        one_sum  = 1.0
        one_cnt  = 0

        for index, val in enumerate(preamble):
            start_location = preamble_start + self.spb * index + self.spb / 4
            end_location = start_location + 3 * self.spb / 4
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
            end_location = offset + 3 * self.spb / 4
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
        '''

        for index, val in enumerate(preamble):
            if bits[index] != preamble[index]:
                print "Cannot detect preamble!"
                sys.exit()

        return bits[len(preamble):]

    def demodulate(self, samples):
        return common.demodulate(self.fc, self.samplerate, samples)
