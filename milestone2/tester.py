# audiocom library: Source and sink functions
import common_srcsink as common
import Image
from graphs import *
import binascii
import random
import os
import itertools
from source import Source
from sink import Sink

# Some tests

src = Source(1000, "testfiles/32pix.png")
payload, databits = src.process()

print "\n\n------------------\n\n"

sink = Sink()
print sink.process(payload)