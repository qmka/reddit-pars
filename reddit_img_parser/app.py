import requests
import os
import json
from progress.bar import Bar
from fake_useragent import UserAgent


def download_json(subreddit, suffix):
    user_agent = UserAgent()
    url = 'https://www.reddit.com/r/' + subreddit + '/new/.json' + suffix
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
    suffix = f"?after={last_entry_name}" 

    return pic_data, suffix


def save_pictures(pic_urls, folder):

    user_agent = UserAgent()

    if not os.path.exists(folder):
        os.makedirs(folder)

    for url in pic_urls:
        filename = os.path.basename(url)
        file_extension = os.path.splitext(filename)[1]
        if not file_extension:
            print(f"{filename} does not have an extension, skipping")
            continue
        filepath = os.path.join(folder, filename)

        if os.path.isfile(filepath):
            print(f"{filename} already in this folder, skipping")
            continue

        try:
            headers = {'User-Agent': user_agent.chrome}
            timeout = 5
            response = requests.get(url, headers=headers, timeout=timeout, stream=True)

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
    

def parser():
    subreddit = 'wallpapers'
    suffix = ''
    folder = 'images'
    
    depth = int(input("Select depth of subreddit downloading (not more than 40): "))
    # score = int(input("How many ups: "))
    for i in range(depth):
        print(f"Range {i}")
        # 1. Загружаем json
        raw_data = download_json(subreddit, suffix)

        with open('json_data.json', 'w') as outfile:
            json.dump(raw_data, outfile)

        # 2. Парсим
        links = []
        pictures, suffix = get_pictures(raw_data)
        for pic in pictures:
            links.append(pic['url'])

        # 3. Сохраняем на диск
        save_pictures(links, folder)

        

