#!/usr/bin/env python

"""Generate a plot of my pause behaviour by day.
"""

from __future__ import print_function
from lib_gtd import gtd_load
import argparse
import datetime
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

def plot_pauses(input_filename, output_filename, width, height,
                max_pause, sum_pauses):
    """Generate an activity plot showing pauses

    The horizontal axis is time (days), the vertical axis is minutes
    of pause (maximum or cumulative).

    """
    tasks = gtd_load(input_filename, 'tasks')
    print('Dataframe loaded')
    x_dates = []
    y_sums = []
    y_max = []
    date_groups = tasks.groupby(['date'])
    for group_date, group_df in date_groups:
        last_time = None
        max_interval = 0
        sum_interval = 0
        for row in group_df.sort_values(by=['time']).itertuples():
            this_time = int(row.time)
            if last_time is not None:
                interval_minutes = (this_time - last_time) / 60
                # Pauses should last at least a couple minutes,
                # otherwise maybe it's clock error.
                if 2 < interval_minutes and interval_minutes < max_pause:
                    sum_interval += interval_minutes
                    max_interval = max(interval_minutes, max_interval)
            last_time = this_time
        x_dates.append(group_date)
        y_sums.append(sum_interval)
        y_max.append(max_interval)

    legend = []
    plt.plot(x_dates, y_max, '-g')
    legend.append(mpatches.Patch(color='g', label='longest pause'))
    if sum_pauses:
        plt.plot(x_dates, y_sums, ':b')
        legend.append(mpatches.Patch(color='b', label='sum of pauses'))

    plt.legend(handles=legend)
    plt.title('Pauses by day (less than {mx} minutes)'.format(mx=max_pause))
    fig = plt.gcf()
    fig.set_size_inches(width, height)
    plt.savefig(output_filename, dpi=100)
    print('Wrote {fn}'.format(fn=output_filename))

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
    named_args.add_argument('--max-pause', type=int, default=60,
                            help='Maximum pause length in minutes above which to ignore')
    named_args.add_argument('--sum', action='store_true',
                            help="Show sum of day's pauses rather than maximum")
    named_args.add_argument('-W', '--width', default=20,
                            help='Width in pixels/100 for output image')
    named_args.add_argument('-H', '--height', default=10,
                            help='Height in pixels/100 for output image')
    # parser.add_argument('--verbose', dest='verbose', action='store_true')
    args = parser.parse_args()

    plot_pauses(args.input_filename, args.output_filename,
                args.width, args.height,
                args.max_pause, args.sum)

if __name__ == '__main__':
    main()
