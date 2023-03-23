from functools import reduce
from reddit_img_parser.reddit import get_reddit_entry, get_submissions


def get_key_entry(sub, type):
    return sub.subreddit if type == 'redditor' else sub.author


def get_key_name(key_entry, type):
    return key_entry.display_name if type == 'redditor' else key_entry.name


def get_statistics(**params):
    type = params.get('parse_type', None)
    name = params.get('name', None)

    entry = get_reddit_entry(type, name)
    if not entry:
        return

    submissions_params = {
        'entry': entry,
        'parse_type': type,
        'category': params.get('category', None),
        'limit': params.get('limit', None),
        'time_filter': params.get('time_filter', None)
    }

    submissions = get_submissions(**submissions_params)

    if not submissions:
        return
    print('Processing... ')
    stat_data = reduce(
        lambda sd, sub: add_to_statistics_data(sd, sub, type),
        submissions,
        {}
    )

    print(f"Statistics to: {name}")
    print((21 + len(name)) * '-')
    sorted_data = dict(sorted(stat_data.items(), key=lambda item: -item[1]))
    list(map(lambda el: print(f"{el}: {sorted_data[el]}"), sorted_data))


def add_to_statistics_data(statistics_data, sub, type):
    key_entry = get_key_entry(sub, type)
    if not key_entry:
        return statistics_data
    key_name = get_key_name(key_entry, type)
    if key_name not in statistics_data:
        statistics_data[key_name] = 1
    else:
        statistics_data[key_name] += 1
    return statistics_data
