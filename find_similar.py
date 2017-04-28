#!/usr/bin/env python

"""Generate a plot of my recent time usage at my computer.

If a first and numeric argument is present, it is the number of days of
history to show.  The default is ten.

"""

from __future__ import print_function
import argparse
from lib_gtd import gtd_load
from operator import itemgetter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def find_similar(input_filename, target):
    """Find some phrases similar to target.

    """
    dataframe = gtd_load(input_filename, 'tasks')
    labels = dataframe.label.unique()
    print('Got {n} labels.'.format(n=len(labels)))

    max_score = .5
    # vectorizer = CountVectorizer(analyzer='word')
    # vectorizer = CountVectorizer(analyzer='word', ngram_range=(1,2))
    # vectorizer = HashingVectorizer(analyzer='word', ngram_range=(1,2))
    # For TfIdf, scores are bigger.
    max_score = .8
    vectorizer = TfidfVectorizer(analyzer='word')
    # vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1,2))
    print('Learning model (TF-IDF)...')
    ft_matrix = vectorizer.fit_transform(labels)
    print('Got model: {r}x{c}.'.format(r=ft_matrix.shape[0], c=ft_matrix.shape[1]))
    cosine_distance = 1 - cosine_similarity(ft_matrix)
    target_index = list(labels).index(target)
    print('Found target at index {i}'.format(i=target_index))
    if len(labels) != cosine_distance.shape[0]:
        print('Warning: {num_labels} labels, {num_dist} distances'.format(
            num_labels=len(labels), num_dist=cosine_distance.shape[0]))

    print('Searching for similarities (among {n})...'.format(n=len(labels)))
    similar = []
    for pattern_index in range(len(labels)):
        pattern = labels[pattern_index]
        if pattern != target:
            score = cosine_distance[target_index, pattern_index]
            if score < max_score:
                similar.append((pattern_index, score))
    similar.sort(key=itemgetter(1))
    print(len(similar))
    print(target)
    for candidate in similar[:10]:
        print('  {score:.2} {phrase}'.format(
            score=candidate[1], phrase=labels[candidate[0]]))
    print(target)
    for candidate in similar[90:100]:
        print('  {score:.2} {phrase}'.format(
            score=candidate[1], phrase=labels[candidate[0]]))

def main():
    """Do what we do."""
    parser = argparse.ArgumentParser()
    named_args = parser.add_argument_group('arguments')
    named_args.add_argument('--input-filename', type=str,
                            default='/tmp/gtd-data',
                            help='Path and filename prefix to pickled data file')
    named_args.add_argument('--target', type=str,
                            help='Target phrase for finding similar phrases')
    # parser.add_argument('--verbose', dest='verbose', action='store_true')
    args = parser.parse_args()

    find_similar(args.input_filename, args.target)

if __name__ == '__main__':
    main()
