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
                'name': game,
                'similar': [g for g in cluster if g != game],
            }

            es.index(index=index, doc_type='game', body=doc)

    es.indices.refresh(index=index)