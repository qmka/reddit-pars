# -*- coding:utf-8 -*-
import argparse
from reddit_img_parser.app import parse


def main():
    app_desc = "Parses Reddit's subreddits or users and extracts media"
    categories = ['hot', 'new', 'rising', 'top']
    time_filters = ['hour', 'day', 'week', 'month', 'year', 'all']

    p = argparse.ArgumentParser(description=app_desc)
    p.add_argument('-s', '--subreddit')
    p.add_argument('-u', '--user')
    p.add_argument('-c', '--category', help='set category of posts',
                   default='new', choices=categories)
    p.add_argument('-t', '--time', help='set time filter of posts',
                   default='day', choices=time_filters)
    p.add_argument('limit')
    args = p.parse_args()

    if (not args.user and not args.subreddit) or (args.user and args.subreddit):
        print('use one of the flags: -u USERNAME or -s SUBREDDIT')
    elif args.subreddit:
        parse('subreddit', args.subreddit, args.category, args.time, int(args.limit))
    elif args.user:
        parse('redditor', args.user, args.category, args.time, int(args.limit))


if __name__ == '__main__':
    main()
