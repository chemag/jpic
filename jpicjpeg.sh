#!/bin/bash

SRC_FILENAME=~/tmp/vqeg/src14_ref__720x480_420.yuv
SRC_FRAMENUM=0

echo "#qp,encode,decode,size,psnr,ssim"
for i in $(seq 1 20); do
	echo -n "$i,"
	# encode raw file using jpic
  echo -n "$(/usr/bin/time -f '%e' ./jpic.py encode -Q jpeg-${i} --dump-input img/src14_frame0.raw --frame ${SRC_FRAMENUM} ${SRC_FILENAME} img/src14_frame0.jpeg-${i}.jpic 2>&1 | tail -1),"
  echo -n "$(/usr/bin/time -f '%e' ./jpic.py decode --dump-pgm img/src14_frame0.jpeg-${i}.jpic.pgm img/src14_frame0.jpeg-${i}.jpic img/src14_frame0.jpeg-${i}.jpic.raw 2>&1 | tail -1),"
	echo -n "$(stat -c '%s' img/src14_frame0.jpeg-${i}.jpic),"
	# get quality
	echo -n "$(ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i img/src14_frame0.raw -f rawvideo -pixel_format yuv420p -s 720x480 -i img/src14_frame0.jpeg-${i}.jpic.raw -lavfi 'psnr' -f null - 2>&1 | grep Parsed_psnr_0 |sed 's/.*PSNR y:\([0-9\.]*\) .*/\1/'),"
	echo -n "$(ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i img/src14_frame0.raw -f rawvideo -pixel_format yuv420p -s 720x480 -i img/src14_frame0.jpeg-${i}.jpic.raw -lavfi 'ssim' -f null - 2>&1 | grep Parsed_ssim_0 |sed 's/.*SSIM Y:\([0-9\.]*\) .*/\1/'),"
	echo ""
done


