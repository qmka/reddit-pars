from redgifs import API
from bs4 import BeautifulSoup


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


def download_rg(id, filepath):

    api = API()
    api.login()

    gif = api.get_gif(id)

    api.download(gif.urls.hd, f"{filepath}")
    api.close()
