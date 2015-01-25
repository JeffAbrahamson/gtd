#!/usr/bin/python3

"""Functions for reading and simple manipulation of gtd data."""

from glob import glob
import matplotlib.pyplot as plt
import numpy as np
from os import getenv
import pandas as pd
from sys import argv

def get_gtd_labels(path):
    """Read the gtd_* files.

    Return a DataFrame with the following columns:
      hostname - the host on which the label was noted
      time - seconds since epoch at which the label was noted
      datetime - python datetime at which label was noted
      label - the user-supplied label (task name)
    """
    prefix = path + '/gtd_'
    gtd_labels = glob_and_read_dataframes(prefix)
    df = pd.DataFrame()
    for host, host_df in gtd_labels.items():
        host_df['hostname'] = host
        df = df.append(host_df)
    return df

def read_all_by_host(path, hostname):
    """Read all gtd files for a given host.

    Return a single dataframe with these columns:
      time - seconds since epoch of observation
      datetime - python datetime of observation
      task - observed task
      hostname - host on which task was observed
      session - a string identifying the session

    Sessions are currently identified by strings representing seconds
    since the epoch from which the session began.  A session
    represents user time at the keyboard, starting at screen unlock
    (or login) and ending at screen lock.  These details shouldn't
    matter here.

    """
    prefix = '{path}/{hostname}_'.format(path=path, hostname=hostname)
    observations = glob_and_read_dataframes(prefix)
    df = pd.DataFrame()
    for session, session_df in observations.items():
        session_df['hostname'] = hostname
        session_df['session'] = session
        df = df.append(session_df)
    return df

def glob_and_read_dataframes(prefix):
    """Glob all files starting with prefix and import to dataframes.

    Glob all the files.
    Read each and stick in a dataframe.
    Return a dictionary mapping keys (trailing parts of filenames, to be
    interpretted by the caller) to dataframes.

    The returned dataframes have the following columns:
      time
      datetime
      label
    """
    filenames = glob(prefix + '*')
    labels_by_key = {}
    for filename in filenames:
        if filename.startswith(prefix):
            key = filename[len(prefix):]
            df = pd.read_csv(filename, sep=' ', names=['time', 'label'])
            df['datetime'] = pd.to_datetime(df['time'], unit='s')
            labels_by_key[key] = df
        else:
            print('Error: filename "{filename}" has bad format: ignored.'.format(filename=filename))
    return labels_by_key

def read(data_dir):
    """Read all the gtd data available.

    Return a dictionary, with elements
      'labels' -> dataframe of (hostname, time, datetime, label)
      'tasks'  -> dataframe of (hostname, time, datetime, taskname)

    Labels are user-provided names for the purposes of semi-supervised
    learning (or providing names after unsupervised learning.  Tasks
    are computer generated, currently the name of the application
    window that is active at observation time.

    """
    df_labels = get_gtd_labels(data_dir)
    df_tasks = pd.DataFrame()
    hostnames = df_labels['hostname'].unique()
    for hostname in hostnames:
        df_tasks = df_tasks.append(read_all_by_host(data_dir, hostname))
    return {'labels': df_labels,
            'tasks': df_tasks}

# The main section is not particularly useful except as documentation.
if __name__ == '__main__':
    if len(argv) > 1:
        data_dir = argv[1]
    else:
        data_dir = '{home}/data/gtd'.format(home=getenv('HOME'))
    dfd = read(data_dir)
    print(('Read {num_labels} user-recorded labels and {num_tasks} ' +
           'recorded tasks on {num_hosts} hosts.').format(
               num_labels=len(dfd['labels']),
               num_tasks=len(dfd['tasks']),
               num_hosts=len(dfd['labels']['hostname'].unique()),
           ))
