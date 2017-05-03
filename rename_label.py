#!/usr/bin/env python

"""Rename all ground truth labels from X to Y.

"""

from __future__ import print_function
from lib_gtd import gtd_load, gtd_dump, gtd_data_store, time_main
import argparse

def rename_label(filename, label_type, src_label, dst_label):
    """Load data, rename ground truth labels in -> out.

    """
    if src_label is None or '' == src_label:
        print('Missing source label.')
        return
    if dst_label is None or '' == dst_label:
        print('Missing destination label.')
        return
    if 'wt' != label_type and 'it' != label_type:
        print('Invalid label name: choose "it" or "wt".')
        return

    if 'wt' == label_type:
        label_key = 'ground_truth_window_title_label'
    if 'it' == label_type:
        label_key = 'ground_truth_window_thumbnail_label'
    gtd_data = gtd_load(filename)
    rename_count = 0
    for point in gtd_data.values():
        if label_key in point and point[label_key] == src_label:
            point[label_key] = dst_label
            rename_count += 1
    print('Renamed {c} points.\n'.format(c=rename_count))
    gtd_dump(filename, gtd_data)

def main():
    """Pick a point at random and offer to label it.

    Read a label from the user, then save it to the label file.

    """
    parser = argparse.ArgumentParser()
    named_args = parser.add_argument_group('arguments')
    named_args.add_argument('-t', '--labeltype', type=str, default='wt',
                            help='The type of label to rename: wt (window title) ' + \
                            'or it (image thumbnail).')
    named_args.add_argument('-i', '--src_label', type=str, default='',
                            help='Label to rename')
    named_args.add_argument('-o', '--dst_label', type=str, default='',
                            help='New label name')
    args = parser.parse_args()
    filename = gtd_data_store()
    rename_label(filename, args.labeltype, args.src_label, args.dst_label)

if __name__ == '__main__':
    time_main(main)
