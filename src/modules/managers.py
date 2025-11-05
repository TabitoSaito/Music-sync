import time
from typing import Any
import random

from bs4 import BeautifulSoup as bs
import pyautogui

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.remote.webelement import WebElement

from ytmusicapi import YTMusic

from utils.enums import ReturnCode
from utils.custom_types import Song
from utils.globals import SPOTIFY, AMAZONE_EMAIL, AMAZONE_PASSWORD, YOUTUBE_USER_ID
import utils.helper as helper


class SpotifyManager(spotipy.Spotify):
    def __init__(self, user_id: str, model=None, scaler=None):
        """manages Spotify playlists with spotify api

        Args:
            user_id (str): id of user to manage
            model (_type_, optional): machine learning model to use for matching. If none, loads basis model. Defaults to None.
            scaler (_type_, optional): scaler to preprocess data for model. If none, loads basis scaler. Defaults to None.
        """
        super().__init__(
            auth_manager=SpotifyOAuth(
                client_id=SPOTIFY["CLIENT_ID"],
                client_secret=SPOTIFY["CLIENT_SECRET"],
                redirect_uri=SPOTIFY["REDIRECT_URI"],
                scope=SPOTIFY["SCOPE"],
            )
        )
        self.user_id = user_id
        self.model = model
        self.scaler = scaler
        self.cur_playlist = []

    def get_user_playlists(self) -> Any | None:
        response = self.current_user_playlists()
        if response:
            return response["items"]

    def get_songs_from_playlist(
        self, playlist_name: str
    ) -> tuple[list[Song], str] | None:
        """fetches all songs in playlist

        Args:
            playlist_name (str): name of playlist to fetch songs from

        Returns:
            tuple[list[Song], str] | None: list of songs with author and playlist id or none if playlist name not found
        """
        playlists = self.get_user_playlists()
        self.cur_playlist = []

        for playlist in playlists:
            print(playlist["name"])
            if playlist["name"].lower() == playlist_name.lower():
                playlist_id = playlist["id"]
                songs = self.playlist(playlist_id)["tracks"]["items"]
                for song in songs:
                    song_name = song["track"]["name"]
                    song_artist = song["track"]["artists"][0]["name"]
                    self.cur_playlist.append((song_name.lower(), song_artist.lower()))
                return self.cur_playlist, playlist_id
        return None

    def search_song(self, name: str, artist: str | None = None) -> Any | None:
        search = f"{name} by {artist}" if artist else name
        result = self.search(search, type="track")
        if result:
            return result["tracks"]["items"]

    def get_similar_songs_data(
        self, name: str, artist: str | None = None, max_items: int = 5, rand: bool = False
    ) -> tuple[ReturnCode, list[Song]]:
        songs = self.search_song(name, artist)
        if not songs:
            return ReturnCode.NONE_FOUND, []
        if len(songs) > max_items:
            if rand:
                songs = random.sample(songs, 5)
            else:
                songs = songs[:5]
        return ReturnCode.FOUND, [
            (item["name"], item["artists"][0]["name"]) for item in songs
        ]

    def update_playlist_str_comparison(
        self, searched_song: Song, found_songs: list[Any], playlist_id: str
    ) -> ReturnCode:
        """try to update playlist using string comparison

        Args:
            searched_song (Song): song to add
            found_songs (list[Any]): possible matches returned by Spotify search
            playlist_id (str): id of playlist to update

        Returns:
            Return_Code: Enum containing result of update
        """
        for found_song in found_songs:
            if found_song["name"].lower() == searched_song[0].lower():
                # check if already in playlist
                if found_song["name"].lower() in [
                    song[0].lower() for song in self.cur_playlist
                ]:
                    return ReturnCode.ALREADY_IN_PLAYLIST
                else:
                    # check if artist is correct
                    artists = [
                        artist["name"].lower() for artist in found_song["artists"]
                    ]
                    if searched_song[1].lower() in artists:
                        # add to playlist
                        song_uri: str = found_song["uri"]
                        self.playlist_add_items(playlist_id, [song_uri])
                        return ReturnCode.MATCH
        return ReturnCode.NO_MATCH

    def update_playlist_machine_learning(
        self,
        searched_song: Song,
        found_songs: list[Any],
        playlist_id: str,
        confidence: float = 0.7,
        max_items: int = 5,
    ) -> ReturnCode:
        """try to update playlist using a machine learning model

        Args:
            searched_song (Song): song to add
            found_songs (list[Any]): possible matches returned by Spotify search
            playlist_id (str): id of playlist to update
            confidence (float, optional): minimum match-probability to consider a match. Defaults to 0.7.
            max_items (int): maximum found songs to compare against. Defaults to 5.

        Returns:
            Return_Code: Enum containing result of update
        """
        if len(found_songs) > max_items:
            found_songs = found_songs[:max_items]

        found_songs = found_songs[::-1]

        # calculate probability for match for all found songs
        found_songs_dict = {
            helper.get_song_match_proba(
                name1=item["name"],
                name2=searched_song[0],
                model=self.model,
                scaler=self.scaler,
            ): item
            for item in found_songs
        }

        while len(found_songs_dict) > 0:
            best_match = max(found_songs_dict)
            best_match_name = found_songs_dict[best_match]["name"]

            if best_match >= confidence:
                # check if already in playlist
                if best_match_name.lower() in [
                    song[0].lower() for song in self.cur_playlist
                ]:
                    return ReturnCode.ALREADY_IN_PLAYLIST

                # check if artist is correct
                artists = [
                    artist["name"].lower()
                    for artist in found_songs_dict[best_match]["artists"]
                ]
                if searched_song[1].lower() in artists:
                    # add to playlist
                    song_uri: str = found_songs_dict[best_match]["uri"]
                    self.playlist_add_items(playlist_id, [song_uri])
                    return ReturnCode.MATCH

            del found_songs_dict[best_match]
        return ReturnCode.NO_MATCH

    def update_playlist(self, playlist_id: str, songs: list[Song]):
        """update playlist with given songs. Avoids duplicates.

        Args:
            playlist_id (str): id of playlist to update
            songs (list[Song]): list containing song names and artists
        """
        print("updating Spotify")
        for song in songs:
            tracks = self.search_song(song[0])

            if tracks is None:
                print(f"No search result for: {song}")
                continue

            # try to match result names to song name with string comparison
            match self.update_playlist_str_comparison(song, tracks, playlist_id):
                case ReturnCode.MATCH:
                    print(f"added: {song}")
                    continue
                case ReturnCode.NO_MATCH:
                    pass
                case ReturnCode.ALREADY_IN_PLAYLIST:
                    print(f"already in playlist: {song}")
                    continue

            # try to match result names to song name with machine learning model
            match self.update_playlist_machine_learning(song, tracks, playlist_id):
                case ReturnCode.MATCH:
                    print(f"added: {song}")
                    continue
                case ReturnCode.NO_MATCH:
                    print(f"no match found: {song}")
                case ReturnCode.ALREADY_IN_PLAYLIST:
                    print(f"already in playlist: {song}")
                    continue


class AmazonMusicManager:
    def __init__(self, email: str, password: str, model=None, scalar=None):
        """manages Amazon Music playlists by scraping Webversion

        Args:
            email (str): email to log into Amazone Music
            password (str): password to log into Amazone Music
            model (_type_, optional): machine learning model to use for matching. If none, loads basis model. Defaults to None.
            scaler (_type_, optional): scaler to preprocess data for model. If none, loads basis scaler. Defaults to None.
        """
        self.email = email
        self.password = password
        self.driver = None
        self.url = "https://music.amazon.de"
        self.short_delay = 1
        self.long_delay = 4
        self.cur_playlist: list[Song] = []
        self.model = model
        self.scaler = scalar

    def start_driver(self):
        options = Options()
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_window_size(1000, 800)

    def close_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def login(self):
        """login to Amazone Music"""
        self.driver.get(f"{self.url}/forceSignIn?useHorizonte=true")

        time.sleep(self.short_delay)

        # enter Email
        WebDriverWait(self.driver, self.long_delay).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#ap_email"))
        ).send_keys(self.email)

        time.sleep(self.short_delay)

        WebDriverWait(self.driver, self.long_delay).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#continue"))
        ).click()

        time.sleep(self.short_delay)

        # close popup
        pyautogui.press("enter")

        time.sleep(self.short_delay)

        # enter password
        WebDriverWait(self.driver, self.long_delay).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#ap_password"))
        ).send_keys(self.password)

        time.sleep(self.short_delay)

        # process login
        WebDriverWait(self.driver, self.long_delay).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#signInSubmit"))
        ).click()

        # special login events
        try:
            WebDriverWait(self.driver, self.long_delay).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#otp_submit_form"))
            )
            print("Enter Code in Webbrowser")
            self.wait_for_homepage()
        except TimeoutException:
            pass

        try:
            WebDriverWait(self.driver, self.long_delay).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#channelDetailsWithImprovedLayout")
                )
            )
            print(
                "You need to allow access to Amazon Music through your phone or an other device."
            )
            self.wait_for_homepage()
        except TimeoutException:
            pass

        time.sleep(self.short_delay)

    def wait_for_homepage(self):
        running = True
        while running:
            try:
                search_element = WebDriverWait(self.driver, self.long_delay).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "#navbarSearchInput")
                    )
                )
                running = False
            except TimeoutException:
                continue

    def get_playlist(self, playlist_name: str) -> bs:
        """fetch playlist by name

        Args:
            playlist_name (str): name of playlist to fetch

        Returns:
            bs: BeautifulSoup of playlist contents
        """
        self.driver.get(f"{self.url}/my/playlists")

        time.sleep(self.long_delay)

        # find playlist by name
        element = WebDriverWait(self.driver, self.long_delay).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f"//*[translate(@primary-text, 'ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜ', 'abcdefghijklmnopqrstuvwxyzäöü')='{playlist_name.lower()}']",
                )
            )
        )

        playlist_url = element.get_attribute("primary-href")
        soup = helper.zoom_and_scrape(driver=self.driver, url=self.url + playlist_url)
        return soup

    def get_songs_from_playlist(self, playlist_name: str) -> list[Song] | None:
        """fetch songs from playlist

        Args:
            playlist_name (str): name of playlist to fetch from

        Returns:
            list[Song] | None: songs and artists or none if playlist is not found
        """
        self.cur_playlist = []
        soup = self.get_playlist(playlist_name)
        rows = soup.select("music-image-row[data-key]")
        for song in rows:
            song_name = song["primary-text"]
            song_artist = song["secondary-text-1"]
            self.cur_playlist.append((song_name.lower(), song_artist.lower()))
        return self.cur_playlist

    def search_song(self, name: str, artist: str | None = None):
        """search for song on Amazone Music

        Args:
            name (str): name to search for
            artist (str): artist to search with
        """
        search_element = WebDriverWait(self.driver, self.long_delay).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#navbarSearchInput"))
        )

        # clear searchfield and enter song and artist
        try:
            search_element.send_keys(Keys.CONTROL, "a")
            search_element.send_keys(Keys.DELETE)
            search = f"{name} by {artist}" if artist else name
            search_element.send_keys(search)
            search_element.send_keys(Keys.ENTER)
        except WebDriverException as e:
            print(f"ERROR at: {name, artist}\n{e}")
        time.sleep(self.long_delay)

    def match_song_str_comparison(
        self, searched_song: Song, song_group_element: WebElement
    ) -> tuple[ReturnCode, WebElement] | tuple[ReturnCode, None]:
        """try to match song with a group of song elements using string comparison

        Args:
            searched_song (Song): song to try to match
            song_group_element (WebElement): element containing found songs

        Returns:
            WebElement | None: match result and element containing song if match is found
        """
        song_name = helper.escape_xpath_string(searched_song[0].lower())
        song_artist = helper.escape_xpath_string(searched_song[1].lower())

        try:
            element = WebDriverWait(song_group_element, self.long_delay).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        f""".//*[translate(@primary-text, 'ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜ', 'abcdefghijklmnopqrstuvwxyzäöü')={song_name}
                    and contains(translate(@secondary-text, 'ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜ','abcdefghijklmnopqrstuvwxyzäöü'), {song_artist})]""",
                    )
                )
            )
            return ReturnCode.MATCH, element

        except TimeoutException:
            return ReturnCode.NO_MATCH, None

    def get_similar_songs(
        self, song_group_element: WebElement, max_items: int = 5, rand: bool = False
    ) -> tuple[ReturnCode, list[WebElement]]:
        """extracts similar songs from webelement containing songs

        Args:
            song_group_element (WebElement): webelement containing songs
            max_items (int, optional): maximum number of output items. Defaults to 5.
            rand (bool, optional): if True a random sample from the webelement is chosen. Defaults to False.

        Returns:
            tuple[ReturnCode, list[WebElement]]: list of webelements containing one song each
        """
        try:
            elements = WebDriverWait(song_group_element, self.long_delay).until(
                EC.presence_of_all_elements_located(
                    (By.TAG_NAME, "music-horizontal-item")
                )
            )
        except TimeoutException:
            return ReturnCode.NONE_FOUND, []

        if len(elements) > max_items:
            if rand:
                elements = random.sample(elements, max_items)
            else:
                elements = elements[:max_items]
        return ReturnCode.FOUND, elements

    def get_similar_songs_data(
        self, name: str, artist: str | None = None, max_items: int = 5, rand: bool = False
    ) -> tuple[ReturnCode, list[Song]]:
        """fetch songs from platform by name

        Args:
            name (str): name of song to search for
            artist (str | None, optional): artist name to search with. Defaults to None.
            max_items (int, optional): maximum number of output items. Defaults to 5.
            rand (bool, optional): if True a random sample from the found songs is chosen. Defaults to False.

        Returns:
            tuple[ReturnCode, list[Song]]: list of song elements containing name and artist of found songs
        """        """"""
        self.search_song(name, artist)

        try:
            song_group_element = WebDriverWait(self.driver, self.long_delay).until(
                EC.presence_of_element_located(
                    (By.XPATH, """//music-shoveler[@primary-text='Songs']""")
                )
            )
        except TimeoutException:
            return ReturnCode.NONE_FOUND, []

        response = self.get_similar_songs(song_group_element, max_items, rand=rand)

        match response[0]:
            case ReturnCode.FOUND:
                song_list = []
                for element in response[1]:
                    try:
                        song = str(element.get_attribute("primary-text"))
                    except AttributeError:
                        continue
                    try:
                        artist = str(element.get_attribute("secondary-text"))
                    except AttributeError:
                        continue
                    song_list.append((song, artist))
                return ReturnCode.FOUND, song_list
            case ReturnCode.NONE_FOUND:
                return ReturnCode.NONE_FOUND, []
            case _:
                return ReturnCode.NONE_FOUND, []

    def match_song_machine_learning(
        self,
        searched_song: Song,
        song_group_element: WebElement,
        confidence: float = 0.7,
        max_items: int = 5,
    ) -> tuple[ReturnCode, WebElement] | tuple[ReturnCode, None]:
        """try to match song with a group of song elements using a machine learning model

        Args:
            searched_song (Song): song to try to match.
            song_group_element (WebElement): element containing found songs.
            confidence (float, optional): minimum match-probability to consider a match. Defaults to 0.7.
            max_items (int): maximum found songs to compare against. Defaults to 5.

        Returns:
            tuple[Return_Code, WebElement] | tuple[Return_Code, None]: match result and element containing song if match is found.
        """
        response = self.get_similar_songs(song_group_element)
        match response[0]:
            case ReturnCode.FOUND:
                elements = response[1][::-1]
            case ReturnCode.NONE_FOUND:
                return ReturnCode.NONE_FOUND, None

        # calculate the match probability of all results
        found_songs_dict = {
            helper.get_song_match_proba(
                name1=str(item.get_attribute("primary-text")),
                name2=searched_song[0],
                model=self.model,
                scaler=self.scaler,
            ): item
            for item in elements
        }

        while len(found_songs_dict) > 0:
            # find best match over confidence and check if already in playlist.
            best_match = max(found_songs_dict)
            best_match_name = found_songs_dict[best_match].get_attribute("primary-text")
            if best_match >= confidence:
                if best_match_name.lower() in [song[0] for song in self.cur_playlist]:
                    return ReturnCode.ALREADY_IN_PLAYLIST, None

            best_element = found_songs_dict[best_match]
            if (
                searched_song[1].lower()
                in best_element.get_attribute("secondary-text").lower()
            ):
                return ReturnCode.MATCH, best_element

            del found_songs_dict[best_match]

        return ReturnCode.NO_MATCH, None

    def add_song_to_playlist(
        self, song_element: WebElement, playlist_name: str
    ) -> ReturnCode:
        """add song to playlist by navigation the UI

        Args:
            song_element (WebElement): element containing the song
            playlist_name (str): name of playlist to add song to
        """
        song_element.find_element(
            By.XPATH,
            """.//*[translate(@icon-name, "ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜ", "abcdefghijklmnopqrstuvwxyzäöü")="more"]""",
        ).click()

        time.sleep(self.short_delay)

        WebDriverWait(self.driver, self.long_delay).until(
            EC.presence_of_element_located((By.TAG_NAME, "music-list-item"))
        ).click()

        playlist_element = WebDriverWait(self.driver, self.long_delay).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f"//*[translate(@primary-text, 'ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜ', 'abcdefghijklmnopqrstuvwxyzäöü')='{playlist_name.lower()}']",
                )
            )
        )

        playlist_element.click()

        # handle edge case
        try:
            button_element = WebDriverWait(self.driver, self.long_delay).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#primaryDialogButton2")
                )
            )

            button_element.click()
            time.sleep(self.short_delay)
            return ReturnCode.ALREADY_IN_PLAYLIST
        except TimeoutException:
            time.sleep(self.short_delay)
            return ReturnCode.MATCH

    def update_playlist(self, playlist_name: str, songs: list[Song]):
        """update playlist with given songs. Avoid duplicates.

        Args:
            playlist_name (str): name of playlist to update
            songs (list[tuple[str, str]]): list containing song names and artists

        """
        print("update Amazon Music")
        self.driver.get(f"{self.url}/search")

        time.sleep(self.long_delay)

        for song in songs:
            self.search_song(song[0], song[1])

            try:
                song_group_element = WebDriverWait(self.driver, self.long_delay).until(
                    EC.presence_of_element_located(
                        (By.XPATH, """//music-shoveler[@primary-text='Songs']""")
                    )
                )
            except TimeoutException:
                print(f"no songs found for {song}")
                continue

            result, element = self.match_song_str_comparison(song, song_group_element)
            match result:
                case ReturnCode.MATCH:
                    result = self.add_song_to_playlist(element, playlist_name)
                    match result:
                        case ReturnCode.ALREADY_IN_PLAYLIST:
                            print(f"already in playlist: {song}")
                        case ReturnCode.MATCH:
                            print(f"added: {song}")
                    continue
                case ReturnCode.NO_MATCH:
                    pass

            result, element = self.match_song_machine_learning(song, song_group_element)
            match result:
                case ReturnCode.MATCH:
                    result = self.add_song_to_playlist(element, playlist_name)
                    match result:
                        case ReturnCode.ALREADY_IN_PLAYLIST:
                            print(f"already in playlist: {song}")
                        case ReturnCode.MATCH:
                            print(f"added: {song}")
                    continue
                case ReturnCode.NO_MATCH:
                    print(f"no match found: {song}")
                case ReturnCode.ALREADY_IN_PLAYLIST:
                    print(f"already in playlist: {song}")
                    continue


class YoutubeMusicManager(YTMusic):
    def __init__(self, user_id: str, model=None, scalar=None):
        """manages Youtube Music playlists with Youtube Music api

        Args:
            user_id (str): id of user to manage
            model (_type_, optional): machine learning model to use for matching. If none, loads basis model. Defaults to None.
            scaler (_type_, optional): scaler to preprocess data for model. If none, loads basis scaler. Defaults to None.
        """
        super().__init__("browser.json")
        self.user_id = user_id
        self.model = model
        self.scaler = scalar
        self.cur_playlist = []

    def get_songs_from_playlist(
        self, playlist_name: str
    ) -> tuple[list[Song], str] | None:
        """fetches all songs in playlist

        Args:
            playlist_name (str): name of playlist to fetch songs from

        Returns:
            tuple[list[Song], str] | None: list of songs with author and playlist id or none if playlist name not found
        """
        playlists = self.get_user(self.user_id)["playlists"]["results"]
        self.cur_playlist = []

        for playlist in playlists:
            if playlist["title"].lower() == playlist_name.lower():
                playlist_id = playlist["playlistId"]

                songs = self.get_playlist(playlist_id)["tracks"]
                for song in songs:
                    song_name = song["title"]
                    song_artist = song["artists"][0]["name"]
                    self.cur_playlist.append((song_name.lower(), song_artist.lower()))
                return self.cur_playlist, playlist_id
        return None

    def search_song(self, name: str, artist: str | None = None) -> Any | None:
        search = f"{name} by {artist}" if artist else name
        result = self.search(search, filter="songs")
        return result

    def get_similar_songs_data(
        self, name: str, artist: str | None = None, max_items: int = 5, rand: bool = False
    ) -> tuple[ReturnCode, list[Song]]:
        """fetch songs from platform by name

        Args:
            name (str): name of song to search for
            artist (str | None, optional): artist name to search with. Defaults to None.
            max_items (int, optional): maximum number of output items. Defaults to 5.
            rand (bool, optional): if True a random sample from the found songs is chosen. Defaults to False.

        Returns:
            tuple[ReturnCode, list[Song]]: list of song elements containing name and artist of found songs
        """
        songs = self.search_song(name, artist)
        if not songs:
            return ReturnCode.NONE_FOUND, []
        if len(songs) > max_items:
            if rand:
                songs = random.sample(songs, 5)
            else:
                songs = songs[:5]
        return ReturnCode.FOUND, [
            (item["title"], item["artists"][0]["name"]) for item in songs
        ]

    def update_playlist_str_comparison(
        self, searched_song: Song, found_songs: list[Any], playlist_id: str
    ) -> ReturnCode:
        """try to update playlist using string comparison

        Args:
            searched_song (Song): song to add
            found_songs (list[Any]): possible matches returned by Spotify search
            playlist_id (str): id of playlist to update

        Returns:
            Return_Code: Enum containing result of update
        """
        for found_song in found_songs:
            if found_song["title"].lower() == searched_song[0].lower():
                # check if already in playlist
                if found_song["title"].lower() in [
                    song[0].lower() for song in self.cur_playlist
                ]:
                    return ReturnCode.ALREADY_IN_PLAYLIST
                else:
                    # check if artist is correct
                    artists = [
                        artist["name"].lower() for artist in found_song["artists"]
                    ]
                    if searched_song[1].lower() in artists:
                        # add to playlist
                        song_id: str = found_song["videoId"]
                        self.add_playlist_items(playlist_id, [song_id])
                        return ReturnCode.MATCH
        return ReturnCode.NO_MATCH

    def update_playlist_machine_learning(
        self,
        searched_song: Song,
        found_songs: list[Any],
        playlist_id: str,
        confidence: float = 0.7,
        max_items: int = 5,
    ) -> ReturnCode:
        """try to update playlist using a machine learning model

        Args:
            searched_song (Song): song to add
            found_songs (list[Any]): possible matches returned by Spotify search
            playlist_id (str): id of playlist to update
            confidence (float, optional): minimum match-probability to consider a match. Defaults to 0.7.
            max_items (int): maximum found songs to compare against. Defaults to 5.

        Returns:
            Return_Code: Enum containing result of update
        """
        if len(found_songs) > max_items:
            found_songs = found_songs[:max_items]

        found_songs = found_songs[::-1]

        # calculate probability for match for all found songs
        found_songs_dict = {
            helper.get_song_match_proba(
                name1=item["title"],
                name2=searched_song[0],
                model=self.model,
                scaler=self.scaler,
            ): item
            for item in found_songs
        }

        while len(found_songs_dict) > 0:
            best_match = max(found_songs_dict)
            best_match_name = found_songs_dict[best_match]["title"]

            if best_match >= confidence:
                # check if already in playlist
                if best_match_name.lower() in [
                    song[0].lower() for song in self.cur_playlist
                ]:
                    return ReturnCode.ALREADY_IN_PLAYLIST

                # check if artist is correct
                artists = [
                    artist["name"].lower()
                    for artist in found_songs_dict[best_match]["artists"]
                ]
                if searched_song[1].lower() in artists:
                    # add to playlist
                    song_id: str = found_songs_dict[best_match]["videoId"]
                    self.add_playlist_items(playlist_id, [song_id])
                    return ReturnCode.MATCH

            del found_songs_dict[best_match]
        return ReturnCode.NO_MATCH

    def update_playlist(self, playlist_id: str, songs: list[Song]):
        """update playlist with given songs. Avoids duplicates.

        Args:
            playlist_id (str): id of playlist to update
            songs (list[Song]): list containing song names and artists
        """
        print("updating Youtube Music")
        for song in songs:
            tracks = self.search_song(song[0])

            if tracks is None:
                print(f"No search result for: {song}")
                continue

            # try to match result names to song name with string comparison
            match self.update_playlist_str_comparison(song, tracks, playlist_id):
                case ReturnCode.MATCH:
                    print(f"added: {song}")
                    continue
                case ReturnCode.NO_MATCH:
                    pass
                case ReturnCode.ALREADY_IN_PLAYLIST:
                    print(f"already in playlist: {song}")
                    continue

            # try to match result names to song name with machine learning model
            match self.update_playlist_machine_learning(song, tracks, playlist_id):
                case ReturnCode.MATCH:
                    print(f"added: {song}")
                    continue
                case ReturnCode.NO_MATCH:
                    print(f"no match found: {song}")
                case ReturnCode.ALREADY_IN_PLAYLIST:
                    print(f"already in playlist: {song}")
                    continue


class Manager:
    def __init__(self) -> None:
        self.sm = SpotifyManager(SPOTIFY["USER_ID"])
        self.amm = AmazonMusicManager(email=AMAZONE_EMAIL, password=AMAZONE_PASSWORD)
        self.ytm = YoutubeMusicManager(YOUTUBE_USER_ID)
