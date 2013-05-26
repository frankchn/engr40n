import numpy
import math
import operator

# Methods common to both the transmitter and receiver
def modulate(fc, samplerate, samples):
  print "Modulating with carrier frequency " + str(fc)
  return samples * numpy.cos(carrier_signal(fc, samplerate, len(samples)))

def carrier_signal(fc, samplerate, sz):
  return numpy.arange(0, sz) * fc * 2 * math.pi / samplerate

def demodulate(fc, samplerate, samples):
  print "Demodulating with carrier frequency " + str(fc)
  l = samples * numpy.cos(carrier_signal(fc, samplerate, len(samples)))
  Q = samples * -1 * numpy.sin(carrier_signal(fc, samplerate, len(samples)))

  print "Performing low pass filter"
  lp = lpfilter(l, math.pi * fc / samplerate)
  lQ = lpfilter(Q, math.pi * fc / samplerate)

  out = []
  for n in xrange(0, len(samples)):
    out.append(math.sqrt(math.pow(lp[n], 2) + math.pow(lQ[n], 2)))

  return out

def lpfilter(samples_in, omega_cut):
  '''
  A low-pass filter of frequency omega_cut.
  '''
  L = 50
  h = [] # shifted by 50

  for n in xrange(-L, L):
    if n == 0:
      h.append(omega_cut / math.pi)
    else:
      h.append(math.sin(omega_cut * n) / (math.pi * n))
  
  out = []
  for n in xrange(0, len(samples_in)):
    accu = 0
    for x in xrange(-L, L):
      ai = n + x - L
      if(ai < 0 or ai >= n):
        continue
      accu += samples_in[ai] * h[x - L]
    out.append(accu)

  # compute the demodulated samples
  return out

