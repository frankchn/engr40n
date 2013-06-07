#!/bin/bash

i="0"

while [ $i -lt 10 ]
do

	python sendrecv_coding.py -f testfiles/32pix.png -c 1000 -s 64 -q 10 -b -z 2.0 -H 7 | tee -a 32pix-2-7.txt
	i=$[$i+1]

done

i="0"

while [ $i -lt 10 ]
do

	python sendrecv_coding.py -f testfiles/32pix.png -c 1000 -s 64 -q 10 -b -z 2.0 -H 31 | tee -a 32pix-2-31.txt
	i=$[$i+1]

done

i="0"

while [ $i -lt 10 ]
do

	python sendrecv_coding.py -f testfiles/32pix.png -c 1000 -s 64 -q 10 -b -z 2.7 -H 7 | tee -a 32pix-27-7.txt
	i=$[$i+1]

done

i="0"

while [ $i -lt 10 ]
do

	python sendrecv_coding.py -f testfiles/32pix.png -c 1000 -s 64 -q 10 -b -z 2.7 -H 31 | tee -a 32pix-27-31.txt
	i=$[$i+1]

done