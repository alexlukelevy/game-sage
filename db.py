class Game:
    def __init__(self, name, **kwargs):
        self.name = name
        self.properties = kwargs


def get_name(data):
    return data['name']


def get_property(data, prop):
    try:
        values = map(lambda g: g['name'], data[prop])
        return ','.join(values)
    except (KeyError, TypeError):
        return ''


def get_genres(data):
    return get_property(data, 'genres')


def get_themes(data):
    return get_property(data, 'themes')


def get_concepts(data):
    return get_property(data, 'concepts')


def get_locations(data):
    return get_property(data, 'locations')


def get_developers(data):
    return get_property(data, 'developers')


def get_platforms(data):
    return get_property(data, 'platforms')


def get_icon(data):
    return data["image"]["icon_url"]


def get_game(data):
    return Game(
        get_name(data),
        genres=get_genres(data),
        themes=get_themes(data),
        concepts=get_concepts(data),
        locations=get_locations(data),
        developers=get_developers(data),
        platforms=get_platforms(data),
        icon=get_icon(data)
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
'''
    curr.execute(sql)
    data = map(lambda row: row[0], curr.fetchall())

    return list(map(get_game, data))
