#!/usr/bin/env python3

"""Generate a plot of my time usage at my computer by day.

If first and second arguments X and Y are present, generate a png with
dimensions X x Y.  Default is display to the screen.
"""

import datetime
from gtd import gtd_read, gtd_data_directory
import matplotlib.pyplot as plt
import pandas as pd
from sys import argv

def plot_history(png_dimensions):
    """Generate an activity plot.

    The horizontal axis is time (days), the vertical axis is minutes
    spent at my computer per day.

    If png_dimensions is not None, it is a tuple (x,y) specifying the
    dimensions of the png graphic to produce.  Otherwise, display to
    the screen.

    """
    data_dir = gtd_data_directory()
    dfd = gtd_read(data_dir)
    tasks = dfd['tasks']
    tasks['minutes'] = tasks.apply(
        lambda row: 60 * row['datetime'].hour + row['datetime'].minute, axis=1)
    first_task_date = min(tasks.datetime)
    tasks['day_index'] = tasks.apply(
        lambda row: (row['datetime'] - first_task_date).days, axis=1)
    X = tasks.day_index
    Y = tasks.minutes
    plt.xlim(0, max(X))
    plt.ylim(0, 1440)
    plt.scatter(X, Y, edgecolors='none')
    fig = plt.gcf()
    print(png_dimensions)
    fig.set_size_inches(png_dimensions[0], png_dimensions[1])
    plt.savefig('history.png', dpi=100)

def main():
    """Do what we do.

    Arguments are plot (w x h) in pixels divided by 100."""
    png_dimensions = (int(argv[1]), int(argv[2]))
    plot_history(png_dimensions)

if __name__ == '__main__':
    main()
