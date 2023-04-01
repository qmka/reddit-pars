# -*- coding:utf-8 -*-
import argparse
from reddit_img_parser.app import parse, batch_parse
from reddit_img_parser.statistics import get_statistics


def parse_args():
    app_desc = "Parses Reddit's subreddits or redditors and extracts media"
    categories = ['hot', 'new', 'rising', 'top']
    time_filters = ['hour', 'day', 'week', 'month', 'year', 'all']

    parser = argparse.ArgumentParser(description=app_desc)
    parser.add_argument('name')
    parser.add_argument('-s', '--statistics',
                        action='store_true', required=False)
    parser.add_argument('-b', '--batch', action='store_true', required=False)
    parser.add_argument('-r', '--subreddit',
                        action='store_true', required=False)
    parser.add_argument('-u', '--user', action='store_true', required=False)
    parser.add_argument('-c', '--category', help='set category of posts',
                        default='new', choices=categories, required=False)
    parser.add_argument('-t', '--time', help='set time filter of posts',
                        default='day', choices=time_filters, required=False)
    parser.add_argument('-l', '--limit', default='10', required=False)

    return parser.parse_args()


def main():
    args = parse_args()

    if not args.user and not args.subreddit:
        print('use one of the flags: -u USERNAME or -s SUBREDDIT')
        return

    parse_type = 'subreddit' if args.subreddit else 'redditor'
    limit = int(args.limit)

    params = {
        'name': args.name,
        'parse_type': parse_type,
        'category': args.category,
        'limit': limit,
        'time_filter': args.time
    }

    if args.batch:
        batch_parse(**params)
        return
    if args.statistics:
        get_statistics(**params)
        return
    parse(**params)


if __name__ == '__main__':
    main()
