#!/bin/bash

SRC_FILENAME=src14_frame0.raw
SRC_FRAMENUM=0

echo "#qp,encode,decode,size,psnr,ssim"
i=0
echo -n "$i,"
# encode raw file using jpic
echo -n "$(/usr/bin/time -f '%e' ./jpic.py encode -Q lossless --frame ${SRC_FRAMENUM} ${SRC_FILENAME} img/src14_frame0.lossless.jpic 2>&1 | tail -1),"
echo -n "$(/usr/bin/time -f '%e' ./jpic.py decode --dump-pgm img/src14_frame0.lossless.jpic.pgm img/src14_frame0.lossless.jpic img/src14_frame0.lossless.jpic.raw 2>&1 | tail -1),"
# produce a png copy
ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i img/src14_frame0.lossless.jpic.raw img/src14_frame0.lossless.jpic.raw.png &>> /dev/null
echo -n "$(stat -c '%s' img/src14_frame0.lossless.jpic),"
# get quality
echo -n "$(ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i ${SRC_FILENAME} -f rawvideo -pixel_format yuv420p -s 720x480 -i img/src14_frame0.lossless.jpic.raw -lavfi 'psnr' -f null - 2>&1 | grep Parsed_psnr_0 |sed 's/.*PSNR y:\([0-9\.]*\) .*/\1/'),"
echo -n "$(ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i ${SRC_FILENAME} -f rawvideo -pixel_format yuv420p -s 720x480 -i img/src14_frame0.lossless.jpic.raw -lavfi 'ssim' -f null - 2>&1 | grep Parsed_ssim_0 |sed 's/.*SSIM Y:\([0-9\.]*\) .*/\1/'),"
echo ""

