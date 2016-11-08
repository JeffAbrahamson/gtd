#!/usr/bin/env python

"""Select a point at random and offer to label it.

We maintain a file of labels indexed by hostname and time.
"""

from __future__ import print_function
from lib_gtd import gtd_load, gtd_label_name
import argparse
import numpy as np

def label_point(input_filename, output_filename):
    """Load tasks, query to label a random task, write to the label file.

    To join labeled points to the full point table, use this inner join:

      pd.merge(labels, tasks, on=['time', 'hostname'], how='inner')
    """
    tasks = gtd_load(input_filename, 'tasks')
    # Pick a random task label and select one task line with that
    # window name.
    df_line = tasks[tasks.label == np.random.choice(tasks.label, 1)[0]]\
              .loc[:, ['hostname', 'time', 'label']].head(1)
    time = df_line.time.values[0]
    hostname = df_line.hostname.values[0]
    task_name = df_line.label.values[0]
    print(task_name)
    print('Label?')
    label = raw_input()
    if '' == label:
        print('OK, ignored.')
        return
    if output_filename is None:
        output_filename = gtd_label_name()
    with open(output_filename, 'a') as file_append_ptr:
        file_append_ptr.write('\t'.join([time, hostname, label]) + '\n')

def main():
    """Pick a point at random and offer to label it.

    Read a label from the user, then save it to the label file.

    """
    parser = argparse.ArgumentParser()
    named_args = parser.add_argument_group('arguments')
    named_args.add_argument('-i', '--input-filename', type=str,
                            default='/tmp/gtd-data',
                            help='Path and filename prefix to pickled data file')
    named_args.add_argument('-o', '--output-filename', type=str,
                            help='Name of label file to which to write')
    args = parser.parse_args()
    label_point(args.input_filename, args.output_filename)

if __name__ == '__main__':
    main()
