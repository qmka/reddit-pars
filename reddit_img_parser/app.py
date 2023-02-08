import requests
import os
import sqlite3
from progress.bar import Bar


def download_json(subreddit, suffix):
    
    url = 'https://www.reddit.com/r/' + subreddit + '/new/.json' + suffix
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.4; en-US; rv:1.9.2.2) Gecko/20100316 Firefox/3.6.2'}
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
    pic_urls = []

    for entry in entries:
        # print(entry['data']['title'])

        # make list of pic urls
        pic_urls.append(entry['data']['url'])
    
    folder = "images"

    if not os.path.exists(folder):
        os.makedirs(folder)

    conn = sqlite3.connect("downloads.db")
    cursor = conn.cursor()

    
    for url in pic_urls:
        filename = os.path.basename(url)
        file_extension = os.path.splitext(filename)[1]
        if not file_extension:
            print(f"{filename} does not have an extension, skipping")
            continue
        filepath = os.path.join(folder, filename)
        cursor.execute("SELECT name FROM files WHERE name=?", (filename,))
        result = cursor.fetchone()

        if result:
            print(f"{filename} already exists in the database, skipping download")
            continue

        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.4; en-US; rv:1.9.2.2) Gecko/20100316 Firefox/3.6.2'}
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
                    
                cursor.execute("INSERT INTO files (name) VALUES (?)", (filename,))
                conn.commit()
                print(f"{filename} saved")
            else:
                print(f"{filename} could not be downloaded")
        except requests.exceptions.RequestException as e:
            print(f"Error while downloading {filename}: {e}")
    
    conn.close()

    # определяем суффикс
    # берем последний элемент
    last_entry_name = entries[-1]['data']['name']
    suffix = f"?after={last_entry_name}"
    return suffix   



def check_db():
    folder = "images"

    conn = sqlite3.connect("downloads.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS files (name TEXT PRIMARY KEY)")
    cursor.execute("SELECT name FROM files")
    results = cursor.fetchall()

    for result in results:
        filename = result[0]
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            cursor.execute("DELETE FROM files WHERE name=?", (filename,))
            conn.commit()
            print(f"{filename} not found in the folder, removing from the database")

    conn.close()

def parser():
    subreddit = 'wallpapers'
    suffix = ''
    depth = int(input("Select depth of subreddit downloading: "))
    for i in range(depth):
        data = download_json(subreddit, suffix)
        check_db()
        # по-хорошему надо сделать так, чтобы парсинг шёл отдельно, а загрузка отдельно
        suffix = get_pictures(data)