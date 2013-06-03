# FRANK CHEN + NICK WU
import numpy
import math
import operator

class HammingNode:
    def __init__(self, valueIn, countIn, leftIn = None, rightIn = None):
        self.value = valueIn
        self.count = countIn
        self.left = leftIn
        self.right = rightIn
    

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
    ber = (hamming_d * 1.0) / (length * 1.0)
    return hamming_d, ber

def get_hamming_tree(data_stats):
    nodes = []
    i = 0
    while i < 16:
        if data_stats[i] > 0:
            node = HammingNode(i, data_stats[i])
            nodes.append(node)
        i = i+1
    while len(nodes) > 1:
        left_node = None
        right_node = None
        left_index = -1
        right_index = -1
        i = 0
        while i < len(nodes):
            if left_node == None:
                left_node = nodes[i]
                left_index = i
            elif nodes[i].count < left_node.count:
                right_node = left_node
                right_index = left_index
                left_node = nodes[i]
                left_index = i
            elif right_node == None:
                right_node = nodes[i]
                right_index = i
            elif nodes[i].count < right_node.count:
                right_node = nodes[i]
                right_index = i
            i = i+1
        new_node = HammingNode(-1, left_node.count + right_node.count, left_node, right_node)
        if left_index < right_index:
            nodes.pop(right_index)
            nodes.pop(left_index)
        else:
            nodes.pop(left_index)
            nodes.pop(right_index)
        nodes.append(new_node)
    return nodes[0]