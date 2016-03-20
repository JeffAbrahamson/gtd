#!/usr/bin/env python3

"""Generate a plot of my pause behaviour by day.
"""

from lib_gtd import gtd_load
from optparse import OptionParser
import datetime
import matplotlib.cm as cm
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

def plot_history(input_filename, output_filename, width, height,
                 max_pause, sum_pauses):
    """Generate an activity plot showing pauses

    The horizontal axis is time (days), the vertical axis is minutes
    of pause (maximum or cumulative).

    """
    tasks = gtd_load(input_filename, 'tasks')
    print('Dataframe loaded')
    tasks['date'] = tasks.apply(
        lambda row: datetime.date(row['datetime'].year,
                                  row['datetime'].month,
                                  row['datetime'].day), axis=1)
    print('Got dates')
    x_dates = []
    #x_offsets = []
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
        #x_offsets.append(row.offset)
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

def main():
    """Do what we do.

    Arguments are plot (w x h) in pixels divided by 100."""
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="input_filename",
                      default='/tmp/gtd-data',
                      help="input filename", metavar="FILE")
    parser.add_option("-o", "--output", dest="output_filename",
                      default='/tmp/gtd-pauses.png',
                      help="output (image) filename", metavar="FILE")
    parser.add_option("--max-pause", dest="max_pause",
                      default=60, type=int,
                      help="Maximum pause length in minutes above which to ignore")
    parser.add_option("--sum", dest="sum_pauses",
                      default=False, action="store_true",
                      help="Show sum of day's pauses rather than maximum")
    parser.add_option("-W", "--width",
                      dest="width", default=20,
                      help="Width in pixels/100 for output image")
    parser.add_option("-H", "--height",
                      dest="height", default=10,
                      help="Height in pixels/100 for output image")

    (options, args) = parser.parse_args()
    plot_history(options.input_filename, options.output_filename,
                 options.width, options.height,
                 options.max_pause, options.sum_pauses)

if __name__ == '__main__':
    main()
