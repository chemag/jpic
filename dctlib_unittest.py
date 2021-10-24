#!/usr/bin/env python3

"""DCT."""


import numpy as np

import dctlib

import unittest


class MyTest(unittest.TestCase):

    def testRun1dDct(self):
        """A test for the get_1d_dct function."""
        inp = np.full(8, 255., dtype='float64')
        dct = dctlib.get_1d_dct(inp)
        idct = dctlib.get_1d_idct(dct)
        self.assertTrue(compare_array(idct, inp, 1.))

    def testRunDCT(self):
        inp = np.full((8, 8), 255., dtype='float64')
        dct = dctlib.get_block_dct(inp)
        idct = dctlib.get_block_idct(dct)
        self.assertTrue(compare_array(idct, inp, 1.))

    def XXXtestGetDCTTest(self):
        """A test for the get_block_dct function."""
        # https://www.geeksforgeeks.org/discrete-cosine-transform-algorithm-program/
        inp = np.full((8, 8), 255., dtype='float64')
        expected_out = np.array(
            [
                [2039.999878, -1.168211, 1.190998, -1.230618, 1.289227, -1.370580, 1.480267, -1.626942],
                [-1.167731, 0.000664, -0.000694, 0.000698, -0.000748, 0.000774, -0.000837, 0.000920],
                [1.191004, -0.000694, 0.000710, -0.000710, 0.000751, -0.000801, 0.000864, -0.000950],
                [-1.230645, 0.000687, -0.000721, 0.000744, -0.000771, 0.000837, -0.000891, 0.000975],
                [1.289146, -0.000751, 0.000740, -0.000767, 0.000824, -0.000864, 0.000946, -0.001026],
                [-1.370624, 0.000744, -0.000820, 0.000834, -0.000858, 0.000898, -0.000998, 0.001093],
                [1.480278, -0.000856, 0.000870, -0.000895, 0.000944, -0.001000, 0.001080, -0.001177],
                [-1.626932, 0.000933, -0.000940, 0.000975, -0.001024, 0.001089, -0.001175, 0.001298],
            ])
        out = dctlib.get_block_dct(inp)
        self.assertTrue(compare_array(expected_out, out, 1.))


def compare_array(a1, a2, max_error):
    assert a1.shape == a2.shape
    e = (a1 - a2)
    error = np.absolute(e).max()
    if not error < max_error:
        print('max_error error matrix: %r' % e)
    return error < max_error


if __name__ == '__main__':
    unittest.main()
