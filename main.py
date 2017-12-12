import psycopg2
import sys

import db
import es
import recommender

# e.g. "host='localhost' dbname='giantbomb' user='user' password='password'"
conn = psycopg2.connect(sys.argv[1])
curr = conn.cursor()

games = db.get_games(curr)
clusters = recommender.cluster(games, 200)

curr.close()
conn.close()

es.reset()
es.store(clusters)