import os
import codecs
from datetime import datetime
from bs4 import BeautifulSoup
from reddit_img_parser.settings import ROOT_FOLDER, FOLDER_TEMPLATE


def log(text, noprint=False, **kwargs):
    # Usage:
    # a = "world"
    # log("hello {a}", a=a)
    now = datetime.now()
    timestamp = now.strftime("[%Y-%m-%d %H:%M:%S]")
    message = text.format(**kwargs)
    log_message = f"{timestamp} {message}\n"
    with codecs.open('parser.log', 'a', encoding='utf-8') as f:
        f.write(log_message)
    if not noprint:
        print(message)


def is_imgur_no_ex(file):
    return file.find("https://s.imgur.com")


def is_reddit_gallery(url):
    return url.find("https://www.reddit.com/gallery/") >= 0


def extract_pic_links(gallery):
    soup = BeautifulSoup(gallery, 'html.parser')
    soup.prettify()

    links = []

    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.find("https://preview.redd.it") >= 0:
            image_direct_link = (
                f"https://i.redd.it/"
                f"{href.split('/')[3].split('?')[0]}")
            links.append(image_direct_link)
    return links


def remove_query_string(filename):
    name, extension = os.path.splitext(filename)
    if extension:
        extension_without_query = extension.split("?")[0]
    else:
        extension_without_query = ""
    return name + extension_without_query


def make_folder(name, category, time_filter):
    if FOLDER_TEMPLATE == 'name_category_time':
        folder_template = f"{name}_{category}_{time_filter}"
    else:
        folder_template = f"{name}"

    if not os.path.exists(ROOT_FOLDER):
        os.mkdir(ROOT_FOLDER)

    path = os.path.join(ROOT_FOLDER, folder_template)
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def convert_unix_time(unix_time):
    timestamp = int(unix_time)
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
