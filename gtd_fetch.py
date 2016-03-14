#!/usr/bin/env python3

"""Read and compute gtd data, dump to a file.
"""

from lib_gtd import gtd_data_directory, gtd_read, gtd_dump
from sys import argv

def main():
    """Fetch and compute gtd data and write to files.

    Write to output_filename.
    """
    if len(argv) > 1:
        output_filename = argv[1]
    else:
        output_filename = '/tmp/gtd-data'
    data_dir = gtd_data_directory()
    dfd = gtd_read(data_dir)
    gtd_dump(dfd, output_filename)

if __name__ == '__main__':
    main()
