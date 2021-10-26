#!/usr/bin/env python3

"""utils."""


def read_as_bin(infile, size=-1, seek_pos=0):
    with open(infile, 'rb') as fin:
        if seek_pos > 0:
            fin.seek(seek_pos)
        data = fin.read(size)
        assert (size == -1) or (len(data) == size), (
            'cannot read %s in [%i, %i]' % (infile, seek_pos, seek_pos + size))
    return data


def write_as_bin(bstring, outfile):
    # write binary string into outfile
    with open(outfile, 'wb') as fout:
        fout.write(bstring)


def write_as_raw(buf, outfile):
    # write buffer into the outfile
    with open(outfile, 'wb') as fout:
        fout.write(buf)


def write_as_pgm(array, outfile):
    # write frame into the outfile (as pgm format)
    with open(outfile, 'w') as fout:
        height, width = array.shape
        # print pgm header
        fout.write('P2\n%i %i\n255\n' % (width, height))
        # print pgm contents
        for i in range(0, height):
            for j in range(0, width):
                fout.write('%i ' % array[i, j])
            fout.write('\n')
        fout.write('\n')
