#!/usr/bin/env python3

"""jpiclib."""

import bitstring
import numpy as np
import pickle

import huffman


def quantization(m, qtype, **kwargs):
    if qtype == 'lossless':
        return quantization_lossless(m)
    elif qtype.split('-')[0] == 'jpeg':
        is_luma = kwargs.get('luma')
        val = int(qtype.split('-')[1])
        return quantization_jpeg(m, is_luma, val)
    elif qtype.split('-')[0] == 'uniform':
        val = int(qtype.split('-')[1])
        return quantization_uniform(m, val)
    assert False, 'invalid quantization type: %s' % qtype


def quantization_rev(m, qtype, **kwargs):
    if qtype == 'lossless':
        return quantization_lossless_rev(m)
    elif qtype.split('-')[0] == 'jpeg':
        is_luma = kwargs.get('luma')
        val = int(qtype.split('-')[1])
        return quantization_jpeg_rev(m, is_luma, val)
    elif qtype.split('-')[0] == 'uniform':
        val = int(qtype.split('-')[1])
        return quantization_uniform_rev(m, val)
    assert False, 'invalid quantization type: %s' % qtype


def quantization_lossless(m):
    # just convert matrix to int
    return np.around(m).astype('int')


def quantization_lossless_rev(m):
    # just convert matrix to float
    return np.around(m).astype('float')


# https://www.sciencedirect.com/topics/engineering/quantization-table
QUANT_JPEG_Y = np.array([
    [16, 11, 10, 16,  24,  40,  51,  61],  # noqa: E201
    [12, 12, 14, 19,  26,  58,  60,  55],  # noqa: E201
    [14, 13, 16, 24,  40,  57,  69,  56],  # noqa: E201
    [14, 17, 22, 29,  51,  87,  80,  62],  # noqa: E201
    [18, 22, 37, 56,  68, 109, 103,  77],  # noqa: E201
    [24, 35, 55, 64,  81, 104, 113,  92],  # noqa: E201
    [49, 64, 78, 87, 103, 121, 120, 101],  # noqa: E201
    [72, 92, 95, 98, 112, 100, 103,  99],  # noqa: E201
])


QUANT_JPEG_C = np.array([
    [17, 18, 24, 47, 99, 99, 99, 99],
    [18, 21, 26, 66, 99, 99, 99, 99],
    [24, 26, 56, 99, 99, 99, 99, 99],
    [47, 66, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
])


def quantization_jpeg(m, is_luma, val):
    qm = np.copy(QUANT_JPEG_Y if is_luma else QUANT_JPEG_C)
    qm //= val
    return quantization_matrix(m, qm)


def quantization_jpeg_rev(m, is_luma, val):
    qm = np.copy(QUANT_JPEG_Y if is_luma else QUANT_JPEG_C)
    qm //= val
    return quantization_matrix_rev(m, qm)


QUANT_UNIFORM = np.array([
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
])


def quantization_uniform(m, val):
    qm = np.copy(QUANT_UNIFORM * val)
    return quantization_matrix(m, qm)


def quantization_uniform_rev(m, val):
    qm = np.copy(QUANT_UNIFORM * val)
    return quantization_matrix_rev(m, qm)


def quantization_matrix(m, qm):
    width, height = m.shape
    for i in range(0, width, 8):
        for j in range(0, height, 8):
            # get block using numpy subset view
            m[i:i+8, j:j+8] /= qm
    return np.around(m).astype('int')


def quantization_matrix_rev(m, qm):
    width, height = m.shape
    for i in range(0, width, 8):
        for j in range(0, height, 8):
            # get block using numpy subset view
            m[i:i+8, j:j+8] *= qm
    return np.around(m).astype('int')


ZIGZAG_ORDER = np.array([
    [ 0,  1,  5,  6, 14, 15, 27, 28],  # noqa: E201
    [ 2,  4,  7, 13, 16, 26, 29, 42],  # noqa: E201
    [ 3,  8, 12, 17, 25, 30, 41, 43],  # noqa: E201
    [ 9, 11, 18, 24, 31, 40, 44, 53],  # noqa: E201
    [10, 19, 23, 32, 39, 45, 52, 54],
    [20, 22, 33, 38, 46, 51, 55, 60],
    [21, 34, 37, 47, 50, 56, 59, 61],
    [35, 36, 48, 49, 57, 58, 62, 63],
])


def zigzag_block(block, order=ZIGZAG_ORDER):
    zigzag = np.zeros(64, dtype=np.int16)
    # map 8x8 vector to 1x64 vector
    for i in range(8):
        for j in range(8):
            # get output position
            index = order[i, j]
            zigzag[index] = block[i, j]
    return zigzag


def zigzag_scan(inp):
    # convert a wxh matrix (where both w and h are multiples of 8) into
    # a 64x(w*h/64) matrix with the coefficients zig-zagged
    width, height = inp.shape
    assert width % 8 == 0, 'width must be a multiple of 8 (%i)' % width
    assert height % 8 == 0, 'height must be a multiple of 8 (%i)' % height
    zigzag = np.zeros((int((width * height) / 64), 64), dtype=np.int16)
    bid = 0
    for i in range(0, width, 8):
        for j in range(0, height, 8):
            # get block using numpy subset view
            block = inp[i:i+8, j:j+8]
            zigzag[bid] = zigzag_block(block)
            bid += 1
    return zigzag


def zigzag_unblock(zigzag, order=ZIGZAG_ORDER):
    block = np.zeros((8, 8), dtype=np.int16)
    # map 1x64 vector to 8x8 vector
    for i in range(8):
        for j in range(8):
            # get output position
            index = order[i, j]
            block[i, j] = zigzag[index]
    return block


def zigzag_unscan(inp, width, height):
    # convert a 64x<numblocks> matrix (where `<numblocks> = width*height/64`)
    # matrix with the coefficients zig-zagged into a <width>x<height> matrix
    numblocks, sixtyfour = inp.shape
    assert sixtyfour == 64, 'zigzagged block must have 64 elements'
    assert width % 8 == 0, 'width must be a multiple of 8 (%i)' % width
    assert height % 8 == 0, 'height must be a multiple of 8 (%i)' % height
    assert numblocks * sixtyfour == width * height

    unzigzag = np.zeros((width, height), dtype=np.int16)
    bid = 0
    for i in range(0, width, 8):
        for j in range(0, height, 8):
            block = zigzag_unblock(inp[bid])
            # set block using numpy subset view
            unzigzag[i:i+8, j:j+8] = block
            bid += 1

    return unzigzag


def dc00_as_delta(inp):
    # basic approach: just get the delta from the previous value
    out = np.copy(inp)
    numblocks = inp.shape[0]
    for i in range(1, numblocks):
        out[i][0] = inp[i][0] - inp[i - 1][0]
    dc000 = out[0][0]
    out[0][0] = 0
    return dc000, out


def get_symbol_distribution(inp):
    symbol_distribution = {'EOB': 0}
    # calculate all the symbols
    numblocks = inp.shape[0]
    zerocnt = 0
    for i in range(0, numblocks):
        for j in range(1, 64):
            if inp[i][j] == 0:
                zerocnt += 1
                continue
            # new symbol
            symbol = '%i,%i' % (zerocnt, inp[i][j])
            if symbol not in symbol_distribution:
                symbol_distribution[symbol] = 0
            symbol_distribution[symbol] += 1
            zerocnt = 0
        if zerocnt != 0:
            symbol_distribution['EOB'] += 1
        zerocnt = 0
    # normalize frequencies to probabilities
    num_symbols = sum(symbol_distribution.values())
    for symbol in symbol_distribution:
        symbol_distribution[symbol] /= num_symbols
    # convert symbol distribution to listed sorted by occurrences
    symbol_distribution = sorted(symbol_distribution.items(),
                                 key=lambda x: x[1], reverse=True)
    return symbol_distribution


def get_encoding_table(inp):
    symbol_distribution = get_symbol_distribution(inp)
    huffman_code = huffman.HuffmanCode(symbol_distribution)
    for symbol in huffman_code.table:
        huffman_code.table[symbol] = bitstring.BitArray(
                '0b%s' % huffman_code.table[symbol])
    return huffman_code.table


def encode(inp, encoding_table):
    # create the output bitstring
    bits = bitstring.BitArray()
    # dc000, dinp = dc00_as_delta(inp)
    numblocks = inp.shape[0]
    zerocnt = 0
    for i in range(0, numblocks):
        # let's encode the DC component using uint16
        bits.append('int:16=%s' % inp[i][0])
        # let's encode the AC components using RLE
        for j in range(1, 64):
            if inp[i][j] == 0:
                zerocnt += 1
                continue
            # new symbol
            symbol = '%i,%i' % (zerocnt, inp[i][j])
            bits.append(encoding_table[symbol])
            zerocnt = 0
        if zerocnt != 0:
            # EOB
            symbol = 'EOB'
            bits.append(encoding_table[symbol])
        zerocnt = 0
    return bits


def decode(inp, width, height, encoding_table):
    zigzag = np.zeros((int((width * height) / 64), 64), dtype=np.int16)

    # we cannot just reverse keys and values as the values (BitArray) are
    # not hashable, and therefore not valid dictionary keys. Instead we will
    # use strings with 0's and 1's
    decoding_table = {val.bin: key for (key, val) in encoding_table.items()}

    bid = 0
    i = 0
    while i < len(inp):
        # let's decode the DC component using uint16
        j = 0
        zigzag[bid][j] = inp[i:i+16].int
        i += 16
        j += 1
        # let's decode the AC components using the decoding table
        while j < 64:
            encstr = ''
            while encstr not in decoding_table:
                # make sure the nexts bit is available
                assert i < len(inp), (
                    'decoder ran out of bits i: %i/%i bid: %i j:%i' % (
                        i, len(inp), bid, j))
                encstr += inp[i:i+1].bin
                i += 1
            symbol = decoding_table[encstr]
            if symbol == 'EOB':
                for _ in range(j, 64):
                    zigzag[bid][j] = 0
                    j += 1
            else:
                zerocnt, val = symbol.split(',')
                zerocnt, val = int(zerocnt), int(val)
                for _ in range(zerocnt):
                    zigzag[bid][j] = 0
                    j += 1
                zigzag[bid][j] = val
                j += 1
        bid += 1
    # make sure we read all the data
    assert zigzag.shape[0] == bid, (
        'error: only read %i rows (expecting %i)' % (bid, zigzag.shape[0]))
    return zigzag


def serialize_encoding_table(encoding_table):
    # TODO(chema): not sure this is a good idea
    return pickle.dumps(encoding_table)


def unserialize_encoding_table(encoding_table_bin):
    # TODO(chema): not sure this is a good idea
    return pickle.loads(encoding_table_bin)
