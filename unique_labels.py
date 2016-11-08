#!/usr/bin/env python

"""Print the unique set of labels we've labeled.

Note that this data is cached by gtd_fetch, so while it is very fast
to load the pickle file, it may not be current if we have spent time
hand labeling.

"""

from __future__ import print_function
from lib_gtd import gtd_load, gtd_label_name
import argparse
import numpy as np
import pandas as pd

def print_points(input_filename):
    """Load and print the label words we've used so far.
    """
    labeled_tasks = gtd_load(input_filename, 'labels')
    labels = labeled_tasks.task_label.unique()
    labels.sort()
    for label in labels:
        print(label)

def main():
    """Pick a point at random and offer to label it.

    Read a label from the user, then save it to the label file.

    """
    parser = argparse.ArgumentParser()
    named_args = parser.add_argument_group('arguments')
    named_args.add_argument('-i', '--input-filename', type=str,
                            default='/tmp/gtd-data',
                            help='Path and filename prefix to pickled data file')
    args = parser.parse_args()
    print_points(args.input_filename)

if __name__ == '__main__':
    main()
