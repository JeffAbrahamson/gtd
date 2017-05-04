#!/usr/bin/env python

"""Export a text file for training word2vec.
"""

import argparse
from lib_gtd import gtd_load, gtd_data_store, time_main

def export_corpus(in_filename, out_filename):
    """Build the corpus of window title names.

    Save it to a textfile.
    """
    gtd_data = gtd_load(in_filename)
    print('Writing corpus to {fn}'.format(fn=out_filename))
    with open(out_filename, 'w') as f_ptr:
        for point in gtd_data.values():
            if 'window_title' in point:
                f_ptr.write(point['window_title'].encode('utf-8') + '\n')

def main():
    """Extract TF-IDF features from window titles.
    """
    parser = argparse.ArgumentParser()
    named_args = parser.add_argument_group('arguments')
    named_args.add_argument('-o', '--outfile', type=str, default='corpus.txt',
                            help='Filename to which to write window title text corpus.')
    args = parser.parse_args()
    data_filename = gtd_data_store()
    export_corpus(data_filename, args.outfile)

if __name__ == '__main__':
    time_main(main)
