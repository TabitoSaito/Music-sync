from modules.managers import Manager
from utils.enums import ReturnCode


class Sync:
    def __init__(self):
        """main handler for synchronizing playlists"""
        self.manager = Manager()

    def sync_spotify_amazon(self, playlist_name: str) -> ReturnCode:
        """synchronies Spotify and Amazone Music Playlist by name

        Args:
            playlist_name (str): Name of playlist to synchronies
        """
        result = self.manager.sm.get_songs_from_playlist(playlist_name)
        if not result:
            return ReturnCode.NO_PLAYLIST_FOUND
        sp_songs, sp_id = result

        self.manager.amm.start_driver()
        self.manager.amm.login()
        result = self.manager.amm.get_songs_from_playlist(playlist_name)
        if not result:
            return ReturnCode.NO_PLAYLIST_FOUND
        am_songs = result

        sp_additions = [
            song for song in am_songs if song[0] not in [song2[0] for song2 in sp_songs]
        ]
        am_additions = [
            song for song in sp_songs if song[0] not in [song2[0] for song2 in am_songs]
        ]

        self.manager.amm.update_playlist(playlist_name, am_additions)
        self.manager.sm.update_playlist(sp_id, sp_additions)
        self.manager.amm.close_driver()
        return ReturnCode.SUCCESS

    def sync_spotify_youtube(self, playlist_name: str) -> ReturnCode:
        """synchronies Spotify and Youtube Music Playlist by name

        Args:
            playlist_name (str): Name of playlist to synchronies
        """
        result = self.manager.sm.get_songs_from_playlist(playlist_name)
        if not result:
            return ReturnCode.NO_PLAYLIST_FOUND
        sp_songs, sp_id = result

        result = self.manager.ytm.get_songs_from_playlist(playlist_name)
        if not result:
            return ReturnCode.NO_PLAYLIST_FOUND
        yt_songs, yt_id = result

        sp_additions = [
            song for song in yt_songs if song[0] not in [song2[0] for song2 in sp_songs]
        ]
        yt_additions = [
            song for song in sp_songs if song[0] not in [song2[0] for song2 in yt_songs]
        ]

        self.manager.ytm.update_playlist(yt_id, yt_additions)

        self.manager.sm.update_playlist(sp_id, sp_additions)
        return ReturnCode.SUCCESS

    def sync_youtube_amazon(self, playlist_name: str) -> ReturnCode:
        """synchronies Youtube Music and Amazone Music Playlist by name

        Args:
            playlist_name (str): Name of playlist to synchronies
        """
        result = self.manager.ytm.get_songs_from_playlist(playlist_name)
        if not result:
            return ReturnCode.NO_PLAYLIST_FOUND
        yt_songs, yt_id = result

        self.manager.amm.start_driver()
        self.manager.amm.login()
        result = self.manager.amm.get_songs_from_playlist(playlist_name)
        if not result:
            return ReturnCode.NO_PLAYLIST_FOUND
        am_songs = result

        yt_additions = [
            song for song in am_songs if song[0] not in [song2[0] for song2 in yt_songs]
        ]
        am_additions = [
            song for song in yt_songs if song[0] not in [song2[0] for song2 in am_songs]
        ]

        self.manager.amm.update_playlist(playlist_name, am_additions)
        self.manager.ytm.update_playlist(yt_id, yt_additions)
        self.manager.amm.close_driver()
        return ReturnCode.SUCCESS

    def sync_amazon_spotify(self, playlist_name: str) -> ReturnCode:
        return self.sync_spotify_amazon(playlist_name)

    def sync_youtube_spotify(self, playlist_name: str) -> ReturnCode:
        return self.sync_spotify_youtube(playlist_name)

    def sync_amazon_youtube(self, playlist_name: str) -> ReturnCode:
        return self.sync_youtube_amazon(playlist_name)

    def sync_all(self, playlist_name: str) -> ReturnCode:
        """synchronies all platforms playlist by name

        Args:
            playlist_name (str): Name of playlist to synchronies
        """
        result = self.manager.sm.get_songs_from_playlist(playlist_name)
        if not result:
            return ReturnCode.NO_PLAYLIST_FOUND
        sp_songs, sp_id = result

        result = self.manager.ytm.get_songs_from_playlist(playlist_name)
        if not result:
            return ReturnCode.NO_PLAYLIST_FOUND
        yt_songs, yt_id = result

        self.manager.amm.start_driver()
        self.manager.amm.login()
        result = self.manager.amm.get_songs_from_playlist(playlist_name)
        if not result:
            return ReturnCode.NO_PLAYLIST_FOUND
        am_songs = result

        all_songs = (
            [song for song in sp_songs]
            + [song for song in yt_songs]
            + [song for song in am_songs]
        )

        unique_songs = set([song[0].lower() for song in all_songs])

        sp_additions = [
            song
            for song in all_songs
            if song[0].lower() in unique_songs and song not in sp_songs
        ]
        yt_additions = [
            song
            for song in all_songs
            if song[0].lower() in unique_songs and song not in yt_songs
        ]
        am_additions = [
            song
            for song in all_songs
            if song[0].lower() in unique_songs and song not in am_songs
        ]

        self.manager.amm.update_playlist(playlist_name, am_additions)
        self.manager.amm.close_driver()
        self.manager.sm.update_playlist(sp_id, sp_additions)
        self.manager.ytm.update_playlist(yt_id, yt_additions)
        return ReturnCode.SUCCESS
