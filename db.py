class Game:
    def __init__(self, name, **kwargs):
        self.name = name
        self.properties = kwargs


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
