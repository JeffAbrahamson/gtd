#!/usr/bin/env python

"""Report on the labeling and feature status of points in the store.

"""

from lib_gtd import gtd_data_store, gtd_data_directory, gtd_data_img_directory
from lib_gtd import gtd_load, gtd_read, gtd_dump

def main():
    """The main section is not particularly useful except as documentation."""
    filename = gtd_data_store()
    gtd_data = gtd_load(filename)
    num_points = len(gtd_data)
    num_window_titles = 0
    num_images = 0
    for name, point in gtd_data.iteritems():
        if 'window_title' in point:
            # We expect this always to be true.
            num_window_titles += 1
        if 'red_histogram' in point:
            num_images += 1
    print('{p} points of which {missing} have no window title.'.format(
        p=num_points, missing=num_points - num_window_titles))
    print('{img} points have image histograms'.format(
        img=num_images))

if __name__ == '__main__':
    main()
