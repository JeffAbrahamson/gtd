from __future__ import print_function

from lib_gtd import gtd_load
from sklearn import metrics
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
import numpy as np

# Playing to make sure I understand vectorizer.

fake_labels = ['Two roads diverged in a yellow wood,',
               'And sorry I could not travel both',
               'And be one traveler, long I stood',
               'And looked down one as far as I could',
               'To where it bent in the undergrowth']

vectorizer = CountVectorizer(analyzer='word')
XF = vectorizer.fit_transform(fake_labels)
vectorizer.inverse_transform(XT[2,:])

vectorizer = CountVectorizer(analyzer='word', ngram_range=(2,2))
XF = vectorizer.fit_transform(fake_labels)
vectorizer.inverse_transform(XT[2,:])

xx = X[0,:]
xx[xx.nonzero()]

pauvres_gens = [
    "Il est nuit. La cabane est pauvre, mais bien close.",
    "Le logis est plein d'ombre et l'on sent quelque chose"
]

# This is how I generated the BoW vectors in the Breizhcamp 2016
# presentation.:
vectorizer = CountVectorizer(analyzer='word')
ft = vectorizer.fit_transform(pauvres_gens)
# vectorizer.inverse_transform(ft)
ft.todense()


# This is how I generated the BoW example in the Breizhcamp 2016
# presentation.
from scipy.sparse import csr_matrix
from les_pauvres_gens import *
vectorizer = CountVectorizer(analyzer='word')
ft = vectorizer.fit_transform(les_pauvres_gens)

phrase_1 = "Comme il faut calculer la marée et le vent !"
phrase_1_code = vectorizer.transform([phrase_1])
phrase_1_code_t = phrase_1_code.transpose()
phrase_match = np.matrix(ft) * np.matrix(phrase_1_code_t)

vocab = np.array(vectorizer.get_feature_names())
veuve_index = vectorizer.vocabulary_['veuve']
phrase_index = ft[:, veuve_index]
phrase_number = list(phrase_index).index(1)
vectorizer.inverse_transform(ft[phrase_number, :])
les_pauvres_gens[phrase_number]

cosine_distance = 1 - cosine_similarity(ft)
[les_pauvres_gens[35], les_pauvres_gens[36]]
cosine_distance[35, 36]

for i in range(cosine_distance.shape[0]):
    for j in range(cosine_distance.shape[1]):
        if i < j:
            if cosine_distance[i, j] < .43:
                print('{i:3}, {j:3}: d={d:.2}\n   {t1}\n   {t2}'.format(
                    i=i, j=j, d=cosine_distance[i, j],
                    t1=les_pauvres_gens[i], t2=les_pauvres_gens[j]))

bigram_vectorizer = CountVectorizer(ngram_range=(1,2))
bigram_ft = bigram_vectorizer.fit_transform(les_pauvres_gens)
bigram_analyze = bigram_vectorizer.build_analyzer()
bigram_analyze(phrase_1)
