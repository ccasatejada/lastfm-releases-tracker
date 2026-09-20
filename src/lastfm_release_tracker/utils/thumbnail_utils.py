from collections.abc import Sequence
from pathlib import Path

import platformdirs
from rich_pixels import Pixels

CACHE_DIR = Path(platformdirs.user_cache_dir('lastfm-release-tracker'))


def get_thumbnail(img_path: Path, resize: tuple = None) -> Pixels:
    return Pixels.from_image_path(img_path, resize=resize)


def artists_thumbnails_dir() -> Path:
    thumbnails_dir = CACHE_DIR / 'artists_thumbnails'
    thumbnails_dir.mkdir(parents=True, exist_ok=True)
    return thumbnails_dir


def releases_thumbnails_dir(id_artist: int) -> Path:
    thumbnails_dir = CACHE_DIR / 'releases_covers' / str(id_artist)
    thumbnails_dir.mkdir(parents=True, exist_ok=True)
    return thumbnails_dir


def save_thumbnails(all_obj_to_save: Sequence[dict], thumbnails_dir: Path) -> None:
    for obj in all_obj_to_save:
        _id = obj['id']
        _content = obj['img_content']
        if not _content:
            continue
        (thumbnails_dir / f'{_id}.jpg').write_bytes(_content)
