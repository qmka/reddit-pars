import requests
import os
from progress.bar import Bar
from fake_useragent import UserAgent
from reddit_img_parser.rg import is_rg, get_rg_id, download_rg


def is_imgur_no_ex(file):
    return file.find("https://s.imgur.com")


def remove_query_string(filename):
    name, extension = os.path.splitext(filename)
    if extension:
        extension_without_query = extension.split("?")[0]
    else:
        extension_without_query = ""
    return name + extension_without_query


def download_json(subreddit, tail):
    """Download JSON from subreddit list of posts."""
    user_agent = UserAgent()
    url = 'https://www.reddit.com/r/' + subreddit + '/' + tail
    headers = {'User-Agent': user_agent.chrome}
    timeout = 5
    print(f"Link to JSON: {url}")
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


def download_by_direct_link(url, folder):
    # возвращает статус скачивания
    user_agent = UserAgent()
    filename = os.path.basename(url)
    filepath = os.path.join(folder, filename)

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
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Error while downloading {filename}: {e}")


def get_file(url, folder, counter):
    rg_id = ''
    readed_data = ''
    type = ''

    filename = remove_query_string(os.path.basename(url))
    filename_without_ex = os.path.splitext(filename)[0]
    file_extension = os.path.splitext(filename)[1]
    print('---------------------------------------------------')
    print(f"{counter}. Trying to download file: {filename}")

    common_extensions = ['.jpg', '.gif', '.jpeg', '.mp4', '.png']

    # 3. Определяем тип файла
    if file_extension in common_extensions:
        type = 'common'
    elif file_extension == '.gifv':
        type = 'gifv'
    else:
        # это папка???
        if url[-1] == '/':
            print("It's a folder, passing")
            return

        # rg? imgur no ex?
        # качаем
        print('For this type of file we need to download additional info')
        # print(f"URL is {url} ... folder is {folder}")
        status = download_by_direct_link(url, folder)
        if status != 200:
            print(f"{filename} could not be downloaded. Response status code is {status}")
            return
        else:
            # если скачали, то загружаем и парсим
            filepath = os.path.join(folder, filename)
            with open(filepath, 'r') as f:
                readed_data = f.read()
            os.remove(filepath)
            if is_rg(readed_data):
                type = 'rg'
            elif is_imgur_no_ex(readed_data):
                type = 'imgur_no_ex'
            else:
                type = 'other'
    # print(f"TYPE IS {type}")
    # 4. Если тип - 'other', то не скачиваем, переходим к след. файлу
    if type == 'other':
        print(f"{filename} doesn't supported, skipping")
        return

    # 5. Проверяем, есть ли данный файл в папке
    if type == 'common':
        filepath = os.path.join(folder, filename)

    if type == 'gifv':
        filename = f"{filename_without_ex}.mp4"
        filepath = os.path.join(folder, filename)

    if type == 'imgur_no_ex':
        filename = f"{filename_without_ex}.jpeg"
        filepath = os.path.join(folder, filename)

    if type == 'rg':
        # Получаем имя файла redgif
        rg_id = get_rg_id(readed_data)
        final_filename = f"{rg_id}.mp4"
        filepath = os.path.join(folder, final_filename)
        # print(filepath)
        # print(os.path.isfile(filepath))

    if os.path.isfile(filepath):
        print(f"{filename} already in this folder, skipping")
        return

    # 6. Качаем

    if type in ['common', 'gifv', 'imgur_no_ex']:
        if type == "gifv":
            filename = f"{filename_without_ex}.mp4"
            url = f"https://i.imgur.com/{filename}"
            print(f"GIFV file will be converted to {filename}")
        if type == 'imgur_no_ex':
            filename = f"{filename_without_ex}.jpeg"
            url = f"https://i.imgur.com/{filename}"
            print(f"File will be saved as {filename}")
        status = download_by_direct_link(url, folder)
        if status == 200:
            print(f"{filename} saved")
        else:
            print(f"{filename} could not be downloaded. Response status code is {status}")

    if type == 'rg':
        print(f"{filename} will be downloaded with external module...")
        print("Downloading |####### no progress bar ########|")
        download_rg(rg_id, filepath)
        print(f"{filename} saved")


def parser(subreddit, url_tail, depth, folder):
    file_counter = 0
    suffix = ''
    if not os.path.exists(folder):
        os.mkdir(folder)

    for i in range(depth):
        print('---------------------------------------------------')
        print(f"Trying to download pics json in range {i}")
        # 1. Загружаем json
        raw_data = download_json(subreddit, f"{url_tail}{suffix}")
        print('Success!')
        '''
        with open('test_json.json', 'w') as f:
            json.dump(raw_data, f)
        '''

        # 2. Парсим

        pictures, last_entry_name = get_pictures(raw_data)

        # 3. Обходим все картинки
        for pic in pictures:
            file_counter += 1
            url = pic['url']
            get_file(url, folder, file_counter)
            
        # Готовимся к следующему уровню погружения
        if url_tail.find("?") == -1:
            suffix = f"?after={last_entry_name}"
        else:
            suffix = f"&after={last_entry_name}"


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
