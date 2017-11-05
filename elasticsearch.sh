#!/usr/bin/env bash

sudo docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" -v `pwd`/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml docker.elastic.co/elasticsearch/elasticsearch:5.6.3
