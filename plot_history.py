#!/usr/bin/env python3

"""Generate a plot of my time usage at my computer by day.

If first and second arguments X and Y are present, generate a png with
dimensions X x Y.  Default is display to the screen.
"""

from lib_gtd import gtd_load
from optparse import OptionParser
import datetime
import matplotlib.cm as cm
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

def plot_history(input_filename, output_filename, width, height, color_hosts):
    """Generate an activity plot.

    The horizontal axis is time (days), the vertical axis is minutes
    spent at my computer per day.

    If png_dimensions is not None, it is a tuple (x,y) specifying the
    dimensions of the png graphic to produce.  Otherwise, display to
    the screen.

    """
    tasks = gtd_load(input_filename, 'tasks')
    print('Dataframe loaded')
    tasks['minutes'] = tasks.apply(
        lambda row: 60 * row['datetime'].hour + row['datetime'].minute, axis=1)
    print('Got minutes')
    tasks['date'] = tasks.apply(
        lambda row: datetime.date(row['datetime'].year,
                                  row['datetime'].month,
                                  row['datetime'].day), axis=1)
    print('Got dates')
    # Express as a date rather than datetime so that we don't cut days
    # in two at the first recorded time each day.
    first_task_date = datetime.date.fromtimestamp(
        min(tasks.datetime).timestamp())
    tasks['day_index'] = tasks.apply(
        lambda row: (row['date'] - first_task_date).days, axis=1)
    print('Got days')
    tasks['day_of_month'] = tasks.apply(
        lambda row: row['datetime'].day, axis=1)
    print('Got first of month')

    x_points = tasks.day_index
    y_points = 1440 - tasks.minutes
    plt.xlim(0, max(x_points))
    plt.ylim(0, 1440)
    fig, ax = plt.subplots(1, 1)
    first_days = tasks.loc[tasks['day_of_month'] == 1]
    ax.set_xticks(sorted(first_days.day_index.unique()))
    ax.set_xticklabels(['{m}-{y}'.format(m=x.month, y=x.year)
                        for x in sorted(first_days.date.unique())])
    ax.set_yticks(np.linspace(0, 1440, 9))
    ax.set_yticklabels(['midnight', 21, 18, 15, 'noon', 9, 6, 3, 'midnight'])
    print('Scattering points...')
    if color_hosts:
        hostnames = tasks.hostname.unique()
        host_map = {hostnames[index]: index
                    for index in range(len(hostnames))}
        print(hostnames)
        colors = cm.rainbow(np.linspace(0, 1, len(hostnames)))
        legend = []
        for host_name in hostnames:
            host_tasks = tasks.loc[tasks['hostname'] == host_name]
            host_x_points = host_tasks.day_index
            host_y_points = 1440 - host_tasks.minutes
            host_color = colors[host_map[host_name]]
            plt.scatter(host_x_points, host_y_points, color=host_color,
                        s=1, edgecolors='none')
            legend.append(mpatches.Patch(color=host_color, label=host_name))
        plt.legend(handles=legend)
    else:
        plt.scatter(x_points, y_points, s=1, edgecolors='none')
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
                      default='/tmp/gtd-history.png',
                      help="output (image) filename", metavar="FILE")
    parser.add_option("--color-hosts", dest="color_hosts",
                      default=False, action="store_true",
                      help="Color different hosts differently")
    parser.add_option("-W", "--width",
                      dest="width", default=20,
                      help="Width in pixels/100 for output image")
    parser.add_option("-H", "--height",
                      dest="height", default=10,
                      help="Height in pixels/100 for output image")

    (options, args) = parser.parse_args()
    plot_history(options.input_filename, options.output_filename, \
                 options.width, options.height, options.color_hosts)

if __name__ == '__main__':
    main()
