# -*- coding:utf-8 -*-
import argparse
from reddit_img_parser.app import ui


def main():
    app_desc = "Parses Reddit's subreddits or users and extracts media"
    p = argparse.ArgumentParser(description=app_desc)
    p.add_argument('-s', '--subreddit')
    p.add_argument('-u', '--user')
    args = p.parse_args()

    if (not args.user and not args.subreddit) or (args.user and args.subreddit):
        print('use one of the flags: -u USERNAME or -s SUBREDDIT')
    elif args.subreddit:
        ui(args.subreddit)
    elif args.user:
        print("User's parse will be rovided in next app versions")

if __name__ == '__main__':
    main()
