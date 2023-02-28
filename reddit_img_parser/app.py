import praw
import prawcore.exceptions
import os

from dotenv import load_dotenv

from reddit_img_parser.utils import log, make_folder, convert_unix_time
from reddit_img_parser.download import get_file


def is_valid_reddit_instance(instance):
    try:
        instance.id
        return True
    except prawcore.exceptions.Redirect:
        return False
    except prawcore.exceptions.NotFound:
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


def parse(type, name, category, time_filter, limit):
    reddit = make_reddit_instance()

    if type == 'redditor':
        entry = reddit.redditor(name)
    elif type == 'subreddit':
        entry = reddit.subreddit(name)

    if not is_valid_reddit_instance(entry):
        print(f"Invalid {type} name, try again!")
        return

    path = make_folder(name, category, time_filter)

    counter = 0

    created = convert_unix_time(entry.created_utc)

    # Make submissions list
    if category == 'hot':
        submissions = entry.hot(limit=limit)
    elif category == 'new':
        submissions = entry.new(limit=limit)
    elif category == 'rising':
        if type == 'redditor':
            log("'Rising' category doesn't exists for redditors, try different!")
            return
        else:
            submissions = entry.rising(limit=limit)
    else:
        submissions = entry.top(limit=limit, time_filter=time_filter)

    # Show info
    log("Name of {type}: {name}", type=type, name=name)
    log("Account created: {created}", created=created)

    # Parse each submission
    for sub in submissions:

        if type == 'subreddit':
            title = sub.title
            author = sub.author
            url = sub.url
        elif type == 'redditor':
            submission_attrs = (vars(sub))
            posted_to = sub.subreddit

            '''
            # Print out all attribute names and their values

            sorted_tuple = dict(sorted(submission_attrs.items(), key=lambda x: x[0]))
            for attr_name in sorted_tuple:
                if counter == 3:
                    print(f"{attr_name}: {sorted_tuple[attr_name]}")
            '''

            if 'link_title' in submission_attrs:
                title = sub.link_title
                url = sub.link_url
            elif 'title' in submission_attrs:
                title = sub.title
                url = sub.url

        counter += 1
        sub_created = convert_unix_time(sub.created)
        print('------------------------------------')
        log('#{counter}', counter=counter)
        log('TITLE: {title}', title=title)
        log('CREATED AT: {sub_created}', sub_created=sub_created)
        log('URL: {url}', url=url)

        if type == 'subreddit':
            log('AUTHOR: {author}', author=author)
        elif type == 'redditor':
            log('POSTED TO: {posted_to}', posted_to=posted_to)

        # Get file
        get_file(url, path)

    log('Parsing completed!')
