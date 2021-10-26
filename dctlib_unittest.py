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

    def testGetDCTTest(self):
        """A test for the get_block_dct function."""
        # https://www.geeksforgeeks.org/discrete-cosine-transform-algorithm-program/
        inp = np.full((8, 8), 255., dtype='float64')
        expected_out = np.array(
            [
                [2039,   0,   0,   0,   0,   0,   0,   0],  # noqa: E201
                [   0,   0,   0,   0,   0,   0,   0,   0],  # noqa: E201
                [   0,   0,   0,   0,   0,   0,   0,   0],  # noqa: E201
                [   0,   0,   0,   0,   0,   0,   0,   0],  # noqa: E201
                [   0,   0,   0,   0,   0,   0,   0,   0],  # noqa: E201
                [   0,   0,   0,   0,   0,   0,   0,   0],  # noqa: E201
                [   0,   0,   0,   0,   0,   0,   0,   0],  # noqa: E201
                [   0,   0,   0,   0,   0,   0,   0,   0],  # noqa: E201
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
