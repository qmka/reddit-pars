import praw
import os

from dotenv import load_dotenv
from progress.spinner import Spinner


class DotSpinner(Spinner):
    phases = [' ', '...']


def make_reddit_instance():
    load_dotenv()
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    USER_AGENT = os.getenv('USER_AGENT')

    return praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT)

def get_posters_list(subreddit_name, category, time_filter, limit):
    
    print('Connecting to Reddit... ', end='')
    reddit = make_reddit_instance()
    entry = reddit.subreddit(subreddit_name)
    print('Success!')

    if category == 'hot':
        submissions = entry.hot(limit=limit)
    elif category == 'new':
        submissions = entry.new(limit=limit)
    elif category == 'rising':
        submissions = entry.rising(limit=limit)
    else:
        submissions = entry.top(limit=limit, time_filter=time_filter)
    
    posters = {}

    print('Processing posts... ')
    
    for sub in submissions:

        sub_author = sub.author
        if not sub_author:
            continue

        author_name = sub_author.name
        if not author_name in posters:
            posters[author_name] = 1
        else:
            posters[author_name] += 1

    print(f"Result: redditors that posted to {subreddit_name} more than 2 times")
    print((51 + len(subreddit_name)) * '-')
    sorted_posters = dict(sorted(posters.items(), key=lambda item: item[1]))
    for user in sorted_posters: 
        count = sorted_posters[user]
        if count > 2:
            print(f"{user}: {count}")
