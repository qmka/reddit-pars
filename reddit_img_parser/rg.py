import requests
import os

# from redgifs import API
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from progress.bar import Bar

from reddit_img_parser.utils import log

TIMEOUT = 10


def is_rg(file):
    if file.find("redgifs.com") == -1:
        return False
    return True


def get_rg_id(file):
    soup = BeautifulSoup(file, 'html.parser')
    soup.prettify()

    link_with_id = soup.select("[rel='canonical']")[0]['href']
    id = link_with_id.split('/')[-1]
    return id


def get_rg_extension(url):
    common_extensions = ['.jpg', '.gif', '.jpeg', '.mp4', '.png']
    file_extension = os.path.splitext(url)[1]
    if file_extension in common_extensions:
        return file_extension
    else:
        return '.mp4'


'''
# Way to download redgif using external library
def download_rg(id, filepath):
    try:
        api = API()
        api.login()
        gif = api.get_gif(id)
        api.download(gif.urls.hd, f"{filepath}")
        success = True
    except Exception as e:
        print(f"An error occurred downloading RedGif file: {e}")
        success = False
    finally:
        api.close()
    return success
'''


def get_response_from_redgif_api(url, headers, stream):
    if not headers:
        headers = {
            'User-Agent': UserAgent().chrome,
        }
    timeout = TIMEOUT
    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=timeout,
            stream=stream
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        log("An error occurred while requesting the URL: {url}", url=url)
        log("The error message is: {e}", e=e)
        return None
    else:
        return response


def login_to_redgif_api():
    try:
        headers = None
        stream = False
        # Логин
        login_response = get_response_from_redgif_api(
            'https://api.redgifs.com/v2/auth/temporary',
            headers,
            stream
        )
        js = login_response.json()
        temp_token = js['token']

        # Авторизуемся
        headers = {
            'User-Agent': UserAgent().chrome,
            'authorization': f"Bearer {temp_token}"
        }
        return headers
    except requests.exceptions.RequestException as e:
        print("Error during login to RedGif API: ", e)


def find_gif_url(id, headers):
    link_response = get_response_from_redgif_api(
        f"https://api.redgifs.com/v2/gifs/{id}",
        headers,
        stream=False
    )
    if link_response is None:
        gif_url = None
    else:
        js = link_response.json()

        ###########
        # print(f"Name: {js['gif']['userName']}")
        # print(f"Video tags: {js['gif']['tags']}")
        ###########

        gif_url = js['gif']['urls']['hd']
    return gif_url


def download_gif(gif_url, headers, filepath):
    try:
        # Качаем и сохраняем гиф
        stream = True
        file_response = get_response_from_redgif_api(
            gif_url,
            headers,
            stream
        )

        total_length = int(file_response.headers.get("Content-Length", 0))
        block_size = 1024
        written = 0
        bar = Bar('Downloading', max=None, suffix='%(percent)d%%')
        with open(filepath, "wb") as f:
            for data in file_response.iter_content(block_size):
                written += len(data)
                f.write(data)
                if bar.max is None:
                    bar.max = max(written, total_length)
                bar.next(len(data))
        bar.finish()
        print('Done!')
    except requests.exceptions.RequestException as e:
        print("Error during downloading gif: ", e)


def download_rg(id, filepath):
    success = False
    try:
        headers = login_to_redgif_api()
        gif_url = find_gif_url(id, headers)
        if gif_url is None:
            log("Gif with ID {id} not found!", id=id)
            success = False
        else:
            download_gif(gif_url, headers, filepath)
            success = True
    except requests.exceptions.RequestException as e:
        print("Error during downloading RedGif: ", e)
        success = False
    finally:
        return success
