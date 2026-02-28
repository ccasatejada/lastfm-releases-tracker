import os
from dataclasses import dataclass

from utils.type_utils import str_to_bool


@dataclass
class AppConfiguration:
    grab_artist_thumbnails: bool = str_to_bool(
        os.getenv('FF_GRAB_ARTIST_THUMBNAILS', 'True')
    )
    grab_release_covers: bool = str_to_bool(os.getenv('FF_GRAB_RELEASE_COVERS', 'True'))
