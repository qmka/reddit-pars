import os
import requests

from fake_useragent import UserAgent
from progress.bar import Bar

from reddit_img_parser.utils import log
from reddit_img_parser.utils import remove_query_string
from reddit_img_parser.utils import is_imgur_no_ex
from reddit_img_parser.utils import is_reddit_gallery
from reddit_img_parser.utils import extract_pic_links
from reddit_img_parser.rg import is_rg
from reddit_img_parser.rg import get_rg_id
from reddit_img_parser.rg import get_rg_extension
from reddit_img_parser.rg import download_rg


def download_file(url, filepath, filename, is_pre):
    try:
        headers = {'User-Agent': UserAgent().chrome}
        timeout = 5
        response = requests.get(
            url,
            headers=headers,
            timeout=timeout,
            stream=True)
        response.raise_for_status()

        total_length = int(response.headers.get("Content-Length", 0))
        if total_length < 1024 and not is_pre:
            log(f"Length is {total_length} bytes: probably not a media file",
                total_length=total_length)
            return 400
        download_with_bar(filepath, response, total_length)
        return response.status_code

    except requests.exceptions.RequestException as e:
        log("Error while downloading {filename}: {e}", filename=filename, e=e)
        return getattr(e.response, "status_code", 400)


def download_with_bar(filepath, response, total_length):
    block_size = 1024
    written = 0
    bar = Bar('Downloading', max=None, suffix='%(percent)d%%')
    with open(filepath, "wb") as f:
        for data in response.iter_content(block_size):
            written += len(data)
            f.write(data)
            if bar.max is None:
                bar.max = max(written, total_length)
            bar.next(len(data))
    bar.finish()


def download_by_direct_link(url, folder, is_pre=False):
    filename = os.path.basename(url)
    filepath = os.path.join(folder, filename)
    status_code = download_file(url, filepath, filename, is_pre=is_pre)
    return status_code


def get_filename_without_ex(filename):
    return os.path.splitext(filename)[0]


def get_filename(url):
    return remove_query_string(os.path.basename(url))


def get_uncommon_media_type(filename, url, folder):
    log('For this type of file we need to download additional info')
    status = download_by_direct_link(url, folder, is_pre=True)
    if status != 200:
        return ("broken", "")
    log("Prepare to download media file...")
    filepath = os.path.join(folder, filename)
    with open(filepath, 'r') as f:
        readed_data = f.read()
    os.remove(filepath)
    if is_rg(readed_data):
        return ('rg', readed_data)
    if is_imgur_no_ex(readed_data):
        return ('imgur_no_ex', readed_data)
    return ('other', readed_data)


def get_file_media_type(filename, url, folder):
    common_extensions = ['.jpg', '.gif', '.jpeg', '.mp4', '.png']
    file_extension = os.path.splitext(filename)[1]
    readed_data = ''
    if file_extension in common_extensions and not is_rg(url):
        media_type = 'common'
    elif file_extension == '.gifv':
        media_type = 'gifv'
    elif is_reddit_gallery(url):
        media_type = 'gallery'
    elif url.endswith('/'):
        media_type = 'folder'
    else:
        media_type, readed_data = get_uncommon_media_type(filename, url, folder)
    return (media_type, readed_data)


def is_file_exists(media_type, folder, filename, readed_data):
    if media_type == 'common':
        filepath = os.path.join(folder, filename)

    if media_type == 'gifv':
        filename = f"{get_filename_without_ex(filename)}.mp4"
        filepath = os.path.join(folder, filename)

    if media_type == 'imgur_no_ex':
        filename = f"{get_filename_without_ex(filename)}.jpeg"
        filepath = os.path.join(folder, filename)

    if media_type == 'rg':
        # Получаем имя файла redgif
        rg_id = get_rg_id(readed_data)
        final_filename = f"{rg_id}.mp4"
        filepath = os.path.join(folder, final_filename)
        # print(filepath)
        # print(os.path.isfile(filepath))

    if os.path.isfile(filepath):
        log("{filename} already in this folder, skipping", filename=filename)
        return True
    return False


def folder_type_handler():
    log("It's a folder, passing")


def other_type_handler(filename):
    log("{filename} doesn't supported, skipping", filename=filename)


def broken_type_handler(filename):
    log("{filename} could not be downloaded", filename=filename)


def gallery_type_handler(url, folder, filename):
    print(url, folder, filename)
    log('For the gallery we need to download its pictures')
    gallery_status = download_by_direct_link(url, folder, is_pre=True)
    if gallery_status != 200:
        log("{filename} could not be downloaded."
            "Response status code is {gallery_status}",
            filename=filename, gallery_status=gallery_status)
    else:
        # если скачали, то загружаем и парсим
        filepath = os.path.join(folder, filename)
        with open(filepath, 'r') as f:
            readed_data = f.read()
        os.remove(filepath)
        pic_links = extract_pic_links(readed_data)
        for link in pic_links:
            get_file(link, folder)
    return


def rg_type_handler(media_type, folder, filename, readed_data):
    if is_file_exists(media_type, folder, filename, readed_data):
        return
    # Uncomment next lines for using external downloading module
    # log("{filename} will be downloaded with external module...",
    #     filename=filename)
    # print("Downloading |####### no progress bar ########|")
    rg_id = get_rg_id(readed_data)
    rg_ex = get_rg_extension(filename)
    final_filename = f"{rg_id}{rg_ex}"
    filepath = os.path.join(folder, final_filename)
    status = download_rg(rg_id, filepath)
    if status is True:
        log("{filename} saved", filename=filename)
    else:
        log("{filename} didn't saved", filename=filename)


def gifv_type_handler(media_type, folder, filename, readed_data):
    if is_file_exists(media_type, folder, filename, readed_data):
        return
    filename = f"{get_filename_without_ex(filename)}.mp4"
    url = f"https://i.imgur.com/{filename}"
    log("GIFV file will be converted to {filename}", filename=filename)
    status = download_by_direct_link(url, folder)
    print_downloading_status(filename, status)


def imgur_type_handler(media_type, folder, filename, readed_data):
    if is_file_exists(media_type, folder, filename, readed_data):
        return
    filename = f"{get_filename_without_ex(filename)}.jpeg"
    url = f"https://i.imgur.com/{filename}"
    log("File will be saved as {filename}", filename=filename)
    status = download_by_direct_link(url, folder)
    print_downloading_status(filename, status)


def common_type_handler(media_type, folder, url, readed_data):
    filename = get_filename(url)
    if is_file_exists(media_type, folder, filename, readed_data):
        return
    status = download_by_direct_link(url, folder)
    print_downloading_status(filename, status)


def get_file(url, folder):
    filename = get_filename(url)
    log("Trying to download file: {filename}", filename=filename)
    media_type, readed_data = get_file_media_type(filename, url, folder)

    type_functions = {
        'folder': folder_type_handler,
        'other': lambda: other_type_handler(filename),
        'broken': lambda: broken_type_handler(filename),
        'gallery': lambda: gallery_type_handler(url, folder, filename),
        'rg': lambda: rg_type_handler(media_type, folder,
                                      filename, readed_data),
        'gifv': lambda: gifv_type_handler(media_type, folder,
                                          filename, readed_data),
        'imgur_no_ex': lambda: imgur_type_handler(media_type, folder,
                                                  filename, readed_data),
        'common': lambda: common_type_handler(media_type, folder,
                                              url, readed_data)
    }

    type_functions[media_type]()
    return


def print_downloading_status(filename, status):
    if status == 200:
        log("{filename} saved", filename=filename)
    else:
        log("{filename} could not be downloaded."
            "Response status code is {status}",
            filename=filename, status=status)
