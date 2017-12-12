from elasticsearch import Elasticsearch

index = 'games'
es = Elasticsearch(http_auth=('elastic', 'changeme'),)


def reset():
    es.indices.delete(index, ignore=[404])
    es.indices.create(index)


def store(clusters):
    for cluster in clusters:
        for game in cluster:
            doc = {
                'name': game.name,
                'similar': [{'name': g.name, 'icon': g.properties["icon"]} for g in cluster if g.name != game.name],
                'icon': game.properties["icon"]
            }

            es.index(index=index, doc_type='game', body=doc)

    es.indices.refresh(index=index)
