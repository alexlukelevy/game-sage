# Game Sage
A machine learning, video game recommendation system.

### Overview
Game Sage works by reading in data from a PostgreSQL table, clustering the games using k-means and then writing the results out to Elasticsearch.


### Running
If you want to run Game Sage, you will have to setup a PostgreSQL instance, run the `table.sql` script and then load game data from the GiantBomb API (https://www.giantbomb.com/api/games).

Once you have the data, start up an Elasticsearch instance

```sh
sudo ./elasticsearch.sh
```

and then run `main.py`, supplying a PostgresSQL connection string

```
python main.py "host='localhost' dbname='db' user='user' password='password'"
```

### Results
You can view the results using the Game Sage [front-end](https://github.com/alexlukelevy/game-sage-web).
