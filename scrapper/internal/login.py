import requests
from bs4 import BeautifulSoup

from constant.constant import LOGIN_PATH


def create_lastfm_session(username: str, password: str) -> requests.Session:
    s = requests.Session()
    login_page = s.get(LOGIN_PATH)
    soup = BeautifulSoup(login_page.text, 'html.parser')
    csrf_token = soup.select_one('input[name="csrfmiddlewaretoken"]')['value']

    resp = s.post(LOGIN_PATH, data={
        'csrfmiddlewaretoken': csrf_token,
        'username_or_email': username,
        'password': password,
        'next': '/fr/user/_',
    }, headers={'Referer': LOGIN_PATH})
    resp.raise_for_status()

    if '/login' in resp.url:
        raise ValueError('Last.fm login failed — check credentials')

    return s
