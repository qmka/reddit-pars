import os
from datetime import datetime
from reddit_img_parser.settings import ROOT_FOLDER


def log(text, noprint=False, **kwargs):
    # Usage:
    # a = "world"
    # log("hello {a}", a=a)
    now = datetime.now()
    timestamp = now.strftime("[%Y-%m-%d %H:%M:%S]")
    message = text.format(**kwargs)
    log_message = f"{timestamp} {message}\n"
    with open('parser.log', 'a') as f:
        f.write(log_message)
    if not noprint:
        print(message)


def is_imgur_no_ex(file):
    return file.find("https://s.imgur.com")


def remove_query_string(filename):
    name, extension = os.path.splitext(filename)
    if extension:
        extension_without_query = extension.split("?")[0]
    else:
        extension_without_query = ""
    return name + extension_without_query


def make_folder(name, category, time_filter):
    folder_template = f"{name}_{category}_{time_filter}"

    if not os.path.exists(ROOT_FOLDER):
        os.mkdir(ROOT_FOLDER)

    path = os.path.join(ROOT_FOLDER, folder_template)
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def convert_unix_time(unix_time):
    timestamp = int(unix_time)
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
