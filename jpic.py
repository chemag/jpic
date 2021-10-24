#!/usr/bin/env python3

"""dctlib."""

import argparse
import bitstring
import math
import struct
import sys


import dctlib
import jpiclib
import utils


FUNCTION_CHOICES = ['encode', 'decode', 'parse']


default_values = {
    'debug': 0,
    'width': 720,
    'height': 480,
    'framenum': 0,
    'dump_input': None,
    'dump_pgm': None,
    'function': 'encode',
    'infile': None,
    'outfile': None,
}


def encode_file(frame_data, width, height):
    # convert into numpy arrays
    y, u, v = dctlib.parse_420_buffer(frame_data, width, height)

    description = ''
    description += 'color: yuv\n'
    description += 'width: %i\n' % width
    description += 'height: %i\n' % height

    # 1. DCT transform
    # process luma
    y_dct = dctlib.get_frame_dct(y)
    description += 'transform: dct\n'

    # 2. quantization
    y_dct_q = jpiclib.quantization_uniform(y_dct)
    description += 'quantization: uniform\n'

    # 3. zig-zag scan
    y_dct_q_z = jpiclib.zigzag_scan(y_dct_q)
    description += 'zigzag: basic\n'

    # 4. huffman coding and RLE
    # jpiclib.dc00_as_delta(y_dct_q_z)
    y_enc_table = jpiclib.get_encoding_table(y_dct_q_z)
    y_enc_bits = jpiclib.encode(y_dct_q_z, y_enc_table)
    description += 'encoding: basic\n'

    # 5. put everything together using a TLV approach (L in bits)
    out = b''
    # 5.1. header
    out += b'jpic'
    # 5.2. description
    out += b'desc'
    description_bitlen = len(description) * 8
    out += struct.pack('=l', description_bitlen)
    out += str.encode(description)
    # 5.3. encoding table
    # serialize encoding table
    y_enc_table_bin = jpiclib.serialize_encoding_table(y_enc_table)
    out += b'ytbl'
    y_enc_table_bitlen = len(y_enc_table_bin) * 8
    out += struct.pack('=l', y_enc_table_bitlen)
    out += y_enc_table_bin
    # 5.4. encoding luma
    out += b'plny'
    # BitArray's return their length in bits
    y_enc_bitlen = len(y_enc_bits)
    out += struct.pack('=l', y_enc_bitlen)
    out += y_enc_bits.tobytes()
    return out


def decode_file(bstring):
    # 1. parse the jpic file (TLV approach, with L in bits)
    i = 0
    # 1.1. header
    header = bstring[i:i + 4]
    i += 4
    assert header == b'jpic', 'non-jpic file: no jpic'
    # 1.2. description
    tag = bstring[i:i + 4]
    i += 4
    assert tag == b'desc', 'invalid jpic file: no desc'
    description_bitlen = struct.unpack('=l', bstring[i:i + 4])[0]
    i += 4
    description_len = description_bitlen >> 3
    description_bits = bstring[i:i + description_len]
    i += description_len
    # 1.3. encoding table
    tag = bstring[i:i + 4]
    i += 4
    assert tag == b'ytbl', 'invalid jpic file: no ytbl'
    y_enc_table_bitlen = struct.unpack('=l', bstring[i:i + 4])[0]
    i += 4
    y_enc_table_len = y_enc_table_bitlen >> 3
    y_enc_table_bin = bstring[i:i + y_enc_table_len]
    i += y_enc_table_len
    y_enc_table = jpiclib.unserialize_encoding_table(y_enc_table_bin)
    # 1.4. encoding bits
    tag = bstring[i:i + 4]
    i += 4
    assert tag == b'plny', 'invalid jpic file: no plny'
    y_enc_bitlen = struct.unpack('=l', bstring[i:i + 4])[0]
    i += 4
    y_enc_len = int(math.ceil(y_enc_bitlen / 8))
    y_enc_binary = bstring[i:i + y_enc_len]
    i += y_enc_len
    y_enc_bits = bitstring.BitArray(y_enc_binary)
    # adjust the length of luma to the bit
    del y_enc_bits[y_enc_bitlen:]
    # 1.5. parse description
    description = description_bits.decode('ascii')
    info = {}
    for line in description.split('\n'):
        if not line:
            continue
        key, value = line.split(': ')
        info[key] = value
    width = int(info['width'])
    height = int(info['height'])

    # 2. huffman coding and RLE
    # jpiclib.dc00_as_delta(y_dct_q_z)
    y_dct_q_z = jpiclib.decode(y_enc_bits, width, height, y_enc_table)

    # 3. un-zig-zag scan
    y_dct_q = jpiclib.zigzag_unscan(y_dct_q_z, width, height)

    # 4. reverse quantization
    y_dct = jpiclib.quantization_uniform_rev(y_dct_q)

    # 5. IDCT transform
    # process luma
    y = dctlib.get_frame_idct(y_dct)

    return y, None, None


def parse_file(bstring):
    size = []
    # 1. parse the jpic file (TLV approach, with L in bits)
    i = 0
    # 1.1. header
    header = bstring[i:i + 4]
    i += 4
    assert header == b'jpic', 'non-jpic file: no jpic'
    size.append(['jpic', 4])

    # 1.2. description
    tag = bstring[i:i + 4]
    i += 4
    assert tag == b'desc', 'invalid jpic file: no desc'
    description_bitlen = struct.unpack('=l', bstring[i:i + 4])[0]
    i += 4
    description_len = description_bitlen >> 3
    description_bits = bstring[i:i + description_len]
    i += description_len
    size.append(['desc', 4 + 4 + description_len])

    # 1.3. encoding table
    tag = bstring[i:i + 4]
    i += 4
    assert tag == b'ytbl', 'invalid jpic file: no ytbl'
    y_enc_table_bitlen = struct.unpack('=l', bstring[i:i + 4])[0]
    i += 4
    y_enc_table_len = y_enc_table_bitlen >> 3
    i += y_enc_table_len
    size.append(['ytbl', 4 + 4 + y_enc_table_len])

    # 1.4. encoding bits
    tag = bstring[i:i + 4]
    i += 4
    assert tag == b'plny', 'invalid jpic file: no plny'
    y_enc_bitlen = struct.unpack('=l', bstring[i:i + 4])[0]
    i += 4
    y_enc_len = int(math.ceil(y_enc_bitlen / 8))
    i += y_enc_len
    size.append(['plny', 4 + 4 + y_enc_len])

    # 1.5. parse description
    description = description_bits.decode('ascii')
    info = {}
    for line in description.split('\n'):
        if not line:
            continue
        key, value = line.split(': ')
        info[key] = value

    return info, size


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
            'function', type=str,
            default=default_values['function'],
            choices=FUNCTION_CHOICES,
            metavar='function',
            help='function',)
    parser.add_argument(
            '-E', '--encode', action='store_const',
            dest='function', const='encode',
            help='Encode file',)
    parser.add_argument(
            '-D', '--decode', action='store_const',
            dest='function', const='decode',
            help='Decode file',)
    parser.add_argument(
            '-P', '--parse', action='store_const',
            dest='function', const='parse',
            help='Parse file',)
    parser.add_argument(
            '--dump-input', type=str,
            default=default_values['dump_input'],
            metavar='dump_input',
            help='dump_input',)
    parser.add_argument(
            '--dump-pgm', type=str,
            default=default_values['dump_pgm'],
            metavar='dump_pgm',
            help='dump_pgm',)
    parser.add_argument(
            'infile', type=str,
            default=default_values['infile'],
            metavar='input-file',
            help='input file',)
    parser.add_argument(
            'outfile', type=str, nargs='?',
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
    if options.function == 'encode':
        frame_data = dctlib.read_frame(options.infile, options.width,
                                       options.height, options.framenum)
        if options.dump_input:
            utils.write_as_raw(frame_data, options.dump_input)
        out = encode_file(frame_data, options.width, options.height)
        utils.write_as_bin(out, options.outfile)

    elif options.function == 'decode':
        bstring = utils.read_as_bin(options.infile)
        y, u, v = decode_file(bstring)
        if options.dump_pgm:
            utils.write_as_pgm(y, options.dump_pgm)
        out = dctlib.dump_420_buffer(y, u, v)
        utils.write_as_raw(out, options.outfile)

    elif options.function == 'parse':
        bstring = utils.read_as_bin(options.infile)
        info, size = parse_file(bstring)
        print(info)
        print(size)


if __name__ == '__main__':
    # at least the CLI program name: (CLI) execution
    main(sys.argv)
