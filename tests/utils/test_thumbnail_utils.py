from pathlib import Path
from unittest.mock import MagicMock, patch

from utils.thumbnail_utils import (
    artists_thumbnails_dir,
    get_thumbnail,
    releases_thumbnails_dir,
    save_thumbnails,
)


class TestArtistsThumbnailsDir:
    def test_creates_and_returns_path(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = artists_thumbnails_dir()
        assert result.exists()
        assert result == Path('files/artists_thumbnails')

    def test_idempotent(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        artists_thumbnails_dir()
        artists_thumbnails_dir()  # should not raise


class TestReleasesThumbnailsDir:
    def test_creates_and_returns_path(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = releases_thumbnails_dir(42)
        assert result.exists()
        assert result == Path('files/releases_covers/42')

    def test_different_artist_ids(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        releases_thumbnails_dir(1)
        releases_thumbnails_dir(2)
        assert Path('files/releases_covers/1').exists()
        assert Path('files/releases_covers/2').exists()


class TestSaveThumbnails:
    def test_writes_file_for_valid_content(self, tmp_path):
        save_thumbnails([{'id': 1, 'img_content': b'image_data'}], tmp_path)
        assert (tmp_path / '1.jpg').read_bytes() == b'image_data'

    def test_skips_none_content(self, tmp_path):
        save_thumbnails([{'id': 2, 'img_content': None}], tmp_path)
        assert not (tmp_path / '2.jpg').exists()

    def test_handles_mixed_objects(self, tmp_path):
        objs = [
            {'id': 1, 'img_content': b'data1'},
            {'id': 2, 'img_content': None},
            {'id': 3, 'img_content': b'data3'},
        ]
        save_thumbnails(objs, tmp_path)
        assert (tmp_path / '1.jpg').read_bytes() == b'data1'
        assert not (tmp_path / '2.jpg').exists()
        assert (tmp_path / '3.jpg').read_bytes() == b'data3'

    def test_empty_list(self, tmp_path):
        save_thumbnails([], tmp_path)  # should not raise


class TestGetThumbnail:
    def test_calls_pixels(self, tmp_path):
        fake_img = tmp_path / 'test.jpg'
        fake_img.write_bytes(b'fake')
        mock_pixels = MagicMock()
        with patch(
            'utils.thumbnail_utils.Pixels.from_image_path', return_value=mock_pixels
        ) as mock_fn:
            result = get_thumbnail(fake_img, resize=(30, 30))
        mock_fn.assert_called_once_with(fake_img, resize=(30, 30))
        assert result is mock_pixels
