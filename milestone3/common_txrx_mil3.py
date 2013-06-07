import numpy
import math
import operator

# Methods common to both the transmitter and receiver
def modulate(fc, samplerate, samples):
  print " + Modulating with carrier frequency " + str(fc)
  return samples * numpy.cos(carrier_signal(fc, samplerate, len(samples)))

def carrier_signal(fc, samplerate, sz):
  return numpy.arange(0, sz) * fc * 2.0 * math.pi / (1.0 * samplerate)

def demodulate(fc, samplerate, samples):
  print " + Demodulating with carrier frequency " + str(fc)
  l = samples * numpy.cos(carrier_signal(fc, samplerate, len(samples)))
  Q = samples * numpy.sin(carrier_signal(fc, samplerate, len(samples))) * -1

  print " + Performing low pass filter for real components"
  lp = lpfilter(l, math.pi * fc / samplerate)

  print " + Performing low pass filter for imaginary components"
  lQ = lpfilter(Q, math.pi * fc / samplerate)

  print " + Outputting filtered signal"
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

  samples_in = numpy.concatenate(([0 for x in range(L)], samples_in, [0 for x in range(L)]))
  samples_in_numpy = numpy.array(samples_in)

  for n in xrange(-L, L):
    if n == 0:
      h.append(omega_cut / math.pi)
    else:
      h.append(math.sin(omega_cut * n) / (math.pi * n))
  
  h_numpy = numpy.array(h)

  out = []

  for n in xrange(0, len(samples_in_numpy)):
    si_left = max(0, n - L)
    si_right = min(len(samples_in_numpy) - 1, n + L)

    h_left = L - (n - si_left)
    h_right = L + (si_right - n)

    assert(si_right - si_left == h_right - h_left)

    out.append(numpy.dot(samples_in_numpy[si_left:si_right], h_numpy[h_left:h_right]))


  # compute the demodulated samples
  return out[L:len(out)-L]

