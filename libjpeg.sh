#!/bin/bash

# bash only: use for
echo "qp,size,psnr,ssim"
for i in $(seq 1 31); do
	echo -n "$i,"
	echo -n "$(stat -c '%s' src14_frame0.libjpg.q_${i}.jpg),"
	ffmpeg -hide_banner -y -f rawvideo -pixel_format yuv420p -s 720x480 -i src14_frame0.raw -q:v ${i} src14_frame0.libjpg.q_${i}.jpg 2>&1 | > /dev/null
	echo -n "$(ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i src14_frame0.raw -i src14_frame0.libjpg.q_${i}.jpg -lavfi "psnr" -f null - 2>&1 | grep Parsed_psnr_0 |sed 's/.*PSNR y:\([0-9\.]*\) .*/\1/'),"
	echo -n "$(ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i src14_frame0.raw -i src14_frame0.libjpg.q_${i}.jpg -lavfi "ssim" -f null - 2>&1 | grep Parsed_ssim_0 |sed 's/.*SSIM Y:\([0-9\.]*\) .*/\1/'),"
	echo ""
done


