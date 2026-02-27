import asyncio

import pytest
from textual.app import App, ComposeResult
from textual.widgets import Label

from pages.user.component.fetch import FetchAllReleases, FetchArtists, FetchReleases


class _App(App):
    def compose(self) -> ComposeResult:
        yield FetchArtists(id='artists')
        yield FetchReleases(id='releases')
        yield FetchAllReleases(id='all-releases')


class TestFetchArtists:
    def test_compute_log_line(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                fa = pilot.app.query_one('#artists', FetchArtists)
                return fa.compute_log_line(artist_name='Radiohead', nb_scrobbles=5000)

        result = asyncio.run(_test())
        assert result == '- Radiohead (5000 scrobbles)'

    def test_add_increments_counter(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                fa = pilot.app.query_one('#artists', FetchArtists)
                fa.add(artist_name='Radiohead', nb_scrobbles=5000)
                await pilot.pause()
                return pilot.app.query_one(f'#{fa.counter_id}', Label).content

        result = asyncio.run(_test())
        assert 'Artists fetched: 1' in result

    def test_reset_clears_counter(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                fa = pilot.app.query_one('#artists', FetchArtists)
                fa.add(artist_name='Radiohead', nb_scrobbles=5000)
                await pilot.pause()
                fa.reset()
                await pilot.pause()
                return pilot.app.query_one(f'#{fa.counter_id}', Label).content

        result = asyncio.run(_test())
        assert 'Artists fetched: 0' in result


class TestFetchReleases:
    def test_compute_log_line(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                fr = pilot.app.query_one('#releases', FetchReleases)
                return fr.compute_log_line(
                    artist_name='Radiohead',
                    release_title='OK Computer',
                    nb_tracks=12,
                )

        result = asyncio.run(_test())
        assert result == '- Radiohead : OK Computer (12 tracks)'

    def test_add_increments_counter(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                fr = pilot.app.query_one('#releases', FetchReleases)
                fr.add(
                    artist_name='Radiohead', release_title='OK Computer', nb_tracks=12
                )
                await pilot.pause()
                return pilot.app.query_one(f'#{fr.counter_id}', Label).content

        result = asyncio.run(_test())
        assert 'Releases fetched: 1' in result

    def test_reset_clears_counter(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                fr = pilot.app.query_one('#releases', FetchReleases)
                fr.add(
                    artist_name='Radiohead', release_title='OK Computer', nb_tracks=12
                )
                await pilot.pause()
                fr.reset()
                await pilot.pause()
                return pilot.app.query_one(f'#{fr.counter_id}', Label).content

        result = asyncio.run(_test())
        assert 'Releases fetched: 0' in result


class TestFetchAllReleases:
    def test_compute_log_line(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                far = pilot.app.query_one('#all-releases', FetchAllReleases)
                return far.compute_log_line(
                    artist_name='Radiohead',
                    release_title='OK Computer',
                    nb_tracks=12,
                )

        result = asyncio.run(_test())
        assert result == '- Radiohead : OK Computer (12 tracks)'

    def test_invalid_fetch_type_raises(self):
        from pages.user.component.fetch import BaseFetch

        with pytest.raises(ValueError, match='Invalid fetch type'):

            class _Bad(BaseFetch):
                def __init__(self):
                    super().__init__(id='bad', fetch_type='invalid_type')

                def compute_log_line(self, **kwargs):
                    return ''

            _Bad()
