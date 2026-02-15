from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.containers import Vertical

from pages.user.component.add_user import AddUserBar
from pages.user.component.fetch_artists import FetchArtists
from pages.user.component.user_section import UserSection
from scrapper.scrapper import fetch_artists, init_user
from service import default_user_service, user_service


class UserPage(Vertical):

    def compose(self) -> ComposeResult:
        yield AddUserBar(id='add-user-bar')
        yield UserSection(id='user-section')

    def on_mount(self) -> None:
        self._load_initial_users()

    @work(thread=True)
    def _load_initial_users(self) -> None:
        section = self.query_one(UserSection)

        env_password, env_username = default_user_service.get_default_user()
        counts, users = user_service.get_users()

        self._add_default_user(counts, env_password, env_username, section)

        for user in users:
            section.add_user(user, nb_artists=counts.get(user.id, 0))

    def _add_default_user(
        self,
        counts: dict,
        env_password: str | None,
        env_username: str | None,
        section: UserSection,
    ) -> None:
        if not env_username:
            return
        try:
            user = init_user(env_username)
            section.add_user(user, nb_artists=counts.get(user.id, 0))
        except Exception:
            pass

        if env_password:
            section.set_env_credentials(env_username, env_password)

    def on_add_user_bar_submitted(self, event: AddUserBar.Submitted) -> None:
        self._add_user(event.username)

    def on_user_section_fetch_requested(self, event: UserSection.FetchRequested) -> None:
        self._fetch_artists_work(event.lastfm_username, event.lastfm_password)

    def on_user_section_delete_requested(self, event: UserSection.DeleteRequested) -> None:
        self._delete_user(event.user_id)

    def on_user_section_edit_saved(self, event: UserSection.EditSaved) -> None:
        self._update_user(event.user_id, event.new_username)

    @work(thread=True, exclusive=True)
    def _add_user(self, username: str) -> None:
        try:
            user = init_user(username)
            self.query_one(UserSection).add_user(user)
            self.notify(f'User {username} added')
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
    def _update_user(self, user_id: int, new_username: str) -> None:
        try:
            user_service.update_user(new_username, user_id)
            self.notify(f'Username updated to {new_username}')
        except Exception as e:
            self.notify(str(e), severity='error')

    @work(thread=True, exclusive=True)
    def _fetch_artists_work(self, lastfm_username: str, lastfm_password: str) -> None:
        count = 0
        progress = self.query_one(FetchArtists)

        def on_artist_fetched(artist_name: str, nb_scrobbles: int) -> None:
            nonlocal count
            count += 1
            self.app.call_from_thread(progress.add_artist, artist_name, nb_scrobbles, count)

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
            self.query_one(UserSection).set_fetching(False)
