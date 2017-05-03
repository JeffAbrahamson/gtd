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

def print_set_in_columns(things):
    """Print set of things in several columns.
    """
    column = 1
    num_columns = 5
    line = '\n'
    for item in things:
        line += '{str:15s}'.format(str=item)
        if column % num_columns == 0:
            print(line)
            line = ''
            column = 1
        else:
            column += 1

def get_label(prompt, ontology, counter):
    """Request a label, return it (or None).
    """
    if counter % 10 == 0:
        # Only remind me from time to time.
        print_set_in_columns(ontology)
    else:
        print('counter=', counter)
    print('==> {p}'.format(p=prompt))
    print('Label?')
    label = raw_input()
    if '' == label:
        print('OK, ignored.')
        return None
    return label

def label_one_point(unlabeled_data,
                    window_title_labels,
                    window_thumbnail_labels,
                    num_title_requests,
                    num_thumbnail_requests):
    """Pick an unlabeled point at random and ask for a label.

    An empty response requests that we save and quit.
    A hyphen means to skip this entry.

    Return true if we should continue, false to terminate.
    """
    key = random.choice(unlabeled_data.keys())
    value = unlabeled_data[key]
    if 'ground_truth_window_title_label' not in value:
        label = get_label(value['window_title'], window_title_labels, num_title_requests)
        num_title_requests += 1
        if None == label:
            return False
        if '-' == label:
            print('Skipped')
        else:
            value['ground_truth_window_title_label'] = label
    if 'ground_truth_window_thumbnail_label' not in value and \
       'window_thumbnail_filename' in value:
        os.system('geeqie --remote {fn}'.format(
            fn=value['window_thumbnail_filename']))
        label = get_label("image", window_thumbnail_labels, num_thumbnail_requests)
        num_thumbnail_requests += 1
        if None == label:
            return False
        if '-' == label:
            print('Skipped')
        else:
            value['ground_truth_window_thumbnail_label'] = label
    return True

def label_points(filename, images):
    """Load data, query for labels until an empty label.

    Load data, filter to unlabeled points, and query for labels until
    the user provides an empty label.  Save the dataset.

    """
    window_title_labels = set()
    window_thumbnail_labels = set()
    num_title_requests = 0
    num_thumbnail_requests = 0
    gtd_data = gtd_load(filename)
    s = set()
    for point in gtd_data.values():
        s = s.union(point.keys())
        if 'ground_truth_window_title_label' in point:
            window_title_labels.add(point['ground_truth_window_title_label'])
        if 'ground_truth_window_thumbnail_label' in point:
            window_thumbnail_labels.add(
                point['ground_truth_window_thumbnail_label'])

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
    while label_one_point(unlabeled_data,
                          window_title_labels,
                          window_thumbnail_labels,
                          num_title_requests,
                          num_thumbnail_requests):
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
