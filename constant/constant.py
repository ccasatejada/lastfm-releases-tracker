from enum import Enum

from attr import dataclass

BASE_URL = 'https://www.last.fm'
LOGIN_PATH = 'https://www.last.fm/login'


class FetchTypeEnum(Enum):
    ARTIST = 'artist'
    RELEASE = 'release'
    ALL_RELEASES = 'all-releases'


@dataclass
class FetchEnum:
    key: str
    label: str


FETCH_TYPE: dict[str, FetchEnum] = {
    FetchTypeEnum.RELEASE.value: FetchEnum(
        key=FetchTypeEnum.RELEASE.value, label='Releases'
    ),
    FetchTypeEnum.ARTIST.value: FetchEnum(
        key=FetchTypeEnum.ARTIST.value, label='Artists'
    ),
    FetchTypeEnum.ALL_RELEASES.value: FetchEnum(
        key=FetchTypeEnum.ALL_RELEASES.value, label='All Releases'
    ),
}
