import datetime
import json

import config
from models import Tweet


def get_stat_until(datetime_until) -> tuple[int, int]:
    hour_from = datetime_until - datetime.timedelta(hours=18)
    tweets = Tweet.select().where(
        (Tweet.created_at > hour_from)
        & (Tweet.created_at < datetime_until)
        & (
            (Tweet.is_better == True & Tweet.is_worse == False)
            | (Tweet.is_worse == True & Tweet.is_better == False)
        )
    )

    is_worse, is_better = 0, 0

    # TODO Optimize it into sql query someday
    for tweet in tweets:
        if tweet.is_worse:
            is_worse += 1
        if tweet.is_better:
            is_better += 1
    return is_worse, is_better


def export():
    current_time = datetime.datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    analytics_by_date = {}

    for i in range(24):
        previous_hour = current_time - datetime.timedelta(hours=i)
        is_worse, is_better = get_stat_until(previous_hour)

        count = is_worse + is_better

        worse_percentage = round(is_worse * 100 / count)
        better_percentage = round(is_better * 100 / count)

        hour_str = previous_hour.isoformat()
        analytics_by_date[hour_str] = (worse_percentage, better_percentage)

    with open(config.ANALYTICS_FILE, "w") as analytics_file:
        analytics_file.write(json.dumps(analytics_by_date))


if __name__ == "__main__":
    export()