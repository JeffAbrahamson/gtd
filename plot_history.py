#!/usr/bin/env python3

"""Generate a plot of my time usage at my computer by day.

If first and second arguments X and Y are present, generate a png with
dimensions X x Y.  Default is display to the screen.
"""

from lib_gtd import gtd_load
from optparse import OptionParser
import matplotlib.pyplot as plt
import numpy as np

def plot_history(input_filename, output_filename, width, height):
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
    first_task_date = min(tasks.datetime)
    tasks['day_index'] = tasks.apply(
        lambda row: (row['datetime'] - first_task_date).days, axis=1)
    print('Got days')
    x_points = tasks.day_index
    y_points = 1440 - tasks.minutes
    plt.xlim(0, max(x_points))
    plt.ylim(0, 1440)
    fig, ax = plt.subplots(1, 1)
    ax.set_yticks(np.linspace(0, 1440, 9))
    ax.set_yticklabels(['midnight', 21, 18, 15, 'noon', 9, 6, 3, 'midnight'])
    print('Scattering points...')
    plt.scatter(x_points, y_points, edgecolors='none')
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
    parser.add_option("-W", "--width",
                      dest="width", default=20,
                      help="Width in pixels/100 for output image")
    parser.add_option("-H", "--height",
                      dest="height", default=10,
                      help="Height in pixels/100 for output image")

    (options, args) = parser.parse_args()
    plot_history(options.input_filename, options.output_filename, \
                 options.width, options.height)

if __name__ == '__main__':
    main()