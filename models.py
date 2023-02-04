from peewee import *

import config

db = SqliteDatabase(config.BASE_PATH / "database.db")


class Tweet(Model):
    tweet_id = CharField(max_length=128)
    text = CharField(max_length=512)
    author_id = CharField(max_length=128)
    created_at = DateTimeField()

    is_worse = BooleanField(default=False)
    is_better = BooleanField(default=False)

    class Meta:
        database = db
