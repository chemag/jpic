

all: img/src14_frame0.raw.png \
    img/src14_frame0.lossless.jpic.raw.png \
    img/src14_frame0.jpeg.jpic.raw.png \
    uniform.csv \
    libjpeg.csv


libjpeg.csv:
	./libjpeg.sh  > libjpeg.csv


uniform.csv:
	./uniform.sh  > uniform.csv


jpicjpeg.csv:
	./jpicjpeg.sh  > jpicjpeg.csv


psnr.png: libjpeg.csv uniform.csv
	~/proj/plotty/plotty-plot.py -d  --sep ',' --xcol qp --xlabel "QP value" --ycol psnr --ylabel "PSNR" --title "JPEG vs. JPIC Quality" -i libjpeg.csv --label "jpeg" --fmt 'r.-' -i uniform.csv --label "jpic-uniform" --fmt 'g.-' psnr.png

size.png: libjpeg.csv uniform.csv
	~/proj/plotty/plotty-plot.py -d  --sep ',' --xcol qp --xlabel "QP value" --ycol size --ylabel "size (bytes)"  --title "JPEG vs. JPIC Compression" -i libjpeg.csv --label "jpeg" --fmt 'r.-' -i uniform.csv --label "jpic-uniform" --fmt 'g.-' size.png


SRC_FILENAME=~/tmp/vqeg/src14_ref__720x480_420.yuv
SRC_FRAMENUM=0

ssim: ssim.lossless \
    ssim.jpeg

psnr: psnr.lossless \
    psnr.jpeg

parse: parse.lossless \
    parse.jpeg

clean: clean.lossless \
    clean.jpeg

# raw
img/src14_frame0.raw:
	./jpic.py encode -Q lossless --dump-input img/src14_frame0.raw --frame ${SRC_FRAMENUM} ${SRC_FILENAME} img/src14_frame0.lossless.jpic

img/src14_frame0.raw.png: img/src14_frame0.raw
	ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i $< $@


# lossless
img/src14_frame0.lossless.jpic:
	./jpic.py encode -Q lossless --dump-input img/src14_frame0.raw --frame ${SRC_FRAMENUM} ${SRC_FILENAME} img/src14_frame0.lossless.jpic

img/src14_frame0.lossless.jpic.pgm: img/src14_frame0.lossless.jpic
	./jpic.py decode --dump-pgm img/src14_frame0.lossless.jpic.pgm img/src14_frame0.lossless.jpic img/src14_frame0.lossless.jpic.raw

img/src14_frame0.lossless.jpic.raw: img/src14_frame0.lossless.jpic
	./jpic.py decode img/src14_frame0.lossless.jpic img/src14_frame0.lossless.jpic.raw

img/src14_frame0.lossless.jpic.raw.png: img/src14_frame0.lossless.jpic.raw
	ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i $< $@

ssim.lossless: img/src14_frame0.raw img/src14_frame0.lossless.jpic.raw
	ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i img/src14_frame0.raw -f rawvideo -pixel_format yuv420p -s 720x480 -i img/src14_frame0.lossless.jpic.raw  -lavfi "ssim" -f null - 2>&1 | grep Parsed_ssim_0

psnr.lossless: img/src14_frame0.raw img/src14_frame0.lossless.jpic.raw
	ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i img/src14_frame0.raw -f rawvideo -pixel_format yuv420p -s 720x480 -i img/src14_frame0.lossless.jpic.raw  -lavfi "psnr" -f null - 2>&1 | grep Parsed_psnr_0

parse.lossless:
	./jpic.py parse img/src14_frame0.lossless.jpic

clean.lossless:
	\rm -rf img/src14_frame0.raw img/src14_frame0.lossless.jpic img/src14_frame0.raw.png img/src14_frame0.lossless.jpic.pgm img/src14_frame0.lossless.jpic.raw img/src14_frame0.lossless.jpic.raw.png

# jpeg
img/src14_frame0.jpeg.jpic:
	./jpic.py encode -Q jpeg --dump-input img/src14_frame0.raw --frame ${SRC_FRAMENUM} ${SRC_FILENAME} img/src14_frame0.jpeg.jpic

img/src14_frame0.jpeg.jpic.pgm: img/src14_frame0.jpeg.jpic
	./jpic.py decode --dump-pgm img/src14_frame0.jpeg.jpic.pgm img/src14_frame0.jpeg.jpic img/src14_frame0.jpeg.jpic.raw

img/src14_frame0.jpeg.jpic.raw: img/src14_frame0.jpeg.jpic
	./jpic.py decode img/src14_frame0.jpeg.jpic img/src14_frame0.jpeg.jpic.raw

img/src14_frame0.jpeg.jpic.raw.png: img/src14_frame0.jpeg.jpic.raw
	ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i $< $@

ssim.jpeg: img/src14_frame0.raw img/src14_frame0.jpeg.jpic.raw
	ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i img/src14_frame0.raw -f rawvideo -pixel_format yuv420p -s 720x480 -i img/src14_frame0.jpeg.jpic.raw  -lavfi "ssim" -f null - 2>&1 | grep Parsed_ssim_0

psnr.jpeg: img/src14_frame0.raw img/src14_frame0.jpeg.jpic.raw
	ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i img/src14_frame0.raw -f rawvideo -pixel_format yuv420p -s 720x480 -i img/src14_frame0.jpeg.jpic.raw  -lavfi "psnr" -f null - 2>&1 | grep Parsed_psnr_0

parse.jpeg:
	./jpic.py parse img/src14_frame0.jpeg.jpic

clean.jpeg:
	\rm -rf img/src14_frame0.raw img/src14_frame0.jpeg.jpic img/src14_frame0.raw.png img/src14_frame0.jpeg.jpic.pgm img/src14_frame0.jpeg.jpic.raw img/src14_frame0.jpeg.jpic.raw.png

