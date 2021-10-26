

all: img/src14_frame0.raw.png \
    lossless.csv \
    uniform.csv \
    jpicjpeg.csv \
    libjpeg.csv \
    size.png \
    psnr.png \
    ssim.png \
    encode.png \
    decode.png


lossless.csv:
	./lossless.sh > lossless.csv

libjpeg.csv:
	./libjpeg.sh > libjpeg.csv

uniform.csv:
	./uniform.sh > uniform.csv

jpicjpeg.csv:
	./jpicjpeg.sh > jpicjpeg.csv


psnr.png: libjpeg.csv uniform.csv
	~/proj/plotty/plotty-plot.py -d --sep ',' --xcol qp --xlabel "QP value" \
        --ycol psnr --ylabel "PSNR" --title "JPEG vs. JPIC Quality" \
        -i libjpeg.csv --label "jpeg" --fmt 'r.-' \
        -i uniform.csv --label "jpic-uniform" --fmt 'g.-' \
        -i jpicjpeg.csv --label "jpic-jpeg" --fmt 'b.-' \
        -i lossless.csv --label "jpic-lossless" --fmt 'k.-' \
        psnr.png

ssim.png: libjpeg.csv uniform.csv
	~/proj/plotty/plotty-plot.py -d --sep ',' --xcol qp --xlabel "QP value" \
        --ycol ssim --ylabel "PSNR" --title "JPEG vs. JPIC Quality" \
        -i libjpeg.csv --label "jpeg" --fmt 'r.-' \
        -i uniform.csv --label "jpic-uniform" --fmt 'g.-' \
        -i jpicjpeg.csv --label "jpic-jpeg" --fmt 'b.-' \
        -i lossless.csv --label "jpic-lossless" --fmt 'k.-' \
        ssim.png


size.png: libjpeg.csv uniform.csv
	~/proj/plotty/plotty-plot.py -d --sep ',' --xcol qp --xlabel "QP value" \
        --ycol size --ylabel "size (bytes)" --title "JPEG vs. JPIC Compression" \
        -i libjpeg.csv --label "jpeg" --fmt 'r.-' \
        -i uniform.csv --label "jpic-uniform" --fmt 'g.-' \
        -i jpicjpeg.csv --label "jpic-jpeg" --fmt 'b.-' \
        -i lossless.csv --label "jpic-lossless" --fmt 'k.-' \
        size.png


encode.png: libjpeg.csv uniform.csv
	~/proj/plotty/plotty-plot.py -d --sep ',' --xcol qp --xlabel "QP value" \
        --ycol encode --ylabel "time (sec)" --title "JPEG vs. JPIC Encoding Time" \
        -i libjpeg.csv --label "jpeg" --fmt 'r.-' \
        -i uniform.csv --label "jpic-uniform" --fmt 'g.-' \
        -i jpicjpeg.csv --label "jpic-jpeg" --fmt 'b.-' \
        -i lossless.csv --label "jpic-lossless" --fmt 'k.-' \
        encode.png

decode.png: libjpeg.csv uniform.csv
	~/proj/plotty/plotty-plot.py -d --sep ',' --xcol qp --xlabel "QP value" \
        --ycol decode --ylabel "time (sec)" --title "JPEG vs. JPIC Encoding Time" \
        -i libjpeg.csv --label "jpeg" --fmt 'r.-' \
        -i uniform.csv --label "jpic-uniform" --fmt 'g.-' \
        -i jpicjpeg.csv --label "jpic-jpeg" --fmt 'b.-' \
        -i lossless.csv --label "jpic-lossless" --fmt 'k.-' \
        decode.png

SRC_FILENAME=~/tmp/vqeg/src14_ref__720x480_420.yuv
SRC_FRAMENUM=0

# raw
img/src14_frame0.raw:
	./jpic.py encode -Q lossless --dump-input img/src14_frame0.raw --frame ${SRC_FRAMENUM} ${SRC_FILENAME} img/src14_frame0.lossless.jpic

img/src14_frame0.raw.png: img/src14_frame0.raw
	ffmpeg -y -f rawvideo -pixel_format yuv420p -s 720x480 -i $< $@

