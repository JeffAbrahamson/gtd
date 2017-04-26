#!/usr/bin/env python

"""Scan the raw gtd data and add whatever points we find that we don't
already have in the database.  We create the database if necessary.

Using the word "database" is grandiose.  At the moment, this is simply
a file with an (enormous) pickled dictionary in it.  Not
computationally efficient, but efficient with my development time for
the moment.

"""

from lib_gtd import gtd_data_store, gtd_data_directory, gtd_data_img_directory
from lib_gtd import gtd_load, gtd_read, gtd_dump

def main():
    """The main section is not particularly useful except as documentation."""
    filename = gtd_data_store()
    data_dir = gtd_data_directory()
    data_img_dir = gtd_data_img_directory()
    gtd_data = gtd_load(filename)
    gtd_data = gtd_read(data_dir, data_img_dir, gtd_data)
    gtd_dump(filename, gtd_data)
    print(('Read {num_objects} objects.').format(
        num_objects=len(gtd_data)))

if __name__ == '__main__':
    main()
