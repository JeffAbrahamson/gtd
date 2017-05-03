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
    num_image_filenames = 0
    num_image_histograms = 0
    num_ground_truth_window_titles = 0
    num_ground_truth_images = 0
    for name, point in gtd_data.iteritems():
        if 'window_title' in point:
            # We expect this always to be true.
            num_window_titles += 1
        if 'window_thumbnail_filename' in point:
            num_image_filenames += 1
        if 'red_histogram' in point:
            num_image_histograms += 1
        if 'ground_truth_window_title_label' in point:
            num_ground_truth_window_titles += 1
        if 'ground_truth_window_thumbnail_label' in point:
            num_ground_truth_images += 1
    print('{p} points of which {missing} have no window title.'.format(
        p=num_points, missing=num_points - num_window_titles))
    print('{img_fn} points have images of which {no_hist} have no histogram'.format(
        img_fn=num_image_filenames, no_hist=num_image_filenames - num_image_histograms))
    print('{win} window titles are hand-labeled, {img} image thumbnails are hand-labeled'.format(
        win=num_ground_truth_window_titles, img=num_ground_truth_images))
    print

if __name__ == '__main__':
    main()
