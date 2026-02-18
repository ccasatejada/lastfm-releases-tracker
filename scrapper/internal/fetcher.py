import re
import time
from abc import abstractmethod
from collections.abc import Callable
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup, ResultSet, Tag

from constant.constant import BASE_URL
from scrapper.internal import login
from service import artist_service, release_service, user_service
from utils import thumbnail_utils, url_utils
from utils.filter_release_utils import excluded_releases


class HttpSession:
    @classmethod
    def set_http_session(
        cls,
        lastfm_username: str,
        lastfm_password: str,
        http_session: requests.Session = None,
    ) -> requests.Session:
        if http_session is None:
            http_session = login.create_lastfm_session(lastfm_username, lastfm_password)
        return http_session


class BaseFetcher:
    def __init__(
        self,
        lastfm_username: str,
        lastfm_password: str,
        http_session: requests.Session = None,
    ):
        self.lastfm_username = lastfm_username
        self.lastfm_password = lastfm_password
        self.http_session = HttpSession.set_http_session(
            self.lastfm_username, self.lastfm_password, http_session
        )

        self.user = user_service.get_user(lastfm_username)
        self.id_user = self.user.id
        _, settings = user_service.get_user_with_settings(self.id_user)
        self.today = datetime.today()
        self.default_min_date = self.today - timedelta(days=365)
        self.settings = settings
        self.page = 1
        self.stop = False

    def get_http_session(self) -> requests.Session:
        return self.http_session

    def get_min_scrobbles(self) -> int:
        return (
            self.settings.min_scrobbles
            if self.settings and self.settings.min_scrobbles
            else 1000
        )

    def get_min_date(self) -> date:
        return (
            self.settings.releases_not_before
            if self.settings and self.settings.releases_not_before
            else self.default_min_date
        )

    @abstractmethod
    def thumbnail_dir(self) -> Path:
        pass

    @abstractmethod
    def fetch(self, on_fetched: Callable[[dict], None] | None = None) -> None:
        pass

    @abstractmethod
    def fetch_one_page(
        self, on_fetched: Callable[[dict], None] | None, rows: Any
    ) -> None:
        pass


class ArtistsFetcher(BaseFetcher):
    def __init__(self, lastfm_username: str, lastfm_password: str):
        super().__init__(lastfm_username, lastfm_password)
        self.base_url = f'{BASE_URL}/fr/user/{lastfm_username}/library/artists'
        self.all_artists = []

    def thumbnail_dir(self) -> Path:
        return thumbnail_utils.artists_thumbnails_dir()

    def fetch(self, on_artist_fetched: Callable[[dict], None] | None = None) -> None:
        while not self.stop:
            response = self.http_session.get(
                self.base_url, params={'date_preset': 'ALL', 'page': self.page}
            )
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

        artist_service.save_artists(self.all_artists, self.id_user)
        thumbnail_utils.save_thumbnails(self.all_artists, self.thumbnail_dir())

    def fetch_one_page(
        self, on_artist_fetched: Callable[[dict], None] | None, rows: ResultSet[Tag]
    ) -> None:
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

            if nb_scrobbles < self.get_min_scrobbles():
                self.stop = True
                break

            img_content = None
            if img_tag and img_tag.get('src'):
                img_response = self.http_session.get(img_tag['src'])
                if img_response.ok:
                    img_content = img_response.content

            artist_obj = {
                'artist_name': artist_name,
                'nb_scrobbles': nb_scrobbles,
                'artist_url': f'{BASE_URL}{href}',
                'img_content': img_content,
            }

            self.all_artists.append(artist_obj)

            if on_artist_fetched:
                on_artist_fetched(
                    dict(artist_name=artist_name, nb_scrobbles=nb_scrobbles)
                )


class ReleasesFetcher(BaseFetcher):
    def __init__(
        self,
        lastfm_username: str,
        lastfm_password: str,
        id_artist: int,
        http_session: requests.Session = None,
    ):
        super().__init__(lastfm_username, lastfm_password, http_session)
        self.all_releases: list[dict[str, Any]] = []
        self.artist = artist_service.get_artist(id_artist)

    def thumbnail_dir(self) -> Path:
        return thumbnail_utils.releases_thumbnails_dir(self.artist.id)

    def fetch(self, on_release_fetched: Callable[[dict], None] | None = None) -> None:
        _artist_url = url_utils.clean_url(str(self.artist.artist_url))
        albums_url = f'{_artist_url}/+albums'

        while not self.stop:
            response = self.http_session.get(
                albums_url, params={'order': 'release_date', 'page': self.page}
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            section = soup.select_one('#artist-albums-section')
            if not section:
                break

            rows = section.select('ol > li')
            if not rows:
                break

            self.fetch_one_page(on_release_fetched, rows)

            if self.stop:
                break

            next_link = soup.select_one('nav.pagination ul li.pagination-next a')
            if not next_link:
                break
            self.page += 1

        release_service.save_releases(self.all_releases, self.artist.id, self.id_user)
        thumbnail_utils.save_thumbnails(self.all_releases, self.thumbnail_dir())

    def fetch_one_page(
        self, on_release_fetched: Callable[[dict], None] | None, rows: Any
    ) -> None:
        """
        if release has no title -> continue
        if release has no tracks (nb_tracks) -> continue
        if release has no release date -> continue
        if release has no cover -> continue
        :param on_release_fetched:
        :param rows:
        :return:
        """
        for li in rows:
            h3_a = li.select_one('h3 a')

            if not h3_a:
                continue

            release_title = h3_a.get_text(strip=True)
            if excluded_releases(release_title):
                continue
            release_href = h3_a.get('href')
            release_url = f'{BASE_URL}{release_href}' if release_href else None

            p_text = ''
            for p_tag in li.find_all('p'):
                p_text = p_tag.get_text(strip=True)
                if 'listeners' not in p_text or 'tracks' in p_text:
                    break

            if not p_text:
                continue

            parts = p_text.split('·')
            date_str = parts[0].strip()
            tracks_str = parts[1].strip() if len(parts) > 1 else '0'

            nb_tracks = int(re.sub(r'[^\d]', '', tracks_str) or '0')
            if nb_tracks < 5:
                continue

            try:
                release_date = date.strptime(date_str, '%d %b %Y')
            except ValueError:
                continue

            if not release_date:
                continue

            if release_date < self.get_min_date():
                self.stop = True
                break

            img_content = None
            img_tag = li.select_one('div.media-item img')
            if img_tag and img_tag.get('src'):
                img_response = self.http_session.get(img_tag['src'])
                if img_response.ok:
                    img_content = img_response.content

            # bonus - get length
            length = 0
            if release_url:
                time.sleep(1)
                detail_resp = self.http_session.get(release_url)
                if detail_resp.ok:
                    detail_soup = BeautifulSoup(detail_resp.text, 'html.parser')
                    dd = detail_soup.select_one('dd.catalogue-metadata-description')
                    if dd:
                        time_match = re.search(r'(\d+):(\d+)', dd.get_text(strip=True))
                        if time_match:
                            length = int(time_match.group(1))

            release_obj = {
                'release_title': release_title,
                'release_date': release_date,
                'nb_tracks': nb_tracks,
                'length': length,
                'release_url': release_url,
                'img_content': img_content,
            }
            self.all_releases.append(release_obj)

            if on_release_fetched:
                on_release_fetched(
                    dict(
                        artist_name=self.artist.artist_name,
                        release_title=release_title,
                        nb_tracks=nb_tracks,
                    )
                )
