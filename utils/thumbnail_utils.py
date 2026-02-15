from pathlib import Path

from rich_pixels import Pixels


def get_thumbnail(img_path, resize=None):
    return Pixels.from_image_path(img_path, resize=resize)

def get_thumbnails_dir() -> Path:
    thumbnails_dir = Path('files/artists_thumbnails')
    thumbnails_dir.mkdir(parents=True, exist_ok=True)
    return thumbnails_dir

def save_thumbnails(all_obj_to_save, thumbnails_dir: Path):
    for obj in all_obj_to_save:
        _id = obj['id']
        _content = obj['img_content']
        (thumbnails_dir / f'{_id}.jpg').write_bytes(_content)