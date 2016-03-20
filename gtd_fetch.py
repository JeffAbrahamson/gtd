#!/usr/bin/env python3

"""Read and compute gtd data, dump to a file.
"""

from lib_gtd import gtd_data_directory, gtd_read, gtd_dump
from optparse import OptionParser
from sys import argv

def main():
    """Fetch and compute gtd data and write to files.

    Write to output_filename.
    """
    opt = OptionParser()
    opt.add_option('-o', '--output-filename', metavar='FILE',
                   dest='output_filename',
                   default='/tmp/gtd-data',
                   help='Base filename to which to write summarized data')
    (opts, args) = opt.parse_args()

    data_dir = gtd_data_directory()
    dfd = gtd_read(data_dir)
    gtd_dump(dfd, opts.output_filename)

if __name__ == '__main__':
    main()
