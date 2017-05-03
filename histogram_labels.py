#!/usr/bin/env python

"""Select a point at random and offer to label it.

We maintain a file of labels indexed by hostname and time.
"""

from __future__ import print_function
from lib_gtd import gtd_load, gtd_data_store, time_main
import argparse
import os
import random

def print_set_in_columns(things):
    """Print set of things in several columns.
    """
    column = 1
    num_columns = 5
    line = '\n'
    things_sorted = list(things)
    things_sorted.sort()
    for item in things_sorted:
        line += '{str:17s}  '.format(str=item)
        if column % num_columns == 0:
            print(line)
            line = ''
            column = 1
        else:
            column += 1
    if line != "":
        print(line)

def get_label(prompt, ontology, counter):
    """Request a label, return it (or None).
    """
    if counter % 10 == 0:
        # Only remind me from time to time.
        print_set_in_columns(ontology)
    else:
        print('counter=', counter)
    print('==> {p}'.format(p=prompt.encode('utf-8')))
    print('Label?')
    label = raw_input()
    if '' == label:
        print('OK, ignored.')
        return None
    ontology.add(label)
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
        if label is None:
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

def labels_matching(gtd_data, label):
    """Print points whose hand-noted label matches label.
    """
    print('Window titles:')
    for name, point in gtd_data.iteritems():
        if point.get('ground_truth_window_title_label', '') == label:
            print('{n:25s}  {v}'.format(
                n=name,
                v=point['window_title'].encode('utf-8')))
    print('\nThumbnails:')
    for name, point in gtd_data.iteritems():
        if point.get('ground_truth_window_thumbnail_label', '') == label:
            print('{n:20s}  {v}'.format(
                n=name,
                v=point['window_thumbnail_filename'].encode('utf-8')))

def histogram_labels(filename, label):
    """Load data, histogram labels or provide single label detail.

    If label is empty, then print histogram of all labels.

    If a label is provided, print the entries that match that label.

    """
    gtd_data = gtd_load(filename)
    if '' != label:
        labels_matching(gtd_data, label)
        return
    window_titles = {}
    window_thumbnails = {}
    for point in gtd_data.values():
        if 'ground_truth_window_title_label' in point:
            window_titles[point['ground_truth_window_title_label']] = \
                window_titles.get(
                    point['ground_truth_window_title_label'], 0) + 1
        if 'ground_truth_window_thumbnail_label' in point:
            window_thumbnails[point['ground_truth_window_thumbnail_label']] = \
                window_thumbnails.get(
                    point['ground_truth_window_thumbnail_label'], 0) + 1

    print('Window titles:')
    for name in sorted(window_titles.keys()):
        print('{count:6.0f}  {n}'.format(
            count=window_titles[name], n=name))
    print('\nThumbnails:')
    for name in sorted(window_thumbnails.keys()):
        print('{count:6.0f}  {n}'.format(
            count=window_thumbnails[name], n=name))

def main():
    """Pick a point at random and offer to label it.

    Read a label from the user, then save it to the label file.

    """
    parser = argparse.ArgumentParser()
    named_args = parser.add_argument_group('arguments')
    named_args.add_argument('-l', '--label', type=str, default='',
                            help='If present, provide detail on this label.')
    args = parser.parse_args()
    filename = gtd_data_store()
    histogram_labels(filename, args.label)

if __name__ == '__main__':
    time_main(main)
