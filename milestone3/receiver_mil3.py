import numpy
import math
import operator
import random
import scipy.cluster.vq
import common_txrx as common

def detect_threshold(demod_samples): 
        # Now, we have a bunch of values that, for on-off keying, are
        # either near amplitude 0 or near a positive amplitude
        # (corresp. to bit "1").  Because we don't know the balance of
        # zeroes and ones in the input, we use 2-means clustering to
        # determine the "1" and "0" clusters.  In practice, some
        # systems use a random scrambler to XOR the input to balance
        # the zeroes and ones. We have decided to avoid that degree of
        # complexity in audiocom (for the time being, anyway).

  print "Detecting threshold with 2-means"

	# initialization
  center1 = min(demod_samples)
  center2 = max(demod_samples) 

  # insert code to implement 2-means clustering 	
  c1f = 0
  c1c = 0
  c2f = 0
  c2c = 0

  for x in xrange(0, len(demod_samples)):
    if(math.fabs(center1 - demod_samples[x]) > math.fabs(center2 - demod_samples[x])):
      c2f += demod_samples[x]
      c2c += 1
    else:
      c1f += demod_samples[x]
      c1c += 1

  center1 = c1f / c1c
  center2 = c2f / c2c

  one = 0.0
  zero = 0.0

  if(center1 > center2):
    one = center1
    zero = center2
  else:
    one = center2
    zero = center1
 
  # insert code to associate the higher of the two centers 
  # with one and the lower with zero
  
  print "Threshold for 1:"
  print one
  print "Threshold for 0:"
  print zero

  thresh = (one - zero) / 2

  # insert code to compute thresh
  return one, zero, thresh

    
