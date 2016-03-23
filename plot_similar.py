#!/usr/bin/env python3

"""Generate a plot of my recent time usage at my computer.

If a first and numeric argument is present, it is the number of days of
history to show.  The default is ten.

"""

from lib_gtd import gtd_load
from optparse import OptionParser
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.manifold import MDS
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import matplotlib.pyplot as plt

def plot_similar(input_filename, output_filename, target, width, height):
    """Find some phrases similar to target.

    """
    dataframe = gtd_load(
        input_filename, 'tasks')
    labels = dataframe.label.unique()
    print('Got {n} labels.'.format(n=len(labels)))
    labels = np.random.choice(labels, len(labels) / 20, False)
    if target not in labels:
        labels = np.append(labels, target)
    print('  Sub-sampled to {n} labels.'.format(n=len(labels)))

    print('Learning model...')
    vectorizer = HashingVectorizer(analyzer='word')
    ft_matrix = vectorizer.fit_transform(labels)
    print('Got model: {r}x{c}.'.format(r=ft_matrix.shape[0], c=ft_matrix.shape[1]))
    cosine_distance = 1 - cosine_similarity(ft_matrix)
    
    target_index = list(labels).index(target)
    print('Found target at index {i}'.format(i=target_index))
    if len(labels) != cosine_distance.shape[0]:
        print('Warning: {num_labels} labels, {num_dist} distances'.format(
            num_labels=len(labels), num_dist=cosine_distance.shape[0]))

    # Two components as we're plotting points in a two-dimensional plane.
    # "Precomputed" because we provide a distance matrix.
    # We specify `random_state` so the plot is reproducible.
    mds = MDS(n_components=2, dissimilarity="precomputed", random_state=1)
    pos = mds.fit_transform(cosine_distance) # shape (n_components, n_samples)
    print('MDS projection completed.')

    print('Scattering (among {n} points)...'.format(n=len(labels)))
    for pattern_index in range(len(labels)):
        distance = cosine_distance[target_index, pattern_index]
        pattern = labels[pattern_index]
        if pattern == target:
            color = 'black'
            ecolor = 'black'
        elif distance < .5:
            color = 'blue'
            ecolor = 'none'
        else:
            color = 'cyan'
            ecolor = 'none'
        plt.scatter(x=pos[pattern_index, 0], y=pos[pattern_index, 1], \
                    c=color, edgecolor=ecolor)
    fig = plt.gcf()
    fig.set_size_inches(width, height)
    plt.savefig(output_filename, dpi=100)
    print('Wrote {fn}'.format(fn=output_filename))

def main():
    """Do what we do."""
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="input_filename",
                      default='/tmp/gtd-data',
                      help="input filename", metavar="FILE")
    parser.add_option("-o", "--output", dest="output_filename",
                      default='/tmp/plot-similar.png',
                      help="output filename", metavar="FILE")
    parser.add_option(
        "--target",
        dest="target",
        help="Target phrase for finding similar phrases")
    parser.add_option("-W", "--width",
                      dest="width", default=10,
                      help="Width in pixels/100 for output image")
    parser.add_option("-H", "--height",
                      dest="height", default=6,
                      help="Height in pixels/100 for output image")

    (options, args) = parser.parse_args()
    plot_similar(options.input_filename, options.output_filename, \
                 options.target, \
                 options.width, options.height)

if __name__ == '__main__':
    main()
