#!/usr/bin/env python3

"""Functions for reading and simple manipulation of gtd data."""

import datetime
from glob import glob
import numpy as np
from os import getenv
import pandas as pd
import re
from sys import argv

def get_hostnames(path):
    """Return a list of all hostnames and all data files participating in gtd.
    """
    all_filenames = glob(path + '/*')
    host_pattern = re.compile('{p}/([a-z]*)__(.*)'.format(p=path))
    hosts = set()
    for filename in all_filenames[:5]:
        host_match = re.match(host_pattern, filename)
        if host_match is not None:
            hosts.add(host_match.groups()[0])
    hosts.discard('gtd')
    return hosts, all_filenames

def read_dataframe(filename):
    """Read a single file and return its canonical dataframe.

    The file format should be time (in seconds since the epoch), a
    space, and then text (which may contain spaces.

    """
    with open(filename, 'rb') as file_read_ptr:
        contents = file_read_ptr.read()
    try:
        lines = contents.decode('utf-8').split('\n')
    except UnicodeDecodeError:
        lines = contents.decode('iso-8859-15').split('\n')
    field_array = [line.split(sep=' ', maxsplit=1)
                   for line in lines]
    fields = [{'time': fields[0], 'label': fields[1] if len(fields) > 1 else ''}
              for fields in field_array
              if fields != ['']]
    df = pd.DataFrame(fields)
    df['datetime'] = df.apply(
        lambda row: datetime.datetime.fromtimestamp(int(row['time'])),
        axis=1)
    return df

def get_labels(filenames):
    """Read the gtd_* files.

    Return a DataFrame with the following columns:
      hostname - the host on which the label was noted
      time     - seconds since epoch at which the label was noted
      datetime - python datetime at which label was noted
      label    - the user-supplied or observed label (task name)

    """
    df = None
    host_pattern = re.compile('^.*/gtd_')
    for filename in filenames:
        host = re.sub(host_pattern, '', filename)
        if host != filename:
            this_df = read_dataframe(filename)
            this_df['hostname'] = host
            if df is None:
                df = this_df
            else:
                df = df.append(this_df)
    return df

def get_tasks(filenames):
    """Read the host__time files.

    Return a DataFrame with the following columns:
      hostname - the host on which the label was noted
      time     - seconds since epoch at which the label was noted
      datetime - python datetime at which label was noted
      label    - the user-supplied or observed label (task name)

    """
    dfs = []
    task_pattern = re.compile('^.*/([^/]*)__(.*)')
    for filename in filenames:
        task_match = re.match(task_pattern, filename)
        if task_match is not None:
            host = task_match.groups()[0]
            # And task_match.groups()[1] is the session start time
            this_df = read_dataframe(filename)
            this_df['hostname'] = host
            dfs.append(this_df)
    return pd.concat(dfs)
    
def gtd_read(data_dir):
    """Read all the gtd data available.

    Path is the directory in which gtd data files live.

    The gtd data files are of two types: label data and task data.
    Labels are user-provided names for the purposes of semi-supervised
    learning (or providing names after unsupervised learning.  Tasks
    are observations of my behaviour.

    Label data files are named 'gtd_<hostname>' and contain time (in
    seconds since the epoch), a space, and the name of the task that I
    think I was performing at that time.  The task name itself could
    contain spaces.

    Task data files are named '<machine>__<session-start-time>'.  The
    session start time has format YYYY-MM-DD_HHMMSS.  The file
    contents have format time (in seconds since the epoch), a space,
    and the active window title at that time.  The active window title
    may have spaces.

    Return a dictionary, with elements
      'labels' -> dataframe of (hostname, time, datetime, label)
      'tasks'  -> dataframe of (hostname, time, datetime, taskname)

    The datetime field is in seconds since the epoch.

    """
    hosts, filenames = get_hostnames(data_dir)
    labels = get_labels(filenames)
    tasks = get_tasks(filenames)
    return {'labels': labels,
            'tasks':  tasks}

def gtd_data_directory():
    """Return the name of the canonical data directory.
    """
    return '{home}/data/gtd'.format(home=getenv('HOME'))

def main():
    """The main section is not particularly useful except as documentation."""
    if len(argv) > 1:
        data_dir = argv[1]
    else:
        data_dir = gtd_data_directory()
    if True:
        dfd = gtd_read(data_dir)
        print(('Read {num_labels} user-recorded labels and {num_tasks} ' +
               'recorded tasks on {num_hosts} hosts.').format(
                   num_labels=len(dfd['labels']),
                   num_tasks=len(dfd['tasks']),
                   num_hosts=len(dfd['labels']['hostname'].unique()),
               ))

if __name__ == '__main__':
    main()
