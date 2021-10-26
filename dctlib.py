#!/usr/bin/env python3

"""dctlib."""

import argparse
import math
import numpy as np
import sys

import utils


default_values = {
    'debug': 0,
    'width': 720,
    'height': 480,
    'framenum': 0,
    'infile': None,
    'outfile': None,
}


# C
C = [1/math.sqrt(2), 1, 1, 1, 1, 1, 1, 1]


def get_1d_dct(s):
    # tu = Cu/2 \sum_{x=0}^7 sx cos((2x+1) \pi u / 16)
    t = np.zeros(8)
    for u in range(8):
        t[u] = 0
        for x in range(8):
            t[u] += s[x] * math.cos((2*x+1) * math.pi * u / 16)
        t[u] *= C[u] / 2
    return t


def get_1d_idct(t):
    # sx = 1/2 \sum_{u=0}^7 tu Cu cos((2x+1) \pi u / 16)
    s = np.zeros(8)
    for x in range(8):
        s[x] = 0
        for u in range(8):
            s[x] += t[u] * C[u] * math.cos((2*x+1) * math.pi * u / 16)
        s[x] *= 1 / 2
    return s


def get_block_dct(block):
    dct = np.zeros((8, 8))
    # perform horizontal DCT
    # row: block[0]
    # array([14., 14., 14., 14., 14., 14., 14., 14.])
    for i in range(8):
        dct[i] = get_1d_dct(block[i])

    # perform vertical DCT
    # column: block[:, 0]
    # array([ 14.,  81., 185.,  14.,  80., 182.,  14.,  84.])
    for j in range(8):
        dct[:, j] = get_1d_dct(dct[:, j])

    return dct


def get_block_idct(block):
    idct = np.zeros((8, 8))
    # perform horizontal IDCT
    # row: block[0]
    # array([14., 14., 14., 14., 14., 14., 14., 14.])
    for i in range(8):
        idct[i] = get_1d_idct(block[i])

    # perform vertical IDCT
    # column: block[:, 0]
    # array([ 14.,  81., 185.,  14.,  80., 182.,  14.,  84.])
    for j in range(8):
        idct[:, j] = get_1d_idct(idct[:, j])

    return idct


def get_frame_dct(inp):
    height, width = inp.shape
    dct = np.zeros((height, width))
    # break luma in 8x8 blocks
    for i in range(0, height, 8):
        for j in range(0, width, 8):
            # get block using numpy subset view
            # https://stackoverflow.com/questions/30917753/
            block = inp[i:i+8, j:j+8]
            outblock = get_block_dct(block)
            dct[i:i+8, j:j+8] = outblock
    return dct


def get_frame_idct(inp):
    height, width = inp.shape
    idct = np.zeros((height, width))
    # break luma in 8x8 blocks
    for i in range(0, height, 8):
        for j in range(0, width, 8):
            # get block using numpy subset view
            # https://stackoverflow.com/questions/30917753/
            block = inp[i:i+8, j:j+8]
            outblock = get_block_idct(block)
            idct[i:i+8, j:j+8] = outblock
    # return integer matrix
    return idct.round().astype('uint8')


# returns an 8x8 matrix with the mean of all the values in a DCT matrix
def get_frame_block_mean(inp):
    mean = np.zeros((8, 8))
    # break luma in 8x8 blocks
    for i in range(0, 8):
        for j in range(0, 8):
            # get all values at position (i, j)
            m = inp[i::8, j::8]
            mean[i, j] = m.mean()
    return mean


# returns an 8x8 matrix with the mean square error of all the values
# in a DCT matrix
def get_frame_block_rmse(inp):
    rmse = np.zeros((8, 8))
    # break luma in 8x8 blocks
    for i in range(0, 8):
        for j in range(0, 8):
            # get all values at position (i, j)
            m = inp[i::8, j::8]
            # root mean square for coordinate (i,j) is
            # $s^2 = \frac{1}{n-1} \sum (x_i - \bar(x))^2$
            n = m.size
            rmse[i, j] = 1/(n-1) * ((m - m.mean()) ** 2).sum()
    return rmse


def process_frame(y, u, v):
    # convert luma matrix to float64
    y = y.astype('float64')
    dct_y = get_frame_dct(y)
    return dct_y


def read_frame(infile, width, height, framenum=0):
    # assume 4:2:0 subsampling
    frame_size = int(width * height * 1.5)
    # read raw data from infile
    frame_data = utils.read_as_bin(infile, frame_size, framenum * frame_size)
    return frame_data


def parse_420_buffer(frame_data, width, height):
    # calculate 4:2:0 parameters
    width_y = width
    height_y = height
    width_c = width_y >> 1
    height_c = height_y >> 1
    # read luma and chromas
    y = np.frombuffer(frame_data[:(width_y * height_y)], dtype=np.uint8)
    y.shape = (height_y, width_y)
    y = y.astype('float64')
    u = np.frombuffer(frame_data[(width_y * height_y):
                                 int(width_y * height_y * 1.25)],
                      dtype=np.uint8)
    u.shape = (height_c, width_c)
    u = u.astype('float64')
    v = np.frombuffer(frame_data[int(width_y * height_y * 1.25):],
                      dtype=np.uint8)
    v.shape = (height_c, width_c)
    v = v.astype('float64')
    return y, u, v


def dump_420_buffer(y, u, v):
    buf = b''
    # dump luma and chromas
    buf += y.tostring()
    if u is not None:
        buf += u.tostring()
    if v is not None:
        buf += v.tostring()
    return buf


def process_file(options):
    y, u, v = read_frame(options.infile, options.width, options.height,
                         options.framenum)

    # process luma
    dct_y = get_frame_dct(y)
    dct_y_mean = get_frame_block_mean(dct_y)
    dct_y_rmse = get_frame_block_rmse(dct_y)

    # print results
    print('mean:\n%s\n' % dct_y_mean.astype('int'))
    print('rmse:\n%s\n' % dct_y_rmse.astype('int'))

    # convert frame back using idct
    idct_y = get_frame_idct(dct_y)
    # need to round before converting back to int
    # https://stackoverflow.com/questions/43910477/
    idct_y = np.around(idct_y).astype('int')

    # recover frame into the outfile (as pgm format)
    utils.write_as_pgm(idct_y, options.outfile)


def get_options(argv):
    """Generic option parser.

    Args:
        argv: list containing arguments

    Returns:
        Namespace - An argparse.ArgumentParser-generated option object
    """
    # init parser
    # usage = 'usage: %prog [options] arg1 arg2'
    # parser = argparse.OptionParser(usage=usage)
    # parser.print_help() to get argparse.usage (large help)
    # parser.print_usage() to get argparse.usage (just usage line)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
            '-d', '--debug', action='count',
            dest='debug', default=default_values['debug'],
            help='Increase verbosity (use multiple times for more)',)
    parser.add_argument(
            '--quiet', action='store_const',
            dest='debug', const=-1,
            help='Zero verbosity',)
    # 2-parameter setter using argparse.Action
    parser.add_argument(
            '--width', action='store', type=int,
            dest='width', default=default_values['width'],
            metavar='WIDTH',
            help=('use WIDTH width (default: %i)' % default_values['width']),)
    parser.add_argument(
            '--height', action='store', type=int,
            dest='height', default=default_values['height'],
            metavar='HEIGHT',
            help=('HEIGHT height (default: %i)' % default_values['height']),)

    class VideoSizeAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            namespace.width, namespace.height = [int(v) for v in
                                                 values[0].split('x')]
    parser.add_argument(
            '--video_size', action=VideoSizeAction, nargs=1,
            help='use <width>x<height>',)
    parser.add_argument(
            '--framenum', action='store', type=int,
            dest='framenum', default=default_values['framenum'],
            metavar='FRAMENUM',
            help=('FRAMENUM (default: %i)' % default_values['framenum']),)

    parser.add_argument(
            'infile', type=str,
            default=default_values['infile'],
            metavar='input-file',
            help='input file',)
    parser.add_argument(
            'outfile', type=str,
            default=default_values['outfile'],
            metavar='output-file',
            help='output file',)
    # do the parsing
    options = parser.parse_args(argv[1:])
    return options


def main(argv):
    # parse options
    options = get_options(argv)
    # get infile/outfile
    if options.infile == '-':
        options.infile = '/dev/fd/0'
    if options.outfile == '-':
        options.outfile = '/dev/fd/1'
    # print results
    if options.debug > 0:
        print(options)
    # do something
    process_file(options)


if __name__ == '__main__':
    # at least the CLI program name: (CLI) execution
    main(sys.argv)
