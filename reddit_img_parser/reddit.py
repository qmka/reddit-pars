import praw
import prawcore.exceptions
import os

from dotenv import load_dotenv

from reddit_img_parser.utils import log


def is_valid_reddit_instance(instance, obj_type):
    try:
        if obj_type == 'subreddit':
            instance.id
        elif obj_type == 'redditor':
            instance.name
        else:
            raise ValueError("Invalid object type. "
                             "Must be either 'redditor' or 'subreddit'.")
        return True
    except (prawcore.exceptions.Redirect,
            prawcore.exceptions.NotFound,
            prawcore.exceptions.Forbidden):
        return False


def make_reddit_instance():
    load_dotenv()
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    USER_AGENT = os.getenv('USER_AGENT')

    return praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT)


def get_reddit_entry(type, name):
    reddit = make_reddit_instance()
    if type == 'redditor':
        entry = reddit.redditor(name)
    elif type == 'subreddit':
        entry = reddit.subreddit(name)
    if not is_valid_reddit_instance(entry, type):
        print(f"Invalid {type} name, try again!")
        return None
    else:
        return entry


def get_submissions(**submission_params):
    # entry, type, category, limit, time_filter
    parse_type = submission_params.get('parse_type', None)
    entry = submission_params.get('entry', None)
    category = submission_params.get('category', None)
    time_filter = submission_params.get('time_filter', None)
    limit = submission_params.get('limit', None)

    categories = {
        'rising': lambda: get_rising_subs(entry, parse_type, limit),
        'hot': lambda: entry.hot(limit=limit),
        'new': lambda: entry.new(limit=limit),
        'top': lambda: entry.top(limit=limit, time_filter=time_filter)
    }

    submissions = categories[category]()

    return submissions


def get_rising_subs(entry, parse_type, limit):
    if parse_type == 'redditor':
        print("'Rising' category doesn't exists "
                "for redditors, try different!")
        return None
    else:
        return entry.rising(limit=limit)

