#!/usr/bin/env python

"""Generate a plot of time spent in activities maching string by day.
"""

from lib_gtd import gtd_load
import argparse
import datetime
import matplotlib.cm as cm
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

def plot_history(input_filename, output_filename, width, height,
                 activities):
    """Generate an activity plot showing time spent in activity

    The horizontal axis is time (days), the vertical axis is minutes
    in activity (as determined by text match).

    """

    print(activities)
    activity = activities[0]    # TODO.  For the moment, just handle one.
    print(activity)
    tasks = gtd_load(input_filename, 'tasks')
    print('Dataframe loaded')
    tasks['date'] = tasks.apply(
        lambda row: datetime.date(row['datetime'].year,
                                  row['datetime'].month,
                                  row['datetime'].day), axis=1)
    print('Got dates')
    x_dates = []
    y_minutes = []
    date_groups = tasks.groupby(['date'])
    for group_date, group_df in date_groups:
        count = group_df.loc[group_df.label.str.contains(activity)].time.count()
        x_dates.append(group_date)
        y_minutes.append(count)

    legend = []
    plt.plot(x_dates, y_minutes, '-r')
    legend.append(mpatches.Patch(color='g',
                                 label='Minutes using {activity}'.format(
                                     activity=activity)))

    plt.legend(handles=legend)
    plt.title('Minutes in {activity} by day'.format(
        activity=activity))
    fig = plt.gcf()
    fig.set_size_inches(width, height)
    plt.savefig(output_filename, dpi=100)

def main():
    """Do what we do.

    Arguments are plot (w x h) in pixels divided by 100."""
    parser = argparse.ArgumentParser()
    named_args = parser.add_argument_group('arguments')
    named_args.add_argument('-i', '--input-filename', type=str,
                            default='/tmp/gtd-data',
                            help='Path and filename prefix to pickled data file')
    named_args.add_argument('-o', '--output-filename', type=str,
                            default='/tmp/gtd-activity.png',
                            help='Name of image file to output')
    named_args.add_argument('--activity', type=str,
                            help='A comma-separated list of activities to plot.  ' +
                            'An event is an activity if the window title contains this string.')
    named_args.add_argument('-W', '--width', default=20,
                            help='Width in pixels/100 for output image')
    named_args.add_argument('-H', '--height', default=10,
                            help='Height in pixels/100 for output image')
    # parser.add_argument('--verbose', dest='verbose', action='store_true')
    args = parser.parse_args()
    plot_history(args.input_filename, args.output_filename,
                 args.width, args.height,
                 args.activity.split(','))

if __name__ == '__main__':
    main()
