import sys
import math
import random
import numpy
import matplotlib
import os
try:
   if os.uname()[0] == 'Darwin':
     matplotlib.use('macosx')
except AttributeError:
   print ''

import matplotlib.pyplot as p
import matplotlib.mlab as mlab
import StringIO
import scipy.signal
import scipy.stats
import operator
from optparse import OptionParser

# import the channel class that utilizes the pyaudio infrastructure to send samples over the speaker/microphone audio link
import audio_channel as ach
import bypass_channel as bch
from transmitter import Transmitter 
from source import Source
from sink import Sink
from receiver import Receiver
from graphs import *

import common_srcsink
# Main program for the audio communication system
if __name__ == '__main__':

    # debugging helper
    #numpy.seterr(all='raise')
    print 'Running sendrecv.py'    
    if len(sys.argv) == 1:
        import config
        opt = config.Options()
    else:
        parser = OptionParser()
        # Source and Sink options
        parser.add_option("-m", "--monotone", type="int", dest="monotone", 
                          default=200, help="number of bits in monotone")
        parser.add_option("-f", "--file", type="string", dest="fname",
                          default=None, help="filename(s)")
        
        # Phy-layer Transmitter and Receiver options
        parser.add_option("-r", "--samplerate", type="int", dest="samplerate", 
                          default=48000, help="sample rate (Hz)")
        parser.add_option("-i", "--chunksize", type="int", dest="chunksize", 
                          default=256, help="samples per chunk (transmitter)")
        parser.add_option("-p", "--prefill", type="int", dest="prefill", 
                          default=60, help="write buffer prefill (transmitter)")
        parser.add_option("-s", "--spb", type="int", dest="spb", 
                          default=256, help="samples per bit")
        parser.add_option("-c", "--channel", type="int", dest="channel", 
                           default=1000, help="lowest carrier frequency (Hz)")
        parser.add_option("-q", "--silence", type="int", dest="silence",
                          default=80, help="#samples of silence at start of preamble")

        # Modulation (signaling) and Demodulation options
        parser.add_option("-o", "--one", type="float", dest="one",
                          default="1.0", help="voltage level for bit 1")

        # BypassChannel options
        parser.add_option("-b", "--bypass", action="store_true", dest="bypass",
                          default=False, help="use bypass channel instead of audio")
        parser.add_option("-z", "--noise", type="float", dest="noise", 
                          default=0.25, help="noise variance (for bypass channel)")
        parser.add_option("-l", "--lag", type="int", dest="lag", 
                          default='0', help="lag (for bypass channel)")
        parser.add_option("-u", "--usr", type="string", dest="h", 
                          default='1', help="unit step & sample response (h)")

        # Got graphs?
        parser.add_option("-g", "--graph", action="store_true", dest="graph",
                          default=False, help="show graphs")

        # Channel coding options
        parser.add_option("-H", "--Hamming", type="int", dest="cc_len",
                          default=7, help="Codeword length (n) of Hamming code")

        (opt,args) = parser.parse_args()

        

    fc = opt.channel
    # Print option summary:
    print 'Parameters in experiment:'
    print '\tSamples per bit:', opt.spb
    print '\tChannel type:', ('Audio' if not opt.bypass else 'Bypass')
    if opt.bypass:
        print '\t  Noise:', opt.noise, ' lag:', opt.lag, 'h: [', opt.h, ']'
    print '\tFrequency:', fc, 'Hz'
    print '\tHamming code n :', opt.cc_len
########################################################

    #instantiate and run the source block
    src = Source(opt.monotone, opt.fname)
    src_payload, databits = src.process()  

    # instantiate and run the transmitter block
    xmitter = Transmitter(fc, opt.samplerate, opt.one, opt.spb, opt.silence, opt.cc_len)
    coded_bits = xmitter.encode(databits)
    coded_bits_with_preamble = xmitter.add_preamble(coded_bits)
    samples = xmitter.bits_to_samples(coded_bits_with_preamble)
    mod_samples = xmitter.modulate(samples)

####################################    
    # create channel instance
    if opt.bypass:
        h = [float(x) for x in opt.h.split(' ')]
        channel = bch.BypassChannel(opt.noise, opt.lag, h)
    else:
        channel = ach.AudioChannel(opt.samplerate, opt.chunksize, opt.prefill)
        
    # transmit the samples, and retrieve samples back from the channel
    try:
        samples_rx = channel.xmit_and_recv(mod_samples)
    except ZeroDivisionError:
        # should only happen for audio channel
        print "I didn't get any samples; is your microphone or speaker OFF?"
        sys.exit(1)
#################################

    # process the received samples
    # make receiver
    r = Receiver(fc, opt.samplerate, opt.spb, 1)
    demod_samples = r.demodulate(samples_rx)
    one, zero, thresh = r.detect_threshold(demod_samples)
    barker_start = r.detect_preamble(demod_samples, thresh, one)
    rcdbits = r.demap_and_check(demod_samples, barker_start)
    decoded_bits = r.decode(rcdbits)

    # push into sink
    sink = Sink()
    rcd_payload = sink.process(decoded_bits)
    
    if len(rcd_payload) > 0:
        hd, err = common_srcsink.hamming(decoded_bits, databits)
        print 'Hamming distance for payload at frequency', fc,'Hz:', hd, 'BER:', err
    else:
        print 'Could not recover transmission.'

    if opt.graph:
                len_mod = len(mod_samples) - opt.spb*opt.silence 
                len_demod = len_mod - opt.spb*(len(src_payload) - len(rcd_payload))
                plot_graphs(mod_samples, samples_rx[barker_start:], demod_samples[barker_start:barker_start + len_demod], opt.spb, src.srctype, opt.silence)


