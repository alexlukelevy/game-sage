import psycopg2
import sys

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline


class Game:
    def __init__(self, name, **kwargs):
        self.name = name
        self.properties = kwargs


class ItemSelector(BaseEstimator, TransformerMixin):
    def __init__(self, key):
        self.key = key

    def fit(self, x, y=None):
        return self

    def transform(self, games):
        return map(lambda game: game.properties[self.key], games)


def get_genres(data):
    try:
        genres = map(lambda g: g['name'], data['genres'])
        return ','.join(genres)
    except KeyError:
        return ''


def get_themes(data):
    try:
        genres = map(lambda g: g['name'], data['themes'])
        return ','.join(genres)
    except KeyError:
        return ''


def get_name(data):
    return data['name']


def get_games(curr):
    # selecting more popular games
    curr.execute('SELECT data FROM games WHERE data->>\'reviews\' IS NOT NULL ORDER BY id DESC LIMIT 200')
    games = map(lambda row: row[0], curr.fetchall())

    return list(map(lambda game: Game(get_name(game), genres=get_genres(game), themes=get_themes(game)), games))


def cluster(games):
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

    features = FeatureUnion(transformer_list=[('genre', genre_pipeline), ('theme', theme_pipeline)])

    x = features.fit_transform(games)

    n_clusters = 40

    km = KMeans(n_clusters=n_clusters)
    km.fit(x)

    print("Top terms per cluster:")

    # order_centroids = km.cluster_centers_.argsort()[:, ::-1]

    # terms = features.get_feature_names()
    # print(terms)

    # for i in range(n_clusters):
    #     print("Cluster %d:" % i, end='')
    #     for ind in order_centroids[i, :10]:
    #         print(' %s' % terms[ind], end='')
    #     print()

    # print(km.labels_)

    results = dict()

    for i, game in enumerate(games):
        cluster_num = km.labels_[i]

        if cluster_num not in results:
            results[cluster_num] = []

        results[cluster_num].append(game.name)

    for key, value in results.items():
        print('Cluster {}'.format(key))
        print('----------')
        print('\n'.join(value))
        print('\n')


def run():
    conn = psycopg2.connect(sys.argv[1])
    curr = conn.cursor()

    games = get_games(curr)
    cluster(games)

    curr.close()
    conn.close()


run()
