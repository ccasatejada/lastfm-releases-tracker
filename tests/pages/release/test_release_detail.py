import asyncio
from datetime import date
from unittest.mock import patch

from textual.app import App, ComposeResult
from textual.widgets import DataTable, Static

from model.model import AppUser, AppUserRelease, Artist, Release
from pages.release.component.release_detail import ReleaseDetailSection


def _make_release(
    id=1,
    title='OK Computer',
    release_date=date(1997, 6, 16),
    length=3180,
    nb_tracks=12,
    url='https://example.com',
    id_artist=10,
) -> Release:
    return Release(
        id=id,
        release_title=title,
        release_date=release_date,
        length=length,
        nb_tracks=nb_tracks,
        release_url=url,
        id_artist=id_artist,
    )


def _make_artist(id=10, name='Radiohead') -> Artist:
    return Artist(id=id, artist_name=name)


def _make_user_release(
    id_user=1, id_release=1, ignored=False, username='alice'
) -> AppUserRelease:
    user = AppUser(id=id_user, lastfm_username=username)
    ur = AppUserRelease(id_user=id_user, id_release=id_release, ignored=ignored)
    ur.user = user
    return ur


class _App(App):
    def compose(self) -> ComposeResult:
        yield ReleaseDetailSection()


class TestReleaseDetailSection:
    def test_shows_placeholder_on_initial_compose(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                placeholder = pilot.app.query_one('#detail-placeholder', Static)
                return placeholder.content

        result = asyncio.run(_test())
        assert 'Select a release' in result

    def test_show_release_displays_artist_and_title(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                section = pilot.app.query_one(ReleaseDetailSection)
                await section.show_release(_make_release(), _make_artist(), [])
                await pilot.pause()
                artist_text = pilot.app.query_one('#release-artist').content
                title_text = pilot.app.query_one('#release-title').content
                return artist_text, title_text

        artist_text, title_text = asyncio.run(_test())
        assert 'Radiohead' in artist_text
        assert 'OK Computer' in title_text

    def test_show_release_displays_no_cover_placeholder_when_no_image(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                section = pilot.app.query_one(ReleaseDetailSection)
                release = _make_release(id=9999, id_artist=9999)  # non-existent file
                await section.show_release(release, _make_artist(), [])
                await pilot.pause()
                return pilot.app.query_one('#no-cover-placeholder', Static).content

        result = asyncio.run(_test())
        assert 'No cover' in result

    def test_show_release_with_url_shows_open_button(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                section = pilot.app.query_one(ReleaseDetailSection)
                await section.show_release(
                    _make_release(url='https://example.com'), _make_artist(), []
                )
                await pilot.pause()
                return len(pilot.app.query('#open-url-button'))

        assert asyncio.run(_test()) == 1

    def test_show_release_without_url_hides_open_button(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                section = pilot.app.query_one(ReleaseDetailSection)
                await section.show_release(_make_release(url=None), _make_artist(), [])
                await pilot.pause()
                return len(pilot.app.query('#open-url-button'))

        assert asyncio.run(_test()) == 0

    def test_show_release_populates_user_table(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                section = pilot.app.query_one(ReleaseDetailSection)
                urs = [
                    _make_user_release(id_user=1, username='alice', ignored=False),
                    _make_user_release(id_user=2, username='bob', ignored=True),
                ]
                await section.show_release(_make_release(), _make_artist(), urs)
                await pilot.pause()
                return pilot.app.query_one('#user-release-table', DataTable).row_count

        assert asyncio.run(_test()) == 2

    def test_show_release_ignored_column_shows_true_false(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                section = pilot.app.query_one(ReleaseDetailSection)
                urs = [
                    _make_user_release(id_user=1, username='alice', ignored=True),
                    _make_user_release(id_user=2, username='bob', ignored=False),
                ]
                await section.show_release(_make_release(), _make_artist(), urs)
                await pilot.pause()
                table = pilot.app.query_one('#user-release-table', DataTable)
                rows = [table.get_row_at(i) for i in range(table.row_count)]
                return rows

        rows = asyncio.run(_test())
        ignored_values = [str(r[1]) for r in rows]
        assert 'True' in ignored_values
        assert 'False' in ignored_values

    def test_open_button_opens_url_in_browser(self):
        opened = []

        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                section = pilot.app.query_one(ReleaseDetailSection)
                await section.show_release(
                    _make_release(url='https://example.com'), _make_artist(), []
                )
                await pilot.pause()
                with patch(
                    'pages.release.component.release_detail.webbrowser.open_new_tab'
                ) as mock_open:
                    await pilot.click('#open-url-button')
                    await pilot.pause()
                    opened.extend(mock_open.call_args_list)

        asyncio.run(_test())
        assert len(opened) == 1
        assert opened[0].args[0] == 'https://example.com'

    def test_show_release_updates_current_url(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                section = pilot.app.query_one(ReleaseDetailSection)
                await section.show_release(
                    _make_release(url='https://myurl.com'), _make_artist(), []
                )
                return section._current_url

        assert asyncio.run(_test()) == 'https://myurl.com'
