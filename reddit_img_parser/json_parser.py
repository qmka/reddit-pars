import os
import requests

from fake_useragent import UserAgent

from reddit_img_parser.utils import log
from reddit_img_parser.settings import ROOT_FOLDER
from reddit_img_parser.app import get_file


def download_json(subreddit, tail):
    """Download JSON from subreddit list of posts."""
    user_agent = UserAgent()
    url = 'https://www.reddit.com/r/' + subreddit + '/' + tail
    headers = {'User-Agent': user_agent.chrome}
    timeout = 5
    log("Link to JSON: {url}", url=url)
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as err:
        log("Failed to download data: {err}", err=err)
    except requests.exceptions.RequestException as err:
        log("Error during request: {err}", err=err)


def get_pictures(parsed_data):

    entries = parsed_data['data']['children']
    pic_data = []

    for entry in entries:
        data = entry['data']
        pic_data.append({
            'title': data['title'],
            'name': data['name'],
            'url': data['url'],
            'upvote_ratio': data['upvote_ratio'],
            'ups': data['ups'],
            'author': data['author'],
            'permalink': data['permalink']
        })

    if parsed_data['data']['after'] is None:
        last_entry_name = ""
    else:
        last_entry_name = entries[-1]['data']['name']

    return pic_data, last_entry_name


def parser(subreddit, url_tail, first_page, last_page, folder):
    file_counter = 0
    suffix = ''
    # if not os.path.exists(folder):
    #    os.mkdir(folder)

    if not os.path.exists(ROOT_FOLDER):
        os.mkdir(ROOT_FOLDER)

    # Create a subfolder inside the folder
    folder = os.path.join(ROOT_FOLDER, folder)
    if not os.path.exists(folder):
        os.mkdir(folder)

    for i in range(last_page + 1):
        log('---------------------------------------------------')
        log("Trying to download pics json in range {i}", i=i)
        # 1. Загружаем json
        raw_data = download_json(subreddit, f"{url_tail}{suffix}")
        log('Success!')

        # 2. Парсим
        pictures, last_entry_name = get_pictures(raw_data)

        if i >= first_page:

            import json
            with open(f"test_json_range_{i}.json", 'w') as f:
                json.dump(raw_data, f)

            # 3. Обходим все картинки
            for pic in pictures:
                log('---------------------------------------------------')

                file_counter += 1
                url = pic['url']
                title = pic['title']
                author = pic['author']

                # log("{file_counter}. POST: {permalink}", file_counter=file_counter, permalink=permalink)
                log('{file_counter}. {title}', file_counter=file_counter, title=title)
                log('AUTHOR: {author}', author=author)
                log('URL: {url}', url=url)

                get_file(url, folder)

        # Готовимся к следующему уровню погружения
        if last_entry_name == "":
            return

        if url_tail.find("?") == -1:
            suffix = f"?after={last_entry_name}"
        else:
            suffix = f"&after={last_entry_name}"


###
# It's old and slow version using /.json parsing instead of api
###
'''


def parse_subreddit_json(subreddit):

    print("Welcome to Reddit Pictures Parser!")
    print(f"Preparing to parse: {subreddit}")
    print("What do you want to download? Enter a number")

    menu_items = [
        "1 - Hot",
        "2 - New",
        "3 - Rising",
        "4 - Top of the day",
        "5 - Top of the week",
        "6 - Top of the month",
        "7 - Top of the year",
        "8 - Top of all time"
    ]
    for menu_item in menu_items:
        print(menu_item)
    posts_type = int(input())

    if posts_type == 1:
        url_tail = 'hot/.json'
        folder = subreddit + '_hot'
    if posts_type == 2:
        url_tail = 'new/.json'
        folder = subreddit + '_new'
    if posts_type == 3:
        url_tail = 'rising/.json'
        folder = subreddit + '_rising'
    if posts_type == 4:
        url_tail = 'top/.json?t=day'
        folder = subreddit + '_top_day'
    if posts_type == 5:
        url_tail = 'top/.json?t=week'
        folder = subreddit + '_top_week'
    if posts_type == 6:
        url_tail = 'top/.json?t=month'
        folder = subreddit + '_top_month'
    if posts_type == 7:
        url_tail = 'top/.json?t=year'
        folder = subreddit + '_top_year'
    if posts_type == 8:
        url_tail = 'top/.json?t=all'
        folder = subreddit + '_top_all'

    print("One page contains 25 posts. We can parse 40 pages in range from 0 to 39")
    first_page = int(input("Select starting page of subreddit (first page is 0): "))
    last_page = int(input("Select last page of subreddit (not more than 39): "))

    parser(subreddit, url_tail, first_page, last_page, folder)

    log('Parsing completed!')
'''
