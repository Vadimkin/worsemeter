import logging
from typing import Optional

import tweepy

import config
import models

logger = logging.getLogger(__name__)


def max_tweet_id() -> Optional[str]:
    tweet = (
        models.Tweet.select(models.Tweet.tweet_id)
        .order_by(models.Tweet.tweet_id.desc())
        .limit(1)
    )

    if not tweet:
        return None

    return tweet[0].tweet_id


def process_tweet(tweet: tweepy.Tweet):
    tweet_id_str = str(tweet.id)
    logger.info("Processing tweet %s...", tweet_id_str)

    is_exist = (
        models.Tweet.select().where(models.Tweet.tweet_id == tweet_id_str).count() == 1
    )
    if is_exist:
        return

    # It's possible to have them both as true
    is_worse = "гірше" in tweet.text
    is_better = "краще" in tweet.text

    models.Tweet.create(
        tweet_id=tweet_id_str,
        text=tweet.text,
        author_id=str(tweet.author_id),
        created_at=tweet.created_at,
        is_worse=is_worse,
        is_better=is_better,
    )


def process_initial_tweets(client):
    print("Processing initial data...")
    # parse latest 500 results
    max_tweet_id = None
    for i in range(5):
        response = process_tweets(client, until_id=max_tweet_id)
        if not response.data:
            break

        last_tweet = response.data[-1]
        max_tweet_id = str(last_tweet.id)


def process_tweets(
    client, since_id: Optional[str] = None, until_id: Optional[str] = None
):
    response = client.search_recent_tweets(
        '("стало гірше") OR ("стало краще")',
        user_auth=True,
        tweet_fields=["created_at"],
        since_id=since_id,
        until_id=until_id,
        max_results=100,
    )

    if response.data:
        for tweet in response.data:
            process_tweet(tweet)
    else:
        logger.info("Nothing to process since id %s...", max_tweet_id)

    return response


def process():
    max_id = max_tweet_id()

    client = tweepy.Client(
        consumer_key=config.TWITTER_APP_API_KEY,
        consumer_secret=config.TWITTER_APP_API_SECRET,
        access_token=config.TWITTER_USER_ACCESS_TOKEN,
        access_token_secret=config.TWITTER_USER_SECRET,
    )

    if not max_id:
        process_initial_tweets(client)
    else:
        process_tweets(client, max_id)
