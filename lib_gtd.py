#!/usr/bin/env python

"""Functions for reading and simple manipulation of gtd data."""

from __future__ import print_function
from glob import glob
from os import getenv
import cv2
import datetime
import numpy as np
import os
import pickle
import re
import time

def filter_n_last_days(data_gtd, num_days):
    """Select the rows of df_tasks in the most recent n days.

    If n is 0, select today's tasks.

    Return the first day in the selection and the selection itself as
    a new dict.  Note that we are not making a deep copy of the slice
    we return, so clients should not modify the dict values.

    """
    first_day = np.datetime64(datetime.date.today()) - \
                np.timedelta64(num_days - 1, 'D')
    # Strangely, numpy.datetime64.tolist() returns a datetime.date.
    restricted_data = {k: v for k, v in data_gtd.iteritems()
                       if v['date'] >= first_day.tolist()}
    return first_day, restricted_data

def get_window_title_filenames(path):
    """Return a list of all data files participating in gtd window titles.
    """
    print('path', path)
    all_filenames = glob(path + '/*')
    # Technically, we probably don't need to do anything more here.
    # But it's maybe interesting to know how many hosts if it doesn't
    # cost too much.
    host_pattern = re.compile('{p}/([a-z]*)__(.*)'.format(p=path))
    hosts = set()
    for filename in all_filenames:
        host_match = re.match(host_pattern, filename)
        if host_match is not None:
            hosts.add(host_match.groups()[0])
    hosts.discard('gtd')
    print('Got {n} window title filenames and {h} hostnames'.format(
        n=len(all_filenames), h=len(hosts)))
    print('Hostnames={h}'.format(h=', '.join(hosts)))
    return all_filenames

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
    except KeyError:
        return 'unknown_host_class'

def get_image_filenames(path):
    """Return a list of all image filenames participating in gtd.
    """
    all_filenames = glob(path + '/*png')
    print('Got {n} image filenames'.format(n=len(all_filenames)))
    return all_filenames

def basic_event_info(host_class, timestamp_int):
    """Return a dict with basic event info.
    """
    bei = {}
    timestamp = datetime.datetime.fromtimestamp(timestamp_int)
    bei['timestamp'] = timestamp
    bei['weekday'] = timestamp.isoweekday()
    bei['hours'] = timestamp.hour
    bei['minutes'] = timestamp.hour * 60 + timestamp.minute
    bei['seconds'] = timestamp.hour * 3600 + timestamp.minute * 60 + timestamp.second
    bei['date'] = timestamp.date()
    bei['host_class'] = host_class
    return bei

def read_window_titles_one_file(filename, hostname, gtd_data):
    """Read a single file and insert its data in gtd_data.

    The file format should be time (in seconds since the epoch), a
    space, and then text (which may contain spaces) representing the
    window title.

    """
    host_class = get_host_class(hostname)
    with open(filename, 'rb') as file_read_ptr:
        contents = file_read_ptr.read()
    try:
        lines = contents.decode('utf-8').split('\n')
    except UnicodeDecodeError:
        lines = contents.decode('iso-8859-15').split('\n')
    field_array = [line.split(' ', 1) for line in lines]
    fields = [{'time': fields[0], 'window_title': fields[1] if len(fields) > 1 else ''}
              for fields in field_array
              if fields != ['']]
    for field in fields:
        timestamp_int = int(field['time'])
        bei = basic_event_info(host_class, timestamp_int)
        bei['window_title'] = field['window_title']
        key = (hostname, timestamp_int)
        if key in gtd_data:
            gtd_data[key].update(bei)
        else:
            gtd_data[key] = bei

def image_to_histograms(image_filename):
    """Read an image, return a triple of histograms.

    The histograms are linear histograms of red, green, and blue
    intensities respectively.

    """
    image = cv2.imread(image_filename)
    red   = cv2.calcHist([image], channels=[0], mask=None, histSize=[256], ranges=[0, 256])
    green = cv2.calcHist([image], channels=[1], mask=None, histSize=[256], ranges=[0, 256])
    blue  = cv2.calcHist([image], channels=[2], mask=None, histSize=[256], ranges=[0, 256])
    return (red, green, blue)

def scan_window_thumbnails(image_filenames, gtd_data):
    """Scan window images (thumbnails) and annotate gtd_data.

    """
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
            image_time = int(host_time_match.groups()[1])
            red, green, blue = image_to_histograms(image_name)
            hist = {'red_histogram': red,
                    'green_histogram': green,
                    'blue_histogram': blue,
                    'window_thumbnail_filename': image_name}

            key = (image_host, image_time)
            if key in gtd_data:
                num_found += 1
                gtd_data[key].update(hist)
            else:
                # Maybe the snapshot happened a smidgeon after the
                # window label was recorded.  This race condition can
                # no longer happen, but it used to be able to happen.
                key2 = (image_host, image_time - 1)
                if key2 in gtd_data:
                    num_found_minus += 1
                    gtd_data[key2].update(hist)
                else:
                    num_missed += 1
                    bei = basic_event_info(get_host_class(image_host), image_time)
                    hist.update(bei)
                    gtd_data[key] = hist
    print('Image thumbnails: found ' +
          '{f} at first, {p} more at -1, {m} missed, {pe} parse errors'.format(
              f=num_found, p=num_found_minus, m=num_missed, pe=num_parse_errors))

def read_window_titles(filenames, gtd_data):
    """Read the host__time (window title) files.

    Filenames is an array of filenames containing timestamped window
    titles.

    The dict gtd_data maps (hostname, timestamp) to keys as described
    in gtd_read().

    We modify gtd_data in place.

    """
    task_pattern = re.compile('^.*/([^/]*)__(.*)')
    for filename in filenames:
        task_match = re.match(task_pattern, filename)
        if task_match is not None:
            hostname = task_match.groups()[0]
            # And task_match.groups()[1] is the session start time
            read_window_titles_one_file(filename, hostname, gtd_data)

def gtd_read(data_dir, image_data_dir, gtd_data):
    """Read all the gtd data available.

    The directory in which gtd data files live is data_dir (for
    timestamped window names) and image_data_dir (for thumbnail
    images).

    The timestamped window names are in files whose format is (for
    each line) a timestamp (seconds since the epoch), a space, and
    then the name of the active window at that moment in time.  The
    filename contains the hostname and (not of interest to us in
    analysis), two underscores and the time at which the file began
    being used.  The session start time has format YYYY-MM-DD_HHMMSS.
    The active window title may have spaces.

    The thumbnail images are stored one per file, with names noting
    the host and timestamp.

    We call these things window titles and window thumbnails.  Our
    eventual goal is to label those data points.

    If present, gtd_data is data we've already loaded (and perhaps
    analysed.  This function is therefore idempotent in the absence of
    external activity.  We modify gtd_data in place but return it in
    case it was absent.

    Return a dictionary whose keys are (hostname, timestamp) and whose
    values are dictionaries with these keys:

      host_class  (laptop or desktop)
      window_title
      window_thumbnail_filename
      window_thumbnail_red_histogram
      window_thumbnail_green_histogram
      window_thumbnail_blue_histogram
        (the histograms are not normalised)
      timestamp_int  (seconds since the epoch)
      timestamp  (datetime.datetime)
      weekday
      hours  (since midnight UTC)
      minutes  (since midnight UTC)
      seconds  (since midnight UTC)
      date  (date.date)

    """
    if gtd_data is None:
        gtd_data = {}
    filenames = get_window_title_filenames(data_dir)
    read_window_titles(filenames, gtd_data)
    print('We have {num_wn} points after reading window titles'.format(
        num_wn=len(gtd_data)))

    image_filenames = get_image_filenames(image_data_dir)
    scan_window_thumbnails(image_filenames, gtd_data)
    print('We have {num_wn} points after reading window contents'.format(
        num_wn=len(gtd_data)))

    return gtd_data

def gtd_dump(filename, gtd_data):
    """Dump a pickled dictionary of the data structure from gtd_read().

    Note that we do nothing to protect against race conditions.  Only
    one gtd analytics process at a time should be running.

    """
    start_time = time.time()
    print('Writing {n} objects to {fn}'.format(n=len(gtd_data), fn=filename))
    pickle.dump(gtd_data, open(filename, 'wb'))
    time_diff = time.time() - start_time
    print('Wrote {fn} in {t:.2f} seconds'.format(fn=filename, t=time_diff))

def gtd_load(filename):
    """Load a pickled file written via gtd_dump() and return it.

    Note that we do nothing to protect against race conditions.  Only
    one gtd analytics process at a time should be running.

    """
    try:
        start_time = time.time()
        print('Reading {fn}...'.format(fn=filename))
        gtd_data = pickle.load(open(filename, 'rb'))
        time_diff = time.time() - start_time
        print('Read {fn}, got {n} objects in {t:.2f} seconds'.format(
            fn=filename, n=len(gtd_data), t=time_diff))
        return gtd_data
    except IOError:
        print('Failed to read {fn}, initialising to empty.'.format(fn=filename))
    return {}

def gtd_data_directory():
    """Return the name of the canonical data directory.
    """
    if  'vagrant' in os.environ['VIRTUAL_ENV']:
        return '/vagrant/data_copy/gtd'
    return '{home}/data/gtd'.format(home=getenv('HOME'))

def gtd_data_img_directory():
    """Return the name of the canonical data directory.
    """
    if  'vagrant' in os.environ['VIRTUAL_ENV']:
        return '/vagrant/data_copy/gtd-img'
    return '{home}/data/gtd-img'.format(home=getenv('HOME'))

def gtd_data_store():
    """Return the path to the file where we store features.

    Bug: no one creates the directory nor (better) checks for its
    existence.

    """
    return '{home}/.gtd_analysis/data.pickle'.format(home=getenv('HOME'))

if __name__ == '__main__':
    print("Don't run lib_gtd.  Consider refresh.py.  And look at README.md.")
