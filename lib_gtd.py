#!/usr/bin/env python

"""Functions for reading and simple manipulation of gtd data."""

from __future__ import print_function
from glob import glob
from os import getenv
import cv2
import datetime
import numpy as np
import pandas as pd
import pickle
import re

def filter_n_last_days(dataframe, num_days):
    """Select the rows of df_tasks in the most recent n days.

    If n is 0, select today's tasks.

    The intent is that dataframe is a tasks dataframe.

    """
    first_day = np.datetime64(datetime.date.today()) - \
                np.timedelta64(num_days - 1, 'D')
    # Strangely, numpy.datetime64.tolist() returns a datetime.date.
    restricted_dataframe = dataframe[dataframe.date >= first_day.tolist()]
    return first_day, restricted_dataframe

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

host_map = {
    'lorax': 'laptop',
    'nantes': 'laptop',
    'birdsong': 'desktop',
    'starshine': 'laptop',
    'siegfried': 'desktop'
}
def get_host_class(hostname):
    """Return laptop or desktop.
    """
    try:
        return host_map[hostname]
    except:
        return 'unknown_host_class'

def get_image_filenames(path):
    """Return a list of all image filenames participating in gtd.
    """
    all_filenames = glob(path + '/*png')
    print('Got {n} image filenames'.format(n=len(all_filenames)))
    return all_filenames

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
    field_array = [line.split(' ', 1) for line in lines]
    fields = [{'time': fields[0], 'label': fields[1] if len(fields) > 1 else ''}
              for fields in field_array
              if fields != ['']]
    dataframe = pd.DataFrame(fields)
    dataframe['datetime'] = dataframe.apply(
        lambda row: datetime.datetime.fromtimestamp(int(row['time'])),
        axis=1)
    dataframe['weekday'] = dataframe.apply(lambda row: row['datetime'].isoweekday(), axis=1)
    dataframe['hours'] = dataframe.apply(lambda row: row['datetime'].hour, axis=1)
    dataframe['minutes'] = dataframe.apply(
        lambda row: row['datetime'].hour * 60 + row['datetime'].minute,
        axis=1)
    dataframe['seconds'] = dataframe.apply(
        lambda row: row['datetime'].hour * 3600 + row['datetime'].minute * 60
        + row['datetime'].second,
        axis=1)
    dataframe['date'] = pd.Series(
        [val.to_datetime().date() for val in dataframe.datetime],
        index=dataframe.index)
    return dataframe

def image_to_histograms(image_filename):
    """Read an image, return a triple of histograms.

    The histograms are linear histograms of red, green, and blue
    intensities respectively.

    """
    image = cv2.imread(image_filename)
    red   = cv2.calcHist([image], channels=[0], mask=None, histSize=[256], ranges=[0,256])
    green = cv2.calcHist([image], channels=[1], mask=None, histSize=[256], ranges=[0,256])
    blue  = cv2.calcHist([image], channels=[2], mask=None, histSize=[256], ranges=[0,256])
    return (red, green, blue)

def append_image_row(df_list, time_str, host_str, image_name):
    """Append a row to a list.
    """
    red, green, blue = image_to_histograms(image_name)
    df_list.append({'hostname': host_str,
                    'time': time_str,
                    'red': red,
                    'green': green,
                    'blue': blue,
                   })

def join_images(dataframe, image_filenames):
    """Join image features to the dataframe based on host and time.

    This will return a new dataframe that right joins the existing
    dataframe with the images.  That is, rows without images are
    silently dropped.

    """
    time_host_df = dataframe.loc[:, ['time', 'hostname']]
    time_host_dict = {row['time']: row['hostname']
                      for row in time_host_df.to_records()}
    with open('/tmp/time_host_dict', 'w') as f:
        pickle.dump(time_host_dict, f)
    df_list = []                # Build a list to make a dataframe.
    num_found = 0
    num_found_minus = 0
    num_missed = 0
    num_parse_errors = 0
    host_time_pattern = re.compile('^.*/([a-z]*)_([0-9]*)\\.[a-z]*$')
    for image_name in image_filenames:
        host_time_match = re.match(host_time_pattern, image_name)
        if host_time_match is None:
            print('Failed to parse filename: {fn}'.format(fn=image_name))
            num_parse_errors += 1
        else:
            image_host = host_time_match.groups()[0]
            image_time = host_time_match.groups()[1]
            if image_time in time_host_dict and \
               time_host_dict[image_time] == image_host:
                append_image_row(df_list, image_time, image_host, image_name)
                num_found += 1
            else:
                # Maybe the snapshot happened a smidgeon after the
                # window label was recorded.
                image_time_minus = str(int(image_time) - 1)
                if image_time_minus in time_host_dict and \
                   time_host_dict[image_time_minus] == image_host:
                    append_image_row(df_list, image_time_minus, image_host, image_name)
                    num_found_minus = 0
                else:
                    print('Failed to match {fn}'.format(fn=image_name))
                    num_missed += 1
    print('Joining: found {f} at first, {p} more at -1, {m} missed, {pe} parse errors'.format(
        f=num_found, p=num_found_minus, m=num_missed, pe=num_parse_errors))
    image_dataframe = pd.DataFrame(df_list)
    joined_dataframe = pd.merge(dataframe, image_dataframe, how='right',
                                on=['time', 'hostname'])
    return joined_dataframe

def get_labels():
    """Read the labels files.

    Return a DataFrame with the following columns:
      hostname   - the host on which the label was noted
      time       - seconds since epoch at which the label was noted
      task_label - the user-supplied or observed label (task name)

    """
    dataframe = None
    filename = gtd_label_name()
    labels = []
    try:
        with open(filename, 'rb') as file_read_ptr:
            contents = file_read_ptr.read()
    except IOError:
        print('Failed to open label file, assuming empty')
        return pd.DataFrame(columns=['time', 'hostname', 'task_label'])
    try:
        lines = contents.decode('utf-8').split('\n')
    except UnicodeDecodeError:
        lines = contents.decode('iso-8859-15').split('\n')
    field_array = [line.split('\t', 2) for line in lines]
    fields = [{'time': fields[0], 'hostname': fields[1], 'task_label': fields[2]}
              for fields in field_array
              if fields != ['']]
    dataframe = pd.DataFrame(fields)
    return dataframe

def get_labels_OLD(filenames):
    """Read the gtd_* files.

    Return a DataFrame with the following columns:
      hostname - the host on which the label was noted
      time     - seconds since epoch at which the label was noted
      datetime - python datetime at which label was noted
      label    - the user-supplied or observed label (task name)

    """
    dataframe = None
    host_pattern = re.compile('^.*/gtd_')
    for filename in filenames:
        host = re.sub(host_pattern, '', filename)
        if host != filename:
            this_df = read_dataframe(filename)
            this_df['hostname'] = host
            if dataframe is None:
                dataframe = this_df
            else:
                dataframe = dataframe.append(this_df)
    return dataframe

def get_tasks(filenames, image_filenames):
    """Read the host__time files.

    Return a DataFrame with the following columns:
      hostname - the host on which the label was noted
      time     - seconds since epoch at which the label was noted
      datetime - python datetime at which label was noted
      label    - the user-supplied or observed label (task name)
      weekday  - Monday == 1 ... Sunday == 7 (UTC)
      hours    - hour of day (UTC)
      minutes  - minutes since midnight (UTC)

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
            this_df['host_class'] = this_df.apply(
                lambda row: get_host_class(row['hostname']),
                axis=1)
            dfs.append(this_df)
    dataframe = pd.concat(dfs, ignore_index=True)
    image_dataframe = join_images(dataframe, image_filenames)
    return dataframe, image_dataframe

def gtd_read(data_dir, image_data_dir):
    """Read all the gtd data available.

    Path is the directory in which gtd data files live.

    The gtd data files are of three types: label data, old label data,
    and task data.

      - Labels are user-provided names for the purposes of semi-supervised
        learning (or providing names after unsupervised learning.
      - Tasks are observations of my behaviour.

    The (new) labels are time synchronised to the task events, while
    the old labels may occur anywhere in the interval between two
    events or even adjoining a pause.

    (Old) label data files are named 'gtd_<hostname>' and contain time
    (in seconds since the epoch), a space, and the name of the task
    that I think I was performing at that time.  The task name itself
    could contain spaces.  These files, and old labels, are probably
    not useful anymore.

    Task data files are named '<machine>__<session-start-time>'.  The
    session start time has format YYYY-MM-DD_HHMMSS.  The file
    contents have format time (in seconds since the epoch), a space,
    and the active window title at that time.  The active window title
    may have spaces.

    Return a dictionary, with elements
      'labels'      -> dataframe of (hostname, time, label)
      'labels_old'  -> dataframe of (hostname, time, datetime, label)
      'tasks'       -> dataframe of (hostname, time, datetime, taskname)
      'image_tasks' -> tasks dataframe plus red, green, and blue histograms

    The datetime field is in seconds since the epoch.

    """
    hosts, filenames = get_hostnames(data_dir)
    image_filenames = get_image_filenames(image_data_dir)
    labels_old = get_labels_OLD(filenames)
    labels = get_labels()
    tasks, image_tasks = get_tasks(filenames, image_filenames)
    return {'labels': labels,
            'labels_old': labels_old,
            'tasks':  tasks,
            'image_tasks': image_tasks,
    }

def gtd_dump(dfd, filename):
    """Dump a pickled dictionary of dataframes from gtd_read().
    """
    for key, dataframe in dfd.items():
        output_filename = filename + '.' + key
        dataframe.to_pickle(output_filename)
        print('Wrote {fn}'.format(fn=output_filename))

def gtd_load(filename, element):
    """Load a pickled file written via gtd_dump().

    Element is a key in the dictionary returned by gtd_read().
    The object returned is a single dataframe.
    """
    input_filename = filename + '.' + element
    dataframe = pd.read_pickle(input_filename)
    print('Read {fn}'.format(fn=input_filename))
    return dataframe

def gtd_data_directory():
    """Return the name of the canonical data directory.
    """
    return '{home}/data/gtd'.format(home=getenv('HOME'))

def gtd_data_img_directory():
    """Return the name of the canonical data directory.
    """
    return '{home}/data/gtd-img'.format(home=getenv('HOME'))

def gtd_label_name():
    """Return the full pathname to the label file.

    Its format is TSV: time, hostname, label.

    Use label_point.py to write lines to the file.
    Use get_labels() to read it.
    """
    return gtd_data_directory() + '/labels'

def main():
    """The main section is not particularly useful except as documentation."""
    data_dir = gtd_data_directory()
    data_img_dir = gtd_data_img_directory()
    dfd = gtd_read(data_dir, data_img_dir)
    print(('Read {num_labels} user-recorded labels and {num_tasks} ' +
           'recorded tasks ({num_images} images) on {num_hosts} hosts.').format(
               num_labels=len(dfd['labels']),
               num_tasks=len(dfd['tasks']),
               num_images=len(dfd['image_tasks']),
               num_hosts=len(dfd['labels']['hostname'].unique()),
           ))

if __name__ == '__main__':
    main()
