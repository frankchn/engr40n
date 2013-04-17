import numpy
import math
import operator

# Methods common to both the transmitter and receiver.
def hamming(s1,s2):
    # Given two binary vectors s1 and s2 (possibly of different 
    # lengths), first truncate the longer vector (to equalize 
    # the vector lengths) and then find the hamming distance
    # between the two. Also compute the bit error rate  .
    # BER = (# bits in error)/(# total bits )
    length = len(s1)
    if len(s2) < length:
        length = len(s2)
    hamming_d = 0
    for i in range(0, length):
        if s1[i] != s2[i]:
            hamming_d = 1 + hamming_d
    ber = hamming_d * 1.0 / length
    return hamming_d, ber
