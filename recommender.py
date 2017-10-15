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


def get_name(data):
    return data['name']


def get_genres(data):
    try:
        genres = map(lambda g: g['name'], data['genres'])
        return ','.join(genres)
    except KeyError:
        return ''


def get_themes(data):
    try:
        themes = map(lambda g: g['name'], data['themes'])
        return ','.join(themes)
    except KeyError:
        return ''


def get_concepts(data):
    try:
        concepts = map(lambda g: g['name'], data['concepts'])
        return ','.join(concepts)
    except (KeyError, TypeError):
        return ''


def get_game(data):
    return Game(
        get_name(data),
        genres=get_genres(data),
        themes=get_themes(data),
        concepts=get_concepts(data)
    )


def get_games(curr):
    # selecting more popular games
    sql = '''
SELECT data
FROM games
WHERE
  data->>'reviews' IS NOT NULL
  AND data->>'themes' IS NOT NULL
  AND data->>'concepts' IS NOT NULL
  AND data->>'genres' IS NOT NULL
ORDER BY id DESC
LIMIT 200
'''
    curr.execute(sql)
    data = map(lambda row: row[0], curr.fetchall())

    return list(map(get_game, data))


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
    cluster(games, 50)

    curr.close()
    conn.close()


run()
