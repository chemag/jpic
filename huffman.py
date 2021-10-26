#!/usr/bin/env python3

"""huffman.py module description."""


import argparse
import sys


default_values = {
    'debug': 0,
    'string': 'Pepper Clemens sent the messenger',
}


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
    parser.add_argument(
            '-s', '--string', action='store',
            dest='string', default=default_values['string'],
            metavar='STRING',
            help='use STRING string',)
    # do the parsing
    options = parser.parse_args(argv[1:])
    return options


# adapted from
# https://www.section.io/engineering-education/huffman-coding-python/
class HuffmanCode:
    def __init__(self, prob_distribution):
        self.symbols = [symbol for (symbol, _) in prob_distribution]
        self.probability = [prob for (_, prob) in prob_distribution]
        self.table = self.compute_table()

    def position(self, value, index):
        for j in range(len(self.probability)):
            if (value >= self.probability[j]):
                return j
        return index - 1

    def compute_table(self):
        num = len(self.probability)
        hcode = [''] * num
        for i in range(num - 2):
            val = self.probability[num - i - 1] + self.probability[num - i - 2]
            if (hcode[num - i - 1] != '' and hcode[num - i - 2] != ''):
                hcode[-1] = ['1' + symbol for symbol in hcode[-1]]
                hcode[-2] = ['0' + symbol for symbol in hcode[-2]]
            elif (hcode[num - i - 1] != ''):
                hcode[num - i - 2] = '0'
                hcode[-1] = ['1' + symbol for symbol in hcode[-1]]
            elif (hcode[num - i - 2] != ''):
                hcode[num - i - 1] = '1'
                hcode[-2] = ['0' + symbol for symbol in hcode[-2]]
            else:
                hcode[num - i - 1] = '1'
                hcode[num - i - 2] = '0'
            position = self.position(val, i)
            probability = self.probability[0:(len(self.probability) - 2)]
            probability.insert(position, val)
            if (isinstance(hcode[num - i - 2], list) and
                    isinstance(hcode[num - i - 1], list)):
                complete_code = (hcode[num - i - 1] + hcode[num - i - 2])
            elif (isinstance(hcode[num - i - 2], list)):
                complete_code = (hcode[num - i - 2] + [hcode[num - i - 1]])
            elif (isinstance(hcode[num - i - 1], list)):
                complete_code = (hcode[num - i - 1] + [hcode[num - i - 2]])
            else:
                complete_code = [hcode[num - i - 2], hcode[num - i - 1]]
            hcode = hcode[0:(len(hcode) - 2)]
            hcode.insert(position, complete_code)
        hcode[0] = ['0' + symbol for symbol in hcode[0]]
        hcode[1] = ['1' + symbol for symbol in hcode[1]]
        if (len(hcode[0]) == 0):
            hcode[0] = '0'
        if (len(hcode[1]) == 0):
            hcode[1] = '1'
        # xxx
        final_code = [''] * num
        count = 0
        for i in range(2):
            for j in range(len(hcode[i])):
                final_code[count] = hcode[i][j]
                count += 1
        final_code = sorted(final_code, key=len)
        # create table
        table = {symbol: code for (symbol, code) in
                 zip(self.symbols, final_code)}
        return table


def do_something(options):
    string = options.string

    # get symbol distribution
    symbol_distribution = {}
    for c in string:
        if c in symbol_distribution:
            symbol_distribution[c] += 1
        else:
            symbol_distribution[c] = 1
    symbol_distribution = sorted(symbol_distribution.items(),
                                 key=lambda x: x[1], reverse=True)

    # normalize (get probability distribution from frequency distribution)
    length = len(string)
    prob_distribution = []
    prob_distribution = [(symbol, frequency / length) for
                         (symbol, frequency) in symbol_distribution]

    # create a huffman code based on the probability distribution
    huffman_code = HuffmanCode(prob_distribution)

    # print huffman table
    print('input_string: "%s"\n' % string)
    print(' Char | Probability | Huffman code ')
    print('----------------------------------')
    for ((symbol, encoding), prob) in zip(huffman_code.table.items(),
                                          huffman_code.probability):
        print(' %-4r | %0.9f |%12s' % (symbol, prob, encoding))

    length_of_code = [len(k) for k in huffman_code.table.values()]
    average_bits_per_symbol = sum(
        [a * b for a, b in zip(length_of_code, huffman_code.probability)])
    print('\naverage_bits_per_symbol: %f' % average_bits_per_symbol)
    # print("Efficiency of the code: %f" %
    # (length_of_code/average_bits_per_symbol))


def main(argv):
    # parse options
    options = get_options(argv)
    # print results
    if options.debug > 0:
        print(options)
    # do something
    do_something(options)


if __name__ == '__main__':
    # at least the CLI program name: (CLI) execution
    main(sys.argv)
