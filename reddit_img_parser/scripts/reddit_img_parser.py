# -*- coding:utf-8 -*-
import argparse
from reddit_img_parser.app import parse, batch_parse
from reddit_img_parser.statistics import get_statistics


def main():
    app_desc = "Parses Reddit's subreddits or redditors and extracts media"
    categories = ['hot', 'new', 'rising', 'top']
    time_filters = ['hour', 'day', 'week', 'month', 'year', 'all']

    p = argparse.ArgumentParser(description=app_desc)
    p.add_argument('name')
    p.add_argument('-a', '--statistics', action='store_true', required=False)
    p.add_argument('-b', '--batch', action='store_true', required=False)
    p.add_argument('-s', '--subreddit', action='store_true', required=False)
    p.add_argument('-u', '--user', action='store_true', required=False)
    p.add_argument('-c', '--category', help='set category of posts',
                   default='new', choices=categories, required=False)
    p.add_argument('-t', '--time', help='set time filter of posts',
                   default='day', choices=time_filters, required=False)
    p.add_argument('-l', '--limit', default='10', required=False)
    args = p.parse_args()
    if args.batch:
        if args.subreddit:
            batch_parse('subreddit', args.name, args.category, args.time, int(args.limit))
        elif args.user:
            batch_parse('redditor', args.name, args.category, args.time, int(args.limit))
    elif (not args.user and not args.subreddit) or (args.user and args.subreddit):
        print('use one of the flags: -u USERNAME or -s SUBREDDIT')
    elif args.statistics:
        if args.subreddit:
            get_statistics('subreddit', args.name, args.category, args.time, int(args.limit))
        else:
            get_statistics('redditor', args.name, args.category, args.time, int(args.limit))
    elif args.subreddit:
        parse('subreddit', args.name, args.category, args.time, int(args.limit))
    elif args.user:
        parse('redditor', args.name, args.category, args.time, int(args.limit))


if __name__ == '__main__':
    main()
