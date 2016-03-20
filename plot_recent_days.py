#!/usr/bin/env python3

"""Generate a plot of my recent time usage at my computer.

If a first and numeric argument is present, it is the number of days of
history to show.  The default is ten.

If a second and third arguments X and Y are present, generate a png with
dimensions X x Y.  Default is display to the screen.
"""

from lib_gtd import gtd_load
from optparse import OptionParser
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
        input_filename, 'tasks').loc[:, ['datetime', 'hostname']]

    # We'll first filter to a bit more than the range we want so that
    # we have less data, then append a date field and do the precise
    # filter.
    dataframe = dataframe[dataframe.datetime >
                          np.datetime64(datetime.datetime.now()) - \
                          np.timedelta64(num_days + 1, 'D')]
    dataframe['date'] = pd.Series(
        [val.to_datetime().date() for val in dataframe.datetime], \
        index=dataframe.index)
    dataframe['time'] = pd.Series(
        [val.to_datetime().time() for val in dataframe.datetime], \
        index=dataframe.index)
    dataframe['offset'] = pd.Series(3600 * t.hour + 60 * t.minute + t.second
                                    for t in dataframe.time)
    first_day = np.datetime64(datetime.date.today()) - \
                np.timedelta64(num_days - 1, 'D')
    dataframe = dataframe[dataframe.date >= first_day]

    fig, ax = plt.subplots(num_days, sharex=True, sharey=True)
    for day_num in range(num_days):
        # TODO(jeff@purple.com): Should plot each host at a different y value.
        this_day = dataframe[dataframe.date == first_day + day_num]
        ax[day_num].plot(this_day.time.as_matrix(),
                         np.ones(len(this_day)),
                         '.')
        ax[day_num].set_ylabel(
            (first_day + np.timedelta64(day_num, 'D')).astype(
                datetime.date).isoformat(),
            rotation='horizontal',
            labelpad=40)
        ax[day_num].set_ybound(0.5, 1.5)
        ax[day_num].set_position([0.1, 0.1, 8.0, 1.0])
        ax[day_num].set_yticks([])
    ax[0].set_title('Computer Use by Day')
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
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="input_filename",
                      default='/tmp/gtd-data',
                      help="input filename", metavar="FILE")
    parser.add_option("-o", "--output", dest="output_filename",
                      default='/tmp/gtd-recent-days.png',
                      help="output filename", metavar="FILE")
    parser.add_option(
        "-n", "--num-days",
        dest="num_days", default=10,
        help="Number of days for which to compute and display data")
    parser.add_option("-W", "--width",
                      dest="width", default=10,
                      help="Width in pixels/100 for output image")
    parser.add_option("-H", "--height",
                      dest="height", default=6,
                      help="Height in pixels/100 for output image")

    (options, args) = parser.parse_args()
    plot_recent_days(options.input_filename, options.output_filename, \
                     options.num_days, \
                     options.width, options.height)

if __name__ == '__main__':
    main()
