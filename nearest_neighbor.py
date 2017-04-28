#!/usr/bin/env python

"""
"""

from lib_gtd import gtd_load, filter_n_last_days
from operator import itemgetter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from sklearn.neighbors import KNeighborsClassifier
import argparse
import numpy as np
import pandas as pd
import pickle

def learn_nearest_neighbors(input_filename, output_model_filename):
    """Learn a kNN model based on tasks and labeled tasks.

    Persist the model for later use.
    """
    all_tasks = gtd_load(input_filename, 'tasks')
    training_size = 1000
    tasks = all_tasks.sample(training_size, replace=False)
    print('Subsampled to {n} events'.format(n=training_size))

    labeled_tasks = gtd_load(input_filename, 'labels')
    task_labels = pd.merge(labeled_tasks, all_tasks, on=['time', 'hostname'], how='inner')

    # First tokenize the words in the labels (window titles) and fit weights.
    training_labels = np.array([x for x in tasks.label.unique() if x != ''])
    target_labels = task_labels.label.unique()
    all_labels = np.unique(np.concatenate((training_labels, target_labels), 0))
    print('Learning  word model (TF-IDF) based on {num_labels} named tasks.'.format(
        num_labels=len(all_labels)))
    vectorizer = TfidfVectorizer(analyzer='word')
    ft_matrix = vectorizer.fit_transform(all_labels)
    print('Got word model: {r}x{c}.'.format(r=ft_matrix.shape[0], c=ft_matrix.shape[1]))
    print('Tokenized {num} words.'.format(num=len(vectorizer.get_feature_names())))

    # Now fit a NN classifier on the weighted TF-IDF points.
    X_points = [vectorizer.transform(x) for x in target_labels]
    target_label_map = {index: value for index, value in enumerate(target_labels)}
    target_label_rmap = {value: index for index, value in target_label_map.iteritems()}
    y_points = target_label_map.keys()
    neighbors = KNeighborsClassifier(n_neighbors=15)
    neighbors.fit(X_points, y_points)
    print(neighbors.predict(task_labels.label[0]))

    with open(output_model_filename, 'w') as file_write_ptr:
        pickle.dump([vectorizer, ft_matrix], file_write_ptr)

def classify_nearest_neighbors(input_filename, model_filename, num_days):
    """Classify the last num_days of points.

    """
    with open(model_filename, 'r') as file_read_ptr:
        [vectorizer, ft_matrix] = pickle.load(file_read_ptr)
    tasks = gtd_load(input_filename, 'tasks')
    num_days = 10
    first_day, dataframe = filter_n_last_days(tasks, 10)
    #vectorizer.predict(

def main():
    """Do what we do.

    Arguments are plot (w x h) in pixels divided by 100."""
    parser = argparse.ArgumentParser()
    named_args = parser.add_argument_group('arguments')
    named_args.add_argument('-i', '--input-filename', type=str,
                            default='/tmp/gtd-data',
                            help='Path and filename prefix to pickled task data file')
    named_args.add_argument('-o', '--model-filename', type=str,
                            default='/tmp/nearest_neighbor',
                            help='Name of model file (to store if learn, to read otherwise)')
    named_args.add_argument('--learn', action='store_true',
                            help='Learn the model and store it')
    named_args.add_argument('--num_days', default=10,
                            help='Show classification for the past num_days')
    # parser.add_argument('--verbose', dest='verbose', action='store_true')
    args = parser.parse_args()
    if args.learn:
        learn_nearest_neighbors(args.input_filename, args.model_filename)
        return
    classify_nearest_neighbors(args.input_filename, args.model_filename, args.num_days)

if __name__ == '__main__':
    main()
