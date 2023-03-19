import os
import requests

from fake_useragent import UserAgent
from progress.bar import Bar

from reddit_img_parser.utils import log, remove_query_string, is_imgur_no_ex, is_reddit_gallery, extract_pic_links
from reddit_img_parser.rg import is_rg, get_rg_id, download_rg


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
        log("Error while downloading {filename}: {e}", filename=filename, e=e)


def get_file(url, folder):
    rg_id = ''
    readed_data = ''
    type = ''

    filename = remove_query_string(os.path.basename(url))
    filename_without_ex = os.path.splitext(filename)[0]
    file_extension = os.path.splitext(filename)[1]

    log("Trying to download file: {filename}", filename=filename)

    common_extensions = ['.jpg', '.gif', '.jpeg', '.mp4', '.png']

    # 3. Определяем тип файла
    if file_extension in common_extensions:
        type = 'common'
    elif file_extension == '.gifv':
        type = 'gifv'
    elif is_reddit_gallery(url):
        type = "gallery"
    else:
        # это папка???
        if url[-1] == '/':
            log("It's a folder, passing")
            return

        # rg? imgur no ex?
        # качаем
        log('For this type of file we need to download additional info')
        # print(f"URL is {url} ... folder is {folder}")
        status = download_by_direct_link(url, folder)
        if status != 200:
            log("{filename} could not be downloaded. Response status code is {status}", filename=filename, status=status)
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

    # 4. Если тип - 'other', то не скачиваем, переходим к след. файлу
    if type == 'other':
        log("{filename} doesn't supported, skipping", filename=filename)
        return

    # 4.5 Если это галерея, то запускаем рекурсивный процесс

    if type == 'gallery':
        log('For the gallery we need to download its pictures')
        gallery_status = download_by_direct_link(url, folder)
        if gallery_status != 200:
            log("{filename} could not be downloaded. Response status code is {gallery_status}", filename=filename, gallery_status=gallery_status)
            return
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
        log("{filename} already in this folder, skipping", filename=filename)
        return

    # 6. Качаем

    if type in ['common', 'gifv', 'imgur_no_ex']:
        if type == "gifv":
            filename = f"{filename_without_ex}.mp4"
            url = f"https://i.imgur.com/{filename}"
            log("GIFV file will be converted to {filename}", filename=filename)
        if type == 'imgur_no_ex':
            filename = f"{filename_without_ex}.jpeg"
            url = f"https://i.imgur.com/{filename}"
            log("File will be saved as {filename}", filename=filename)
        status = download_by_direct_link(url, folder)
        if status == 200:
            log("{filename} saved", filename=filename)
        else:
            log("{filename} could not be downloaded. Response status code is {status}", filename=filename, status=status)

    if type == 'rg':
        log("{filename} will be downloaded with external module...", filename=filename)
        print("Downloading |####### no progress bar ########|")
        download_rg(rg_id, filepath)
        log("{filename} saved", filename=filename)
