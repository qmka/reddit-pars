from reddit_img_parser.reddit import get_reddit_entry, get_submissions
from reddit_img_parser.app import get_submission_attrs, parse
from reddit_img_parser.sql import get_nodes, set_status, add_node
from reddit_img_parser.constants import STATUS_NEW, STATUS_COMMON, STATUS_FAVORITE
from reddit_img_parser.constants import TYPE_REDDITOR, TYPE_SUBREDDIT
from reddit_img_parser.constants import ANSWER_YES


def digest_ui():
    print('1. Seek new redditors from fav subreddits')
    print('2. Seek new subreddits from fav redditors')
    print('3. Update fav subreddit files')
    print('4. Update fav redditor files')
    print('5. Process new subreddits from database')
    print('6. Process new redditors from database')
    print('7. Add subreddit to database')
    print('8. Add redditor to database')
    print('0. Quit')

    ui_menu_choise = input('What to do? ')

    if ui_menu_choise == '0':
        raise SystemExit

    menu_functions = {
        '1': lambda: seek_for_new_instances(TYPE_SUBREDDIT),
        '2': lambda: seek_for_new_instances(TYPE_REDDITOR),
        '3': lambda: download_favorites(TYPE_SUBREDDIT),
        '4': lambda: download_favorites(TYPE_REDDITOR),
        '5': lambda: process_new_instances(TYPE_SUBREDDIT),
        '6': lambda: process_new_instances(TYPE_REDDITOR),
        '7': lambda: add_instance_ui(TYPE_SUBREDDIT),
        '8': lambda: add_instance_ui(TYPE_REDDITOR)
    }

    if ui_menu_choise not in menu_functions:
        print('Type correct number!')
    else:
        menu_functions[ui_menu_choise]()

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


def seek_for_new_instances(instance_type):
    print('Prepare to process...')

    instances = get_favorites(instance_type)
    connected_instance_type = get_connected_instance_type(instance_type)

    for instance in instances:
        print(f"Processing {instance}")
        entry = get_reddit_entry(instance_type, instance)
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
        for instance in uniq_connected_instances:
            if connected_instance_type == TYPE_REDDITOR:
                add_redditor(instance, STATUS_NEW)
            elif connected_instance_type == TYPE_SUBREDDIT and instance[:3] != 't5_' and instance[:2] != 'u_':
                add_subreddit(instance, STATUS_NEW)
        print('Done!')


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
     
    if instance_type == TYPE_REDDITOR:
        result = add_redditor(name_ui, status)
    elif instance_type == TYPE_SUBREDDIT:
        result = add_subreddit(name_ui, status)
    
    if not result:
        print(f"{name_ui} is already in database")
    
    return


def get_status_from_ui(status_ui):
    statuses = {
        'n': STATUS_NEW,
        'f': STATUS_FAVORITE,
        'c': STATUS_COMMON
    }
    if status_ui in statuses:
        return statuses[status_ui]
    return None


def add_subreddit(name, status):
    if name[:3] != 't5_' and name[:2] != 'u_':
        is_added = add_node(TYPE_SUBREDDIT, name, status)
        if is_added:
            print(f"Subreddit {name} successfully added "
                f"to database with '{status}' status.")
        return True
    return False


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
