#!/bin/bash

# bash only: use for
echo "#qp,encode,decode,size,psnr,ssim"
for i in $(seq 1 31); do
	echo -n "$i,"
	# encode file
	echo -n "$(/usr/bin/time -f '%e' ffmpeg -hide_banner -y -f rawvideo -pixel_format yuv420p -s 720x480 -i img/src14_frame0.raw -q:v ${i} img/src14_frame0.libjpg.q_${i}.jpg 2>&1 | tail -1),"
	echo -n "$(/usr/bin/time -f '%e' ffmpeg -hide_banner -y -i img/src14_frame0.libjpg.q_${i}.jpg -f rawvideo -pix_fmt yuv420p -s 720x480 img/src14_frame0.libjpg.q_${i}.jpg.raw 2>&1 | tail -1),"
	echo -n "$(stat -c '%s' img/src14_frame0.libjpg.q_${i}.jpg),"
	echo -n "$(ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i img/src14_frame0.raw -i img/src14_frame0.libjpg.q_${i}.jpg -lavfi 'psnr' -f null - 2>&1 | grep Parsed_psnr_0 |sed 's/.*PSNR y:\([0-9\.]*\) .*/\1/'),"
	echo -n "$(ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i img/src14_frame0.raw -i img/src14_frame0.libjpg.q_${i}.jpg -lavfi 'ssim' -f null - 2>&1 | grep Parsed_ssim_0 |sed 's/.*SSIM Y:\([0-9\.]*\) .*/\1/'),"
	echo ""
done

