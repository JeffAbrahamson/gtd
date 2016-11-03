#!/usr/bin/env python

"""Generate a plot of my time usage at my computer by day.
"""

from lib_gtd import gtd_load
import argparse
import datetime
import matplotlib.cm as cm
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

def plot_history(input_filename, output_filename, width, height,
                 color_host, color_host_class):
    """Generate an activity plot.

    The horizontal axis is time (days), the vertical axis is minutes
    spent at my computer per day.

    """
    tasks = gtd_load(input_filename, 'tasks')
    print('Dataframe loaded')
    tasks['date'] = tasks.apply(
        lambda row: datetime.date(row['datetime'].year,
                                  row['datetime'].month,
                                  row['datetime'].day), axis=1)
    print('Got dates')
    # Express as a date rather than datetime so that we don't cut days
    # in two at the first recorded time each day.
    first_task_date = datetime.date.fromtimestamp(
        (min(tasks.datetime).to_datetime()
         - datetime.datetime.utcfromtimestamp(0)).total_seconds())
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
    if color_host or color_host_class:
        if color_host:
            column = 'hostname'
        else:
            column = 'host_class'
        names = tasks[column].unique()
        name_map = {names[index]: index
                    for index in range(len(names))}
        print(names)
        colors = cm.rainbow(np.linspace(0, 1, len(names)))
        legend = []
        for name in names:
            name_tasks = tasks.loc[tasks[column] == name]
            name_x_points = name_tasks.day_index
            name_y_points = 1440 - name_tasks.minutes
            name_color = colors[name_map[name]]
            plt.scatter(name_x_points, name_y_points, color=name_color,
                        s=1, edgecolors='none')
            legend.append(mpatches.Patch(color=name_color, label=name))
        plt.legend(handles=legend)
    else:
        plt.scatter(x_points, y_points, s=1, edgecolors='none')
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
    named_args.add_argument('--color-host', action='store_true',
                            help='Color different hosts differently')
    named_args.add_argument('--color-host-class', action='store_true',
                            help='Color different host classes differently')
    named_args.add_argument('-W', '--width', default=20,
                            help='Width in pixels/100 for output image')
    named_args.add_argument('-H', '--height', default=10,
                            help='Height in pixels/100 for output image')
    # parser.add_argument('--verbose', dest='verbose', action='store_true')
    args = parser.parse_args()
    plot_history(args.input_filename, args.output_filename,
                 args.width, args.height, args.color_host, args.color_host_class)

if __name__ == '__main__':
    main()
