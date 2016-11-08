#!/usr/bin/env python

"""Print in time order the events we have hand labeled.

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
    """Load, sort, and print the labeled tasks.
    """
    tasks = gtd_load(input_filename, 'tasks')
    labeled_tasks = gtd_load(input_filename, 'labels')
    task_labels = pd.merge(labeled_tasks, tasks, on=['time', 'hostname'], how='inner')
    df = task_labels.sort(['time', 'hostname']).\
         loc[:, ['time', 'hostname', 'task_label', 'label']]
    for index, row in df.iterrows():
        print('{t:9s} {hn:<10s} {task_label:<15s}  {task}'.format(
            t=row.time, hn=row.hostname,
            task_label=row.task_label,
            task=row.label.encode('utf-8')))

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
