#!/usr/bin/env python

"""Print in time order the events we have hand labeled.

"""

from __future__ import print_function
from lib_gtd import gtd_load
import argparse
import numpy as np

def print_points(filename):
    """Load, sort, and print the labeled tasks.
    """
    print('Loading data...')
    gtd_data = gtd_load(filename)
    print('Scanning...')
    labeled_data = {k: v for k, v in gtd_data.iteritems()
                    if 'ground_truth_window_title_label' in v
                    or 'ground_truth_window_thumbnail_label' in v}
    for k, v in labeled_data.iteritems():
        print('{when}: {label} / {img_label}'.format(
            when=v['timestamp'],
            label=v['ground_truth_window_title_label'],
            img_label=v['ground_truth_window_thumbnail_label'] if
            'ground_truth_window_thumbnail_label' in v else ''))

def main():
    """Pick a point at random and offer to label it.

    Read a label from the user, then save it to the label file.

    """
    parser = argparse.ArgumentParser()
    named_args = parser.add_argument_group('arguments')
    named_args.add_argument('-f', '--filename', type=str,
                            default='/tmp/gtd_data.pickle',
                            help='Path and filename prefix to pickled data file')
    args = parser.parse_args()
    print_points(args.filename)

if __name__ == '__main__':
    main()
