#!/usr/bin/env python

"""Generate a plot of my recent time usage at my computer.

If a first and numeric argument is present, it is the number of days of
history to show.  The default is ten.

"""

from lib_gtd import gtd_load
import argparse
import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot_recent_days(input_filename, output_filename, num_days,
                     width, height):
    """Generate an activity plot, one band per day.

    Show num_days days (wall time, even for days with no activity) with
    the most recent at the bottom.
    """
    dataframe = gtd_load(
        input_filename, 'tasks').loc[:, ['datetime', 'host_class']]

    # We'll first filter to a bit more than the range we want so that
    # we have less data, then append a date field and do the precise
    # filter.
    dataframe = dataframe[dataframe.datetime >
                          np.datetime64(datetime.datetime.now()) -
                          np.timedelta64(num_days + 1, 'D')]
    dataframe['date'] = pd.Series(
        [val.to_datetime().date() for val in dataframe.datetime],
        index=dataframe.index)
    dataframe['time'] = pd.Series(
        [val.to_datetime().time() for val in dataframe.datetime],
        index=dataframe.index)
    first_day = np.datetime64(datetime.date.today()) - \
                np.timedelta64(num_days - 1, 'D')
    # Strangely, numpy.datetime64.tolist() returns a datetime.date.
    dataframe = dataframe[dataframe.date >= first_day.tolist()]

    fig, ax = plt.subplots(num_days, sharex=True, sharey=True)
    for day_num in range(num_days):
        # TODO(jeff@purple.com): Should plot each host at a different y value.
        this_day = dataframe[dataframe.date == (first_day + day_num).tolist()]
        desktop = this_day[this_day.host_class == 'desktop']
        laptop = this_day[this_day.host_class == 'laptop']
        ax[day_num].plot(desktop.time.as_matrix(),
                         np.ones(len(desktop)),
                         '.b')
        ax[day_num].plot(laptop.time.as_matrix(),
                         np.ones(len(laptop)),
                         '.r')
        ax[day_num].set_ylabel(
            (first_day + np.timedelta64(day_num, 'D')).astype(
                datetime.date).isoformat(),
            rotation='horizontal',
            labelpad=40)
        ax[day_num].set_ybound(0.5, 1.5)
        ax[day_num].set_position([0.1, 0.1, 8.0, 1.0])
        ax[day_num].set_yticks([])
    ax[0].set_title('Computer Use by Day (desktop=blue, laptop=red)')
    min_tick = 0
    max_tick = 86400
    ax[0].set_xbound(lower=min_tick, upper=max_tick)
    ax[0].set_xticks(np.linspace(min_tick, max_tick, 9))
    fig.subplots_adjust(hspace=0)
    fig = plt.gcf()
    fig.set_size_inches(width, height)
    plt.savefig(output_filename, dpi=100)
    print('Wrote {fn}'.format(fn=output_filename))

def main():
    """Do what we do."""
    parser = argparse.ArgumentParser()
    named_args = parser.add_argument_group('arguments')
    named_args.add_argument('-i', '--input-filename', type=str,
                            default='/tmp/gtd-data',
                            help='Path and filename prefix to pickled data file')
    named_args.add_argument('-o', '--output-filename', type=str,
                            default='/tmp/gtd-activity.png',
                            help='Name of image file to output')
    named_args.add_argument('--num-days', type=int, default=10,
                            help='Number of days for which to compute and display data')
    named_args.add_argument('-W', '--width', default=20,
                            help='Width in pixels/100 for output image')
    named_args.add_argument('-H', '--height', default=10,
                            help='Height in pixels/100 for output image')
    # parser.add_argument('--verbose', dest='verbose', action='store_true')
    args = parser.parse_args()

    plot_recent_days(args.input_filename, args.output_filename,
                     args.num_days,
                     args.width, args.height)

if __name__ == '__main__':
    main()
