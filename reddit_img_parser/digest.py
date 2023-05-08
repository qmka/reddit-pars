from reddit_img_parser.reddit import get_reddit_entry
from reddit_img_parser.reddit import get_submissions
from reddit_img_parser.app import get_submission_attrs
from reddit_img_parser.app import parse
from reddit_img_parser.sql import init_db
from reddit_img_parser.sql import get_nodes
from reddit_img_parser.sql import set_status
from reddit_img_parser.sql import add_node
from reddit_img_parser.sql import connect_nodes
from reddit_img_parser.constants import STATUS_NEW
from reddit_img_parser.constants import STATUS_COMMON
from reddit_img_parser.constants import STATUS_FAVORITE
from reddit_img_parser.constants import TYPE_REDDITOR
from reddit_img_parser.constants import TYPE_SUBREDDIT
from reddit_img_parser.constants import ANSWER_YES


def digest_ui():
    menu_items = [
        'Seek new redditors from fav subreddits',
        'Seek new subreddits from fav redditors',
        'Seek new redditors from one subreddit',
        'Seek new subreddits from one redditor',
        'Update fav subreddit files',
        'Update fav redditor files',
        'Process new subreddits from database',
        'Process new redditors from database',
        'Add subreddit to database',
        'Add redditor to database'
    ]
    for i in range(len(menu_items)):
        print(f"{i + 1}. {menu_items[i]}")
    print('DB. Make empty database')
    print('0. Quit')

    ui_menu_choise = input('What to do? ')

    if ui_menu_choise == '0':
        raise SystemExit

    menu_functions = {
        '1': lambda: seek_favorites_for_new_instances(TYPE_SUBREDDIT),
        '2': lambda: seek_favorites_for_new_instances(TYPE_REDDITOR),
        '3': lambda: ask_to_seek_for_connected_instances(TYPE_SUBREDDIT),
        '4': lambda: ask_to_seek_for_connected_instances(TYPE_REDDITOR),
        '5': lambda: download_favorites(TYPE_SUBREDDIT),
        '6': lambda: download_favorites(TYPE_REDDITOR),
        '7': lambda: process_new_instances(TYPE_SUBREDDIT),
        '8': lambda: process_new_instances(TYPE_REDDITOR),
        '9': lambda: add_instance_ui(TYPE_SUBREDDIT),
        '10': lambda: add_instance_ui(TYPE_REDDITOR),
        'DD': lambda: make_empty_db()
    }

    if ui_menu_choise not in menu_functions:
        print('Type correct number!')
    else:
        menu_functions[ui_menu_choise]()

    digest_ui()


def make_empty_db():
    ui_make_new_db = input("Are you sure to make a new database? "
                           "It will destroy existing db!!!(y/n) ")
    if ui_make_new_db in ANSWER_YES:
        init_db()
        print('New database "reddit.db" is created.')
    digest_ui()


def download_favorites(instance_type):
    ui_download_favorite = input("Download updates for all favorities?(y/n) ")
    if ui_download_favorite in ANSWER_YES:
        ui_t_filter = input("Type time filter. "
                            "Recommend to use week or month. ")
        print(f"Downloading your favorities updates for last {ui_t_filter}...")
        favorites = get_favorites(instance_type)
        for instance in favorites:
            print(f"Downloading for {instance}")
            params = {
                'name': instance,
                'parse_type': instance_type,
                'category': 'top',
                'limit': 100,
                'time_filter': ui_t_filter
            }
            parse(**params)
        print('Done!')


def get_favorites(instance_type):
    if instance_type == TYPE_REDDITOR:
        instances = get_favorite_redditors()
    elif instance_type == TYPE_SUBREDDIT:
        instances = get_favorite_subreddits()
    return instances


def get_news(instance_type):
    if instance_type == TYPE_REDDITOR:
        instances = get_new_redditors()
    elif instance_type == TYPE_SUBREDDIT:
        instances = get_new_subreddits()
    return instances


def get_connected_instance_type(instance_type):
    if instance_type == TYPE_REDDITOR:
        connected_instance_type = TYPE_SUBREDDIT
    elif instance_type == TYPE_SUBREDDIT:
        connected_instance_type = TYPE_REDDITOR
    return connected_instance_type


def make_connected_instances(submissions, instance_type):
    connected_instances = []
    for sub in submissions:
        sub_attrs = get_submission_attrs(sub, instance_type)
        author = sub_attrs.get('author', None)
        posted_to = sub_attrs.get('posted_to', None)
        if author:
            connected_instances.append(author.name)
        elif posted_to:
            connected_instances.append(posted_to.display_name)
    return connected_instances


def ask_to_seek_for_connected_instances(instance_type):
    name_ui = input(f"Type {instance_type}'s name: ")
    print('Checking entry...')
    entry = get_reddit_entry(instance_type, name_ui)
    if not entry:
        print(f"{name_ui} seems not valid {instance_type}")
        return
    get_connected_instances(name_ui, instance_type, entry)


def get_connected_instances(instance, instance_type, entry):
    print(f"Processing {instance}")
    submissions_params = {
        'entry': entry,
        'parse_type': instance_type,
        'category': 'top',
        'limit': 20,
        'time_filter': 'week'
    }
    submissions = get_submissions(**submissions_params)
    connected_instances = make_connected_instances(
        submissions,
        instance_type
    )

    uniq_connected_instances = list(set(connected_instances))
    connected_instance_type = get_connected_instance_type(instance_type)
    process_connected_instances(uniq_connected_instances,
                                connected_instance_type)
    add_connections_to_db(instance, uniq_connected_instances)
    return uniq_connected_instances
    # print('Done!')


def seek_favorites_for_new_instances(instance_type):
    print('Prepare to process...')

    instances = get_favorites(instance_type)

    for instance in instances:
        entry = get_reddit_entry(instance_type, instance)
        get_connected_instances(instance, instance_type, entry)


def add_connections_to_db(basic_instance, connected_instances):
    for conn_instance in connected_instances:
        is_connected, message = connect_nodes(basic_instance, conn_instance)
        if is_connected:
            print(f"{basic_instance} connected to {conn_instance}")


def process_connected_instances(instances, connected_instance_type):
    there_are_connections = False
    for instance in instances:
        if connected_instance_type == TYPE_REDDITOR:
            is_added = add_redditor(instance, STATUS_NEW)
            there_are_connections = is_added
        elif connected_instance_type == TYPE_SUBREDDIT and \
                instance[:3] != 't5_' and \
                instance[:2] != 'u_':
            is_added = add_subreddit(instance, STATUS_NEW)
            there_are_connections = is_added
            print(is_added)
    if not there_are_connections:
        print(f"No new connected {connected_instance_type}s")


def process_new_instances(instance_type):
    new_instances = get_news(instance_type)
    if len(new_instances) == 0:
        print(f"There are no new {instance_type}s!")
        return
    for instance in new_instances:
        ask_to_download(instance, instance_type)
        ask_to_set_status(instance, instance_type)


def ask_to_download(instance, instance_type):
    ui_want_to_download = input(f"Качаем для {instance}? ")
    if ui_want_to_download in ANSWER_YES:
        params = {
            'name': instance,
            'parse_type': instance_type,
            'category': 'top',
            'limit': 20,
            'time_filter': 'month'
        }
        parse(**params)


def ask_to_set_status(instance, instance_type):
    ui_make_fav = input(f"Change status of {instance} to favorite? (y/n) ")
    if ui_make_fav in ANSWER_YES:
        status = STATUS_FAVORITE
    else:
        status = STATUS_COMMON
    is_status_changed, message = set_status(instance_type, instance, status)
    if is_status_changed:
        print(f"The status of {instance} is set to '{status}'!")
    else:
        print(message)


def add_redditor(name, status):
    is_added = add_node(TYPE_REDDITOR, name, status)
    if is_added:
        print(f"Redditor {name} successfully added "
              f"to database with '{status}' status.")
    return is_added


def add_subreddit(name, status):
    if name[:3] != 't5_' and name[:2] != 'u_':
        is_added = add_node(TYPE_SUBREDDIT, name, status)
        if is_added:
            print(f"Subreddit {name} successfully added "
                  f"to database with '{status}' status.")
            return True
    return False


def add_instance_ui(instance_type):
    name_ui = input(f"Type {instance_type}'s name: ")
    while True:
        status_ui = input("Type status: (n)ew, (f)avorite or (c)ommon: ")
        status = get_status_from_ui(status_ui)
        if status:
            break

    # Check validity
    print('Checking entry...')
    entry = get_reddit_entry(instance_type, name_ui)
    if not entry:
        return
    result = add_instance_by_type(instance_type, name_ui, status)
    if not result:
        print(f"{name_ui} is already in database")
    return


def add_instance_by_type(instance_type, name, status):
    if instance_type == TYPE_REDDITOR:
        result = add_redditor(name, status)
    elif instance_type == TYPE_SUBREDDIT:
        result = add_subreddit(name, status)
    return result


def get_status_from_ui(status_ui):
    statuses = {
        'n': STATUS_NEW,
        'f': STATUS_FAVORITE,
        'c': STATUS_COMMON
    }
    if status_ui in statuses:
        return statuses[status_ui]
    return None


def get_redditors():
    return get_nodes(TYPE_REDDITOR)


def get_subreddits():
    return get_nodes(TYPE_SUBREDDIT)


def get_favorite_subreddits():
    return get_nodes(TYPE_SUBREDDIT, status=STATUS_FAVORITE)


def get_favorite_redditors():
    return get_nodes(TYPE_REDDITOR, status=STATUS_FAVORITE)


def get_new_redditors():
    return get_nodes(TYPE_REDDITOR, status=STATUS_NEW)


def get_new_subreddits():
    return get_nodes(TYPE_SUBREDDIT, status=STATUS_NEW)
