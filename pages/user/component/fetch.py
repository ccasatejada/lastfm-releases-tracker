from abc import abstractmethod
from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Label, Log

from constant.constant import FETCH_TYPE, FetchEnum, FetchTypeEnum


class BaseFetch(Vertical):
    def __init__(self, id: str, fetch_type: str):
        super().__init__(id=id)
        if fetch_type not in FETCH_TYPE:
            raise ValueError(f'Invalid fetch type: {fetch_type}')
        self.fetch_enum: FetchEnum | None = FETCH_TYPE.get(fetch_type)
        self.counter_id = f'fetch-{self.fetch_enum.key}-counter'
        self.log_id = f'fetch-{self.fetch_enum.key}-log'

    def compose(self) -> ComposeResult:
        yield Label(f'{self.fetch_enum.label} fetched: 0', id=f'{self.counter_id}')
        yield Log(id=f'{self.log_id}', auto_scroll=True)

    def reset(self) -> None:
        self.query_one(f'#{self.counter_id}', Label).update(
            f'{self.fetch_enum.label} fetched: 0'
        )
        self.query_one(f'#{self.log_id}', Log).clear()

    @abstractmethod
    def compute_log_line(self, **kwargs: Any) -> str:
        return ''

    def add(self, **kwargs: Any) -> None:
        log = self.query_one(f'#{self.log_id}', Log)
        log_line = self.compute_log_line(**kwargs)
        log.write(log_line + '\n')
        self.query_one(f'#{self.counter_id}', Label).update(
            f'{self.fetch_enum.label} fetched: {log.line_count}'
        )


class FetchAllReleases(BaseFetch):
    def __init__(self, id: str):
        super().__init__(id=id, fetch_type=FetchTypeEnum.ALL_RELEASES.value)

    def compute_log_line(self, **kwargs: Any) -> str:
        return f'- {kwargs["artist_name"]} : {kwargs["release_title"]} ({kwargs["nb_tracks"]} tracks)'


class FetchReleases(BaseFetch):
    def __init__(self, id: str):
        super().__init__(id=id, fetch_type=FetchTypeEnum.RELEASE.value)

    def compute_log_line(self, **kwargs: Any) -> str:
        return f'- {kwargs["artist_name"]} : {kwargs["release_title"]} ({kwargs["nb_tracks"]} tracks)'


class FetchArtists(BaseFetch):
    def __init__(self, id: str):
        super().__init__(id=id, fetch_type=FetchTypeEnum.ARTIST.value)

    def compute_log_line(self, **kwargs: Any) -> str:
        return f'- {kwargs["artist_name"]} ({kwargs["nb_scrobbles"]} scrobbles)'
