import psycopg2
import sys
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer


def get_genres(data):
    try:
        genres = map(lambda g: g['name'], data['genres'])
        return ','.join(genres)
    except KeyError:
        return ''


def get_name(data):
    return data['name']


def get_games(curr):
    # selecting more popular games
    curr.execute('SELECT data FROM games WHERE data->>\'reviews\' IS NOT NULL ORDER BY id DESC LIMIT 200')
    games = map(lambda row: row[0], curr.fetchall())

    return list(map(lambda game: (get_name(game), get_genres(game)), games))


def cluster(games):
    def tokenizer(words):
        return words.split(',')

    vectorizer = TfidfVectorizer(input='content', analyzer='word', tokenizer=tokenizer, lowercase=True)
    # vectorize the genres
    v = vectorizer.fit_transform(map(lambda game: game[1], games))

    km = KMeans(n_clusters=40)
    km.fit(v)

    print("Top terms per cluster:")

    order_centroids = km.cluster_centers_.argsort()[:, ::-1]

    terms = vectorizer.get_feature_names()
    # print(terms)

    for i in range(40):
        print("Cluster %d:" % i, end='')
        for ind in order_centroids[i, :10]:
            print(' %s' % terms[ind], end='')
        print()

    # print(km.labels_)

    results = dict()

    for i, game in enumerate(games):
        cluster_num = km.labels_[i]

        if cluster_num not in results:
            results[cluster_num] = []

        results[cluster_num].append(game[0])

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

