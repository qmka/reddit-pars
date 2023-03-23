from reddit_img_parser.utils import log, make_folder, convert_unix_time
from reddit_img_parser.download import get_file
from reddit_img_parser.reddit import get_reddit_entry, get_submissions


def get_submission_attrs(sub, type):
    if type == 'subreddit':
        return {
            'title': sub.title,
            'author': sub.author,
            'url': sub.url,
            'posted_to': None
        }
    elif type == 'redditor':
        attrs = vars(sub)
        return {
            'title': attrs.get('link_title') or attrs.get('title'),
            'author': None,
            'url': attrs.get('link_url') or attrs.get('url'),
            'posted_to': sub.subreddit
        }


def parse_submissions(submissions, type, path):
    for i, sub in enumerate(submissions):
        sub_attrs = get_submission_attrs(sub, type)
        title = sub_attrs.get('title', None)
        author = sub_attrs.get('author', None)
        url = sub_attrs.get('url', None)
        posted_to = sub_attrs.get('posted_to', None)
        sub_created = convert_unix_time(sub.created)

        print('------------------------------------')
        log('#{counter}', counter=i + 1)
        log('TITLE: {title}', title=title)
        log('CREATED AT: {sub_created}', sub_created=sub_created)
        log('URL: {url}', url=url)

        if type == 'subreddit':
            log('AUTHOR: {author}', author=author)
        elif type == 'redditor':
            log('POSTED TO: {posted_to}', posted_to=posted_to)

        get_file(url, path)


def parse(**params):
    type = params.get('parse_type', None)
    name = params.get('name', None)
    category = params.get('category', None)
    time_filter = params.get('time_filter', None)
    limit = params.get('limit', None)

    entry = get_reddit_entry(type, name)
    if not entry:
        return

    path = make_folder(name, category, time_filter)

    try:
        created = convert_unix_time(entry.created_utc)
    except Exception as e:
        log("Incorrect Reddit entry {name} "
            "(doesn't exists, suspended or something else).",
            name=name)
        log("{e}", e=e)
        return

    submissions_params = {
        'entry': entry,
        'parse_type': type,
        'category': category,
        'limit': limit,
        'time_filter': time_filter
    }

    submissions = get_submissions(**submissions_params)
    if not submissions:
        return

    log("Name of {type}: {name}", type=type, name=name)
    log("Account created: {created}", created=created)
    log("Processing...")

    parse_submissions(submissions, type, path)
    log('Parsing completed!')


def batch_parse(**params):
    type = params.get('parse_type', None)
    filename = params.get('name', None)
    category = params.get('category', None)
    time_filter = params.get('time_filter', None)
    limit = params.get('limit', None)

    print('Preparing to batch parse...')

    try:
        with open(filename, "r") as f:
            entries = f.read().splitlines()
    except Exception as e:
        print(e)
        print("Can't read the batch file!")
        return

    for entry_name in entries:
        entry_params = {
            'name': entry_name,
            'parse_type': type,
            'category': category,
            'limit': limit,
            'time_filter': time_filter
        }

        parse(**entry_params)
        print('------------------------------------')
        print('------------------------------------')

    log('Batch parsing completed!')
