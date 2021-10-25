

all: img/src14_frame0.raw.png \
    img/src14_frame0.lossless.jpic.raw.png \
    img/src14_frame0.jpeg.jpic.raw.png \
    img/src14_frame0.uniform-2.jpic.raw.png \
    img/src14_frame0.uniform-10.jpic.raw.png \
    img/src14_frame0.uniform-20.jpic.raw.png \
    libjpeg.csv


libjpeg.csv:
	./libjpeg.sh  > libjpeg.csv


SRC_FILENAME=~/tmp/vqeg/src14_ref__720x480_420.yuv
SRC_FRAMENUM=0

ssim: ssim.lossless \
    ssim.jpeg \
    ssim.uniform-2 \
    ssim.uniform-10 \
    ssim.uniform-20

psnr: psnr.lossless \
    psnr.jpeg \
    psnr.uniform-2 \
    psnr.uniform-10 \
    psnr.uniform-20

parse: parse.lossless \
    parse.jpeg \
    parse.uniform-2 \
    parse.uniform-10 \
    parse.uniform-20

clean: clean.lossless \
    clean.jpeg \
    clean.uniform-2 \
    clean.uniform-10 \
    clean.uniform-20

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
src14_frame0.jpeg.jpic:
	./jpic.py encode -Q jpeg --dump-input src14_frame0.raw --frame ${SRC_FRAMENUM} ${SRC_FILENAME} src14_frame0.jpeg.jpic

src14_frame0.jpeg.jpic.pgm: src14_frame0.jpeg.jpic
	./jpic.py decode --dump-pgm src14_frame0.jpeg.jpic.pgm src14_frame0.jpeg.jpic src14_frame0.jpeg.jpic.raw

src14_frame0.jpeg.jpic.raw: src14_frame0.jpeg.jpic
	./jpic.py decode src14_frame0.jpeg.jpic src14_frame0.jpeg.jpic.raw

src14_frame0.jpeg.jpic.raw.png: src14_frame0.jpeg.jpic.raw
	ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i $< $@

ssim.jpeg: src14_frame0.raw src14_frame0.jpeg.jpic.raw
	ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i src14_frame0.raw -f rawvideo -pixel_format yuv420p -s 720x480 -i src14_frame0.jpeg.jpic.raw  -lavfi "ssim" -f null - 2>&1 | grep Parsed_ssim_0

psnr.jpeg: src14_frame0.raw src14_frame0.jpeg.jpic.raw
	ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i src14_frame0.raw -f rawvideo -pixel_format yuv420p -s 720x480 -i src14_frame0.jpeg.jpic.raw  -lavfi "psnr" -f null - 2>&1 | grep Parsed_psnr_0

parse.jpeg:
	./jpic.py parse src14_frame0.jpeg.jpic

clean.jpeg:
	\rm -rf src14_frame0.raw src14_frame0.jpeg.jpic src14_frame0.raw.png src14_frame0.jpeg.jpic.pgm src14_frame0.jpeg.jpic.raw src14_frame0.jpeg.jpic.raw.png

# uniform-2
src14_frame0.uniform-2.jpic:
	./jpic.py encode -Q uniform-2 --dump-input src14_frame0.raw --frame ${SRC_FRAMENUM} ${SRC_FILENAME} src14_frame0.uniform-2.jpic

src14_frame0.uniform-2.jpic.pgm: src14_frame0.uniform-2.jpic
	./jpic.py decode --dump-pgm src14_frame0.uniform-2.jpic.pgm src14_frame0.uniform-2.jpic src14_frame0.uniform-2.jpic.raw

src14_frame0.uniform-2.jpic.raw: src14_frame0.uniform-2.jpic
	./jpic.py decode src14_frame0.uniform-2.jpic src14_frame0.uniform-2.jpic.raw

src14_frame0.uniform-2.jpic.raw.png: src14_frame0.uniform-2.jpic.raw
	ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i $< $@

ssim.uniform-2: src14_frame0.raw src14_frame0.uniform-2.jpic.raw
	ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i src14_frame0.raw -f rawvideo -pixel_format yuv420p -s 720x480 -i src14_frame0.uniform-2.jpic.raw  -lavfi "ssim" -f null - 2>&1 | grep Parsed_ssim_0

psnr.uniform-2: src14_frame0.raw src14_frame0.uniform-2.jpic.raw
	ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i src14_frame0.raw -f rawvideo -pixel_format yuv420p -s 720x480 -i src14_frame0.uniform-2.jpic.raw  -lavfi "psnr" -f null - 2>&1 | grep Parsed_psnr_0

parse.uniform-2:
	./jpic.py parse src14_frame0.uniform-2.jpic

clean.uniform-2:
	\rm -rf src14_frame0.raw src14_frame0.uniform-2.jpic src14_frame0.raw.png src14_frame0.uniform-2.jpic.pgm src14_frame0.uniform-2.jpic.raw src14_frame0.uniform-2.jpic.raw.png

# uniform-10
src14_frame0.uniform-10.jpic:
	./jpic.py encode -Q uniform-10 --dump-input src14_frame0.raw --frame ${SRC_FRAMENUM} ${SRC_FILENAME} src14_frame0.uniform-10.jpic

src14_frame0.uniform-10.jpic.pgm: src14_frame0.uniform-10.jpic
	./jpic.py decode --dump-pgm src14_frame0.uniform-10.jpic.pgm src14_frame0.uniform-10.jpic src14_frame0.uniform-10.jpic.raw

src14_frame0.uniform-10.jpic.raw: src14_frame0.uniform-10.jpic
	./jpic.py decode src14_frame0.uniform-10.jpic src14_frame0.uniform-10.jpic.raw

src14_frame0.uniform-10.jpic.raw.png: src14_frame0.uniform-10.jpic.raw
	ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i $< $@

ssim.uniform-10: src14_frame0.raw src14_frame0.uniform-10.jpic.raw
	ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i src14_frame0.raw -f rawvideo -pixel_format yuv420p -s 720x480 -i src14_frame0.uniform-10.jpic.raw  -lavfi "ssim" -f null - 2>&1 | grep Parsed_ssim_0

psnr.uniform-10: src14_frame0.raw src14_frame0.uniform-10.jpic.raw
	ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i src14_frame0.raw -f rawvideo -pixel_format yuv420p -s 720x480 -i src14_frame0.uniform-10.jpic.raw  -lavfi "psnr" -f null - 2>&1 | grep Parsed_psnr_0

parse.uniform-10:
	./jpic.py parse src14_frame0.uniform-10.jpic

clean.uniform-10:
	\rm -rf src14_frame0.raw src14_frame0.uniform-10.jpic src14_frame0.raw.png src14_frame0.uniform-10.jpic.pgm src14_frame0.uniform-10.jpic.raw src14_frame0.uniform-10.jpic.raw.png

# uniform-20
src14_frame0.uniform-20.jpic:
	./jpic.py encode -Q uniform-20 --dump-input src14_frame0.raw --frame ${SRC_FRAMENUM} ${SRC_FILENAME} src14_frame0.uniform-20.jpic

src14_frame0.uniform-20.jpic.pgm: src14_frame0.uniform-20.jpic
	./jpic.py decode --dump-pgm src14_frame0.uniform-20.jpic.pgm src14_frame0.uniform-20.jpic src14_frame0.uniform-20.jpic.raw

src14_frame0.uniform-20.jpic.raw: src14_frame0.uniform-20.jpic
	./jpic.py decode src14_frame0.uniform-20.jpic src14_frame0.uniform-20.jpic.raw

src14_frame0.uniform-20.jpic.raw.png: src14_frame0.uniform-20.jpic.raw
	ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i $< $@

ssim.uniform-20: src14_frame0.raw src14_frame0.uniform-20.jpic.raw
	ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i src14_frame0.raw -f rawvideo -pixel_format yuv420p -s 720x480 -i src14_frame0.uniform-20.jpic.raw  -lavfi "ssim" -f null - 2>&1 | grep Parsed_ssim_0

psnr.uniform-20: src14_frame0.raw src14_frame0.uniform-20.jpic.raw
	ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i src14_frame0.raw -f rawvideo -pixel_format yuv420p -s 720x480 -i src14_frame0.uniform-20.jpic.raw  -lavfi "psnr" -f null - 2>&1 | grep Parsed_psnr_0

parse.uniform-20:
	./jpic.py parse src14_frame0.uniform-20.jpic

clean.uniform-20:
	\rm -rf src14_frame0.raw src14_frame0.uniform-20.jpic src14_frame0.raw.png src14_frame0.uniform-20.jpic.pgm src14_frame0.uniform-20.jpic.raw src14_frame0.uniform-20.jpic.raw.png

