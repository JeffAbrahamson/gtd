#!/usr/bin/env python

"""Select a point at random and offer to label it.

We maintain a file of labels indexed by hostname and time.
"""

from __future__ import print_function
from lib_gtd import gtd_load, gtd_dump, gtd_data_store, time_main
import argparse
import os
import random
import time

def get_label():
    """Request a label, return it (or None).
    """
    print('Label?')
    label = raw_input()
    if '' == label:
        print('OK, ignored.')
        return None
    return label

def label_one_point(unlabeled_data):
    """Pick an unlabeled point at random and ask for a label.

    Return true if we should continue, false to terminate.
    """
    key = random.choice(unlabeled_data.keys())
    value = unlabeled_data[key]
    if 'ground_truth_window_title_label' not in value:
        print(value['window_title'])
        label = get_label()
        if None == label:
            return False
        value['ground_truth_window_title_label'] = label
    if 'ground_truth_window_thumbnail_label' not in value and \
       'window_thumbnail_filename' in value:
        os.system('geeqie --remote {fn}'.format(
            fn=value['window_thumbnail_filename']))
        label = get_label()
        if None == label:
            return False
        value['ground_truth_window_thumbnail_label'] = label
    return True

def label_points(filename, images):
    """Load data, query for labels until an empty label.

    Load data, filter to unlabeled points, and query for labels until
    the user provides an empty label.  Save the dataset.

    """
    gtd_data = gtd_load(filename)
    s = set()
    for v in gtd_data.values():
        s = s.union(v.keys())
    print('Key set: ', s)
    unlabeled_data = {k: v for k, v in gtd_data.iteritems() if
                      'ground_truth_window_title_label' not in v or
                      'ground_truth_window_thumbnail_label' not in v}
    print('Found {n} unlabeled points'.format(n=len(unlabeled_data)))
    if images:
        unlabeled_data = {k: v for k, v in unlabeled_data.iteritems()
                          if 'window_thumbnail_filename' in v}
        print('With images: found {n} unlabeled points'.format(n=len(unlabeled_data)))
    # The slice is not deep, so modifying the values will modify in
    # the original gtd_data as well.  So we can persist.
    while label_one_point(unlabeled_data):
        pass
    gtd_dump(filename, gtd_data)

def main():
    """Pick a point at random and offer to label it.

    Read a label from the user, then save it to the label file.

    """
    parser = argparse.ArgumentParser()
    named_args = parser.add_argument_group('arguments')
    named_args.add_argument('-f', '--filename', type=str,
                            default=gtd_data_store(),
                            help='Path and filename prefix to pickled data file')
    named_args.add_argument('-i', '--images', dest='images',
                            action='store_true',
                            help='Filter to events with thumbnails')
    args = parser.parse_args()
    label_points(args.filename, args.images)

if __name__ == '__main__':
    time_main(main)
