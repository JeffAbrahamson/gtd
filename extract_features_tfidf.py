#!/usr/bin/env python

"""Extract TF-IDF features and store in gtd_data structure.

Re-persist the data structure afterwords.
"""

import argparse
from lib_gtd import gtd_load, gtd_dump, gtd_data_store, time_main
from sklearn.feature_extraction.text import TfidfVectorizer

def extract_features(filename):
    """Learn a kNN model based on tasks and labeled tasks.

    Persist the model for later use.
    """
    gtd_data = gtd_load(filename)
    corpus = []
    for point in gtd_data.values():
        if 'window_title' in point:
            corpus.append(point['window_title'])

    print('Computing tf-idf weights.')
    vectorizer = TfidfVectorizer(analyzer='word')
    ft_matrix = vectorizer.fit_transform(corpus)
    # Well, we really only needed to fit()...

    print('Computing individual feature vectors.')
    for point in gtd_data.values():
        # Note that this array is sparse.  We can recover a dense
        # array with vec.toarray()[0] and even list(vec.toarray()[0]).
        if 'window_title' in point:
            # The thing returned by tranform is a sparse matrix
            # (scipy.sparse.csr.csr_matrix).  If necessary, we can
            # call toarray() on it and get a numpy.ndarray, but this
            # is much larger (order 10^2 vs 10^6).
            point['tf-idf'] = vectorizer.transform([point['window_title']])
    gtd_dump(filename, gtd_data)

def main():
    """Extract TF-IDF features from window titles.
    """
    parser = argparse.ArgumentParser()
    #named_args = parser.add_argument_group('arguments')
    args = parser.parse_args()
    data_filename = gtd_data_store()
    extract_features(data_filename)

if __name__ == '__main__':
    time_main(main)
