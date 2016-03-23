#!/usr/bin/env python3

"""Generate a plot of my recent time usage at my computer.

If a first and numeric argument is present, it is the number of days of
history to show.  The default is ten.

"""

from lib_gtd import gtd_load
from operator import itemgetter
from optparse import OptionParser
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def find_similar(input_filename, target):
    """Find some phrases similar to target.

    """
    dataframe = gtd_load(
        input_filename, 'tasks')
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
    print('Learning model...')
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
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="input_filename",
                      default='/tmp/gtd-data',
                      help="input filename", metavar="FILE")
    parser.add_option(
        "--target",
        dest="target",
        help="Target phrase for finding similar phrases")

    (options, args) = parser.parse_args()
    find_similar(options.input_filename, options.target)

if __name__ == '__main__':
    main()
