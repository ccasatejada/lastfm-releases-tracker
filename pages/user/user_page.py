from __future__ import annotations

from requests import HTTPError
from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal

from pages.user.component.add_user import AddUserBar
from pages.user.component.fetch_artists import FetchArtists
from pages.user.component.user_detail import UserDetailSection
from pages.user.component.user_list import UserListSection
from scrapper.scrapper import fetch_artists, init_user
from service import default_user_service, user_service


class UserPage(Horizontal):

    _env_username: str | None = None
    _env_password: str | None = None

    def compose(self) -> ComposeResult:
        yield UserListSection(id='user-list-section')
        yield UserDetailSection(id='user-detail-section')

    def on_mount(self) -> None:
        self._load_initial_users()

    @work(thread=True)
    def _load_initial_users(self) -> None:
        env_password, env_username = default_user_service.get_default_user()
        self._env_username = env_username
        self._env_password = env_password

        counts, users = user_service.get_users()
        list_section = self.query_one(UserListSection)

        if env_username:
            try:
                user = init_user(env_username)
                self.app.call_from_thread(list_section.add_user, user, counts.get(user.id, 0))
            except (ValueError, HTTPError):
                pass

        for user in users:
            self.app.call_from_thread(list_section.add_user, user, counts.get(user.id, 0))

    def on_add_user_bar_submitted(self, event: AddUserBar.Submitted) -> None:
        self._add_user(event.username)

    def on_user_list_section_selected(self, event: UserListSection.Selected) -> None:
        self._load_user_detail(event.user_id, event.lastfm_username)

    def on_user_list_section_delete_requested(self, event: UserListSection.DeleteRequested) -> None:
        self._delete_user(event.user_id)

    def on_user_detail_section_fetch_requested(self, event: UserDetailSection.FetchRequested) -> None:
        self._fetch_artists_work(event.lastfm_username, event.lastfm_password)

    def on_user_detail_section_settings_changed(self, event: UserDetailSection.SettingsChanged) -> None:
        self._save_settings(event.user_id, event.min_scrobbles, event.releases_not_before)

    @work(thread=True, exclusive=True)
    def _add_user(self, username: str) -> None:
        try:
            user = init_user(username)
            self.app.call_from_thread(self.query_one(UserListSection).add_user, user)
            self.notify(f'User {username} added')
        except (ValueError, HTTPError) as e:
            self.notify(str(e), severity='error')

    @work(thread=True, exclusive=True, group='user-detail')
    def _load_user_detail(self, user_id: int, lastfm_username: str) -> None:
        try:
            _, settings = user_service.get_user_with_settings(user_id)
            env_password = (
                self._env_password
                if self._env_username and lastfm_username == self._env_username
                else None
            )
            self.app.call_from_thread(
                self.query_one(UserDetailSection).show_user,
                lastfm_username, user_id, settings, env_password,
            )
        except Exception as e:
            self.notify(str(e), severity='error')

    @work(thread=True)
    def _delete_user(self, user_id: int) -> None:
        try:
            user_service.delete_user(user_id)
            self.notify('User deleted')
        except Exception as e:
            self.notify(str(e), severity='error')

    @work(thread=True)
    def _save_settings(self, user_id: int, min_scrobbles: int, releases_not_before) -> None:
        try:
            user_service.update_user_settings(user_id, min_scrobbles, releases_not_before)
            self.notify('Settings saved')
        except Exception as e:
            self.notify(str(e), severity='error')

    @work(thread=True, exclusive=True)
    def _fetch_artists_work(self, lastfm_username: str, lastfm_password: str) -> None:
        progress = self.query_one(FetchArtists)

        def on_artist_fetched(artist_name: str, nb_scrobbles: int) -> None:
            self.app.call_from_thread(progress.add_artist, artist_name, nb_scrobbles)

        try:
            fetch_artists(
                lastfm_username,
                lastfm_password,
                on_artist_fetched=on_artist_fetched,
            )
            self.notify(f'Artists fetched for {lastfm_username}')
        except Exception as e:
            self.notify(str(e), severity='error')
        finally:
            self.app.call_from_thread(self.query_one(UserDetailSection).set_fetching, False)
