import re
from abc import abstractmethod
from typing import Any, Callable

from bs4 import BeautifulSoup, ResultSet, Tag

from constant.constant import BASE_URL
from scrapper.internal import login
from service import user_service, artist_service
from utils import thumbnail_utils



class BaseFetcher:
    def __init__(self, lastfm_username: str, lastfm_password: str):
        self.lastfm_username = lastfm_username
        self.lastfm_password = lastfm_password
        self.http = login.create_lastfm_session(lastfm_username, lastfm_password)
        self.user = user_service.get_user(lastfm_username)
        self.user_id = self.user.id
        self.page = 1
        self.stop = False

    @abstractmethod
    def thumbnail_dir(self):
        pass

    @abstractmethod
    def fetch(self, on_fetched: Callable[[str, int], None] | None = None):
        pass

    @abstractmethod
    def fetch_one_page(self, on_fetched: Callable[[str, int], None] | None, rows: Any):
        pass

class ArtistsFetcher(BaseFetcher):

    def __init__(self, lastfm_username: str, lastfm_password: str):
        super().__init__(lastfm_username, lastfm_password)
        self.base_url = f'{BASE_URL}/fr/user/{lastfm_username}/library/artists'
        self.all_artists = []

    def thumbnail_dir(self):
        return thumbnail_utils.get_thumbnails_dir()

    def fetch(self, on_artist_fetched: Callable[[str, int], None] | None = None):
        while not self.stop:
            response = self.http.get(self.base_url, params={'date_preset': 'ALL', 'page': self.page})
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            rows = soup.select('tr.chartlist-row')

            if not rows:
                break

            self.fetch_one_page(on_artist_fetched, rows)

            # pagination: stop if no next page
            if self.stop:
                break
            next_link = soup.select_one('ul.pagination-list li.pagination-next a')
            if not next_link:
                break
            self.page += 1

        artist_service.save_artists(self.all_artists, self.user_id)
        thumbnail_utils.save_thumbnails(self.all_artists, self.thumbnail_dir())

    def fetch_one_page(self, on_artist_fetched: Callable[[str, int], None] | None,
                       rows: ResultSet[Tag]) -> bool:
        for row in rows:
            # artist name
            name_tag = row.select_one('td.chartlist-name a')
            if not name_tag:
                continue
            artist_name = name_tag.get_text(strip=True)
            href = name_tag.attrs.get('href')
            count_span = row.select_one('td.chartlist-bar .chartlist-count-bar-value')
            scrobble_text = count_span.get_text(strip=True) if count_span else '0'
            nb_scrobbles = int(re.sub(r'[^\d]', '', scrobble_text))
            img_tag = row.select_one('td.chartlist-image img')

            if nb_scrobbles < 1000:
                self.stop = True
                break

            img_content = None
            if img_tag and img_tag.get('src'):
                img_response = self.http.get(img_tag['src'])
                if img_response.ok:
                    img_content = img_response.content

            artist_obj = {
                'artist_name': artist_name,
                'nb_scrobbles': nb_scrobbles,
                'artist_url': f'{BASE_URL}{href}',
                'img_content': img_content
            }

            self.all_artists.append(artist_obj)

            if on_artist_fetched:
                on_artist_fetched(artist_name, nb_scrobbles)
