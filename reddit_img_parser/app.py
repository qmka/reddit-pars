import requests
import os
from progress.bar import Bar
from fake_useragent import UserAgent


def download_json(subreddit, tail):
    """Download JSON from subreddit list of posts."""
    user_agent = UserAgent()
    url = 'https://www.reddit.com/r/' + subreddit + '/' + tail
    headers = {'User-Agent': user_agent.chrome}
    timeout = 5

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as err:
        print("Failed to download data:", err)
    except requests.exceptions.RequestException as err:
        print("Error during request:", err)


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
            'ups': data['ups']
        })

    last_entry_name = entries[-1]['data']['name']

    return pic_data, last_entry_name


def save_pictures(pic_urls, folder):

    user_agent = UserAgent()

    if not os.path.exists(folder):
        os.makedirs(folder)

    for url in pic_urls:
        filename = os.path.basename(url)
        filename_without_ex = os.path.splitext(filename)[0]
        file_extension = os.path.splitext(filename)[1]
        if not file_extension:
            print(f"{filename} does not have an extension, skipping")
            continue

        # gifv to mp4
        if file_extension == ".gifv":
            filename = f"{filename_without_ex}.mp4"
            url = f"https://i.imgur.com/{filename}"

        filepath = os.path.join(folder, filename)

        if os.path.isfile(filepath):
            print(f"{filename} already in this folder, skipping")
            continue

        try:
            headers = {'User-Agent': user_agent.chrome}
            timeout = 5
            response = requests.get(
                url,
                headers=headers,
                timeout=timeout,
                stream=True)

            if response.status_code == 200:
                total_length = int(response.headers.get("Content-Length", 0))
                block_size = 1024
                written = 0
                bar = Bar('Downloading', max=None, suffix='%(percent)d%%')
                with open(filepath, "wb") as f:
                    for data in response.iter_content(block_size):
                        written = written + len(data)
                        f.write(data)
                        if bar.max is None:
                            bar.max = max(written, total_length)
                        bar.next(len(data))
                bar.finish()

                print(f"{filename} saved")
            else:
                print(f"{filename} could not be downloaded")
        except requests.exceptions.RequestException as e:
            print(f"Error while downloading {filename}: {e}")


def parser(subreddit, url_tail, depth, folder):
    suffix = ''

    for i in range(depth):
        print(f"Range {i}")
        # 1. Загружаем json
        raw_data = download_json(subreddit, f"{url_tail}{suffix}")

        # 2. Парсим
        links = []
        pictures, last_entry_name = get_pictures(raw_data)

        # 2.5 Делаем суффикс в зависимости от глубины
        if url_tail.find("?") == -1:
            suffix = f"?after={last_entry_name}"
        else:
            suffix = f"&after={last_entry_name}"

        for pic in pictures:
            links.append(pic['url'])

        # 3. Сохраняем на диск
        save_pictures(links, folder)


def ui():
    print("Welcome to Reddit Pictures Parser!")
    subreddit = input("Enter the name of the subreddit you want to scrape: ")
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

    depth = int(input("Select depth of subreddit (not more than 40): "))

    parser(subreddit, url_tail, depth, folder)

    print('Parsing completed!')
