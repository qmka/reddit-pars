import praw
import prawcore.exceptions
import os

from dotenv import load_dotenv

from reddit_img_parser.utils import log


'''
def is_valid_reddit_instance(instance, type):
    if type == 'subreddit':
        try:
            instance.id
            return True
        except prawcore.exceptions.Redirect:
            return False
        except prawcore.exceptions.NotFound:
            return False
    elif type == 'redditor':
        try:
            instance.name
            return True
        except prawcore.exceptions.NotFound:
            return False
        except prawcore.exceptions.Forbidden:
            return False
    else:
        raise ValueError("Invalid object type. Must be either 'redditor' or 'subreddit'.")
'''


def is_valid_reddit_instance(instance, obj_type):
    try:
        if obj_type == 'subreddit':
            instance.id
        elif obj_type == 'redditor':
            instance.name
        else:
            raise ValueError("Invalid object type. Must be either 'redditor' or 'subreddit'.")
        return True
    except (prawcore.exceptions.Redirect, prawcore.exceptions.NotFound, prawcore.exceptions.Forbidden):
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

'''
def get_submissions(entry, type, category, limit, time_filter):
    if category == 'hot':
        submissions = entry.hot(limit=limit)
    elif category == 'new':
        submissions = entry.new(limit=limit)
    elif category == 'rising':
        if type == 'redditor':
            log("'Rising' category doesn't exists for redditors, try different!")
            submissions = None
        else:
            submissions = entry.rising(limit=limit)
    else:
        submissions = entry.top(limit=limit, time_filter=time_filter)
    return submissions

def get_submissions_old(entry, type, category, limit, time_filter):
    if category == 'rising' and type == 'redditor':
        log("'Rising' category doesn't exists for redditors, try different!")
        return None
    elif category == 'rising':
        submissions = entry.rising(limit=limit)
    elif category == 'hot':
        submissions = entry.hot(limit=limit)
    elif category == 'new':
        submissions = entry.new(limit=limit)
    else:
        submissions = entry.top(limit=limit, time_filter=time_filter)
    return submissions
'''
def get_submissions(entry, type, category, limit, time_filter):
    match category:
        case 'rising':
            if type == 'redditor':
                log("'Rising' category doesn't exists for redditors, try different!")
                return None
            else:
                submissions = entry.rising(limit=limit)
        case 'hot':
            submissions = entry.hot(limit=limit)
        case 'new':
            submissions = entry.new(limit=limit)
        case 'top':
            submissions = entry.top(limit=limit, time_filter=time_filter)
    return submissions
