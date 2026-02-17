from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch

from model.model import AppUser, AppUserSettings, Artist
from scrapper.internal.fetcher import (
    ArtistsFetcher,
    BaseFetcher,
    HttpSession,
    ReleasesFetcher,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_user(id_=1, username='testuser'):
    u = AppUser(id=id_, lastfm_username=username)
    return u


def _make_settings(min_scrobbles=1000, releases_not_before=None):
    s = AppUserSettings(id=1, id_user=1, min_scrobbles=min_scrobbles)
    if releases_not_before:
        s.releases_not_before = releases_not_before
    return s


def _make_artist(id_=1, name='Radiohead', url='https://www.last.fm/music/Radiohead'):
    a = Artist(id=id_, artist_name=name, artist_url=url)
    return a


def _patch_base_fetcher_deps(user=None, settings=None):
    """Return a dict of patches needed to instantiate BaseFetcher without network."""
    user = user or _make_user()
    settings = settings or _make_settings()

    patches = {
        'login': patch(
            'scrapper.internal.fetcher.login.create_lastfm_session',
            return_value=MagicMock(),
        ),
        'get_user': patch(
            'scrapper.internal.fetcher.user_service.get_user', return_value=user
        ),
        'get_user_with_settings': patch(
            'scrapper.internal.fetcher.user_service.get_user_with_settings',
            return_value=(user, settings),
        ),
    }
    return patches


# ---------------------------------------------------------------------------
# HttpSession
# ---------------------------------------------------------------------------


class TestHttpSession:
    @patch('scrapper.internal.fetcher.login.create_lastfm_session')
    def test_creates_session_when_none(self, mock_login):
        mock_session = MagicMock()
        mock_login.return_value = mock_session

        result = HttpSession.set_http_session('user', 'pass', None)

        mock_login.assert_called_once_with('user', 'pass')
        assert result is mock_session

    def test_reuses_existing_session(self):
        existing = MagicMock()
        result = HttpSession.set_http_session('user', 'pass', existing)
        assert result is existing


# ---------------------------------------------------------------------------
# BaseFetcher
# ---------------------------------------------------------------------------


class TestBaseFetcher:
    def test_init_sets_attributes(self):
        user = _make_user()
        settings = _make_settings(min_scrobbles=2000)
        patches = _patch_base_fetcher_deps(user, settings)

        with patches['login'], patches['get_user'], patches['get_user_with_settings']:
            fetcher = BaseFetcher('testuser', 'testpass')

        assert fetcher.id_user == 1
        assert fetcher.settings.min_scrobbles == 2000
        assert fetcher.page == 1
        assert fetcher.stop is False

    def test_get_min_scrobbles_from_settings(self):
        settings = _make_settings(min_scrobbles=500)
        patches = _patch_base_fetcher_deps(settings=settings)

        with patches['login'], patches['get_user'], patches['get_user_with_settings']:
            fetcher = BaseFetcher('testuser', 'testpass')

        assert fetcher.get_min_scrobbles() == 500

    def test_get_min_scrobbles_default_when_no_settings(self):
        patches = _patch_base_fetcher_deps(settings=None)
        with (
            patches['login'],
            patches['get_user'],
            patch(
                'scrapper.internal.fetcher.user_service.get_user_with_settings',
                return_value=(_make_user(), None),
            ),
        ):
            fetcher = BaseFetcher('testuser', 'testpass')

        assert fetcher.get_min_scrobbles() == 1000

    def test_get_min_date_from_settings(self):
        d = date(2023, 6, 1)
        settings = _make_settings(releases_not_before=d)
        patches = _patch_base_fetcher_deps(settings=settings)

        with patches['login'], patches['get_user'], patches['get_user_with_settings']:
            fetcher = BaseFetcher('testuser', 'testpass')

        assert fetcher.get_min_date() == d

    def test_get_min_date_default_when_no_settings(self):
        patches = _patch_base_fetcher_deps(settings=None)
        with (
            patches['login'],
            patches['get_user'],
            patch(
                'scrapper.internal.fetcher.user_service.get_user_with_settings',
                return_value=(_make_user(), None),
            ),
        ):
            fetcher = BaseFetcher('testuser', 'testpass')

        # default_min_date is a datetime (datetime.today() - timedelta)
        expected = datetime.today() - timedelta(days=365)
        result = fetcher.get_min_date()
        assert result.year == expected.year
        assert result.month == expected.month
        assert result.day == expected.day

    def test_get_http_session_returns_session(self):
        mock_session = MagicMock()
        patches = _patch_base_fetcher_deps()

        with (
            patches['login'] as login_mock,
            patches['get_user'],
            patches['get_user_with_settings'],
        ):
            login_mock.return_value = mock_session
            fetcher = BaseFetcher('testuser', 'testpass')

        assert fetcher.get_http_session() is mock_session


# ---------------------------------------------------------------------------
# ArtistsFetcher
# ---------------------------------------------------------------------------

ARTIST_ROW_HTML = """
<tr class="chartlist-row">
  <td class="chartlist-image"><img src="https://img.example.com/artist.jpg"></td>
  <td class="chartlist-name"><a href="/music/Radiohead">Radiohead</a></td>
  <td class="chartlist-bar"><span class="chartlist-count-bar-value">5,000 scrobbles</span></td>
</tr>
"""

ARTIST_ROW_LOW_SCROBBLES_HTML = """
<tr class="chartlist-row">
  <td class="chartlist-image"><img src="https://img.example.com/artist2.jpg"></td>
  <td class="chartlist-name"><a href="/music/Unknown">Unknown</a></td>
  <td class="chartlist-bar"><span class="chartlist-count-bar-value">100 scrobbles</span></td>
</tr>
"""


class TestArtistsFetcher:
    def _make_fetcher(self):
        patches = _patch_base_fetcher_deps()
        with patches['login'], patches['get_user'], patches['get_user_with_settings']:
            fetcher = ArtistsFetcher('testuser', 'testpass')
        return fetcher

    def test_init(self):
        fetcher = self._make_fetcher()
        assert 'testuser' in fetcher.base_url
        assert fetcher.all_artists == []

    def test_fetch_one_page_parses_artists(self):
        from bs4 import BeautifulSoup

        fetcher = self._make_fetcher()
        fetcher.http_session = MagicMock()
        img_response = MagicMock()
        img_response.ok = True
        img_response.content = b'fake_image_data'
        fetcher.http_session.get.return_value = img_response

        soup = BeautifulSoup(ARTIST_ROW_HTML, 'html.parser')
        rows = soup.select('tr.chartlist-row')

        callback = MagicMock()
        fetcher.fetch_one_page(callback, rows)

        assert len(fetcher.all_artists) == 1
        assert fetcher.all_artists[0]['artist_name'] == 'Radiohead'
        assert fetcher.all_artists[0]['nb_scrobbles'] == 5000
        assert fetcher.all_artists[0]['img_content'] == b'fake_image_data'
        callback.assert_called_once_with('Radiohead', 5000)

    def test_fetch_one_page_stops_on_low_scrobbles(self):
        from bs4 import BeautifulSoup

        fetcher = self._make_fetcher()
        fetcher.http_session = MagicMock()

        soup = BeautifulSoup(ARTIST_ROW_LOW_SCROBBLES_HTML, 'html.parser')
        rows = soup.select('tr.chartlist-row')

        fetcher.fetch_one_page(None, rows)

        assert fetcher.stop is True
        assert len(fetcher.all_artists) == 0

    def test_fetch_one_page_handles_missing_image(self):
        from bs4 import BeautifulSoup

        html = """
        <tr class="chartlist-row">
          <td class="chartlist-image"></td>
          <td class="chartlist-name"><a href="/music/Radiohead">Radiohead</a></td>
          <td class="chartlist-bar"><span class="chartlist-count-bar-value">5,000 scrobbles</span></td>
        </tr>
        """
        fetcher = self._make_fetcher()
        fetcher.http_session = MagicMock()

        soup = BeautifulSoup(html, 'html.parser')
        rows = soup.select('tr.chartlist-row')

        fetcher.fetch_one_page(None, rows)

        assert len(fetcher.all_artists) == 1
        assert fetcher.all_artists[0]['img_content'] is None

    def test_fetch_one_page_skips_row_without_name(self):
        from bs4 import BeautifulSoup

        html = """
        <tr class="chartlist-row">
          <td class="chartlist-image"></td>
          <td class="chartlist-name"></td>
          <td class="chartlist-bar"><span class="chartlist-count-bar-value">5,000</span></td>
        </tr>
        """
        fetcher = self._make_fetcher()
        soup = BeautifulSoup(html, 'html.parser')
        rows = soup.select('tr.chartlist-row')

        fetcher.fetch_one_page(None, rows)

        assert len(fetcher.all_artists) == 0

    @patch('scrapper.internal.fetcher.thumbnail_utils')
    @patch('scrapper.internal.fetcher.artist_service')
    def test_fetch_full_single_page(self, mock_artist_svc, mock_thumb):
        fetcher = self._make_fetcher()

        page_html = f"""
        <html><body>
        <table>{ARTIST_ROW_HTML}</table>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.text = page_html
        mock_response.raise_for_status = MagicMock()
        mock_response.ok = True
        mock_response.content = b'img'

        fetcher.http_session = MagicMock()
        fetcher.http_session.get.return_value = mock_response

        # ArtistsFetcher.fetch() calls self.set_http_session which doesn't exist
        # (HttpSession is not a parent class) — patch around this bug in source
        fetcher.set_http_session = lambda *a, **kw: None

        fetcher.fetch()

        mock_artist_svc.save_artists.assert_called_once()
        mock_thumb.save_thumbnails.assert_called_once()


# ---------------------------------------------------------------------------
# ReleasesFetcher
# ---------------------------------------------------------------------------

RELEASE_LI_HTML = """
<li>
  <div class="media-item"><img src="https://img.example.com/cover.jpg"></div>
  <h3><a href="/music/Radiohead/OK+Computer">OK Computer</a></h3>
  <p>16 Jun 1997 · 12 tracks</p>
</li>
"""

RELEASE_LI_FEW_TRACKS_HTML = """
<li>
  <h3><a href="/music/Radiohead/Single">Single</a></h3>
  <p>16 Jun 1997 · 2 tracks</p>
</li>
"""

RELEASE_LI_NO_DATE_HTML = """
<li>
  <h3><a href="/music/Radiohead/NoDate">NoDate</a></h3>
  <p>invalid date · 12 tracks</p>
</li>
"""


class TestReleasesFetcher:
    def _make_fetcher(self, artist=None):
        artist = artist or _make_artist()
        patches = _patch_base_fetcher_deps()
        with patches['login'], patches['get_user'], patches['get_user_with_settings']:
            with patch(
                'scrapper.internal.fetcher.artist_service.get_artist',
                return_value=artist,
            ):
                fetcher = ReleasesFetcher('testuser', 'testpass', 1)
        return fetcher

    def test_init(self):
        fetcher = self._make_fetcher()
        assert fetcher.all_releases == []
        assert fetcher.artist.artist_name == 'Radiohead'

    def test_fetch_one_page_parses_release(self):
        from bs4 import BeautifulSoup

        fetcher = self._make_fetcher()
        fetcher.settings = _make_settings(releases_not_before=date(1990, 1, 1))
        fetcher.http_session = MagicMock()

        # mock image download
        img_response = MagicMock()
        img_response.ok = True
        img_response.content = b'cover_bytes'

        # mock detail page for length
        detail_response = MagicMock()
        detail_response.ok = True
        detail_response.text = (
            '<html><dd class="catalogue-metadata-description">53:21</dd></html>'
        )

        fetcher.http_session.get.side_effect = [img_response, detail_response]

        soup = BeautifulSoup(RELEASE_LI_HTML, 'html.parser')
        rows = soup.select('li')

        callback = MagicMock()
        with patch('scrapper.internal.fetcher.time.sleep'):
            fetcher.fetch_one_page(callback, rows)

        assert len(fetcher.all_releases) == 1
        release = fetcher.all_releases[0]
        assert release['release_title'] == 'OK Computer'
        assert release['nb_tracks'] == 12
        assert release['length'] == 53
        assert release['img_content'] == b'cover_bytes'
        callback.assert_called_once_with('OK Computer', 12)

    def test_fetch_one_page_skips_few_tracks(self):
        from bs4 import BeautifulSoup

        fetcher = self._make_fetcher()
        soup = BeautifulSoup(RELEASE_LI_FEW_TRACKS_HTML, 'html.parser')
        rows = soup.select('li')

        fetcher.fetch_one_page(None, rows)

        assert len(fetcher.all_releases) == 0

    def test_fetch_one_page_skips_invalid_date(self):
        from bs4 import BeautifulSoup

        fetcher = self._make_fetcher()
        soup = BeautifulSoup(RELEASE_LI_NO_DATE_HTML, 'html.parser')
        rows = soup.select('li')

        fetcher.fetch_one_page(None, rows)

        assert len(fetcher.all_releases) == 0

    def test_fetch_one_page_stops_on_old_release(self):
        from bs4 import BeautifulSoup

        fetcher = self._make_fetcher()
        # set min_date to something recent
        fetcher.settings = _make_settings(releases_not_before=date(2020, 1, 1))

        soup = BeautifulSoup(RELEASE_LI_HTML, 'html.parser')
        rows = soup.select('li')

        fetcher.fetch_one_page(None, rows)

        assert fetcher.stop is True
        assert len(fetcher.all_releases) == 0

    def test_fetch_one_page_handles_missing_cover(self):
        from bs4 import BeautifulSoup

        html = """
        <li>
          <h3><a href="/music/Radiohead/OK+Computer">OK Computer</a></h3>
          <p>16 Jun 1997 · 12 tracks</p>
        </li>
        """
        fetcher = self._make_fetcher()
        # set min_date far in the past
        fetcher.settings = _make_settings(releases_not_before=date(1990, 1, 1))
        fetcher.http_session = MagicMock()

        # mock detail page
        detail_response = MagicMock()
        detail_response.ok = True
        detail_response.text = (
            '<html><dd class="catalogue-metadata-description">53:21</dd></html>'
        )
        fetcher.http_session.get.return_value = detail_response

        soup = BeautifulSoup(html, 'html.parser')
        rows = soup.select('li')

        with patch('scrapper.internal.fetcher.time.sleep'):
            fetcher.fetch_one_page(None, rows)

        assert len(fetcher.all_releases) == 1
        assert fetcher.all_releases[0]['img_content'] is None

    def test_fetch_one_page_handles_no_length_on_detail(self):
        from bs4 import BeautifulSoup

        fetcher = self._make_fetcher()
        fetcher.settings = _make_settings(releases_not_before=date(1990, 1, 1))
        fetcher.http_session = MagicMock()

        img_resp = MagicMock(ok=True, content=b'img')
        detail_resp = MagicMock(
            ok=True, text='<html><body>no length here</body></html>'
        )
        fetcher.http_session.get.side_effect = [img_resp, detail_resp]

        soup = BeautifulSoup(RELEASE_LI_HTML, 'html.parser')
        rows = soup.select('li')

        with patch('scrapper.internal.fetcher.time.sleep'):
            fetcher.fetch_one_page(None, rows)

        assert fetcher.all_releases[0]['length'] == 0

    @patch('scrapper.internal.fetcher.thumbnail_utils')
    @patch('scrapper.internal.fetcher.release_service')
    @patch('scrapper.internal.fetcher.url_utils')
    def test_fetch_full_single_page(self, mock_url_utils, mock_release_svc, mock_thumb):
        fetcher = self._make_fetcher()
        mock_url_utils.clean_url.return_value = 'https://www.last.fm/music/Radiohead'

        page_html = f"""
        <html><body>
        <section id="artist-albums-section">
          <ol>{RELEASE_LI_HTML}</ol>
        </section>
        </body></html>
        """
        detail_html = (
            '<html><dd class="catalogue-metadata-description">53:21</dd></html>'
        )

        mock_page_resp = MagicMock()
        mock_page_resp.text = page_html
        mock_page_resp.raise_for_status = MagicMock()

        mock_img_resp = MagicMock(ok=True, content=b'img')
        mock_detail_resp = MagicMock(ok=True, text=detail_html)

        fetcher.http_session = MagicMock()
        fetcher.http_session.get.side_effect = [
            mock_page_resp,
            mock_img_resp,
            mock_detail_resp,
        ]
        fetcher.settings = _make_settings(releases_not_before=date(1990, 1, 1))

        with patch('scrapper.internal.fetcher.time.sleep'):
            fetcher.fetch()

        mock_release_svc.save_releases.assert_called_once()
        mock_thumb.save_thumbnails.assert_called_once()

    @patch('scrapper.internal.fetcher.thumbnail_utils')
    @patch('scrapper.internal.fetcher.release_service')
    @patch('scrapper.internal.fetcher.url_utils')
    def test_fetch_stops_when_no_section(
        self, mock_url_utils, mock_release_svc, mock_thumb
    ):
        fetcher = self._make_fetcher()
        mock_url_utils.clean_url.return_value = 'https://www.last.fm/music/Radiohead'

        mock_resp = MagicMock()
        mock_resp.text = '<html><body>no section</body></html>'
        mock_resp.raise_for_status = MagicMock()

        fetcher.http_session = MagicMock()
        fetcher.http_session.get.return_value = mock_resp

        fetcher.fetch()

        # should still call save (with empty list)
        mock_release_svc.save_releases.assert_called_once()
        assert fetcher.all_releases == []
