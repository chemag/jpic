

all: src14_frame0.raw.png \
    src14_frame0.lossless.jpic.raw.png

SRC_FILENAME=~/tmp/vqeg/src14_ref__720x480_420.yuv
SRC_FRAMENUM=0

ssim: ssim.lossless

psnr: psnr.lossless

parse: parse.lossless

clean: clean.lossless

src14_frame0.lossless.jpic:
	./jpic.py encode -Q lossless --dump-input src14_frame0.raw --frame ${SRC_FRAMENUM} ${SRC_FILENAME} src14_frame0.lossless.jpic

src14_frame0.raw:
	./jpic.py encode -Q lossless --dump-input src14_frame0.raw --frame ${SRC_FRAMENUM} ${SRC_FILENAME} src14_frame0.lossless.jpic

src14_frame0.raw.png: src14_frame0.raw
	ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i $< $@

src14_frame0.lossless.jpic.pgm: src14_frame0.lossless.jpic
	./jpic.py decode --dump-pgm src14_frame0.lossless.jpic.pgm src14_frame0.lossless.jpic src14_frame0.lossless.jpic.raw

src14_frame0.lossless.jpic.raw: src14_frame0.lossless.jpic
	./jpic.py decode src14_frame0.lossless.jpic src14_frame0.lossless.jpic.raw

src14_frame0.lossless.jpic.raw.png: src14_frame0.lossless.jpic.raw
	ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i $< $@

ssim.lossless: src14_frame0.raw src14_frame0.lossless.jpic.raw
	ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i src14_frame0.raw -f rawvideo -pixel_format yuv420p -s 720x480 -i src14_frame0.lossless.jpic.raw  -lavfi "ssim" -f null -

psnr.lossless: src14_frame0.raw src14_frame0.lossless.jpic.raw
	ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i src14_frame0.raw -f rawvideo -pixel_format yuv420p -s 720x480 -i src14_frame0.lossless.jpic.raw  -lavfi "psnr" -f null -

parse.lossless:
	./jpic.py parse src14_frame0.lossless.jpic

clean.lossless:
	\rm -rf src14_frame0.raw src14_frame0.lossless.jpic src14_frame0.raw.png src14_frame0.lossless.jpic.pgm src14_frame0.lossless.jpic.raw src14_frame0.lossless.jpic.raw.png
