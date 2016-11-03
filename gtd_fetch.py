#!/usr/bin/env python

"""Read and compute gtd data, dump to a file.
"""

from __future__ import print_function
import argparse
from lib_gtd import gtd_data_directory, gtd_data_img_directory, gtd_read, gtd_dump
from sys import argv

def main():
    """Fetch and compute gtd data and write to files.

    Write to output_filename.
    """
    parser = argparse.ArgumentParser()
    named_args = parser.add_argument_group('arguments')
    named_args.add_argument('--output-filename', type=str,
                            default='/tmp/gtd-data',
                            help='Path and filename prefix to which to write data')
    # parser.add_argument('--verbose', dest='verbose', action='store_true')
    args = parser.parse_args()

    data_dir = gtd_data_directory()
    data_image_dir = gtd_data_img_directory()
    dfd = gtd_read(data_dir, data_image_dir)
    gtd_dump(dfd, args.output_filename)

if __name__ == '__main__':
    main()
