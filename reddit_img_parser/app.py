from reddit_img_parser.utils import log, make_folder, convert_unix_time
from reddit_img_parser.download import get_file
from reddit_img_parser.reddit import get_reddit_entry, get_submissions


def parse(type, name, category, time_filter, limit):
    
    entry = get_reddit_entry(type, name)
    if not entry:
        return

    path = make_folder(name, category, time_filter)

    counter = 0

    try:
        created = convert_unix_time(entry.created_utc)
    except:
        log("Incorrect Reddit entry {name} (doesn't exists, suspended or something else).", name=name)
        return

    submissions = get_submissions(entry, type, category, limit, time_filter)
    if not submissions:
        return

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


def batch_parse(type, filename, category, time_filter, limit):
    print('Preparing to batch parse...')
    # 1. Читаем из файла в список
    # 2. Для каждого из списка вызываем parse
    try:
        with open(filename, "r") as f:
            entries = f.read().splitlines()
    except:
        print("Batch file doesn't exists!")
        return

    # Print the list of usernames
    for entry_name in entries:

        parse(type, entry_name, category, time_filter, limit)
        print('------------------------------------')
        print('------------------------------------')

    log('Batch parsing completed!')
