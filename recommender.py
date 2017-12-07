from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline


class ItemSelector(BaseEstimator, TransformerMixin):
    def __init__(self, key):
        self.key = key

    def fit(self, x, y=None):
        return self

    def transform(self, games):
        return map(lambda game: game.properties[self.key], games)


def cluster(games, n_clusters):
    def tokenizer(words):
        return words.split(',')

    genre_pipeline = Pipeline([
        ('selector', ItemSelector('genres')),
        ('tfidf', TfidfVectorizer(input='content', analyzer='word', tokenizer=tokenizer, lowercase=True))
    ])

    theme_pipeline = Pipeline([
        ('selector', ItemSelector('themes')),
        ('tfidf', TfidfVectorizer(input='content', analyzer='word', tokenizer=tokenizer, lowercase=True))
    ])

    concept_pipeline = Pipeline([
        ('selector', ItemSelector('concepts')),
        ('tfidf', TfidfVectorizer(input='content', analyzer='word', tokenizer=tokenizer, lowercase=True))
    ])

    features = FeatureUnion(
        transformer_list=[
            ('genre', genre_pipeline),
            ('theme', theme_pipeline),
            ('concept', concept_pipeline),
        ],
        transformer_weights={
            'genre': 1,
            'theme': 0.2,
            'concept': 0.3,
        }
    )

    x = features.fit_transform(games)

    km = KMeans(n_clusters=n_clusters, max_iter=10000)
    km.fit(x)

    results = dict()

    for i, game in enumerate(games):
        cluster_num = km.labels_[i]

        if cluster_num not in results:
            results[cluster_num] = []

        results[cluster_num].append(game)

    for key, values in results.items():
        print('Cluster {}'.format(key))
        print('----------')
        for game in values:
            print(game.name)
        print('\n')

    return results.values()
